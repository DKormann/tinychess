from model import Model, device
import os
from loaddata import pieces, positions, policy, wins
from collections import namedtuple
import torch
import numpy as np

def tensor(x):return torch.tensor(x).to(device)

pieces = tensor(pieces)
positions = tensor(positions)
policy = tensor(policy)
wins = tensor(wins)

train_split = 1300
data = namedtuple('data', ['pieces', 'positions', 'policy', 'wins'])

train = data(pieces[:train_split], positions[:train_split], policy[:train_split], wins[:train_split])
test_set = data(pieces[train_split:], positions[train_split:], policy[train_split:], wins[train_split:])

assert test_set.pieces.shape[0] == test_set.positions.shape[0]
assert test_set.policy.shape[0] == test_set.wins.shape[0]

#%%
model = Model().to(device)
opt = torch.optim.Adam(model.parameters(), lr=1e-3)

# %%
bs = 20

def trainstep(i=0):
  model.train(True)
  xpie = train.pieces[i*bs:(i+1)*bs]
  xpos = train.positions[i*bs:(i+1)*bs]
  
  ppol, pwin = model(xpos, xpie) # shape[bs, S, 64]
  ypol = train.policy[i*bs:(i+1)*bs]
  ywin = train.wins[i*bs:(i+1)*bs]

  losspol = torch.nn.functional.cross_entropy(ppol.reshape(-1, 64), ypol.reshape(-1))
  pwin = pwin.reshape(-1, 3)
  ywin = ywin.reshape(-1,1,1).reshape(-1)
  losswin = torch.nn.functional.cross_entropy(pwin, ywin)
  loss = losspol + losswin
  opt.zero_grad()
  loss.backward()
  opt.step()
  return np.array([losspol.item(), losswin.item()])

def test():
  with torch.no_grad():
    model.train(False)
    xpie = test_set.pieces
    xpos = test_set.positions
    ppol, pwin = model(xpos, xpie)
    ypol = test_set.policy.reshape(-1)
    pwin = pwin.reshape(-1, 3)
    ppol = ppol.reshape(-1, 64)
    policy_loss = torch.nn.functional.cross_entropy(ppol, ypol)

    ywin = test_set.wins
    ywin = ywin.reshape(-1,1,1).reshape(-1)
    win_loss = torch.nn.functional.cross_entropy(pwin, ywin)
    return np.array([policy_loss.item(), win_loss.item()])

test()

#%%

import sys
if os.path.exists('training/model.pth') and '--load' in sys.argv:
  model.load_state_dict(torch.load('training/model.pth'))
  print('loaded model')

epochs = 100
besteval = float('inf')
for e in range(epochs):
  avg_loss = None
  try:
    for i in range(train_split//bs):
      loss = trainstep(i)
      avg_loss = loss if avg_loss is None else .95 * avg_loss + .05 * loss
      if i %10 ==0: print(f'\rTrain: {avg_loss}', end='')
  except KeyboardInterrupt: break
  print(f' TEST: {(eval:=test())}')
  if eval[0] < besteval:
    besteval = eval[0]
    torch.save(model.state_dict(), 'training/model.pth')

#%%


