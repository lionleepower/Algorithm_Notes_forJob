
# 堆 / 优先队列：在 k 个候选中反复取极值

堆 (heap) 用 $O(\log k)$ 的代价维护「一堆数里谁最小」，并支持动态插入。当你需要**反复**从若干个候选中取极值、且候选集合会不断变化时，就该想到它 —— LeetCode 23「合并 K 个升序链表」正是这个形状。

注意「极值」是**单向**的：一个堆只对**一个方向**提供 $O(1)$ 查询，另一个方向和普通数组一样贵。见第 3 节。

---

## 思路

### 不用堆会怎样

合并 K 个升序链表，最朴素的做法是：每次扫描 k 个链表的头节点，挑出最小的接到结果上。

```python
# 朴素做法：每次线性扫描 k 个候选
while any(lists):
    best = min((i for i in range(k) if lists[i]), key=lambda i: lists[i].val)
    cur.next = lists[best]
    lists[best] = lists[best].next
    cur = cur.next
```

设总节点数为 $n$，则总共要取 $n$ 次最小值，每次扫描 $O(k)$ → **$O(nk)$**。当 $k = 10^4$ 时直接超时。

问题出在：每次 `min()` 都从零开始扫，上一轮已经比较出来的大小关系**全部作废**。而实际上，每轮只有**一个**候选发生了变化（被取走的那条链前进一格），其余 $k-1$ 个纹丝不动 —— 重扫是巨大的浪费。

### 堆为什么合适

堆恰好是「维护极值 + 支持局部更新」的结构。它不追求全局有序（那要 $O(k\log k)$），只维持一个**弱得多的不变量 (invariant)**：

> **堆序性质 (heap property)**：每个节点的值 ≤ 其所有子节点的值（min-heap）。

这个性质只约束父子之间，兄弟之间毫无关系。代价小，但已经足够保证**根节点是全局最小**。于是：

- 取最小 → 直接读根，$O(1)$
- 取走后修复 → 只需沿一条路径下沉 (sift down)，$O(\log k)$
- 新候选入堆 → 沿一条路径上浮 (sift up)，$O(\log k)$

总复杂度降为 $O(n \log k)$。

> [!tip]- 核心思路
> 
> 堆里始终只放 **k 个链表各自的当前头节点**，堆大小恒 ≤ k。每弹出一个最小节点，就把它的后继补进去 —— 候选集合的规模不变，只是内容更新。
> 
> ```python
> h = [head for head in lists if head]   # 只放头节点，不是所有节点
> heapify(h)
> while h:
>     node = heappop(h)                  # 剩余节点中的最小者
>     if node.next:
>         heappush(h, node.next)         # 补充该链的下一个候选
>     cur.next = node
>     cur = cur.next
> ```
> 
> 不变量：**堆中恰好包含每条未耗尽链表的第一个未使用节点**。因为每条链自身有序，全局最小值必定在这 k 个之中。

---

## 1. 导入与创建

Python 的 `heapq` 操作的是**普通 list**，没有独立的 Heap 类 —— 它把 list 当作数组式的完全二叉树来操作。

> [!success]- 基础语法
> 
> ```python
> from heapq import heapify, heappush, heappop, heappushpop, heapreplace, nlargest, nsmallest
> 
> h = []                      # 空堆就是空 list
> heappush(h, 3)              # 逐个插入：O(log n) × n = O(n log n)
> 
> h = [5, 1, 4, 2]
> heapify(h)                  # 原地堆化：O(n)，比逐个 push 更快
> # h 变成 [1, 2, 4, 5]（合法 min-heap，但并非排序结果）
> ```
> 
> C++ 用 `priority_queue`，**默认是 max-heap**，求最小值必须显式传比较器：
> 
> ```cpp
> #include <queue>
> priority_queue<int> maxHeap;                                  // 默认大根堆
> priority_queue<int, vector<int>, greater<int>> minHeap;       // 小根堆
> 
> vector<int> v{5, 1, 4, 2};
> priority_queue<int, vector<int>, greater<int>> pq(v.begin(), v.end());  // O(n) 建堆
> ```

