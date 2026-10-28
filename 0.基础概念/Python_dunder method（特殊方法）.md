
# Python 特殊方法：让自定义类接入语言内建语法

特殊方法 (special method)，俗称 **dunder method**（double underscore，双下划线），是 Python 定义好的一组方法名。你实现了它，你的类就能被 `<`、`len()`、`for`、`in`、`[]`、`with` 等**内建语法**直接操作。

算法题里最常见的触发点：`heapq` 只认 `<`，`sorted` 只认 `<`，`set` / `dict` 只认 `__hash__` + `__eq__`。元素不满足这些协议，库函数就直接抛 `TypeError`。

---

## 思路

### 不用它会有什么问题

回到 [[23. 合并 K 个升序链表]]：把 `ListNode` 塞进堆里会炸。

```python
h = [head for head in lists if head]
heapify(h)
# TypeError: '<' not supported between instances of 'ListNode' and 'ListNode'
```

`heapq` 内部上浮下沉时只做一件事：问「这个是不是比那个小」。而 `ListNode` 只定义了 `__init__`，没有 `__lt__` —— Python 不知道两个节点谁大谁小，只能报错。

关键在于：**你没法给 `heapq` 传 `key=`**。它没有这个参数。所以「换个比较标准」的需求，只能落到被比较的**对象本身**上。

### 核心机制：运算符是语法糖

Python 里几乎所有内建语法都是**方法调用的语法糖 (syntactic sugar)**：

|你写的|Python 实际执行|
|---|---|
|`a < b`|`type(a).__lt__(a, b)`|
|`len(x)`|`type(x).__len__(x)`|
|`x[0]`|`type(x).__getitem__(x, 0)`|
|`for i in x`|`type(x).__iter__(x)` 拿迭代器，反复 `__next__`|
|`a in x`|`type(x).__contains__(x, a)`|
|`if x:`|`type(x).__bool__(x)`，无则回退 `__len__`|
|`str(x)`|`type(x).__str__(x)`|
|`x + y`|`type(x).__add__(x, y)`|

所以「让类支持某个语法」等价于「给类挂上对应的 dunder method」。这套机制叫**协议 (protocol)** 或**鸭子类型 (duck typing)**：Python 不检查你继承了什么，只检查你有没有那个方法。

> [!tip]- 核心思路
> 
> 内建语法 → 查**类型**上的 dunder method → 调用。想让对象接入某个语法，实现对应方法即可。
> 
> ```python
> class Node:
>     def __init__(self, val):
>         self.val = val
>     def __lt__(self, other):        # 支持 <，从而支持 heapq / sorted / min / max
>         return self.val < other.val
>     def __repr__(self):             # 支持 print / 调试显示
>         return f"Node({self.val})"
> ```
> 
> 判断依据：报错信息里出现「`'<' not supported between`」「`object is not iterable`」「`unhashable type`」，就是缺了对应的 dunder。

---

## 1. 导入与创建

不需要任何导入 —— dunder method 是语言级机制。定义方式有三种：

> [!success]- 三种定义方式
> 
> ```python
> # 方式一：写在类定义里（类归你所有时的正规做法）
> class Node:
>     def __init__(self, val):
>         self.val = val
>     def __lt__(self, other):
>         return self.val < other.val
> 
> # 方式二：猴子补丁 monkey patching（类不归你，如 LeetCode 的 ListNode）
> ListNode.__lt__ = lambda a, b: a.val < b.val
> 
> # 方式三：装饰器自动生成
> from dataclasses import dataclass
> @dataclass(order=True)              # 自动生成 __eq__ __lt__ __le__ __gt__ __ge__
> class Point:
>     x: int
>     y: int
> ```

方式二里 `a` 就是 `self` —— 存放在类上的函数被实例调用时，实例自动作为第一个参数传入，参数叫什么名字无所谓。

```python
node1 < node2
# ↓
ListNode.__lt__(node1, node2)     # a = node1, b = node2
```

---

## 2. 核心操作

按用途分类，只列算法题和日常最常用的：

