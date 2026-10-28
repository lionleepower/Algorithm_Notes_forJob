# Python dict：字典语法与使用实例

Python 的 `dict` 用 `key → value` 建立映射，适合快速查找、计数、记录位置和分组。算法题出现“是否出现过”“出现几次”“值对应哪个位置”时，优先考虑字典。

---

## 思路

如果每次查找都遍历列表，单次查询需要 $O(n)$；`dict` 基于哈希表实现，查找、插入和删除平均可以做到 $O(1)$，本质是用额外空间换取更快查询。

> [!tip]- 核心思路
>
> 字典保存的是映射关系：
>
> ```text
> key → value
> ```
>
> 常见用途：
>
> - 查重：元素是否已经出现。
> - 计数：每个元素出现几次。
> - 定位：某个值对应哪个下标。
> - 分组：同一类元素放到同一个列表。
> - 缓存：输入对应已经计算出的结果。

---

## 1. 创建字典

> [!success]- 常见创建方式
>
> ```python
> empty1 = {}
> empty2 = dict()
>
> scores = {"Alice": 90, "Bob": 85}
> coordinates = dict(x=10, y=20)
> pairs = dict([("a", 1), ("b", 2)])
>
> keys = ["a", "b", "c"]
> initialized = dict.fromkeys(keys, 0)
> ```

字典的键不能重复。重复赋值会覆盖旧值：

```python
d = {"a": 1}
d["a"] = 2
print(d)  # {'a': 2}
```

---

## 2. 读取与判断

| 写法 | 作用 | 键不存在时 |
| --- | --- | --- |
| `d[key]` | 读取值 | 抛出 `KeyError` |
| `d.get(key)` | 安全读取 | 返回 `None` |
| `d.get(key, default)` | 带默认值读取 | 返回 `default` |
| `key in d` | 判断键是否存在 | 返回 `False` |

> [!example]- 安全访问
>
> ```python
> scores = {"Alice": 90}
>
> print(scores["Alice"])          # 90
> print(scores.get("Bob"))        # None
> print(scores.get("Bob", 0))     # 0
> print("Alice" in scores)         # True
> ```

`in` 默认检查键，不检查值。检查值需要写 `value in d.values()`，但这通常需要线性扫描。

---

## 3. 添加、更新与删除

> [!success]- 常用修改操作
>
> ```python
> d = {"a": 1, "b": 2}
>
> d["c"] = 3                 # 添加
> d["a"] = 10                # 更新
> d.update({"b": 20, "d": 4})
>
> value = d.pop("c")         # 删除并返回值
> missing = d.pop("x", None) # 不存在时返回默认值
> last_pair = d.popitem()     # 删除并返回最后加入的键值对
>
> del d["a"]                 # 键不存在会抛出 KeyError
> d.clear()                   # 清空字典
> ```

只在键不存在时写入默认值，可以使用：

```python
d.setdefault("items", []).append(1)
```

如果需要频繁分组，`defaultdict` 通常更清晰。

---

## 4. 遍历字典

> [!success]- 三种遍历方式
>
> ```python
> scores = {"Alice": 90, "Bob": 85}
>
> for name in scores:
>     print(name)
>
> for score in scores.values():
>     print(score)
>
> for name, score in scores.items():
>     print(name, score)
> ```

| 方法 | 得到的内容 |
| --- | --- |
| `d.keys()` | 所有键的动态视图 |
| `d.values()` | 所有值的动态视图 |
| `d.items()` | 所有 `(key, value)` 的动态视图 |

不要在遍历字典时直接改变它的大小。需要删除元素时，可以先复制键：

```python
for key in list(d):
    if should_remove(key):
        del d[key]
```

---

## 5. 键必须可哈希

字典需要通过键的哈希值定位位置，因此键必须是可哈希对象：生命周期内哈希值保持不变，并且能参与相等比较。

| 可以作为键 | 通常不能作为键 |
| --- | --- |
| `int`、`str`、`bytes` | `list` |
| 只含可哈希元素的 `tuple` | `dict` |
| `frozenset` | `set` |

