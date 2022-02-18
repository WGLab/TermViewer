import sqlite3

from flask import Flask, render_template
from werkzeug.exceptions import abort

app = Flask(__name__)

@app.route('/')
def index():
    patients = get_notesets()
    return render_template('termviewer.html', patients=patients)

@app.route('/get_file/<path:path>', methods=['GET'])
def get_json_file(path):
    print(path)
    with open(path, 'r', encoding='utf8') as f:
        text = f.read()
    return text

@app.route('/get_score/<path:path>/<evaluator>', methods=['GET'])
def get_score(path, evaluator):
    print(path, evaluator)
    conn = get_db_connection()
    score = conn.execute('SELECT * FROM scores WHERE evaluator = ? AND file_path = ?',
                         (evaluator, path)).fetchone()
    conn.close()
    if score is None:
        return str(-1)
    return str(score)

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


