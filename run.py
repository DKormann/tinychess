#%%
from chess import Board, Move


board = Board.fromstring('''
r n b q k . n r
p p . . p p . p
. . p . . b . .
. . . p . . . .
. . . . . Q . .
. N P B P . . p
P P . P . P P P
R . B . . R K .
''').flip()



print(Move(60, 50) in board.get_moves())