### 构造与表示

|方法|触发方式|说明|
|---|---|---|
|`__init__(self, ...)`|`Cls(...)`|初始化实例（不是构造，构造是 `__new__`）|
|`__repr__(self)`|`repr(x)`、REPL 回显、容器内显示|面向**开发者**，应尽量无歧义|
|`__str__(self)`|`str(x)`、`print(x)`、f-string|面向**用户**，缺失时回退到 `__repr__`|

### 比较（算法题最高频）

| 方法         | 运算符                               |
| ---------- | --------------------------------- |
| `__lt__`   | `a < b`                           |
| `__le__`   | `a <= b`                          |
| `__gt__`   | `a > b`                           |
| `__ge__`   | `a >= b`                          |
| `__eq__`   | `a == b`                          |
| `__ne__`   | `a != b`，默认取 `__eq__` 的反          |
| `__hash__` | `hash(x)`，进 `set` / 作 `dict` 键的前提 |

### 容器协议

|方法|触发方式|说明|
|---|---|---|
|`__len__(self)`|`len(x)`、`if x:`|返回非负 int|
|`__getitem__(self, k)`|`x[k]`|支持切片时 `k` 可能是 `slice`|
|`__setitem__(self, k, v)`|`x[k] = v`|mutation|
|`__delitem__(self, k)`|`del x[k]`||
|`__contains__(self, v)`|`v in x`|缺失时回退为遍历，$O(n)$|
|`__iter__(self)`|`for i in x`、`list(x)`、解包|返回迭代器|
|`__next__(self)`|`next(it)`|迭代器自身实现，耗尽时抛 `StopIteration`|

### 其他常用

|方法|触发方式|说明|
|---|---|---|
|`__bool__(self)`|`if x:`、`while x:`|缺失时回退 `__len__`，再缺失恒为真|
|`__call__(self, ...)`|`x(...)`|让实例像函数一样被调用|
|`__enter__` / `__exit__`|`with x:`|上下文管理器|
|`__add__` / `__sub__` / `__mul__`|`+` / `-` / `*`|数值或序列运算|
|`__getattr__(self, name)`|属性**查不到时**兜底|注意不是每次属性访问都触发|

> [!example]- 最小示例
> 
> ```python
> class Bag:
>     def __init__(self, items):
>         self.items = list(items)
>     def __len__(self):
>         return len(self.items)
>     def __getitem__(self, i):
>         return self.items[i]
>     def __repr__(self):
>         return f"Bag({self.items})"
> 
> b = Bag([3, 1, 2])
> print(len(b))          # 3       ← __len__
> print(b[0])            # 3       ← __getitem__
> print(list(b))         # [3,1,2] ← __getitem__ 的迭代 fallback
> print(2 in b)          # True    ← 同样走 fallback
> print(b)               # Bag([3, 1, 2])  ← __repr__
> if b: print("非空")     # 非空    ← __bool__ 缺失，回退 __len__
> ```
> 
> 只实现了三个方法，却同时支持了 `len` / 下标 / 迭代 / `in` / 真值判断 / 打印 —— 这就是协议的威力。

---

## 3. 关键行为与边界

### 3.1 隐式查找：dunder 只在**类型**上找

这是最容易踩的一条：特殊方法的查找**绕过实例属性**，也绕过 `__getattr__`。

```python
class A:
    pass

a = A()
a.__len__ = lambda: 5      # 挂在实例上
len(a)                     # TypeError: object of type 'A' has no len()
print(a.__len__())         # 5  ← 显式调用可以，但 len() 不认

A.__len__ = lambda self: 5 # 挂在类上
len(a)                     # 5  ✅
```

> [!tip]- 为什么这样设计
> 
> 为了性能。`len(x)` 每次都去查实例字典会很慢，Python 直接在 `type(x)` 的 slot 上取函数指针。副作用就是：**猴子补丁必须打在类上**，`ListNode.__lt__ = ...` 而不是 `some_node.__lt__ = ...`。

