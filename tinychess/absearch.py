from tinychess.chess import Board, Move

oo = float('inf')


lastval= 0.5

def handle(state:Board, depth=5):
  global lastval

  val, mv = absearch(state, depth, minval=lastval-0.2, maxval=lastval+0.2)
  print(f"plan:{val:0.4f}",)
  for i,m in enumerate(mv): print(m.flip() if i%2 and isinstance(m, Move) else m)
  print()
  lastval = val

  return val, mv[0]

from typing import List, Tuple


transtable = {}

def absearch(state:Board, depth:int, minval = 0., maxval = 1.):
  key = hash((state.tuple, depth, minval, maxval))

  bestmove = ['resign']
  if state.islost():return 0, ['resign']
  if depth == 0 or not (options:=state.get_moves(only_captures=depth<1)):
    transtable[key] = state.eval(), ['fin']
    return transtable[key]
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
  
  transtable[key] = minval, bestmove
  return minval, bestmove

