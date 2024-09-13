from chess import Piece, Color, Fig, Board, start, check_safe, Move

assert Piece.from_num(1) == Piece(Color.White, Fig.King)
assert Piece.from_char('K') == Piece(Color.White, Fig.King)
assert Piece.from_char('r') == Piece(Color.Black, Fig.Rook)

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

board = Board.fromstring('''
r n . q k b . r
p . p p p p p p
. . b . . n . .
P p . . . . . .
. . . . . . . .
. . . . . P . .
. P P P P . P P
R N B Q K B N R''')

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
