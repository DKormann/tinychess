from chess import Board, Move
from training.model import Model, device
import torch
import numpy as np

torch.random.manual_seed(2)
model = Model().to(device)

oo = np.inf

model.load_state_dict(torch.load('tinychess/training/model.pth'))
def tensor(x): return torch.tensor(x).to(device)

class NNBot():
  def __init__(self):
    self.hist = []
    self.state = Board.start()
    self.poshist = [0]
    self.piecehist = [0]

  def pospred(self, options:list):
    pol, eval = model(tensor([self.poshist]), tensor([self.piecehist]))
    res = pol[0,-1]
    for i in range(64):
      if i not in options: res[i] = -oo
    return res.argmax().item()

  def handle(self, opponentmove:Move):
    piece=  self.state.data[opponentmove.start]
    pos = opponentmove.flip().tokens()

    self.poshist += pos
    self.piecehist += [0, piece]
    self.state.move(opponentmove)

    starts, ens = zip(*[mv.tokens() for mv in  self.state.get_moves()])
    plan = self.pospred(starts)
    self.poshist += [plan]
    self.piecehist += [0]
    plan = self.pospred(ens)
    mymmove = self.state.movefromtoks([self.poshist[-1], plan])
    piece = self.state.data[mymmove.start]
    self.state.move(mymmove)
    self.poshist += [plan]
    self.piecehist += [piece]
    return mymmove

#%%
bot = NNBot()
board = Board.start()

def playmove(start,end):
  global board
  mv = Move(board, start, end)
  assert board.move(mv), f'move not possible {mv}'
  print(board)
  resp = bot.handle(mv)
  assert board.move(resp), f'bot illegal move {resp}'
  print(board)

playmove(64,44)
playmove(65,55)
playmove(63,53)
playmove(72,36)
playmove(36,14)

#%%
