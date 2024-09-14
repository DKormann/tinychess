from enum import Enum, auto
from dataclasses import dataclass
import numpy as np
from typing import Optional

e, K, Q, R, B, N, P = 0, 1, 2, 3, 4, 5, 6

values = np.array([0, 10, 9, 5, 3, 3, 1])
PieceChars = '.KQRBNP'

def piece_str(piece:int):
  c = PieceChars[abs(piece)]
  return c.lower() if piece < 0 else c

def str_piece(s:str):
  p = PieceChars.index(s.upper())
  return -p if s.islower() else p

class Move:
  def __init__(self, board, start:int, end:int, prom=None):
    assert prom is None or prom in [Q, R, B, N]
    self.board = board
    self.castles = board.castles.copy()
    self.passant = board.passant
    self.start = start
    self.end = end
    self.prom = prom
    self.target = board.data[end]

  def __repr__(self): return f'{self.start:02} -> {self.end:02}' +( piece_str(self.prom) if self .prom else '')
  def __eq__(self, other): return isinstance(other, Move) and self.board is other.board\
    and self.start == other.start and self.end == other.end and (self.prom == other.prom or other.prom is None)
  def flip(self): return Move(self.board, 77-self.start, 77-self.end, self.prom)

U, S, E, W = -10, 10, 1, -1

directions = {
  K: [U, S, E, W, U+E, U+W, S+E, S+W],
  Q: [U, S, E, W, U+E, U+W, S+E, S+W],
  R: [U, S, E, W],
  B: [U+E, U+W, S+E, S+W],
  N: [2*U+E, 2*U+W, 2*E+U, 2*E+S, 2*S+E, 2*S+W, 2*W+S, 2*W+U],
}

def onboard(pos:int): return not( pos < 0 or pos % 10 > 7 or pos > 79)

def check_safe(board:np.ndarray, pos:int):
  for piece, dirs in directions.items():
    for dir in dirs:
      newpos = pos + dir
      while onboard(newpos):
        if board[newpos] == -piece: return False
        if board[newpos] != 0 or piece in [N, K]: break
        newpos += dir
  for p in [pos + U + E, pos + U + W]:
    if board[p] == -P: return False
  return True

