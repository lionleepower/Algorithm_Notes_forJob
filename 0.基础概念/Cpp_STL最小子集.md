# C++ STL 最小子集：有序容器与优先队列速查

Python 没有内置的有序集合，遇到「前驱 / 后继 / 第 k 小」这类题只能自己拼；C++ 的 `set`、`multiset`、`map`、`priority_queue` 开箱即用。本篇只收**刷牛客 ACM 模式题够用的最小子集**，示例代码都在本机编译运行并核对了输出，两个完整实例另与暴力解法对拍过。第 1 节专门把 `<int>`、迭代器、`auto`、`*it` / `->` 这几个最让人发懵的符号讲透，读完再看后面的代码会轻松很多；`cin`、`cout`、`::` 等更基础的符号见 [[Cpp_基础语法速查]]。

---

## 思路

只要题目要**有序**（小于 $x$ 的最大值、大于 $x$ 的最小值、按键有序遍历），哈希容器就帮不上忙。Python 里要靠 `list` 加 `bisect`（插入 $O(n)$）或树状数组按值域计数；C++ 里这些操作是一个容器自带的 $O(\log n)$。

> [!tip]- 核心思路：`bisect` 的概念原样迁移，只是换了名字
> 
> | 含义 | Python | C++ |
> | --- | --- | --- |
> | 第一个 $\ge x$ | `bisect_left(a, x)` | `s.lower_bound(x)` |
> | 第一个 $> x$ | `bisect_right(a, x)` | `s.upper_bound(x)` |
> | 前驱（最后一个 $< x$） | `bisect_left(a, x) - 1` | `prev(s.lower_bound(x))`，先判 `it != s.begin()` |
> | 后继（第一个 $> x$） | `a[bisect_right(a, x)]` | `*s.upper_bound(x)`，先判 `it != s.end()` |
> 
> C++ 的 `lower_bound` / `upper_bound` 返回**迭代器**，不是下标。迭代器可以理解成「插在容器里的书签」，取值用 `*it`，没找到时等于 `end()`，详见第 1 节。

---

## 1. 模板、读入与几个必懂的符号

> [!success]- 每道题的固定开头
> 
> ```cpp
> #include <bits/stdc++.h>
> using namespace std;
> 
> int main() {
>     ios::sync_with_stdio(false);   // 关闭与 C 输入输出的同步，读写大数据明显更快
>     cin.tie(nullptr);              // 解除 cin 与 cout 的绑定
>     int q;
>     cin >> q;
>     while (q--) {
>         int op, x;
>         cin >> op;
>         // 按 op 决定还要不要读 x
>     }
>     return 0;
> }
> ```
> 
> 输出换行用 `"\n"`，不要用 `endl`（它每次都刷新缓冲区，大量输出时更慢）。这两行加速写法只能在**不混用** `scanf` / `printf` 与 `cin` / `cout` 时使用。
> 
> 这些符号每一行是什么意思，见 [[Cpp_基础语法速查]] 第 1 节。

> [!tip]- 尖括号 `<int>` 是什么？
> 
> 尖括号里写的是**这个容器里装什么类型的元素**，相当于 Java 的泛型 `List<Integer>`，或 Python 类型标注里的 `list[int]`。
> 
> | 写法 | 意思 |
> | --- | --- |
> | `vector<int>` | 装 `int` 的动态数组 |
> | `set<int>` | 装 `int` 的有序集合 |
> | `map<string, int>` | 键是 `string`、值是 `int` 的有序字典 |
> | `priority_queue<int, vector<int>, greater<int>>` | 三个参数：元素类型、底层用什么容器存、比较规则 |
> 
> 最后一行最长，其实只有一个知识点：**`priority_queue` 默认把最大的放在堆顶，传入 `greater<int>` 这个「比较规则」就改成最小的放堆顶**。前两个参数照抄即可。下面的示例里放入 3 和 1 之后，`top()` 输出的是 `1`。

