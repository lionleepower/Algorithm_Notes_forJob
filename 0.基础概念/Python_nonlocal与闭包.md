# Python nonlocal 与闭包：内层函数怎么改写外层的变量

递归里常见的写法是「外层定义一个 `ans`，内层 `dfs` 一边递归一边更新它」。**内层函数读外层变量不用声明，但只要写（赋值），就必须 `nonlocal`**，否则 Python 会把它当成一个全新的局部变量，直接报 `UnboundLocalError`。树形 DP 打擂台、回溯计数、DFS 收集答案都要用到。

---

## 思路

Python 的作用域是**编译期静态决定**的：函数体里只要出现「给某个名字赋值」的语句，这个名字**在整个函数里**就被登记为局部变量——哪怕赋值写在最后一行。于是 `ans = ans + 1` 里右边那个 `ans` 找的是「本函数的局部 `ans`」，而它还没被赋值，就炸了。

`nonlocal` 的作用就是取消这次登记：**告诉编译器「这个名字不是我的，去最近的外层函数里找那个已存在的绑定，我要改的是它」。**

> [!tip]- 核心思路
> 
> **读不用声明，写才要声明。**
> 
> ```python
> def solve():
>     ans = 0
>     def dfs(x):
>         nonlocal ans          # 只要下面出现 ans = ...，这行就不能少
>         ans = max(ans, x)
>     dfs(3)
>     return ans
> ```
> 
> 判据一句话：**函数体里有没有「`名字 =`」这种赋值？** 有 → 需要 `nonlocal`（或 `global`）；只是取值、只是 `ans[0] += 1` 这种改内容 → 不需要。

---

## 1. 闭包是什么

内层函数引用了外层函数的局部变量，这个「函数 + 它捕获的外层变量」的组合就叫**闭包 Closure**。被捕获的变量叫**自由变量 free variable**，它不会随外层函数返回而消失。

> [!success]- 基础语法
> 
> ```python
> def outer():
>     ans = 42                      # 外层局部变量
>     def inner():
>         return ans                # 自由变量：只读，不需要任何声明
>     return inner                  # 返回函数本身，不是调用结果
>
> f = outer()
> print(f())                        # 42 —— outer 早已返回，ans 仍活着
> print(f.__code__.co_freevars)     # ('ans',)  自由变量名
> print(f.__closure__[0].cell_contents)  # 42    实际存放的值
> ```
> 
> `ans` 被存进一个 cell 对象里由闭包持有，所以外层函数返回后它依然存活。

---

## 2. 三个关键字对照

| 写法 | 改的是谁 | 什么时候用 |
| --- | --- | --- |
| 不声明 | 只能**读**外层变量 | 取值、传参、比较 |
| `nonlocal x` | 最近的**外层函数**里的 `x` | 嵌套函数（`dfs` 更新 `ans`），**算法题里几乎只用这个** |
| `global x` | **模块级**的 `x` | 改全局配置，算法题里基本用不到 |

> [!example]- 三种情形的最小对照
> 
> ```python
> def outer():
>     ans = 0
>
>     def read_only():
>         return ans + 1            # ✓ 只读，不用声明
>
>     def bad():
>         ans = ans + 1             # ✗ UnboundLocalError
>
>     def good():
>         nonlocal ans
>         ans = ans + 1             # ✓
>
>     return read_only, bad, good
> ```
> 
> 报错信息：`UnboundLocalError: local variable 'ans' referenced before assignment`（Python 3.11+ 措辞改成 `cannot access local variable 'ans' where it is not associated with a value`，是同一个错）。

---

## 3. 关键行为与边界

> [!tip]- 为什么「只读」不用声明，「写」就必须声明
> 
> 名字查找走的是 **LEGB** 顺序：Local → Enclosing → Global → Builtins。**读**的时候本层找不到就自动往外找，所以不用声明。
> 
> 但**写**不一样：Python 不允许「隐式地改外层作用域」，否则一个手滑的赋值就能污染外层状态。所以规则被定成「**赋值默认创建本层变量**」，想改外层必须显式表态。`nonlocal` 就是那次表态。
> 
> 注意这是**编译期**决定的，与运行顺序无关——即使赋值语句写在函数最后一行、甚至在一个永不执行的 `if` 里，整个函数里的这个名字也已经是局部的了。

> [!warning]- 边界条件
> 
> - **`nonlocal` 必须有外层绑定**：外层函数里不存在同名变量时，`nonlocal x` 直接是**语法错误** `no binding for nonlocal 'x' found`——它不会帮你创建变量。
> - **`nonlocal` 绑不到模块级**：外层是模块（不是函数）时必须用 `global`，`nonlocal` 会报同样的语法错误。
> - **`+=` 也是赋值**：`ans += 1` 等价于 `ans = ans + 1`，同样需要 `nonlocal`。
> - **`ans[0] += 1` 不需要**：那是「改对象内容」不是「重新绑定名字」，见下一节。参见 [[Python_赋值与拷贝]]。
> - **循环变量的延迟绑定**：闭包捕获的是**变量本身**，不是当时的值，见易错点。

---

## 4. 实例一：树形 DP 打擂台（最典型用法）

树的直径类问题里，「拐点路径」没法向上返回，只能当场记进全局擂台——`nonlocal` 就是干这个的。

