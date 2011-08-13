#include <algorithm>
#include <climits>
#include <cstdio>
#include <cstring>
#include <queue>
#include <utility>
#include <vector>
using namespace std;
typedef long long ll;
typedef pair<int, int> pii;

const int N = 1000;
struct Node {
    char name[21];
    Node *lchild, *rchild;
    int x, mark, llen, rlen, childs;
    vector<pii> *tree;
} a[N];

int main()
{
    int n;
    scanf("%d", &n);
    for (int i = 0; i < n; i++) {
        scanf("%s", a[i].name);
        a[i].llen = (strlen(a[i].name)-1)/2;
        a[i].rlen = strlen(a[i].name)/2;
        if (i) {
            int parent;
            scanf("%d", &parent);
            if (!a[parent].childs++) a[parent].lchild = a+i;
            else a[parent].rchild = a+i;
        }
    }

    for (Node *i = a+n; --i >= a; ) {
        switch (i->childs) {
        case 0:
            i->x = 0;
            i->tree = new vector<pii>;
            break;
        case 1:
            i->x = i->lchild->x;
            i->tree = i->lchild->tree;
            break;
        case 2:
            vector<pii> *left = i->lchild->tree, *right = i->rchild->tree;
            int m = (int)min(left->size(), right->size()), move = INT_MIN;
            for (int j = 1; j <= m; j++)
                move = max(move, (*left)[left->size()-j].second-(*right)[right->size()-j].first+2);
            if (left->size() < right->size()) {
                i->tree = right;
                i->lchild->x -= move;
                i->lchild->mark -= move;
                for (int j = 1; j <= m; j++)
                    (*right)[right->size()-j].first = (*left)[left->size()-j].first-move;
            } else {
                i->tree = left;
                i->rchild->x += move;
                i->rchild->mark += move;
                for (int j = 1; j <= m; j++)
                    (*left)[left->size()-j].second = (*right)[right->size()-j].second+move;
            }
            i->x = (i->lchild->x+i->rchild->x)/2;
        }
        i->tree->push_back(pii(i->x-i->llen, i->x+i->rlen));
    }

    for (Node *i = a; i < a+n; i++) {
        if (i->lchild) i->lchild->x += i->mark, i->lchild->mark += i->mark;
        if (i->rchild) i->rchild->x += i->mark, i->rchild->mark += i->mark;
    }
    int m = INT_MAX;
    for (Node *i = a; i < a+n; i++)
        m = min(m, i->x-i->llen);
    for (Node *i = a; i < a+n; i++)
        i->x -= m;

    int last_depth = 0, last_column = 0;
    queue<pii> q;
    vector<pii> segments;
    q.push(pii(0, 0));
    while (!q.empty()) {
        int u = q.front().first, depth = q.front().second;
        q.pop();
        if (last_depth < depth) {
            last_depth = depth;
            puts("");
            last_column = 0;
            for (vector<pii>::const_iterator it = segments.begin(); it != segments.end(); it++) {
                int column = (it->first+it->second)/2;
                printf("%*s|", column-last_column, "");
                last_column = column+1;
            }
            puts("");
            last_column = 0;
            for (vector<pii>::const_iterator it = segments.begin(); it != segments.end(); it++) {
                printf("%*s", it->first-last_column, "");
                for (int i = it->first; i <= it->second; i++)
                    putchar(i == it->first || i == (it->first+it->second)/2 || i == it->second ? '+' : '-');
                last_column = it->second+1;
            }
            puts("");
            last_column = 0;
            for (vector<pii>::const_iterator it = segments.begin(); it != segments.end(); it++) {
                printf("%*s|", it->first-last_column, "");
                last_column = it->first+1;
                if (it->first < it->second) {
                    printf("%*s|", it->second-last_column, "");
                    last_column = it->second+1;
                }
            }
            puts("");
            last_column = 0;
            segments.clear();
        }
        printf("%*s%s", a[u].x-a[u].llen-last_column, "", a[u].name);
        last_column = a[u].x+a[u].rlen+1;
        if (a[u].lchild) {
            q.push(pii(a[u].lchild-a, depth+1));
            if (a[u].rchild) q.push(pii(a[u].rchild-a, depth+1)), segments.push_back(pii(a[u].lchild->x, a[u].rchild->x));
            else segments.push_back(pii(a[u].lchild->x, a[u].lchild->x));
        }
    }
}