> [!warning]- 元组不一定可哈希
>
> ```python
> valid = {(1, 2): "point"}
> invalid = {([1, 2], 3): "value"}  # TypeError
> ```
>
> 元组内部如果包含列表等不可哈希对象，整个元组也不能作为键。

---

## 6. 实例一：元素计数

> [!success]- 使用 `get`
>
> ```python
> def count_items(nums):
>     counts = {}
>
>     for value in nums:
>         counts[value] = counts.get(value, 0) + 1
>
>     return counts
>
>
> print(count_items([1, 2, 1, 3, 2, 1]))
> # {1: 3, 2: 2, 3: 1}
> ```

标准库也提供 `Counter`：

```python
from collections import Counter

counts = Counter([1, 2, 1, 3, 2, 1])
print(counts[1])  # 3
```

手写 `get` 模板更能体现哈希计数思路，`Counter` 更适合工程代码或允许使用标准库的场景。

---

## 7. Counter 的比较运算：多重集包含

`dict` 本身**不支持**大小比较，`Counter` 却可以。这不是「按长度比」，而是**多重集 multiset 的包含关系**——滑动窗口判断「窗口是否已经覆盖目标串」正是靠它。

> [!tip]- 核心语义：逐 key 比计数，缺失的 key 当 0
>
> `cnt_s >= cnt_t` 为真的条件是：**两边出现过的每一个 key**，`cnt_s` 里的计数都不小于 `cnt_t` 里的；某一边没有的 key 一律按 0 处理。
>
> 也就是「`cnt_s` 这个多重集**包含**了 `cnt_t`」。`cnt_s` 里多出来的 key 完全不影响判断。
>
> ```python
> from collections import Counter
>
> Counter("ADOBEC") >= Counter("ABC")      # True：窗口已覆盖目标
> ```

> [!example]- 六个例子：它比的不是长度
>
> | `cnt_s` | `cnt_t` | `cnt_s >= cnt_t` | 为什么 |
> | --- | --- | --- | --- |
> | `Counter("AABC")` | `Counter("ABC")` | `True` | A:2≥1、B:1≥1、C:1≥1；多出来的那个 A 无所谓 |
> | `Counter("ABCDEFG")` | `Counter("ABC")` | `True` | 多出的 D~G 不参与比较，长度差再大也没关系 |
> | `Counter("AB")` | `Counter("ABC")` | `False` | C 在 `cnt_s` 里缺失 $\to$ 视为 0，而 0 < 1 |
> | `Counter("ABB")` | `Counter("ABB")` | `True` | 每个 key 都相等，$\ge$ 成立 |
> | `Counter("AAA")` | `Counter("AB")` | `False` | A:3≥1 通过，但 B:0 < 1 |
> | `Counter("ADOBEC")` | `Counter("ABC")` | `True` | 正是滑窗里「窗口已覆盖 `t`」的那一刻 |
>
> **重点看第 2 行和第 5 行**：若真按长度比，`len("ABCDEFG") > len("ABC")` 和 `len("AAA") > len("AB")` 都成立，可实际结果一个 `True` 一个 `False`。所以它显然不是在比长度，而是在逐 key 比计数。

> [!tip]- 官方实现：它扫的是**两边**的 key
>
> CPython 里 `Counter.__ge__` 只有一行：
>
> ```python
> def __ge__(self, other):
>     if not isinstance(other, Counter):
>         return NotImplemented
>     return all(self[e] >= other[e] for c in (self, other) for e in c)
> ```
>
> 注意 `for c in (self, other)`——**两个字典的 key 都要遍历一遍**。常写的那个简化版
>
> ```python
> all(cnt_s[k] >= v for k, v in cnt_t.items())     # 只扫 cnt_t，不完全等价
> ```
>
> 在计数**非负**时结果一致，但一旦 `cnt_s` 出现负计数就会错：`cnt_s` 为 `{'a': -1}`、`cnt_t` 为空时，真实结果是 `False`（因为 $-1 < 0$），简化版却因为没什么可扫而返回 `True`。滑窗代码里窗口计数天然非负，所以能用简化版理解语义，但别把它当成定义。
>
> **复杂度**：单次比较是 $O(\text{两边 key 数})$，即 $O(\lvert\Sigma\rvert)$ 级别，**不是** $O(1)$。写在滑窗的循环里，整体就从 $O(m)$ 退化成 $O(m \cdot \lvert\Sigma\rvert)$——[[1.3 滑动窗口 定长窗口与最小覆盖子串]] 里 76 的两种写法实测差了 45 倍，根因就在这里。

