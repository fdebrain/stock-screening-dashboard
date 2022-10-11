# Stock Screening Dashboard

[Try the Online Demo](https://fdebrain-stock-screening-dashboard-app-4jmasj.streamlitapp.com/)

Explore ETFs and stocks using Yahoo Finance API and Streamlit.

Don't forget to :star: the repo :)

## Requirements

Python 3.8

Poetry

## Installation

**Install dependencies:** `make install`

## Run the app

**Run Streamlit app:** `make run` (localhost:8501)

## Check code quality

We use Black, Flake8 and isort to ensure standard coding practices.

Each commit and pull request triggers a CI (Continuous Integration) pipeline job that runs code quality checks remotely (see Github Actions).

**(Optional) Run linters locally:** `pre-commit run -a`

## Features

- [x] Key information (expense ratio, price, 52 weeks low/high, total assets, yield)
- [x] Historical market data visualization (line plot, period & interval sliders)
- [x] Sectors weights visualization (donut plot)
- [x] Dividends visualization (bar plot, average yearly dividends & increase, distribution frequency, dataframe)
- [x] Top 15 holdings (donut plot, aggregated share)
- [ ] News
- [ ] Real-time typing ETF recommendation
- [ ] Additional information (~~total nbr of holdings~~, ~~weight by country~~, top performing holdings, etc...)
- [ ] Extending app to stocks (currently only ETFs)
- [ ] Comparing two ETFs/stocks (correlation, returns, etc...)
- [ ] More to come...

## Contributing
To learn more about making a contribution to this repository, please see our [Contributing guide](https://github.com/fdebrain/stock-screening-dashboard/blob/master/CONTRIBUTING.md).
