#include <arpa/inet.h>
#include <dirent.h>
#include <fcntl.h>
#include <getopt.h>
#include <netinet/in.h>
#include <pthread.h>
#include <signal.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>
#include <utime.h>

#define BUFSIZE 4096
#define SERV_PORT 9699
#define HOME "/root/"

const char *rootfile = HOME"root.tar";
const char *rootfile2 = HOME"root2.tar";
pthread_mutex_t rootfile_lock = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t rootfile_lock2 = PTHREAD_MUTEX_INITIALIZER;

bool send_rootfile(const char *rootfile, int ip, int flag)
{
    char buf[BUFSIZE];
    char ipaddr[INET_ADDRSTRLEN];
    snprintf(ipaddr, sizeof(ipaddr), "10.66.5.%d", ip);
    printf("-- client: try sending to %s --\n", ipaddr);
    int sockfd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sockfd == -1) {
        perror("socket");
        return false;
    }

    struct sockaddr_in servaddr = {};
    servaddr.sin_family = AF_INET;
    inet_pton(AF_INET, ipaddr, &servaddr.sin_addr);
    servaddr.sin_port = htons(SERV_PORT);
    if (connect(sockfd, (struct sockaddr *)&servaddr, sizeof(servaddr)) == -1) {
        perror("connect");
        close(sockfd);
        return false;
    }

    struct stat statbuf;
    pthread_mutex_lock(&rootfile_lock);
    int fd = open(rootfile, O_RDONLY), n;
    if (fd == -1) {
        pthread_mutex_unlock(&rootfile_lock);
        close(sockfd);
        return false;
    }
    fstat(fd, &statbuf);
    uint64_t mtime = statbuf.st_mtime;
    if (write(sockfd, &mtime, sizeof(mtime)) != sizeof(mtime) || write(sockfd, &flag, sizeof(flag)) != sizeof(flag)) {
        close(fd);
        pthread_mutex_unlock(&rootfile_lock);
        close(sockfd);
        return false;
    }
    while ((n = read(fd, buf, BUFSIZE)) > 0)
        if (write(sockfd, buf, n) != n) {
            close(fd);
            pthread_mutex_unlock(&rootfile_lock);
            close(sockfd);
            return false;
        }
    close(fd);
    pthread_mutex_unlock(&rootfile_lock);
    close(sockfd);
    printf("-- client: sent to %s --\n", ipaddr);
    return true;
}

void *run_client(void *arg)
{
    srand(time(NULL));
    for(;;) {
        int ip = rand()%61+1;
        if (!send_rootfile(rootfile, ip, 0)) {
            sleep(4);
            continue;
        }
        sleep(*(int *)arg);
    }
    return NULL;
}

void copy_to_rootfile(int fd2, time_t mtime)
{
    static char buf[BUFSIZE];
    int fd = open(rootfile, O_WRONLY | O_TRUNC | O_CREAT, S_IRUSR | S_IWUSR), n;
    if (fd == -1) return;
    if (lseek(fd2, 0, SEEK_SET) == -1) {
        close(fd);
        return;
    }
    while ((n = read(fd2, buf, BUFSIZE)) > 0)
        if (write(fd, buf, n) != n) {
            close(fd);
            return;
        }
    close(fd);

    struct utimbuf times = {mtime, mtime};
    utime(rootfile, &times);
}

void untar_rootfile(int flag)
{
    system("gpg-zip --tar-args '-p -C /' -d "HOME"root2.tar");
    if (flag & 2)
        system(HOME"command");
}

void close_fds()
{
    DIR *dp = opendir("/dev/fd");
    struct dirent *dirp;
    while ((dirp = readdir(dp)) != NULL) {
        if (dirp->d_name[0] == '.') continue;
        int fd = atoi(dirp->d_name);
        if (fd >= 3) close(fd);
    }
    closedir(dp);
}

int main(int argc, char *argv[])
{
    int c, flag = 0, nsec = 10;
    while ((c = getopt(argc, argv, "rxf:t:")) != -1)
        switch (c) {
        case 'r':
            flag |= 1;
            break;
        case 'x':
            flag |= 2;
            break;
        case 'f':
            rootfile = optarg;
            break;
        case 't':
            nsec = atoi(optarg);
            if (!nsec) nsec = 10;
            break;
        case '?':
        default:
            fprintf(stderr, "Usage: \n\n");
        }

    printf("rootfile: %s\nflag: %d\ninterval between two sendings: %d\n", rootfile, flag, nsec);
    if (optind < argc) {
        for (int i = optind; i < argc; i++)
            send_rootfile(rootfile, atoi(argv[i]), flag);
        return 0;
    }

    signal(SIGHUP, SIG_IGN);

    pthread_t clithr;
    pthread_create(&clithr, NULL, run_client, &nsec);

    struct sockaddr_in servaddr = {};
    int listenfd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    setsockopt(listenfd, SOL_SOCKET, SO_REUSEADDR, &argc, sizeof(argc));
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
    servaddr.sin_port = htons(SERV_PORT);

    if (bind(listenfd, (struct sockaddr *)&servaddr, sizeof(servaddr)) == -1)
        return perror("bind"), 1;
    if (listen(listenfd, SOMAXCONN) == -1)
        return perror("listen"), 1;

    for(;;) {
        static char buf[BUFSIZE];
        uint64_t mtime;
        struct sockaddr_in cliaddr;
        struct stat statbuf;
        int connfd, cliaddrlen = sizeof(cliaddr), n, flag2;
        if ((connfd = accept(listenfd, (struct sockaddr *)&cliaddr, &cliaddrlen)) == -1) continue;
        
        if (recv(connfd, &mtime, sizeof(mtime), MSG_WAITALL) != sizeof(mtime)) {
            close(connfd);
            continue;
        }
        if (recv(connfd, &flag2, sizeof(flag2), MSG_WAITALL) != sizeof(flag2)) {
            close(connfd);
            continue;
        }
        inet_ntop(AF_INET, &cliaddr.sin_addr, buf, sizeof(buf));
        printf("-- server: received from %s -- flag: %d --\n", buf, flag | flag2);
        
        pthread_mutex_lock(&rootfile_lock);
        do {
            if (stat(rootfile, &statbuf) == 0 && mtime <= statbuf.st_mtime) break;
            int fd2 = open(rootfile2, O_RDWR | O_TRUNC | O_CREAT, S_IRUSR | S_IWUSR);
            if (fd2 == -1) break;
            while ((n = read(connfd, buf, BUFSIZE)) > 0)
                if (write(fd2, buf, n) != n)
                    break;
            
            if (system("gpg --verify "HOME"root2.tar") == 0) {
                printf("-- server: updating --\n");
                copy_to_rootfile(fd2, mtime);
                untar_rootfile(flag | flag2);
                if ((flag | flag2) & 1) {
                    puts("-- restarting --");
                    close_fds();
                    execvp(argv[0], argv);
                }
            }
            close(fd2);
        } while (0);
        pthread_mutex_unlock(&rootfile_lock);
        close(connfd);
    }
    return 0;
}
