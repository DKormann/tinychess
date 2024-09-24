from tinychess.chess import Board, Move
from tinychess.training.model import pretrained, device
import torch
import numpy as np

torch.random.manual_seed(2)

model = pretrained().to(device)
model.eval()



oo = np.inf

def tensor(x): return torch.tensor(x, device=device)

class NNBot():
  def __init__(self):
    self.board = Board.start()
    self.poshist = [0]
    self.piecehist = [0]

  def handle(self, move:Move):
    assert self.board.move(move)
    self.poshist.extend(move.tokens())
    self.piecehist.extend([0, self.board.data[move.start]])

    def sample(options:list[int]):
      with torch.no_grad():
        plan, eval = model(tensor([self.poshist]), tensor([self.piecehist]))
        for i in range(64):
          if i not in options: plan[0, -1, i] = -oo

        ev = eval[0, -1].softmax(-1).cpu().numpy()
        print(ev)
        ev = (np.array([0., 0.5, 1.]) * ev).sum()
        dec = plan[0,-1].argmax(-1).item()
        assert dec in options
        return dec, 1-ev

    options = [m.tokens() for m in self.board.get_moves()]
    starts = [o[0] for o in options]
    start, _ = sample(starts)
    self.poshist.append(start)
    self.piecehist.append(0)
    end, ev = sample([o[1] for o in options if o[0] == start])
    self.poshist.append(end)
    self.piecehist.append(self.board.data[start])
    mv = self.board.movefromtoks(start, end)
    assert self.board.move(mv)
    return ev, mv




if __name__ == '__main__':

  bot = NNBot()
  for i in range(10):  
    print(bot.handle(bot.board.get_moves()[0]))
    print(bot.board)