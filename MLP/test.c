#include <stdlib.h>
#include <stdio.h>

void int_to_str(int n, char *str) {
	int i = 0;
	while (n > 0) {
		str[i++] = n % 10 + '0';
		n /= 10;
	}

	int j = 0;
	int k = i - 1;
	while (j < k) {
		char temp = str[j];
		str[j] = str[k];
		str[k] = temp;
		j++;
		k--;
	}
}

void long_to_str(long n, char *str) {
	int i = 0;
	while (n > 0) {
		str[i++] = n % 10 + '0';
		n /= 10;
	}

	int j = 0;
	int k = i - 1;
	while (j < k) {
		char temp = str[j];
		str[j] = str[k];
		str[k] = temp;
		j++;
		k--;
	}
}

int get_num_digits(long n) {
	int i = 0;
	while (n > 0) {
		n /= 10;
		i++;
	}
	return i;
}

void long_array_to_str(long *n, char *str) {
	int i = 0;
	str[i] = '[';
	i++;
	int size = n[0];
	for(int j = 0; j < size; j++) {
		char number[10];
		long_to_str(n[j + 1], number);

		int len = get_num_digits(n[j + 1]);

		for(int k = 0; k < len; k++) {
			str[i + k] = number[k];
		}

		i += len;

		if(j != size - 1) {
			str[i] = ',';
			str[i + 1] = ' ';
			i += 2;
		}
	}
	str[i] = ']';
}

int main() {
	long *layer_sizes;
	long list[] = {6, 7, 13, 9, 2147483647};
	int size = sizeof(list) / sizeof(list[0]);
	layer_sizes = calloc(size + 1, sizeof(list[0]));
	layer_sizes[0] = size;
	for(int i = 0; i < size; i++) {
		layer_sizes[i + 1] = list[i];
	}

    char result[100];
	long_array_to_str(layer_sizes, result);
	printf(result);
	printf("\n");
	return 0;
}
