import random
from chess import Board, Move

def handle(state:Board, depth=2):

  val, mv = absearch(state, depth)
  return mv

from typing import List, Tuple


def absearch(state:Board, depth:int, minval = 0., maxval = 1.):
  if depth == 0: return state.eval(), None
  
  bestmove = None

  pre = str(state)
  for m in state.get_moves():
    try:
      step = state.move(m)
      val = 1 - absearch(state.flip(), depth-1, 1-maxval, 1-minval)[0]

      if val > minval:
        minval = val
        bestmove = m
      if val > maxval: return val, None
      state.unmove(step)

    except RuntimeError: pass

    assert pre == str(state), f'\n{pre}\n\n{state}'
  
  return minval, bestmove

class SearchNode():
  def __init__(self, eval:float):
    self.eval = eval
    self.options:List[Tuple[Move, SearchNode]] = []
    self.n = 0
    self.score = 0.
  
  def expand(self, board:Board):
    if self.n == 0:
      self.options = []
      for mv in board.get_moves():
        try:
          o = board.move(mv)
          val = board.eval()
          board.unmove(o)

          self.options.append((o, SearchNode(1-val)))
        except RuntimeError: pass
    else:
      _, targetnode = self.options[0]
      for mv, sn in self.options:
        if sn.n == 0:
          targetnode = sn
          break
        else:
          if sn.n < targetnode.n:
            targetnode = sn
      board.flip()
      targetnode.expand(board)
      board.flip()
    self.n += 1
    self.eval = max([1-sn.eval for _,sn in self.options])

  def __repr__(self): return f'SN:{self.eval:2.2f}'
  
