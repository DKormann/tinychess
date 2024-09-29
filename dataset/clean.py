#%%
import csv, sys
import numpy as np
from tinychess.chess import Board, Move

games = csv.reader(open('dataset/games.csv'))
games = [[['white','black','draw'].index(g[6]), g[12], int(g[11])] for g in list(games)[1:]]

maxlen = 100

#%%
allmoves = []
wins = []
allpieces = []

minrating = ([int(a.split('=')[1]) for a in sys.argv if a.startswith('--elo')]+[2000])[0]

def parsegame(win, moves, rating):
  board = Board.start()

  toks = []
  pieces = []
  for ms in moves.split():
    m = Move.from_algebraic(board, ms)
    if m is None:return
    toks += list(m.tokens())
    pieces += [0, m.prom or m.piece]
    try: board = board.move(m)
    except ValueError: return

  toks = toks + [0] * (maxlen*2 - len(toks))
  toks = toks[:maxlen*2]
  pieces = pieces + [0] * (maxlen*2 - len(pieces))
  pieces = pieces[:maxlen*2]
  allmoves.append(toks)
  allpieces.append(pieces)
  wins.append(win)

for win, moves, rating in games:
  if rating < minrating: continue
  parsegame(win, moves, rating)
  if len (allmoves) > 20_000: break

np.savez(f'dataset/moves{minrating}+.npz', moves=np.array(allmoves), wins=np.array(wins), pieces=np.array(allpieces))
