from chess import Board, Move

oo = float('inf')

def handle(state:Board, depth=4):

  val, mv = absearch(state, depth)
  print("plan:")
  for i,m in enumerate(mv): print(m.flip() if i%2 and isinstance(m, Move) else m)
  print()
  return val, mv[0]

from typing import List, Tuple


transtable = {}

def absearch(state:Board, depth:int, minval = 0., maxval = 1.):
  # key = hash(state.tuple, depth)
  bestmove = ['resign']
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
  
  return minval, bestmove

