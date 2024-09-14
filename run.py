#%%
from chess import Board, Move
from bot import handle



# %%


def response(board):

  print(board)
  resp = handle(board, 3)
  return resp

board = Board.fromstring('''
. . . . . k . .
p . p . p p . p
. . n p . . p .
. . . . . . . .
. . . R . . . .
N . . . . . . .
b K P . P . P P
. . . . . B N n 
''')

print(response(board))


# %%
