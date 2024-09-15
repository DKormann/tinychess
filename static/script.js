
let board = document.getElementById('board');
let statusbar = document.getElementById("status")
let face = document.getElementById("face")

console.log(statusbar);


tiles = [];

const e = 0;

black = 0;
white = 1;
mycolor = white;

function setActive(x,y){
  board.querySelectorAll('.active').forEach(tile => tile.classList.remove('active'));
  console.log(x,y);
  

  if (! thinking && active[0] > -1){
    send_move(JSON.stringify({start:active[0]*10 + active[1], end:x*10 + y, prom:null}))
  }

  active = [x,y];
  tiles[x][y].classList.add('active');
}

var thinking = false

function display(boardState){
  statusbar.textContent = thinking? 'thinking ... ' : 'your move'
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
      let c = boardState[x][y];
      if (c != '.'){
        let iswhite = c == c.toUpperCase();
        c = c.toLowerCase();
        piece = document.createElement('div');
        piece.className = `piece ${c} ${iswhite ? 'white' : 'black'}`;
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

function get_board(start = false){
  fetch('http://localhost:8081/getstate')
  .then(response => response.text().then(data => {
    console.log(data);
    data = data.split('\n').map(row=>row.split(' '))
    display(data);
    if (! start){
      fetch('http://localhost:8081/answer').then(response=>{
        response.text().then(data=>{
          console.log(data);
          if (data.startsWith("GAME OVER")){
            statusbar.textContent = data
            return
          }
          data = data.split('\n').map(row=>row.split(' '))
          thinking = false
          display(data);
          update_face()

        })
      })
    }
  }))
}

function update_face(){
  fetch('http://localhost:8081/confidence').then(response=>{
    response.text().then(data=>{
      console.log("confidence:",data);
      emoji = ['🥶','🤯','😳','😒','🤨','🤔','😎','🥹','😏','🤩'][Math.round(Number(data) *10 -1)]
      face.textContent = emoji
    })
  })
}

get_board(true)

function send_move(move){
  thinking = true
  console.log("sending",move)
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
      thinking = false
    }
  })
}