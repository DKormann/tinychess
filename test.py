
from chess import Piece, Color, Fig, Board, start

assert Piece.from_num(1) == Piece(Color.White, Fig.King)
assert Piece.from_char('K') == Piece(Color.White, Fig.King)
assert Piece.from_char('r') == Piece(Color.Black, Fig.Rook)



print(start)

print(start.get_moves())

print(start.move(76, 55))