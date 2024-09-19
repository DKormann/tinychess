#%%
from chess import Board, Move
# from AI import handle

from chess import Q, K, N, P, R
from chess import Board, start
# from AI import MCTSNode, MChandle

#%%
moves = 'c4 e5 Nc3 Bc5 g3 Nc6 Bg2 Nf6 Nf3 b6 Nxe5 Bb7 Nd3 Bd4 O-O Bxc3 dxc3 O-O Nb4 Re8 Nxc6 Bxc6 Bxc6 dxc6 Be3 Ng4 Qxd8 Raxd8 Rad1 Nxe3 fxe3 Rxd1 Rxd1 Rxe3'.split()

# moves = 'e4 c5 Nf3 d6 d4 cxd4 Nxd4 Nf6 Nc3 g6 Be3 Bg7 f3 O-O Qd2 Nc6 O-O-O d5 exd5 Nxd5 Nxc6 bxc6 Nxd5 cxd5 Qxd5 Qc7 Qc5 Qb7 b3 Bf5 Bd3 Rac8 Qa3 Bxd3 Rxd3 Qc7 c4 Qe5 Kc2 Rfd8 Rhd1 Rxd3 Rxd3 Rc6 Rd8+ Bf8 Qxa7 Rd6 Rxd6 exd6 Qd4 Qf5+ Qd3 Qf6 Bd4 Qf5 Qxf5 gxf5 a4 Bg7 Bxg7 Kxg7 a5 f4 a6 Kf8'.split()

with open('dataset/highrated.csv') as f:
  games = f.readlines()[1:]


games[0]
#%%


with open('dataset/highrated.nums', 'w') as f:
  for i,game in enumerate(games[:]):
    moves = game.split(',')[1].split()
    nums = []

    board = start()
    flipped = False
    for move in moves:
      mv = Move.from_algebraic(board, move, flipped)

      if mv is None:
        print('Invalid move:', move, 'in game', i)
        break
      board.move(mv)
      nums.append(str(mv))
      flipped = not flipped
      board = board.flip()
    if mv is not None: f.write(game.split(',')[0]+ ', '+ ', '.join(nums) + '\n')



