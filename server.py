import flask
import flask_cors
import json
import functools, json
from enum import Enum, auto
from tinychess.AI import MChandle
from tinychess.absearch import handle

import sys

app = flask.Flask(__name__)
flask_cors.CORS(app, resources={r"/*": {"origins": "*"}})

from tinychess.chess import Board, Move

state = Board.empty()
status = "running"
confidence = 0.5
hist = []

@app.route('/getstate')
def get_state():
  return json.dumps({'confidence':confidence, 'board':str(state), "status":status, "history":list(map(str, hist))})

@app.route('/move', methods=['POST'])
def move():
  global state, status
  status = 'thinking ...'
  data = json.loads(flask.request.json['move'])
  move = Move(state.data[int(data['start'])], int(data['start']), int(data['end']), data['prom'])
  print(move)
  if not (newstate := state.move(move)):
    print(f'illegal move')
    flask.abort(400)
  else: hist.append(move)
  state = newstate
  if state.isover():
    print('game over')
    status = "GAME OVER: you won"
  return 'ok'

@app.route('/answer')
def answer():
  print(f'ANSWER {hist}')
  global state, confidence, status
  if status.startswith('GAME OVER'): return 'ok'
  val, response = handler(state)
  confidence = val
  status = 'your turn'
  print(f'confidence: {val}, response: {response}')
  if response == 'resign': status = "GAME OVER: you won"
  state = state.move(response.start, response.end, response.prom)
  if state.isover():
    print('game over')
    status = "GAME OVER: you lost"
  hist.append(response)
  return "ok"

@app.route('/reset')
def reset():
  print("RESET")
  global state, status, hist, handler

  hist=  []
  handler = MChandle if '--ai' in sys.argv else handle
  if '--nn' in sys.argv:
    from tinychess.NNplayer import NNBot
    bot = NNBot()
    handler = lambda state: bot.handle(hist[-1])

  status = "your turn"
  state = Board.start()
  return 'ok'

import webbrowser
if __name__ == '__main__':
  webbrowser.open("http://localhost:8081/static/index.html")
  app.run(host='localhost', port=8081)
