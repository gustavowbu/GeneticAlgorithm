// neurallib.c
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <string.h>
#include <stdint.h> /* for SIZE_MAX */

/*
  Single-buffer MLP implementation.
  Internal layout:
    - layer_sizes: Py_ssize_t* length n_layers (malloc'ed via PyMem_Malloc)
    - act_names: char** length n_layers (malloc'ed via PyMem_Malloc; each string copied)
    - params: double* contiguous buffer of all biases and weights
    - bias_offsets: Py_ssize_t* length n_layers; bias for layer L starts at params[bias_offsets[L]]
    - weight_offsets: Py_ssize_t* length n_layers; weight block for layer L starts at params[weight_offsets[L]]
        weight block length is layer_sizes[L] * layer_sizes[L+1]; for last layer weight_offsets[L] == -1
*/

typedef struct {
    PyObject_HEAD
    Py_ssize_t n_layers;

    Py_ssize_t *layer_sizes;    /* length n_layers */
    char **act_names;           /* length n_layers */

    double *params;             /* contiguous buffer */
    Py_ssize_t total_params;    /* number of doubles in params */

    Py_ssize_t *bias_offsets;   /* length n_layers */
    Py_ssize_t *weight_offsets; /* length n_layers; -1 for last layer */
} mlpObject;

/* Helper random double [0,1) */
static double rand_double(void) {
    return ((double)rand()) / ((double)RAND_MAX + 1.0);
}

/* Forward declarations */
static PyObject *mlp_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static int mlp_init(mlpObject *self, PyObject *args, PyObject *kwds);
static void mlp_dealloc(mlpObject *self);
static PyObject *mlp_repr(mlpObject *self);

static PyObject *mlp_randomize(mlpObject *self, PyObject *Py_UNUSED(ignored));
static PyObject *mlp_mutate(mlpObject *self, PyObject *args);
static PyObject *mlp_relu(PyObject *self, PyObject *args);
static PyObject *mlp_sigmoid(PyObject *self, PyObject *args);
static PyObject *mlp_forward_propagate(mlpObject *self, PyObject *args);
static PyObject *mlp_get_weights(mlpObject *self, PyObject *Py_UNUSED(ignored));
static PyObject *mlp_get_biases(mlpObject *self, PyObject *Py_UNUSED(ignored));

/* Helpers for memory management */
static void free_internal_storage(mlpObject *self) {
    if (!self) return;

    if (self->layer_sizes) {
        PyMem_Free(self->layer_sizes);
        self->layer_sizes = NULL;
    }

    if (self->act_names) {
        for (Py_ssize_t i = 0; i < self->n_layers; ++i) {
            if (self->act_names[i]) PyMem_Free(self->act_names[i]);
        }
        PyMem_Free(self->act_names);
        self->act_names = NULL;
    }

    if (self->params) {
        PyMem_Free(self->params);
        self->params = NULL;
    }

    if (self->bias_offsets) {
        PyMem_Free(self->bias_offsets);
        self->bias_offsets = NULL;
    }

    if (self->weight_offsets) {
        PyMem_Free(self->weight_offsets);
        self->weight_offsets = NULL;
    }

    self->total_params = 0;
    self->n_layers = 0;
}

/* Copy layer_sizes list to C array */
static int copy_layer_sizes_from_pylist(PyObject *list, Py_ssize_t **out_sizes, Py_ssize_t *out_n) {
    if (!PyList_Check(list)) {
        PyErr_SetString(PyExc_TypeError, "layer_sizes must be a list of positive ints");
        return -1;
    }
    Py_ssize_t n = PyList_Size(list);
    if (n <= 0) {
        PyErr_SetString(PyExc_ValueError, "layer_sizes must have at least one layer");
        return -1;
    }
    Py_ssize_t *sizes = PyMem_Malloc(sizeof(Py_ssize_t) * n);
    if (!sizes) { PyErr_NoMemory(); return -1; }
    for (Py_ssize_t i = 0; i < n; ++i) {
        PyObject *it = PyList_GetItem(list, i); /* borrowed */
        if (!PyLong_Check(it)) {
            PyMem_Free(sizes);
            PyErr_SetString(PyExc_TypeError, "layer_sizes must contain ints");
            return -1;
        }
        long v = PyLong_AsLong(it);
        if (PyErr_Occurred()) { PyMem_Free(sizes); return -1; }
        if (v <= 0) { PyMem_Free(sizes); PyErr_SetString(PyExc_ValueError, "layer sizes must be positive integers"); return -1; }
        sizes[i] = (Py_ssize_t)v;
    }
    *out_sizes = sizes;
    *out_n = n;
    return 0;
}

