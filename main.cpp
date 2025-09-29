#pragma GCC optimize "-O3,omit-frame-pointer,inline,unroll-all-loops,fast-math"
#include <bits/stdc++.h>
using namespace std;

// ===== Constants / Mapping =====
enum Cell : int {
    EMPTY = 0,
    TREE = 1,
    PATH = 2,
    PATH_2 = 3,
    NEW_TREE = 4,
    START = 5,
    GOAL = 6,
    HIDDEN_TREE = 7,
};

static inline char cellToChar(int v){
    switch(v){
        case EMPTY: return '.';
        case TREE: return 'T';
        case PATH: return '*';
        case PATH_2: return '@';
        case NEW_TREE: return '#';
        case START: return 'S';
        case GOAL: return 'X';
        case HIDDEN_TREE: return 'H';
        default: return '?';
    }
}

static inline int charToCell(char c){
    switch(c){
        case '.': return EMPTY;
        case 'T': return TREE;
        case '*': return PATH;
        case '@': return PATH_2;
        case '#': return NEW_TREE;
        case 'S': return START;
        case 'X': return GOAL;
        default: return EMPTY;
    }
}

static constexpr int NUM_EVALUATIONS = 2;

// ===== Board =====
struct Board {
    int n;
    int start_pos;
    int goal_pos;
    vector<int> state;
    bool is_up_down_reversed;
    bool is_left_right_reversed;

    Board(int n_, int start_i, int start_j, int ti, int tj, const vector<string>& initial_board)
        : n(n_), start_pos(_to_1d(start_i, start_j)), goal_pos(_to_1d(ti, tj)),
          state(), is_up_down_reversed(false), is_left_right_reversed(false) {
        state.reserve(n * n);
        for(int i=0;i<n;i++){
            for(int j=0;j<n;j++){
                state.push_back(charToCell(initial_board[i][j]));
            }
        }
        state[start_pos] = START;
        state[goal_pos] = GOAL;
    }

    inline int _to_1d(int i, int j) const { return i * n + j; }
    inline pair<int,int> to_2d(int v) const { return {v / n, v % n}; }

    inline int get_state(int x, int y) const { return state[_to_1d(x,y)]; }
    inline void set_state(int x, int y, int s){ state[_to_1d(x,y)] = s; }

    void reverse_up_down(){
        is_up_down_reversed = !is_up_down_reversed;
        for(int i1=0;i1<n;i1++){
            int i2 = n - 1 - i1;
            if(i1 >= i2) break;
            for(int j=0;j<n;j++){
                swap(state[_to_1d(i1,j)], state[_to_1d(i2,j)]);
            }
        }
        auto [sx, sy] = to_2d(start_pos);
        start_pos = _to_1d(n-1-sx, sy);
        auto [gx, gy] = to_2d(goal_pos);
        goal_pos = _to_1d(n-1-gx, gy);
    }

    void reverse_left_right(){
        is_left_right_reversed = !is_left_right_reversed;
        for(int i=0;i<n;i++){
            for(int j1=0;j1<n;j1++){
                int j2 = n - 1 - j1;
                if(j1 >= j2) break;
                swap(state[_to_1d(i,j1)], state[_to_1d(i,j2)]);
            }
        }
        auto [sx, sy] = to_2d(start_pos);
        start_pos = _to_1d(sx, n-1-sy);
        auto [gx, gy] = to_2d(goal_pos);
        goal_pos = _to_1d(gx, n-1-gy);
    }

    void output() const {
        vector<pair<int,int>> new_trees;
        new_trees.reserve(n*n/2);
        for(int i=0;i<n;i++){
            for(int j=0;j<n;j++){
                if(get_state(i,j) == NEW_TREE){
                    new_trees.emplace_back(i,j);
                }
            }
        }
        cout << new_trees.size();
        if(!new_trees.empty()) cout << ' ';
        for(size_t k=0;k<new_trees.size();k++){
            if(k) cout << ' ';
            cout << new_trees[k].first << ' ' << new_trees[k].second;
        }
        cout << "\n";
    }

    void debug_output() const {
        // 盤面をデバッグ出力
        cerr << "Board (n=" << n << "):\n";
        for(int i=0;i<n;i++){
            for(int j=0;j<n;j++){
                int s = get_state(i,j);
                if(_to_1d(i,j) == start_pos) {
                    cerr << 'S';
                } else if(_to_1d(i,j) == goal_pos) {
                    cerr << 'X';
                } else if(s == EMPTY || s == PATH || s == PATH_2) {
                    cerr << '.';
                } else if(s == TREE) {
                    cerr << 'T';
                } else if(s == NEW_TREE) {
                    cerr << '#';
                } else {
                    cerr << '?';
                }
            }
            cerr << '\n';
        }
        cerr << '\n';
    }
};

// ===== Random Engine =====
static std::mt19937 rng((uint32_t)chrono::steady_clock::now().time_since_epoch().count());

// ===== Step0Constructor =====
struct Step0Constructor {
    int max_distance;
    Step0Constructor(int max_distance_=5, optional<unsigned> seed = nullopt)
        : max_distance(max_distance_) { if(seed) rng.seed(*seed); }

    Board construct(Board board){
        auto [start_i, start_j] = board.to_2d(board.start_pos);
        auto [ti, tj] = _find_random_target(board, start_i, start_j);
        if(ti == -1) return board;

        vector<pair<int,int>> path = _find_path_bfs(board, start_i, start_j, ti, tj);
        if(path.empty() || (int)path.size() > max_distance) return board;

        _apply_path_to_board(board, path);
        _surround_path_with_trees(board, path);
        _recover_path_to_board(board, path);
        return board;
    }

    pair<int,int> _find_random_target(const Board& board, int start_i, int start_j){
        vector<pair<int,int>> cand; cand.reserve(32);
        for(int i=0;i<min(2, board.n);i++){
            for(int j=max(0, start_j-3); j<min(board.n, start_j+4); j++){
                if(board.get_state(i,j) == EMPTY){
                    cand.emplace_back(i,j);
                }
            }
        }
        if(cand.empty()) return {-1,-1};
        uniform_int_distribution<int> dist(0, (int)cand.size()-1);
        return cand[dist(rng)];
    }

    vector<pair<int,int>> _find_path_bfs(const Board& board, int si, int sj, int ti, int tj){
        const int n = board.n;
        deque<tuple<int,int, vector<pair<int,int>>>> q;
        q.emplace_back(si, sj, vector<pair<int,int>>{{si,sj}});
        vector<vector<char>> vis(n, vector<char>(n, 0));
        vis[si][sj] = 1;
        const int d4[4][2] = {{0,1},{0,-1},{1,0},{-1,0}};

        while(!q.empty()){
            auto [ci,cj,path] = std::move(q.front()); q.pop_front();
            if(ci==ti && cj==tj) return path;
            for(auto& d: d4){
                int ni=ci+d[0], nj=cj+d[1];
                if(ni<0||nj<0||ni>=n||nj>=n) continue;
                if(vis[ni][nj]) continue;
                int st = board.get_state(ni,nj);
                if(st==EMPTY || (ni==ti && nj==tj)){
                    vis[ni][nj]=1;
                    auto new_path = path; new_path.emplace_back(ni,nj);
                    q.emplace_back(ni,nj, std::move(new_path));
                }
            }
        }
        return {};
    }

