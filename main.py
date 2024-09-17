import flask
import flask_cors
import json
import functools, json
from enum import Enum, auto
from AI import MChandle
from absearch import handle
import sys

app = flask.Flask(__name__)
flask_cors.CORS(app, resources={r"/*": {"origins": "*"}})

from chess import Board, start

state = Board.empty()
status = "running"
confidence = 0.5


@app.route('/getstate')
def get_state():
  return json.dumps({'confidence':confidence, 'board':str(state), "status":status})

@app.route('/move', methods=['POST'])
def move():
  print("move")
  global state,status
  status = 'thinking ...'
  data = flask.request.json['move']
  if not state.move(**json.loads(data)):
    print(f'illegal move {json.loads(data)}')
    flask.abort(400)
  print(state, '\n')

  return 'ok'


handler = MChandle if '--ai' in sys.argv else handle

@app.route('/answer')
def answer():
  global state, confidence, status
  state = state.flip()
  print("thinking:")
  print(state, '\n')

  val, response = handler(state)

  confidence = val
  status = 'your turn'
  if response == 'resign':
    state = state.flip()
    status = "GAME OVER: you won"
  state.move(response.start, response.end, response.prom)
  state = state.flip()
  print(state)
  if state.isover():
    print('game over')
    status = "GAME OVER: you lost"

  return "ok"

@app.route('/reset')
def reset():
  global state, status
  status = "your turn"
  state = start()
  return 'ok'

import webbrowser
if __name__ == '__main__':
  webbrowser.open("http://localhost:8081/static/index.html")
  app.run(host='localhost', port=8081)