数组表示的下标关系（0-indexed），理解 $O(\log n)$ 从何而来的关键：

|关系|公式|
|---|---|
|左子节点|`2 * i + 1`|
|右子节点|`2 * i + 2`|
|父节点|`(i - 1) // 2`|
|叶节点范围|下标 `n // 2` 到 `n - 1`|

因为是**完全二叉树 (complete binary tree)**，树高恒为 $\lfloor \log_2 n \rfloor$，且数组中间无空洞 —— 这就是堆能用连续数组存储、缓存局部性 (cache locality) 良好的原因。

---

## 2. 核心操作

|Python|C++|作用|复杂度|
|---|---|---|---|
|`h[0]`|`pq.top()`|查看堆顶（唯一免费的那个方向）|$O(1)$|
|`heappush(h, x)`|`pq.push(x)`|插入，上浮|$O(\log n)$|
|`heappop(h)`|`pq.pop()`（无返回值）|弹出堆顶，下沉修复|$O(\log n)$|
|`heapify(h)`|构造函数传迭代器|原地建堆|$O(n)$|
|`heapreplace(h, x)`|—|先 pop 再 push|$O(\log n)$，一次调整|
|`heappushpop(h, x)`|—|先 push 再 pop|$O(\log n)$|
|`nsmallest(k, it)`|—|取最小的 k 个|$O(n \log k)$|
|`nlargest(k, it)`|—|取最大的 k 个|$O(n \log k)$|
|`max(h)` / `min(h)`|—|查**非堆顶**方向的极值|$O(n)$，堆帮不上忙|

> [!example]- 最小示例
> 
> ```python
> from heapq import heapify, heappop
> 
> h = [5, 1, 4, 2, 3]
> heapify(h)
> print(h)                                   # [1, 2, 4, 5, 3] —— 未排序！
> print([heappop(h) for _ in range(5)])      # [1, 2, 3, 4, 5] —— 逐个弹出才有序
> ```
> 
> 注意第一行输出：`4` 排在 `2` 后面、`3` 排在最末，但它们都是各自父节点的子节点且更大 —— 堆序性质成立。**堆不等于排好序的数组**，这是最常见的误解。

### 为什么 `heapify` 是 $O(n)$ 而不是 $O(n\log n)$

从最后一个非叶节点倒序向前，对每个节点做一次下沉。关键在于**大部分节点很浅**：约 $n/2$ 个叶节点下沉 0 层，$n/4$ 个下沉 ≤ 1 层，$n/8$ 个 ≤ 2 层……

$$\sum_{h=0}^{\log n} \frac{n}{2^{h+1}} \cdot h = n \sum_{h=0}^{\log n} \frac{h}{2^{h+1}} < n \cdot 1 = O(n)$$

所以本题里 `heapify(h)` 建 k 个头节点的堆是 $O(k)$，而不是 $O(k \log k)$。用 `for head in lists: heappush(h, head)` 则退化为 $O(k\log k)$ —— 结果正确但不必要。

---

## 3. 关键行为与边界

### 3.1 堆是单向的：另一个方向的极值不免费

`heapq` 只提供 min-heap，`h[0]` 是最小值。那最大值在哪？**不是 `h[-1]`** —— 用上面那个例子直接证伪：

```python
from heapq import heapify

h = [5, 1, 4, 2, 3]
heapify(h)
print(h)        # [1, 2, 4, 5, 3]
print(h[-1])    # 3  ← 不是最大值
print(max(h))   # 5  ← 在下标 3
```

画成树就清楚了：

```
        1(idx0)
       /       \
    2(idx1)   4(idx2)
    /     \
 5(idx3) 3(idx4)
```

`5` 和 `3` 都是叶子，谁在数组里靠后完全取决于建堆时的下沉路径，与值无关。**堆序只约束父子，兄弟与堂兄弟之间毫无关系**，所以数组末尾那个元素没有任何大小语义。