/* Copy activation functions names */
static int copy_act_names_from_pylist(PyObject *list, char ***out_names, Py_ssize_t expected_n) {
    if (!PyList_Check(list)) {
        PyErr_SetString(PyExc_TypeError, "activation_functions must be a list of strings");
        return -1;
    }
    Py_ssize_t n = PyList_Size(list);
    if (n != expected_n) {
        PyErr_SetString(PyExc_ValueError, "activation_functions must have same length as layer_sizes");
        return -1;
    }
    char **names = PyMem_Malloc(sizeof(char*) * n);
    if (!names) { PyErr_NoMemory(); return -1; }
    for (Py_ssize_t i = 0; i < n; ++i) {
        PyObject *it = PyList_GetItem(list, i); /* borrowed */
        if (!PyUnicode_Check(it)) {
            for (Py_ssize_t k = 0; k < i; ++k) PyMem_Free(names[k]);
            PyMem_Free(names);
            PyErr_SetString(PyExc_TypeError, "activation_functions must contain strings");
            return -1;
        }
        const char *s = PyUnicode_AsUTF8(it);
        if (!s) {
            for (Py_ssize_t k = 0; k < i; ++k) PyMem_Free(names[k]);
            PyMem_Free(names);
            return -1;
        }
        size_t len = strlen(s);
        char *copy = PyMem_Malloc(len + 1);
        if (!copy) {
            for (Py_ssize_t k = 0; k < i; ++k) PyMem_Free(names[k]);
            PyMem_Free(names);
            PyErr_NoMemory();
            return -1;
        }
        memcpy(copy, s, len + 1);
        names[i] = copy;
    }
    *out_names = names;
    return 0;
}

/* Compute offsets and allocate single params buffer (with overflow checks) */
static int allocate_single_params_buffer(mlpObject *self) {
    Py_ssize_t n = self->n_layers;
    if (n <= 0) { PyErr_SetString(PyExc_RuntimeError, "invalid n_layers"); return -1; }

    /* compute total counts safely using size_t */
    size_t total_bias = 0;
    size_t total_weights = 0;

    for (Py_ssize_t L = 0; L < n; ++L) {
        size_t add = (size_t) self->layer_sizes[L];
        if (total_bias > SIZE_MAX - add) { PyErr_SetString(PyExc_OverflowError, "total bias overflow"); return -1; }
        total_bias += add;
    }

    for (Py_ssize_t L = 0; L + 1 < n; ++L) {
        size_t a = (size_t) self->layer_sizes[L];
        size_t b = (size_t) self->layer_sizes[L+1];
        if (a != 0 && b > SIZE_MAX / a) { PyErr_SetString(PyExc_OverflowError, "layer size multiplication overflow"); return -1; }
        size_t prod = a * b;
        if (total_weights > SIZE_MAX - prod) { PyErr_SetString(PyExc_OverflowError, "total weights overflow"); return -1; }
        total_weights += prod;
    }

    if (total_bias > SIZE_MAX - total_weights) { PyErr_SetString(PyExc_OverflowError, "total params overflow"); return -1; }
    size_t total_sz = total_bias + total_weights;

    if (total_sz > (size_t)PY_SSIZE_T_MAX) { PyErr_SetString(PyExc_OverflowError, "total params exceed PY_SSIZE_T_MAX"); return -1; }
    Py_ssize_t total = (Py_ssize_t) total_sz;

    /* allocate buffer */
    double *params = PyMem_Malloc(sizeof(double) * total_sz);
    if (!params) { PyErr_NoMemory(); return -1; }

    /* allocate offsets arrays */
    Py_ssize_t *bias_offsets = PyMem_Malloc(sizeof(Py_ssize_t) * (size_t)n);
    Py_ssize_t *weight_offsets = PyMem_Malloc(sizeof(Py_ssize_t) * (size_t)n);
    if (!bias_offsets || !weight_offsets) {
        if (bias_offsets) PyMem_Free(bias_offsets);
        if (weight_offsets) PyMem_Free(weight_offsets);
        PyMem_Free(params);
        PyErr_NoMemory();
        return -1;
    }

    /* fill offsets: first place all biases, then all weights */
    Py_ssize_t pos = 0;
    for (Py_ssize_t L = 0; L < n; ++L) {
        bias_offsets[L] = pos;
        pos += self->layer_sizes[L];
    }
    for (Py_ssize_t L = 0; L < n; ++L) {
        if (L + 1 >= n) {
            weight_offsets[L] = -1;
            continue;
        }
        weight_offsets[L] = pos;
        pos += self->layer_sizes[L] * self->layer_sizes[L+1];
    }
    /* pos should equal total */
    self->params = params;
    self->total_params = total;
    self->bias_offsets = bias_offsets;
    self->weight_offsets = weight_offsets;
    return 0;
}

