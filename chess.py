from enum import Enum, auto
from dataclasses import dataclass
import numpy as np
import functools
from typing import Optional

class Fig(Enum):
  King = auto()
  Queen = auto()
  Rook = auto()
  Bishop = auto()
  Knight = auto()
  Pawn = auto()
  def __str__(self): return self.name

class Color(Enum):
  Black = auto()
  White = auto()

  def __str__(self): return self.name

@dataclass
class Piece:
  color: Color
  type: Fig

  @staticmethod
  def from_num(num:int):
    if num == 0: return None
    color = Color.White if num > 0 else Color.Black
    num = abs(num)
    t = Fig(num)
    return Piece(color, t)

  def num(self): return self.type.value if self.color == Color.White else -self.type.value
  def __str__(self): return f'<{self.color} {self.type}>'
  def char(self):
    c = self.type.name[0] if self.type != Fig.Knight else 'N'
    return c.lower() if self.color == Color.Black else c

  def from_char(char:str):
    color = Color.Black if char.islower() else Color.White
    return Piece(color, Fig('KQRBNP'.index(char.upper())+1))

def pos2code(pos): return str((pos // 10, pos % 10))

class Move:
  def __init__(self, board, start:int, end:int, prom:Fig=None):
    self.board = board
    self.castles = board.castles.copy()
    self.passant = board.passant
    self.start = start
    self.end = end
    self.prom = prom
    self.target = board.data[end]
  def __repr__(self): return f'{pos2code(self.start)} -> {pos2code(self.end)}'

  def __eq__(self, other): return self.board is other.board and self.start == other.start and self.end == other.end and self.prom == other.prom



@dataclass
class Step:
  pos: int
  before: Piece
  after: Piece

N = -10
S = 10
E = 1
W = -1

directions = {
  Fig.King.value: [N, S, E, W, N+E, N+W, S+E, S+W],
  Fig.Queen.value: [N, S, E, W, N+E, N+W, S+E, S+W],
  Fig.Rook.value: [N, S, E, W],
  Fig.Bishop.value: [N+E, N+W, S+E, S+W],
  Fig.Knight.value: [2*N+E, 2*N+W, 2*E+N, 2*E+S, 2*S+E, 2*S+W, 2*W+S, 2*W+N],
}

def onboard(pos:int):
  if pos < 0: return False
  if pos % 10 > 7: return False
  if pos > 79: return False
  return True

class Board:
  def __init__(self, data:np.ndarray, castles:list[bool]=[True, True, True, True], passant=None):
    self.data = data
    self.castles = castles
    self.passant:Optional[int] = passant
  
  @staticmethod
  def empty(): return Board(np.zeros(N, dtype=np.int8))

  @staticmethod
  def fromstring(s:str):
    return Board(np.array([0 if c == '.' else Piece.from_char(c).num() for line in s.strip().split('\n') for c in (line+' . .').split() if c ]))
  def __repr__(self): return '=================\n|'+ '|\n|'.join(' '.join(p.char() if (p:=Piece.from_num(c)) else '.' for c in row[:8]) for row in self.data.reshape(8,10)) + '|\n================='

  def flip(self):
    passant = self.passant and (77 - self.passant)
    
    state = -np.pad(self.data.copy()[-3::-1], (0, 2), 'constant')
    return Board(state, self.castles.copy()[::-1], passant)

  def move(self,start, end, prom:Optional[Fig]= None):
    move = Move(self, start, end, prom)
    assert move in self.get_moves(), f'Invalid move {move}, moves are {self.get_moves()}'
    if self.data[start] == Fig.Pawn.value:
      if start%10 != end%10 and self.data[end] == 0:
        assert self.passant == end, f'Invalid passant {self.passant} {end}'
        self.data[end + S] = 0
    if self.data[start] == Fig.Pawn.value and end - start == N * 2: self.passant = start + N
    else: self.passant = None
    self.data[end] = self.data[start]
    self.data[start] = 0
  
  def get(self, pos): return self.data[pos] if onboard(pos) else None

  def get_moves(self):
    positions = np.where(self.data > 0)
    pieces = self.data[positions]
    moves = []
    for pos, piece in zip(positions[0], pieces):
      if piece == Fig.Pawn.value:
        if self.get(pos + N) == 0:
          moves.append(Move(self, pos, pos + N))
          if self.get(pos + N * 2) == 0: moves.append(Move(self, pos, pos + 2*N))
        for p in [pos + N + E, pos + N + W]:
          if ((t := self.get(p)) is not None) and (t < 0 or p == self.passant): moves.append(Move(self, pos, p))

        continue
      for d in directions[piece]:
        newpos = pos + d
        while True:
          if not onboard(newpos): break
          if self.data[newpos] > 0: break
          moves.append(Move(self, pos, newpos))
          if self.data[newpos] < 0: break
          if piece in [Fig.Knight.value, Fig.King.value]: break
          newpos += d
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
  
