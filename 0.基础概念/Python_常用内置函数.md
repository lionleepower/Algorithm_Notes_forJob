# Python 常用内置函数：LeetCode 刷题速查

这篇只整理 **LeetCode 解题时高频、能够直接减少模板代码** 的 Python 工具，并按照“看到什么题型，就想到什么函数”组织。

严格来说，`sorted()`、`len()` 是内置函数，`list.sort()` 是对象方法，`bisect_left()`、`Counter` 等是标准库工具。刷题时三者经常组合使用，因此统一收录，但会明确标注类别。

---

## 思路

刷题不需要背完整的 Python API，只需要掌握高频工具的四件事：**输入是什么、返回什么、是否修改原对象、复杂度是多少**。

> [!tip]- 题型触发信号
>
> ```python
> # 排序 / 贪心
> ordered = sorted(nums)
> nums.sort()
>
> # 同时取得下标和值
> for i, x in enumerate(nums):
>     ...
>
> # 聚合 / 二分答案 check
> total = sum(values)
> upper = max(values)
>
> # 有序数组边界
> i = bisect_left(nums, target)
>
> # 哈希计数 / 分组
> counts = Counter(nums)
> groups = defaultdict(list)
> ```
>
> 先识别题型，再选择工具；不要为了代码短而隐藏关键算法逻辑。

---

## 1. 导入与分类

### 1.1 无需导入：真正的内置函数

```python
len(nums)
range(n)
enumerate(nums)
zip(a, b)
sorted(nums)
sum(nums)
min(nums)
max(nums)
abs(x)
any(conditions)
all(conditions)
ord(ch)
chr(code)
```

### 1.2 对象方法：由容器调用

```python
nums.sort()
nums.append(x)
nums.pop()

freq.get(x, 0)
freq.items()

seen.add(x)
seen.discard(x)
```

### 1.3 需要导入：LeetCode 高频标准库

```python
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict, deque
from functools import cache
from itertools import accumulate
from math import inf, gcd
from heapq import heappush, heappop, heapify
```

> [!warning]- 名称不要混淆
>
> - `sorted()` 是内置函数。
> - `.sort()` 是 `list` 的方法，不是内置函数。
> - `bisect_left()` 等来自标准库，也不是内置函数。
> - 它们都可以在 LeetCode 的 Python 代码中使用；需要导入的工具不能漏写 `import`。

---

## 2. LeetCode 高频工具总表

| 题目中的需求 | 优先想到 | 关键提醒 |
| --- | --- | --- |
| 获取数组、字符串长度 | `len(x)` | 常见内置容器为 $O(1)$ |
| 按下标遍历 | `range(len(nums))` | `range` 左闭右开 |
| 同时得到下标和元素 | `enumerate(nums)` | 比手写下标更直接 |
| 多个数组对应位置一起遍历 | `zip(a, b)` | 在最短输入结束时停止 |
| 保留原数组并排序 | `sorted(nums)` | 返回新列表 |
| 允许修改原列表并排序 | `nums.sort()` | 返回 `None` |
| 求和、计数满足条件的元素 | `sum(...)` | 可以直接接生成器 |
| 求最值或选出最优元素 | `min()`、`max()` | 支持 `key=` |
| 判断是否至少一个满足 | `any(...)` | 短路求值 |
| 判断是否全部满足 | `all(...)` | 空输入返回 `True` |
| 求距离或差的大小 | `abs(x)` | 常见于坐标、二分验证 |
| 去重或快速判存在 | `set(...)` | 平均查询 $O(1)$ |
| 把计数数组作为哈希键 | `tuple(counts)` | `list` 不可哈希 |
| 字母映射到 `0..25` | `ord(ch) - ord('a')` | 仅适用于小写英文字母 |
| 有序数组找左右边界 | `bisect_left/right` | 输入必须有序 |
| 频率统计 | `Counter(nums)` | 哈希计数 |
| 自动创建分组容器 | `defaultdict(list)` | 适合异位词分组、邻接表 |
| BFS / 双端队列 | `deque()` | 两端操作 $O(1)$ |
| Top K / 动态最值 | `heapq` | Python 默认小根堆 |
| 记忆化搜索 | `@cache` | 参数必须可哈希 |
| 前缀和 | `accumulate(nums, initial=0)` | `initial=0` 便于区间和 |

