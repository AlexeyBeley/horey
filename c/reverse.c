#include <stdio.h>

int main(){
    int ret;
    int max_len = 1000;
    char arr[max_len];
    int end = 0;
    int myreverse(char x[], int end);

    printf("Enter characters up to 1000\n");
    scanf("%999[^\n]", arr);

    printf("Scanned '%s'\n", arr);

    myreverse(arr, end);
    printf("Reverse: '%s'\n", arr);
}

int myreverse(char arr[], int end){
    printf("Entering %d\n", end);
    if (arr[end] == '\0') {
        return 0;
    }
    int new_end = end + 1;
    int start = myreverse(arr, new_end);
    if (start >= end) return start;

    int tmp = arr[end];
    arr[end] =  arr[start];
    arr[start] = tmp;

    printf("Exiting after swapping. Start: %d, End: %d\n", start, end);
    return ++start;
}