/* Copyright 2012 Dietrich Epp <depp@zdome.net>
   See LICENSE.txt for details.  */
#include <unistd.h>

int main(int argc, char *argv[])
{
    close(STDOUT_FILENO);
    sleep(1);
    return 0;
}
