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
def get_state(): return str(state)

@app.route('/move', methods=['POST'])
def move():
  global state
  data = flask.request.json['move']
  state.move(**json.loads(data))
  print(state, '\n\n')
  return 'ok'

@app.route('/answer')
def answer():
  global state
  state = state.flip()

  print(state, '\n\n')
  response = handle(state, 3)
  if response is None:return "GAME OVER"
  print(response)
  state.move(response.start, response.end, response.prom)
  state = state.flip()
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
