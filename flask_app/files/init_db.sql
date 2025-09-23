CREATE TABLE messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  message TEXT
);

INSERT INTO messages (message) VALUES ('Hello from SQLite!'), ('Deployed with Ansible'), ('Artifact stored in S3');