唯一能确定的是：**最大值必定是某个叶节点 (leaf)**。反证 —— 若最大值在内部节点，它必有子节点，而堆序要求子 ≥ 父，那子节点也是最大值，答案总可以挪到叶子上。

```python
max_val = max(h[len(h) // 2:])    # 只扫叶子，约 n/2 个
```

但这仍是 $O(n)$，**常数减半、渐进不变**。实战里直接 `max(h)` 即可，没必要卖弄。

> [!warning]- 单向性
> 
> min-heap 对最大值**不提供任何加速**。$O(1)$ 查极值这个能力是单向的：选了 min-heap，就只有最小值免费；查最大值、查任意元素，一律 $O(n)$。
> 
> `h[-1]`、`h[1]` 等任何非 `h[0]` 的下标都**没有语义**，不要读它们。

需要另一个方向时的四种做法：

|需求|做法|复杂度|
|---|---|---|
|只要最大值（Python）|全部取负存 min-heap，弹出时再取负|$O(\log n)$|
|只要最大值（C++）|`priority_queue` 默认就是 max-heap|$O(\log n)$|
|**同时**要最大和最小|双堆 / `SortedList` / `multiset`|$O(\log n)$|
|一次性取最大的 K 个|`heapq.nlargest(k, it)`|$O(n\log k)$|

**取负法**（Python 最常用）：

```python
from heapq import heapify, heappush, heappop

nums = [5, 1, 4, 2, 3]
h = [-x for x in nums]
heapify(h)
print(-heappop(h))          # 5
heappush(h, -10)
print(-h[0])                # 10
```

元素是 tuple 时只对排序键取负，其余键保持原方向：

```python
heappush(h, (-freq, word))  # freq 降序，word 升序
```

**C++ 方向恰好相反**，跨语言刷题的高频翻车点：

```cpp
priority_queue<int> maxHeap;                              // top() 是最大值（默认）
priority_queue<int, vector<int>, greater<int>> minHeap;   // top() 是最小值
```

同一个 `top()`，含义完全由比较器决定。

**双堆**（既要最大又要最小，如 LC 295 数据流中位数）：

```python
small = []   # max-heap（存负数），堆顶是「较小一半」的最大值
large = []   # min-heap，堆顶是「较大一半」的最小值
```

两个堆背对背，各自只负责一个方向。若需要「随时查任意排名」，那已经超出堆的能力 —— 该用 `sortedcontainers.SortedList` 或 C++ 的 `multiset`。

### 3.2 比较机制：一切走 `__lt__`

> [!tip]- 为什么没有 key= 参数
> 
> `heapq` 的比较全部走 `<` 运算符（即 `__lt__`）。它不接受 `key=`，也没有 `reverse=` —— 所有「换个排序标准」的需求，都必须落到**被比较对象本身**上：要么改对象的 `__lt__`，要么把对象包进一个天然可比较的容器（tuple）里。上面的取负法就是后者的特例。

### 3.3 本题的核心坑：ListNode 不可比较

`ListNode` 没有定义 `__lt__`，直接入堆会炸：

```python
h = [head for head in lists if head]
heapify(h)
# TypeError: '<' not supported between instances of 'ListNode' and 'ListNode'
```

题解给出的写法是**猴子补丁 (monkey patching)** —— 给类动态挂上比较方法：

```python
ListNode.__lt__ = lambda a, b: a.val < b.val
```

这行写在 class 外部，运行时修改了 `ListNode` 这个类对象的属性。之后所有 `ListNode` 实例之间的 `<` 都走这个 lambda。

> [!warning]- 边界条件
> 
> - **空输入**：`lists = []` 或 `lists = [None, None]`。列表推导 `[head for head in lists if head]` 已经过滤掉 `None`，`h` 为空 → `while h` 不执行 → 返回 `dummy.next` 即 `None`。✅ 无需特判。
> - **单链表**：`k = 1` 时堆里恒有 1 个元素，退化成逐个搬运，结果正确。
> - **值相等**：`__lt__` 返回 `False`，堆不做交换，两个节点顺序任意 —— 本题不要求稳定性，无所谓。但若换成 tuple 写法则必须补 tiebreaker，见下。
> - **忘记判 `if node.next`**：会把 `None` 推入堆，下一轮 `heappop` 出 `None` 后访问 `node.next` → **AttributeError**。
> - **猴子补丁的副作用**：修改的是全局的类对象。在 LeetCode 单次提交里无害，但在真实工程中会影响所有使用该类的代码，属于要慎用的技巧。

