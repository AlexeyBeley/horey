#include <stdio.h>

int main(){
    int ret;
    int mymult(int x, int y);
    ret = mymult(6, 7);
    printf("%d * %d = %d\n", 6, 7, ret);
}

int mymult(int x, int y){
    int z=x*y;
    return z;
}