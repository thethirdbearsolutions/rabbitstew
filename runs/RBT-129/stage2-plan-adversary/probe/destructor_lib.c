#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
static long cnt;
void work(void){ cnt++; }
__attribute__((destructor)) static void fini(void){ const char*p=getenv("ST"); if(!p) return; FILE*f=fopen(p,"a"); fprintf(f,"pid %d cnt %ld\n",getpid(),cnt); fclose(f);}
