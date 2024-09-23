#%%
import csv

reader = csv.reader(open('games.csv', 'r'))
head = reader.__next__()
print(head)

# %%
cleaned = [line for line in reader]

# %%

rated  = []
for line in cleaned:

  id, israted, created, lastmoveat, turns, victory, winner, increment, whiteid, whiteelo, blackid, blackelo, moves,*res = line
  if israted: rated.append((winner, moves, min(whiteelo, blackelo)))

# %%

highrated = [line[:2] for line in rated if int(line[2]) > 1900]
#%%

from chess import Board

def al2num(move:str, col=0):
  assert move[0] in 'abcdefgh' and move[1] in '12345678'
  return (ord(move[0]) - ord('a')) + 10 * (8-int(move[1]))

print(al2num('a1'))

#%%

for game in highrated:
  board = Board.start()
  for i, move in enumerate(game[1].split()):
    # print(i, move)
    if len(move) == 2:

  break
# %%