> [!tip]- 迭代器（iterator）：容器里的「书签」
> 
> `set` 和 `map` 没有下标，不能写 `s[0]`。取位置靠**迭代器**，可以理解成**插在容器某个位置上的书签**。它和 Python 里 `bisect` 返回的下标是一一对应的：
> 
> | 写法 | 意思 | 对应 Python 的下标写法 |
> | --- | --- | --- |
> | `s.begin()` | 指向第一个元素的书签 | 下标 `0` |
> | `s.end()` | 指向**最后一个元素后面的一格**，是个空位，不是最后一个元素 | 下标 `len(a)` |
> | `*it` | 打开书签，取出所指位置的值 | `a[i]` |
> | `++it` / `--it` | 书签往后 / 往前移一格 | `i + 1` / `i - 1` |
> | `prev(it)` / `next(it)` | 前一个 / 后一个位置的书签（`it` 自己不动） | `i - 1` / `i + 1` |
> | `it == s.end()` | 没找到，或者越过了末尾 | `i == len(a)` |
> | `it == s.begin()` | 已经在最前面，前面没有元素了 | `i == 0` |
> 
> 所以上面「`bisect` 对照表」里的 `bisect_left(a, x) - 1`，在 C++ 里就是 `prev(s.lower_bound(x))`：先找到第一个 `>= x` 的位置，再往前挪一格。
> 
> 三个容易踩的点：
> 
> - **`end()` 不能取值**：它是空位，`*s.end()` 是未定义行为，所以取值前总要先判 `it != s.end()`。
> - **`find` 没找到时返回 `end()`**：示例里 `s.find(99) == s.end()` 输出 `1`（真）。
> - **`set` 的书签不能当下标用**：只能一格一格地 `++` / `--`，不能写 `it + 1`，要跳一格用 `next(it)`。

> [!tip]- `auto`：让编译器自己推断类型
> 
> 迭代器的完整类型很长，比如 `set<int>::iterator`。**`auto` 的意思是「这里的类型你看右边自己推断，我不写了」**，下面两行等价：
> 
> ```cpp
> set<int>::iterator it = s.begin();   // 完整写法
> auto jt = s.begin();                 // 等价，省事
> ```
> 
> 它有点像 Python 里变量不用写类型，区别是 C++ 的类型在编译时就确定了，用 `auto` 之后也不能中途改成别的类型。

> [!tip]- `*it`、`it->first`、`auto& [k, v]`：怎么取元素里的内容
> 
> - **`set` 的每个元素就是一个值**，`*it` 直接取出来。
> - **`map` 的每个元素是一对 `(键, 值)`**，书签指着这一对：`it->first` 是键，`it->second` 是值，还可以直接改值：`it->second = 5;`。`->` 可以读作「书签所指的那一对里的……」，它等价于 `(*it).second`。
> - **遍历 `map` 想同时拿键和值**：`for (auto& [k, v] : m)`，相当于 Python 的 `for k, v in m.items()`；`&` 表示不拷贝，可以直接改值。

> [!example]- 完整示例（已编译运行）：迭代器、`auto`、`->`、三参数堆
> 
> ```cpp
> #include <bits/stdc++.h>
> using namespace std;
> 
> int main() {
>     set<int> s = {10, 20, 30};          // <int> 表示「这个集合里装的是 int」
> 
>     // 迭代器：指向容器里某个元素的「位置标记」，像一枚书签
>     set<int>::iterator it = s.begin();  // 完整写法，又长又难记
>     auto jt = s.begin();                // auto：让编译器自己推断类型，和上一行等价
>     cout << *it << " " << *jt << "\n";  // *it：取出书签所指位置上的值
> 
>     ++it;                               // 书签往后移一格
>     cout << *it << "\n";
>     --it;                               // 再往前移一格
>     cout << *it << " " << *prev(s.end()) << " " << *next(s.begin()) << "\n";   // prev / next：前一个 / 后一个位置
> 
>     // end() 不是最后一个元素，而是「最后一个元素再往后一格」的空位
>     auto e = s.end();
>     cout << (s.find(99) == e) << " " << (s.find(20) == e) << "\n";   // 没找到时 find 返回 end()
> 
>     // 用书签遍历，和范围 for 等价
>     for (auto p = s.begin(); p != s.end(); ++p) cout << *p << " ";
>     cout << "\n";
>     for (int x : s) cout << x << " ";
>     cout << "\n";
> 
>     // map 里每个元素是一对 (key, value)，书签用 -> 访问它的两个部分
>     map<string, int> m = {{"a", 1}, {"b", 2}};
>     auto mi = m.find("b");
>     cout << mi->first << " " << mi->second << "\n";
>     mi->second = 5;                     // 通过书签直接修改 value
>     cout << m["b"] << "\n";
>     for (auto& [k, v] : m) cout << k << "=" << v << " ";   // 同时拿到 key 和 value
>     cout << "\n";
> 
>     // priority_queue 的三个尖括号参数：元素类型、底层容器、比较方式
>     priority_queue<int, vector<int>, greater<int>> pq;
>     pq.push(3);
>     pq.push(1);
>     cout << pq.top() << "\n";
>     return 0;
> }
> ```
> 
> 实际输出，逐行对应上面的写法：
> 
> ```text
> 10 10
> 20
> 10 30 20
> 1 0
> 10 20 30 
> 10 20 30 
> b 2
> 5
> a=1 b=5 
> 1
> ```

