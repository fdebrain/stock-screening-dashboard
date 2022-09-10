from typing import List

import streamlit as st

from src.extract import Extractor
from src.plots import plot_bar, plot_line, plot_pie
from src.utils import simplify_numbers

PERIODS: List[str] = [
    "1d",
    "5d",
    "1mo",
    "3mo",
    "6mo",
    "ytd",
    "1y",
    "2y",
    "5y",
    "10y",
    "max",
]

INTERVALS: List[str] = [
    "1m",
    "2m",
    "5m",
    "15m",
    "30m",
    "60m",
    "90m",
    "1h",
    "1d",
    "5d",
    "1wk",
    "1mo",
    "3mo",
]


class Dashboard:
    def __init__(self, ticker: str):
        self.data_source = Extractor(ticker)
        self.is_valid = True

        if not self.data_source.name:
            st.error(f"Could not find ticker {ticker}.", icon="🚨")
            self.is_valid = False
        elif not self.data_source.is_etf:
            st.error("Only ETF assets are currently handled.", icon="🚨")
            self.is_valid = False

    def show_description(self):
        st.header(self.data_source.name)
        st.text(f"ISIN: {self.data_source.isin}")
        st.info(f"**Description:** {self.data_source.description}")
        st.success(f"**Exposure:** {self.data_source.exposure}")

    def show_key_info(self):
        col1, col2, col3 = st.columns([30, 35, 35])
        col1.metric("Symbol", self.data_source.symbol)
        col1.metric(
            f"Price [{self.data_source.currency}]",
            value=self.data_source.price,
            delta=f"{self.data_source.delta} to MA200",
            help="Price & difference w.r.t. the past 200 days average prices",
        )
        col2.metric("Expense ratio [%]", self.data_source.fee)
        col2.metric(
            "52w Low | High",
            f"{self.data_source.low_52w:.1f} | {self.data_source.high_52w:.1f}",
        )
        col3.metric("Yield [%]", self.data_source.dividend_yield)
        col3.metric(
            f"Total assets [{self.data_source.currency}]",
            simplify_numbers(self.data_source.assets),
        )

    def show_historical_data(self):
        period = st.select_slider(label="Period", options=PERIODS, value="10y")
        interval = st.select_slider(label="Interval", options=INTERVALS, value="1d")
        hist = self.data_source.get_historical_data(period, interval)
        col_x = "Date" if interval in ["1d", "5d", "1wk", "1mo", "3mo"] else "Datetime"
        plot_line(hist, col_x=col_x, col_y="Close")

    def show_sector_weights(self):
        sector_weights = self.data_source.get_sector_weights()
        plot_pie(sector_weights, col_cat="sector", col_val="share")

    def show_country_weights(self):
        country_weights = self.data_source.get_country_weights()
        plot_pie(country_weights, col_cat="country", col_val="share")

    def show_dividends(self):
        dividends_info = self.data_source.get_dividends()
        dividends = dividends_info["dividends"]
        yearly_dividends = dividends_info["yearly_dividends"]
        average_dividend = dividends_info["average_dividend"]
        average_increase = dividends_info["average_increase"]
        distribution_type = dividends_info["distribution_type"]

        col1, col2, col3 = st.columns([30, 30, 30])
        col1.metric(
            f"Average yearly dividend [{self.data_source.currency}]",
            f"{average_dividend:.2f}",
            help="Discarding current year",
        )
        col2.metric("Average yearly increase [%]", f"{average_increase:.2f}")
        col3.metric("Distribution frequency", distribution_type)
        col3, col4 = st.columns([70, 28])
        with col3:
            plot_bar(dividends, col_x="Date", col_y="Dividends")
        col4.dataframe(yearly_dividends.style.format("{:.2f}"))

    def show_top_holdings(self):
        top_holdings, top_holdings_share, n_holdings = self.data_source.get_top_holdings()
        col1, col2, _ = st.columns([30, 30, 40])
        col1.metric("Top 10 holdings share", f"{top_holdings_share:.2f} %")
        col2.metric("Total holdings", n_holdings)
        plot_pie(top_holdings, col_cat="company", col_val="share")

    def show_news(self):
        news = self.data_source.get_news()
        st.dataframe(news)
