
#%%

import math
from chess import Board, Move

oo = float('inf')
# explore param
c = 2.

def MChandle(board, N = 100, c=0.2):
  root = MCTSNode()
  for i in range(N): root.expand(board, c= c)

  node, plan = root.best_option()
  print('plan:\n', plan)
  return root.score/ root.n, plan[0] or "resign"


class MCTSNode():

  def __gt__(self,other): return self.n > other.n or self.score > other.score
  def __init__(self):
    self.children:list[tuple[Move, MCTSNode]] = []
    self.n = 0
    self.score = 0
  
  def best_option(self):
    if self.children:
      child, mv = max([(child, mv) for mv, child in self.children])
      return child, [mv] + [m.flip() for m in child.best_option()[1]]
    else: return None, []


  def expand(self, board:Board, c = c):
    self.n += 1

    if self.n == 1:
      self.score = board.eval()
      self.boardeval = board.eval()
      return self.score
    if self.score == 0 or self.score == 1 : return self.score
    assert board.eval() != 0

    if self.n == 2:
      options = board.get_moves()
      for move in options:
        self.children.append((move, MCTSNode()))
    
    if not self.children: return 0
    for i, (mv, child) in enumerate(self.children):
      if child.n == 0: 
        res = self.expand_child(mv, child, board)
        if res < 0:
          self.children.pop(i)
          return 0
        return res
  
    bestucb = -oo
    bestnode = None
    for mv, child in self.children:
      ucb = - child.score/child.n + c * (math.log(self.n)/child.n) ** 0.5
      if ucb > bestucb:
        bestnode = mv, child
        bestucb = ucb
    return self.expand_child(*bestnode, board)
  
  def expand_child(self, mv, child, board:Board):
    assert self.boardeval != 0
    hist = board.move(mv)
    if hist == False:
      child.n += 1
      return -1
    val = 1 - child.expand(board.flip())
    self.score += val
    board.unmove(hist)
    return val

