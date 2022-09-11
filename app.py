import streamlit as st

from src.dashboard import Dashboard

if __name__ == "__main__":
    st.title("📈 Stock Screening Dashboard")
    st.caption(
        "Explore ETFs and stocks using Yahoo Finance, TrackInsights and Streamlit."
    )

    if ticker := st.text_input("Enter ticker name or ISIN", placeholder="VOO"):
        dashboard = Dashboard(ticker)

        if dashboard.is_valid:
            dashboard.show_description()
            st.subheader("1.Key information")
            dashboard.show_key_info()
            st.subheader("2.Historical market data")
            dashboard.show_historical_data()
            st.subheader("3.Weight by sectors")
            dashboard.show_sector_weights()
            st.subheader("4.Weight by country")
            dashboard.show_country_weights()
            st.subheader("5.Dividends")
            dashboard.show_dividends()
            st.subheader("6.Top holdings")
            dashboard.show_top_holdings()
            st.subheader("7.News")
            dashboard.show_news()
            st.subheader("8.TrackInsight")
            dashboard.show_trackinsight_page()
