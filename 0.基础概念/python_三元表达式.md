
# ✅ expression if cond else expression —— 两边都是"值"
x = a if a > 0 else -a

# ❌ 三元表达式里塞 statement
n = len(digits) if n != 0 else return []   # SyntaxError


必须两边都是值才可以去使用
