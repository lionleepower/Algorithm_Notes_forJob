# Python `@cache`：一行装饰器实现记忆化

`functools.cache`（Python 3.9+）是一个装饰器，自动把函数的「参数 → 返回值」存进字典，相同参数第二次调用直接返回缓存结果。它让 [[记忆化搜索]] 从「手写缓存表」缩成一行 `@cache`，是自顶向下写 DP 最快的方式。

---

## 思路

手写记忆化要维护缓存数组、选哨兵值、处理多维 key，样板代码多且容易错。`@cache` 把这些全接管：以**参数元组**为 key 查字典，「key 在不在」本身就是「算没算过」的标记，因此**不需要哨兵值**，多维参数也零额外代码。

> [!tip]- 核心思路
> 
> ```python
> from functools import cache
> 
> @cache                     # 加在递归函数上，其它一字不改
> def dfs(i: int) -> int:
>     if i < 0:
>         return 0
>     return max(dfs(i - 1), dfs(i - 2) + nums[i])
> ```
> 
> 成立前提和手写记忆化完全一致：函数必须**无后效性**（返回值只由参数决定），且参数必须**可哈希**。

---

## 1. 导入与创建

> [!success]- 基础语法
> 
> ```python
> from functools import cache          # Python 3.9+
> # 3.8 及以前用 lru_cache：
> from functools import lru_cache
> 
> @cache
> def f(x): ...
> 
> @lru_cache(maxsize=None)             # @cache 等价于 lru_cache(maxsize=None)
> def g(x): ...
> ```

---

## 2. 核心操作

| 操作 | 作用 | 注意事项 |
| --- | --- | --- |
| `@cache` | 自动缓存全部调用结果 | 缓存无上限，长期运行可能吃内存 |
| `@lru_cache(maxsize=N)` | 只保留最近 N 条 | DP 里通常要 `None`，别限量 |
| `f.cache_clear()` | 清空缓存 | 多组测试数据间要清，否则串味 |
| `f.cache_info()` | 查命中 / 未命中次数 | 调试确认是否真的命中 |

> [!example]- 手写 vs `@cache` 逐条对应
> 
> ```python
> # 你写的                          # @cache 帮你做的
> memo = [-1] * n                  # 内部建一个 dict
> if memo[i] != -1: return memo[i] # 以参数元组为 key 查 dict
> memo[i] = res                    # 算完写回 dict
> ```
> 
> 区别只有两点：dict 用「key 在不在」当标记所以**免哨兵**；参数几维都自动支持，写 `dfs(i, j, k)` 无需改动。

---

## 3. 关键行为与边界

> [!warning]- 边界条件
> 
> - **参数必须可哈希**：`int` / `str` / `tuple` 可以；`list` / `dict` / `set` 会抛 `TypeError: unhashable type`——传数组要先转 `tuple`。
> - **多组用例要 `cache_clear()`**：LeetCode 把 `dfs` 定义在方法内、每次新建时问题不大；但定义在类外或全局时，上一组的缓存会污染下一组。
> - **别用 `maxsize` 限量做 DP**：限量会淘汰仍需复用的状态，退化回重复计算。
> - **变量名别叫 `cache`**：局部变量 `cache` 会遮住 `from functools import cache`，之后再想用装饰器就报错；习惯把手写表叫 `memo`。

---

## 4. 实例：打家劫舍的 `@cache` 写法

> [!success]- 完整实现
> 
> ```python
> from functools import cache
> from typing import List
> 
> class Solution:
>     def rob(self, nums: List[int]) -> int:
>         @cache                       # 定义在方法内，闭包捕获 nums
>         def dfs(i: int) -> int:
>             if i < 0:
>                 return 0
>             return max(dfs(i - 1), dfs(i - 2) + nums[i])
>         return dfs(len(nums) - 1)
> ```
> 
> 主流程：递归方程和朴素版一字不差，`@cache` 独自负责去重。定义在方法内，`dfs` 每次随实例重建，天然隔离不同用例。

> [!summary]- 复杂度
> 
> - 时间：$O(n)$——$n$ 个状态各只真正算一次，其余命中 $O(1)$（哈希均摊）。
> - 空间：$O(n)$ 缓存字典 + $O(n)$ 递归栈。
> - 代价：dict 常数比数组大，且不能像数组那样 $O(1)$ 随机访问；换来的是免哨兵、多维零改动。

---

## 5. 与手写 memo 怎么选

| 需求 | 推荐写法 | 原因 |
| --- | --- | --- |
| 面试速写、参数多维 / 非整数 | `@cache` | 一行搞定，免哨兵，key 自动组合 |
| 参数是小范围非负整数、追求常数 | 手写数组 memo | $O(1)$ 随机访问、无哈希开销 |
| C++ / 无装饰器语言 | 手写 | 没有 `@cache` 可用 |

---

## 一句话总结

`@cache` 用字典把「参数→结果」记死，一行实现记忆化、免哨兵、多维自动支持；前提是函数无后效性且参数可哈希，多组用例记得 `cache_clear()`。

---

## 模板归纳

看到以下信号，优先用 `@cache`：

- 已写出无后效性的递归方程，只想去掉重复计算。
- 状态是多维或非整数（字符串、坐标元组），手写数组不方便。

```python
from functools import cache

@cache
def dfs(*state):
    if 到达边界:
        return 基础值
    return combine(dfs(下一状态), ...)
```

相关：[[记忆化搜索]] · [[7.1 DP 打家劫舍]] · [[重叠子问题与无后效性]] · [[Python_dict]]