    void _apply_path_to_board(Board& board, const vector<pair<int,int>>& path){
        for(size_t i=0;i<path.size();i++){
            if(i==0) continue;
            auto [x,y] = path[i];
            if(board.get_state(x,y)==EMPTY) board.set_state(x,y, PATH);
        }
    }
    void _recover_path_to_board(Board& board, const vector<pair<int,int>>& path){
        for(size_t i=0;i<path.size();i++){
            if(i==0) continue;
            auto [x,y] = path[i];
            board.set_state(x,y, EMPTY);
        }
    }
    void _surround_path_with_trees(Board& board, const vector<pair<int,int>>& path){
        const int d4[4][2]={{-1,0},{0,-1},{0,1},{1,0}};
        for(size_t i=0;i<path.size();i++){
            if(i+1==path.size()) continue;
            auto [pi,pj]=path[i];
            for(auto& d: d4){
                int ni=pi+d[0], nj=pj+d[1];
                if(ni<0||nj<0||ni>=board.n||nj>=board.n) continue;
                if(board.get_state(ni,nj)==EMPTY) board.set_state(ni,nj, NEW_TREE);
            }
        }
    }
};

// ===== Step1Constructor =====
struct Step1Constructor {
    struct Pattern {
        vector<pair<int,int>> trees;
        vector<pair<int,int>> paths;
    };
    vector<Pattern> PATTERNS;
    vector<Pattern> PATTERNS_2;
    Step1Constructor(){
        PATTERNS.reserve(8);
        PATTERNS.push_back({{{-2,0},{-1,1},{0,-1},{0,1},{1,0}}, {{-1,-1},{-1,0}}});
        PATTERNS.push_back({{{-2,0},{-1,-1},{0,-1},{0,1},{1,0}}, {{-1,0},{-1,1}}});
        PATTERNS.push_back({{{-1,0},{0,-1},{0,1},{1,1},{2,0}}, {{1,-1},{1,0}}});
        PATTERNS.push_back({{{-1,0},{0,-1},{0,1},{1,-1},{2,0}}, {{1,0},{1,1}}});
        PATTERNS.push_back({{{-1,0},{0,-2},{0,1},{1,-1},{1,0}}, {{-1,-1},{0,-1}}});
        PATTERNS.push_back({{{-1,-1},{-1,0},{0,-2},{0,1},{1,0}}, {{0,-1},{1,-1}}});
        PATTERNS.push_back({{{-1,0},{0,-1},{0,2},{1,0},{1,1}}, {{-1,1},{0,1}}});
        PATTERNS.push_back({{{-1,0},{-1,1},{0,-1},{0,2},{1,0}}, {{0,1},{1,1}}});
        PATTERNS_2.reserve(8);
        PATTERNS_2.push_back({{{-3,0},{-2,1},{0,-1},{0,1},{1,0},{-1,-1},{-1,1}}, {{-2,-1},{-2,0},{-1,0}}});
        PATTERNS_2.push_back({{{3,0},{2,1},{0,-1},{0,1},{-1,0},{1,-1},{1,1}}, {{2,-1},{2,0},{1,0}}});
        PATTERNS_2.push_back({{{-3,0},{-2,-1},{0,1},{0,-1},{1,0},{-1,1},{-1,-1}}, {{-2,1},{-2,0},{-1,0}}});
        PATTERNS_2.push_back({{{3,0},{2,-1},{0,1},{0,-1},{-1,0},{1,1},{1,-1}}, {{2,1},{2,0},{1,0}}});
        PATTERNS_2.push_back({{{0,-3},{1,-2},{-1,0},{1,0},{0,1},{-1,-1},{1,-1}}, {{-1,-2},{0,-2},{0,-1}}});
        PATTERNS_2.push_back({{{0,-3},{-1,-2},{1,0},{-1,0},{0,1},{1,-1},{-1,-1}}, {{1,-2},{0,-2},{0,-1}}});
        PATTERNS_2.push_back({{{0,3},{1,2},{-1,0},{1,0},{0,-1},{-1,1},{1,1}}, {{-1,2},{0,2},{0,1}}});
        PATTERNS_2.push_back({{{0,3},{-1,2},{1,0},{-1,0},{0,-1},{1,1},{-1,1}}, {{1,2},{0,2},{0,1}}});
    }

    optional<Board> random_construct(Board board){
        // Try random order until one fits
        vector<int> idx(PATTERNS.size());
        iota(idx.begin(), idx.end(), 0);
        shuffle(idx.begin(), idx.end(), rng);
        for(int id: idx){
            if(can_apply_pattern(board, id)){
                return construct(board, id);
            }
        }
        idx.clear();
        idx.reserve(PATTERNS_2.size());
        iota(idx.begin(), idx.end(), 0);
        shuffle(idx.begin(), idx.end(), rng);
        for(int id: idx){
            if(can_apply_pattern2(board, id)){
                return construct2(board, id);
            }
        }
        return nullopt;
    }

    bool can_apply_pattern(const Board& board, int idx) const {
        return _can_apply_pattern(board, PATTERNS[idx]);
    }

    optional<Board> construct(Board board, int idx){
        auto [gi, gj] = board.to_2d(board.goal_pos);
        if(!_can_apply_pattern(board, PATTERNS[idx])) return nullopt;
        return _apply_pattern(board, gi, gj, PATTERNS[idx]);
    }

    bool can_apply_pattern2(const Board& board, int idx) const {
        return _can_apply_pattern(board, PATTERNS_2[idx]);
    }

    optional<Board> construct2(Board board, int idx){
        auto [gi, gj] = board.to_2d(board.goal_pos);
        if(!_can_apply_pattern(board, PATTERNS_2[idx])) return nullopt;
        return _apply_pattern(board, gi, gj, PATTERNS_2[idx]);
    }


    bool _can_apply_pattern(const Board& board, const Pattern& p) const {
        auto [ti,tj] = board.to_2d(board.goal_pos);
        for(auto [di,dj]: p.paths){
            int ni=ti+di, nj=tj+dj;
            if(ni<0||nj<0||ni>=board.n||nj>=board.n) return false;
            if(board.get_state(ni,nj)==TREE) return false;
        }
        // trees: out of board is allowed (skip), otherwise always ok
        return true;
    }

    Board _apply_pattern(Board board, int ti, int tj, const Pattern& p){
        for(auto [di,dj]: p.trees){
            int ni=ti+di, nj=tj+dj;
            if(ni<0||nj<0||ni>=board.n||nj>=board.n) continue;
            if(board.get_state(ni,nj)==TREE) continue;
            board.set_state(ni,nj, NEW_TREE);
        }
        return board;
    }
};

// ===== Step2Constructor =====
struct Step2Constructor {
    int penalty;
    int max_width;
    int L;
    int N, R;
    int edge_size;
    // dp[i][l][r]
    vector<vector<vector<double>>> dp;
    vector<vector<vector<pair<int,int>>>> parent;

    Step2Constructor(int penalty_=6, int max_width_=8)
        : penalty(penalty_), max_width(max_width_), L(0), N(0), R(0), edge_size(0) {}

    Board construct(Board board, int path_type, int edge_size_){
        edge_size = edge_size_;
        auto res = _solve(board);
        if(!res.first.has_value()) return board;
        return _apply_path_to_board(board, *res.first, path_type);
    }

    bool _is_passable(const Board& board, int i, int j) const {
        if(i<0||j<0||i>=board.n||j>=board.n) return false;
        int st = board.get_state(i,j);
        return st==EMPTY || st==PATH;
    }

    pair<optional<vector<tuple<int,int,int>>>, optional<double>>
    _solve(const Board& board){
        N = board.n;
        R = min(max_width, board.n);
        const double INF = 1e100;

        dp.assign(N, vector<vector<double>>(R, vector<double>(R, INF)));
        parent.assign(N, vector<vector<pair<int,int>>>(R, vector<pair<int,int>>(R, {-1,-1})));

        _initialize(board, INF);
        _transition(board, INF);
        return _reconstruct_path(INF);
    }