---

## 3. 排序：`list.sort()` 与 `sorted()`

排序常见于贪心、双指针、区间合并、二分预处理、字母异位词和自定义规则排序。

### 3.1 原理一：是否修改原对象

`list.sort()` 原地修改列表，并返回 `None`：

> [!example]- `.sort()` 的真实行为
>
> ```python
> nums = [3, 1, 2]
> result = nums.sort()
>
> print(nums)    # [1, 2, 3]：原列表被修改
> print(result)  # None
> ```

所以不能写：

```python
nums = nums.sort()  # 错误：nums 变成 None
```

`sorted()` 读取可迭代对象，并返回一个新的列表：

> [!example]- `sorted()` 的真实行为
>
> ```python
> nums = [3, 1, 2]
> ordered = sorted(nums)
>
> print(nums)     # [3, 1, 2]：原列表不变
> print(ordered)  # [1, 2, 3]
>
> print(sorted("tea"))
> # ['a', 'e', 't']：无论输入是什么可迭代对象，返回值都是 list
> ```

| 需求 | 写法 |
| --- | --- |
| 后续还要使用原顺序 | `ordered = sorted(nums)` |
| 允许改变原列表 | `nums.sort()` |
| 输入是字符串、集合、元组等 | `ordered = sorted(data)` |

### 3.2 原理二：`key` 决定比较依据

`key` 函数会为每个元素计算一个“排序标签”。Python 按标签比较，但结果中保留的仍是原元素。

```python
intervals = [[1, 4], [2, 3], [1, 2]]

ordered = sorted(intervals, key=lambda interval: interval[1])
print(ordered)
# [[1, 2], [2, 3], [1, 4]]
```

可以把原理理解成：

```text
[1, 4] -> key 是 4
[2, 3] -> key 是 3
[1, 2] -> key 是 2

按 2、3、4 排序，但移动的是完整区间。
```

按字典的 value 排序：

```python
freq = {"a": 3, "b": 1, "c": 2}
items = sorted(freq.items(), key=lambda item: item[1], reverse=True)

print(items)
# [('a', 3), ('c', 2), ('b', 1)]
```

多个条件使用元组：

```python
records = [("Bob", 90), ("Alice", 90), ("Carol", 85)]

# 分数降序；同分时姓名升序
records.sort(key=lambda item: (-item[1], item[0]))
```

### 3.3 字母异位词中的排序签名

```python
s = "tea"
characters = sorted(s)           # ['a', 'e', 't']
signature = "".join(characters)  # "aet"
```

`"eat"`、`"tea"`、`"ate"` 排序后都是 `"aet"`，因此可以作为同一组的哈希键。

> [!summary]- 排序复杂度
>
> - `sorted()` 和 `list.sort()`：时间复杂度 $O(n\log n)$。
> - `sorted()` 会创建结果列表，额外需要 $O(n)$ 级别的结果空间。
> - Python 排序是稳定的：`key` 相同时保持原相对顺序。

---

## 4. 遍历：`len()`、`range()`、`enumerate()`、`zip()`、`reversed()`

### 4.1 什么时候用下标，什么时候直接取值

只需要元素：

```python
for x in nums:
    ...
```

需要下标和元素：

```python
for i, x in enumerate(nums):
    ...
```

需要访问 `i - 1`、`i + 1` 或修改指定位置：

```python
for i in range(len(nums)):
    ...
```

`range` 是左闭右开：

```python
list(range(2, 6))      # [2, 3, 4, 5]
list(range(5, 0, -1)) # [5, 4, 3, 2, 1]
```

### 4.2 `zip()`：对应位置一起处理

```python
for have, need, price in zip(stock, composition, cost):
    required = need * amount
    money += max(0, required - have) * price
```

常见于：

- 同时遍历两个字符串或数组。
- 比较相邻元素：`zip(nums, nums[1:])`。
- 二分答案的可行性检查中对齐多组数据。

