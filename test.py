from chess import piece_str, Board, start, check_safe, Move, K, Q, R, B, N

assert piece_str(1) == 'K'
assert piece_str(-1) == 'k'
assert piece_str(6) == 'P'

board = start()
board.move((64), (44))
board = board.flip()
board.move((64), (44))
board = board.flip()
board.move((44), (34))
board = board.flip()
board.move(62, 42)
board = board.flip()
board.move(34, 25)
assert board.data[24] == 0
board = board.flip()

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


def checkreplay(board:Board, move:Move):
  prestate = board.data.copy()
  preparams = board.passant, board.castles.copy()
  mv = board.move(move.start, move.end, move.prom)
  board.unmove(mv)

  assert (prestate == board.data).all()
  assert preparams == (board.passant, board.castles)

board.passant = 21
checkreplay(board, Move(board, 64, 44))
checkreplay(board, Move(board, 64, 54))
checkreplay(board, Move(board, 71, 50))
checkreplay(board, Move(board, 74, 65))

checkreplay(board, Move(board, 30, 21))

board = start()

board.move(64, 54)
board.move(75, 64)
board.move(76, 57)
assert Move(board,74, 76) in board.get_moves()
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
step = board.move(73, 71)

print(board)

print(board.castles)
board.unmove(step)

print(board)

print(step.__dict__)

assert rp == str(board)