    void _initialize(const Board& board, double INF){
        for(int l=L; l<R; l++){
            for(int r=l; r<R; r++){
                bool valid=true;
                for(int j=l;j<=r;j++){
                    if(!_is_passable(board,0,j)){ valid=false; break; }
                }
                if(valid){
                    dp[0][l][r] = r;
                    if(l<edge_size-1) {
                        dp[0][l][r] += penalty;
                    }
                    else if(l<edge_size) {
                        dp[0][l][r] += 2;
                    }
                    parent[0][l][r] = {-1,-1};
                }
            }
        }
    }

    void _transition(const Board& board, double INF){
        for(int i=1;i<N;i++){
            // pattern1: (l,r) -> (r,r2)
            for(int r=L;r<R;r++){
                double min_r = INF;
                int argl = -1;
                for(int l=L;l<=r;l++){
                    if(dp[i-1][l][r] < min_r){ min_r = dp[i-1][l][r]; argl=l; }
                }
                if(min_r < INF){
                    for(int r2=r;r2<R;r2++){
                        if(!_is_passable(board,i,r2)) break;
                        double nc = min_r + r2;
                        if(r<edge_size-1) {
                            nc += penalty;
                        }
                        else if(r<edge_size) {
                            nc += 2;
                        }
                        if(nc < dp[i][r][r2]){
                            dp[i][r][r2] = nc;
                            // find parent with min value
                            int chosen_l = -1;
                            for(int l=L;l<=r;l++){
                                if(dp[i-1][l][r] == min_r){ chosen_l = l; break; }
                            }
                            parent[i][r][r2] = {chosen_l, r};
                        }
                    }
                }
            }
            // pattern2: (l,r) -> (l2,r)
            for(int l=L;l<R;l++){
                double min_l = INF;
                int argr = -1;
                for(int r=l;r<R;r++){
                    if(dp[i-1][l][r] < min_l){ min_l = dp[i-1][l][r]; argr=r; }
                }
                if(min_l < INF){
                    for(int l2=l; l2>=L; l2--){
                        if(!_is_passable(board,i,l2)) break;
                        double nc = min_l + l;
                        if(l2<edge_size-1) {
                            nc += penalty;
                        }
                        else if(l2<edge_size) {
                            nc += 2;
                        }
                        if(nc < dp[i][l2][l]){
                            dp[i][l2][l] = nc;
                            int chosen_r = -1;
                            for(int r=l;r<R;r++){
                                if(dp[i-1][l][r] == min_l){ chosen_r = r; break; }
                            }
                            parent[i][l2][l] = {l, chosen_r};
                        }
                    }
                }
            }
        }
    }

    pair<optional<vector<tuple<int,int,int>>>, optional<double>>
    _reconstruct_path(double INF){
        double min_cost = INF; int best_l=-1,best_r=-1,best_i=-1;
        for(int i=N-1;i>=0;i--){
            for(int l=L;l<R;l++){
                for(int r=l;r<R;r++){
                    if(dp[i][l][r] < min_cost){
                        min_cost = dp[i][l][r];
                        best_l=l; best_r=r; best_i=i;
                    }
                }
            }
            if(min_cost<INF) break;
        }
        if(min_cost==INF) return {nullopt, nullopt};

        vector<tuple<int,int,int>> path_ranges;
        path_ranges.reserve(N);
        int cl=best_l, cr=best_r, ci=best_i;
        for(int i=ci;i>=0;i--){
            path_ranges.emplace_back(i,cl,cr);
            if(i>0 && parent[i][cl][cr].first!=-1){
                auto pr = parent[i][cl][cr];
                cl = pr.first; cr = pr.second;
            }else if(i>0){
                // fallback (rare)
                bool found=false;
                for(int l=L;l<R;l++){
                    for(int r=l;r<R;r++){
                        if(dp[i-1][l][r] + cr == dp[i][cl][cr]){
                            cl=l; cr=r; found=true; break;
                        }
                    }
                    if(found) break;
                }
            }
        }
        reverse(path_ranges.begin(), path_ranges.end());
        return {path_ranges, min_cost};
    }

    Board _apply_path_to_board(Board board, const vector<tuple<int,int,int>>& ranges, int tree_type){
        for(auto [i,l,r]: ranges){
            for(int j=l;j<=r;j++){
                if(board.get_state(i,j)==EMPTY) board.set_state(i,j, tree_type);
            }
        }
        return board;
    }
};

// ===== Step3Constructor =====
struct Step3Constructor {
    int N;
    vector<vector<vector<double>>> dp;
    vector<vector<vector<pair<int,int>>>> parent;

    Step3Constructor(): N(0) {}

    pair<Board,bool> construct(Board board, int path_type, int start_i = 0){
        N = board.n;
        auto ranges = _calculate_ranges(board);

        auto [si,sj] = _find_starting_point(board, ranges, start_i);
        if(si==-1) return {board, true};
        ranges[si].first -= 2;

        _initialize_dp(board, ranges, si, sj);
        _process_dp(board, ranges, si);

        auto path_ranges = _reconstruct_path(ranges, si);
        if(path_ranges.empty()){
            return construct(board, path_type, start_i+1);
        }
        return _apply_path_to_board(board, path_ranges, path_type);
    }

    vector<pair<int,int>> _calculate_ranges(const Board& board){
        vector<pair<int,int>> ranges; ranges.reserve(N);
        for(int i=0;i<N;i++){
            int left = 2;
            for(int j=board.n-1;j>=0;j--){
                if(board.get_state(i,j)==PATH) break;
                int up = (i-1>=0? board.get_state(i-1,j): -1);
                int lf = (j-1>=0? board.get_state(i,j-1): -1);
                int dn = (i+1<board.n? board.get_state(i+1,j): -1);
                if(up==PATH || lf==PATH || dn==PATH) continue;
                left=j;
            }
            int right = min(board.n-1, left + 12);
            ranges.emplace_back(left, right);
        }
        return ranges;
    }

    pair<int,int> _find_starting_point(const Board& board, const vector<pair<int,int>>& ranges, int start_i){
        for(int i=start_i;i<N-1;i++){
            int left = ranges[i].first;
            int left2_state = (left-3>=0? board.get_state(i,left-2): -1);
            if(left2_state == PATH) return {i, left-2};
        }
        return {-1,-1};
    }

    void _initialize_dp(const Board& board, const vector<pair<int,int>>& ranges, int si, int sj){
        const double INF = 1e100;
        dp.assign(N, vector<vector<double>>(N, vector<double>(N, INF)));
        parent.assign(N, vector<vector<pair<int,int>>>(N, vector<pair<int,int>>(N, {-1,-1})));
        int l = sj;
        for(int r=sj+1; r<ranges[si].second; r++){
            if(!_is_passable(board, si, r)) break;
            dp[si][l][r] = r;
            parent[si][l][r] = {-1,-1};
        }
    }

    bool _is_passable(const Board& board, int i, int j) const {
        if(i<0||j<0||i>=board.n||j>=board.n) return false;
        return board.get_state(i,j)==EMPTY;
    }

