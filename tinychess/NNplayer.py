from tinychess.chess import Board, Move, tokpos
from tinychess.training.model import pretrained, device
import torch
import numpy as np

model = pretrained()
model.eval()

oo = np.inf
def tensor(x): return torch.tensor(x, device=device)
class NNBot():
  def __init__(self):
    self.board = Board.start()
    self.poshist = [0]
    self.piecehist = [0]

  def handle(self, move:Move):
    self.poshist.extend(move.tokens())
    self.piecehist.extend([0, move.prom or move.piece])
    self.board = self.board.move(move)

    def sample(options:list[int]):
      with torch.no_grad():
        plan, eval = model(tensor([self.poshist]), tensor([self.piecehist]))
        for i in range(64):
          if i not in options: plan[0, -1, i] = -oo
        ev = (np.array([0., 1., .5]) * eval[0, -1].softmax(-1).cpu().numpy()).sum()
        dec = plan[0,-1].argmax(-1).item()
        assert dec in options
        return dec, ev

    mvs = self.board.get_moves()
    options = [m.tokens() for m in mvs]
    starts = [o[0] for o in options]
    start, _ = sample(starts)
    options = [o for o in options if o[0] == start]
    self.poshist.append(start)
    self.piecehist.append(0)
    end, ev = sample([o[1] for o in options])
    chosenmv = [m for m in mvs if list(m.tokens()) == [start, end]][0]
    self.poshist.append(end)
    self.piecehist.append(chosenmv.prom or chosenmv.piece)
    self.board = self.board.move(chosenmv)
    return ev, chosenmv



if __name__ == '__main__':
  bot = NNBot()

  def play(m):
    print(f"playing {m}")
    ev, mv = bot.handle(m)
    print(f"eval: {ev}")
    print(bot.board)
    return mv
  
  play(Move.from_algebraic(bot.board, 'd4'))
  play(Move.from_algebraic(bot.board, 'e3'))
  