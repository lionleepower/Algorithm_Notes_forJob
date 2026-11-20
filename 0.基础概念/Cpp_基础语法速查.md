# C++ 基础语法速查：给 Python 刷题者的最小子集

牛客 ACM 模式题用到的 C++ 语法其实很少：声明变量、读写、分支循环、函数、数组和结构体。本篇只收这一小块，并专门标出**从 Python 过来最容易写错的地方**。容器（`set`、`priority_queue` 等）见 [[Cpp_STL最小子集]]。第 1 节专门把 `cin`、`cout`、`::`、`ios` 这些最让人发懵的符号讲透，并用 Java / Python 做类比。

---

## 思路

C++ 和 Python 的区别集中在三点：**变量要声明类型**、**整数有范围且除法行为不同**、**`vector` 的 `size()` 是无符号数**。其余（`if`、`for`、`while`、函数）逻辑完全相同，只是换了写法。

> [!tip]- 核心思路：Python 写法逐条换成 C++ 写法
> 
> | Python | C++ |
> | --- | --- |
> | `x = 5` | `int x = 5;` |
> | `print(x)` | `cout << x << "\n";` |
> | `x = int(input())` | `cin >> x;` |
> | `for i in range(n):` | `for (int i = 0; i < n; i++) {` |
> | `for x in v:` | `for (int x : v) {` |
> | `len(v)` | `v.size()` |
> | `v.append(x)` | `v.push_back(x);` |
> | `elif` | `else if` |
> | `and` / `or` / `not` | `&&` / `||` / `!` |
> | `True` / `False` | `true` / `false` |
> | `# 注释` | `// 注释` |
> | `def f(a, b):` | `int f(int a, int b) {` |
> | `[[] for _ in range(n)]` | `vector<vector<int>> g(n);` |
> 
> 记住三条：每条语句以 `;` 结尾；代码块用 `{}` 不靠缩进；`for` 和 `if` 的条件要放在圆括号里。

---

## 1. 代码框架：每一行是什么意思

别被这几行吓到：它们是**每道题都一样的固定模板**，先背下来就能写题。下面把每个符号用 Java / Python 做类比讲清楚，类比只是帮你理解，并不完全等价。

> [!success]- 固定框架（先背下来）
> 
> ```cpp
> #include <bits/stdc++.h>             // ① 把标准库一次性引进来
> using namespace std;                 // ② 省掉到处写 std::
> 
> int main() {                         // ③ 程序从这里开始运行
>     ios::sync_with_stdio(false);     // ④ 关闭同步，读写更快
>     cin.tie(nullptr);                // ⑤ 解除 cin 与 cout 的绑定，再快一点
> 
>     int n;
>     cin >> n;                        // ⑥ 读一个整数，存进 n
>     cout << n << "\n";               // ⑦ 输出 n，再换行
>     return 0;                        // ⑧ 告诉系统：正常结束
> }
> ```
> 
> - 读到文件结束：`while (cin >> x) { ... }`，适用于题目不给个数的输入。
> - 输出换行用 `"\n"`，不要用 `endl`（它每次都刷新缓冲区，大量输出时更慢）。

> [!tip]- 逐行翻译：① ② ③ ⑧
> 
> | 这一行 | 白话 | 类比 |
> | --- | --- | --- |
> | `#include <bits/stdc++.h>` | 编译器是从上往下读代码的，不先引入就不认识 `cin`、`cout`、`vector`。这个头文件是个「全家桶」，一行就把常用的全引进来 | Python 的 `import`，Java 的 `import java.util.*` |
> | `using namespace std;` | 声明「后面遇到不认识的名字，先去 `std` 里找」，这样就不必每次写 `std::cout` | Python 的 `from math import *` |
> | `int main() { ... }` | 程序入口，运行从这里开始，大括号里是函数体 | Java 的 `public static void main`；Python 里 `if __name__ == "__main__":` 下面那段 |
> | `return 0;` | 告诉系统程序正常结束，照着写就行 | 没有直接对应物 |

