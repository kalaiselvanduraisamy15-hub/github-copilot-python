const SIZE = 9;
let puzzle = [];
let selectedCell = null;
let timerId = null;
let startTimestamp = null;
const SCORE_KEY = 'sudoku_top10_scores';

function setMessage(text, type = 'error') {
  const msg = document.getElementById('message');
  msg.className = type;
  msg.innerText = text;
}

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

function startTimer() {
  if (timerId) {
    clearInterval(timerId);
  }
  startTimestamp = Date.now();
  document.getElementById('timer').innerText = '00:00';
  timerId = setInterval(() => {
    const elapsed = Math.floor((Date.now() - startTimestamp) / 1000);
    document.getElementById('timer').innerText = formatTime(elapsed);
  }, 1000);
}

function getElapsedSeconds() {
  if (!startTimestamp) return 0;
  return Math.floor((Date.now() - startTimestamp) / 1000);
}

function getInputs() {
  return document.getElementById('sudoku-board').getElementsByTagName('input');
}

function idx(row, col) {
  return row * SIZE + col;
}

function getBoardFromUI() {
  const inputs = getInputs();
  const board = [];
  for (let row = 0; row < SIZE; row++) {
    board[row] = [];
    for (let col = 0; col < SIZE; col++) {
      const value = inputs[idx(row, col)].value;
      board[row][col] = value ? parseInt(value, 10) : 0;
    }
  }
  return board;
}

function computeConflicts(board) {
  const conflicts = new Set();

  for (let row = 0; row < SIZE; row++) {
    const positionsByValue = {};
    for (let col = 0; col < SIZE; col++) {
      const value = board[row][col];
      if (!value) continue;
      if (!positionsByValue[value]) positionsByValue[value] = [];
      positionsByValue[value].push([row, col]);
    }
    Object.values(positionsByValue).forEach((positions) => {
      if (positions.length > 1) {
        positions.forEach(([r, c]) => conflicts.add(idx(r, c)));
      }
    });
  }

  for (let col = 0; col < SIZE; col++) {
    const positionsByValue = {};
    for (let row = 0; row < SIZE; row++) {
      const value = board[row][col];
      if (!value) continue;
      if (!positionsByValue[value]) positionsByValue[value] = [];
      positionsByValue[value].push([row, col]);
    }
    Object.values(positionsByValue).forEach((positions) => {
      if (positions.length > 1) {
        positions.forEach(([r, c]) => conflicts.add(idx(r, c)));
      }
    });
  }

  for (let boxRow = 0; boxRow < SIZE; boxRow += 3) {
    for (let boxCol = 0; boxCol < SIZE; boxCol += 3) {
      const positionsByValue = {};
      for (let r = 0; r < 3; r++) {
        for (let c = 0; c < 3; c++) {
          const row = boxRow + r;
          const col = boxCol + c;
          const value = board[row][col];
          if (!value) continue;
          if (!positionsByValue[value]) positionsByValue[value] = [];
          positionsByValue[value].push([row, col]);
        }
      }
      Object.values(positionsByValue).forEach((positions) => {
        if (positions.length > 1) {
          positions.forEach(([r, c]) => conflicts.add(idx(r, c)));
        }
      });
    }
  }

  return conflicts;
}

