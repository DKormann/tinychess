
let board = document.getElementById('board');

tiles = [];

const e = 0;

black = 0;
white = 1;
mycolor = white;

function setActive(x,y){
  board.querySelectorAll('.active').forEach(tile => tile.classList.remove('active'));


  if (active[0] > -1){  
    send_move(JSON.stringify([active, [x,y]]));
    active = [-1,-1];
    return;
  }

  active = [x,y];
  tiles[x][y].classList.add('active');
}

function getcolor(piece){
  return piece % 2;
}

function display(boardState){
  board.innerHTML = '';
  tiles = [];
  for (let x = 0; x < 8; x++) {
    row = document.createElement('div');
    row.className = 'row';
    board.appendChild(row);
    tiles.push([]);
    for (let y = 0; y < 8; y++) {
      tile = document.createElement('div');
      tile.id = `tile-${x}-${y}`;
      tile.className = 'tile';
      if ((x + y) % 2 == 1) tile.className += ' white';
      tile.addEventListener('click', setActive.bind(null, x, y));
      if (boardState[x][y] != 0){
        piece = document.createElement('div');
        piece.className += `piece p-${(boardState[x][y]-1)%9+1}`;
        piece.className += ' ' + (boardState[x][y] < 10 ? 'black' : 'white');
        tile.appendChild(piece);
      }

      if (active[0] == x && active[1] == y) tile.className += ' active';
      
      row.appendChild(tile);
      tiles[x].push(tile);
    }
  }
}


fetch('http://localhost:8081/reset')

active = [-1,-1]

function get_board(){
  fetch('http://localhost:8081/getstate')
  .then(response => response.json().then(data => {
    console.log(data);
    display(data);
  }))
}
get_board()

function send_move(move){
  fetch('http://localhost:8081/move', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({move}),
  }).then(response => {
    if (response.ok){
      console.log('move sent');
      get_board();
    }else{
      console.log('move failed');
    }
  })
}