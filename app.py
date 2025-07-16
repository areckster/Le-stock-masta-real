"""Streamlit UI for displaying signals and backtest results."""

import streamlit as st
from pathlib import Path
import yaml
from signals import generate_signal
from backtest import backtest_strategy

CONFIG_PATH = "config.yaml"


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def main():
    st.title("Stock Signals")
    config = load_config()
    signals = {}
    for ticker in config.get("tickers", []):
        signals[ticker] = generate_signal(ticker)
    st.write(signals)

    if st.button("Run Backtest"):
        results = {}
        for ticker in config.get("tickers", []):
            results[ticker] = backtest_strategy(ticker)
        st.write(results)


if __name__ == "__main__":
    main()