    void _process_dp(const Board& board, const vector<pair<int,int>>& ranges, int si){
        const double INF = 1e100;
        for(int i=si+1;i<N;i++){
            // pattern1
            for(int r=ranges[i-1].first; r<ranges[i-1].second; r++){
                if(!(ranges[i].first <= r && r < ranges[i].second)) continue;
                double min_r = INF; int argl=-1;
                for(int l=ranges[i-1].first ;l<=r;l++){
                    if(l>ranges[i-1].second) break;
                    if(dp[i-1][l][r] < min_r){ min_r = dp[i-1][l][r]; argl=l; }
                }
                if(min_r<INF){
                    for(int r2=r; r2<ranges[i].second; r2++){
                        if(!_is_passable(board,i,r2)) break;
                        double nc = min_r + r2;
                        if(nc < dp[i][r][r2]){
                            dp[i][r][r2] = nc;
                            parent[i][r][r2] = {argl, r};
                        }
                    }
                }
            }
            // pattern2
            for(int l=ranges[i-1].first; l<ranges[i-1].second; l++){
                if(!(ranges[i].first <= l && l < ranges[i].second)) continue;
                double min_l = 1e100; int argr=-1;
                for(int r=l; r<ranges[i-1].second; r++){
                    if(dp[i-1][l][r] < min_l){ min_l = dp[i-1][l][r]; argr=r; }
                }
                if(min_l<1e100){
                    for(int l2=l; l2>=ranges[i].first; l2--){
                        if(!_is_passable(board,i,l2)) break;
                        double nc = min_l + l;
                        if(nc < dp[i][l2][l]){
                            dp[i][l2][l] = nc;
                            parent[i][l2][l] = {l, argr};
                        }
                        if(i >= N-2) break;
                    }
                }
            }
        }
    }

    vector<tuple<int,int,int>> _reconstruct_path(const vector<pair<int,int>>& ranges, int si){
        const double INF = 1e100;
        double best = INF; int bl=-1, br=-1, bi=-1;
        for(int i=N-1; i> N/2; i--){
            for(int l=ranges[i].first; l<ranges[i].second; l++){
                for(int r=l; r<ranges[i].second; r++){
                    if(dp[i][l][r] < best){ best = dp[i][l][r]; bl=l; br=r; bi=i; }
                }
            }
            if(best<INF) break;
        }
        if(best==INF) return {};
        vector<tuple<int,int,int>> out;
        int cl=bl, cr=br, ci=bi;
        while(ci>=si){
            out.emplace_back(ci,cl,cr);
            if(ci>si && parent[ci][cl][cr].first!=-1){
                auto pr = parent[ci][cl][cr];
                cl=pr.first; cr=pr.second; ci--;
            }else break;
        }
        reverse(out.begin(), out.end());
        return out;
    }

    pair<Board,bool> _apply_path_to_board(Board board, const vector<tuple<int,int,int>>& ranges, int path_type){
        for(auto [i,l,r]: ranges){
            for(int j=l;j<=r;j++){
                if(board.get_state(i,j)==EMPTY){
                    board.set_state(i,j, path_type);
                    if(j+1<board.n && board.get_state(i,j+1)==PATH_2){
                        return {board, true};
                    }
                }
            }
        }
        return {board, false};
    }
};

// ===== Step4Constructor =====
struct Step4Constructor {
    Board construct(Board board){
        _convert_path2_to_path(board);
        _connect_start_to_path(board);
        _connect_goal_to_path(board);
        return board;
    }

    void _convert_path2_to_path(Board& board){
        for(int i=0;i<board.n;i++)
            for(int j=0;j<board.n;j++)
                if(board.get_state(i,j)==PATH_2) board.set_state(i,j, PATH);
    }

    void _connect_start_to_path(Board& board){
        auto [si,sj] = board.to_2d(board.start_pos);
        auto path_positions = _find_path_positions(board);
        if(path_positions.empty()) return;
        auto [ti,tj] = _find_nearest_path(board, si, sj, path_positions);
        if(ti==-1) return;
        auto conn = _find_connection_path_bfs(board, si, sj, ti, tj);
        if(!conn.empty()) _apply_connection_path(board, conn);
    }

    void _connect_goal_to_path(Board& board){
        auto [gi,gj] = board.to_2d(board.goal_pos);
        auto path_positions = _find_path_positions(board);
        if(path_positions.empty()) return;
        auto [ti,tj] = _find_nearest_path(board, gi, gj, path_positions);
        if(ti==-1) return;
        auto conn = _find_connection_path_bfs(board, gi, gj, ti, tj);
        if(!conn.empty()) _apply_connection_path(board, conn);
    }

    vector<pair<int,int>> _find_path_positions(const Board& board){
        vector<pair<int,int>> v;
        v.reserve(board.n*board.n/4);
        for(int i=0;i<board.n;i++)
            for(int j=0;j<board.n;j++)
                if(board.get_state(i,j)==PATH) v.emplace_back(i,j);
        return v;
    }

    pair<int,int> _find_nearest_path(const Board& board, int fi, int fj, const vector<pair<int,int>>& paths){
        if(paths.empty()) return {-1,-1};
        int n=board.n;
        deque<tuple<int,int,int>> q;
        vector<vector<char>> vis(n, vector<char>(n,0));
        q.emplace_back(fi,fj,0); vis[fi][fj]=1;
        const int d4[4][2]={{0,1},{0,-1},{1,0},{-1,0}};
        unordered_set<long long> pathset;
        pathset.reserve(paths.size()*2);
        auto enc=[&](int x,int y)->long long{return ( (long long)x<<32 ) ^ (unsigned long long)y;};
        for(auto &p: paths) pathset.insert(enc(p.first,p.second));

        while(!q.empty()){
            auto [ci,cj,dist]=q.front(); q.pop_front();
            if(pathset.count(enc(ci,cj))) return {ci,cj};
            for(auto& d: d4){
                int ni=ci+d[0], nj=cj+d[1];
                if(ni<0||nj<0||ni>=n||nj>=n) continue;
                if(vis[ni][nj]) continue;
                int st = board.get_state(ni,nj);
                bool is_target = pathset.count(enc(ni,nj));
                if(_is_passable_for_connection(st, is_target)){
                    vis[ni][nj]=1;
                    q.emplace_back(ni,nj,dist+1);
                }
            }
        }
        return {-1,-1};
    }

    vector<pair<int,int>> _find_connection_path_bfs(const Board& board, int si, int sj, int ti, int tj){
        int n=board.n;
        deque<tuple<int,int,vector<pair<int,int>>>> q;
        q.emplace_back(si,sj, vector<pair<int,int>>{{si,sj}});
        vector<vector<char>> vis(n, vector<char>(n,0)); vis[si][sj]=1;
        const int d4[4][2]={{0,1},{0,-1},{1,0},{-1,0}};
        while(!q.empty()){
            auto [ci,cj,path]=std::move(q.front()); q.pop_front();
            if(ci==ti && cj==tj) return path;
            for(auto& d: d4){
                int ni=ci+d[0], nj=cj+d[1];
                if(ni<0||nj<0||ni>=n||nj>=n) continue;
                if(vis[ni][nj]) continue;
                int st = board.get_state(ni,nj);
                if(_is_passable_for_connection(st, (ni==ti && nj==tj))){
                    vis[ni][nj]=1;
                    auto np = path; np.emplace_back(ni,nj);
                    q.emplace_back(ni,nj, std::move(np));
                }
            }
        }
        return {};
    }

    bool _is_passable_for_connection(int st, bool is_target){
        if(is_target) return (st==EMPTY || st==PATH);
        return (st==EMPTY || st==START || st==GOAL);
    }

    void _apply_connection_path(Board& board, const vector<pair<int,int>>& path){
        for(size_t i=0;i<path.size();i++){
            if(i==0 || i+1==path.size()) continue;
            auto [x,y]=path[i];
            if(board.get_state(x,y)==EMPTY) board.set_state(x,y, PATH);
        }
    }
};

