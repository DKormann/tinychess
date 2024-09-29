from tinychess.chess import piece_str, Board, check_safe, Move, K, Q, R, B, N, P, e

assert piece_str(1) == 'K'
assert piece_str(-1) == 'k'
assert piece_str(6) == 'P'

board = Board.start()
board = board.move(64, 44)
assert board.get(44) == P
assert board.get(64) == e
board = board.move(14, 34)

board = board.move(71, 52 )
board = board.move(12, 32)
assert board.data[24] == 0



board = Board.fromstring(s:='''\
r n . q k b . r
p . p p p p p p
. . b . . n . .
P p . . . . . .
. . . . . . . .
. . . . . P . .
. P P P P . P P
R N B Q K B N R''')


assert len(board.get_moves()) == 21, f'{len(board.get_moves())}'
assert str(board).strip() == s.strip()

assert check_safe(board.data, 45)
assert not check_safe(board.data, 46)
assert not check_safe(board.data, 55)
assert check_safe(board.data, 54)
assert not check_safe(board.data, 21)


board = Board.start()

board = board = board.move(64, 54)
board = board = board.move(6, 25)
board = board = board.move(76, 57)
board = board = board.move(1, 22)
board = board = board.move(75, 64)
assert Move(board, 74, 76) not in board.get_moves()
board = board = board.move(13, 23)
board.move(74,76)


board = Board.fromstring('''\
r n b q k b n r
p p p p p p p p
. . . . . . . .
. . . . . . . .
. . . . . . . .
. . . . P . . N
P P P P B P P P
R N B Q K . . R
''')

assert repr(board) == repr(board.mirror().mirror())


print(board)

for mv in board.get_moves():
  print(mv, mv.algebraics())

assert Move(board, 74, 76) in board.get_moves()

board = Board.empty()
board.data[70] = R
board.data[74] = K
board.castles = [True, True]
assert Move(board, 74, 72) in board.get_moves()

board.data[43] = -R

assert not check_safe(board.data, 73)
assert Move(board, 74, 72) not in board.get_moves()

board = Board.empty()

board.data[70] = R
board.data[73] = K
rp = str(board)


assert Move(P, 13,4) in Board.fromstring('''\
r n b q k b . r
p . . P . p p p
. p . . . n . .
. . p . p . . .
. . . P . . . .
. . . . . . . .
P P P . . P P P
R N B Q K B N R''').get_moves()