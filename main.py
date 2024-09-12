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
    if pos[0] < 0 or pos[0] > 7 or pos[1] < 0 or pos[1] > 7: return
    piece = state[pos[0]][pos[1]]
    yield pos, piece
    if piece != o: return

def legalpos(pos): return pos[0] > -1 and pos[0] < 8 and pos[1] > -1 and pos[1] < 8

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
      state = state.copy()[range(7, -1, -1)]
      state = state + 9
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
      longrange = False
      if piece == R or piece == _R:
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        longrange = True
      if piece == B:
        dirs = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
        longrange = True
      if piece == Q:
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
        longrange = True
      if piece == N: dirs = [(2, 1), (-2, 1), (2, -1), (-2, -1), (1, 2), (-1, 2), (1, -2), (-1, -2)]
      if piece == K or piece == _K: dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
        
      if longrange:
        for dir in dirs:
          for targetpos,targetpiece in get_line(state, pos, dir):
            if targetpiece == o: moves.append((pos, targetpos))
            else:
              if not is_white(targetpiece): moves.append((pos, targetpos))
              break
      else:
        for dir in dirs:
          targetpos = pos + dir
          if not legalpos(targetpos):
            print(piece_name(piece), 'illegal', targetpos)
            continue
          targetpiece = state[targetpos[0]][targetpos[1]]
          if targetpiece == o or not is_white(targetpiece): moves.append((pos, targetpos))
      

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