// ===== Step5Constructor =====
struct Step5Constructor {
    Board construct(Board board, bool use_hidden_tree = false){
        auto dist = _calculate_distances_from_start(board);
        auto path_positions = _get_path_positions_sorted_by_distance(board, dist);
        for(auto [pi,pj]: path_positions){
            if (_try_create_four_branch(board, pi, pj, use_hidden_tree)) {
                continue;
            }
            if (_try_create_three_branch(board, pi, pj, use_hidden_tree)) {
                continue;
            }
            if (_try_create_branch(board, pi, pj, use_hidden_tree)) {
                continue;
            }
        }
        if (use_hidden_tree){
            for(int i=0; i<board.n; ++i){
                for(int j=0; j<board.n; ++j){
                    if(board.get_state(i,j) == HIDDEN_TREE){
                        board.set_state(i,j, NEW_TREE);
                    }
                }
            }
        }
        for(auto [pi,pj]: path_positions){
            if (_try_create_four_branch(board, pi, pj, false)) {
                continue;
            }
            if (_try_create_three_branch(board, pi, pj, false)) {
                continue;
            }
            if (_try_create_branch(board, pi, pj, false)) {
                continue;
            }
        }
        return board;
    }

    unordered_map<long long,int> _calculate_distances_from_start(const Board& board){
        auto [si,sj] = board.to_2d(board.start_pos);
        deque<tuple<int,int,int>> q;
        q.emplace_back(si,sj,0);
        unordered_map<long long,int> dist; dist.reserve(board.n*board.n);
        vector<vector<char>> vis(board.n, vector<char>(board.n,0));
        vis[si][sj]=1; dist[((long long)si<<32) ^ (unsigned long long)sj]=0;
        const int d4[4][2]={{0,1},{0,-1},{1,0},{-1,0}};
        while(!q.empty()){
            auto [ci,cj,cd]=q.front(); q.pop_front();
            for(auto& d: d4){
                int ni=ci+d[0], nj=cj+d[1];
                if(ni<0||nj<0||ni>=board.n||nj>=board.n) continue;
                if(vis[ni][nj]) continue;
                int st = board.get_state(ni,nj);
                if(st==PATH || st==GOAL){
                    vis[ni][nj]=1;
                    dist[((long long)ni<<32) ^ (unsigned long long)nj]=cd+1;
                    q.emplace_back(ni,nj,cd+1);
                }
            }
        }
        return dist;
    }

    vector<pair<int,int>> _get_path_positions_sorted_by_distance(const Board& board, const unordered_map<long long,int>& dist){
        vector<pair<pair<int,int>, int>> v;
        v.reserve(board.n*board.n/2);
        for(int i=0;i<board.n;i++){
            for(int j=0;j<board.n;j++){
                if(board.get_state(i,j)==PATH){
                    long long key = ((long long)i<<32) ^ (unsigned long long)j;
                    auto it = dist.find(key);
                    int d = (it==dist.end()? INT_MAX : it->second);
                    v.push_back({{i,j}, d});
                }
            }
        }
        sort(v.begin(), v.end(), [](auto& a, auto& b){ return a.second > b.second; });
        vector<pair<int,int>> out; out.reserve(v.size());
        for(auto &e: v) out.push_back(e.first);
        return out;
    }

    bool _try_create_branch(Board& board, int pi, int pj, bool use_hidden_tree){
        const int d4[4][2]={{0,1},{0,-1},{1,0},{-1,0}};
        for(auto& d: d4){
            int ai=pi+d[0], aj=pj+d[1];
            int bi=pi+2*d[0], bj=pj+2*d[1];
            if(ai<0||aj<0||bi<0||bj<0||ai>=board.n||aj>=board.n||bi>=board.n||bj>=board.n) continue;
            if(!(board.get_state(ai,aj)==EMPTY && board.get_state(bi,bj)==EMPTY)) continue;
            if(!_check_no_adjacent_paths(board, ai,aj, pi,pj)) continue;
            if(!_check_no_adjacent_paths(board, bi,bj, pi,pj)) continue;
            _create_branch(board, ai,aj, bi,bj, use_hidden_tree);
            return true;
        }
        return false;
    }

    bool _try_create_three_branch(Board& board, int pi, int pj, bool use_hidden_tree){
        const int d4[4][2]={{0,1},{0,-1},{1,0},{-1,0}};
        for(auto& d: d4){
            int ai=pi+d[0], aj=pj+d[1];
            int bi=pi+2*d[0], bj=pj+2*d[1];
            int ci=pi+3*d[0], cj=pj+3*d[1];
            if(ai<0||aj<0||bi<0||bj<0||ci<0||cj<0||ai>=board.n||aj>=board.n||bi>=board.n||bj>=board.n||ci>=board.n||cj>=board.n) continue;
            if(!(board.get_state(ai,aj)==EMPTY && board.get_state(bi,bj)==EMPTY && board.get_state(ci,cj)==EMPTY)) continue;
            if(!_check_no_adjacent_paths(board, ai,aj, pi,pj)) continue;
            if(!_check_no_adjacent_paths(board, bi,bj, pi,pj)) continue;
            if(!_check_no_adjacent_paths(board, ci,cj, pi,pj)) continue;
            _create_three_branch(board, ai,aj, bi,bj, ci,cj, use_hidden_tree);
            return true;
        }
        return false;
    }
    bool _try_create_four_branch(Board& board, int pi, int pj, bool use_hidden_tree){
        const int d4[4][2]={{0,1},{0,-1},{1,0},{-1,0}};
        for(auto& d: d4){
            int ai=pi+d[0], aj=pj+d[1];
            int bi=pi+2*d[0], bj=pj+2*d[1];
            int ci=pi+3*d[0], cj=pj+3*d[1];
            int di=pi+4*d[0], dj=pj+4*d[1];
            if(ai<0||aj<0||bi<0||bj<0||ci<0||cj<0||di<0||dj<0||ai>=board.n||aj>=board.n||bi>=board.n||bj>=board.n||ci>=board.n||cj>=board.n||di>=board.n||dj>=board.n) continue;
            if(!(board.get_state(ai,aj)==EMPTY && board.get_state(bi,bj)==EMPTY && board.get_state(ci,cj)==EMPTY && board.get_state(di,dj)==EMPTY)) continue;
            if(!_check_no_adjacent_paths(board, ai,aj, pi,pj)) continue;
            if(!_check_no_adjacent_paths(board, bi,bj, pi,pj)) continue;
            if(!_check_no_adjacent_paths(board, ci,cj, pi,pj)) continue;
            if(!_check_no_adjacent_paths(board, di,dj, pi,pj)) continue;
            _create_four_branch(board, ai,aj, bi,bj, ci,cj, di,dj, use_hidden_tree);
            return true;
        }
        return false;
    }

    bool _check_no_adjacent_paths(const Board& board, int ci, int cj, int exi, int exj){
        const int d4[4][2]={{0,1},{0,-1},{1,0},{-1,0}};
        for(auto& d: d4){
            int ni=ci+d[0], nj=cj+d[1];
            if(ni<0||nj<0||ni>=board.n||nj>=board.n) continue;
            if(ni==exi && nj==exj) continue;
            if(board.get_state(ni,nj)==PATH || board.get_state(ni,nj)==HIDDEN_TREE) return false;
        }
        return true;
    }

    void _create_branch(Board& board, int ai, int aj, int bi, int bj, bool use_hidden_tree){
        board.set_state(ai,aj, PATH);
        board.set_state(bi,bj, PATH);
        _surround_with_trees(board, ai,aj, false);
        _surround_with_trees(board, bi,bj, use_hidden_tree);
    }

