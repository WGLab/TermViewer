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

def get_score(note_id):
    conn = get_db_connection()
    score = conn.execute('SELECT * FROM scores WHERE note_id = ?',
                         (note_id,)).fetchone()
    conn.close()
    if score is None:
        abort(404)
    return score
