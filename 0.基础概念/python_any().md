`any()` 是内置函数,签名是 `any(iterable) -> bool`:只要 iterable 里**至少有一个元素是 truthy**,就返回 `True`,否则 `False`。

```python
any([False, False, True])    # True
any([0, 0, 0])               # False
any([])                      # False  ← 空的返回 False
```

配套的 `all()` 是「全部都 truthy 才 True」,空的时候返回 `True`(vacuous truth)。

```python
all([True, True])            # True
all([True, False])           # False
all([])                      # True  ← 注意和 any 相反
```

## 「加和不加」的区别

这个问题最常出现在 generator expression 上,而这里有一个非常经典的坑。假设要判断「列表里有没有大于 5 的数」:

```python
nums = [1, 2, 3]

# ❌ 不加 any
if (n > 5 for n in nums):
    print("有大于 5 的")     # 会打印!哪怕一个都没有

# ✅ 加 any
if any(n > 5 for n in nums):
    print("有大于 5 的")     # 不打印,正确
```

**为什么不加就永远为真?** 因为 `(n > 5 for n in nums)` 求值出来是一个 **generator object**,不是布尔值。而 generator object 是一个普通对象,没有定义 `__bool__` 或 `__len__`,所以 Python 默认认为它 truthy——不管里面有没有元素、元素是什么。`any()` 的作用就是真正去**迭代**这个 generator,把它 collapse 成一个 bool。

|写法|求值结果|`if` 判断|
|---|---|---|
|`(n > 5 for n in nums)`|`<generator object ...>`|永远 True|
|`[n > 5 for n in nums]`|`[False, False, False]`|非空 list → 也是 True ❗|
|`any(n > 5 for n in nums)`|`False`|False ✅|

注意第二行:换成 list comprehension 也不对,因为 `[False, False, False]` 是一个**非空** list,truthiness 看的是长度而不是内容。

## 短路求值 short-circuit

`any()` 一旦遇到第一个 truthy 就立刻停止迭代,后面的元素根本不会被计算:

```python
def check(n):
    print(f"检查 {n}")
    return n > 2

any(check(n) for n in [1, 2, 3, 4, 5])
# 输出:
# 检查 1
# 检查 2
# 检查 3      ← 到这里返回 True,4 和 5 从未被计算
```

如果你写成 `any([check(n) for n in ...])`,list comprehension 会**先把全部 5 个算完**再交给 `any()`,短路就失效了。所以传 generator(不加方括号)通常更好:省内存,还能提前退出。

## 和 `or` 链的区别

`any()` 返回的是**布尔值**,而 `or` 返回的是**元素本身**:

```python
a, b, c = 0, "", "hello"

a or b or c                  # 'hello'   ← 返回元素
any([a, b, c])               # True      ← 返回 bool
```

需要拿到值就用 `or` 或 `next(...)`,只需要知道「有没有」就用 `any()`。

## 接上一个话题的实用场景

判断一个对象是不是多种类型之一,有两种写法:

```python
import io

# 写法 1:isinstance 直接接受 tuple(推荐,更快更简洁)
isinstance(obj, (io.TextIOBase, io.BufferedIOBase))

# 写法 2:any + generator
any(isinstance(obj, t) for t in (io.TextIOBase, io.BufferedIOBase))
```

两者结果等价,但类型是**固定几个**时用写法 1;类型来自一个**运行时才确定的变量/列表**时,写法 2 更自然。

## 常见误用小结

|误写|问题|正确写法|
|---|---|---|
|`if (x for x in lst)`|generator 恒为真|`if any(x for x in lst)`|
|`any([f(x) for x in lst])`|失去短路,全部算完|`any(f(x) for x in lst)`|
|`any(x > 5)` 其中 x 是 int|int 不可迭代 → `TypeError`|`any(n > 5 for n in nums)`|
|用 `any()` 判断空 list 是否「全真」|`any([])` 是 False,`all([])` 是 True|按语义选对函数|