```python
nums = [1, 3, 6, 10]

for left, right in zip(nums, nums[1:]):
    print(right - left)
# 2, 3, 4
```

> [!warning]- `zip()` 的长度
>
> `zip()` 在最短的输入结束时停止。如果输入长度本应相同，题目逻辑中要保证这一点。

### 4.3 `reversed()`：反向遍历而不手写下标

```python
for x in reversed(nums):
    ...
```

如果需要下标：

```python
for i in range(len(nums) - 1, -1, -1):
    ...
```

---

## 5. 聚合与判断：`sum()`、`min()`、`max()`、`any()`、`all()`、`abs()`

### 5.1 `sum()`：求和或计数

```python
total = sum(nums)
```

二分答案中计算总耗时：

```python
hours = sum((pile + speed - 1) // speed for pile in piles)
```

统计满足条件的元素个数：布尔值在 Python 中可以当作 `0/1`。

```python
even_count = sum(x % 2 == 0 for x in nums)
```

它等价于：

```python
even_count = 0
for x in nums:
    if x % 2 == 0:
        even_count += 1
```

### 5.2 `min()` / `max()`：求值或选择元素

```python
smallest = min(nums)
largest = max(nums)
```

二分答案中常用最大值作为可行上界：

```python
left, right = 0, max(piles)
```

支持 `key`，返回的是原元素：

```python
words = ["pear", "watermelon", "fig"]
longest = max(words, key=len)

print(longest)  # "watermelon"
```

钳制数值到区间 `[low, high]`：

```python
x = max(low, min(x, high))
```

### 5.3 `any()` / `all()`：存在性与全称判断

```python
has_negative = any(x < 0 for x in nums)
all_positive = all(x > 0 for x in nums)
```

二者都会短路：

- `any()` 遇到第一个真值就停止并返回 `True`。
- `all()` 遇到第一个假值就停止并返回 `False`。

空输入：

```python
any([])  # False
all([])  # True
```

### 5.4 `abs()`：距离与误差

```python
distance = abs(a - b)
manhattan = abs(x1 - x2) + abs(y1 - y2)
```

---

## 6. 哈希题常用转换：`set()`、`tuple()`、`ord()`、`chr()`

### 6.1 `set()`：去重和判存在

```python
seen = set(nums)

if target in seen:
    ...
```

```python
unique_count = len(set(nums))
```

哈希集合查询、插入、删除平均为 $O(1)$；从 `n` 个元素构造集合需要 $O(n)$。

### 6.2 `tuple()`：把不可哈希列表变成稳定签名

字典键必须可哈希。计数数组是列表，不能直接作为键：

```python
counts = [0] * 26
for ch in word:
    counts[ord(ch) - ord('a')] += 1

signature = tuple(counts)
groups[signature].append(word)
```

### 6.3 `ord()` / `chr()`：字符与整数映射

```python
ord('a')  # 97
ord('c')  # 99
chr(99)   # 'c'
```

小写字母映射到 `0..25`：

```python
index = ord(ch) - ord('a')
```

其原理是小写英文字母的 Unicode 码点连续：

```text
'a' -> 97 -> 97 - 97 = 0
'b' -> 98 -> 98 - 97 = 1
'c' -> 99 -> 99 - 97 = 2
...
'z' -> 122 -> 122 - 97 = 25
```

---

## 7. 二分查找：`bisect_left()` 与 `bisect_right()`

`bisect` 是标准库，不是真正的内置函数，但在 LeetCode 二分题中非常高频。

```python
from bisect import bisect_left, bisect_right

nums = [1, 2, 2, 2, 5]

left = bisect_left(nums, 2)    # 1：第一个 >= 2
right = bisect_right(nums, 2)  # 4：第一个 > 2
```

| 查询目标 | 写法 |
| --- | --- |
| 第一个 `>= target` | `bisect_left(nums, target)` |
| 第一个 `> target` | `bisect_right(nums, target)` |
| 最后一个 `< target` | `bisect_left(nums, target) - 1` |
| 最后一个 `<= target` | `bisect_right(nums, target) - 1` |
| `target` 的出现次数 | `bisect_right(nums, target) - bisect_left(nums, target)` |

