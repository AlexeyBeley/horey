#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <errno.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#define die(e) do { fprintf(stderr, "%s\n", e); exit(EXIT_FAILURE); } while (0);


void main_thread(pid_t pid, int *link)
{
  pid_t ret;
  int status;
  char foo[4096 + 1];
  memset(foo, 0, 4096);

  while ((ret = waitpid(pid, &status, 0)) == -1) {
      if (errno != EINTR) {
        printf("errno != EINTR: %d", errno);
        break;
      }
    }

    close(link[1]);
    printf("debug 0\n");
    int nbytes = read(link[0], foo, sizeof(foo));
    printf("debug 1\n");
    printf("Output: (%.*s)\n", nbytes, foo);
    wait(NULL);

    if ((ret == 0) ||
        !(WIFEXITED(status) && !WEXITSTATUS(status))) {
        printf("fork child error %d, %d, %d\n", ret, WIFEXITED(status), WEXITSTATUS(status));
        die("fork child error");
    }
}

void child_thread(int *link, char *const *args, char **env)
{
    /* ... Initialize env as a sanitized copy of environ ... */
    printf("debug 3\n");
    dup2 (link[1], STDOUT_FILENO);
    printf("debug 4\n");

    close(link[0]);
    close(link[1]);
    printf("debug 5\n");
    if (execve("/usr/bin/ls", args, env) == -1) {
      /* Handle error */
      printf("Error executing %s", args[0]);
      _Exit(15);
    }
    die("execve");
}


void run(char *input) {
  pid_t pid;
  int status;
  char *const args[3] = {"/usr/bin/ls", input, NULL};
  char **env;
  extern char **environ;
  int link[2];


  if (pipe(link)==-1)
    die("pipe");

  if ((pid = fork()) == -1) {
    die("fork");
  } else if (pid != 0) {
  main_thread(pid, link);
  } else {
  child_thread(link, args, env);
  }

}