/* --- Python API implementations --- */

static PyObject *
mlp_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    mlpObject *self = (mlpObject *)type->tp_alloc(type, 0);
    if (!self) return NULL;
    /* initialize fields to safe defaults */
    self->n_layers = 0;
    self->layer_sizes = NULL;
    self->act_names = NULL;
    self->params = NULL;
    self->total_params = 0;
    self->bias_offsets = NULL;
    self->weight_offsets = NULL;
    return (PyObject *)self;
}

static int mlp_init(mlpObject *self, PyObject *args, PyObject *kwds) {
    PyObject *layer_sizes_arg = NULL;
    PyObject *activations_arg = NULL;
    static char *kwlist[] = {"layer_sizes", "activation_functions", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO", kwlist,
                                     &layer_sizes_arg, &activations_arg)) {
        return -1;
    }

    /* free any previous internal storage */
    free_internal_storage(self);

    /* copy layer sizes and activation names */
    Py_ssize_t *sizes = NULL;
    Py_ssize_t n_layers = 0;
    if (copy_layer_sizes_from_pylist(layer_sizes_arg, &sizes, &n_layers) < 0) {
        return -1;
    }
    char **act_names = NULL;
    if (copy_act_names_from_pylist(activations_arg, &act_names, n_layers) < 0) {
        PyMem_Free(sizes);
        return -1;
    }

    self->n_layers = n_layers;
    self->layer_sizes = sizes;
    self->act_names = act_names;

    /* allocate single params buffer and offsets */
    if (allocate_single_params_buffer(self) < 0) {
        free_internal_storage(self);
        return -1;
    }

    /* randomize */
    if (mlp_randomize(self, NULL) == NULL) {
        free_internal_storage(self);
        return -1;
    }

    return 0;
}

static void mlp_dealloc(mlpObject *self) {
    free_internal_storage(self);
    Py_TYPE(self)->tp_free((PyObject*)self);
}

/* __repr__ */
static PyObject *mlp_repr(mlpObject *self) {
    if (self->n_layers <= 0 || !self->layer_sizes || !self->act_names) {
        return PyUnicode_FromString("mlp(<uninitialized>)");
    }

    Py_ssize_t n = self->n_layers;
    size_t bufsize = 32 + (size_t)n * 48;
    char *buf = PyMem_Malloc(bufsize);
    if (!buf) return PyErr_NoMemory();

    size_t pos = 0;
    pos += snprintf(buf + pos, bufsize - pos, "mlp(");

    for (Py_ssize_t i = 0; i < n; ++i) {
        if (i) pos += snprintf(buf + pos, bufsize - pos, ", ");

        if (i == 0) {
            pos += snprintf(buf + pos, bufsize - pos, "%zd: None", self->layer_sizes[i]);
        } else {
            pos += snprintf(buf + pos, bufsize - pos, "%zd: %s", self->layer_sizes[i], self->act_names[i]);
        }

        if (pos + 64 > bufsize) {
            size_t newsize = bufsize * 2;
            char *tmp = PyMem_Realloc(buf, newsize);
            if (!tmp) {
                PyMem_Free(buf);
                return PyErr_NoMemory();
            }
            buf = tmp;
            bufsize = newsize;
        }
    }

    pos += snprintf(buf + pos, bufsize - pos, ")");

    PyObject *res = PyUnicode_FromStringAndSize(buf, (Py_ssize_t)pos);
    PyMem_Free(buf);
    return res;
}