### 7.1 `bisect_left()` 的手写原理

```python
def lower_bound(nums, target):
    """返回第一个 >= target 的下标；不存在则返回 len(nums)。"""
    left, right = -1, len(nums)

    while left + 1 < right:
        mid = (left + right) // 2

        if nums[mid] < target:
            left = mid
        else:
            right = mid

    return right
```

关键不变量：

```text
left 一侧始终 < target
right 一侧始终 >= target
```

### 7.2 LeetCode 34：查找左右边界

```python
from bisect import bisect_left, bisect_right


class Solution:
    def searchRange(self, nums: list[int], target: int) -> list[int]:
        start = bisect_left(nums, target)

        if start == len(nums) or nums[start] != target:
            return [-1, -1]

        end = bisect_right(nums, target) - 1
        return [start, end]
```

> [!warning]- 二分库函数易错点
>
> - `nums` 必须已经升序排列。
> - 返回值可能是 `len(nums)`，访问前必须检查越界。
> - `bisect_left()` 找的是插入位置，不保证目标实际存在。
> - 查询位置为 $O(\log n)$，但向列表中间插入仍然是 $O(n)$。

---

## 8. 高频标准库：计数、队列、堆、记忆化与前缀和

这些不属于内置函数，但它们是 LeetCode Python 解法中最值得掌握的一组工具。

### 8.1 `Counter`：频率统计

```python
from collections import Counter

freq = Counter([1, 2, 1, 3, 1])

print(freq[1])                 # 3
print(freq.most_common(2))     # [(1, 3), (2, 1)]
```

适合：字符频率、元素计数、Top K 的预处理。

### 8.2 `defaultdict`：分组与邻接表

```python
from collections import defaultdict

groups = defaultdict(list)
groups["aet"].append("eat")
groups["aet"].append("tea")
```

计数：

```python
freq = defaultdict(int)
freq[x] += 1
```

适合：字母异位词分组、图的邻接表、按键收集元素。

### 8.3 `deque`：BFS 与双端队列

```python
from collections import deque

queue = deque([start])

while queue:
    node = queue.popleft()
    for next_node in graph[node]:
        queue.append(next_node)
```

`popleft()` 是 $O(1)$；列表的 `pop(0)` 是 $O(n)$，BFS 不要用 `pop(0)`。

### 8.4 `heapq`：Top K 与动态最值

```python
from heapq import heapify, heappop, heappush

heap = [3, 1, 4]
heapify(heap)

heappush(heap, 2)
smallest = heappop(heap)  # 1
```

Python 默认是小根堆；需要最大值时常存负数：

```python
heappush(heap, -value)
largest = -heappop(heap)
```

大小固定为 `k` 的堆通常把 Top K 优化到 $O(n\log k)$。

### 8.5 `@cache`：记忆化搜索

```python
from functools import cache


@cache
def dfs(i, state):
    if i < 0:
        return 0
    return max(dfs(i - 1, state), dfs(i - 2, state) + nums[i])
```

函数参数构成缓存键，因此参数必须可哈希；不要直接传入 `list`。

### 8.6 `accumulate`：前缀和

```python
from itertools import accumulate

nums = [2, 4, 1, 3]
prefix = list(accumulate(nums, initial=0))

print(prefix)  # [0, 2, 6, 7, 10]
```

区间 `[left, right]` 的和：

```python
range_sum = prefix[right + 1] - prefix[left]
```

### 8.7 `inf` 与 `gcd`

```python
from math import gcd, inf

best = inf
worst = -inf
common_divisor = gcd(a, b)
```

`inf` 常用于最短路、DP 最小值初始化；`gcd` 常用于数论和分数化简。

---

## 9. 按题型选择工具

