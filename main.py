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
  response = handle(state)
  state.move(response.start, response.end, response.prom)
  state = state.flip()
  return str(state)

@app.route('/reset')
def reset():
  global state
  state = start()
  state.castles = [False, False, False, False]
  return 'ok'

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8081)
