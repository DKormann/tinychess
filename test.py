from main import State
import numpy as np

start = State.start()

s = start.move((6, 0), (5, 0))
assert s.turn == 1

moves = s.moves

assert s.check_move(((1,0), (2,0)))
assert s.check_move(((1,0), (3,0)))
assert not s.check_move(((1,0), (4,0)))


s = s.move((1, 0), (2, 0))
assert s.turn == 2
print(s.moves)

print(s)