/* randomize: fill params with random values [0,1) */
static PyObject *mlp_randomize(mlpObject *self, PyObject *Py_UNUSED(ignored)) {
    if (!self->params) { PyErr_SetString(PyExc_RuntimeError, "mlp not initialized"); return NULL; }
    for (Py_ssize_t i = 0; i < self->total_params; ++i) self->params[i] = rand_double();
    Py_RETURN_NONE;
}

/* mutate(rate): for each parameter, with probability `rate` mutate it by adding
   a random delta in [-rate, +rate]. rate must be in [0,1]. */
static PyObject *mlp_mutate(mlpObject *self, PyObject *args) {
    double rate;
    if (!PyArg_ParseTuple(args, "d", &rate)) return NULL;
    if (rate < 0.0 || rate > 1.0) {
        PyErr_SetString(PyExc_ValueError, "rate must be between 0.0 and 1.0");
        return NULL;
    }
    if (!self->params) { PyErr_SetString(PyExc_RuntimeError, "mlp not initialized"); return NULL; }

    /* Numeric work only — allow other Python threads to run. */
    Py_BEGIN_ALLOW_THREADS;
    for (Py_ssize_t i = 0; i < self->total_params; ++i) {
        if (rand_double() < rate) {
            double delta = (rand_double() * 2.0 - 1.0) * 0.1;
            double v = self->params[i] + delta;
            if (v < 0.0) v = 0.0;
            if (v > 1.0) v = 1.0;
            self->params[i] = v;
        }
    }
    Py_END_ALLOW_THREADS;

    Py_RETURN_NONE;
}

/* relu, sigmoid helpers */
static PyObject *mlp_relu(PyObject *self, PyObject *args) {
    double x;
    if (!PyArg_ParseTuple(args, "d", &x)) return NULL;
    double r = x > 0.0 ? x : 0.0;
    return PyFloat_FromDouble(r);
}
static PyObject *mlp_sigmoid(PyObject *self, PyObject *args) {
    double x;
    if (!PyArg_ParseTuple(args, "d", &x)) return NULL;
    double s = 1.0 / (1.0 + exp(-x));
    return PyFloat_FromDouble(s);
}

/* apply activation to array in-place by name */
static int apply_activation_by_name_c(const char *name, double *arr, Py_ssize_t len) {
    if (!name || !arr) return -1;
    if (strcmp(name, "relu") == 0) {
        for (Py_ssize_t i = 0; i < len; ++i) if (arr[i] < 0.0) arr[i] = 0.0;
        return 0;
    } else if (strcmp(name, "sigmoid") == 0) {
        for (Py_ssize_t i = 0; i < len; ++i) arr[i] = 1.0 / (1.0 + exp(-arr[i]));
        return 0;
    } else if (strcmp(name, "identity") == 0) {
        return 0;
    } else {
        return -1;
    }
}