> [!success]- 完整实现
> 
> ```python
> def diameterOfBinaryTree(root) -> int:
>     ans = 0
>     def dfs(node):
>         if node is None:
>             return -1
>         l, r = dfs(node.left), dfs(node.right)
>         nonlocal ans                     # 因为下一行要给 ans 赋值
>         ans = max(ans, l + r + 2)        # 报答案：拐点路径，用完即弃
>         return max(l, r) + 1             # 传上去：单链，靠返回值
>     dfs(root)
>     return ans
> ```
> 
> - **主流程**：`return` 与 `nonlocal ans` 是**两条独立的轨道**——返回值传给父节点，擂台收集全局答案。详见 [[7.7 树型DP 树的直径]]。
> - **易错位置**：`nonlocal` 写在函数体任意位置都合法，但必须在第一次赋值**之前**；习惯上写在赋值那行的紧上方或函数开头。

---

## 5. 实例二：能用返回值就别用 nonlocal

同样是树形 DP，[[7.8 树型dp 打家劫舍 树上最大独立集]] 完全不需要 `nonlocal`——因为每个子树要报告的信息可以**打包进返回值**。

> [!success]- 两种风格对照
> 
> ```python
> # ① 返回值风格（推荐）：信息随返回值上传，没有共享状态
> def rob(root) -> int:
>     def dfs(node):
>         if node is None:
>             return 0, 0                          # (选, 不选)
>         l_rob, l_not = dfs(node.left)
>         r_rob, r_not = dfs(node.right)
>         return (l_not + r_not + node.val,
>                 max(l_rob, l_not) + max(r_rob, r_not))
>     return max(dfs(root))
>
> # ② 擂台风格：只有「这个量无法向上传」时才被迫使用
> def count_nodes(root) -> int:
>     cnt = 0
>     def dfs(node):
>         if node is None: return
>         nonlocal cnt
>         cnt += 1
>         dfs(node.left); dfs(node.right)
>     dfs(root)
>     return cnt
> ```
> 
> **判据**：这个量能不能作为「子树的答案」向上合成？能 → 用返回值（无共享状态，更容易验证）；不能（比如拐点路径、全局计数） → 才用 `nonlocal`。

---

## 6. 与相近写法怎么选

| 需求 | 推荐写法 | 原因 |
| --- | --- | --- |
| 子问题的答案能向上合成 | **返回值**（可以是元组） | 无共享状态，天然无副作用，最好验证 |
| 全局最值 / 计数，无法上传 | `nonlocal ans` | 语义最直白，一行声明 |
| 不想写 `nonlocal` | `ans = [0]` 后 `ans[0] += 1` | 改的是列表内容不是名字绑定，所以免声明；但可读性差 |
| 状态很多、要传给多个函数 | 包成类的属性 `self.ans` | 见 [[Python_self与递归调用]] |

`ans = [0]` 这种「用可变容器绕过声明」的写法在竞赛代码里常见，理解即可，**面试白板建议老老实实写 `nonlocal`**，意图更清楚。

---

## 7. 常见易错点

> [!warning]- 易错点
> 
> - **漏写 `nonlocal` 却给外层变量赋值** → `UnboundLocalError`。最隐蔽的场景：函数很长，赋值语句藏在某个分支里，读的地方在前面，看起来「明明有值」却报未赋值。
> - **以为 `nonlocal` 能创建变量**：它只做「绑定到已存在的外层变量」，外层没有就是语法错误。必须先在外层写 `ans = 0`。
> - **`nonlocal` 与 `global` 用反**：外层是函数用 `nonlocal`，外层是模块用 `global`。
> - **循环里的闭包延迟绑定**：
> 
> ```python
> fs = [lambda: i for i in range(3)]
> print([f() for f in fs])          # [2, 2, 2]  ✗ 全是最后一个值
>
> fs = [lambda i=i: i for i in range(3)]
> print([f() for f in fs])          # [0, 1, 2]  ✓ 用默认参数当场固定
> ```
> 
> 闭包捕获的是**变量本身**而不是当时的值，循环结束后 `i` 是 `2`，三个 lambda 一起看到 `2`。回溯题里把 `path` 直接存进结果而不是 `path[:]` 是**同一类错误的另一种形态**——见 [[Python_赋值与拷贝]]。
> - **递归深度**：闭包写法不会增加栈开销，但树 / 链表递归本身可能超过 Python 默认递归上限 1000，必要时 `sys.setrecursionlimit(10**5)`。

---

## 复杂度

> [!summary]- 复杂度
> 
> - 访问自由变量：$O(1)$ —— 通过 cell 对象直接取值，与普通局部变量几乎同速（比全局变量查字典还略快）。
> - 额外空间：$O(1)$ —— 每个被捕获的变量一个 cell，与递归深度无关。

---

## 一句话总结

**内层函数读外层变量随便读，一旦要赋值就必须 `nonlocal`**——因为 Python 在编译期就把「出现赋值的名字」登记成局部变量；而能用返回值上传的信息，就别用擂台变量。

---

## 模板归纳

看到以下信号时想到 `nonlocal`：

- 递归函数需要维护一个**全局最值 / 计数器**，而这个量**没法作为返回值向上合成**（树的直径的拐点路径、路径计数、DFS 统计）
- 写完递归跑出 `UnboundLocalError`，第一反应就是检查有没有漏声明

```python
def solve(...):
    ans = INIT                      # ① 外层先创建绑定
    def dfs(...):
        nonlocal ans                # ② 内层声明要改的是外层那个
        ans = max(ans, 当前候选)     # ③ 打擂台
        return 能向上合成的那部分     # ④ 能返回的就返回，别塞进 ans
    dfs(起点)
    return ans
```

- 同类：[[Python_赋值与拷贝]]（绑定 vs 内容修改，同一套心智模型）· [[Python_self与递归调用]]（用类属性代替闭包变量）
- 用到它的题解：[[7.7 树型DP 树的直径]]（擂台的典型场景，543 / 124 / 2246 全靠它收集拐点答案）· [[7.8 树型dp 打家劫舍 树上最大独立集]]（反例：信息能打包进返回值，就不用它）
