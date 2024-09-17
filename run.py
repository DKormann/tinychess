#%%
from chess import Board, Move
from bot import handle

from chess import Q, K, N, P, R
from chess import Board
from bot import MCTSNode, MChandle

#%%

board = Board.fromstring('''
r n . k . . n r
p p p . . b p p
. . . b . p . .
. . . . p P . .
. . . . . . P .
. . . . . . . P
P P P Q N . . .
R . B K . B . R
''')


print(board)

node, plan = MChandle(board, 4000)
print(plan)

print(node.score/ node.n)

#%%


root = MCTSNode()
for i in range(4000):
  root.expand(board, c=.1)

for m, c in root.children:
  print(m, c.n, c.score/ c.n)