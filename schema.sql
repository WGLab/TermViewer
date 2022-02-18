DROP TABLE IF EXISTS notes;
DROP TABLE IF EXISTS scores;

CREATE TABLE notes (
    file_path TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL
);

CREATE TABLE scores (
    evaluator VARCHAR(20),
    note_id INTEGER,
    file_path TEXT NOT NULL,
    SCORE INTEGER,
    PRIMARY KEY (evaluator, note_id)
);