    void _create_three_branch(Board& board, int ai, int aj, int bi, int bj, int ci, int cj, bool use_hidden_tree){
        board.set_state(ai,aj, PATH);
        board.set_state(bi,bj, PATH);
        board.set_state(ci,cj, PATH);
        _surround_with_trees(board, ai,aj, false);
        _surround_with_trees(board, bi,bj, use_hidden_tree);
        _surround_with_trees(board, ci,cj, use_hidden_tree);
    }

    void _create_four_branch(Board& board, int ai, int aj, int bi, int bj, int ci, int cj, int di, int dj, bool use_hidden_tree){
        board.set_state(ai,aj, PATH);
        board.set_state(bi,bj, PATH);
        board.set_state(ci,cj, PATH);
        board.set_state(di,dj, PATH);
        _surround_with_trees(board, ai,aj, false);
        _surround_with_trees(board, bi,bj, use_hidden_tree);
        _surround_with_trees(board, ci,cj, use_hidden_tree);
        _surround_with_trees(board, di,dj, use_hidden_tree);
    }

    void _surround_with_trees(Board& board, int ci, int cj, bool hidden_tree = false){
        const int d4[4][2]={{-1,0},{0,-1},{0,1},{1,0}};
        for(auto& d: d4){
            int ni=ci+d[0], nj=cj+d[1];
            if(ni<0||nj<0||ni>=board.n||nj>=board.n) continue;
            if(board.get_state(ni,nj)==EMPTY){
                if (hidden_tree){
                    board.set_state(ni,nj, HIDDEN_TREE);
                } else {
                    board.set_state(ni,nj, NEW_TREE);
                }
            }
        }
    }
};

// ===== Step6Constructor =====
struct Step6Constructor {
    Step6Constructor(optional<unsigned> seed = nullopt){ if(seed) rng.seed(*seed); }

    Board construct(Board board){
        auto empty_queue = _find_empty_cells_adjacent_to_paths(board);
        shuffle(empty_queue.begin(), empty_queue.end(), rng);
        deque<pair<int,int>> q(empty_queue.begin(), empty_queue.end());

        while(!q.empty()){
            auto [ei,ej] = q.front(); q.pop_front();
            if(board.get_state(ei,ej)!=EMPTY) continue;
            if(_should_convert_to_path(board, ei,ej)){
                board.set_state(ei,ej, PATH);
                auto adj = _find_adjacent_empty_cells(board, ei,ej);
                for(auto& p: adj) q.push_back(p);
            }
        }

        // 【新規追加】Xからマンハッタン距離がちょうど2のEMPTYセルに対する特別な処理
        _process_goal_adjacent_empty_cells(board);

        _convert_remaining_empty_to_trees(board);
        return board;
    }

    vector<pair<int,int>> _find_empty_cells_adjacent_to_paths(const Board& board){
        vector<pair<int,int>> v; v.reserve(board.n*board.n/4);
        const int d4[4][2]={{0,1},{0,-1},{1,0},{-1,0}};
        for(int i=0;i<board.n;i++){
            for(int j=0;j<board.n;j++){
                if(board.get_state(i,j)==EMPTY){
                    bool has=false;
                    for(auto& d: d4){
                        int ni=i+d[0], nj=j+d[1];
                        if(ni>=0&&nj>=0&&ni<board.n&&nj<board.n && board.get_state(ni,nj)==PATH){
                            has=true; break;
                        }
                    }
                    if(has) v.emplace_back(i,j);
                }
            }
        }
        return v;
    }

    bool _should_convert_to_path(const Board& board, int ei, int ej){
        const int d4[4][2]={{0,1},{0,-1},{1,0},{-1,0}};
        int cnt=0;
        for(auto& d: d4){
            int ni=ei+d[0], nj=ej+d[1];
            if(ni<0||nj<0||ni>=board.n||nj>=board.n) continue;
            if(board.get_state(ni,nj)==PATH) cnt++;
        }
        return cnt==1;
    }

    vector<pair<int,int>> _find_adjacent_empty_cells(const Board& board, int ci, int cj){
        vector<pair<int,int>> v;
        const int d4[4][2]={{0,1},{0,-1},{1,0},{-1,0}};
        for(auto& d: d4){
            int ni=ci+d[0], nj=cj+d[1];
            if(ni<0||nj<0||ni>=board.n||nj>=board.n) continue;
            if(board.get_state(ni,nj)==EMPTY) v.emplace_back(ni,nj);
        }
        return v;
    }

    void _process_goal_adjacent_empty_cells(Board& board){
        // ゴール位置を取得
        auto [goal_x, goal_y] = board.to_2d(board.goal_pos);

        // マンハッタン距離がちょうど2のEMPTYセルを探す
        for(int i=0; i<board.n; i++){
            for(int j=0; j<board.n; j++){
                if(board.get_state(i,j) != EMPTY) continue;

                // マンハッタン距離をチェック
                int manhattan_distance = abs(i - goal_x) + abs(j - goal_y);
                if(manhattan_distance != 2) continue;

                // 4つの方向パターンをチェック
                if(_check_corner_path_pattern(board, i, j)){
                    board.set_state(i, j, PATH);
                }
            }
        }
    }

    bool _check_corner_path_pattern(const Board& board, int x, int y){
        // 仕様書に記載された4パターン
        vector<vector<pair<int,int>>> patterns = {
            {{x+1, y}, {x+1, y+1}, {x, y+1}},     // ([x+1,y], [x+1,y+1],[x,y+1])
            {{x+1, y}, {x+1, y-1}, {x, y-1}},     // ([x+1,y], [x+1,y-1],[x,y-1])
            {{x-1, y}, {x-1, y+1}, {x, y+1}},     // ([x-1,y], [x-1,y+1],[x,y+1])
            {{x-1, y}, {x-1, y-1}, {x, y-1}}      // ([x-1,y], [x-1,y-1],[x,y-1])
        };

        for(const auto& pattern: patterns){
            // パターン内の全ての点がPATHかチェック
            bool all_path = true;
            for(const auto& [px, py]: pattern){
                // 境界チェック
                if(!(0 <= px && px < board.n && 0 <= py && py < board.n)){
                    all_path = false;
                    break;
                }
                // PATH状態チェック
                if(board.get_state(px, py) != PATH){
                    all_path = false;
                    break;
                }
            }

            // いずれかのパターンが全てPATHなら true を返す
            if(all_path) return true;
        }

        return false;
    }

    void _convert_remaining_empty_to_trees(Board& board){
        for(int i=0;i<board.n;i++)
            for(int j=0;j<board.n;j++)
                if(board.get_state(i,j)==EMPTY) board.set_state(i,j, NEW_TREE);
    }
};

// ===== BoardChecker =====
struct BoardChecker {
    vector<pair<int,int>> directions = {{0,1}, {0,-1}, {1,0}, {-1,0}}; // 右、左、下、上

    BoardChecker() {}

