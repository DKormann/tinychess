#%%
from chess import Board, Move
from bot import handle



from chess import Q, K, N, P, R
from chess import Board
from bot import MCTSNode

def MChandle(board, N = 40):
  root = MCTSNode()
  for i in range(N):
    root.expand(board)
  
  return max([(child.n, mv) for mv, child in root.children])[1]

root = MCTSNode()

board = Board.empty()
board.castles = [False]*4
board.data[0] = -K
board.data[70] = K

board.data[32] = P


print(board)
print()


for i in range(1000):
  root.expand(board)

for mv, c in root.children:
  print(c.n, mv, c.score)
print()

# for mv, c in root.children[0][1].children:
  # print(c.n, mv)

