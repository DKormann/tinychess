
from chess import Piece, Color, Fig, Board, start

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



