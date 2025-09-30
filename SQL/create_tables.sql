CREATE TABLE billboard100(
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    song_title TEXT,
    artist TEXT,
    week DATE,
    rank INT
);

CREATE TABLE musicbrainz(
    mbid TEXT PRIMARY KEY,
    song_title TEXT,
    artist TEXT,
    release_name TEXT,
    release_type TEXT,
    release_date DATE
);