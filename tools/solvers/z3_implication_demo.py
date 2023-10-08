import z3

def implication(P, Q):
    solver = z3.Solver()
    solver.add(z3.And(P, z3.Not(Q)))
    return solver.check() == z3.unsat

"""
x > y, y > z
=> x > z
"""
x, y, z = z3.Ints("x y z")
print(implication(P=z3.And(x > y, y > z), Q=z3.And(x > z)))
print(implication(P=z3.And(x > y, y > z), Q=z3.And(x == x)))

a, b, c, d = z3.Ints("a b c d")
print(implication(P=z3.And(a + b + c + d == 100, a + b == 70), Q=z3.And(c + d == 30)))
print(implication(P=z3.And(a + b + c + d == 100, a + b == 70), Q=z3.And(c == 30)))
print(implication(P=z3.And(a * b + a * d == 100, b + d == 50), Q=z3.And(a == 2)))

