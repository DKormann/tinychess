import random
from chess import Board, Move

def handle(state:Board, depth=2):

  _, mv = absearch(state, depth)
  print("plan:")
  for i,m in enumerate(mv): print(m.flip() if i%2 and isinstance(m, Move) else m)
  print()
  return mv[0]

from typing import List, Tuple


def absearch(state:Board, depth:int, minval = 0., maxval = 1.):

  if depth == 0: return state.eval(), ["fin"]
  
  bestmove = ['placeholder']
  for m in state.get_moves():

    step = state.move(m)
    if not step: continue
    val, mv = absearch(state.flip(), depth-1, 1-maxval, 1-minval)
    val = 1 - val

    if val > minval:
      minval = val
      bestmove = [m] + mv
    if val >= maxval: return val, bestmove
    state.unmove(step)
  
  return minval, bestmove
