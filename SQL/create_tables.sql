CREATE TABLE billboard100(
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    song_title TEXT,
    artist TEXT,
    week DATE,
    rank INT
);
--so that songs are not repeated before getting additional data from musicbrainz
CREATE TABLE billboard_songs(
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    song_title TEXT,
    artist TEXT,
    peak_rank INT,
    first_week DATE,
    last_week DATE
);
INSERT INTO billboard_songs (song_title, artist, peak_rank, first_week, last_week)
    SELECT
        song_title,
        artist,
        MIN(rank) AS peak_rank,
        MIN(week) AS first_week,
        MAX(week) AS last_week
    FROM billboard100
    GROUP BY song_title, artist
    ORDER BY MIN(week) ASC;

CREATE TABLE musicbrainz(
    bb_id INT REFERENCES billboard_songs(id),
    mbid TEXT,
    release_name TEXT,
    release_type TEXT,
    release_date DATE,
    PRIMARY KEY (bb_id, mbid)
);