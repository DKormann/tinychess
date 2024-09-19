#%%

with open('dataset/highrated.nums') as f:
  data = f.readlines()

#%%

games = []

for line in data[:]:
  game = []
  for move in line.split(',')[1:]:
    move = move.strip().replace('Q', '')
    if 'N' in move: break
    game.append(move)
  if len (game) < 10: continue
  print(' '.join(game))
  games.append(game)

lens = list(map(len, games))
# %%
import numpy as np
import matplotlib.pyplot as plt

_ = plt.hist(lens, bins=range(10, 400, 5))
# %%

def mv2num(mv):
  def pos(c):
    res = 8*(c//10) + c%10
  
    assert res < 64
    return res
  start, end = [int(x) for x in mv.split('->')]
  return pos(start), pos(end)

# %%
ids = np.array(list(map(mv2num, games[0])))
eye=np.eye(2**12)

onehot = eye[ids]

#%%
