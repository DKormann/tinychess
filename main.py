import flask
import flask_cors
import json
import functools, json
from enum import Enum, auto

app = flask.Flask(__name__)
flask_cors.CORS(app, resources={r"/*": {"origins": "*"}})

from chess import Board, start

state = start()

from bot import handle

@app.route('/getstate')
def get_state(): return str(state)

@app.route('/move', methods=['POST'])
def move():
  global state
  data = flask.request.json['move']
  state.move(**json.loads(data))
  state = state.flip()
  print("new passant:",state.passant)
  # response = handle(state)
  # state.move(response.start, response.end, response.prom)
  # state = state.flip()
  return 'ok'

@app.route('/reset')
def reset():
  global state
  state = start()
  return 'ok'

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8081)
