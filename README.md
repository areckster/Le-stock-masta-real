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

1. **Install Python** – Python 3.11 was used for development. Verify
   `python3 --version` to confirm that the correct interpreter is available. The
   recommended approach is to manage Python with **pyenv** as described below.
2. **Install packages** – Execute `./setup.sh` which installs everything listed
   in `requirements.txt`. If your system cannot reach the internet, download the
   wheels yourself and point `pip` to that directory. `setup.sh` expects a
   `python3.11` executable, so ensure pyenv (or your system) provides it.

3. **Download a sentiment model** – The default configuration expects the
   *Mistral‑7B‑Instruct* model. Fetch it from Hugging Face (or another source)
   and place the files on disk. You can change the path in `sentiment.py` to use
   any other transformer model.

### Using pyenv

`setup.sh` installs dependencies with `python3.11`. If your system does not
provide this interpreter, install [pyenv](https://github.com/pyenv/pyenv) and
`pyenv-virtualenv`.

```bash
# install Python 3.11 and create a virtual environment
pyenv install 3.11.0
pyenv virtualenv 3.11.0 stock-signal

# set the local version for this project
pyenv local stock-signal

# activate for the current shell (if not done automatically)
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

After activating the environment, run `./setup.sh` to install the required
packages.

## Configuration

Edit `config.yaml` to specify tickers, social keywords, thresholds, schedule and
`discord_webhook_url`. The template includes comments describing each setting to
make configuration straightforward.

### Selecting tickers

The `tickers` list in `config.yaml` determines which stocks are tracked.
Add or remove symbols under this key to customize alerts. Example:

```yaml
tickers:
  - AAPL
  - MSFT
  - GOOGL
```


### Switching sentiment models

`sentiment.py` loads a transformer model from the local filesystem. To use a
different model, update the `model_name` path in that file to point to your
downloaded weights. Any sequence classification model from Hugging Face should
work as long as the tokenizer and model files are available offline.

### Adjusting the schedule

The interval for the background scheduler is defined in `config.yaml` under the
`schedule.every` key.  Specify a value like `"15 minutes"` or simply `15` to
run `main.py` at your desired frequency.  `run_scheduler.py` reads this setting
each time it starts.

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

### Discord webhook setup

Set the `STOCK_SIGNAL_WEBHOOK` environment variable with your Discord webhook URL.
`config.yaml` references this variable via the `discord_webhook_url` setting. Example:

```bash
export STOCK_SIGNAL_WEBHOOK="https://discord.com/api/webhooks/..."
```

### Offline social media cache

Both scrapers automatically store results so they can be reused when the network
is unavailable. The Twitter helper first tries `snscrape` and then a Nitter
instance if scraping fails. Tweets are cached under
`data/twitter_cache/<keyword>.txt` and Reddit posts under
`data/reddit_cache/<keyword>.txt`. Each file contains one line per entry.