> [!tip]- `cin` 和 `cout` 怎么理解？
> 
> **`cout` 就是「标准输出」，可以理解成 Java 的 `System.out`、Python 的 `print` 背后的那根管子**；**`cin` 是「标准输入」，对应 Java 的 `System.in`（配 `Scanner`）、Python 的 `input()`**。
> 
> 中间那两个箭头 `<<`、`>>` 的方向就是**数据流动的方向**：
> 
> - `cout << x`：x 的内容流向 `cout`（输出）。
> - `cin >> x`：`cin` 里的内容流进 x（输入）。
> 
> 几个要点：
> 
> - **可以连着写**：`cout << a << " " << b << "\n";`、`cin >> a >> b;`。
> - **不会自动加空格**：Python 的 `print(a, b)` 会在中间补空格，`cout << a << b` 不会。示例里输入 `3 4` 后 `cout << a << b` 输出的是 `34`，想要空格必须自己写 `" "`。
> - **按变量的类型来读**：读到 `int` 变量就读整数，读到 `string` 变量就读一个单词（遇到空格或换行停下）。`cin` 会自动跳过前面的空格和换行，所以不用像 Python 那样 `split()`。
> - **`while (cin >> x)` 为什么能读到结束**：`cin` 读不到东西时，整个 `cin >> x` 的值相当于「假」，循环就结束了。

> [!tip]- `::` 和 namespace 是什么？
> 
> **namespace（命名空间）就是给名字分组的「姓氏」，目的是防止重名。**它像 Java 里的包（`java.util.List`）或 Python 里的模块（`math.sqrt`）。
> 
> **`::` 读作「属于」。**`std::cout` 就是「`std` 这个命名空间里的 `cout`」。标准库里所有名字都放在 `std` 里，所以完整写法是 `std::cout`、`std::vector`；写了 `using namespace std;` 之后就可以省掉前缀。
> 
> 下面的例子**故意没写** `using namespace std;`，所以每个标准库名字都带着 `std::`；同时自己定义了两个命名空间，里面各有一个叫 `val` 的变量，靠前缀区分：
> 
> ```cpp
> #include <iostream>
> #include <string>
> 
> // 自己定义两个命名空间，各有一个同名变量 val：靠 :: 前缀区分
> namespace A { int val = 1; }
> namespace B { int val = 2; }
> 
> int main() {
>     // 不写 using namespace std 时，标准库的名字都要带 std:: 前缀
>     std::ios::sync_with_stdio(false);
>     std::cin.tie(nullptr);
> 
>     std::cout << A::val << " " << B::val << "\n";
> 
>     int a, b;
>     std::cin >> a >> b;                      // 一次读两个数
>     std::cout << a << b << " " << a + b << "\n";   // << 可以连着写
> 
>     std::string name;
>     std::cin >> name;
>     std::cout << "hi " << name << "\n";
>     return 0;
> }
> ```
> 
> 输入 `3 4` 和 `Anna`（两行），实际输出：
> 
> ```text
> 1 2
> 34 7
> hi Anna
> ```
> 
> 第一行说明 `A::val` 和 `B::val` 是两个不同的变量；第二行的 `34` 说明 `cout` 不会自动加空格。
> 
> 再记一个容易混的点：**`::` 跟在「命名空间 / 类的名字」后面，`.` 跟在「具体的变量」后面。**比如 `cin.tie(nullptr)` 里的 `cin` 是一个具体对象，用点；`std::cout` 里的 `std` 是一个命名空间，用 `::`。

