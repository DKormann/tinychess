import flask
import flask_cors
import json
import functools
from enum import Enum, auto

app = flask.Flask(__name__)
flask_cors.CORS(app, resources={r"/*": {"origins": "*"}})

import numpy as np
o = 0
k, q, r, b, n, p = 1, 2, 3, 4, 5, 6
_k, _r, _p = 7, 8, 9
K, Q, R, B, N, P = 10, 11, 12, 13, 14, 15
_K, _R, _P = 16, 17, 18

def piece_name(piece):
  return '. k q r b n p _k _r _p K Q R B N P _K _R _P'.split()[piece]

black = 0
white = 1

def is_white(piece): return piece >= 10
def get_type(piece):
  if piece == o: return None
  if piece > 9 : piece -= 9
  if piece == _k: return k
  if piece == _r: return r
  if piece == _p: return p
  return piece

def make_piece(white, type, special:False):
  if special:
    if type == k: type = _k
    if type == r: type = _r
    if type == p: type = _p
  return type + 9 if white else type

def get_piece(white, type): return type if white else type + 9

def get_line(state, pos, dir):
  while True:
    pos = pos + dir
    if not legalpos(pos): return
    piece = state[pos[0]][pos[1]]
    yield pos, piece

def legalpos(pos): return pos[0] > -1 and pos[0] < 8 and pos[1] > -1 and pos[1] < 8

piece_dirs = {
  r: [(1, 0), (-1, 0), (0, 1), (0, -1)],
  b: [(1, 1), (-1, 1), (1, -1), (-1, -1)],
  n: [(2, 1), (-2, 1), (2, -1), (-2, -1), (1, 2), (-1, 2), (1, -2), (-1, -2)],
  k: [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
}

def check_safe(state, pos):
  pos = np.array(pos)
  for v in [[-1,-1], [-1,1]]:
    loc = pos + v
    if not legalpos(loc): continue
    if state[loc[0]][loc[1]] in [p, _p]:
      print("unsafe pawn")
      return False

  for threat in [[r, _r, q], [b, q], [n], [k]]:
    for dir in piece_dirs[threat[0]]:
      for targetpos,targetpiece in get_line(state, pos, dir):
        if targetpiece == o or targetpiece == K or targetpiece == _K: continue
        if targetpiece  in threat:
          print(f'unsafe {piece_name(targetpiece)} on {targetpos}')
          return False
        break

class State:
  start_pos = np.array(
    [[r, n, b, q, k, b, n, r],
    [p, p, p, p, p, p, p, p],
    [o, o, o, o, o, o, o, o],
    [o, o, o, o, o, o, o, o],
    [o, o, o, o, o, o, o, o],
    [o, o, o, o, o, o, o, o],
    [P, P, P, P, P, P, P, P],
    [R, N, B, Q, K, B, N, R]], dtype=np.int8)

  def __init__(self, data:np.ndarray, turn=0):
    self.data = data
    self.turn = turn
  
  def start(): return State(State.start_pos)
  def copy(self): return State(self.data.copy(), self.turn)

  def check_move(self, move):
    return (np.array([move]) == self.moves).all((1,2)).any()

  def move(self, start, end):
    assert self.check_move((start, end)), f'Invalid move {start} -> {end} \n{self.moves}\n{self}'
    self.moves
    res = self.copy()
    piece = res.data[start[0]][start[1]]
    res.data[start[0]][start[1]] = o
    white = is_white(piece)
    type = get_type(piece)
    special = False
    if type == k or type == r: special = True
    if type == p:
      if abs (start[0] - end[0]) > 1: special = True
      if end[0] == 0 or end[0] == 7: type = q
      if start[1] != end[1] and res.data[end[0]][end[1]] == o: res.data[start[0]][end[1]] = o

    piece = make_piece(white, type, special)
    res.data[end[0]][end[1]] = piece
    res.turn += 1
    return res

  @functools.cached_property
  def moves(self):
    mover = 1 - (self.turn % 2)
    moves = []
    state = self.data
    if mover == black:
      state = state.copy()[range(7, -1, -1)] + 9
      state[state == 9] = 0
      state[state >= 19] -= 18

    my_pieces = state > 9
    positions = np.where(my_pieces)
    pieces = state[positions]

    for piece,pos in zip(pieces, np.array(positions).T):
      if piece == P or piece == _P:
        if state[pos[0] -1][pos[1]] == o: moves.append((pos, (pos[0] - 1, pos[1])))
        if pos[0] == 6 and state[5][pos[1]] == o and state[4][pos[1]] == o:
          moves.append((pos, (4, pos[1])))
        for targetpos in [(pos[0] - 1, pos[1] + 1), (pos[0] - 1, pos[1] - 1)]:
          if not legalpos(targetpos): continue
          targetpiece = state[targetpos[0]][targetpos[1]]
          if not is_white(targetpiece): moves.append((pos, targetpos))
        for passantes in [(pos[0], pos[1] + 1), (pos[0], pos[1] - 1)]:
          if not legalpos(passantes): continue
          targetpiece = state[passantes[0]][passantes[1]]
          if targetpiece == _p and state[passantes[0] - 1][passantes[1]] == o:
            moves.append((pos, (passantes[0] - 1, passantes[1])))

      dirs = []
      if piece == R or piece == _R: dirs = piece_dirs[r]
      if piece == B: dirs = piece_dirs[b]
      if piece == Q or piece == K or piece == _K: dirs = piece_dirs[r] + piece_dirs[b]
      if piece == N: dirs = piece_dirs[n]


      if piece in [R, _R, B, Q]:
        for dir in dirs:
          for targetpos,targetpiece in get_line(state, pos, dir):
            if targetpiece == o: moves.append((pos, targetpos))
            else:
              if not is_white(targetpiece): moves.append((pos, targetpos))
              break
      else:
        for dir in dirs:
          targetpos = pos + dir
          if not legalpos(targetpos): continue
          targetpiece = state[targetpos[0]][targetpos[1]]
          if targetpiece == o or not is_white(targetpiece): 
            if piece == K or piece == _K:
              if not check_safe(state, targetpos): continue
            moves.append((pos, targetpos))

    if mover == black: moves = [((7 - move[0][0], move[0][1]), (7 - move[1][0], move[1][1])) for move in moves]
    return np.array(moves)
  
  def __str__(self):
    res = f'-----[turn {self.turn:02}]-----\n'
    for row in self.data:
      res += '| '
      for piece in row: res += piece_name(piece)[-1] + ' '
      res += '|\n'
    res += '-' * 19
    return res

  def from_str(s:str):
    data = [['. k q r b n p _k _r _p K Q R B N P _K _R _P'.split().index(piece) for piece in line.split()] for line in s.split('\n')]
    return State(np.array(data, dtype=np.int8))
  
  def __eq__(self, other): return (self.data == other.data).all() and self.turn == other.turn


board = State.start()

@app.route('/getstate')
def get_state(): return flask.jsonify(board.data.tolist())


@app.route('/move', methods=['POST'])
def move():
  global board
  move = json.loads(flask.request.json['move'])
  board = board.move(*move)
  return 'ok'

@app.route('/reset')
def reset():
  global board
  board = State.start()
  return 'ok'

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8081)
