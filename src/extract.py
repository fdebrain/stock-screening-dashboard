from collections import ChainMap
from datetime import datetime

import pandas as pd
import streamlit as st
import yfinance as yf
from streamlit_elements import elements

from src.plots import plot_line, plot_pie
from src.utils import simplify_numbers


@st.experimental_singleton
def get_data(ticker: str) -> yf.Ticker:
    return yf.Ticker(ticker)


def get_distribution_type(dividends: pd.DataFrame):
    distributions_per_year = dividends.groupby(dividends["Date"].dt.year).size().mean()
    if distributions_per_year > 7:
        return "Monthly"
    elif distributions_per_year > 3.5:
        return "Quarterly"
    elif distributions_per_year > 1.5:
        return "Bi-annually"
    else:
        return "Annually"


def get_description(ticker: yf.Ticker):
    info = ticker.info
    name = info.get("longName")
    asset_type = info.get("quoteType")
    assert name, "Could not find ticker"
    assert asset_type == "ETF", "Only ETF assets are currently handled"
    st.header(name)
    description = info.get("longBusinessSummary")
    st.text(f"ISIN: {ticker.get_isin()}")
    st.info(f"**Description:** {description}")


def get_key_info(ticker: yf.Ticker):
    info = ticker.info
    symbol = info.get("symbol")
    assets = info.get("totalAssets", "?")
    currency = info.get("currency", "USD")
    low_52w = info.get("fiftyTwoWeekLow", 0)
    high_52w = info.get("fiftyTwoWeekHigh", 0)
    price = info.get("regularMarketPrice")
    price_ma200 = info.get("twoHundredDayAverage")
    delta = round(price - price_ma200, 2) if price and price_ma200 else "None"

    institutional_holders = ticker.get_institutional_holders()
    fee = institutional_holders.set_index(0).loc["Expense Ratio (net)"].values[0]
    # TODO: Look at dividendYield if asset is a stock
    dividend_yield = round(100 * info.get("yield"), 2)

    # Show in Streamlit
    col1, col2, col3 = st.columns([30, 35, 35])

    col1.metric("Symbol", symbol)
    col1.metric(
        f"Price [{currency}]",
        value=price,
        delta=f"{delta} to MA200",
        help="Price & difference w.r.t. the past 200 days average prices",
    )
    col2.metric("Expense ratio [%]", fee)
    col2.metric("52w Low | High", f"{low_52w:.1f} | {high_52w:.1f}")
    col3.metric("Yield [%]", dividend_yield)
    col3.metric(f"Total assets [{currency}]", simplify_numbers(assets))


def get_sector_weights(ticker: yf.Ticker):
    # List of dictionnaries into single dict
    info = ticker.info
    sector_weights = dict(ChainMap(*info["sectorWeightings"]))
    sector_weights = dict(
        sector=list(sector_weights.keys()),
        share=list(sector_weights.values()),
    )
    df_sectors = pd.DataFrame(sector_weights)
    df_sectors["sector"] = df_sectors["sector"].str.replace("_", " ")
    df_sectors["sector"] = df_sectors["sector"].str.capitalize()
    df_sectors["share"] *= 100
    df_sectors.sort_values(by="share", inplace=True, ascending=False)

    # Show in Streamlit
    with elements("sector_weights"):
        plot_pie(df_sectors, col_cat="sector", col_val="share")
        # show_dataframe(df_sectors)


def get_historical_data(ticker: yf.Ticker):
    period = st.select_slider(
        label="Period",
        options=[
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
        ],
        value="10y",
    )
    interval = st.select_slider(
        label="Interval",
        options=[
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
        ],
        value="1d",
    )

    hist = ticker.history(period=period, interval=interval)
    hist = hist.copy().reset_index()
    col_x = "Date" if interval in ["1d", "5d", "1wk", "1mo", "3mo"] else "Datetime"

    # Show in Streamlit
    with elements("historical_data"):
        plot_line(hist, col_x=col_x, col_y="Close")


def get_dividends(ticker: yf.Ticker, date_format: str = "%d/%m/%Y"):
    currency = ticker.info.get("currency", "USD")
    dividends = ticker.dividends.copy().reset_index().sort_values(by="Date")
    yearly_dividends = dividends.groupby(dividends["Date"].dt.year).sum()
    yearly_dividends["Increase"] = 100 * (
        yearly_dividends["Dividends"].diff() / yearly_dividends["Dividends"].shift(+1)
    )
    dividends["Date"] = pd.to_datetime(
        dividends["Date"].dt.strftime(date_format),
        infer_datetime_format=True,
    )
    average_dividend, average_increase = yearly_dividends.iloc[:-1, :].mean(axis=0)

    # Show in Streamlit
    col1, col2, col3 = st.columns([30, 30, 30])
    col1.metric(
        f"Average yearly dividend [{currency}]",
        f"{average_dividend:.2f}",
        help="Discarding current year",
    )
    col2.metric("Average yearly increase [%]", f"{average_increase:.2f}")
    col3.metric("Distribution frequency", get_distribution_type(dividends))
    col3, col4 = st.columns([70, 30])
    col3.bar_chart(data=dividends, x="Date", y="Dividends")
    col4.dataframe(yearly_dividends)


def get_top_holdings(ticker: yf.Ticker):
    top_holdings = pd.DataFrame(ticker.info["holdings"])
    top_holdings["holdingPercent"] *= 100
    top_holdings_share = top_holdings["holdingPercent"].sum()

    # Show in Streamlit
    with elements("top_holdings"):
        st.metric("Top 10 holdings share", f"{top_holdings_share:.2f} %")
        plot_pie(top_holdings, col_cat="holdingName", col_val="holdingPercent")


def get_news(ticker, date_format="%d/%m/%Y  %H:%M:%S"):
    news = [
        {
            "Time": datetime.fromtimestamp(news["providerPublishTime"]).strftime(
                date_format
            ),
            "Title": news["title"],
        }
        for news in ticker.get_news()
    ]
    st.dataframe(news)