function refreshCellStates(serverIncorrect = new Set()) {
  const board = getBoardFromUI();
  const conflicts = computeConflicts(board);
  const inputs = getInputs();

  for (let i = 0; i < inputs.length; i++) {
    const input = inputs[i];
    input.classList.remove('selected', 'incorrect', 'conflict');
    if (input.disabled) {
      input.classList.add('prefilled');
    }
    if (selectedCell === i) {
      input.classList.add('selected');
    }
    if (conflicts.has(i)) {
      input.classList.add('conflict');
    }
    if (serverIncorrect.has(i)) {
      input.classList.add('incorrect');
    }
  }
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let row = 0; row < SIZE; row++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let col = 0; col < SIZE; col++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      const boxClass = ((Math.floor(row / 3) + Math.floor(col / 3)) % 2 === 0) ? 'box-even' : 'box-odd';
      input.className = `sudoku-cell ${boxClass}`;
      input.dataset.row = row;
      input.dataset.col = col;
      input.addEventListener('click', () => {
        if (!input.disabled) {
          selectedCell = idx(row, col);
          refreshCellStates();
        }
      });
      input.addEventListener('input', (e) => {
        e.target.value = e.target.value.replace(/[^1-9]/g, '');
        selectedCell = idx(row, col);
        refreshCellStates();
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  selectedCell = null;
  createBoardElement();
  const inputs = getInputs();
  for (let row = 0; row < SIZE; row++) {
    for (let col = 0; col < SIZE; col++) {
      const input = inputs[idx(row, col)];
      const value = puzzle[row][col];
      if (value !== 0) {
        input.value = value;
        input.disabled = true;
      } else {
        input.value = '';
        input.disabled = false;
      }
    }
  }
  refreshCellStates();
}

function fillSelectedCell(value) {
  if (selectedCell === null) {
    setMessage('Select an empty cell first.', 'error');
    return;
  }
  const inputs = getInputs();
  const input = inputs[selectedCell];
  if (input.disabled) return;
  input.value = value === '0' ? '' : value;
  refreshCellStates();
}

async function newGame() {
  const difficulty = document.getElementById('difficulty').value;
  const res = await fetch(`/new?difficulty=${difficulty}`);
  const data = await res.json();
  renderPuzzle(data.puzzle);
  startTimer();
  setMessage(`New ${data.difficulty} puzzle started.`, 'info');
}

async function checkPuzzle() {
  const board = getBoardFromUI();
  const flat = board.flat();
  const hasEmpty = flat.includes(0);
  const conflicts = computeConflicts(board);
  refreshCellStates();

  if (conflicts.size > 0) {
    setMessage('Puzzle has conflicting cells.', 'error');
    return;
  }
  if (hasEmpty) {
    setMessage('No conflicts found so far. Keep going!', 'info');
    return;
  }
  setMessage('Puzzle is complete with no conflicts. Check solution to finish!', 'success');
}

async function submitScore(board) {
  const name = document.getElementById('player-name').value || 'Player';
  const difficulty = document.getElementById('difficulty').value;
  const timeSeconds = getElapsedSeconds();

  const payload = {
    name: name.trim().slice(0, 20) || 'Player',
    difficulty,
    time_seconds: timeSeconds
  };

  try {
    const list = JSON.parse(localStorage.getItem(SCORE_KEY) || '[]');
    list.push(payload);
    list.sort((a, b) => a.time_seconds - b.time_seconds);
    const top10 = list.slice(0, 10);
    localStorage.setItem(SCORE_KEY, JSON.stringify(top10));
  } catch {
    localStorage.setItem(SCORE_KEY, JSON.stringify([payload]));
  }

  loadScores();
  setMessage(`Solved in ${timeSeconds}s! Score saved.`, 'success');
}

async function checkSolution() {
  const board = getBoardFromUI();
  const res = await fetch('/check', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ board })
  });
  const data = await res.json();
  if (data.error) {
    setMessage(data.error, 'error');
    return;
  }

  const incorrect = new Set(data.incorrect.map(([r, c]) => idx(r, c)));
  refreshCellStates(incorrect);

  if (data.solved) {
    if (timerId) clearInterval(timerId);
    await submitScore(board);
  } else {
    setMessage('Some entries are incorrect.', 'error');
  }
}

async function requestHint() {
  const board = getBoardFromUI();
  const res = await fetch('/hint', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ board })
  });
  const data = await res.json();
  if (!res.ok || data.error) {
    setMessage(data.error || 'Hint unavailable.', 'error');
    return;
  }
  if (data.message) {
    setMessage(data.message, 'info');
    return;
  }

  const inputs = getInputs();
  const index = idx(data.row, data.col);
  inputs[index].value = data.value;
  inputs[index].disabled = true;
  inputs[index].classList.add('hint-lock');
  selectedCell = null;
  refreshCellStates();
  setMessage(`Hint used. Total hints: ${data.hints_used}`, 'info');
}

function loadScores() {
  const data = JSON.parse(localStorage.getItem(SCORE_KEY) || '[]');
  const tbody = document.getElementById('score-body');
  tbody.innerHTML = '';
  data.forEach((score, index) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${index + 1}</td>
      <td>${score.name}</td>
      <td>${score.difficulty}</td>
      <td>${score.time_seconds}</td>
    `;
    tbody.appendChild(tr);
  });
}

function applySavedTheme() {
  const theme = localStorage.getItem('theme') || 'light';
  document.body.classList.toggle('dark-theme', theme === 'dark');
}

function toggleTheme() {
  const dark = !document.body.classList.contains('dark-theme');
  document.body.classList.toggle('dark-theme', dark);
  localStorage.setItem('theme', dark ? 'dark' : 'light');
}

window.addEventListener('load', async () => {
  applySavedTheme();

  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('check-puzzle').addEventListener('click', checkPuzzle);
  document.getElementById('hint-btn').addEventListener('click', requestHint);
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);

  document.querySelectorAll('.num-btn').forEach((button) => {
    button.addEventListener('click', () => fillSelectedCell(button.dataset.value));
  });

  document.addEventListener('keydown', (event) => {
    if (selectedCell === null) return;
    if (/^[1-9]$/.test(event.key)) {
      fillSelectedCell(event.key);
    }
    if (event.key === 'Backspace' || event.key === 'Delete' || event.key === '0') {
      fillSelectedCell('0');
    }
  });

  loadScores();
  await newGame();
});