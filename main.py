import flask
import flask_cors
import json
import functools, json
from enum import Enum, auto

app = flask.Flask(__name__)
flask_cors.CORS(app, resources={r"/*": {"origins": "*"}})

from chess import Board, start

state = Board.empty()

from bot import handle

@app.route('/getstate')
def get_state():
  return str(state)

@app.route('/move', methods=['POST'])
def move():
  global state
  data = flask.request.json['move']
  if not state.move(**json.loads(data)):
    print(f'illegal move {json.loads(data)}')
    flask.abort(400)

  print(state, '\n')
  return 'ok'

@app.route('/answer')
def answer():
  global state
  state = state.flip()
  print("thinking:")
  print(state, '\n')
  response = handle(state, 4)
  if response == 'placeholder': return "GAME OVER: you won"
  state.move(response.start, response.end, response.prom)
  state = state.flip()
  if state.isover(): return "GAME OVER: you lost"
  print(state)
  return str(state)

@app.route('/reset')
def reset():
  global state
  state = start()
  return 'ok'

import webbrowser
if __name__ == '__main__':
  webbrowser.open("http://localhost:8081/static/index.html")
  app.run(host='localhost', port=8081)
