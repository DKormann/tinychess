#%%
with open('dataset/highrated.nums') as f: data = f.readlines()
games = []
wins = []
for line in data[:]:
  game = []
  for move in line.split(',')[1:]:
    move = move.strip().replace('=Q', '')
    if '=N' in move: break
    game.append(move)
  if len (game) < 10: continue
  wins.append(['white','draw', 'black'].index(line.split(',')[0]))
  games.append(game)

lens = list(map(len, games))
# %%
import numpy as np

e, K, Q, R, B, N, P = 0, 1, 2, 3, 4, 5, 6
PieceChars = '.KQRBNP'

# %%

def ptok10(pos): return (pos//8) * 10 + pos % 8
def p10tok(pos): return (pos//10) * 8 + pos % 10

data
data[0]

maxlen = 200
minlen = 20

def parse_game(line):
  if '=N' in line: return
  line = line.replace('=Q', '')
  head, *moves = line.split(',')

  winner = ['white','draw', 'black'].index(head)

  positions = []
  pieces = []

  for i, move in enumerate(moves):

    def tok(pos):
      n = int(pos.split(':')[1])
      n = p10tok(n)
      if i % 2 == 1: n = 63-n
      assert n>=0 and n<64
      return n

    poss = move.split('->')
    start,end = map(tok, poss)

    positions.extend([start,end])
    pieces.extend([0,PieceChars.index(poss[0].strip().split(':')[0])] )

  if len(positions) < minlen: return
  wins = [winner] * maxlen
  policy = positions[:maxlen] + [0] * (maxlen - len(positions))
  positions = [0] + policy[:-1]
  pieces = [0] + pieces[:maxlen-1] + [0] * (maxlen - len(pieces) - 1)
  return [np.array(x) for x in [positions, pieces, policy, wins]]

positions, pieces, policy, wins = map(np.array, zip(*[ps for line in data if (ps:=parse_game(line)) is not None]))

if __name__ == '__main__':
  print(positions[0])
  print(policy[0])
  print(positions[1])
  print(policy[1])
  print(pieces[0])

  print(np.array(lens).mean())