### 3.2 `NotImplemented` 与反射运算

当左操作数不知道怎么和右操作数比较时，应返回 `NotImplemented`（注意不是 `NotImplementedError`），Python 会自动尝试**反射操作 (reflected operation)**：

```python
a < b
# ① 试 type(a).__lt__(a, b)
# ② 若返回 NotImplemented，试 type(b).__gt__(b, a)
# ③ 都不行 → TypeError
```

所以只实现 `__lt__` 也能让 `a > b` 工作（Python 会转成 `b < a`）—— 但只在两边类型不同或返回 `NotImplemented` 时才走这条路。稳妥写法：

```python
def __lt__(self, other):
    if not isinstance(other, Node):
        return NotImplemented          # 交给对方处理
    return self.val < other.val
```

### 3.3 `__eq__` 会把 `__hash__` 置为 `None`

**极易踩的坑**：只要你定义了 `__eq__`，Python 自动把 `__hash__` 设为 `None`，对象立刻变得不可哈希。

```python
class P:
    def __init__(self, x): self.x = x
    def __eq__(self, other): return self.x == other.x

{P(1)}      # TypeError: unhashable type: 'P'
```

原因是**哈希不变式 (hash invariant)**：相等的对象必须有相同的哈希值。Python 无法猜出你新定义的相等语义对应什么哈希，只能保守地禁用。

修复方式是显式补上：

```python
class P:
    def __init__(self, x): self.x = x
    def __eq__(self, other): return isinstance(other, P) and self.x == other.x
    def __hash__(self): return hash(self.x)     # 基于相同字段
```

> [!warning]- 边界条件
> 
> - **`__hash__` 必须基于不可变字段**。若字段可变，对象放进 `set` 后再修改，哈希桶就找不到它了 —— 逻辑上的内存泄漏。
> - **只定义 `__lt__` 不定义 `__eq__`**：`sorted` / `heapq` 能用（它们只需要 `<`），但 `a == b` 会退化为**身份比较** `is`，两个 val 相同的节点被判为不等。本题不影响，但换成去重题就出错。
> - **`__len__` 返回 0 时对象为假**。若你的类逻辑上「空但有意义」，要显式实现 `__bool__` 覆盖掉。
> - **`__repr__` 里不要访问可能不存在的属性**，否则调试时报错叠报错，极难排查。
> - **`__getattr__` 只在属性查不到时触发**，`__getattribute__` 才是每次都触发（后者极易写出无限递归，不要碰）。

### 3.4 `functools.total_ordering`

只想写一个比较方法、却要全套运算符时用它：

```python
from functools import total_ordering

@total_ordering
class Task:
    def __init__(self, pri): self.pri = pri
    def __eq__(self, other): return self.pri == other.pri
    def __lt__(self, other): return self.pri < other.pri
    # __le__ __gt__ __ge__ 自动补全
```

要求：必须提供 `__eq__` 加**至少一个**序方法。代价是自动生成的版本比手写慢（每次多一层函数调用）。

---

## 4. 实例一：让 `ListNode` 可比较、可打印

LeetCode 的 `ListNode` 由平台提供，不能改定义，只能猴子补丁。目标是让它能进堆，顺便让调试输出可读。

> [!success]- 完整实现
> 
> ```python
> from heapq import heapify, heappop
> 
> # ① 支持 < ：heapq / sorted / min / max 全部解锁
> ListNode.__lt__ = lambda a, b: a.val < b.val
> 
> # ② 支持打印：默认输出是 <ListNode object at 0x7f...>，毫无信息
> def _node_repr(self):
>     vals, cur, guard = [], self, 0
>     while cur and guard < 20:              # 防环，避免调试时死循环
>         vals.append(str(cur.val))
>         cur, guard = cur.next, guard + 1
>     if cur: vals.append("...")
>     return "->".join(vals)
> ListNode.__repr__ = _node_repr
> 
> # 用起来
> h = [head for head in lists if head]
> heapify(h)
> print(h)          # [1->4->5, 1->3->4, 2->6]  ← 一眼看清堆里有什么
> print(heappop(h)) # 1->3->4 或 1->4->5
> ```

