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
            st.subheader("1.Key information", anchor="1")
            dashboard.show_key_info()
            st.subheader("2.Historical market data", anchor="2")
            dashboard.show_historical_data()
            st.subheader("3.Weight by sectors", anchor="3")
            dashboard.show_sector_weights()
            st.subheader("4.Weight by country", anchor="4")
            dashboard.show_country_weights()
            st.subheader("5.Dividends", anchor="5")
            dashboard.show_dividends()
            st.subheader("6.Top holdings", anchor="6")
            dashboard.show_top_holdings()
            st.subheader("7.News", anchor="7")
            dashboard.show_news()
            st.subheader("8.TrackInsight", anchor="8")
            dashboard.show_trackinsight_page()

            with st.sidebar:
                st.markdown("[1. Key information](#1)")
                st.markdown("[2. Historical market data](#2)")
                st.markdown("[3. Weight by sectors](#3)")
                st.markdown("[4. Weight by country](#4)")
                st.markdown("[5. Dividends](#5)")
                st.markdown("[6. Top holdings](#6)")
                st.markdown("[7. News](#7)")
                st.markdown("[8. Trackinsights](#8)")

                with open("style.css") as f:
                    style = f"<style>{f.read()}</style>"
                st.markdown(style, unsafe_allow_html=True)
