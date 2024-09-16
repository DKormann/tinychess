
#%%
import random
from chess import Board, Move

oo = float('inf')

def handle(state:Board, depth=2):

  val, mv = absearch(state, depth)
  print("plan:")
  for i,m in enumerate(mv): print(m.flip() if i%2 and isinstance(m, Move) else m)
  print()
  return val, mv[0]

from typing import List, Tuple


transtable = {}

def absearch(state:Board, depth:int, minval = 0., maxval = 1.):
  # key = hash(state.tuple, depth)
  bestmove = ['placeholder']
  if depth == 0 or not (options:=state.get_moves(only_captures=depth<1)): return state.eval(), ['fin']
  for m in options:

    step = state.move(m)
    if not step: continue
    val, mv = absearch(state.flip(), depth-1, 1-maxval, 1-minval)
    val = 1 - val

    if val > minval:
      minval = val
      bestmove = [m] + mv
    if val >= maxval: break
    state.unmove(step)
  
  # transtable[key] = minval
  return minval, bestmove


#%%


import math


# explore param
c = 2.

def MChandle(board, N = 40):
  root = MCTSNode()
  for i in range(N):
    root.expand(board)
  
  return root.score/root.n, max([(child.n, mv) for mv, child in root.children])[1] if root.children else 'placeholder'


class MCTSNode():
  def __init__(self):
    self.children:list[tuple[Move, MCTSNode]] = []
    self.n = 0
    self.score = 0

  def expand(self, board:Board):
    self.n += 1

    if self.n == 1:
      self.score = board.eval()
      return self.score
    if self.score == 0 or self.score == 1 : return self.score

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
    hist = board.move(mv)
    if hist == False:
      child.n += 1
      return -1
    val = 1 - child.expand(board.flip())
    self.score += val
    board.unmove(hist)
    return val
