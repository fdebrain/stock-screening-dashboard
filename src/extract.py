from datetime import datetime

import pandas as pd
import requests
import streamlit as st
import yfinance as yf


@st.experimental_singleton
class Extractor:
    def __init__(self, ticker: str):
        self.data = yf.Ticker(ticker)
        self.info = self.data.info
        self.is_etf = self.info.get("quoteType") == "ETF"

        if self.info.get("longName") and self.is_etf:
            self.get_basic_info()

    def get_basic_info(self):
        self.isin = self.data.isin
        self.symbol = self.info.get("symbol")
        self.holdings = requests.get(
            f"https://data.trackinsight.com/holdings/{self.symbol}.json"
        ).json()
        self.funds = requests.get(
            f"https://data.trackinsight.com/funds/{self.symbol}.json"
        ).json()
        self.name = self.funds["label"]
        self.description = self.funds["description"]
        self.exposure = self.funds["exposureDescription"]
        self.assets = self.info.get("totalAssets", "?")
        self.currency = self.info.get("currency", "?")
        self.low_52w = self.info.get("fiftyTwoWeekLow") or 0
        self.high_52w = self.info.get("fiftyTwoWeekHigh") or 0
        self.price = self.info.get("regularMarketPrice") or 0
        self.price_ma200 = self.info.get("twoHundredDayAverage") or 0
        self.delta = (
            round(self.price - self.price_ma200, 2)
            if self.price and self.price_ma200
            else "None"
        )

        self.institutional_holders = self.data.get_institutional_holders()
        self.fee = (
            self.institutional_holders.set_index(0).loc["Expense Ratio (net)"].values[0]
        )
        self.dividend_yield = round(100 * self.info.get("yield"), 2)

    def get_historical_data(self, period: str, interval: str) -> pd.DataFrame:
        hist = self.data.history(period=period, interval=interval)
        hist = hist.copy().reset_index()
        return hist

    def get_sector_weights(self) -> pd.DataFrame:
        data = self.holdings["sectors"]
        sectors = list(data.keys())
        weights = [c["weight"] for c in data.values()]
        counts = [c["count"] for c in data.values()]
        df_sectors = pd.DataFrame(
            {
                "sector": sectors,
                "share": weights,
                "count": counts,
            }
        )
        df_sectors["share"] *= 100
        df_sectors.sort_values(by="share", inplace=True, ascending=False)
        return df_sectors

    def get_country_weights(self):
        data = self.holdings["countries"]
        countries = list(data.keys())
        weights = [c["weight"] for c in data.values()]
        counts = [c["count"] for c in data.values()]
        df_country = pd.DataFrame(
            {
                "country": countries,
                "share": weights,
                "count": counts,
            }
        )
        df_country["share"] *= 100
        df_country.sort_values(by="share", inplace=True, ascending=False)
        return df_country

    def get_dividends(self, date_format: str = "%d/%m/%Y") -> pd.DataFrame:
        dividends = self.data.dividends.copy().reset_index().sort_values(by="Date")
        yearly_dividends = dividends.groupby(dividends["Date"].dt.year).sum()

        average_dividend, average_increase = 0, 0
        if len(yearly_dividends) > 1:
            yearly_dividends["Increase"] = 100 * (
                yearly_dividends["Dividends"].diff()
                / yearly_dividends["Dividends"].shift(+1)
            )
            average_dividend, average_increase = yearly_dividends.iloc[:-1, :].mean(
                axis=0
            )

        dividends["Date"] = pd.to_datetime(
            dividends["Date"].dt.strftime(date_format),
            infer_datetime_format=True,
        )

        distribution_type = self.get_distribution_type(dividends)
        return {
            "dividends": dividends,
            "yearly_dividends": yearly_dividends,
            "average_dividend": average_dividend,
            "average_increase": average_increase,
            "distribution_type": distribution_type,
        }

    def get_top_holdings(self):
        data = self.holdings["topHoldings"]
        n_holdings = self.holdings["count"]
        companies = [c["label"] for c in data]
        weights = [c["weight"] for c in data]
        df_top_holdings = pd.DataFrame({"company": companies, "share": weights})
        df_top_holdings["share"] *= 100
        top_holdings_share = df_top_holdings["share"].sum()
        return df_top_holdings, top_holdings_share, n_holdings

    def get_news(self, date_format="%d/%m/%Y  %H:%M:%S"):
        news = [
            {
                "Time": datetime.fromtimestamp(news["providerPublishTime"]).strftime(
                    date_format
                ),
                "Title": news["title"],
            }
            for news in self.data.get_news()
        ]
        return news

    def get_distribution_type(self, dividends: pd.DataFrame):
        distributions_per_year = (
            dividends.groupby(dividends["Date"].dt.year).size().mean()
        )
        if distributions_per_year > 7:
            return "Monthly"
        elif distributions_per_year > 3.5:
            return "Quarterly"
        elif distributions_per_year > 1.5:
            return "Bi-annually"
        else:
            return "Annually"
