# Local Stock Signal App

This project provides a simple stock signal application with optional Streamlit UI. All dependencies must be installed locally as the runtime environment lacks internet access.

Key features:
- Price data retrieval via `yfinance` with retry logic.
- Twitter and Reddit scraping using `snscrape` and Pushshift.
- Quantized Mistral model for sentiment analysis.
- Technical indicators (RSI, SMA, MACD) via `technical_analysis`.
- Signal generation and historical backtesting with `backtrader`.

## Installation

```bash
./setup.sh
```

The script expects Python 3.11 and installs packages from `requirements.txt` (requires internet access).

## Configuration

Edit `config.yaml` to specify tickers, social keywords, thresholds, schedule, and `discord_webhook_url`.

## Usage

Run the main process manually:

```bash
python3 main.py
```

Schedule the app with APScheduler:

```bash
python3 run_scheduler.py
```

Example crontab entry to run every 30 minutes:

```
*/30 * * * * cd /path/to/project && python3 run_scheduler.py
```

### Streamlit UI

To launch the optional UI:

```bash
streamlit run app.py
```

### Tests

Run unit tests with:

```bash
python3 -m unittest
```
