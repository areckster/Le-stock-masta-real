# Local Stock Signal App

This project provides a simple stock signal application with an optional
Streamlit UI. Because the target environment does not have internet access, you
must download all required Python packages and model weights beforehand and
install them from local files.

Key features:
- Price data retrieval via `yfinance` with retry logic.
- Twitter and Reddit scraping using `snscrape` and Pushshift.
- Quantized Mistral model for sentiment analysis.
- Technical indicators (RSI, SMA, MACD) via `technical_analysis`.
- Signal generation and historical backtesting with `backtrader`.

## Installation

1. **Install Python** – Python 3.11 was used for development, but the scripts
   run with newer versions as well. Verify `python3 --version` to confirm.
2. **Install packages** – Execute `./setup.sh` which installs everything listed
   in `requirements.txt`. If your system cannot reach the internet, download the
   wheels yourself and point `pip` to that directory.
3. **Download a sentiment model** – The default configuration expects the
   *Mistral‑7B‑Instruct* model. Fetch it from Hugging Face (or another source)
   and place the files on disk. You can change the path in `sentiment.py` to use
   any other transformer model.

## Configuration

Edit `config.yaml` to specify tickers, social keywords, thresholds, schedule and
`discord_webhook_url`. The template includes comments describing each setting to
make configuration straightforward.

### Switching sentiment models

`sentiment.py` loads a transformer model from the local filesystem. To use a
different model, update the `model_name` path in that file to point to your
downloaded weights. Any sequence classification model from Hugging Face should
work as long as the tokenizer and model files are available offline.

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