    int check(const Board& board) {
        // 1. SからXに向かう最短パスの経路を求める
        auto shortest_path = _find_shortest_path(board);
        if(shortest_path.empty()) {
            // パスが見つからない場合は大きなペナルティを返す
            return 999;
        }

        // 2. Xの周囲の#のセルについて、@と接しているかどうかをカウントする
        int penalty = _calculate_penalty(board, shortest_path);

        return penalty;
    }

private:
    vector<pair<int,int>> _find_shortest_path(const Board& board) {
        auto [start_x, start_y] = board.to_2d(board.start_pos);
        auto [goal_x, goal_y] = board.to_2d(board.goal_pos);

        // BFS用のキューと訪問管理
        deque<tuple<int,int,vector<pair<int,int>>>> queue;
        queue.emplace_back(start_x, start_y, vector<pair<int,int>>{{start_x, start_y}});

        vector<vector<bool>> visited(board.n, vector<bool>(board.n, false));
        visited[start_x][start_y] = true;

        while(!queue.empty()) {
            auto [x, y, path] = queue.front();
            queue.pop_front();

            // ゴールに到達した場合
            if(x == goal_x && y == goal_y) {
                return path;
            }

            // 4方向への移動を試す（上下左右の優先順位）
            for(auto [dx, dy] : directions) {
                int nx = x + dx, ny = y + dy;

                // 境界チェック
                if(!(0 <= nx && nx < board.n && 0 <= ny && ny < board.n)) continue;

                // 既に訪問済みかチェック
                if(visited[nx][ny]) continue;

                // 通行可能セルかチェック
                int cell_state = board.get_state(nx, ny);
                if(_is_passable(cell_state)) {
                    visited[nx][ny] = true;
                    auto new_path = path;
                    new_path.emplace_back(nx, ny);
                    queue.emplace_back(nx, ny, new_path);
                }
            }
        }

        return {}; // パスが見つからない
    }

    bool _is_passable(int cell_state) const {
        return cell_state == EMPTY || cell_state == PATH ||
               cell_state == PATH_2 || cell_state == START || cell_state == GOAL;
    }

    int _calculate_penalty(const Board& board, const vector<pair<int,int>>& shortest_path) {
        auto [goal_x, goal_y] = board.to_2d(board.goal_pos);

        // 最短パスをセットに変換（高速な検索のため）
        unordered_set<long long> path_cells;
        for(auto [px, py] : shortest_path) {
            // ゴールに隣接していない@のみを対象とする（Xに隣接している@は.に戻す）
            if(abs(px - goal_x) + abs(py - goal_y) > 1) {
                path_cells.insert(((long long)px << 32) | (unsigned long long)py);
            }
        }

        int penalty = 0;

        // Xの4方向について、最初の#セルを見つける
        for(auto [dx, dy] : directions) {
            // Xから方向に進んで最初の#を探す
            int nx = goal_x + dx, ny = goal_y + dy;

            while(0 <= nx && nx < board.n && 0 <= ny && ny < board.n) {
                int cell_state = board.get_state(nx, ny);

                // #（TREE または NEW_TREE）を見つけた場合
                if(cell_state == TREE || cell_state == NEW_TREE) {
                    // この#が@と隣接しているかチェック
                    if(!_is_adjacent_to_path(board, nx, ny, path_cells, board.n)) {
                        penalty++;
                    }
                    break; // 最初の#を見つけたので終了
                }

                // 次のセルへ進む
                nx += dx;
                ny += dy;
            }
        }

        return penalty;
    }

    bool _is_adjacent_to_path(const Board& board, int tree_x, int tree_y, const unordered_set<long long>& path_cells, int board_size) const {
        for(auto [dx, dy] : directions) {
            int adj_x = tree_x, adj_y = tree_y;
            while(true){
                if(path_cells.count(((long long)adj_x << 32) | (unsigned long long)adj_y)) {
                    return true;
                }
                adj_x += dx;
                adj_y += dy;
                if(adj_x<0||adj_x>=board_size||adj_y<0||adj_y>=board_size) break;
                if(board.get_state(adj_x, adj_y) != PATH) break;
            }
        }
        return false;
    }
};

// ===== BoardSimulator =====
struct BoardSimulator {
    int n;
    int start_i, start_j, ti, tj;
    vector<pair<int,int>> point_order;
    array<pair<int,int>,4> dij;

    // runtime state
    const Board* boardPtr = nullptr;
    pair<int,int> p, t;
    pair<int,int> target;
    vector<char> revealed;     // 1次元配列に変更
    vector<int> new_revealed;
    vector<int> dist;          // 1次元配列に変更
    vector<int> q;
    int turn;

    BoardSimulator(int n_, int si, int sj, int ti_, int tj_, const vector<pair<int,int>>* given_order=nullptr)
        : n(n_), start_i(si), start_j(sj), ti(ti_), tj(tj_) {
        if(given_order){
            point_order = *given_order;
        }else{
            point_order.reserve(n*n);
            for(int i=0;i<n;i++) for(int j=0;j<n;j++) point_order.emplace_back(i,j);
            // remove goal and start
            point_order.erase(remove(point_order.begin(), point_order.end(), make_pair(ti_,tj_)), point_order.end());
            point_order.erase(remove(point_order.begin(), point_order.end(), make_pair(si,sj)), point_order.end());
            shuffle(point_order.begin(), point_order.end(), rng);
            point_order.push_back({ti_,tj_});
        }
        point_order.push_back({ti_,tj_});
        dij = {make_pair(-1,0), make_pair(1,0), make_pair(0,-1), make_pair(0,1)};
    }

    inline bool _is_passable(int c){ return c==EMPTY || c==PATH || c==PATH_2 || c==START || c==GOAL; }

    void _change_target(const pair<int,int>& tgt, const Board& board){
        if(target==tgt) return;
        target = tgt;
        if(target.first==-1) return;

        // BFS for distance from target
        dist.assign(n*n, INT_MAX);
        deque<pair<int,int>> dq;
        dq.push_back(target);
        dist[target.first*n + target.second]=0;

        while(!dq.empty()){
            auto [i,j] = dq.front(); dq.pop_front();
            for(auto [di,dj]: dij){
                int i2=i+di, j2=j+dj;
                if(i2<0||j2<0||i2>=n||j2>=n) continue;
                if(dist[i2*n + j2] != INT_MAX) continue;
                if((!revealed[i2*n + j2]) || _is_passable(board.get_state(i2,j2))){
                    dist[i2*n + j2] = dist[i*n + j] + 1;
                    dq.emplace_back(i2,j2);
                }
            }
        }
    }

    bool _reveal_from_position(const pair<int,int>& pos, const Board& board){
        bool changed=false;
        int i=pos.first, j=pos.second;
        for(auto [di,dj]: dij){
            int i2=i, j2=j;
            while(true){
                i2+=di; j2+=dj;
                if(i2<0||j2<0||i2>=n||j2>=n) break;
                if(!revealed[i2*n + j2]){
                    revealed[i2*n + j2]=1;
                    new_revealed.emplace_back(i2*n + j2);
                    if(!_is_passable(board.get_state(i2,j2))) changed=true;
                }
                if(!_is_passable(board.get_state(i2,j2))) break;
            }
        }
        return changed;
    }

    int simulate(const Board& board){
        boardPtr = &board;
        p = {start_i, start_j};
        t = {ti, tj};
        target = {-1,-1};
        revealed.assign(n*n, 0);
        revealed[start_i*n + start_j]=1;
        new_revealed.clear(); new_revealed.emplace_back(start_i*n + start_j);
        dist.assign(n*n, INT_MAX);
        q.clear();
        q.reserve(point_order.size());
        for(auto it = point_order.rbegin(); it != point_order.rend(); ++it) {
            q.push_back(it->first*n + it->second);
        }
        turn = 0;

        _reveal_from_position(p, board);

        while(p != t){
            if(!_step(board)) return 0;
        }
        return turn;
    }

