# BBC iPlayer Integration for AniWorld Downloader

## Overview

The BBC iPlayer integration has been successfully added to the AniWorld Downloader. This integration allows users to search for and download content from BBC iPlayer using the same interface as the other streaming platforms (AniWorld, SerienStream, MegaKino).

## Architecture & Implementation

### 1. Core Components

#### a) Get-iPlayer API Wrapper
- **File**: `src/aniworld/models/bbc_iplayer/get_iplayer_api.py`
- **Purpose**: Provides a Python interface to the get-iPlayer Perl script
- **Key Features**:
  - Automatic discovery of get-iPlayer executable
  - Search functionality for TV and Radio programmes
  - Programme information retrieval
  - Download coordination
  - Fallback mechanism to find get-iPlayer in common locations

#### b) BBC iPlayer Models
- **Files**:
  - `src/aniworld/models/bbc_iplayer/series.py` - BBCiPlayerSeries and BBCiPlayerSeason classes
  - `src/aniworld/models/bbc_iplayer/episode.py` - BBCiPlayerEpisode class
  - `src/aniworld/models/bbc_iplayer/__init__.py` - Module exports

- **Features**:
  - Full compatibility with existing Series/Season/Episode architecture
  - Support for both TV and Radio content
  - URL format: `bbc-iplayer://tv/<pid>` or `bbc-iplayer://radio/<pid>`
  - Query parameters support for options like `?subtitles=true`

### 2. Integration Points

#### URL Patterns (config.py)
```python
BBC_IPLAYER_SERIES_PATTERN = re.compile(
    r"^bbc-iplayer://(?:tv|radio)/[a-z0-9]+(?:\?.*)?/?$",
    re.IGNORECASE,
)

BBC_IPLAYER_EPISODE_PATTERN = re.compile(
    r"^bbc-iplayer://(?:tv|radio)/[a-z0-9]+(?:\?.*)?/?$",
    re.IGNORECASE,
)
```

#### Provider Registration (providers.py)
- Added BBC iPlayer as a new provider with Series, Season, and Episode classes
- Pattern matching for URL resolution

#### Search Function (search.py)
- `query_bbc_iplayer(keyword, content_type="tv", channel=None)` - Searches BBC iPlayer content
- Returns formatted results compatible with the web UI

#### Web API Routes (web/app.py)
- `/api/search` - Added BBC iPlayer search support when `site=bbc`
- Existing `/api/series`, `/api/seasons`, `/api/episodes` endpoints work transparently

#### Web UI Templates (web/templates/index.html)
- Added BBC iPlayer button to the site switcher
- Language labels for BBC iPlayer (English with/without subtitles)

#### Frontend JavaScript (web/static/app.js)
- Added BBC to the site list
- Updated switchSite() function with BBC handling
- Added BBC color theme (dark blue gradient)
- Updated language selector for BBC

### 3. File Structure

```
src/aniworld/
├── config.py                    [MODIFIED] - Added BBC URL patterns
├── providers.py                 [MODIFIED] - Added BBC provider registration
├── search.py                    [MODIFIED] - Added query_bbc_iplayer function
├── models/
│   ├── __init__.py             [MODIFIED] - Added BBC iPlayer imports
│   └── bbc_iplayer/            [NEW]
│       ├── __init__.py
│       ├── get_iplayer_api.py
│       ├── episode.py
│       └── series.py
└── web/
    ├── app.py                  [MODIFIED] - Added BBC search route
    ├── templates/
    │   └── index.html          [MODIFIED] - Added BBC button and labels
    └── static/
        └── app.js              [MODIFIED] - Added BBC UI handling
```

## Usage

### For End Users

1. **Access BBC iPlayer from Web UI**:
   - Click the "BBC iPlayer" button in the site switcher
   - Search for TV or Radio programmes
   - Select a result to view details
   - Choose language options (English with/without subtitles)
   - Click Download to queue the download

2. **Supported Content**:
   - BBC TV programmes (last 30 days)
   - BBC Radio programmes (last 30 days)
   - Quality options: HD, SD, Web, Mobile (automatic fallback)
   - Optional subtitle download for TV content

### For Developers

#### Adding More Platforms (Using BBC as Template)

1. Create model classes in `src/aniworld/models/<platform>/`:
   - series.py
   - season.py (or season_cls=None if not needed)
   - episode.py
   - __init__.py

2. Add URL patterns in `src/aniworld/config.py`:
   - NEWPLATFORM_SERIES_PATTERN
   - NEWPLATFORM_SEASON_PATTERN (if needed)
   - NEWPLATFORM_EPISODE_PATTERN

3. Register provider in `src/aniworld/providers.py`:
   - Import patterns and classes
   - Add to PROVIDERS list

4. Add search function in `src/aniworld/search.py`:
   - query_newplatform(keyword)

5. Update Web API in `src/aniworld/web/app.py`:
   - Add platform handling to api_search()
   - Import search function

6. Update Web UI:
   - Add button to `index.html`
   - Update `app.js` for UI handling
   - Add language labels as needed

## Dependencies