---

## 4. 实例一：合并 K 个升序链表（Python 写法一，猴子补丁）

输入 k 条各自升序的链表，输出一条合并后的升序链表。选堆是因为每轮都要在 k 个候选头节点中取最小，且取走后要立即补入新候选。

> [!success]- 完整实现
> 
> ```python
> from heapq import heapify, heappush, heappop
> 
> # 让堆可以比较节点大小
> ListNode.__lt__ = lambda a, b: a.val < b.val
> 
> class Solution:
>     def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:
>         cur = dummy = ListNode()          # 哨兵节点，作为合并后链表头节点的前一个节点
>         h = [head for head in lists if head]   # 把所有非空链表的头节点入堆
>         heapify(h)                        # O(k) 堆化
>         while h:                          # 循环直到堆为空
>             node = heappop(h)             # 剩余节点中的最小节点
>             if node.next:                 # 下一个节点不为空
>                 heappush(h, node.next)    # 下一个节点有可能是最小节点，入堆
>             cur.next = node               # 把 node 添加到新链表的末尾
>             cur = cur.next                # 准备合并下一个节点
>         return dummy.next                 # 哨兵节点的下一个节点就是新链表的头节点
> ```

### 主流程拆解

|变量|角色|
|---|---|
|`dummy`|哨兵节点 (sentinel)，避免为「第一个节点」写特判|
|`cur`|结果链表的**当前末尾**，每轮往后推一格|
|`h`|候选池，恒等于「每条未耗尽链表的当前头节点」|
|`node`|本轮胜出者，直接**复用原节点**，不新建对象|

`cur = dummy = ListNode()` 是链式赋值 (chained assignment)，两个名字绑定到**同一个对象**。之后 `cur = cur.next` 是 rebinding，`dummy` 不受影响，始终指着哨兵 —— 这正是最后能靠 `dummy.next` 找回表头的原因。

### 最容易写错的位置

**入堆顺序与出堆顺序不同**。`heappush(h, node.next)` 推进去的节点，不一定下一轮就出来 —— 它会和其余 $k-1$ 个候选一起重新竞争。这与「归并两条链」时的直觉不同，那里指针推进和输出是同步的。

**别把所有节点一次性入堆**。有人写成把 n 个节点全塞进堆再逐个弹出，结果正确但复杂度变成 $O(n\log n)$，且空间 $O(n)$ —— 完全放弃了「每条链自身已有序」这个前提。堆大小必须控制在 k。

---

## 5. 实例二：不改 `__lt__` 的写法（tuple 包装）

猴子补丁污染全局。更干净的做法是把节点包进 tuple —— tuple 的比较是**字典序 (lexicographic)**，逐元素比较，遇到第一个不等就停。

> [!success]- 完整实现（Python 写法二）
> 
> ```python
> from heapq import heapify, heappush, heappop
> 
> class Solution:
>     def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:
>         cur = dummy = ListNode()
>         h = [(head.val, i, head) for i, head in enumerate(lists) if head]
>         heapify(h)
>         while h:
>             _, i, node = heappop(h)
>             if node.next:
>                 heappush(h, (node.next.val, i, node.next))
>             cur.next = node
>             cur = cur.next
>         return dummy.next
> ```

**为什么中间必须塞一个 `i`？**

如果只写 `(head.val, head)`，当两个节点 `val` 相等时，tuple 比较会继续比第二个元素 —— 也就是拿 `ListNode` 和 `ListNode` 比 —— 又回到 `TypeError`。加入**唯一且可比较**的 `i` 作为 tiebreaker，保证比较永远在第二项就分出胜负，第三项的 `node` 永远不会被比较到。

