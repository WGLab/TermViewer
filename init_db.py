import sqlite3

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO notes (file_path, patient_id) VALUES (?, ?)",
            ("/Users/annanixon/Documents/CHOP_Research/AJHG_taggedFolderOutput.json", "AJHG_samplenotes"))

#cur.execute("INSERT INTO notes (file_path, patient_id) VALUES (?, ?)",
#            ("/home/nixona2/scripted_final/FolderOutput.json", "Z123117"))

#cur.execute("INSERT INTO scores (evaluator, file_path, score) VALUES (?, ?, ?)",
#            ("Anna", "/home/nixona2/scripted_preprocess/39484013.txt", 1))

connection.commit()
connection.close()