### External
- **get-iPlayer**: Perl script for BBC iPlayer content retrieval
  - Installation: See [get-iPlayer documentation](https://github.com/get-iplayer/get_iplayer)
  - Included in: `/get_iplayer-master/get_iplayer`
  - Auto-detection paths: `/usr/bin/get_iplayer`, `/usr/local/bin/get_iplayer`, `/opt/homebrew/bin/get_iplayer`, `$PATH`

### Python Packages
- All existing AniWorld Downloader dependencies
- No new Python packages required

## Limitations & Notes

1. **Search Scope**: BBC iPlayer only indexes programmes from the last 30 days. Older programmes must be accessed directly via URL or PID.

2. **Supported Formats**: Only whole episodes scheduled on BBC linear services. Not supported:
   - Red Button programmes
   - iPlayer box sets
   - BBC podcasts
   - News/sport videos
   - Programme clips
   - Archive programmes

3. **Regional Restrictions**: Content is only available from UK IP addresses (BBC licensing requirement)

4. **Quality Levels**: Available quality options depend on the programme:
   - HD (1920x1080)
   - SD (704x576)
   - Web (704x396)
   - Mobile (480x270)

## Testing

All Python files have been validated for syntax:
- ✓ get_iplayer_api.py
- ✓ series.py
- ✓ episode.py
- ✓ __init__.py (bbc_iplayer module)
- ✓ config.py
- ✓ providers.py
- ✓ search.py
- ✓ app.py (web)

URL patterns have been tested with:
- Basic URLs: `bbc-iplayer://tv/b0123456789`
- With query parameters: `bbc-iplayer://tv/b0123456789?subtitles=true`
- Both TV and Radio: `bbc-iplayer://radio/b0123456789`

## Future Enhancements

1. **Metadata Enhancement**:
   - Extract and display episode descriptions
   - Show channel information
   - Display programme availability duration

2. **Advanced Search**:
   - Filter by channel
   - Filter by content type (TV/Radio)
   - Advanced filtering options

3. **Auto-Sync**: 
   - Implement automatic downloading of new episodes

4. **Quality Profiles**:
   - Allow users to set preferred quality
   - Save user preferences per platform

## Files Modified Summary

| File | Type | Changes |
|------|------|---------|
| src/aniworld/config.py | Modified | Added BBC URL patterns |
| src/aniworld/providers.py | Modified | Added BBC provider, updated imports |
| src/aniworld/models/__init__.py | Modified | Added BBC iPlayer imports |
| src/aniworld/search.py | Modified | Added query_bbc_iplayer function |
| src/aniworld/web/app.py | Modified | Added BBC search route, updated imports |
| src/aniworld/web/templates/index.html | Modified | Added BBC button, language labels |
| src/aniworld/web/static/app.js | Modified | Added BBC UI handling, color theme |
| src/aniworld/models/bbc_iplayer/ | New | BBC iPlayer integration module |

## Installation Instructions

### For Local Installation

1. **Ensure get-iPlayer is installed**:
   ```bash
   # macOS (Homebrew)
   brew install get-iplayer
   
   # Ubuntu/Debian
   sudo apt-get install get-iplayer
   
   # Or use the included version in get_iplayer-master/
   ```

2. **Install/Update AniWorld Downloader**:
   ```bash
   pip install -U aniworld
   ```

3. **Launch and Use**:
   ```bash
   # Web UI
   aniworld -w
   
   # CLI Menu
   aniworld
   ```

### For Docker Installation

1. **Rebuild the Docker image with BBC iPlayer support**:
   ```bash
   # Navigate to the project directory
   cd /path/to/AniWorld-Downloader
   
   # Build the image with BBC iPlayer support
   docker-compose build
   ```

2. **Run the container**:
   ```bash
   # Start the container
   docker-compose up -d
   
   # View logs
   docker-compose logs -f
   ```

3. **Access the Web UI**:
   - Open http://localhost:8080 in your browser

The updated `Dockerfile` now includes:
- Perl and required Perl dependencies for get-iPlayer
- Automatic copy of the get_iplayer executable from `get_iplayer-master/`
- Proper installation to `/usr/local/bin/get_iplayer`

The updated `docker-compose.yaml` now:
- Uses local build by default (`build: .`)
- Includes instructions on switching to pre-built images if needed

## Troubleshooting

### get-iPlayer Not Found
- Ensure get-iPlayer is installed and in PATH
- Check if the executable is at: `/usr/bin/get_iplayer` or `/usr/local/bin/get_iplayer`
- For macOS with Homebrew: `brew install get-iplayer`

### No Search Results
- BBC iPlayer only indexes programmes from the last 30 days
- Try searching with different keywords
- Verify your internet connection
- Check if the programme is still available on BBC iPlayer

### Download Failures
- Verify get-iPlayer is working: `get_iplayer --help`
- Check available disk space
- Ensure proper permissions on download directory
- Try using a specific PID: `get_iplayer --pid=<pid>`

## References

- [get-iPlayer Documentation](https://github.com/get-iplayer/get_iplayer)
- [BBC iPlayer](https://www.bbc.co.uk/iplayer)
- [AniWorld Downloader](https://github.com/phoenixthrush/AniWorld-Downloader)