> [!warning]- 这个坑非常隐蔽
> 
> `(val, node)` 的写法在**没有重复值**的测试用例上能通过，一旦出现相等的 `val` 才崩溃。属于典型的「本地测试过了、提交挂了」类型 bug。
> 
> 用 `i` 还是用递增计数器都可以；本题里同一条链的后继复用同一个 `i`，因为不同链的 `i` 已经互不相同。

> [!summary]- 当前实例复杂度
> 
> - 时间复杂度：$O(n\log k)$。共 $n$ 个节点，每个节点恰好入堆一次、出堆一次，单次操作 $O(\log k)$（堆大小恒 ≤ k）。建堆 $O(k)$ 可忽略。
> - 空间复杂度：$O(k)$ 额外空间 —— 堆里最多 k 个元素。返回的链表**复用原节点**，不计入额外空间。

### C++ 写法

> [!success]- C++ 完整实现
> 
> ```cpp
> class Solution {
> public:
>     ListNode* mergeKLists(vector<ListNode*>& lists) {
>         // lambda 比较器：a->val > b->val 得到小根堆（注意方向与直觉相反）
>         auto cmp = [](ListNode* a, ListNode* b) { return a->val > b->val; };
>         priority_queue<ListNode*, vector<ListNode*>, decltype(cmp)> pq(cmp);
> 
>         for (auto head : lists)
>             if (head) pq.push(head);
> 
>         ListNode dummy{};              // 栈上对象，函数返回即销毁
>         ListNode* cur = &dummy;
>         while (!pq.empty()) {
>             ListNode* node = pq.top();
>             pq.pop();                  // pop() 无返回值，必须先 top()
>             if (node->next) pq.push(node->next);
>             cur->next = node;
>             cur = cur->next;
>         }
>         return dummy.next;             // 返回的是堆上节点的指针，安全
>     }
> };
> ```

C++ 三个和 Python 不同的点：

1. **比较器方向反直觉**。`priority_queue` 的比较器语义是「a 的优先级低于 b」，所以写 `a->val > b->val` 才得到小根堆。记法：**你写的比较为真者，排在后面**。
2. **`top()` 和 `pop()` 分离**。`pop()` 返回 `void`，必须先 `top()` 取值再 `pop()`。写反了就是取到已弹出的元素。
3. **没有 $O(n)$ 建堆的 push 循环**。上面用 `for` + `push` 是 $O(k\log k)$；要 $O(k)$ 建堆需先收集到 vector 再用迭代器构造函数：`priority_queue<...> pq(heads.begin(), heads.end(), cmp);`

C++20 之前，无捕获 lambda 不能默认构造，所以必须写 `pq(cmp)` 把比较器实例传进去；C++20 起可以直接写 `pq;`。

另外注意：C++ 的 `priority_queue` **只暴露 `top()`**，连底层容器都藏起来了 —— 想扫叶子找反方向极值都做不到（除非继承访问 protected 的 `c`）。这比 Python 的 list 更严格地体现了「堆是单向的」。

---

## 6. 堆 vs 栈：两组同名概念

中文里「堆」「栈」各自指两样完全不同的东西 —— **数据结构**和**内存区域**。本题的 `h` 是前者；C++ 代码里 `ListNode dummy{}` 住在后者的栈区。二者除了命名巧合外没有关系。

### 6.1 作为数据结构

||Heap（堆）|Stack（栈）|
|---|---|---|
|不变量|父 ≤ 子（部分有序）|LIFO，后进先出|
|取出的是|**单方向的全局极值**|**最近压入者**|
|push / pop|$O(\log n)$|$O(1)$|
|查看顶部|$O(1)$|$O(1)$|
|查非顶部元素|$O(n)$，无加速|$O(n)$，无加速|
|底层|完全二叉树，数组存储|数组或链表|
|是否有序|只保证根，其余无序|完全不涉及大小|
|Python|`heapq`|`list.append` / `list.pop`|
|C++|`priority_queue`|`stack` / `vector`|

**判断标准**：堆关心「谁**最小**」，栈关心「谁**最新**」。本题要在 k 个候选中反复取最小 —— 与插入时间无关 —— 所以是堆。若题目问的是「最近一个未匹配的左括号」，那是栈。

