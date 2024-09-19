#%%
from chess import Board, Move
# from AI import handle

from chess import Q, K, N, P, R
from chess import Board, start, piece_str
# from AI import MCTSNode, MChandle

#%%


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
      rep = f'{piece_str(board.data[mv.start])}:{mv.start}->{piece_str(board.data[mv.end]).capitalize()}:{mv.end}'

      board.move(mv)


      print(rep)
      print(board)

      nums.append(rep)

      flipped = not flipped
      board = board.flip()

    if mv is not None: f.write(game.split(',')[0]+ ', '+ ', '.join(nums) + '\n')
    break