### 说明

|位置|要点|
|---|---|
|`__lt__` 用 lambda|一行逻辑，够用；多行就改 `def` 再赋值|
|`__repr__` 而非 `__str__`|容器内显示（`print(h)`）只走 `__repr__`，`__str__` 不生效|
|`guard < 20`|链表带环时 `__repr__` 会无限循环，加个上限保命|
|赋值目标是 `ListNode.xxx`|打在**类**上，见 3.1|

`print(h)` 打印的是 list，list 的 `__repr__` 会对每个元素调 `repr()` —— 这就是为什么必须实现 `__repr__` 而不是 `__str__`。这一点在链表和树的调试里非常实用。

---

## 5. 实例二：用 `__iter__` 让链表可迭代

链表调试的痛点是「看不见内容」。实现 `__iter__` 后，`list()`、`for`、解包、`in` 全部可用。

> [!success]- 完整实现
> 
> ```python
> def _node_iter(self):
>     cur = self
>     while cur:
>         yield cur.val          # 生成器函数天然就是迭代器
>         cur = cur.next
> ListNode.__iter__ = _node_iter
> 
> # 解锁的用法
> head = build([1, 2, 3, 4, 5])
> print(list(head))              # [1, 2, 3, 4, 5]
> print(sum(head))               # 15
> print(max(head))               # 5
> print(3 in head)               # True   ← __contains__ 缺失，回退到迭代
> for v in head:
>     print(v, end=" ")          # 1 2 3 4 5
> a, b, *rest = head             # 解包也能用
> ```

**为什么 `yield` 就够了**：迭代协议要求 `__iter__` 返回一个有 `__next__` 的对象。生成器函数被调用时返回生成器 (generator)，它同时实现了 `__iter__` 和 `__next__` —— 一步到位，不用手写迭代器类。

对比手写版本（理解协议用，实战不必）：

```python
class _NodeIterator:
    def __init__(self, node): self.cur = node
    def __iter__(self): return self          # 迭代器必须返回自身
    def __next__(self):
        if not self.cur: raise StopIteration # 耗尽的信号
        val, self.cur = self.cur.val, self.cur.next
        return val
```

> [!summary]- 当前实例复杂度
> 
> - 遍历一次：时间 $O(n)$，与手写 `while cur` 完全相同 —— `yield` 不产生额外的渐进开销。
> - 空间：$O(1)$，生成器是**惰性 (lazy)** 的，不会一次性构造整个列表；`list(head)` 才会占 $O(n)$。
> - 常数开销：每次 `next()` 有一层函数调用，比裸 `while` 略慢，调试场景无所谓。

---

## 6. 与相近写法怎么选

|需求|推荐写法|原因|
|---|---|---|
|一次性排序，比较标准临时|`sorted(xs, key=...)`|不碰类，最轻量；`key` 只算一次，比 `__lt__` 快|
|进 `heapq`，类不归你|猴子补丁 `__lt__` 或 tuple 包装|`heapq` **没有** `key=` 参数|
|进 `heapq`，不想污染全局|tuple 包装 `(key, i, obj)`|见 [[23. 合并 K 个升序链表]]，需 tiebreaker|
|类归你、比较是内在语义|类里定义 `__lt__`|正规做法，可读性最好|
|要全套比较运算符|`@total_ordering` 或 `@dataclass(order=True)`|少写四个方法|
|纯数据容器|`@dataclass` / `NamedTuple`|自动生成 `__init__` `__repr__` `__eq__`|

**`key=` 和 `__lt__` 的分工**：`key=` 是「这一次这样排」，`__lt__` 是「这个类天生就这样排」。临时需求用前者，内在语义用后者。`heapq` 不支持 `key=` 是个例外，所以才需要 tuple 包装这个变通。

---

## 7. 常见易错点