两者还有一个共同点值得记：**都只有「顶」是免费的**。栈只能碰栈顶，堆只能碰 `h[0]`；想看第二个、想看反方向，都得付出线性代价或换结构。

### 6.2 作为内存区域

||Heap（堆区）|Stack（栈区）|
|---|---|---|
|分配|运行时显式申请 (`malloc` / `new`)|函数调用自动|
|释放|手动或 GC|函数返回自动弹帧|
|速度|慢，需查找空闲块|快，只移动 stack pointer|
|容量|大，受虚拟地址空间限制|小，典型 1–8 MB|
|生命周期|可跨函数存活|与作用域绑定|
|溢出表现|分配失败 / OOM|**stack overflow**|

回到 C++ 代码，这个区别是**实打实起作用**的：

```cpp
ListNode dummy{};      // 栈上，函数返回时销毁
return dummy.next;     // ✅ 返回的是 dummy 内部存的指针，指向堆上的节点
// return &dummy;      // ❌ 悬垂指针 (dangling pointer)，dummy 已不存在
```

`dummy` 本身随函数结束消失，但它的 `next` 字段保存的是一个**指向堆上真实节点的指针**，复制这个指针出去完全安全。这也是为什么哨兵节点可以放栈上、不必 `new`。

Python 里没有这个顾虑 —— 所有对象（包括 `ListNode`、`list`、`int`）都在堆上，栈帧里只存「名字 → 对象」的引用。`ListNode()` 创建的哨兵对象在函数返回后依然被 `dummy.next` 链条引用着，引用计数不为零，不会被回收。

> [!tip]- 唯一的交集
> 
> 函数调用栈 (call stack) 是「栈这个数据结构」在系统层面的实例：每次调用 push 一个 frame，返回时 pop。内存那块区域因此得名「栈」。
> 
> 而内存的「堆」和堆数据结构**毫无关系** —— 它是历史命名，早期指一堆无组织的空闲内存块。这是初学者最容易混淆的地方，面试里可以主动点破。

---

## 7. 与相近解法怎么选

|需求|推荐写法|原因|
|---|---|---|
|k 较大、追求代码短|**堆**，$O(n\log k)$ / 空间 $O(k)$|逻辑直白，一个 while 搞定|
|想把空间压到 $O(1)$|**分治两两合并**（迭代版）|同为 $O(n\log k)$，但不需要额外容器|
|k 很小（如 ≤ 3）|朴素扫描 $O(nk)$|常数更小，堆的开销反而不划算|
|数据流持续到来|**堆**|分治要求一次拿到全部输入，流式场景不适用|
|需要**双向**极值 / 任意排名|`SortedList` / `multiset` / 双堆|单个堆做不到，别硬凑|

分治写法的核心：

```python
def mergeKLists(self, lists):
    if not lists: return None
    while len(lists) > 1:
        merged = []
        for i in range(0, len(lists), 2):
            a = lists[i]
            b = lists[i + 1] if i + 1 < len(lists) else None
            merged.append(self.merge2(a, b))
        lists = merged
    return lists[0]
```

每轮链表数量减半 → $\log k$ 轮，每轮总共处理 $n$ 个节点 → $O(n\log k)$。**和堆同阶**，但常数通常更小（没有堆调整的比较开销），且不需要解决 `ListNode` 不可比较的问题。面试里两种都能说出来是加分项。

---

## 8. 常见易错点

