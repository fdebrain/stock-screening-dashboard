import logging
from typing import List, Optional

import streamlit as st

from src.extract import UNKNOWN, Extractor
from src.plots import plot_bar, plot_line, plot_pie
from src.utils import simplify_numbers


def show_float(value: Optional[float], precision: int = 1):
    value = float(value) if value else None
    if value:
        return f"{value:.{precision}f}"
    else:
        return UNKNOWN


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


def handle_exception(func):
    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            st.error(e, icon="🚨")
        except AssertionError as e:
            st.error(e, icon="⚠️")
        except Exception as e:
            st.error("Could not fetch data.", icon="⚠️")
            logging.error(e)

    return func_wrapper


class Dashboard:
    @handle_exception
    def __init__(self, ticker: str):
        self.is_valid = False
        try:
            self.data_source = Extractor(ticker)
            self.is_valid = True
        except Exception as e:
            raise e

    @handle_exception
    def show_description(self):
        st.header(self.data_source.name)
        st.text(f"ISIN: {self.data_source.isin}")
        st.info(f"**Description:** {self.data_source.description}")
        st.success(f"**Exposure:** {self.data_source.exposure}")

    @handle_exception
    def show_key_info(self):
        col1, col2, col3 = st.columns([30, 35, 35])
        col1.metric("Symbol", self.data_source.symbol)
        col1.metric(
            f"Price [{self.data_source.currency}]",
            value=show_float(self.data_source.price, 2),
            delta=f"{show_float(self.data_source.delta, 2)} to MA200",
            help="Price & difference w.r.t. the past 200 days average prices",
        )
        col2.metric("Expense ratio [%]", show_float(self.data_source.fee, 2))
        col2.metric(
            f"52w Low | High [{self.data_source.currency}]",
            f"{show_float(self.data_source.low_52w)} | "
            f"{show_float(self.data_source.high_52w)}",
        )
        col3.metric(
            "Yield [%]",
            show_float(self.data_source.dividend_yield, 2),
        )
        col3.metric(
            f"Total assets [{self.data_source.currency}]",
            simplify_numbers(self.data_source.assets),
        )

    @handle_exception
    def show_historical_data(self):
        period = st.select_slider(label="Period", options=PERIODS, value="10y")
        interval = st.select_slider(label="Interval", options=INTERVALS, value="1d")
        hist = self.data_source.get_historical_data(period, interval).reset_index()
        assert len(hist) > 0, "No historical data found"
        col_x = "Date" if interval in ["1d", "5d", "1wk", "1mo", "3mo"] else "Datetime"
        plot_line(hist, col_x=col_x, col_y="Close")

    @handle_exception
    def show_sector_weights(self):
        sector_weights = self.data_source.get_sector_weights()
        plot_pie(sector_weights, col_cat="sectors", col_val="share")

    @handle_exception
    def show_country_weights(self):
        country_weights = self.data_source.get_country_weights()
        plot_pie(country_weights, col_cat="countries", col_val="share")

    @handle_exception
    def show_dividends(self):
        dividends_info = self.data_source.get_dividends()
        dividends = dividends_info["dividends"]
        assert len(dividends) > 0, "No dividend data found"
        yearly_dividends = dividends_info["yearly_dividends"]
        average_dividend = dividends_info["average_dividend"]
        average_increase = dividends_info["average_increase"]
        distribution_type = dividends_info["distribution_type"]

        col1, col2, col3 = st.columns([30, 30, 30])
        col1.metric(
            f"Average yearly dividend [{self.data_source.currency}]",
            show_float(average_dividend, 2),
            help="Discarding current year",
        )
        col2.metric("Average yearly increase [%]", show_float(average_increase, 2))
        col3.metric("Distribution frequency", distribution_type)
        col3, col4 = st.columns([70, 28])
        with col3:
            plot_bar(dividends, col_x="Date", col_y="Dividends")
        col4.dataframe(yearly_dividends.style.format("{:.2f}"))

    @handle_exception
    def show_top_holdings(self):
        top_holdings, top_holdings_share, n_holdings = self.data_source.get_top_holdings()
        col1, col2, _ = st.columns([30, 30, 40])
        col1.metric("Total holdings", n_holdings)
        col2.metric("Top 10 holdings share", f"{top_holdings_share:.2f} %")
        plot_pie(top_holdings, col_cat="company", col_val="share")

    @handle_exception
    def show_news(self):
        news = self.data_source.get_news()
        st.dataframe(news)
