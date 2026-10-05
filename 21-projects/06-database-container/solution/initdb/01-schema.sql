-- Runs once, when the container starts with an EMPTY data folder (a new volume).
CREATE TABLE menu (
  id    SERIAL PRIMARY KEY,
  item  TEXT NOT NULL UNIQUE,
  price NUMERIC(5, 2) NOT NULL CHECK (price > 0)
);
