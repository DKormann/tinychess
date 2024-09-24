#%%
import csv
import numpy as np
from tinychess.chess import Board, Move

games = csv.reader(open('dataset/games.csv'))
games = list(games)
games = [[['white','black','draw'].index(g[6]), g[12], int(g[11])] for g in games[1:]]

maxlen = 100

#%%

allmoves = []
wins = []
minrating = 1000

def parsegame(win, moves, rating):
  board = Board.start()

  toks = [0]
  for ms in moves.split():
    m = Move.from_algebraic(board, ms)
    if m is None:return
    toks += list(m.tokens())
    if not board.move(m): return
  toks = toks + [0] * (maxlen*2 - len(toks))
  toks = toks[:maxlen*2]
  allmoves.append(toks)
  wins.append(win)


for win, moves, rating in games:
  if rating < 1000: continue
  parsegame(win, moves, rating)
  print(len(wins))

#%%

np.savez(f'dataset/moves{minrating}+.npz', moves=np.array(allmoves), wins=np.array(wins*2))
