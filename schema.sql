DROP TABLE IF EXISTS notes;
DROP TABLE IF EXISTS scores;
DROP TABLE IF EXISTS tags;

CREATE TABLE notes (
    file_path TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL
);

CREATE TABLE scores (
    evaluator VARCHAR(20),
--    note_id INTEGER,
    file_path TEXT NOT NULL,
    SCORE INTEGER,
    PRIMARY KEY (evaluator, file_path)
);

CREATE TABLE tags (
    evaluator VARCHAR(20),
    file_path TEXT NOT NULL,
    offset INTEGER,
    tag_length INTEGER,
    SCORE INTEGER,
    PRIMARY KEY (evaluator, file_path, offset, tag_length)
);
