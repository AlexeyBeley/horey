#include <stdio.h>
#include <stdlib.h>

int file_utils_len(char* str)
{
    int i = 0;
    while (str[i] != '\0') i++;
    return i;
}

char* file_utils_read(char* file_path)
{
    int num = 0;
    FILE *fptr;
    long length = 0;
    char * buffer =0;

    if ((fptr = fopen(file_path, "r")) == NULL)
    {
        printf("Error: no such file %s", file_path);
        exit(1);
    }

    fseek (fptr, 0, SEEK_END);
    length = ftell (fptr);
    fseek (fptr, 0, SEEK_SET);
    buffer = malloc (length);

    if (buffer)
    {
        fread (buffer, 1, length, fptr);
    }
    else
    {
        printf("Error allocating buffer of size %ld", length);
        exit(1);
    }

    fclose(fptr);
    return buffer;
}


int file_utils_write(char* file_path, char* src_string)
{
    FILE *fptr;

    if ((fptr = fopen(file_path, "w")) == NULL)
    {
        printf("Error");
        exit(1);
    }

    fwrite(src_string, sizeof(char), file_utils_len(src_string), fptr);

    fclose(fptr);
    return 0;

}

