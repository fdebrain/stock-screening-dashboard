from datetime import datetime

import pandas as pd
import requests
import streamlit as st
import yfinance as yf

UNKNOWN = "?"


@st.cache(allow_output_mutation=True)
def get_yahoo_finance_info(ticker: str):
    return yf.Ticker(ticker)


# @st.experimental_singleton
class Extractor:
    def __init__(self, ticker: str):
        self.data = get_yahoo_finance_info(ticker)
        self.info = self.data.info.copy()
        self.symbol = self.info.get("symbol") or ticker  # TODO: Alternative source

        try:
            self.get_basic_info()
        except Exception as e:
            st.text(e)

        try:
            self.get_trackinsights_info()
        except Exception as e:
            st.text(e)

        if not self.name:
            raise ValueError(f"Could not find ticker {ticker}.")

        if not self.is_etf:
            raise ValueError("Only ETF assets are currently handled.")

    def get_trackinsights_info(self):
        self.holdings = requests.get(
            f"https://data.trackinsight.com/holdings/{self.symbol}.json"
        ).json()
        self.funds = requests.get(
            f"https://data.trackinsight.com/funds/{self.symbol}.json"
        ).json()
        self.daily = requests.get(
            f"https://data.trackinsight.com/funds/{self.symbol}/daily.json"
        ).json()

        self.name = self.funds.get("label")
        self.description = self.funds["description"]
        self.exposure = self.funds["exposureDescription"]
        self.esg_grade = self.daily["esgGrade"]

        # Alternative source
        if not self.is_etf:
            self.is_etf = self.funds["product_type"] == "ETF" or False
        if not self.isin:
            self.isin = self.funds["isin"] or UNKNOWN
        if not self.currency:
            self.currency = self.funds["baseCurrency"] or UNKNOWN
        if not self.fee or self.fee == "0.00":
            self.fee = 100 * self.funds.get("expenseRatio", 0) or UNKNOWN
        if not self.price:
            self.price = self.daily["snap"]["nav"]

    def get_basic_info(self):
        self.name = self.info.get("longName")
        self.description = self.info.get("longBusinessSummary")
        self.exposure = UNKNOWN
        self.is_etf = self.info.get("quoteType") == "ETF"
        self.isin = self.data.isin.replace("-", "")
        self.assets = self.info.get("totalAssets")
        self.currency = self.info.get("currency")
        self.low_52w = self.info.get("fiftyTwoWeekLow")
        self.high_52w = self.info.get("fiftyTwoWeekHigh")
        self.price = self.info.get("regularMarketPrice")
        self.ma200 = self.info.get("twoHundredDayAverage")
        self.delta = self.price - self.ma200 if self.price and self.ma200 else None

        self.institutional_holders = self.data.get_institutional_holders(as_dict=True)
        self.fee = None
        if self.institutional_holders:
            self.institutional_holders = {
                k: v
                for k, v in zip(
                    self.institutional_holders[0].values(),
                    self.institutional_holders[1].values(),
                )
            }
            self.fee = self.institutional_holders["Expense Ratio (net)"].replace("%", "")
        self.dividend_yield = 100 * self.info.get("yield", 0)

    def get_historical_data(self, period: str, interval: str) -> pd.DataFrame:
        return self.data.history(period=period, interval=interval)  # .reset_index()

    def get_weights(self, field):
        data = self.holdings[field]
        names = list(data.keys())
        weights = [c["weight"] for c in data.values()]
        counts = [c["count"] for c in data.values()]
        df = pd.DataFrame({field: names, "share": weights, "count": counts})
        df["share"] *= 100
        df.sort_values(by="share", inplace=True, ascending=False)
        return df

    def get_sector_weights(self) -> pd.DataFrame:
        return self.get_weights("sectors")

    def get_country_weights(self):
        return self.get_weights("countries")

    def get_dividends(self, date_format: str = "%d/%m/%Y") -> pd.DataFrame:
        dividends = self.data.dividends.reset_index().sort_values(by="Date")
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