> [!warning]- 三个容易踩的点
>
> **1. 普通 `dict` 根本不支持大小比较**
>
> ```python
> {'a': 1} >= {'a': 1}
> # TypeError: '>=' not supported between instances of 'dict' and 'dict'
> ```
>
> `Counter` 是特意实现了 `__lt__` / `__le__` / `__gt__` / `__ge__` 来表达多重集关系的。而且**这套比较是 Python 3.10 才加的**——3.9 及以前，`Counter` 之间用 `>=` 同样抛 `TypeError`。LeetCode 选 Python3 没问题，本地拿旧解释器验证会直接报错。
>
> **2. 这是偏序 partial order，不是全序**
>
> ```python
> a, b = Counter("A"), Counter("B")
> a >= b     # False
> a <= b     # False
> a == b     # False        ← 三个同时为假
> ```
>
> 两个多重集可以**互不包含**。所以 `not (a >= b)` **推不出** `a < b`，写 `if / else` 分支时尤其要小心：`else` 分支里并不意味着「`a` 比 `b` 小」，只意味着「`a` 没包含 `b`」。
>
> **3. 相等比较会忽略零值键，但这也是 3.10 起才有的**
>
> ```python
> Counter(a=1) == Counter(a=1, b=0)     # 3.10+：True    3.9 及以前：False
> ```
>
> 3.10 起 `Counter.__eq__` 被重写为「缺失计数按 0 处理」；此前它直接继承 `dict.__eq__`，零值键会让两表不等。这条在滑窗里很关键：`cnt_s[s[left]] -= 1` 会在表里留下计数为 0 的残余 key，新版本下它们不干扰比较，旧版本下必须 `del` 掉。

> [!warning]- 顺带：`Counter` 读缺键不插入，`defaultdict` 会插入
>
> 两者读缺键都得到 0，但副作用不同：
>
> ```python
> from collections import Counter, defaultdict
>
> c = Counter();        c['zzz'];  print(dict(c))    # {}              没插入
> d = defaultdict(int); d['zzz'];  print(dict(d))    # {'zzz': 0}      插入了
> ```
>
> 所以在 `defaultdict` 上取 `len(d)` 当「种类数」时，**必须在循环开始前就取好快照**——循环里读过的每个新 key 都会让 `len(d)` 变大。这正是 [[1.3 滑动窗口 定长窗口与最小覆盖子串]] 里 76 那句 `kinds = len(diff)` 不能挪位置的原因。
>
> 反过来，`defaultdict` 的默认工厂在 C 层，`Counter.__missing__` 是 Python 层的方法，所以缺键读写 `defaultdict` 更快——同一份滑窗逻辑实测 0.025 s 对 0.066 s。

---

## 8. 实例二：分组

> [!success]- 使用 `defaultdict(list)`
>
> ```python
> from collections import defaultdict
>
> def group_positions(nums):
>     positions = defaultdict(list)
>
>     for index, value in enumerate(nums):
>         positions[value].append(index)
>
>     return dict(positions)
>
>
> print(group_positions([1, 2, 1, 3, 2]))
> # {1: [0, 2], 2: [1, 4], 3: [3]}
> ```

访问不存在的键时，`defaultdict(list)` 会自动创建空列表，省去手动初始化。

---

## 9. 实例三：Two Sum

遍历当前数字 `value` 时，只需判断补数 `target - value` 是否已经出现。字典保存“数字 → 下标”。

> [!success]- 一次遍历
>
> ```python
> def two_sum(nums, target):
>     positions = {}
>
>     for index, value in enumerate(nums):
>         need = target - value
>
>         if need in positions:
>             return [positions[need], index]
>
>         positions[value] = index
>
>     return []
>
>
> print(two_sum([2, 7, 11, 15], 9))  # [0, 1]
> ```

