#%%
from tinychess.training.model import device
import numpy as np
import torch
from dataclasses import dataclass
import sys

elo = ([a.split('=')[1] for a in sys.argv if a.startswith('--elo=')] or ['2000'])[0]

datapath = f"./dataset/moves{elo}+.npz"
data = np.load(datapath)

moves = data['moves']
wins = data['wins'][:len(moves)]
pieces = data['pieces']

policy = moves
moves = np.pad(moves, ((0,0), (1,0)))[:,:-1]
pieces = np.pad(pieces, ((0,0), (1,0)))[:,:-1]
wins = wins.reshape(-1,1).repeat(200, axis=1)

def tensor(x):return torch.tensor(x).to(device)

@dataclass
class Dataset():
  moves: torch.Tensor
  wins: torch.Tensor
  pieces: torch.Tensor
  policy: torch.Tensor
  winmask = None

  def __post_init__(self):
    if self.winmask is None:
      seq_len = self.moves.shape[1]
      winmask = torch.ones(3, seq_len, dtype=torch.bool)
      winmask[0] = (torch.arange(seq_len) % 4 == 0).logical_or(torch.arange(seq_len) % 4 == 1)
      winmask[1] = (torch.arange(seq_len) % 4 == 2).logical_or(torch.arange(seq_len) % 4 == 3)
      self.winmask = winmask.to(device)
      self.winmask = self.winmask[self.wins[:,0]]

  def __getitem__(self, i): return Dataset(self.moves[i], self.wins[i], self.pieces[i], self.policy[i])
  def __len__(self): return len(self.moves)

  def batches(self, B):
    for i in range(0, len(self), B):
      yield self[i:i+B]

data = Dataset(*map(tensor, [moves, wins, pieces, policy]))
train_split = int(len(data) * 0.8)
train_data = data[:train_split]
test_data = data[train_split:]
del data

if __name__ == '__main__':
  print(train_data.moves.shape)
  print(train_data.wins.shape)
  print(train_data.pieces.shape)
  print(train_data.policy.shape)

  print((train_data.moves[0, :10]))
  print((train_data.pieces[0, :10]))
  print((train_data.policy[0, :10]))