/* forward_propagate (with GIL release for numeric core) */
static PyObject *mlp_forward_propagate(mlpObject *self, PyObject *args) {
    PyObject *input_list;
    if (!PyArg_ParseTuple(args, "O", &input_list)) return NULL;
    if (!PyList_Check(input_list)) { PyErr_SetString(PyExc_TypeError, "input must be a list"); return NULL; }
    if (!self->params) { PyErr_SetString(PyExc_RuntimeError, "mlp not initialized"); return NULL; }

    Py_ssize_t in_sz = PyList_Size(input_list);
    if (in_sz != self->layer_sizes[0]) {
        PyErr_Format(PyExc_ValueError, "input length %zd != first layer size %zd", in_sz, self->layer_sizes[0]);
        return NULL;
    }

    double *current = PyMem_Malloc(sizeof(double) * (size_t)in_sz);
    if (!current) return PyErr_NoMemory();
    for (Py_ssize_t i = 0; i < in_sz; ++i) {
        PyObject *it = PyList_GetItem(input_list, i); /* borrowed */
        double v = PyFloat_AsDouble(it);
        if (PyErr_Occurred()) { PyMem_Free(current); return NULL; }
        current[i] = v;
    }

    /* propagate */
    for (Py_ssize_t L = 0; L + 1 < self->n_layers; ++L) {
        Py_ssize_t next_sz = self->layer_sizes[L+1];
        double *next = PyMem_Malloc(sizeof(double) * (size_t)next_sz);
        if (!next) { PyMem_Free(current); return PyErr_NoMemory(); }

        /* bias for next layer */
        double *bias_next = self->params + self->bias_offsets[L+1];
        for (Py_ssize_t j = 0; j < next_sz; ++j) next[j] = bias_next[j];

        /* weights block for layer L */
        Py_ssize_t woff = self->weight_offsets[L];
        double *wbase = self->params + woff; /* length: layer_sizes[L] * next_sz */
        Py_ssize_t cur_sz = self->layer_sizes[L];

        /* We'll do the heavy numeric work with the GIL released.
           We must not call any Python C-API while the GIL is released.
           We set a local error flag if activation name is unknown. */
        int unknown_activation = 0;
        char unknown_act_buf[128];
        unknown_act_buf[0] = '\0';

        Py_BEGIN_ALLOW_THREADS;
        for (Py_ssize_t i = 0; i < cur_sz; ++i) {
            double ci = current[i];
            double *row = wbase + (size_t)i * (size_t)next_sz;
            for (Py_ssize_t j = 0; j < next_sz; ++j) {
                next[j] += ci * row[j];
            }
        }

        /* activation: pure C (strcmp, exp), safe without GIL */
        const char *act = self->act_names[L+1];
        if (apply_activation_by_name_c(act, next, next_sz) < 0) {
            /* copy the activation name into a local buffer so we can raise an error after reacquiring GIL */
            if (act) {
                strncpy(unknown_act_buf, act, sizeof(unknown_act_buf) - 1);
                unknown_act_buf[sizeof(unknown_act_buf) - 1] = '\0';
            } else {
                unknown_act_buf[0] = '\0';
            }
            unknown_activation = 1;
        }
        Py_END_ALLOW_THREADS;

        if (unknown_activation) {
            PyMem_Free(next);
            PyMem_Free(current);
            if (unknown_act_buf[0]) {
                PyErr_Format(PyExc_ValueError, "unknown activation '%s'", unknown_act_buf);
            } else {
                PyErr_SetString(PyExc_ValueError, "unknown activation (null name)");
            }
            return NULL;
        }

        PyMem_Free(current);
        current = next;
    }

    /* build Python list from current */
    Py_ssize_t out_sz = self->layer_sizes[self->n_layers - 1];
    PyObject *output = PyList_New(out_sz);
    if (!output) { PyMem_Free(current); return PyErr_NoMemory(); }
    for (Py_ssize_t j = 0; j < out_sz; ++j) {
        PyObject *f = PyFloat_FromDouble(current[j]);
        if (!f) { Py_DECREF(output); PyMem_Free(current); return NULL; }
        PyList_SetItem(output, j, f);
    }

    PyMem_Free(current);
    return output;
}