> [!tip]- `ios::sync_with_stdio(false)` 和 `cin.tie(nullptr)` 是什么？
> 
> **`ios` 是标准库里管输入输出流的一个类（class）**，`sync_with_stdio` 是它自带的一个函数，所以写成 `类名::函数名`。因为前面有 `using namespace std;`，`ios` 就是 `std::ios`；上面示例没写 `using`，所以写成了 `std::ios::sync_with_stdio`。
> 
> 这两行是**竞赛里通用的加速写法**，不用深究，了解效果即可：
> 
> - **④ `ios::sync_with_stdio(false)`**：C++ 的 `cin` / `cout` 默认会和 C 语言的 `scanf` / `printf` 保持同步，这样两套混用也不会乱序，但同步有额外开销。传入 `false` 就是关掉同步。**代价是之后不能再混用两套输入输出。**
> - **⑤ `cin.tie(nullptr)`**：`cin` 默认和 `cout` 「绑」在一起，每次读入前都会先把 `cout` 里没输出的内容冲出去。`nullptr` 是「空指针」，表示不绑任何东西，省掉这个动作。**需要「问一句答一句」的交互题除外**，普通题放心用。
> - 数据量大时这两行能省时间，数据很小的题写不写都行，养成习惯就不会漏。

---

## 2. 变量、类型与取整

| 类型 | 说明 | 注意 |
| --- | --- | --- |
| `int` | 整数 | 通常约到 $\pm 2.1\times10^9$，累加、相乘容易溢出 |
| `long long` | 大整数 | 超过 `int` 范围就用它，字面量写成 `1000000LL` |
| `double` | 浮点数 | 整数转浮点：`(double)7 / 2` |
| `bool` | 布尔 | 输出时是 `1` / `0`，不是 `True` / `False` |
| `string` | 字符串 | `s[0]` 是单个 `char`，不是字符串 |
| `vector<int>` | 动态数组 | `vector<int> v(n)` 长度为 $n$、初值全是 0 |

> [!example]- 完整示例（已编译运行）：把上面所有语法点串起来
> 
> ```cpp
> #include <bits/stdc++.h>
> using namespace std;
> 
> struct Edge {                       // 结构体：把几个字段打包
>     int to;
>     int w;
> };
> 
> int add(int a, int b) {             // 函数：返回类型 名字(参数)
>     return a + b;
> }
> 
> void bump(int& x) {                 // 引用参数：函数里改了，外面也变（Python 里没有对应物）
>     x++;
> }
> 
> long long sumVec(const vector<int>& v) {   // const 引用：只读、不拷贝
>     long long s = 0;
>     for (int x : v) s += x;         // 范围 for，类似 Python 的 for x in v
>     return s;
> }
> 
> int main() {
>     // 变量：必须声明类型，语句以分号结尾
>     int a = 7;
>     long long big = 1000000LL * 1000000LL;   // 超过 int 范围用 long long
>     double d = 3.5;
>     bool ok = true;
>     string s = "abc";
>     cout << a << " " << big << " " << d << " " << ok << " " << s << "\n";
> 
>     // 输入输出
>     int n;
>     cin >> n;                       // 读一个整数
>     vector<int> v(n);               // 长度为 n 的数组，初值 0
>     for (int i = 0; i < n; i++) cin >> v[i];
> 
>     // 分支与循环
>     if (n > 3) cout << "big\n";
>     else if (n == 3) cout << "three\n";
>     else cout << "small\n";
> 
>     int i = 0;
>     while (i < 2) { cout << i << " "; i++; }
>     cout << "\n";
> 
>     // 函数与引用
>     int t = add(2, 3);
>     bump(t);
>     cout << t << " " << sumVec(v) << "\n";
> 
>     // 数组、字符串、结构体
>     int arr[3] = {10, 20, 30};
>     cout << arr[1] << " " << s.size() << " " << s[0] << "\n";
>     Edge e = {5, 9};
>     vector<Edge> g;
>     g.push_back(e);
>     g.push_back({1, 2});
>     cout << g.size() << " " << g[1].to << "\n";
> 
>     // 取整与取模：整数相除直接向零取整
>     cout << 7 / 2 << " " << 7 % 2 << " " << -7 / 2 << " " << (double)7 / 2 << "\n";
> 
>     // 读到文件结束（有些题不给 n）
>     int x, cnt = 0;
>     while (cin >> x) cnt++;
>     cout << cnt << "\n";
>     return 0;
> }
> ```
> 
> 输入 `3`、`1 2 3`、`4 5 6`（三行），实际输出：
> 
> ```text
> 7 1000000000000 3.5 1 abc
> three
> 0 1 
> 6 6
> 20 3 a
> 2 1
> 3 1 -3 3.5
> 3
> ```
> 
> 对应关系：最后的 `3` 是读完 `n` 和前三个数之后，`while (cin >> x)` 数到的剩余整数个数（`4 5 6`）。

