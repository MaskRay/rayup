#include <dirent.h>
#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <sys/ptrace.h>
#include <sys/types.h>
#include <unistd.h>

const char *configdir = "/root/mem";

char *buf = NULL;
size_t bufsize;

struct List
{
    List *next;
    char *cmd;
} *ignored_prefix;

size_t nodecnt = 1;
struct Node
{
    bool flag;
    Node *ch[256], *pi;
    Node() : flag(false), pi(NULL) { bzero(ch, sizeof(ch)); }
} root;

void aho_corasick_insert(const char *s, size_t size)
{
    Node *x = &root;
    for (const char *p = s; p != s+size; p++) {
        if (x->ch[(unsigned char)*p] == NULL)
            x->ch[(unsigned char)*p] = new Node, nodecnt++;
        x = x->ch[(unsigned char)*p];
    }
    x->flag = true;
}

void aho_corasick_build()
{
    Node **q = (Node **)malloc(sizeof(Node)*nodecnt), **fore = q, **rear = q;
    for (int i = 0; i < 256; i++)
        if (!root.ch[i])
            root.ch[i] = &root;
        else {
            root.ch[i]->pi = &root;
            *rear++ = root.ch[i];
        }
    while (fore < rear) {
        Node *x = *fore++;
        if (x->pi->flag) x->flag = true;
        for (int i = 0; i < 256; i++)
            if (!x->ch[i])
                x->ch[i] = x->pi->ch[i];
            else {
                x->ch[i]->pi = x->pi->ch[i];
                *rear++ = x->ch[i];
            }
    }
    free(q);
}

bool check(pid_t pid, unsigned long bgn, unsigned long end)
{
    char filename[1000];
    if (!buf || end-bgn > bufsize) {
        buf = (char *)realloc(buf, end-bgn);
        bufsize = end-bgn;
        if (!buf) return false;
    }

    snprintf(filename, sizeof(filename), "/proc/%d/mem", (int)pid);
    int fd = open(filename, O_RDONLY);
    if (fd == -1) return false;
    if (lseek64(fd, bgn, SEEK_SET) == -1 || read(fd, buf, end-bgn) != end-bgn) {
        close(fd);
        return false;
    }

    Node *x = &root;
    for (char *p = buf; p != buf+(end-bgn); p++) {
        x = x->ch[(unsigned char)*p];
        if (x->flag) {
            close(fd);
            return true;
        }
    }
    close(fd);
    return false;
}

void init()
{
    DIR *dp = opendir(configdir);
    struct dirent *dirp;
    if (dp == NULL) return;
    chdir(configdir);
    while (dirp = readdir(dp)) {
        int fd = open(dirp->d_name, O_RDONLY);
        if (fd == -1) continue;
        off_t size = lseek(fd, 0, SEEK_END);
        if (size <= 0) {
            close(fd);
            continue;
        }

        if (!buf || size > bufsize) {
            buf = (char *)realloc(buf, size);
            bufsize = size;
            if (!buf) {
                close(fd);
                continue;
            }
        }
        if (pread(fd, buf, size, 0) != size) {
            close(fd);
            continue;
        }
        printf("reading config file: %s/%s\n", configdir, dirp->d_name);
        if (!strcmp(dirp->d_name, "ignore.lst")) {
            FILE *fp = fdopen(fd, "r");
            fseek(fp, 0, SEEK_SET);
            while (fgets(buf, bufsize, fp)) {
                if (strlen(buf) <= 1) continue;
                List *elem = (List *)malloc(sizeof(List));
                elem->next = ignored_prefix;
                elem->cmd = strndup(buf, strlen(buf)-1);
                ignored_prefix = elem;
            }
            fclose(fp);
        } else
            aho_corasick_insert(buf, size);
        close(fd);
    }
    closedir(dp);
    aho_corasick_build();
}

void run()
{
    char buf[1000], cmdline[1000];
    DIR *dp = opendir("/proc");
    if (dp == NULL) return;
    struct dirent *dirp;
    int n, fd;
    FILE *fp;
    while (dirp = readdir(dp)) {
        pid_t pid = atoi(dirp->d_name);
        if (!pid || pid == getpid()) continue;

        bool ignore = false;
        snprintf(buf, sizeof(buf), "/proc/%s/cmdline", dirp->d_name);
        fd = open(buf, O_RDONLY);
        if (fd == -1) continue;
        if ((n = read(fd, cmdline, sizeof(cmdline))) < 0) {
            close(fd);
            continue;
        }
        close(fd);
        for (List *i = ignored_prefix; i; i = i->next)
            if (memmem(cmdline, strlen(cmdline), i->cmd, strlen(i->cmd)) == cmdline) {
                ignore = true;
                break;
            }
        if (ignore) continue;

        unsigned long bgn, end;
        sprintf(buf, "/proc/%s/maps", dirp->d_name);
        if ((fp = fopen(buf, "r")) == NULL) continue;
        if (ptrace(PTRACE_ATTACH, pid, NULL, NULL) == -1 || kill(pid, SIGCONT) == -1) {
            fclose(fp);
            ptrace(PTRACE_DETACH, pid, NULL, NULL);
            continue;
        }
        while (fscanf(fp, "%lx-%lx%*s%*s%*s%*s%[^\n]\n", &bgn, &end, buf) == 3)
            if (strchr(buf, '/') == NULL && check(pid, bgn, end)) {
                printf("killing %d\t%s\trange %lx-%lx\t%s\n", (int)pid, cmdline, bgn, end, buf);
#ifndef DEBUG
                kill(pid, SIGTERM);
#endif
                break;
            }
        fclose(fp);
        ptrace(PTRACE_DETACH, pid, NULL, NULL);
    }
    closedir(dp);
}

int main()
{
    init();
    for(;;) {
        run();
        sleep(60);
    }
}