    bool _step(const Board& board){
        new_revealed.clear();
        turn++;

        if(p==t) return false;

        bool changed = _reveal_from_position(p, board);

        if(changed){
            auto old = target; target = {-1,-1}; _change_target(old, board);
        }
        if(revealed[t.first*n + t.second]) _change_target(t, board);

        if(target.first!=-1 && dist[p.first*n + p.second]==INT_MAX){
            target = {-1,-1};
        }
        if(target.first==-1 || (target!=t && revealed[target.first*n + target.second])){
            _change_target(p, board);
            while(true){
                if(!q.empty()){
                    auto targetCandIdx = q.back(); q.pop_back();
                    if(!revealed[targetCandIdx] &&
                       dist[targetCandIdx]!=INT_MAX){
                        pair<int,int> targetCand = {targetCandIdx/n, targetCandIdx%n};
                        _change_target(targetCand, board);
                        break;
                    }
                }else return false;
            }
        }

        int min_dist = INT_MAX; int next_dir = -1;
        for(int dir=0; dir<4; dir++){
            int i2 = p.first + dij[dir].first;
            int j2 = p.second + dij[dir].second;
            if(i2>=0&&j2>=0&&i2<n&&j2<n && dist[i2*n + j2] < min_dist){
                min_dist = dist[i2*n + j2]; next_dir = dir;
            }
        }
        if(next_dir==-1) return false;
        p.first += dij[next_dir].first;
        p.second += dij[next_dir].second;
        return true;
    }
};

// ===== main =====
int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int N, ti, tj;
    if(!(cin >> N >> ti >> tj)) return 0;
    vector<string> board_input(N);
    for(int i=0;i<N;i++) cin >> board_input[i];
    int start_i, start_j;
    cin >> start_i >> start_j;
    string dummy;
    cin >> dummy; // consume an extra line like Python's input()

    Step0Constructor constructor_0;
    Step1Constructor constructor_1;
    Step2Constructor constructor_2;
    Step3Constructor constructor_3;
    Step4Constructor constructor_4;
    Step5Constructor constructor_5;
    Step6Constructor constructor_6;

    vector<BoardSimulator> evaluators; evaluators.reserve(NUM_EVALUATIONS);
    for(int k=0;k<NUM_EVALUATIONS;k++){
        evaluators.emplace_back(N, start_i, start_j, ti, tj);
    }

    // Phase 1: 最初の1秒で候補ボードを生成
    vector<Board> board_candidates;
    board_candidates.reserve(10000); // 適切なサイズで予約

    auto t0 = chrono::steady_clock::now();
    const double PHASE1_LIMIT = 1.1; // seconds for candidate generation
    const double PHASE2_LIMIT = 1.5; // seconds for candidate generation
    const double TOTAL_LIMIT = 1.82;  // total time limit
    int edge_size;

    while(true){
        auto now = chrono::steady_clock::now();
        double elapsed = chrono::duration<double>(now - t0).count();
        if(elapsed >= PHASE1_LIMIT) break;

        Board board(N, start_i, start_j, ti, tj, board_input);

        // step0
        board = constructor_0.construct(std::move(board));

        // step1
        {
            auto opt = constructor_1.random_construct(board);
            if(opt.has_value()) board = std::move(*opt);
        }

        if(rand() % 2) board.reverse_up_down();
        if(rand() % 2) board.reverse_left_right();

        // step2
        if (rand() % 2) {
            edge_size = 3;
        } else {
            edge_size = 3;
        }
        board = constructor_2.construct(std::move(board), PATH, edge_size);
        board.reverse_left_right();
        if (rand() % 2) {
            edge_size = 3;
        } else {
            edge_size = 3;
        }
        board = constructor_2.construct(std::move(board), PATH_2, edge_size);
        board.reverse_left_right();

        if(rand() % 2) board.reverse_up_down();

        int c = 0;
        while(true){
            if(c % 2 == 1) board.reverse_up_down();
            if (c == 0){
                start_i = rand() % (2*N/3) + N/6;
            }else{
                start_i = 0;
            }

            auto res = constructor_3.construct(std::move(board), PATH, start_i);
            board = std::move(res.first);
            if(c % 2 == 1) board.reverse_up_down();
            if(res.second) break;
            c++;
            // Safety: prevent infinite loop just in case
            if(c > 2*N) break;
        }
        if (c == 0) continue;

        board = constructor_4.construct(std::move(board));
        board = constructor_5.construct(std::move(board), true);
        board = constructor_6.construct(std::move(board));

        if(board.is_up_down_reversed) board.reverse_up_down();
        if(board.is_left_right_reversed) board.reverse_left_right();

        board_candidates.push_back(board);
    }

    cerr << "Generated " << board_candidates.size() << " candidates in phase 1\n";

    // Phase 2: BoardCheckerでペナルティを計算し、ソート
    BoardChecker checker;
    vector<tuple<int, int, int>> penalty_path_indices; // (penalty, -path_count, index)
    penalty_path_indices.reserve(board_candidates.size());

    auto now = chrono::steady_clock::now();
    double elapsed = chrono::duration<double>(now - t0).count();
    cerr << "Phase 2 start time: " << elapsed << "\n";

    for(size_t i = 0; i < board_candidates.size(); i++){
        now = chrono::steady_clock::now();
        elapsed = chrono::duration<double>(now - t0).count();
        if(elapsed >= PHASE2_LIMIT) break;
        int penalty = checker.check(board_candidates[i]);
        int path_count = 0;
        // PATHセルの数をカウント
        for(int x = 0; x < board_candidates[i].n; x++){
            for(int y = 0; y < board_candidates[i].n; y++){
                if(board_candidates[i].get_state(x, y) == PATH){
                    path_count++;
                }
            }
        }
        penalty_path_indices.emplace_back(penalty, -path_count, i); // path_countを負数にして降順ソート
    }

    // ペナルティが小さい順、同じ場合はPATH数が多い順にソート
    sort(penalty_path_indices.begin(), penalty_path_indices.end());

    cerr << "Sorted candidates by penalty (min=" << (penalty_path_indices.empty() ? -1 : get<0>(penalty_path_indices[0]))
         << ", max=" << (penalty_path_indices.empty() ? -1 : get<0>(penalty_path_indices.back())) << ")\n";

    // Phase 3: 残り1秒でペナルティが最小のもののみBoardSimulatorで評価
    int best_score = -1;
    optional<Board> best_board;
    int evaluated_count = 0;
    now = chrono::steady_clock::now();
    elapsed = chrono::duration<double>(now - t0).count();
    cerr << "Phase 3 start time: " << elapsed << "\n";

    // 最小ペナルティを取得
    int min_penalty = penalty_path_indices.empty() ? INT_MAX : get<0>(penalty_path_indices[0]);
    cerr << "Evaluating only candidates with minimum penalty: " << min_penalty << "\n";

    for(const auto& [penalty, neg_path_count, idx]: penalty_path_indices){
        // 最小ペナルティでない場合はスキップ
        if(penalty > min_penalty) break;

        auto now = chrono::steady_clock::now();
        double elapsed = chrono::duration<double>(now - t0).count();
        if(elapsed >= TOTAL_LIMIT && evaluated_count > 0) break;

        const Board& board = board_candidates[idx];

        int score_min = INT_MAX;
        for(auto& ev: evaluators){
            int sc = ev.simulate(board);
            score_min = min(score_min, sc);
            if(score_min < best_score) break;
        }

        if(score_min > best_score){
            best_score = score_min;
            best_board = board;
            int path_count = -neg_path_count;
            cerr << "New best: score=" << best_score << ", penalty=" << penalty << ", paths=" << path_count << "\n";
        }

        evaluated_count++;
    }

    cerr << "Evaluated " << evaluated_count << " candidates in phase 3\n";

    if(best_board.has_value()){
        best_board->output();
        best_board->debug_output();
    }else{
        // fallback: output nothing new trees
        cout << 0 << "\n";
    }

    string d1, d2;
    cin >> d1; // consume like Python input()
    cin >> d2; // consume like Python input()

    cout << -1 << "\n";
    cerr << "Best score: " << best_score << "\n";
    return 0;
}
