import sqlite3

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO notes (file_path, patient_id) VALUES (?, ?)",
            ("C:/Users/nixona2/Documents/test_notes/FolderOutput.json", "Z123115"))

cur.execute("INSERT INTO notes (file_path, patient_id) VALUES (?, ?)",
            ("C:/Users/nixona2/Downloads/named_entity_annotation.json", "Z123117"))

cur.execute("INSERT INTO scores (evaluator, note_id, file_path, score) VALUES (?, ?, ?, ?)",
            ("Anna", 39484013, "/home/nixona2/scripted_preprocess/39484013.txt", 1))

connection.commit()
connection.close()