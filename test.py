from main import State, check_safe
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


datastring = '''\
r n b q k b n r
. p p p p p p p
p . . . . . . .
. . . . . . . .
. . . . . . . .
P . . . . . . .
. P P P P P P P
R N B Q K B N R'''

loaded = State.from_str(datastring)
loaded.turn = 2

assert loaded == s

assert check_safe(loaded.data, [6,4])

loaded = State.from_str("""\
. . . . . . . .
. n . . . . . .
. . . . . . . .
. . . . . . . .

. . . . . . . .
. . . . . . . .
. b . . . . . .
. . . . . . . .""")

assert check_safe(loaded.data, [6,4])
assert not check_safe(loaded.data, [4,3])

