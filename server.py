
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

from tinychess.chess import Board

state = Board.empty()
status = "running"
confidence = 0.5
hist = []

@app.route('/getstate')
def get_state():

  return json.dumps({'confidence':confidence, 'board':str(state.flip() if state.flipped else state), "status":status, "history":list(map(str, hist))})

@app.route('/move', methods=['POST'])
def move():
  global state,status
  status = 'thinking ...'
  data = flask.request.json['move']
  if not (mv := state.move(**json.loads(data))):
    print(f'illegal move {json.loads(data)}')
    flask.abort(400)
  else: hist.append(mv)
  return 'ok'


handler = MChandle if '--ai' in sys.argv else handle
@app.route('/answer')
def answer():
  global state, confidence, status
  val, response = handler(state)
  confidence = val
  status = 'your turn'
  print(f'confidence: {val}, response: {response}')
  if response == 'resign': status = "GAME OVER: you won"
  mv = state.move(response.start, response.end, response.prom)
  if state.islost():
    print('game over')
    status = "GAME OVER: you lost"
  hist.append(mv)
  return "ok"

@app.route('/reset')
def reset():
  global state, status, hist
  status = "your turn"
  state = Board.start()
  hist=  []
  return 'ok'

import webbrowser
if __name__ == '__main__':
  webbrowser.open("http://localhost:8081/static/index.html")
  app.run(host='localhost', port=8081)
