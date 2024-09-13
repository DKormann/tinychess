import random
from chess import Board, Move

def handle(state:Board):

  search = SearchNode(0.5)

  search.expand(state)

  print(search.options)

  for i in range(100):
    search.expand(state)

  bestm, bestn = search.options[0]


  print(search.options)
  for m, n in search.options:
    if n.eval > bestn.eval:
      bestn = n
      bestm = m
  return bestm

from typing import List, Tuple

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
  
