DROP TABLE IF EXISTS sessions;

CREATE TABLE sessions (
  sid TEXT PRIMARY KEY,
  portfolio1 TEXT NOT NULL,
  portfolio2 TEXT NOT NULL
);