---

## 2. 核心操作

| 容器 | 作用 | 常用操作与复杂度 |
| --- | --- | --- |
| `vector<int>` | 动态数组，对应 Python `list` | `push_back` $O(1)$，下标访问 $O(1)$ |
| `sort(v.begin(), v.end())` | 排序，升序；降序加第三个参数 `greater<int>()` | $O(n \log n)$ |
| `set<int>` | 有序、去重的集合 | `insert` / `erase` / `find` / `lower_bound` / `upper_bound`，均 $O(\log n)$ |
| `multiset<int>` | 有序、**允许重复**的集合 | 同 `set`；`count(x)` 是 $O(\log n + k)$，$k$ 为重复个数 |
| `map<int,int>` | 按键有序的字典，计数用 | `m[x]++`、`find`、`erase`，均 $O(\log n)$ |
| `priority_queue<int>` | 堆，**默认大根堆** | `push` / `pop` $O(\log n)$，`top` $O(1)$ |

> [!example]- 最小示例（已编译运行）
> 
> ```cpp
> #include <bits/stdc++.h>
> using namespace std;
> 
> int main() {
>     ios::sync_with_stdio(false);
>     cin.tie(nullptr);
> 
>     // vector + sort
>     vector<int> v = {5, 2, 9, 1};
>     sort(v.begin(), v.end());                       // 升序
>     for (int x : v) cout << x << " ";
>     cout << "\n";
>     sort(v.begin(), v.end(), greater<int>());       // 降序
>     for (int x : v) cout << x << " ";
>     cout << "\n";
> 
>     // map 计数（等价 Python Counter）
>     map<int, int> cnt;
>     for (int x : {3, 1, 3, 2, 3, 1}) cnt[x]++;
>     for (auto& [k, c] : cnt) cout << k << ":" << c << " ";   // 按 key 升序遍历
>     cout << "\n";
> 
>     // set：有序、去重
>     set<int> s = {5, 1, 3, 3, 9};
>     for (int x : s) cout << x << " ";
>     cout << "\n";
>     auto it = s.lower_bound(4);                     // 第一个 >= 4
>     cout << *it << " ";
>     it = s.upper_bound(5);                          // 第一个 > 5
>     cout << *it << " ";
>     cout << (s.upper_bound(9) == s.end() ? "end" : "has") << "\n";
> 
>     // multiset：erase(值) 删光，erase(迭代器) 只删一个
>     multiset<int> m = {2, 2, 2, 7};
>     m.erase(m.find(2));
>     cout << m.size() << " ";
>     m.erase(2);
>     cout << m.size() << "\n";
> 
>     // priority_queue：默认大根堆
>     priority_queue<int> mx;
>     priority_queue<int, vector<int>, greater<int>> mn;
>     for (int x : {4, 1, 8}) { mx.push(x); mn.push(x); }
>     cout << mx.top() << " " << mn.top() << "\n";
> 
>     // 反向迭代取最大 / 最小
>     cout << *s.begin() << " " << *s.rbegin() << "\n";
>     return 0;
> }
> ```
> 
> 实际输出，与注释的语义一一对应：
> 
> ```text
> 1 2 5 9
> 9 5 2 1
> 1:2 2:1 3:3
> 1 3 5 9
> 5 9 end
> 3 1
> 8 1
> 1 9
> ```

