#include <stdio.h>
#include <stdint.h>

uint64_t djb2a(const char *str)
{
	uint64_t hash = 5381;
	int c;

	while ((c = *str++)) {
		hash = (hash * 33) ^ c;
	}
	return hash;
}

int main(int argc, char ** argv) {
    for (int i = 1; i < argc; i++) {
        printf("%40s: %016llx\n", argv[i], djb2a(argv[i]));
    }
}
