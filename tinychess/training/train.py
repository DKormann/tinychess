
#%%
import sys
sys.argv += ['--clean']
sys.argv += ['--elo=2000']
from tinychess.training.model import Model, device, pretrained
import os
from tinychess.training.loaddata import train_data, test_data, Dataset
from collections import namedtuple
import torch
import numpy as np

#%%
model = Model().to(device)
oo = np.inf

besteval = oo

import json
if os.path.exists('tinychess/training/model.pth') and '--clean' not in sys.argv:
  model = pretrained()
  print('loaded model')

  if os.path.exists('tinychess/training/eval.json'):
    eval = json.load(open('tinychess/training/eval.json'))
    besteval = eval['test'][0]
    print(f'Loaded best eval: {besteval}')

opt = torch.optim.Adam(model.parameters(), lr=1e-3)
# %%
bs = 20

def lossfn(data:Dataset):
  ppol, pwin = model(data.moves, data.pieces)
  assert data.winmask.dtype == torch.bool, f'{data.winmask.dtype}'
  ppol = ppol[data.winmask]
  policy = data.policy[data.winmask]

  pol_loss = torch.nn.functional.cross_entropy(ppol, policy)
  win_loss = torch.nn.functional.cross_entropy(pwin.reshape(-1, 3), data.wins.reshape(-1))
  return pol_loss, win_loss

def trainstep(data):
  model.train(True)
  pol_loss, win_loss = lossfn(data)
  loss = pol_loss + win_loss
  opt.zero_grad()
  loss.backward()
  opt.step()
  return np.array([pol_loss.item(), win_loss.item()])

def test():
  model.eval()
  with torch.no_grad():
    pol_loss, win_loss = lossfn(test_data)
    return np.array([pol_loss.item(), win_loss.item()])


test()
#%%
import json
import numpy as np

epochs = 100

for e in range(epochs):
  avg_loss = None
  try:
    # for i in range(train_split//bs):
    for i, batch in enumerate(train_data.batches(bs)):
      loss = trainstep(batch)
      avg_loss = loss if avg_loss is None else .95 * avg_loss + .05 * loss
      if i %10 ==0: print(f'\rTrain: {avg_loss}', end='')
  except KeyboardInterrupt: break

  print(f' TEST: {(eval:=test())} EXP: {np.exp(eval)}')
  if eval[0] < besteval:
    besteval = eval[0]
    torch.save(model.state_dict(), 'tinychess/training/model.pth')
    json.dump({'train':avg_loss.tolist(), 'test':eval.tolist()}, open('tinychess/training/eval.json', 'w'), indent=2)
