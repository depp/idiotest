#include <unistd.h>

int main(int argc, char *argv[])
{
    close(STDIN_FILENO);
    sleep(1);
    return 0;
}
