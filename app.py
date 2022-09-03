import streamlit as st

from src.extract import (
    get_data,
    get_description,
    get_dividends,
    get_historical_data,
    get_key_info,
    get_news,
    get_sector_weights,
    get_top_holdings,
)

if __name__ == "__main__":
    st.title("📈 Stock Screening Dashboard")
    st.caption("Explore ETFs and stocks using Yahoo Finance API and Streamlit.")

    if ticker := st.text_input("Enter ticker name or ISIN"):
        ticker = get_data(ticker)
        get_description(ticker)

        st.subheader("1.Key information")
        get_key_info(ticker)

        st.subheader("2.Historical market data")
        get_historical_data(ticker)

        st.subheader("3.Sectors weights")
        get_sector_weights(ticker)

        st.subheader("4.Dividends")
        dividends = get_dividends(ticker)

        st.subheader("5.Top holdings")
        top_holdings = get_top_holdings(ticker)

        st.subheader("6.News")
        get_news(ticker)