> [!warning]- 易错点
> 
> - **补丁打在实例上**：`node.__lt__ = ...` 无效，dunder 只在类型上查找。必须写 `ListNode.__lt__ = ...`。
> - **定义了 `__eq__` 忘补 `__hash__`**：对象变得不可哈希，进 `set` / 作 dict 键时 `TypeError: unhashable type`。
> - **实现 `__str__` 却在容器里看不到效果**：`print(列表)` 走的是元素的 `__repr__`，调试时优先实现 `__repr__`。
> - **`lambda a, b: a.val < b.val` 里的冒号当成条件**：冒号是参数与返回值的分隔符，函数对任何输入都会执行，只是返回 `True` 或 `False`。
> - **返回 `NotImplementedError` 而非 `NotImplemented`**：前者是异常类，会直接抛错；后者是单例值，用于触发反射运算。
> - **在 `__hash__` 里用了可变字段**：对象进 `set` 后修改字段，就再也找不到它了。
> - **`__getattr__` 里访问自身属性导致无限递归**：需要用 `object.__getattribute__(self, name)` 或 `self.__dict__` 绕开。
> - **`__iter__` 返回了自己但没有 `__next__`**：`TypeError: iter() returned non-iterator`。用生成器函数最省事。
> - **猴子补丁污染全局**：修改的是类对象，影响整个进程。LeetCode 单次提交无害，工程代码要慎用。

---

## 性能与查找机制

> [!summary]- 复杂度
> 
> - dunder 调用本身：$O(1)$ 的查找 —— CPython 把常用 dunder 存在类型对象的 **slot**（C 结构体字段）里，不走字典查找，所以 `a < b` 只比裸函数调用略慢。
> - `sorted(xs)` 用 `__lt__`：$O(n\log n)$ 次比较，每次一层 Python 函数调用 —— 因此 `key=` 通常更快（只算 $n$ 次 key，之后比较原生类型）。
> - `@total_ordering` 生成的方法：每次多一层间接调用，热路径上建议手写。
> - `__iter__` 用生成器：遍历 $O(n)$、额外空间 $O(1)$，惰性求值不预先物化。

---

## 一句话总结

特殊方法是 Python **把内建语法翻译成方法调用**的协议表；看到 `TypeError: '<' not supported` / `not iterable` / `unhashable type` 就去补对应的 dunder，且**必须挂在类上**而不是实例上。

---

## 模板归纳

看到以下报错或需求时，对号入座：

|信号|缺的方法|
|---|---|
|`'<' not supported between instances of`|`__lt__`|
|`object is not iterable`|`__iter__`（或 `__getitem__`）|
|`unhashable type`|`__hash__`（通常是定义了 `__eq__` 引起的）|
|`object of type X has no len()`|`__len__`|
|`object is not subscriptable`|`__getitem__`|
|`object is not callable`|`__call__`|
|打印出 `<X object at 0x...>`|`__repr__`|

```python
# 算法题万能补丁模板：把不可比较的平台类塞进堆/排序
SomeClass.__lt__ = lambda a, b: a.key < b.key        # 解锁 heapq / sorted / min / max
SomeClass.__repr__ = lambda self: f"X({self.key})"   # 解锁可读的调试输出

# 自己的类：一次配齐
from functools import total_ordering

@total_ordering
class Item:
    __slots__ = ("key",)                    # 可选：省内存、禁止动态属性
    def __init__(self, key): self.key = key
    def __eq__(self, o): return isinstance(o, Item) and self.key == o.key
    def __lt__(self, o): return self.key < o.key
    def __hash__(self): return hash(self.key)        # 定义 __eq__ 后必须补
    def __repr__(self): return f"Item({self.key})"
```

三个必查项：① 补丁是否打在**类**上；② 定义 `__eq__` 后是否补了 `__hash__`；③ 调试输出实现的是 `__repr__` 而非 `__str__`。

---

相关笔记：[[23. 合并 K 个升序链表]]（`heapq` 与 `__lt__` 的实战场景）、[[堆与优先队列]]

算法标签：`python-syntax` `special-method` `dunder` `operator-overloading` `protocol`