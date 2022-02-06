#include <stdio.h>
#include "file_utils.h"
#include "limiter.h"

void tests()
{
    char* hello_world = "Hello world\n";

    int i = 0;
    while (hello_world[i] != '\0') i++;
    printf("i: %d\n", i);

    printf("sizeof hello_world: %lu\n", sizeof(hello_world));
}

void test_write()
{
char* hello_world = "Hello world\n";

file_utils_write("./test.txt", hello_world);

printf("%s", hello_world);
}


void test_read()
{
char* hello_world = file_utils_read("./test.txt");
printf("%s", hello_world);
}


void test_run()
{
run("/");
}

int main()
{
test_run();
return 0;
}
