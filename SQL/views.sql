CREATE OR REPLACE VIEW hot100_release_types AS
SELECT
    EXTRACT(YEAR FROM billboard_songs.first_week) AS chart_year, m.release_type,
    COUNT(billboard_songs.id) AS num_songs
FROM billboard_songs 
JOIN musicbrainz m
    ON billboard_songs.id = m.bb_id
GROUP BY chart_year, m.release_type
ORDER BY chart_year;