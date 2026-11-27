#include <stdio.h>

int main(){
    int first = 1;
    int min_val, max_val, cur_val;

    while (scanf("%d", &cur_val) != EOF){
        if (first || cur_val < min_val) min_val = cur_val;
        if (first || cur_val > max_val) max_val = cur_val;
        first = 0;
    }
    printf("min_val: '%d', max_val: '%d'\n", min_val, max_val);
}