> [!warning]- 易错点
> 
> - **以为 `h[-1]` 是最大值**：数组末尾没有任何大小语义。最大值只保证在叶节点区（下标 `n // 2` 起），且查它仍是 $O(n)$。
> - **忘记 `if node.next` 判空**：把 `None` 推入堆，下一轮出堆后访问属性 → AttributeError。
> - **`(val, node)` 少了 tiebreaker**：值相等时 tuple 比较落到 `ListNode` 上 → TypeError，且只在有重复值的用例上暴露。
> - **把所有节点全部入堆**：结果对但复杂度退化为 $O(n\log n)$、空间 $O(n)$，浪费了「每条链已有序」的前提。
> - **C++ 比较器写反**：`a->val < b->val` 得到的是大根堆。记「你写的比较为真者，排在后面」。
> - **C++ 用 `pq.pop()` 的返回值**：它返回 `void`，必须先 `top()`。
> - **以为 `heapify` 后数组就有序**：打印出来常常不是升序，这是正常的 —— 只有逐个 `heappop` 才产生有序序列。
> - **忘记 Python 只有 min-heap**：求最大值系列题（如 Top K Largest）需要取负，或改用 `nlargest`。
> - **取负法忘了取回来**：`heappop` 出来的是负数，输出前必须再加负号；tuple 写法则只对排序键取负，别把整个 tuple 都反了。
> - **在多线程/工程代码里用猴子补丁**：`ListNode.__lt__ = ...` 修改的是全局类对象，会影响所有使用方。

---

## 复杂度

> [!summary]- 复杂度
> 
> - 单次 `heappush` / `heappop`：$O(\log k)$，因为完全二叉树高度为 $\lfloor\log_2 k\rfloor$，上浮/下沉最多走一条根到叶的路径。
> - 查堆顶 `h[0]`：$O(1)$。查**反方向极值或任意元素**：$O(n)$ —— 堆不提供加速。
> - `heapify` 建堆：$O(k)$，而非 $O(k\log k)$ —— 大部分节点是叶子，下沉距离为 0。
> - 完整流程：$O(n\log k)$。$n$ 个节点各入堆出堆一次，堆大小恒 ≤ k。
> - 额外空间：$O(k)$，来自堆本身。返回链表复用原节点，不额外计入；哨兵节点是 $O(1)$。

---

## 一句话总结

堆是**只维持「父 ≤ 子」这一弱不变量、从而用 $O(\log k)$ 换取单方向 $O(1)$ 查极值**的结构；看到「反复从 k 个动态变化的候选中取最小/最大」就用它，Python 记住 `heapify` + `heappop` + 条件 `heappush` 三件套，先解决元素**可比较**的问题，并确认自己要的极值方向和堆的方向一致 —— 反方向不免费。

---

## 模板归纳

看到以下信号时，优先想到堆：

- 「**第 K 大 / 最小的 K 个**」—— 维护大小为 K 的堆，$O(n\log K)$ 优于排序
- 「**合并 K 个有序序列**」—— 本题形状，堆里只放各序列的当前头
- 「**数据流中的中位数 / 极值**」—— 输入无法一次拿全，排序和分治都失效；中位数需**双堆**
- 「**每次都要取当前最优，取完后集合会更新**」—— Dijkstra、Prim、任务调度
- 反之，出现「**最近一个**」「**匹配**」「**回退**」「**单调**」→ 该用栈，不是堆
- 若同时需要**两个方向**的极值或任意排名 → 堆不够用，换 `SortedList` / `multiset` / 双堆

```python
from heapq import heapify, heappush, heappop

def solve(candidates):
    """k 路归并通用骨架：堆中恒为「每路的当前候选」"""
    h = [(first_key(c), i, c) for i, c in enumerate(candidates) if c]
    heapify(h)                       # O(k)
    result = []
    while h:
        key, i, item = heappop(h)    # 全局最小；要最大就把 first_key 取负
        result.append(item)
        nxt = advance(item)          # 该路前进一格
        if nxt:
            heappush(h, (first_key(nxt), i, nxt))
    return result
```

四个必查项：① 元素是否可比较（`__lt__` 或 tuple + tiebreaker）；② 补入新候选前是否判空；③ 堆大小是否被控制在 k 而不是 n；④ **方向是否搞反**（Python 默认小根、C++ 默认大根）。

---

相关笔记：[[25. K 个一组翻转链表]]、[[20. 有效的括号]]（栈的对照）、[[295. 数据流的中位数]]（双堆）

算法标签：`heap` `priority-queue` `k-way-merge` `linked-list` `divide-and-conquer`