---

## 3. 关键行为与边界

> [!tip]- 为什么要用 `s.lower_bound(x)`，而不是 `lower_bound(s.begin(), s.end(), x)`
> 
> 两者都能编译，但复杂度不同：`set` 自带的成员函数是 $O(\log n)$，而 `algorithm` 库里的 `std::lower_bound` 用在 `set` 上是 $O(n)$（OI Wiki 的关联容器页明确指出了这一点）。原因是 `set` 的书签（迭代器）只能一格一格地走，不能像数组下标那样一步跳到中间，通用二分用不上；成员函数则直接沿着树往下找。所以**对 `set` / `multiset` / `map` 一律调成员函数**；只有对 `vector` 才用 `std::lower_bound`。

> [!warning]- 边界条件
> 
> - **前驱**：`it = s.lower_bound(x)` 若等于 `s.begin()`，说明没有更小的元素，不能再取 `prev(it)`。
> - **后继**：`it = s.upper_bound(x)` 若等于 `s.end()`，说明没有更大的元素，不能取 `*it`。
> - **空容器**：对空的 `priority_queue` 调 `top()` / `pop()` 是未定义行为（C++ 标准不保证结果，可能崩溃，也可能碰巧「正常」），不会抛异常。题目若没保证非空，要先判 `empty()`。
> - **`map` 的 `[]` 会插入**：`m[x]` 读一个不存在的键时，会悄悄插入 `x` 并置 0。只想查询时用 `find`。

---

## 4. 实例一：多重集合（牛客 BISHI5）

题目要求：插入（可重复）、删除**一个**、查个数、查总数、前驱、后继，$n \le 10^5$，$x$ 可以为负。

直觉写法是 `multiset`，但它的 `count(x)` 是 $O(\log n + k)$。**实测 5e4 次插入同一个值再 5e4 次查个数，要 12.07 秒**；随机数据只要 0.06 秒，所以普通对拍发现不了。稳妥写法是**用 `set` 管有序的不同值，用 `map` 管个数**，全部 $O(\log n)$。

> [!success]- 完整实现：`set` + `map` 计数
> 
> ```cpp
> #include <bits/stdc++.h>
> using namespace std;
> 
> int main() {
>     ios::sync_with_stdio(false);
>     cin.tie(nullptr);
> 
>     int q;
>     cin >> q;
>     set<int> S;                 // 有序的「不同值」
>     map<int, int> cnt;          // 值 -> 个数
>     long long total = 0;
>     while (q--) {
>         int op, x;
>         cin >> op;
>         if (op == 1) {
>             cin >> x;
>             if (cnt[x]++ == 0) S.insert(x);
>             total++;
>         } else if (op == 2) {
>             cin >> x;
>             auto it = cnt.find(x);
>             if (it != cnt.end()) {
>                 if (--it->second == 0) { cnt.erase(it); S.erase(x); }
>                 total--;
>             }
>         } else if (op == 3) {
>             cin >> x;
>             auto it = cnt.find(x);
>             cout << (it == cnt.end() ? 0 : it->second) << "\n";
>         } else if (op == 4) {
>             cout << total << "\n";
>         } else if (op == 5) {
>             cin >> x;
>             auto it = S.lower_bound(x);
>             cout << (it == S.begin() ? -1 : *prev(it)) << "\n";
>         } else {
>             cin >> x;
>             auto it = S.upper_bound(x);
>             cout << (it == S.end() ? -1 : *it) << "\n";
>         }
>     }
>     return 0;
> }
> ```
> 
> - 主流程：`cnt[x]++ == 0` 表示这个值是第一次出现，此时才插入 `S`；删除时个数减到 0 才把它从 `S` 和 `cnt` 里移除。
> - 关键不变量：`S` 恰好等于 `cnt` 里所有个数大于 0 的键，`total` 等于所有个数之和。
> - 易错位置：查询个数用 `find` 而不是 `cnt[x]`（否则会插入）；前驱先判 `it == S.begin()`。
> 
> 样例通过，与暴力解法对拍 300 组随机用例（含 $\pm10^6$ 边界）无不一致。重复值最坏的两组输入都是 0.05 秒。

