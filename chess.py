from enum import Enum, auto
from dataclasses import dataclass
import numpy as np
from typing import Optional

K, Q, R, B, N, P = 1, 2, 3, 4, 5, 6
PieceChars = '.KQRBNP'

def piece_str(piece:int):
  c = PieceChars[abs(piece)]
  return c.lower() if piece < 0 else c

def str_piece(s:str):
  p = PieceChars.index(s.upper())
  return -p if s.islower() else p

class Move:
  def __init__(self, board, start:int, end:int, prom=None):
    self.board = board
    self.castles = board.castles.copy()
    self.passant = board.passant
    self.start = start
    self.end = end
    self.prom = prom
    self.target = board.data[end]

  def __repr__(self): return f'{self.start} -> {self.end}'
  def __eq__(self, other): return self.board is other.board and self.start == other.start and self.end == other.end and self.prom == other.prom

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
  def __init__(self, data:np.ndarray, castles:list[bool]=[True, True, True, True], passant=None):
    self.data = data
    self.castles = castles
    self.passant:Optional[int] = passant
  
  @staticmethod
  def empty(): return Board(np.zeros(80, dtype=np.int8))

  @staticmethod
  def __repr__(self): return '\n'.join(' '.join(piece_str(c) for c in row[:8]) for row in self.data.reshape(8,10))

  def flip(self):
    passant = self.passant and (77 - self.passant)
    
    state = -np.pad(self.data.copy()[-3::-1], (0, 2), 'constant')
    return Board(state, self.castles.copy()[::-1], passant)

  def move(self,start, end, prom:Optional[int]= None):
    move = Move(self, start, end, prom)
    assert move in self.get_moves(), f'Invalid move {move}, moves are {self.get_moves()}'
    if self.data[start] == P:
      if start%10 != end%10 and self.data[end] == 0:
        assert self.passant == end, f'Invalid passant {self.passant} {end}'
        self.data[end + S] = 0
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
    return move
  
  def unmove(self, move:Move):
    self.data[move.start] = P if move.prom else  self.data[move.end]
    self.data[move.end] = move.target
    self.passant = move.passant
    self.castles = move.castles
    if move.end == move.passant: self.data[move.end + S] = -P
  
  def get(self, pos): return self.data[pos] if onboard(pos) else None

  def get_moves(self):
    positions = np.where(self.data > 0)
    pieces = self.data[positions]
    moves = []
    for pos, piece in zip(positions[0], pieces):
      if piece == P:
        if self.get(pos + U) == 0:
          moves.append(Move(self, pos, pos + U))
          if self.get(pos + U * 2) == 0: moves.append(Move(self, pos, pos + 2*U))
        for p in [pos + U + E, pos + U + W]:
          if ((t := self.get(p)) is not None) and (t < 0 or p == self.passant): moves.append(Move(self, pos, p))
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

def start():return Board.fromstring('''
    r n b q k b n r
    p p p p p p p p
    . . . . . . . .
    . . . . . . . .
    . . . . . . . .
    . . . . . . . .
    P P P P P P P P
    R N B Q K B N R''')
  