| LeetCode 题型 | 常用工具 | 典型写法 |
| --- | --- | --- |
| 数组遍历 | `len`、`range`、`enumerate` | `for i, x in enumerate(nums)` |
| 双数组比较 | `zip` | `for x, y in zip(a, b)` |
| 排序 / 贪心 / 区间 | `sorted`、`.sort`、`key` | `intervals.sort(key=lambda x: x[1])` |
| 哈希计数 | `dict.get`、`Counter` | `freq[x] = freq.get(x, 0) + 1` |
| 哈希分组 | `defaultdict(list)`、`tuple` | `groups[key].append(value)` |
| 判存在 / 去重 | `set` | `if x in seen` |
| 二分查找 | `bisect_left/right` | `i = bisect_left(nums, target)` |
| 二分答案 | `sum`、`min`、`max`、`zip` | `sum(cost(x) for x in nums)` |
| BFS / 层序遍历 | `deque` | `node = queue.popleft()` |
| Top K / 动态最值 | `heapq` | `heappush(heap, value)` |
| DP / 记忆化搜索 | `@cache`、`inf` | `@cache def dfs(state): ...` |
| 前缀和 | `accumulate` | `list(accumulate(nums, initial=0))` |
| 字符计数 | `ord`、`tuple` | `counts[ord(ch)-ord('a')] += 1` |

---

## 10. 常见易错点

> [!warning]- 易错点
>
> - `nums = nums.sort()`：`.sort()` 返回 `None`。
> - `sorted("tea")` 返回字符列表，不是字符串；需要 `"".join(sorted(s))`。
> - `key=` 只决定比较依据，结果仍是原元素。
> - `zip()` 遇到最短输入结束，长度不同可能静默丢数据。
> - `min([])`、`max([])` 会抛出 `ValueError`；必要时提前判断或使用 `default=`。
> - `all([])` 是 `True`，`any([])` 是 `False`。
> - `list` 不能作为字典键，需要根据语义转成 `tuple`。
> - `ord(ch) - ord('a')` 只适合小写英文字母。
> - `bisect` 的输入必须有序，并且返回的是插入位置。
> - BFS 使用 `deque.popleft()`，不要使用列表 `pop(0)`。
> - `heapq` 默认小根堆；模拟大根堆通常存负数。
> - `@cache` 的参数必须可哈希，缓存也会占用额外空间。

---

## 复杂度

> [!summary]- 高频工具复杂度
>
> - `len()`：对常见内置容器为 $O(1)$。
> - `sorted()` / `.sort()`：$O(n\log n)$。
> - `sum()` / `min()` / `max()` / 完整遍历：$O(n)$。
> - `dict` / `set` 查询、插入、删除：平均 $O(1)$。
> - `bisect_left()` / `bisect_right()`：$O(\log n)$。
> - `deque.append()` / `popleft()`：$O(1)$。
> - `heappush()` / `heappop()`：$O(\log n)$；`heapify()`：$O(n)$。
> - `Counter(nums)`、`list(accumulate(nums))`：$O(n)$。
> - `@cache`：时间取决于不同状态数，空间也与缓存状态数同阶。

---

## 一句话总结

LeetCode 刷题先记住这一条工具链：**遍历用 `enumerate/zip`，排序用 `sorted/.sort + key`，聚合用 `sum/min/max/any/all`，哈希用 `set/tuple/Counter/defaultdict`，二分用 `bisect`，BFS 用 `deque`，Top K 用 `heapq`，记忆化用 `@cache`。**

---

## 模板归纳

```python
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict, deque
from functools import cache
from heapq import heappop, heappush
from itertools import accumulate
from math import inf

# 排序：按第二项升序
ordered = sorted(data, key=lambda item: item[1])

# 遍历
for i, x in enumerate(nums):
    ...

for x, y in zip(a, b):
    ...

# 哈希计数 / 分组
freq = Counter(nums)
groups = defaultdict(list)

# 二分边界
first_ge = bisect_left(nums, target)
first_gt = bisect_right(nums, target)

# BFS
queue = deque([start])

# 前缀和
prefix = list(accumulate(nums, initial=0))
```

相关：[[Python_range]] · [[python_any()]] · [[Python_字符串常用操作]] · [[Python_dict]] · [[Python_set]] · [[Python_deque]] · [[Python_cache]] · [[c++python 堆与栈]] · [[3.0 二分查找 红蓝染色法]] · [[3.1 二分答案]] · [[8.1 哈希实战 分组、连续序列与原地哈希]] · [[10.0 堆 TopK与对顶堆]]