> [!tip]- 逐行读懂这段代码里的几个写法
> 
> - **`while (q--)`**：先用 `q` 当前的值判断真假，再让它减 1，所以恰好循环 `q` 次。
> - **`if (cnt[x]++ == 0)`**：`x++` 是**先用旧值、再加 1**。所以这句是「如果 `x` 原来的个数是 0（说明集合里本来没有它），就把它插进有序集合 `S`」，同时个数加 1。`cnt[x]` 读不存在的键时会自动插入并置 0，这里恰好利用了这一点。
> - **`auto it = cnt.find(x); if (it != cnt.end())`**：`find` 返回书签，不等于 `end()` 就说明找到了。
> - **`--it->second == 0`**：`it->second` 是 `x` 当前的个数，前面的 `--` 让它减 1，再和 0 比较。减到 0 就把 `x` 从 `cnt` 和 `S` 里都删掉。
> - **`cout << (it == cnt.end() ? 0 : it->second)`**：`条件 ? 甲 : 乙` 是三目运算符，相当于 Python 的 `甲 if 条件 else 乙`，见 [[python_三元表达式]]。没找到就输出 0，找到了就输出个数。
> - **`*prev(it)`**：先让书签往前挪一格，再取出那个位置的值，就是前驱。

---

## 5. 实例二：整数优先队列（牛客 BISHI6）

题目要求：插入、查最小值、删除一个最小值，$n \le 10^6$，限时 3 秒。这正是堆的标准场景，只取一端，不需要前驱后继。

> [!success]- 完整实现：小根堆
> 
> ```cpp
> #include <bits/stdc++.h>
> using namespace std;
> 
> int main() {
>     ios::sync_with_stdio(false);
>     cin.tie(nullptr);
> 
>     int n;
>     cin >> n;
>     priority_queue<long long, vector<long long>, greater<long long>> h;   // 小根堆
>     while (n--) {
>         int op;
>         cin >> op;
>         if (op == 1) {
>             long long x;
>             cin >> x;
>             h.push(x);
>         } else if (op == 2) {
>             cout << h.top() << "\n";
>         } else {
>             h.pop();
>         }
>     }
>     return 0;
> }
> ```
> 
> - 主流程：`priority_queue` 加 `greater` 就是小根堆，`top()` 是最小值。
> - 关键变量：$x < 2^{31}$ 恰好落在 `int` 的范围内，这里用 `long long` 只是保险。
> - 易错位置：忘了写 `greater` 就变成大根堆，`top()` 会返回最大值而不是最小值。
> 
> 样例通过，对拍 300 组 0 处不一致，$n = 10^6$ 约 0.18～0.23 秒。

> [!summary]- 当前实例复杂度
> 
> - 时间：$O(n \log n)$，每次 `push` / `pop` 是 $O(\log n)$，`top` 是 $O(1)$。
> - 空间：$O(n)$，堆最多存全部插入的元素。

---

## 6. 与相近写法怎么选

| 需求 | 推荐写法 | 原因 |
| --- | --- | --- |
| 只判存在、去重、计数 | Python `set` / `dict` | 更短，不必换语言 |
| 只取最小或最大值 | Python `heapq` 或 C++ `priority_queue` | 堆只暴露一端，够用 |
| 前驱 / 后继，数据小（约 $n \le 2\times10^4$） | Python `list` + `bisect` | 最省事，见 [[BISHI4 集合操作]] |
| 前驱 / 后继，数据大、值域小 | Python 树状数组按值域计数 | 纯标准库，用时稳定 |
| 前驱 / 后继，数据大、值域大，或有序多重集合 | **C++ `set` / `multiset` / `map`** | 一个容器自带，没有下标偏移，也没有双容器同步 |