> [!tip]- 为什么先查找再存当前下标
>
> 先判断 `need in positions`，可以保证补数来自之前的元素，避免在目标是当前值两倍时把同一个元素使用两次。

---

## 10. 字典推导式与合并

> [!success]- 常用写法
>
> ```python
> squares = {x: x * x for x in range(5)}
>
> left = {"a": 1, "b": 2}
> right = {"b": 20, "c": 3}
>
> merged1 = {**left, **right}
> merged2 = left | right  # Python 3.9+
> ```

键冲突时，后面的字典覆盖前面的值。上例中合并结果里的 `"b"` 是 `20`。

---

## 11. dict、set 与 list 怎么选

| 需求 | 推荐结构 |
| --- | --- |
| `key → value` 映射 | `dict` |
| 只判断元素是否存在或去重 | `set` |
| 按顺序保存并通过下标访问 | `list` |
| 统计次数 | `dict` 或 `Counter` |
| 每个键对应多个元素 | `defaultdict(list)` |
| 判断一个计数表是否覆盖另一个 | `Counter` 的 `>=`（见第 7 节） |

如果只需要记录“见过哪些元素”，使用 `set` 比保存无意义字典值更直接；需要附带次数、下标或其他信息时使用 `dict`。

---

## 12. 常见易错点

> [!warning]- 易错点
>
> - 用 `d[key]` 读取不存在的键，触发 `KeyError`。
> - 误以为 `value in d` 检查值；它实际检查键。
> - 使用 `list`、`dict` 或 `set` 作为键，触发 `TypeError`。
> - 计数时直接写 `counts[x] += 1`，却没有初始化。
> - 遍历字典时增加或删除键，触发运行时错误。
> - 用 `dict.fromkeys(keys, [])` 创建多个列表；所有键会共享同一个列表对象。
> - Two Sum 先存当前值再查补数，可能错误使用同一元素两次。
> - 把 `Counter` 的 `>=` 当成「比长度」；它是多重集包含，且 `a >= b` 与 `a <= b` 可以同时为假。
> - 在循环里用 `Counter` 的比较当判据，误以为是 $O(1)$；它是 $O(\lvert\Sigma\rvert)$，会把线性算法拖成一个数量级。
> - 在 `defaultdict` 上边遍历边取 `len(d)` 当种类数；读缺键就会插入新 key，必须提前取快照。

避免共享默认列表：

```python
safe = {key: [] for key in keys}
```

---

## 复杂度

> [!summary]- 平均复杂度
>
> - 查找、插入、更新、删除：平均 $O(1)$。
> - 遍历、复制字典：$O(n)$。
> - 额外空间：保存 $n$ 个键值对需要 $O(n)$。
>
> 哈希冲突严重时，单次操作最坏可能退化；算法分析通常使用平均复杂度 $O(1)$。

---

## 一句话总结

`dict` 用哈希表维护 `key → value` 映射，能把查重、计数、定位和分组中的频繁查找优化为平均 $O(1)$；它的子类 `Counter` 额外把「谁包含谁」做成了 $O(\lvert\Sigma\rvert)$ 的多重集比较。

---

## 模板归纳

```python
# 安全读取
value = d.get(key, default)

# 计数
counts[x] = counts.get(x, 0) + 1

# 记录位置
positions[x] = index

# 分组
from collections import defaultdict

groups = defaultdict(list)
groups[key].append(value)

# Two Sum
positions = {}
for index, value in enumerate(nums):
    need = target - value
    if need in positions:
        return [positions[need], index]
    positions[value] = index
```

看到“是否出现、出现几次、对应位置、建立映射、按键分组”，优先想到 `dict`。

---

## 关联

- 同类：[[Python_set]] · [[Python_deque]] · [[pythonList、Tuple、Dict容器创建与操作选择]]
- 用到本篇的题解：[[1.3 滑动窗口 定长窗口与最小覆盖子串]]（`Counter` 比较与 `defaultdict` 计数的实战取舍）· [[8.0 前缀和与哈希]] · [[8.1 哈希实战 分组、连续序列与原地哈希]]
