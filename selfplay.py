

from chess import Board, start
import json
from AI import MChandle, MCTSNode

import random


board = start()
root = MCTSNode()


for step in range(100):
  for i in range(2000):
    root.expand(board, c = 0.2)
  # lst = sorted([(nd, mv) for mv, nd in root.children])
  # if random.random() > 0.2: nd,mv = lst[-1]
  # else: nd,mv = lst[-2]
  nd, mv = max([(nd, mv) for mv, nd in root.children])
  
  root = nd
  board.move(mv)
  if step%2==0:print(board)

  board = board.flip()

  if step%2==1:print(board)
  
  




