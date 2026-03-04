from flask import Flask, render_template, jsonify, request
import sudoku_logic
import time
import sqlite3
import os

app = Flask(__name__)

DB_PATH = os.path.join(app.root_path, 'scores.db')

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None,
    'difficulty': 'medium',
    'start_time': None,
    'hints_used': 0
}

DIFFICULTY_CLUES = {
    'easy': 40,
    'medium': 34,
    'hard': 28
}


def init_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                time_seconds INTEGER NOT NULL,
                hints_used INTEGER NOT NULL,
                score INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
    finally:
        conn.close()


def get_top_scores(limit=10):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            '''
            SELECT name, difficulty, time_seconds, hints_used, score
            FROM scores
            ORDER BY score DESC, time_seconds ASC, id ASC
            LIMIT ?
            ''',
            (limit,)
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def insert_score(name, difficulty, time_seconds, hints_used, score):
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            '''
            INSERT INTO scores (name, difficulty, time_seconds, hints_used, score)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (name, difficulty, time_seconds, hints_used, score)
        )
        conn.commit()
    finally:
        conn.close()


init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty', 'medium').lower()
    clues = int(request.args.get('clues', DIFFICULTY_CLUES.get(difficulty, 34)))
    if difficulty not in DIFFICULTY_CLUES:
        difficulty = 'medium'
    puzzle, solution = sudoku_logic.generate_puzzle(clues)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['difficulty'] = difficulty
    CURRENT['start_time'] = time.time()
    CURRENT['hints_used'] = 0
    return jsonify({'puzzle': puzzle, 'difficulty': difficulty, 'clues': clues})

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect, 'solved': len(incorrect) == 0})


@app.route('/hint', methods=['POST'])
def get_hint():
    solution = CURRENT.get('solution')
    puzzle = CURRENT.get('puzzle')
    if solution is None or puzzle is None:
        return jsonify({'error': 'No game in progress'}), 400

    data = request.json or {}
    board = data.get('board')
    if not board:
        return jsonify({'error': 'Board is required'}), 400

    candidates = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if puzzle[i][j] != 0:
                continue
            if board[i][j] != solution[i][j]:
                candidates.append((i, j))

    if not candidates:
        return jsonify({'message': 'No hint needed. Puzzle already solved!'}), 200

    row, col = candidates[0]
    CURRENT['hints_used'] += 1
    return jsonify({'row': row, 'col': col, 'value': solution[row][col], 'hints_used': CURRENT['hints_used']})


@app.route('/scores')
def get_scores():
    return jsonify({'scores': get_top_scores(10)})


@app.route('/score', methods=['POST'])
def submit_score():
    solution = CURRENT.get('solution')
    start_time = CURRENT.get('start_time')
    if solution is None or start_time is None:
        return jsonify({'error': 'No game in progress'}), 400

    data = request.json or {}
    board = data.get('board')
    name = (data.get('name') or 'Player').strip()[:20] or 'Player'

    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                return jsonify({'error': 'Board is not solved correctly'}), 400

    elapsed_seconds = int(time.time() - start_time)
    hints_used = CURRENT.get('hints_used', 0)
    difficulty = CURRENT.get('difficulty', 'medium')
    difficulty_bonus = {'easy': 0, 'medium': 250, 'hard': 500}.get(difficulty, 250)
    score = max(0, 5000 + difficulty_bonus - (elapsed_seconds * 10) - (hints_used * 150))

    insert_score(name, difficulty, elapsed_seconds, hints_used, score)

    return jsonify({
        'name': name,
        'difficulty': difficulty,
        'time_seconds': elapsed_seconds,
        'hints_used': hints_used,
        'score': score
    })

if __name__ == '__main__':
    app.run(debug=True)