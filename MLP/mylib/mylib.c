#include <Python.h>
#include <stdio.h>

static PyObject *add(PyObject *self, PyObject *args) {
    int a, b;
    if (!PyArg_ParseTuple(args, "ii", &a, &b))
        return NULL;
    return PyLong_FromLong(a + b);
}

static PyObject *for_loop(PyObject *self, PyObject *args) {
    int start, stop, step;
    PyObject *func;
    if (!PyArg_ParseTuple(args, "iiiO", &start, &stop, &step, &func))
        return NULL;

    if (!PyCallable_Check(func)) {
        PyErr_SetString(PyExc_TypeError, "forth argument must be callable");
        return NULL;
    }

    for(int i = start; i < stop; i += step) {
        PyObject *arg = PyLong_FromLong(i);
        if (!arg)
            return NULL;

        PyObject *result = PyObject_CallOneArg(func, arg);
        Py_DECREF(arg);

        if (!result)
            return NULL;

        Py_DECREF(result);
    };

    Py_RETURN_NONE;
}

static PyObject *sum_range(PyObject *self, PyObject *args) {
    int start, stop;
    long long sum = 0;

    if (!PyArg_ParseTuple(args, "ii", &start, &stop))
        return NULL;

    for (int i = start; i < stop; i++)
        sum += i;

    return PyLong_FromLongLong(sum);
}

static PyObject *print(PyObject *self, PyObject *args) {
    int i;
    if (!PyArg_ParseTuple(args, "i", &i))
        return NULL;

    printf("%d\n", i);

    Py_RETURN_NONE;
}

static PyMethodDef Methods[] = {
    {"add", add, METH_VARARGS, "Add two integers"},
    {"for_loop", for_loop, METH_VARARGS, "Loops over a function"},
    {"sum_range", sum_range, METH_VARARGS, "Sums over a range"},
    {"print", print, METH_VARARGS, "Prints something"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "mylib",
    NULL,
    -1,
    Methods
};

PyMODINIT_FUNC PyInit_mylib(void) {
    return PyModule_Create(&module);
}
