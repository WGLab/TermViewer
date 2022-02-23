import sqlite3

from flask import Flask, render_template, session, request, jsonify
from werkzeug.exceptions import abort

app = Flask(__name__)

#Initialize page and pass the list of available patient notesets
@app.route('/')
def index():
    patients = get_notesets()
    return render_template('termviewer.html', patients=patients)

#Returns contents of requested json file
@app.route('/get_file', methods = ['GET', 'POST'])
def get_file():
    path = request.args.get('path')
    print(path)
    with open( path, 'r', encoding='utf8') as f:
        text = f.read()
    return jsonify(result=text)

#Returns good/bad/unknown score for note
#Requires path to original patient note and evaluator
@app.route('/get_score', methods=['GET', 'POST'])
def get_score():
    note_path = request.args.get('path')
    evaluator = request.args.get('evaluator')
    conn = get_db_connection()
    score = conn.execute('SELECT score FROM scores WHERE evaluator = ? AND file_path = ?',
                         (evaluator, note_path)).fetchone()
    conn.close()
    if score is None:
        return jsonify(score=-1)
    return jsonify(score=int(score[0]))

#Updates score if it exists in database or creates new entry
#Requires path to original patient note, evaluator, and score
@app.route('/set_score', methods=['GET', 'POST'])
def set_score():
    note_path = request.args.get('path')
    evaluator = request.args.get('evaluator')
    score = request.args.get('score')
    conn = get_db_connection()
    cursor = conn.cursor()
    current_val = conn.execute('SELECT score FROM scores WHERE evaluator = ? AND file_path = ?',
                         (evaluator, note_path)).fetchone()
    if current_val is None:
        cursor.execute("INSERT INTO scores (evaluator, file_path, score) VALUES (?, ?, ?)",
                     (evaluator, note_path, score))
        conn.commit()
    else:
        cursor.execute('UPDATE scores SET score = ? WHERE evaluator = ? AND file_path = ?',
                     (score, evaluator, note_path))
        conn.commit()
    conn.close()
    if current_val: current_val = int(current_val[0])
    return jsonify(prev_score=current_val)

#Get available annotated notesets (path to JSON on server)
def get_notesets():
    conn = get_db_connection()
    notes = conn.execute('SELECT * FROM notes')
    return notes

#Connect to DB
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


