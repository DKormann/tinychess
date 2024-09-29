from enum import Enum, auto
from dataclasses import dataclass
import numpy as np
from typing import Optional, Union
import math

def sig(x): return 1/(math.exp(-x) + 1)

e, K, Q, R, B, N, P = 0, 1, 2, 3, 4, 5, 6

values = np.array([0, 0, 9, 5, 3, 3, 1])
PieceChars = '.KQRBNP'

def piece_str(piece:int):
  c = PieceChars[abs(piece)]
  return c.lower() if piece < 0 else c

def str_piece(s:str):
  p = PieceChars.index(s.upper())
  return -p if s.islower() else p

def postok(pos:int): return (pos//10) * 8 + pos % 10
def tokpos(tok:int): return (tok//8) * 10 + tok % 8
def mirror(pos:int): return (7-pos//10)*10 + pos%10

class Move:
  def __init__(self, piece, start:int, end:int, prom=None):
    assert prom is None or prom in [Q, R, B, N, -Q, -R, -B, -N]
    assert piece != 0
    self.piece = piece
    self.start = start
    self.end = end
    self.prom = prom 

  def __lt__(self, other): return True
  def __repr__(self): return f'{self.piece}:{self.start:02} -> {self.end:02}' +( piece_str(self.prom) if self .prom else '')
  def __eq__(self, other): return isinstance(other, Move) and self.start == other.start and self.end == other.end and (self.prom == other.prom or other.prom is None)
  def mirror(self): return Move(-self.piece, mirror(self.start), mirror(self.end), self.prom and -self.prom)

  @staticmethod
  def from_algebraic(board, alg:str):
    move = alg.strip().replace('x', '').replace('+', '').replace('#', '').replace('=R', '=Q').replace('=B', '=Q')
    res = []
    moves = board.get_moves()
    for opt in moves:
      for note in opt.algebraics():
        if note == move:
          res += [opt]

    if res == []: return None
    if len(res) > 1: return max(res, key=lambda x: (x.start%10, x.start//10))
    return res[0]


  def algebraics(self):
    def num2alg(n:int):
      col = n % 10
      row = 8 - n // 10
      return chr(ord('a') + col) + str(row)
    start = num2alg(self.start)
    end = num2alg(self.end)
    ptype = abs(self.piece)
    prep = piece_str(ptype)
    if ptype == P:
      if self.end < 10 or self.end > 70:
        assert self.prom is not None, f'Promotion needed {self}'
        return [f'{end}={piece_str(self.prom)}']
      return [end, f'{start[0]}{end}']
    if self.piece == 'K':
      if self.start - self.end == 2: return ['O-O-O']
      if self.start - self.end == -2: return ['O-O']
    return [f'{prep}{end}', f'{prep}{start[0]}{end}', f'{prep}{start[1]}{end}']

  def tokens(self): return (self.start//10)*8 + self.start%10, (self.end//10)*8 + self.end%10

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
  def __init__(self, data:np.ndarray, castles=None, passant=None, white=True):
    self.data = data
    self.castles = castles or [True, True, True, True]
    self.passant:Optional[int] = passant
    self.white = white
  
  def movefromtoks(self, *toks): return Move(self, toks[0]//8*10 + toks[0]%8, toks[1]//8*10 + toks[1]%8)
  
  @staticmethod
  def empty(): return Board(np.zeros(80, dtype=np.int8))
  def __repr__(self):  return '\n'.join(' '.join(piece_str(c) for c in row[:8]) for rn,row in enumerate(self.data.reshape(8,10)))+'\n'

  @staticmethod
  def fromstring(s:str):
    return Board(np.array([str_piece(c) for line in s.strip().split('\n') for c in (line+' . .').split() if c ]))

  def copy(self): return Board(self.data.copy(), self.castles.copy(), self.passant, self.white)

  def mirror(self):
    state = -self.data.reshape(8, 10)[::-1].reshape(80)
    castles = self.castles[2:] + self.castles[:2]
    passant = self.passant and (7-self.passant//10)*10 + self.passant%10
    return Board(state, castles, passant, self.white)

  def move(self, start, end=None, prom:Optional[int]= None):
    board = self.copy()
    if type(start) == Move:
      start,end,prom = start.start, start.end, start.prom
      # assert start.piece == board.data[start.start]
    move = Move(board.data[start], start, end, prom)
    if move not in board.get_moves(): return None
    if board.data[start] == P:
      if start%10 != end%10 and board.data[end] == 0:
        assert board.passant == end, f'Invalid passant {board.passant} {end}'
        board.data[end + S] = 0
      if end // 10 == 0: board.data[start] = prom or Q
    elif board.data[start] == K:
      board.castles[0] = False
      board.castles[1] = False
      if start - end == 2: board.data[[70, end+1]] = e, R
      if start - end == -2: board.data[[77, end-1]] = e, R
    elif board.data[start] == R:
      if start == 70: board.castles[0] = False
      if start == 77: board.castles[1] = False
    if board.data[start] == P and end - start == U * 2: board.passant = start + U
    else: board.passant = None
    board.data[end] = board.data[start]
    board.data[start] = 0
    board.white = not board.white
    return board

  def get(self, pos): return self.data[pos] if onboard(pos) else None

  def get_moves(self, only_captures = False)-> list[Move]:

    board = self if self.white else self.mirror()
    positions = np.where(board.data > 0)
    pieces = board.data[positions]

    moves = []
    captures = []
    for startpos, piece in zip(positions[0], pieces):
      if piece == P:
        if board.get(startpos + U) == 0:
          if startpos // 10 == 1: captures.extend([Move(P, startpos, startpos + U, Q), Move(P, startpos, startpos + U, N)])
          else: moves.append(Move(P, startpos, startpos + U))
          if startpos //10 == 6 and board.get(startpos + U * 2) == 0: moves.append(Move(P, startpos, startpos + 2*U))
        for endpos in [startpos + U + E, startpos + U + W]:
          if ((t := board.get(endpos)) is not None) and (t < 0 or endpos == board.passant):
            if endpos // 10 == 0: captures.extend([Move(P, startpos, endpos, Q), Move(P, startpos, endpos, N)])
            else: captures.append(Move(P, startpos, endpos))
        continue
      for d in directions[piece]:
        endpos = startpos + d
        while True:
          if not onboard(endpos) or board.data[endpos] > 0: break
          (captures if board.data[endpos] < 0 else moves).append(Move(piece, startpos, endpos))
          if board.data[endpos] < 0 or piece in [N, K]: break
          endpos += d
      if piece == K:
        board.data[startpos] = 0
        for i in range(2):
          if board.castles[i]:
            steps = list(range(startpos, startpos + (3 if i else -3) , (1 if i else -1)))
            for step in steps:
              if board.data[step] != 0: break
              if not check_safe(board.data, step): break
              if step == steps[-1]: moves.append(Move(piece, startpos, step))
        board.data[startpos] = piece
    res = captures + moves * (not only_captures)
    return res if self.white else [m.mirror() for m in res]

  def tuple(self):return (tuple(self.data), tuple(self.castles), self.passant)
  def iswon(self): return sum(self.data == -K) == 0
  def islost(self): return sum(self.data == K) == 0
  def isover(self): return self.iswon() or self.islost()

  def eval(self):
    if not sum(self.data == K): return 0
    if not sum(self.data == -K): return 1.
    myval = sum(values[self.data[np.where(self.data>0)]])
    otherval = sum(values[-self.data[np.where(self.data<0)]])
    for t, v in position_vals.items():
      myval += v[0][self.data == t].sum()
      otherval += v[1][self.data == -t].sum()
    myval += sum(self.castles[:2]) / 2
    otherval += sum(self.castles[2:]) / 2
    return sig((myval-otherval)/2)

  def start(): return Board.fromstring('''
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
    0, 0, 0, 0,  0, 0, 0, 0,
    0, 0, 0, 0,  0, 0, 0, 0,
    0, 0, 0, 0,  0, 0, 0, 0,
    0, 0, 0, 0,  0, 0, 0, 0,

    0, 0, 0, 0,  0, 0, 0, 0,
    0, 0, 0, 0,  0, 0, 0, 0,
    1, 1, 1, 1,  1, 1, 1, 1,
    4, 3, 3, 2,  1, 2, 3, 4,
  ])/2,

  N:np.array([
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 1, 1, 0, 0, 0,
    0, 0, 1, 2, 2, 1, 0, 0,
    0, 1, 2, 2, 2, 2, 1, 0,

    0, 1, 2, 2, 2, 2, 1, 0,
    0, 0, 1, 2, 2, 1, 0, 0,
    0, 0, 0, 1, 1, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
  ])/2,

  P:np.array([
    0, 0, 0, 0, 0, 0, 0, 0,
    3, 3, 4, 5, 5, 4, 3, 3,
    2, 2, 3, 4, 4, 3, 2, 2,
    1, 2, 2, 3, 3, 2, 2, 1,
    1, 1, 1, 2, 2, 1, 1, 1,
    0, 1, 1, 1, 1, 1, 1, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
  ])/2,

}


for k in list(position_vals):
  v = position_vals[k]
  position_vals[k] = np.pad(v.reshape(8,8), [(0,0),(0,2)]).flatten(),  np.pad(v[::-1].reshape(8,8), [(0,0), (0,2)]).flatten()