class Board:
  def __init__(self, data:np.ndarray, passant=None):

    self.data = data
    self.castles = [True, True, True, True]
    self.passant:Optional[int] = passant
  
  @staticmethod
  def empty(): return Board(np.zeros(80, dtype=np.int8))

  def __repr__(self): return '\n'.join(' '.join(piece_str(c) for c in row[:8]) for row in self.data.reshape(8,10))

  @staticmethod
  def fromstring(s:str):
    return Board(np.array([str_piece(c) for line in s.strip().split('\n') for c in (line+' . .').split() if c ]))

  def flip(self):
    passant = self.passant and (77 - self.passant)
    state = -np.pad(self.data.copy()[-3::-1], (0, 2), 'constant')
    res = Board(state, passant)
    res.castles = self.castles.copy()[::-1]
    return res

  def move(self,start, end=None, prom:Optional[int]= None):
    if type(start) == Move:
      start,end,prom = start.start, start.end, start.prom
    move = Move(self, start, end, prom)
    if move not in self.get_moves(): return False
    if self.data[start] == P:
      if start%10 != end%10 and self.data[end] == 0:
        assert self.passant == end, f'Invalid passant {self.passant} {end}'
        self.data[end + S] = 0
      if end // 10 == 0: self.data[start] = prom or Q
    elif self.data[start] == K:
      self.castles[0] = False
      self.castles[1] = False
      if start == 74 and end == 72: self.data[[73,70]] = self.data[[70,73]]
      if start == 74 and end == 76: self.data[[75,77]] = self.data[[77,75]]
    elif self.data[start] == R:
      if start == 70: self.castles[0] = False
      if start == 77: self.castles[1] = False
    if self.data[start] == P and end - start == U * 2: self.passant = start + U
    else: self.passant = None
    self.data[end] = self.data[start]
    self.data[start] = 0
    kingpos = np.where(self.data == K)[0]
    if not check_safe(self.data, kingpos):
      self.unmove(move)
      return False
    return move
  
  def unmove(self, move:Move):
    self.data[move.start] = P if move.prom else self.data[move.end]
    self.data[move.end] = move.target
    self.passant = move.passant
    if self.castles != move.castles:

      if self.data[move.start] == K and (move.start-move.end) == -2:
        self.data[77] = R
        self.data[75] = 0
      if self.data[move.start] == K and (move.start-move.end) == 2:
        self.data[70] = R
        self.data[73] = 0
      self.castles = move.castles
    if move.end == move.passant: self.data[move.end + S] = -P
  
  def get(self, pos): return self.data[pos] if onboard(pos) else None

  def get_moves(self)-> list[Move]:
    positions = np.where(self.data > 0)
    pieces = self.data[positions]
    moves = []
    for pos, piece in zip(positions[0], pieces):
      if piece == P:
        # if pos // 10 == 1: 
        if self.get(pos + U) == 0:
          if pos // 10 == 1: moves.extend([Move(self, pos, pos + U, Q), Move(self, pos, pos + U, N)])
          else: moves.append(Move(self, pos, pos + U))
          if pos //10 == 6 and self.get(pos + U * 2) == 0: moves.append(Move(self, pos, pos + 2*U))
        for p in [pos + U + E, pos + U + W]:
          if ((t := self.get(p)) is not None) and (t < 0 or p == self.passant):
            if p // 10 == 0: moves.extend([Move(self, pos, p, Q), Move(self, pos, p, N)])
            else: moves.append(Move(self, pos, p))
        continue
      for d in directions[piece]:
        newpos = pos + d
        while True:
          if not onboard(newpos) or self.data[newpos] > 0: break
          moves.append(Move(self, pos, newpos))
          if self.data[newpos] < 0 or piece in [N, K]: break
          newpos += d
      if piece == K:
        self.data[pos] = 0
        for dir, path in enumerate([[72, 71, 73], [76, 75]]):
          for p in path:
            if not self.castles[dir] or self.data[p] != 0 or not check_safe(self.data, p): break
            if p == path[-1]: moves.append(Move(self, pos, path[0]))
        self.data[pos] = piece
    return moves
  
  def isover(self):
    for mv in self.get_moves():
      if self.move(mv):
        self.unmove(mv)
        return False
    return True

  def eval(self):
    if not sum(self.data == K): return 0
    if not sum(self.data == -K): return 1.
    myval = sum(values[self.data[np.where(self.data>0)]])
    otherval = sum(values[-self.data[np.where(self.data<0)]])
    for t, v in position_vals.items():
      myval += v[0][self.data == t].sum()
      otherval += v[1][self.data == -t].sum()
    return myval/(myval + otherval)


def start():return Board.fromstring('''
    r n b q k b n r
    p p p p p p p p
    . . . . . . . .
    . . . . . . . .
    . . . . . . . .
    . . . . . . . .
    P P P P P P P P
    R N B Q K B N R''')


position_vals = {

  K:np.array([
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,

    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    1, 1, 1, 1, 1, 1, 1, 1,
    4, 3, 2, 1, 1, 2, 3, 4,
  ]),

  N:np.array([
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 1, 1, 0, 0, 0,
    0, 0, 1, 2, 2, 1, 0, 0,
    0, 1, 2, 2, 2, 2, 1, 0,

    0, 1, 2, 2, 2, 2, 1, 0,
    0, 0, 1, 2, 2, 1, 0, 0,
    0, 0, 0, 1, 1, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
  ]),

  P:np.array([
    7, 7, 7, 7, 7, 7, 7, 7,
    6, 6, 6, 6, 6, 6, 6, 6,
    5, 5, 5, 5, 5, 5, 5, 5,
    4, 4, 4, 4, 4, 4, 4, 4,

    3, 3, 3, 3, 3, 3, 3, 3,
    2, 2, 2, 2, 2, 2, 2, 2,
    1, 1, 1, 1, 1, 1, 1, 1,
    0, 0, 0, 0, 0, 0, 0, 0,
  ])

}


for k in list(position_vals):
  v = position_vals[k]
  position_vals[k] = np.pad(v.reshape(8,8), [(0,0),(0,2)]).flatten(),  np.pad(v[::-1].reshape(8,8), [(0,0), (0,2)]).flatten()