#include <stdio.h>

int main1(){
int usf, euf;
printf("Enter US floor\n");
scanf("%d", &usf);
euf = usf - 1;
printf("EU floor %d\n", euf);
return 1;
}


int main(){
int first = 1;
int val, maxval, minval;

while(scanf("%d", &val) != EOF ){
if (first || val > maxval) maxval = val;
if (first || val < minval) minval = val;
first = 0;
}

printf("Maximum: %d\n", maxval);
printf("Minimum: %d\n", minval);
}