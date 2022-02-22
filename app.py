import sqlite3

from flask import Flask, render_template, session, request, jsonify
from werkzeug.exceptions import abort

app = Flask(__name__)

@app.route('/')
def index():
    patients = get_notesets()
    return render_template('termviewer.html', patients=patients)

@app.route('/get_file', methods = ['GET', 'POST'])
def get_file():
    path = request.args.get('path')
    print(path)
    with open( path, 'r', encoding='utf8') as f:
        text = f.read()
    return jsonify(result=text)

@app.route('/get_score', methods=['GET', 'POST'])
def get_score():
    note_path = request.args.get('path')
    evaluator = request.args.get('evaluator')
    print(note_path, evaluator)
    conn = get_db_connection()
    score = conn.execute('SELECT * FROM scores WHERE evaluator = ? AND file_path = ?',
                         (evaluator, note_path)).fetchone()
    conn.close()
    if score is None:
        return jsonify(score=-1)
    return jsonify(score=score)

@app.route('/set_score', methods=['POST'])
def set_score():
    note_path = request.args.get('path')
    evaluator = request.args.get('evaluator')
    score = request.args.get('score')
    print(note_path, evaluator)
    conn = get_db_connection()
    current_val = conn.execute('SELECT * FROM scores WHERE evaluator = ? AND file_path = ?',
                         (evaluator, note_path)).fetchone()

    if current_val is None:
        conn.execute("INSERT INTO scores (evaluator, file_path, score) VALUES (?, ?, ?)",
                     (evaluator, note_path, score))
    else:
        conn.execute('UPDATE scores SET score = ? WHERE evaluator = ? AND file_path = ?',
                     (score, evaluator, note_path))
    conn.close()

@app.route('/update_score/<path:path>/evaluator/score', methods=['POST'])
def update_score(path, evaluator, score):
    conn = get_db_connection()
    # score = conn.execute('SELECT * FROM scores WHERE evaluator = ? AND file_path = ?',
    #                      (evaluator, path)).fetchone()
    conn.close()

def get_next_note(notes):
    return notes.fetchone()



def get_notesets():
    conn = get_db_connection()
    notes = conn.execute('SELECT * FROM notes')
    return notes

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