Java 的对应物是 `TreeSet`。官方文档里：`floor(e)` 返回小于等于 `e` 的最大元素，`ceiling(e)` 返回大于等于 `e` 的最小元素，`lower(e)` 返回严格小于 `e` 的最大元素，`higher(e)` 返回严格大于 `e` 的最小元素，找不到统一返回 `null`。前驱就是 `lower`，后继就是 `higher`。多重集合在 Java 里需要用 `TreeMap` 自己记个数，这一点我没有专门查证。

---

## 7. 常见易错点

> [!warning]- 易错点
> 
> - **`multiset::erase(x)` 会删掉所有等于 `x` 的元素**：要只删一个，必须先 `find` 再 `erase(迭代器)`，写成 `s.erase(s.find(x))`，并先判 `find` 的结果不是 `end()`。
> - **`multiset::count(x)` 在重复值多时很慢**：它要数完所有重复元素。需要个数时用 `map` 另记，如上面的实例一。
> - **`priority_queue` 默认是大根堆**：要小根堆写 `priority_queue<int, vector<int>, greater<int>>`。Python 的 `heapq` 刚好相反，默认小根堆，这是两边来回切换时最容易写反的地方。
> - **对 `set` 用 `std::lower_bound`**：能编译但是 $O(n)$，会悄悄变慢。
> - **前驱忘了判 `begin()`**：`prev(s.begin())` 不能取值，结果是未定义的。
> - **把迭代器当下标用**：对 `set` 写 `s[0]` 会报 `no match for 'operator[]'`，写 `it + 1` 会报 `no match for 'operator+'`。要取最小值用 `*s.begin()`，要跳一格用 `next(it)`。
> - **用 `m[x]` 做查询**：会插入默认值，破坏「键存在」的判断。
> - **`int` 溢出**：值接近 $2^{31}$ 或要累加时用 `long long`。

---

## 复杂度

> [!summary]- 复杂度
> 
> - `set` / `multiset` / `map` 的增删查和 `lower_bound` / `upper_bound`：$O(\log n)$，因为底层是平衡二叉搜索树，每次沿树高走一条路径。
> - `priority_queue`：`push` / `pop` 是 $O(\log n)$，`top` 是 $O(1)$，因为底层是二叉堆。
> - `sort`：$O(n \log n)$。
> - 空间：$O(n)$，每个元素一个树节点或堆元素。

---

## 一句话总结

需要**有序**就上 C++ 的 `set` 系列，只需要**一端最值**用 `priority_queue` 或 Python `heapq`；其余多数题继续用 Python。

---

## 模板归纳

看到以下信号时，优先想到当前知识点：

- 题面出现「前驱 / 后继 / 小于 $x$ 的最大 / 大于 $x$ 的最小」，同时有插入删除。
- 要「按键有序遍历」或「动态维护第 k 小」。
- 值域很大、Python 的 `list` + `bisect` 会超时，而树状数组又要离散化。
- 看不懂代码里的 `auto`、`*it`、`->`、`<int>`：回到第 1 节。

```cpp
set<int> s;
auto it = s.lower_bound(x);                          // 第一个 >= x
int pre  = (it == s.begin()) ? -1 : *prev(it);       // 前驱：最后一个 < x
auto jt = s.upper_bound(x);                          // 第一个 > x
int back = (jt == s.end()) ? -1 : *jt;               // 后继
```

相关笔记与教程：

- 前置：[[Python_set]]、[[3.0 二分查找 红蓝染色法]]（`bisect_left` / `bisect_right` 的语义）、[[Cpp_基础语法速查]]（C++ 基础语法）
- 同类：[[BISHI4 集合操作]]（同一道题的 Python 三种写法与 C++ `set` 版）、[[Python_常用内置函数]]
- 教程（均为英文或中文在线资料）：[OI Wiki：STL 关联容器](https://oi-wiki.org/lang/csl/associative-container/)、[OI Wiki：容器适配器](https://oi-wiki.org/lang/csl/container-adapter/)、[LearnCpp.com](https://www.learncpp.com/)、[Oracle：TreeSet 文档](https://docs.oracle.com/javase/8/docs/api/java/util/TreeSet.html)
