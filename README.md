# FlashscoreParser

A Python-based web scraper that extracts football match data from Flashscore.com, including fixtures, results, team statistics, head-to-head records and more.

## Features

- Extract fixture data including match dates, teams, and venues
- Get team form data with recent match history
- Retrieve head-to-head records between teams
- Collect detailed match statistics
- Export data in JSON format
- Rate limiting and caching to be respectful of the source website
- Configurable logging system

## Requirements

- Python 3.10+
- Dependencies listed in requirements.txt:
  - selenium ~= 4.24.0
  - tqdm ~= 4.66.5
  - typing ~= 3.10.0.0

## Installation

1. Clone the repository:

```bash
git clone https://github.com/MateiTiplea/FlashscoreParser.git
```

2. Create and activate a virtual environment (optional but recommended):

```bash
cd FlashscoreParser
python -m venv venv
source venv/bin/activate
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

The main script is `flashscore.py`. Run it with the desired arguments to extract data from Flashscore.com.

```bash
python flashscore.py -c "England" -l "Premier League" -r 1
```

<!-- add arguments  -->

## Arguments

- `-c`, `--country`: The country of the league to scrape (e.g. "England")
- `-l`, `--league`: The name of the league to scrape (e.g. "Premier League")
- `-r`, `--round`: The round number of the league to scrape (default: 1) (OPTIONAL)

## Project Structure

The project is structured as follows:

```plaintext
FlashscoreParser/
├── models/           # Data models for matches, teams, etc.
├── services/         # Business logic and data extraction
├── browsers/         # Web browser automation code
├── logs/            # Application logs
├── output/          # Generated JSON data
└── mappings/        # URL and data mappings
```
