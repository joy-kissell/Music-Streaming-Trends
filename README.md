# Music-Streaming-Trends
Dashboard project analyzing changes in music listening habits, primarily albums vs singles from 1958-2021. 
Data sourced from MusicBrainz and Kaggle. Visualized in Tableau, documented here.

## Datasets:
- **Billboard Hot 100 (1958-2021)**
  ```bash
  kaggle datasets download -d dhruvildave/billboard-the-hot-100-songs -p data --unzip
  ```
- **MusicBrainz API** - https://musicbrainz.org/

## Tableau Link:
![dashboard_preview](https://github.com/joy-kissell/Music-Streaming-Trends/blob/main/music-streaming-trends.png)

[Tableau Dashboard](https://public.tableau.com/views/MusicStreamingTrends_17598133254280/Dashboard1?:language=en-US&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link)

## Data Engineering

### Database Schema
**PostgreSQL Database**: `billboard_analysis`

**Tables:**
- `billboard100` - Raw Billboard chart data
  - `id` (auto-generated primary key)
  - `song_title`, `artist`, `week` (date), `rank`
  
- `billboard_songs` - Unique songs subset from billboard100
  - `id` (auto-generated primary key) 
  - `song_title`, `artist`, `first_week` (date of first chart appearance)

- `musicbrainz` - Release metadata from MusicBrainz API
  - `bb_id` (foreign key to billboard_songs.id)
  - `mbid` (MusicBrainz recording ID)
  - `release_name`, `release_type`, `release_date`

### Data Processing Pipeline

#### 1. Billboard Data Ingestion (`load_billboard.py`)
- Downloaded Billboard Hot 100 CSV from Kaggle
- Cleaned column names: `date` → `week`, `song` → `song_title`, `artist` → `artist`
- Filtered to 4 core columns matching database schema
- Loaded into PostgreSQL with proper date handling
- **Challenge**: URL-encoded password with special characters (`%`) for database connection

#### 2. Artist Name Cleaning (`clean_artist()`)
- Removed featured artists to focus on primary artist for API matching
- Regex patterns for: "feat.", "featuring", "ft.", "with"
- **Design choice**: Preserved band names with "&" (e.g., "Simon & Garfunkel")

#### 3. MusicBrainz API Integration (`musicbrainz_download.py`)
**Filtering Strategy:**
- **Title Matching**: Exact match between Billboard song and MusicBrainz recording title
- **Artist Verification**: Cross-reference artist names to prevent mismatched results
- **Date Filtering**: Only releases before or same data as first Billboard chart appearance date
- **Release Type Priority**: 
  1. Singles 
  2. EPs 
  3. Albums 
- Excluded compilations to avoid reissues

**API Rate Limiting:**
- 1-second delay between requests (MusicBrainz guidelines)
- Batch processing: Insert every 50 successful matches
- Error handling for API timeouts and missing data

#### 4. Data Quality Improvements
- **Exact title matching** prevents false positives (e.g., "Madrid" vs "Give Me Your Love")
- **Temporal validation** ensures release dates precede chart appearances and weeds out greatest hit compilations
- **Release type filtering** prioritizes original releases over compilations
- **Batch processing** for memory efficiency and database performance

### Key Technical Decisions
1. **Separate billboard_songs table**: Created subset for unique songs to avoid duplicate API calls
2. **SQLAlchemy with connection pooling**: Handles database connections efficiently
3. **Comprehensive error handling**: Graceful handling of API failures and date parsing issues
4. **Foreign key relationships**: `musicbrainz.bb_id` links to `billboard_songs.id` for data integrity

### Files:
- `scripts/download_billboard.py` - Kaggle dataset download
- `scripts/load_billboard.py` - Database ingestion and cleaning
- `scripts/musicbrainz_download.py` - API integration and metadata enrichment
- `config.py` - Database configuration