---

## 3. 关键行为与边界

> [!tip]- 为什么函数参数要加 `&`
> 
> C++ 默认**按值传递**：函数拿到的是副本，改了不影响外面。参数写成 `int& x`（引用）才能让函数修改调用者的变量，如 `bump(t)` 之后 `t` 变了。
> 
> 传大容器时也常写 `const vector<int>& v`：`&` 避免把整个数组拷贝一遍，`const` 保证函数里只读。Python 传的是对象的引用，函数里修改列表外面也会变；C++ 里这要显式写 `&`，这是从 Python 过来最需要建立的新概念。

> [!warning]- 边界条件
> 
> - **整数除法**：`7 / 2` 是 `3`，`-7 / 2` 是 `-3`（向零取整）。Python 的 `//` 对负数向下取整，结果不同，见 [[Python_除法与取整]]。
> - **取模**：`-7 % 2` 是 `-1`，不是 Python 里的 `1`。涉及负数取模时要自己调整成非负。
> - **溢出**：`int` 相乘或累加超出范围会出错，有符号整数溢出在标准里是未定义行为。要乘大数时写 `1LL * a * a`，让乘法在 `long long` 里进行。
> - **`size()` 是无符号数**：空的 `vector` 做 `v.size() - 1` 会得到一个极大的数，而不是 `-1`。需要和负数比较或做减法时先转成 `(int)v.size()`。
> - **数组越界**：`v[i]` 越界不会报错，结果未定义。`v[i]` 不检查范围，下标是否合法要自己保证。

---

## 4. 补充示例：常用小函数与易混写法

> [!success]- 完整示例（已编译运行）
> 
> ```cpp
> #include <bits/stdc++.h>
> using namespace std;
> 
> int main() {
>     // 取模：负数取模结果带符号（Python 里 -7 % 2 是 1）
>     cout << -7 % 2 << " " << 7 % -2 << "\n";
> 
>     // char 参与运算会变成整数
>     string s = "abc";
>     cout << s[0] << " " << s[0] + 1 << " " << (char)(s[0] + 1) << "\n";
> 
>     // 乘法溢出：先转 long long 再乘
>     int a = 100000;
>     cout << 1LL * a * a << "\n";
> 
>     // size() 是无符号数：空 vector 减 1 会变成极大的数
>     vector<int> e;
>     cout << e.size() - 1 << " " << (int)e.size() - 1 << "\n";
> 
>     // 字符串与常用函数
>     s += "d";
>     cout << s << " " << s.substr(1, 2) << " " << (s == "abcd") << "\n";
>     cout << to_string(12) + "x" << " " << stoi("34") + 1 << "\n";
>     int x = 3, y = 8;
>     swap(x, y);
>     cout << x << " " << y << " " << max(x, y) << " " << min(x, y) << " " << abs(-5) << "\n";
> 
>     // 二维 vector 与倒序循环
>     int n = 3;
>     vector<vector<int>> g(n);
>     g[0].push_back(5);
>     g[2].push_back(7);
>     g[2].push_back(9);
>     for (int i = n - 1; i >= 0; i--) cout << g[i].size() << " ";
>     cout << "\n";
> 
>     // 逻辑运算符
>     bool p = true, q = false;
>     cout << (p && q) << (p || q) << (!p) << "\n";
>     return 0;
> }
> ```
> 
> 实际输出：
> 
> ```text
> -1 1
> a 98 b
> 10000000000
> 18446744073709551615 -1
> abcd bc 1
> 12x 35
> 8 3 8 3 5
> 2 0 1 
> 010
> ```
> 
> 逐行对应：负数取模；`char` 参与运算变成整数；`1LL` 防溢出；`size()` 减 1 变成极大数；字符串拼接、截取、比较；`to_string` 和 `stoi`；`swap` / `max` / `min` / `abs`；二维 `vector` 与倒序循环；逻辑运算。

