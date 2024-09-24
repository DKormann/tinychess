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

class Move:
  @staticmethod
  def from_algebraic(board, alg:str):
    move = alg.strip().replace('x', '').replace('+', '').replace('#', '').replace('=R', '=Q').replace('=B', '=Q')
    res = []
    moves = board.get_moves()
    for opt in moves:
      for note in opt.algebraics(board.flipped):
        if note == move:
          res += [opt]

    # assert res != [], f'Invalid move: {alg} {res}'
    if res == []: return None
    if len(res) > 1:
      print(board.flipped)
      return max(res, key=lambda x: ((x.start%10, x.start//10) if not board.flipped else (x.start//10, x.start%10)))
    return res[0]

  def algebraics(self, flipped:bool):
    def num2alg(n:int):
      n = 77 - n if flipped else n
      col = n % 10
      row = 8 - n // 10
      res = chr(ord('a') + col) + str(row)
      return res
    piece = piece_str(self.board.data[self.start])
    start = num2alg(self.start)
    end = num2alg(self.end)
    if piece == 'P':
      if self.end < 10: return [f'{end}={piece_str(self.prom)}']
      return [end, f'{start[0]}{end}']
    if piece == 'K':
      if self.start - self.end == 2: return ['O-O' if flipped else 'O-O-O']
      if self.start - self.end == -2: return ['O-O-O' if flipped else 'O-O']
    return [f'{piece}{end}', f'{piece}{start[0]}{end}', f'{piece}{start[1]}{end}']

  def tokens(self):
    mv = self.flip() if self.board.flipped else self
    return (mv.start//10)*8 + mv.start%10, (mv.end//10)*8 + mv.end%10

  def __init__(self, board, start:int, end:int, prom=None):
    assert prom is None or prom in [Q, R, B, N]
    self.board = board
    self.castles = board.castles.copy()
    self.passant = board.passant
    self.start = start
    self.end = end
    self.prom = prom
    self.target = board.data[end]
  def __lt__(self, other): return True
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
  def __init__(self, data:np.ndarray, passant=None, flipped=False):
    self.data = data
    self.castles = [True, True, True, True]
    self.passant:Optional[int] = passant
    self.flipped = flipped
  
  def movefromtoks(self, *toks):
    mv = Move(self, toks[0]//8*10 + toks[0]%8, toks[1]//8*10 + toks[1]%8)
    return mv.flip() if self.flipped else mv
  
  @staticmethod
  def empty(): return Board(np.zeros(80, dtype=np.int8))

  def __repr__(self):  return '\n'.join(' '.join(piece_str(c) for c in row[:8]) for rn,row in enumerate(self.data.reshape(8,10)))+'\n'

  @staticmethod
  def fromstring(s:str):
    return Board(np.array([str_piece(c) for line in s.strip().split('\n') for c in (line+' . .').split() if c ]))

  def flip(self, inplace=False):
    passant = self.passant and (77 - self.passant)
    state = -np.pad(self.data.copy()[-3::-1], (0, 2), 'constant')
    res = Board(state, passant)
    res.castles = self.castles.copy()[::-1]
    res.flipped = not self.flipped
    if inplace: self.data, self.castles, self.passant, self.flipped = res.data, res.castles, res.passant, res.flipped
    return None if inplace else res

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
      if start - end == 2: self.data[[70, end+1]] = e, R
      if start - end == -2: self.data[[77, end-1]] = e, R
    elif self.data[start] == R:
      if start == 70: self.castles[0] = False
      if start == 77: self.castles[1] = False
    if self.data[start] == P and end - start == U * 2: self.passant = start + U
    else: self.passant = None
    self.data[end] = self.data[start]
    self.data[start] = 0
    self.flip(inplace=True)
    return move
  
  def unmove(self, move:Move):
    self.flip(inplace=True)
    self.data[move.start] = P if move.prom else self.data[move.end]
    self.data[move.end] = move.target
    self.passant = move.passant
    if self.castles != move.castles:
      if self.data[move.start] == K and (move.start-move.end) == -2:
        self.data[77] = R
        self.data[move.start+1] = 0
      if self.data[move.start] == K and (move.start-move.end) == 2:
        self.data[70] = R
        self.data[move.start-1] = 0
      self.castles = move.castles
    if move.end == move.passant: self.data[move.end + S] = -P
  
  def get(self, pos): return self.data[pos] if onboard(pos) else None

  def get_moves(self, only_captures = False)-> list[Move]:
    positions = np.where(self.data > 0)
    pieces = self.data[positions]
    moves = []
    captures = []
    for startpos, piece in zip(positions[0], pieces):
      if piece == P:
        # if pos // 10 == 1: 
        if self.get(startpos + U) == 0:
          if startpos // 10 == 1: captures.extend([Move(self, startpos, startpos + U, Q), Move(self, startpos, startpos + U, N)])
          else: moves.append(Move(self, startpos, startpos + U))
          if startpos //10 == 6 and self.get(startpos + U * 2) == 0: moves.append(Move(self, startpos, startpos + 2*U))
        for endpos in [startpos + U + E, startpos + U + W]:
          if ((t := self.get(endpos)) is not None) and (t < 0 or endpos == self.passant):
            if endpos // 10 == 0: captures.extend([Move(self, startpos, endpos, Q), Move(self, startpos, endpos, N)])
            else: moves.append(Move(self, startpos, endpos))
        continue
      for d in directions[piece]:
        endpos = startpos + d
        while True:
          if not onboard(endpos) or self.data[endpos] > 0: break
          (captures if self.data[endpos] < 0 else moves).append(Move(self, startpos, endpos))
          if self.data[endpos] < 0 or piece in [N, K]: break
          endpos += d
      if piece == K:
        self.data[startpos] = 0
        for i in range(2):
          if self.castles[i]:
            steps = list(range(startpos, startpos + (3 if i else -3) , (1 if i else -1)))
            for step in steps:
              if self.data[step] != 0: break
              if not check_safe(self.data, step): break
              if step == steps[-1]: moves.append(Move(self, startpos, step))
        self.data[startpos] = piece
    return captures + moves * (not only_captures)

  def tuple(self):return (tuple(self.data), tuple(self.castles), self.passant)
  
  def iswon(self): return sum(self.data == -K) == 0
  def islost(self): return sum(self.data == K) == 0

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