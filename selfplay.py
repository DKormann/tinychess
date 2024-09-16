

from chess import Board, start
import json
from bot import MChandle



for match in range(1):
  hist = []
  board = start()
  for t in range (100):

    eval, move = MChandle(board, 1000)

    hist.append((str(board),list(board.castles),board.passant and float(board.passant),eval if eval !='placeholder' else 0 ))

    if not board.move(move): break
    if t%2: 
      print(match, t)
      print(board)

    if move == 'placeholder': break
    if board.isover(): break
    board = board.flip()

  json.dump(hist, open(f'game_{match}.json', 'w'))