---

## 5. 与相近写法怎么选

| 需求 | 推荐写法 | 原因 |
| --- | --- | --- |
| 读入 | `cin >> x` 加两行提速 | 比 `scanf` 省去格式串，类型自动匹配 |
| 遍历容器 | `for (int x : v)` | 不必写下标，和 Python 的 `for x in v` 对应 |
| 需要下标 | `for (int i = 0; i < n; i++)` | 注意 `n` 要和 `v.size()` 类型一致，必要时转 `(int)` |
| 数字转字符串 / 字符串转数字 | `to_string(x)` / `stoi(s)` | 对应 Python 的 `str(x)` / `int(s)` |
| 交换 | `swap(x, y)` | Python 里写 `x, y = y, x` |

---

## 6. 常见易错点

> [!warning]- 易错点
> 
> - **忘了 `;`**：每条语句必须以分号结尾，结构体定义的右花括号后面也要有分号。实测漏掉第 4 行的分号，报错 `expected ',' or ';' before 'cout'` 却指向第 5 行，所以**错误出在报错位置的上一行**。
> - **`'cout' was not declared in this scope; did you mean 'std::cout'?`**：忘了写 `using namespace std;`，或者没带 `std::` 前缀。
> - **`'vector' was not declared in this scope`**：没引入对应的头文件。用 `#include <bits/stdc++.h>` 就不会漏。
> - **`reference to 'count' is ambiguous`**：你自己起的变量名（如 `count`）和标准库里的同名函数撞了，因为 `using namespace std;` 把 `std` 里的名字都放进来了。改个名即可，如 `cnt`。
> - **赋值号和比较号写混**：`if (x = 3)` 是赋值，条件永远为真；要比较必须写成 `if (x == 3)`。
> - **未初始化的局部变量**：`int cnt;` 里的值是随机的，要自己写 `int cnt = 0;`。`vector<int> v(n)` 才会自动置 0。
> - **用 `int` 存会超范围的数**：累加、乘法、阶乘一律先想一下会不会超 $2\times10^9$。
> - **`size()` 减法回绕**：见上，空容器减 1 变成极大数，循环条件会失控。
> - **`char` 当字符串用**：`s[0] + 1` 得到的是整数 `98`，想要字符要转 `(char)`。
> - **函数里改了参数但外面没变**：需要修改调用者的变量时参数要加 `&`。

---

## 复杂度

> [!summary]- 复杂度
> 
> - 下标访问 `v[i]`：$O(1)$。
> - `push_back`：均摊 $O(1)$，偶尔扩容时会整体搬移。
> - `s.substr(pos, len)`：$O(\text{len})$，因为要拷贝出一个新字符串。
> - `sort`：$O(n \log n)$。
> - 本篇的语法本身不改变算法复杂度；常见的额外开销来自**按值传递大容器**，每次调用 $O(n)$，用 `const 引用` 即可避免。

---

## 一句话总结

C++ 的逻辑和 Python 一致，真正要补的是：**声明类型、整数溢出与向零取整、`size()` 无符号、引用传参**。

---

## 模板归纳

看到以下信号时，回来查这篇：

- 要把 Python 解法翻成 C++，但忘了语法写法。
- C++ 程序结果不对，怀疑取整、取模、溢出或 `size()` 回绕。
- 在牛客网页里写不出能编译的代码。

练习建议：**直接在牛客网页的在线编辑器里写并点"自测"**。牛客题目页上有提醒，校招时部分企业笔试会禁止编程题跳出页面，在线练习是对这个环境最好的适应，也省去本地配置编译器。

相关笔记与教程：

- 同类：[[Cpp_STL最小子集]]（`set` / `multiset` / `map` / `priority_queue` 速查）
- 对照：[[Python_除法与取整]]、[[Python_常用内置函数]]
- 教程：[OI Wiki：语言基础](https://oi-wiki.org/lang/)、[OI Wiki：C++ 语法基础](https://oi-wiki.org/lang/basic/)、[LearnCpp.com](https://www.learncpp.com/)
