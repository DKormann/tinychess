from chess import Board, Move
from training.model import Model, device
import torch
import numpy as np

torch.random.manual_seed(2)
model = Model().to(device)

oo = np.inf

model.load_state_dict(torch.load('training/model.pth'))

def move2toks(piece, mv, flipped):
  def pos2tok(pos):
    if flipped: pos = 77-pos
    return (pos // 10)*8 + pos %10
  return [pos2tok(mv.start), pos2tok(mv.end)], [0, piece]

def toks2move(board, toks, flipped):
  def tok2pos(tok): 
    if flipped: tok = 63-tok
    return (tok//8)*10 + tok%8
  return Move(board, tok2pos(toks[0]), tok2pos(toks[1]))

def tensor(x): return torch.tensor(x).to(device)

class NNBot():
  def __init__(self):
    self.hist = []
    self.state = Board.start()
    self.poshist = [0]
    self.piecehist = [0]

  def handle(self, opponentmove:Move):
    piece=  self.state.data[opponentmove.start]
    pos, piece = move2toks(piece, opponentmove, False)

    self.poshist += pos
    self.piecehist += piece
    self.state.move(opponentmove)

    starts, ens = zip(*[mv.tokens() for mv in  self.state.get_moves()])


    pol, eval = model(tensor([self.poshist]), tensor([self.piecehist]))
    pol = pol[0,-1].flatten()

    for i in range(64):
      if i not in starts: pol[i] = -oo
    print(pol.softmax(-1  ).reshape(-1,8,8).int())

    plan = pol.argmax().item()
    self.poshist += [plan]
    self.piecehist += [0]

    pol, eval = model(tensor([self.poshist]), tensor([self.piecehist]))
    plan = pol.argmax(-1)[:,-1].item()

    mymmove = toks2move(self.state, [self.poshist[-1], plan], True)
    piece = self.state.data[mymmove.start]
    self.poshist += [plan]
    self.piecehist += [piece]
    self.state.move(mymmove)
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

#%%
