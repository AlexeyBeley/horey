#include <stdio.h>


int main(){
int guess;

while(scanf("%d", &guess) != EOF) {
if (guess == 42) {
printf("Nice job\n");
break;
}
else if (guess < 42) printf("Too small\n");
else printf("Too high\n");
}

}