/* get_weights builds nested lists from params (on-demand) */
static PyObject *mlp_get_weights(mlpObject *self, PyObject *Py_UNUSED(ignored)) {
    if (!self->params) { Py_RETURN_NONE; }
    PyObject *outer = PyList_New(self->n_layers);
    if (!outer) return PyErr_NoMemory();
    for (Py_ssize_t L = 0; L < self->n_layers; ++L) {
        Py_ssize_t sz = self->layer_sizes[L];
        PyObject *layer_list = PyList_New(sz);
        if (!layer_list) { Py_DECREF(outer); return PyErr_NoMemory(); }
        if (L + 1 >= self->n_layers) {
            for (Py_ssize_t i = 0; i < sz; ++i) {
                PyObject *empty = PyList_New(0);
                if (!empty) { Py_DECREF(layer_list); Py_DECREF(outer); return PyErr_NoMemory(); }
                PyList_SetItem(layer_list, i, empty);
            }
            PyList_SetItem(outer, L, layer_list);
            continue;
        }
        Py_ssize_t next_sz = self->layer_sizes[L+1];
        double *wbase = self->params + self->weight_offsets[L];
        for (Py_ssize_t i = 0; i < sz; ++i) {
            PyObject *neuron_list = PyList_New(next_sz);
            if (!neuron_list) { Py_DECREF(layer_list); Py_DECREF(outer); return PyErr_NoMemory(); }
            double *row = wbase + (size_t)i * (size_t)next_sz;
            for (Py_ssize_t j = 0; j < next_sz; ++j) {
                PyObject *f = PyFloat_FromDouble(row[j]);
                if (!f) { Py_DECREF(neuron_list); Py_DECREF(layer_list); Py_DECREF(outer); return NULL; }
                PyList_SetItem(neuron_list, j, f);
            }
            PyList_SetItem(layer_list, i, neuron_list);
        }
        PyList_SetItem(outer, L, layer_list);
    }
    return outer;
}

/* get_biases builds nested lists from params */
static PyObject *mlp_get_biases(mlpObject *self, PyObject *Py_UNUSED(ignored)) {
    if (!self->params) { Py_RETURN_NONE; }
    PyObject *outer = PyList_New(self->n_layers);
    if (!outer) return PyErr_NoMemory();
    for (Py_ssize_t L = 0; L < self->n_layers; ++L) {
        Py_ssize_t sz = self->layer_sizes[L];
        PyObject *layer_list = PyList_New(sz);
        if (!layer_list) { Py_DECREF(outer); return PyErr_NoMemory(); }
        double *b = self->params + self->bias_offsets[L];
        for (Py_ssize_t j = 0; j < sz; ++j) {
            PyObject *f = PyFloat_FromDouble(b[j]);
            if (!f) { Py_DECREF(layer_list); Py_DECREF(outer); return NULL; }
            PyList_SetItem(layer_list, j, f);
        }
        PyList_SetItem(outer, L, layer_list);
    }
    return outer;
}

/* methods table and type definition */
static PyMethodDef mlp_methods[] = {
    {"randomize", (PyCFunction)mlp_randomize, METH_NOARGS, "randomize weights and biases"},
    {"mutate", (PyCFunction)mlp_mutate, METH_VARARGS, "mutate(rate) -- mutate weights and biases"},
    {"relu", (PyCFunction)mlp_relu, METH_VARARGS, "relu(x)"},
    {"sigmoid", (PyCFunction)mlp_sigmoid, METH_VARARGS, "sigmoid(x)"},
    {"forward_propagate", (PyCFunction)mlp_forward_propagate, METH_VARARGS, "forward_propagate(input_list)"},
    {"get_weights", (PyCFunction)mlp_get_weights, METH_NOARGS, "return weights as nested lists"},
    {"get_biases", (PyCFunction)mlp_get_biases, METH_NOARGS, "return biases as nested lists"},
    {NULL}
};

static PyTypeObject mlpType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "neurallib.mlp",
    .tp_basicsize = sizeof(mlpObject),
    .tp_itemsize = 0,
    .tp_dealloc = (destructor)mlp_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_doc = "mlp objects (single-buffer C-backed)",
    .tp_methods = mlp_methods,
    .tp_init = (initproc)mlp_init,
    .tp_new = mlp_new,
    .tp_repr = (reprfunc)mlp_repr,
};

/* module setup */
static PyMethodDef module_methods[] = {
    {NULL}
};

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "neurallib",
    "Simple neural network MLP implemented as a C extension (single-buffer)",
    -1,
    module_methods
};

PyMODINIT_FUNC PyInit_neurallib(void) {
    PyObject *m;
    if (PyType_Ready(&mlpType) < 0) return NULL;
    m = PyModule_Create(&moduledef);
    if (!m) return NULL;
    srand((unsigned)time(NULL));
    Py_INCREF(&mlpType);
    if (PyModule_AddObject(m, "mlp", (PyObject *)&mlpType) < 0) {
        Py_DECREF(&mlpType);
        Py_DECREF(m);
        return NULL;
    }
    return m;
}
