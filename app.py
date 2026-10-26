import streamlit as st
import pandas as pd
import yfinance as yf
import os
import requests
import matplotlib.pyplot as plt
from io import BytesIO



def calculate_rsi(close, period=14):

    delta = close.diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()

    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    return 100 - (100 / (1 + rs))
def calculate_macd(close):

    ema12 = close.ewm(
        span=12,
        adjust=False
    ).mean()

    ema26 = close.ewm(
        span=26,
        adjust=False
    ).mean()

    macd = ema12 - ema26

    signal = macd.ewm(
        span=9,
        adjust=False
    ).mean()

    histogram = macd - signal

    return (
        macd,
        signal,
        histogram
    )
def calculate_obv(df):

    obv = [0]

    for i in range(
        1,
        len(df)
    ):

        if (
            df["Close"].iloc[i]
            >
            df["Close"].iloc[i-1]
        ):

            obv.append(
                obv[-1]
                + df["Volume"].iloc[i]
            )

        elif (
            df["Close"].iloc[i]
            <
            df["Close"].iloc[i-1]
        ):

            obv.append(
                obv[-1]
                - df["Volume"].iloc[i]
            )

        else:

            obv.append(obv[-1])

    return obv

# =========================
# SIDEBAR
# =========================

menu = st.sidebar.radio(
    "📋 Menu",
    ["Saham", "FPL"]
)

if menu == "Saham":

    submenu = st.sidebar.radio(
        "Menu Saham",
        [
            "IDX Nexus",
            "Portfolio Radar",
            "Analisa Saham",
            "Breakout Scanner",
            "Support Resistance",
            "Avg Down Planner",
            "Value Screener",
            "Price Momentum",
            "Dividend Tracker",
            "Dividend Momentum",
            "Right Issue Calc",
            "MyPorto",
            "Import Portfolio"
        ]
    )

else:

    submenu = st.sidebar.radio(
        "Menu FPL",
        [
            "Home",
            "Fixtures",
            "My Team",
            "Best XI",
            "League Info",
            "Standings",
            "Statistics",
            "Captain Picks",
            "Rival Analyzer",
            "Transfer Activity",
            "Transfer Trends"
        ]
    )

menu = submenu



# =========================
# PAGES
# =========================
if menu == "Home":


                
elif menu == "IDX Nexus":


    st.title("📈 IDX Nexus")

    portfolio_file = "portfolio.csv"

    if not os.path.exists(
        portfolio_file
    ):

        st.warning(
            "Portfolio belum dibuat. Tambahkan saham di menu MyPorto."
        )

        st.stop()

    portfolio_df = pd.read_csv(
        portfolio_file
    )

    if portfolio_df.empty:

        st.warning(
            "Portfolio kosong."
        )

        st.stop()

    idx_menu = st.radio(
        "Module",
        [
            "Watchlist",
            "Stock Detail",
            "Compare Stocks",
            "Value Screener"
        ],
        horizontal=True
    )

    # ==================================
    # WATCHLIST
    # ==================================

    if idx_menu == "Watchlist":

        rows = []

        for _, row in portfolio_df.iterrows():

            try:

                ticker = (
                    str(
                        row["Ticker"]
                    ).upper()
                    + ".JK"
                )

                stock = yf.Ticker(
                    ticker
                )

                hist = stock.history(
                    period="5d"
                )

                if hist.empty:
                    continue

                current = round(
                    hist["Close"]
                    .iloc[-1],
                    2
                )

                prev = round(
                    hist["Close"]
                    .iloc[-2],
                    2
                )

                change_pct = round(
                    (
                        (
                            current
                            - prev
                        )
                        / prev
                    )
                    * 100,
                    2
                )

                shares = (
                    row["Lot"]
                    * 100
                )

                market_value = (
                    current
                    * shares
                )

                cost_value = (
                    row["Avg Buy"]
                    * shares
                )

                pnl = (
                    market_value
                    - cost_value
                )

                pnl_pct = round(
                    (
                        pnl
                        /
                        cost_value
                    )
                    * 100,
                    2
                )

                rows.append(
                    {
                        "Ticker":
                        row["Ticker"],

                        "Lot":
                        row["Lot"],

                        "Avg Buy":
                        row["Avg Buy"],

                        "Current":
                        current,

                        "Day %":
                        change_pct,

                        "P/L":
                        round(
                            pnl
                        ),

                        "P/L %":
                        pnl_pct
                    }
                )

            except Exception:

                continue

        watchlist_df = pd.DataFrame(
            rows
        )

        st.dataframe(
            watchlist_df,
            hide_index=True,
            use_container_width=True
        )

        if not watchlist_df.empty:

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Stocks",
                    len(
                        watchlist_df
                    )
                )

            with col2:

                st.metric(
                    "Top Winner",
                    watchlist_df
                    .sort_values(
                        "P/L %",
                        ascending=False
                    )
                    .iloc[0]["Ticker"]
                )

            with col3:

                st.metric(
                    "Top Loser",
                    watchlist_df
                    .sort_values(
                        "P/L %"
                    )
                    .iloc[0]["Ticker"]
                )

    # ==================================
    # STOCK DETAIL
    # ==================================

    elif idx_menu == "Stock Detail":

        selected = st.selectbox(
            "Stock",
            portfolio_df[
                "Ticker"
            ]
        )

        try:

            stock = yf.Ticker(
                selected
                + ".JK"
            )

            hist = stock.history(
                period="1y"
            )

            if hist.empty:

                st.warning(
                    "Data tidak ditemukan."
                )

            else:

                current = round(
                    hist["Close"]
                    .iloc[-1],
                    2
                )

                high52 = round(
                    hist["High"]
                    .max(),
                    2
                )

                low52 = round(
                    hist["Low"]
                    .min(),
                    2
                )

                volume = int(
                    hist["Volume"]
                    .iloc[-1]
                )

                col1, col2, col3, col4 = st.columns(
                    4
                )

                with col1:

                    st.metric(
                        "Price",
                        current
                    )

                with col2:

                    st.metric(
                        "52W High",
                        high52
                    )

                with col3:

                    st.metric(
                        "52W Low",
                        low52
                    )

                with col4:

                    st.metric(
                        "Volume",
                        f"{volume:,}"
                    )

                st.subheader(
                    "1 Year Chart"
                )

                st.line_chart(
                    hist["Close"]
                )

                st.subheader(
                    "Recent Prices"
                )

                st.dataframe(
                    hist.tail(30),
                    use_container_width=True
                )

        except Exception as e:

            st.error(e)
       
    
            
        
            

     

    # ==================================
    # COMPARE
    # ==================================

    elif idx_menu == "Compare Stocks":

        tickers = (
            portfolio_df[
                "Ticker"
            ]
            .tolist()
        )

        if len(tickers) < 2:

            st.warning(
                "Minimal 2 saham."
            )

        else:

            col1, col2 = st.columns(
                2
            )

            with col1:

                stock1 = st.selectbox(
                    "Stock 1",
                    tickers
                )

            with col2:

                stock2 = st.selectbox(
                    "Stock 2",
                    tickers,
                    index=1
                )

            try:

                hist1 = yf.Ticker(
                    stock1 + ".JK"
                ).history(
                    period="6mo"
                )

                hist2 = yf.Ticker(
                    stock2 + ".JK"
                ).history(
                    period="6mo"
                )

                price1 = round(
                    hist1["Close"]
                    .iloc[-1],
                    2
                )

                price2 = round(
                    hist2["Close"]
                    .iloc[-1],
                    2
                )

                change1 = round(
                    (
                        (
                            price1
                            -
                            hist1["Close"]
                            .iloc[0]
                        )
                        /
                        hist1["Close"]
                        .iloc[0]
                    )
                    * 100,
                    2
                )

                change2 = round(
                    (
                        (
                            price2
                            -
                            hist2["Close"]
                            .iloc[0]
                        )
                        /
                        hist2["Close"]
                        .iloc[0]
                    )
                    * 100,
                    2
                )

                compare_df = pd.DataFrame(
                    [
                        {
                            "Metric":
                            "Price",

                            stock1:
                            price1,

                            stock2:
                            price2
                        },
                        {
                            "Metric":
                            "6M Return %",

                            stock1:
                            change1,

                            stock2:
                            change2
                        }
                    ]
                )

                st.dataframe(
                    compare_df,
                    hide_index=True,
                    use_container_width=True
                )

                chart_df = pd.DataFrame(
                    {
                        stock1:
                        hist1["Close"],

                        stock2:
                        hist2["Close"]
                    }
                )

                st.subheader(
                    "6 Month Comparison"
                )

                st.line_chart(
                    chart_df
                )

            except Exception as e:

                st.error(e)

            
elif menu == "Value Screener":

    st.title("💰 Value Screener")

    portfolio_file = "portfolio.csv"

    if not os.path.exists(
        portfolio_file
    ):

        st.warning(
            "Portfolio belum ada."
        )

        st.stop()

    portfolio_df = pd.read_csv(
        portfolio_file
    )

    if portfolio_df.empty:

        st.warning(
            "Portfolio kosong."
        )

        st.stop()

    rows = []

    for _, row in portfolio_df.iterrows():

        try:

            ticker = (
                str(
                    row["Ticker"]
                ).upper()
                + ".JK"
            )

            stock = yf.Ticker(
                ticker
            )

            info = stock.info

            current = info.get(
                "currentPrice"
            )

            pe = info.get(
                "trailingPE"
            )

            pbv = info.get(
                "priceToBook"
            )

            dividend = info.get(
                "dividendYield"
            )

            avg_buy = float(
                row["Avg Buy"]
            )

            profit_pct = None

            if current:

                profit_pct = round(
                    (
                        (
                            current
                            - avg_buy
                        )
                        / avg_buy
                    ) * 100,
                    2
                )

            status = "HOLD"

            if (
                pe is not None
                and pbv is not None
            ):

                if (
                    pe < 12
                    and pbv < 1.5
                ):

                    status = "BUY"

                elif (
                    pbv > 4
                    and profit_pct is not None
                    and profit_pct > 30
                ):

                    status = "TAKE PROFIT"

            rows.append(
                {
                    "Ticker":
                    row["Ticker"],

                    "Current":
                    current,

                    "Avg Buy":
                    avg_buy,

                    "Profit %":
                    profit_pct,

                    "PE":
                    pe,

                    "PBV":
                    pbv,

                    "Dividend %":
                    round(
                        dividend * 100,
                        2
                    )
                    if dividend
                    else None,

                    "Status":
                    status
                }
            )

        except Exception as e:

            st.error(
                f"{row['Ticker']} : {e}"
            )

    screen_df = pd.DataFrame(
        rows
    )

    if screen_df.empty:

        st.warning(
            "No data loaded"
        )

    else:

        st.dataframe(
            screen_df,
            hide_index=True,
            use_container_width=True
        )

        st.divider()

        st.subheader(
            "✅ Buy Candidates"
        )

        buy_df = screen_df[
            screen_df["Status"]
            == "BUY"
        ]

        if buy_df.empty:

            st.info(
                "No buy candidates."
            )

        else:

            st.dataframe(
                buy_df,
                hide_index=True,
                use_container_width=True
            )

        st.divider()

        st.subheader(
            "⚠️ Take Profit Candidates"
        )

        tp_df = screen_df[
            screen_df["Status"]
            == "TAKE PROFIT"
        ]

        if tp_df.empty:

            st.info(
                "No take profit candidates."
            )

        else:

            st.dataframe(
                tp_df,
                hide_index=True,
                use_container_width=True
            )

        st.divider()

        st.subheader(
            "🏆 Lowest PBV"
        )

        cheap_df = (
            screen_df
            .dropna(
                subset=["PBV"]
            )
            .sort_values(
                "PBV"
            )
        )

        st.dataframe(
            cheap_df.head(10),
            hide_index=True,
            use_container_width=True
        )

                        
elif menu == "MyPorto":

    st.title("📁 My Portfolio")

    PORTFOLIO_FILE = "portfolio.csv"

    # Create file first time
    if not os.path.exists(PORTFOLIO_FILE):

        pd.DataFrame(
            columns=[
                "Ticker",
                "Lot",
                "Avg Buy"
            ]
        ).to_csv(
            PORTFOLIO_FILE,
            index=False,
            float_format="%.2f"
        )

    portfolio_df = pd.read_csv(PORTFOLIO_FILE)

    if not portfolio_df.empty:

        portfolio_df["Lot"] = pd.to_numeric(
            portfolio_df["Lot"],
            errors="coerce"
        ).fillna(0).astype(int)

        portfolio_df["Avg Buy"] = pd.to_numeric(
            portfolio_df["Avg Buy"],
            errors="coerce"
        ).fillna(0).astype(float)

    st.subheader("➕ Add / Update Position")

    col1, col2, col3 = st.columns(3)

    with col1:

        ticker = st.text_input(
            "Ticker",
            placeholder="BBCA"
        )

    with col2:

        lot = st.number_input(
            "Lot",
            min_value=1,
            value=100
        )

    with col3:

        avg_buy = st.number_input(
            "Buy Price",
            min_value=0.01,
            value=1000.00,
            step=0.01,
            format="%.2f"
        )

    if st.button("Save Position"):

        ticker = ticker.upper().strip()

        if ticker:

            existing = portfolio_df[
                portfolio_df["Ticker"] == ticker
            ]

            if not existing.empty:

                old_lot = int(
                    existing.iloc[0]["Lot"]
                )

                old_avg = float(
                    existing.iloc[0]["Avg Buy"]
                )

                total_lot = old_lot + lot

                new_avg = (
                    (old_lot * old_avg)
                    +
                    (lot * avg_buy)
                ) / total_lot

                portfolio_df.loc[
                    portfolio_df["Ticker"] == ticker,
                    "Lot"
                ] = total_lot

                portfolio_df.loc[
                    portfolio_df["Ticker"] == ticker,
                    "Avg Buy"
                ] = round(new_avg, 2)

                portfolio_df.to_csv(
                    PORTFOLIO_FILE,
                    index=False,
                    float_format="%.2f"
                )

                st.success(
                    f"""
✅ Updated {ticker}

Total Lot : {total_lot}

Average Buy : {new_avg:.2f}
"""
                )

            else:

                new_row = pd.DataFrame([
                    {
                        "Ticker": ticker,
                        "Lot": int(lot),
                        "Avg Buy": round(
                            float(avg_buy),
                            2
                        )
                    }
                ])

                portfolio_df = pd.concat(
                    [
                        portfolio_df,
                        new_row
                    ],
                    ignore_index=True
                )

                portfolio_df.to_csv(
                    PORTFOLIO_FILE,
                    index=False,
                    float_format="%.2f"
                )

                st.success(
                    f"{ticker} added."
                )

            st.rerun()

    st.divider()

    st.subheader("📊 Holdings")

    portfolio_df = pd.read_csv(PORTFOLIO_FILE)

    if portfolio_df.empty:

        st.info("Portfolio is empty.")

    else:

        portfolio_df["Avg Buy"] = pd.to_numeric(
            portfolio_df["Avg Buy"],
            errors="coerce"
        ).round(2)

        display_df = portfolio_df.copy()

        display_df["Avg Buy"] = display_df[
            "Avg Buy"
        ].map(
            lambda x: f"{x:.2f}"
        )

        st.metric(
            "Total Stocks",
            len(display_df)
        )

        st.dataframe(
            display_df.sort_values(
                "Ticker"
            ),
            hide_index=True,
            use_container_width=True
        )

        st.divider()

        st.subheader("🗑 Delete Stock")

        delete_ticker = st.selectbox(
            "Select Stock",
            portfolio_df["Ticker"]
        )

        if st.button("Delete Stock"):

            portfolio_df = portfolio_df[
                portfolio_df["Ticker"]
                != delete_ticker
            ]

            portfolio_df.to_csv(
                PORTFOLIO_FILE,
                index=False,
                float_format="%.2f"
            )

            st.success(
                f"{delete_ticker} deleted."
            )

            st.rerun()

        st.divider()

        csv_data = portfolio_df.to_csv(
            index=False,
            float_format="%.2f"
        )

        st.download_button(
            label="📥 Download Portfolio CSV",
            data=csv_data,
            file_name="portfolio.csv",
            mime="text/csv"
        )

elif menu == "Price Momentum":

    st.title("🚀 Price Momentum")

    portfolio_file = "portfolio.csv"

    if not os.path.exists(
        portfolio_file
    ):

        st.warning(
            "Portfolio belum ada."
        )

        st.stop()

    portfolio_df = pd.read_csv(
        portfolio_file
    )

    rows = []

    for _, row in portfolio_df.iterrows():

        try:

            ticker = row["Ticker"]

            avg_buy = float(
                row["Avg Buy"]
            )

            hist = yf.Ticker(
                ticker + ".JK"
            ).history(
                period="1y"
            )

            if len(hist) < 130:

                continue

            close = hist["Close"]

            current_price = float(
                close.iloc[-1]
            )

            low_52w = float(
                close.min()
            )

            high_52w = float(
                close.max()
            )

            ret_1m = round(
                (
                    (
                        current_price
                        - close.iloc[-21]
                    )
                    /
                    close.iloc[-21]
                )
                * 100,
                2
            )

            ret_3m = round(
                (
                    (
                        current_price
                        - close.iloc[-63]
                    )
                    /
                    close.iloc[-63]
                )
                * 100,
                2
            )

            ret_6m = round(
                (
                    (
                        current_price
                        - close.iloc[-126]
                    )
                    /
                    close.iloc[-126]
                )
                * 100,
                2
            )

            ma20 = (
                close
                .tail(20)
                .mean()
            )

            ma50 = (
                close
                .tail(50)
                .mean()
            )

            vol_ratio = (
                hist["Volume"]
                .iloc[-1]
                /
                hist["Volume"]
                .tail(20)
                .mean()
            )

            discount_avg = round(
                (
                    (
                        current_price
                        - avg_buy
                    )
                    /
                    avg_buy
                )
                * 100,
                2
            )

            score = 0

            if ret_1m > 5:
                score += 1

            if ret_3m > 15:
                score += 2

            if ret_6m > 30:
                score += 2

            if current_price > ma20:
                score += 1

            if current_price > ma50:
                score += 1

            if (
                current_price
                >= high_52w * 0.95
            ):
                score += 2

            if vol_ratio > 1.5:
                score += 1

            if score >= 8:

                rating = "🚀 Strong Momentum"

            elif score >= 5:

                rating = "📈 Uptrend"

            else:

                rating = "⏸ Sideways"

            rows.append(
                {
                    "Ticker":
                    ticker,

                    "Avg Buy":
                    round(avg_buy),

                    "Price":
                    round(current_price),

                    "Disc Avg %":
                    discount_avg,

                    "1M %":
                    ret_1m,

                    "3M %":
                    ret_3m,

                    "6M %":
                    ret_6m,

                    "52W Low":
                    round(low_52w),

                    "52W High":
                    round(high_52w),

                    "Rating":
                    rating,

                    "Score":
                    score
                }
            )

        except:
            pass

    momentum_df = pd.DataFrame(
        rows
    )

    if momentum_df.empty:

        st.warning(
            "No data found."
        )

    else:

        momentum_df = (
            momentum_df
            .sort_values(
                "Score",
                ascending=False
            )
        )

        st.subheader(
            "📈 Portfolio Momentum"
        )

        st.dataframe(
            momentum_df[
                [
                    "Ticker",
                    "Avg Buy",
                    "Price",
                    "Disc Avg %",
                    "1M %",
                    "3M %",
                    "6M %",
                    "52W Low",
                    "52W High",
                    "Rating"
                ]
            ],
            hide_index=True,
            use_container_width=True
        )

        st.divider()

        st.subheader(
            "🏆 Top 5 Recommendation"
        )

        top5 = momentum_df.head(5)

        for i, (_, row) in enumerate(
            top5.iterrows(),
            start=1
        ):

            st.success(
                f"""
#{i} {row['Ticker']}

Price : {row['Price']:,.0f}

Avg Buy :
{row['Avg Buy']:,.0f}

1M : {row['1M %']}%
3M : {row['3M %']}%
6M : {row['6M %']}%

52W Range :
{row['52W Low']:,.0f}
-
{row['52W High']:,.0f}

{row['Rating']}
"""
            )

        st.divider()

        st.subheader(
            "🎯 Average Down Opportunities"
        )

        avg_down_df = momentum_df[
            (
                momentum_df[
                    "Disc Avg %"
                ]
                < 0
            )
            &
            (
                momentum_df[
                    "Rating"
                ]
                != "⏸ Sideways"
            )
        ]

        if avg_down_df.empty:

            st.info(
                "No average down opportunities."
            )

        else:

            avg_down_df = (
                avg_down_df
                .sort_values(
                    "Disc Avg %",
                    ascending=True
                )
            )

            st.dataframe(
                avg_down_df[
                    [
                        "Ticker",
                        "Avg Buy",
                        "Price",
                        "Disc Avg %",
                        "Rating"
                    ]
                ],
                hide_index=True,
                use_container_width=True
            )

        st.divider()

        wa_text = (
            "🚀 PRICE MOMENTUM\n\n"
        )

        wa_text += (
            "🏆 TOP MOMENTUM\n\n"
        )

        for i, (_, row) in enumerate(
            top5.iterrows(),
            start=1
        ):

            wa_text += (
                f"{i}. {row['Ticker']}\n"
                f"Price {row['Price']:,.0f}\n"
                f"3M {row['3M %']}%\n"
                f"6M {row['6M %']}%\n"
                f"{row['Rating']}\n\n"
            )

        if not avg_down_df.empty:

            wa_text += (
                "🎯 AVG DOWN\n\n"
            )

            for _, row in (
                avg_down_df
                .head(5)
                .iterrows()
            ):

                wa_text += (
                    f"• {row['Ticker']}\n"
                    f"Avg {row['Avg Buy']:,.0f}\n"
                    f"Now {row['Price']:,.0f}\n"
                    f"{row['Disc Avg %']}%\n"
                    f"{row['Rating']}\n\n"
                )

        st.subheader(
            "📱 Copy To WhatsApp"
        )

        st.code(
            wa_text,
            language="text"
        )
elif menu == "Dividend Tracker":

    st.title("💰 Dividend Tracker")

    portfolio_file = "portfolio.csv"

    if not os.path.exists(
        portfolio_file
    ):

        st.warning(
            "Portfolio belum ada."
        )

        st.stop()

    portfolio_df = pd.read_csv(
        portfolio_file
    )

    rows = []

    total_dividend = 0

    for _, row in portfolio_df.iterrows():

        try:

            ticker = row["Ticker"]

            stock = yf.Ticker(
                ticker + ".JK"
            )

            hist = stock.history(
                period="1y"
            )

            if hist.empty:
                continue

            price = float(
                hist["Close"]
                .iloc[-1]
            )

            dividends = stock.dividends

            dividend = 0

            if not dividends.empty:

                dividend = float(
                    dividends.tail(1)
                    .iloc[0]
                )

            shares = (
                int(row["Lot"])
                * 100
            )

            avg_buy = float(
                row["Avg Buy"]
            )

            cash_dividend = (
                dividend
                * shares
            )

            total_dividend += (
                cash_dividend
            )

            yield_pct = round(
                (
                    dividend
                    / price
                )
                * 100,
                2
            ) if price else 0

            yoc = round(
                (
                    dividend
                    / avg_buy
                )
                * 100,
                2
            ) if avg_buy else 0

            rows.append(
                {
                    "Ticker":
                    ticker,

                    "Price":
                    round(price),

                    "Dividend":
                    round(
                        dividend,
                        2
                    ),

                    "Yield %":
                    yield_pct,

                    "YOC %":
                    yoc,

                    "Shares":
                    shares,

                    "Cash Dividend":
                    round(
                        cash_dividend
                    )
                }
            )

        except:
            pass

    dividend_df = pd.DataFrame(
        rows
    )

    dividend_df = (
        dividend_df
        .sort_values(
            "Cash Dividend",
            ascending=False
        )
    )

    st.metric(
        "💵 Total Estimated Dividend",
        f"Rp {total_dividend:,.0f}"
    )

    st.dataframe(
        dividend_df,
        hide_index=True,
        use_container_width=True
    )

    wa_text = (
        "💰 DIVIDEND TRACKER\n\n"
        f"Total Portfolio Dividend\n"
        f"Rp {total_dividend:,.0f}\n\n"
    )

    for _, row in (
        dividend_df.head(5)
        .iterrows()
    ):

        wa_text += (
            f"• {row['Ticker']}\n"
            f"Yield {row['Yield %']}%\n"
            f"Cash Rp {row['Cash Dividend']:,.0f}\n\n"
        )

    st.subheader(
        "📱 Copy To WhatsApp"
    )

    st.code(
        wa_text,
        language="text"
    )
elif menu == "Dividend Momentum":

    st.title("💰 Dividend Momentum")

    portfolio_file = "portfolio.csv"

    if not os.path.exists(
        portfolio_file
    ):

        st.warning(
            "Portfolio belum ada."
        )

        st.stop()

    portfolio_df = pd.read_csv(
        portfolio_file
    )

    rows = []

    total_dividend = 0

    for _, row in portfolio_df.iterrows():

        try:

            ticker = row["Ticker"]

            stock = yf.Ticker(
                ticker + ".JK"
            )

            hist = stock.history(
                period="1y"
            )

            if hist.empty:
                continue

            current_price = float(
                hist["Close"]
                .iloc[-1]
            )

            dividends = stock.dividends

            dividend_per_share = 0

            if not dividends.empty:

                dividend_per_share = float(
                    dividends.tail(1)
                    .iloc[0]
                )

            shares = (
                int(row["Lot"])
                * 100
            )

            avg_buy = float(
                row["Avg Buy"]
            )

            current_yield = round(
                (
                    dividend_per_share
                    / current_price
                )
                * 100,
                2
            ) if current_price else 0

            yoc = round(
                (
                    dividend_per_share
                    / avg_buy
                )
                * 100,
                2
            ) if avg_buy else 0

            cash_dividend = (
                dividend_per_share
                * shares
            )

            total_dividend += (
                cash_dividend
            )

            score = 0

            if current_yield >= 8:

                score += 3

            elif current_yield >= 6:

                score += 2

            elif current_yield >= 4:

                score += 1

            if yoc > current_yield:

                score += 1

            if current_price < avg_buy:

                score += 1

            if score >= 4:

                rating = "🔥 Strong"

            elif score >= 2:

                rating = "✅ Good"

            else:

                rating = "⚠️ Weak"

            rows.append(
                {
                    "Ticker":
                    ticker,

                    "Price":
                    round(
                        current_price,
                        0
                    ),

                    "Dividend":
                    round(
                        dividend_per_share,
                        2
                    ),

                    "Yield %":
                    current_yield,

                    "YOC %":
                    yoc,

                    "Cash Dividend":
                    round(
                        cash_dividend
                    ),

                    "Rating":
                    rating
                }
            )

        except:
            pass

    dividend_df = pd.DataFrame(
        rows
    )

    if dividend_df.empty:

        st.warning(
            "No dividend data found."
        )

    else:

        dividend_df = (
            dividend_df
            .sort_values(
                "Yield %",
                ascending=False
            )
        )

        st.metric(
            "💵 Expected Dividend",
            f"Rp {total_dividend:,.0f}"
        )

        st.dataframe(
            dividend_df,
            hide_index=True,
            use_container_width=True
        )

        st.subheader(
            "🏆 Top Dividend Opportunities"
        )

        st.dataframe(
            dividend_df.head(5),
            hide_index=True,
            use_container_width=True
        )

        wa_text = (
            "💰 DIVIDEND MOMENTUM\n\n"
        )

        wa_text += (
            f"Expected Dividend\n"
            f"Rp {total_dividend:,.0f}\n\n"
        )

        for _, row in (
            dividend_df.head(5)
            .iterrows()
        ):

            wa_text += (
                f"• {row['Ticker']}\n"
                f"Yield {row['Yield %']}%\n"
                f"YOC {row['YOC %']}%\n"
                f"Cash Rp {row['Cash Dividend']:,.0f}\n\n"
            )

        st.subheader(
            "📱 Copy To WhatsApp"
        )

        st.code(
            wa_text,
            language="text"
        )
elif menu == "Right Issue Calc":

    st.title(
        "🎁 Right Issue Calculator"
    )

    portfolio_file = "portfolio.csv"

    if not os.path.exists(
        portfolio_file
    ):

        st.warning(
            "Portfolio belum ada."
        )

        st.stop()

    portfolio_df = pd.read_csv(
        portfolio_file
    )

    ticker = st.selectbox(
        "Ticker",
        portfolio_df["Ticker"]
    )

    row = portfolio_df[
        portfolio_df["Ticker"]
        == ticker
    ].iloc[0]

    lots = int(
        row["Lot"]
    )

    avg_buy = float(
        row["Avg Buy"]
    )

    shares = lots * 100

    current_price = 0

    try:

        hist = yf.Ticker(
            ticker + ".JK"
        ).history(
            period="5d"
        )

        current_price = float(
            hist["Close"].iloc[-1]
        )

    except:
        pass

    st.subheader(
        "📋 Rights Issue Parameters"
    )

    col1, col2 = st.columns(2)

    with col1:

        rights_price = st.number_input(
            "RI Price",
            min_value=1.0,
            value=max(
                current_price * 0.8,
                1.0
            )
        )

    with col2:

        cum_date = st.text_input(
            "Cum Date",
            ""
        )

    st.markdown(
        "### Ratio"
    )

    col1, col2 = st.columns(2)

    with col1:

        ratio_old = st.number_input(
            "Existing Shares",
            min_value=1,
            value=5
        )

    with col2:

        ratio_new = st.number_input(
            "New Shares",
            min_value=1,
            value=1
        )

    rights_shares = int(
        shares
        * ratio_new
        / ratio_old
    )

    funds_needed = (
        rights_shares
        * rights_price
    )

    discount = round(
        (
            (
                current_price
                - rights_price
            )
            / current_price
        )
        * 100,
        2
    ) if current_price else 0

    terp = round(
        (
            (
                ratio_old
                * current_price
            )
            +
            (
                ratio_new
                * rights_price
            )
        )
        /
        (
            ratio_old
            + ratio_new
        ),
        2
    ) if current_price else 0

    profit_to_terp = round(
        (
            (
                current_price
                - terp
            )
            / terp
        )
        * 100,
        2
    ) if terp else 0

    st.subheader(
        "📊 RI Analysis"
    )

    result_df = pd.DataFrame(
        [
            {
                "Metric": "Current Price",
                "Value":
                f"{current_price:,.0f}"
            },
            {
                "Metric": "RI Price",
                "Value":
                f"{rights_price:,.0f}"
            },
            {
                "Metric": "Discount",
                "Value":
                f"{discount:.2f}%"
            },
            {
                "Metric": "Ratio",
                "Value":
                f"{ratio_old}:{ratio_new}"
            },
            {
                "Metric": "Owned Shares",
                "Value":
                f"{shares:,}"
            },
            {
                "Metric": "Rights Shares",
                "Value":
                f"{rights_shares:,}"
            },
            {
                "Metric": "Funds Needed",
                "Value":
                f"Rp {funds_needed:,.0f}"
            },
            {
                "Metric": "TERP",
                "Value":
                f"{terp:,.0f}"
            },
            {
                "Metric": "Premium vs TERP",
                "Value":
                f"{profit_to_terp:.2f}%"
            },
            {
                "Metric": "Avg Buy",
                "Value":
                f"{avg_buy:,.0f}"
            }
        ]
    )

    st.dataframe(
        result_df,
        hide_index=True,
        use_container_width=True
    )

    score = 0

    if discount >= 20:

        score += 3

    elif discount >= 10:

        score += 2

    elif discount >= 5:

        score += 1

    if current_price > terp:

        score += 2

    if score >= 5:

        rating = "🔥 Attractive"

    elif score >= 3:

        rating = "⚠️ Neutral"

    else:

        rating = "🚫 Less Attractive"

    st.metric(
        "RI Rating",
        rating
    )

    st.divider()

    wa_text = (
        "🎁 RIGHTS ISSUE ANALYZER\n\n"
        f"{ticker}\n\n"
        f"Current Price : {current_price:,.0f}\n"
        f"RI Price : {rights_price:,.0f}\n"
        f"Discount : {discount:.2f}%\n\n"
        f"Ratio : {ratio_old}:{ratio_new}\n"
        f"Shares Owned : {shares:,}\n"
        f"HMETD : {rights_shares:,}\n\n"
        f"Need Funds : Rp {funds_needed:,.0f}\n"
        f"TERP : {terp:,.0f}\n"
        f"Premium vs TERP : {profit_to_terp:.2f}%\n\n"
        f"Rating : {rating}"
    )

    if cum_date:

        wa_text += (
            f"\nCum Date : {cum_date}"
        )

    st.subheader(
        "📱 Copy To WhatsApp"
    )

    st.code(
        wa_text,
        language="text"
    )
elif menu == "Transfer Trends":

    st.title("🔥 Transfer Trends")

    LEAGUE_ID = 147447

    try:

        bootstrap = requests.get(
            "https://fantasy.premierleague.com/api/bootstrap-static/",
            timeout=20
        ).json()

        players = pd.DataFrame(
            bootstrap["elements"]
        )

        player_lookup = dict(
            zip(
                players["id"],
                players["web_name"]
            )
        )

        league = requests.get(
            f"https://fantasy.premierleague.com/api/leagues-classic/{LEAGUE_ID}/standings/",
            timeout=20
        ).json()

        standings = pd.DataFrame(
            league["standings"]["results"]
        )

        current_gw = next(
            e["id"]
            for e in bootstrap["events"]
            if e["is_current"]
        )

        selected_gw = st.selectbox(
            "Gameweek",
            list(range(1, current_gw + 2))
        )

        transfers_in = []
        transfers_out = []

        latest_transfers = []

        no_transfer_teams = []

        progress = st.progress(0)

        for idx, row in standings.iterrows():

            try:

                entry_id = row["entry"]

                transfers = requests.get(
                    f"https://fantasy.premierleague.com/api/entry/{entry_id}/transfers/",
                    timeout=20
                ).json()

                gw_transfers = [
                    t
                    for t in transfers
                    if t["event"] == selected_gw
                ]

                if len(gw_transfers) == 0:

                    no_transfer_teams.append(
                        {
                            "Team": row["entry_name"],
                            "Manager": row["player_name"]
                        }
                    )

                for t in gw_transfers:

                    player_in = player_lookup.get(
                        t["element_in"],
                        "Unknown"
                    )

                    player_out = player_lookup.get(
                        t["element_out"],
                        "Unknown"
                    )

                    transfers_in.append(
                        player_in
                    )

                    transfers_out.append(
                        player_out
                    )

                    latest_transfers.append(
                        {
                            "Team": row["entry_name"],
                            "Manager": row["player_name"],
                            "OUT": player_out,
                            "IN": player_in,
                            "Time": t["time"]
                        }
                    )

                progress.progress(
                    (idx + 1)
                    / len(standings)
                )

            except Exception:
                pass

        progress.empty()

        # Most Bought

        st.subheader(
            f"📈 Most Bought GW{selected_gw}"
        )

        if transfers_in:

            bought_df = (
                pd.Series(
                    transfers_in
                )
                .value_counts()
                .reset_index()
            )

            bought_df.columns = [
                "Player",
                "Bought"
            ]

            st.dataframe(
                bought_df.head(10),
                hide_index=True,
                use_container_width=True
            )

        else:

            bought_df = pd.DataFrame(
                columns=["Player", "Bought"]
            )

            st.info(
                "No transfers in."
            )

        st.divider()

        # Most Sold

        st.subheader(
            f"📉 Most Sold GW{selected_gw}"
        )

        if transfers_out:

            sold_df = (
                pd.Series(
                    transfers_out
                )
                .value_counts()
                .reset_index()
            )

            sold_df.columns = [
                "Player",
                "Sold"
            ]

            st.dataframe(
                sold_df.head(10),
                hide_index=True,
                use_container_width=True
            )

        else:

            sold_df = pd.DataFrame(
                columns=["Player", "Sold"]
            )

            st.info(
                "No transfers out."
            )

        st.divider()

        # Latest Transfers

        st.subheader(
            "🔄 Latest Transfers"
        )

        if latest_transfers:

            latest_df = pd.DataFrame(
                latest_transfers
            )

            latest_df = latest_df.sort_values(
                "Time",
                ascending=False
            )

            st.dataframe(
                latest_df,
                hide_index=True,
                use_container_width=True
            )

        else:

            st.info(
                "No transfers found."
            )

        st.divider()

        # No Transfer Teams

        st.subheader(
            "🟢 Teams With No Transfer"
        )

        if no_transfer_teams:

            no_transfer_df = pd.DataFrame(
                no_transfer_teams
            )

            st.dataframe(
                no_transfer_df,
                hide_index=True,
                use_container_width=True
            )

            st.caption(
                f"{len(no_transfer_df)} teams rolled transfer"
            )

        else:

            st.success(
                "Everyone made transfers."
            )

        st.divider()

        # WhatsApp Report

        wa_text = (
            f"🔥 GW{selected_gw} TRANSFER TRENDS\n\n"
        )

        wa_text += (
            "📈 TOP 5 BOUGHT\n"
        )

        if not bought_df.empty:

            for _, row in (
                bought_df.head(5)
                .iterrows()
            ):

                wa_text += (
                    f"• {row['Player']} "
                    f"({row['Bought']})\n"
                )

        wa_text += "\n"

        wa_text += (
            "📉 TOP 5 SOLD\n"
        )

        if not sold_df.empty:

            for _, row in (
                sold_df.head(5)
                .iterrows()
            ):

                wa_text += (
                    f"• {row['Player']} "
                    f"({row['Sold']})\n"
                )

        wa_text += "\n"

        wa_text += (
            "🟢 NO TRANSFER\n"
        )

        wa_text += (
            f"{len(no_transfer_teams)} teams\n"
        )

        for team in no_transfer_teams[:5]:

            wa_text += (
                f"• {team['Team']}\n"
            )

        st.subheader(
            "📱 Copy To WhatsApp"
        )

        st.code(
            wa_text,
            language="text"
        )

    except Exception as e:

        st.error(
            f"Error loading trends: {e}"
        )
elif menu == "Rival Analyzer":

    st.title("⚔️ Rival Analyzer")

    LEAGUE_ID = 147447

    try:

        league = requests.get(
            f"https://fantasy.premierleague.com/api/leagues-classic/{LEAGUE_ID}/standings/",
            timeout=20
        ).json()

        standings = pd.DataFrame(
            league["standings"]["results"]
        )

        teams = sorted(
            standings["entry_name"].tolist()
        )

        col1, col2 = st.columns(2)

        with col1:

            team_a = st.selectbox(
                "Team A",
                teams,
                index=0
            )

        with col2:

            team_b = st.selectbox(
                "Team B",
                teams,
                index=min(
                    1,
                    len(teams) - 1
                )
            )

        if team_a != team_b:

            bootstrap = requests.get(
                "https://fantasy.premierleague.com/api/bootstrap-static/",
                timeout=20
            ).json()

            current_gw = next(
                e["id"]
                for e in bootstrap["events"]
                if e["is_current"]
            )

            players = pd.DataFrame(
                bootstrap["elements"]
            )

            player_lookup = dict(
                zip(
                    players["id"],
                    players["web_name"]
                )
            )

            entry_a = standings.loc[
                standings["entry_name"] == team_a,
                "entry"
            ].iloc[0]

            entry_b = standings.loc[
                standings["entry_name"] == team_b,
                "entry"
            ].iloc[0]

            rank_a = standings.loc[
                standings["entry_name"] == team_a,
                "rank"
            ].iloc[0]

            rank_b = standings.loc[
                standings["entry_name"] == team_b,
                "rank"
            ].iloc[0]

            points_a = standings.loc[
                standings["entry_name"] == team_a,
                "total"
            ].iloc[0]

            points_b = standings.loc[
                standings["entry_name"] == team_b,
                "total"
            ].iloc[0]

            picks_a = requests.get(
                f"https://fantasy.premierleague.com/api/entry/{entry_a}/event/{current_gw}/picks/",
                timeout=20
            ).json()

            picks_b = requests.get(
                f"https://fantasy.premierleague.com/api/entry/{entry_b}/event/{current_gw}/picks/",
                timeout=20
            ).json()

            captain_a = "-"
            vice_a = "-"

            for p in picks_a["picks"]:

                if p["is_captain"]:

                    captain_a = player_lookup.get(
                        p["element"],
                        "Unknown"
                    )

                if p["is_vice_captain"]:

                    vice_a = player_lookup.get(
                        p["element"],
                        "Unknown"
                    )

            captain_b = "-"
            vice_b = "-"

            for p in picks_b["picks"]:

                if p["is_captain"]:

                    captain_b = player_lookup.get(
                        p["element"],
                        "Unknown"
                    )

                if p["is_vice_captain"]:

                    vice_b = player_lookup.get(
                        p["element"],
                        "Unknown"
                    )

            squad_a = {
                player_lookup[p["element"]]
                for p in picks_a["picks"]
            }

            squad_b = {
                player_lookup[p["element"]]
                for p in picks_b["picks"]
            }

            common_players = sorted(
                squad_a & squad_b
            )

            only_a = sorted(
                squad_a - squad_b
            )

            only_b = sorted(
                squad_b - squad_a
            )

            st.subheader(
                "📊 Rival Overview"
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    team_a,
                    f"{points_a} pts",
                    delta=f"Rank {rank_a}"
                )

            with col2:

                st.metric(
                    "Points Gap",
                    abs(
                        points_a - points_b
                    )
                )

            with col3:

                st.metric(
                    team_b,
                    f"{points_b} pts",
                    delta=f"Rank {rank_b}"
                )
            st.divider()

            st.subheader(
                "🧢 Captain Comparison"
            )

            cap_df = pd.DataFrame(
                [
                    {
                        "Team": team_a,
                        "Captain": captain_a,
                        "Vice Captain": vice_a
                    },
                    {
                        "Team": team_b,
                        "Captain": captain_b,
                        "Vice Captain": vice_b
                    }
                ]
            )

            st.dataframe(
                cap_df,
                hide_index=True,
                use_container_width=True
            )

            if captain_a != captain_b:

                st.warning(
                    f"""
Captain Differential

{team_a}: {captain_a}

{team_b}: {captain_b}
"""
                )

            st.divider()

            st.subheader(
                "🤝 Common Players"
            )

            common_df = pd.DataFrame(
                {
                    "Player": common_players
                }
            )

            st.metric(
                "Common Players",
                len(common_players)
            )

            st.dataframe(
                common_df,
                hide_index=True,
                use_container_width=True
            )

            st.divider()

            col1, col2 = st.columns(2)

            with col1:

                st.subheader(
                    f"🔵 Only {team_a}"
                )

                only_a_df = pd.DataFrame(
                    {
                        "Player": only_a
                    }
                )

                st.metric(
                    "Unique Picks",
                    len(only_a)
                )

                st.dataframe(
                    only_a_df,
                    hide_index=True,
                    use_container_width=True
                )

            with col2:

                st.subheader(
                    f"🟠 Only {team_b}"
                )

                only_b_df = pd.DataFrame(
                    {
                        "Player": only_b
                    }
                )

                st.metric(
                    "Unique Picks",
                    len(only_b)
                )

                st.dataframe(
                    only_b_df,
                    hide_index=True,
                    use_container_width=True
                )

            similarity = round(
                len(common_players)
                /
                max(
                    len(
                        squad_a | squad_b
                    ),
                    1
                )
                * 100,
                1
            )

            st.divider()

            st.success(
                f"""
Similarity Score

{similarity}%

Common Players:
{len(common_players)}

Differentials:
{len(only_a) + len(only_b)}
"""
            )

            st.divider()

            wa_text = (
                "⚔️ RIVAL ANALYZER\n\n"
            )

            wa_text += (
                f"{team_a}\n"
                f"Rank #{rank_a}\n"
                f"{points_a} pts\n\n"
            )
            wa_text += (
                f"{team_b}\n"
                f"Rank #{rank_b}\n"
                f"{points_b} pts\n\n"
            )

            wa_text += (
                f"📊 Gap: "
                f"{abs(points_a - points_b)} pts\n\n"
            )

            wa_text += (
                f"🧢 Captain\n"
                f"{team_a}: {captain_a}\n"
                f"{team_b}: {captain_b}\n\n"
            )

            wa_text += (
                f"🎖 Vice Captain\n"
                f"{team_a}: {vice_a}\n"
                f"{team_b}: {vice_b}\n\n"
            )

            wa_text += (
                f"🤝 Common Players: "
                f"{len(common_players)}\n"
            )

            wa_text += (
                f"📈 Similarity: "
                f"{similarity}%\n\n"
            )

            wa_text += (
                f"🔵 Only {team_a}: "
                f"{len(only_a)}\n"
            )

            for player in only_a[:5]:
                wa_text += (
                    f"• {player}\n"
                )

            wa_text += "\n"

            wa_text += (
                f"🟠 Only {team_b}: "
                f"{len(only_b)}\n"
            )

            for player in only_b[:5]:
                wa_text += (
                    f"• {player}\n"
                )

            st.subheader(
                "📱 Copy To WhatsApp"
            )

            st.code(
                wa_text,
                language="text"
            )

    except Exception as e:

        st.error(
            f"Error loading rival analysis: {e}"
        )
  

elif menu == "Import Portfolio":

    st.title("📥 Import Portfolio CSV")

    uploaded_file = st.file_uploader(
        "Upload portfolio.csv",
        type=["csv"]
    )

    if uploaded_file:

        try:

            df = pd.read_csv(uploaded_file)

            required_cols = [
                "Ticker",
                "Lot",
                "Avg Buy"
            ]

            if not all(
                col in df.columns
                for col in required_cols
            ):
                st.error(
                    "CSV harus memiliki kolom: Ticker, Lot, Avg Buy"
                )

            else:

                df.to_csv(
                    "portfolio.csv",
                    index=False,
                    float_format="%.2f"
                )

                st.success(
                    "✅ Portfolio berhasil di-import"
                )

                st.dataframe(
                    df,
                    hide_index=True,
                    use_container_width=True
                )

        except Exception as e:

            st.error(
                f"Import gagal: {e}"
            )



elif menu == "Distribution Scanner":

    st.title(
        "⚠️ Distribution Scanner"
    )

    rows = []

    portfolio_df = pd.read_csv(
        "portfolio.csv"
    )

    for _, row in portfolio_df.iterrows():

        try:

            ticker = (
                row["Ticker"]
                + ".JK"
            )

            hist = yf.Ticker(
                ticker
            ).history(
                period="3mo"
            )

            high = (
                hist["High"]
                .iloc[-1]
            )

            low = (
                hist["Low"]
                .iloc[-1]
            )

            close = (
                hist["Close"]
                .iloc[-1]
            )

            open_price = (
                hist["Open"]
                .iloc[-1]
            )

            avg_vol = (
                hist["Volume"]
                .tail(20)
                .mean()
            )

            vol_ratio = (
                hist["Volume"]
                .iloc[-1]
                /
                avg_vol
            )

            upper_shadow = (
                high
                -
                max(
                    close,
                    open_price
                )
            )

            distribution = (
                vol_ratio > 1.5
                and
                upper_shadow >
                ((high-low)*0.4)
            )

            if distribution:

                rows.append(
                    {
                        "Ticker":
                        row["Ticker"],

                        "Volume":
                        round(
                            vol_ratio,
                            2
                        ),

                        "Signal":
                        "DISTRIBUSI"
                    }
                )

        except:
            pass

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True
    )
elif menu == "Avg Down Planner":

    st.title(
        "🎯 Avg Down Planner"
    )

    portfolio_df = pd.read_csv(
        "portfolio.csv"
    )

    ticker = st.selectbox(
        "Stock",
        portfolio_df["Ticker"]
    )

    lot_plan = st.selectbox(
        "Tambah Lot",
        [1,2,5,10,20,50]
    )

    row = portfolio_df[
        portfolio_df["Ticker"]
        == ticker
    ].iloc[0]

    current_lot = int(
        row["Lot"]
    )

    avg_buy = float(
        row["Avg Buy"]
    )

    current_price = yf.Ticker(
        ticker
        + ".JK"
    ).history(
        period="5d"
    )["Close"].iloc[-1]

    current_shares = (
        current_lot
        * 100
    )

    add_shares = (
        lot_plan
        * 100
    )

    new_avg = (
        (
            current_shares
            * avg_buy
        )
        +
        (
            add_shares
            * current_price
        )
    ) / (
        current_shares
        +
        add_shares
    )

    st.metric(
        "Current Avg",
        round(avg_buy)
    )

    st.metric(
        "Current Price",
        round(current_price)
    )

    st.metric(
        "New Avg",
        round(new_avg)
    )

elif menu == "Analisa Saham":

    st.title("📈 Analisa Saham")

    if not os.path.exists("portfolio.csv"):

        st.warning("Portfolio belum ada")
        st.stop()

    portfolio_df = pd.read_csv(
        "portfolio.csv"
    )

    ticker = st.selectbox(
        "Pilih Saham",
        portfolio_df["Ticker"]
    )

    hist = yf.Ticker(
        ticker + ".JK"
    ).history(
        period="1y"
    )

    if hist.empty:

        st.warning(
            "Data tidak ditemukan"
        )

        st.stop()

    hist["MA20"] = (
        hist["Close"]
        .rolling(20)
        .mean()
    )

    hist["MA50"] = (
        hist["Close"]
        .rolling(50)
        .mean()
    )

    hist["RSI"] = calculate_rsi(
        hist["Close"]
    )

    (
        hist["MACD"],
        hist["MACD_SIGNAL"],
        hist["MACD_HIST"]
    ) = calculate_macd(
        hist["Close"]
    )

    hist["OBV"] = calculate_obv(
        hist
    )

    close = float(
        hist["Close"].iloc[-1]
    )

    ma20 = float(
        hist["MA20"].iloc[-1]
    )

    ma50 = float(
        hist["MA50"].iloc[-1]
    )

    rsi = float(
        hist["RSI"].iloc[-1]
    )

    support = round(
        hist["Low"]
        .tail(20)
        .min()
    )

    resistance = round(
        hist["High"]
        .tail(20)
        .max()
    )

    analysis_menu = st.selectbox(
        "Analisa",
        [
            "Dashboard",
            "Support Resistance",
            "RSI MACD",
            "OBV",
            "Volume",
            "Average Down",
            "Full Analysis"
        ]
    )

    if analysis_menu == "Dashboard":

        c1,c2,c3,c4 = st.columns(4)

        c1.metric(
            "Price",
            round(close)
        )

        c2.metric(
            "MA20",
            round(ma20)
        )

        c3.metric(
            "MA50",
            round(ma50)
        )

        c4.metric(
            "RSI",
            round(rsi,2)
        )

        st.line_chart(
            hist[
                [
                    "Close",
                    "MA20",
                    "MA50"
                ]
            ]
        )

    elif analysis_menu == "Support Resistance":

        st.metric(
            "Support",
            support
        )

        st.metric(
            "Resistance",
            resistance
        )

        st.line_chart(
            hist["Close"]
        )

    elif analysis_menu == "RSI MACD":

        c1,c2,c3 = st.columns(3)

        c1.metric(
            "RSI",
            round(rsi,2)
        )

        c2.metric(
            "MACD",
            round(
                hist["MACD"].iloc[-1],
                2
            )
        )

        c3.metric(
            "Signal",
            round(
                hist["MACD_SIGNAL"].iloc[-1],
                2
            )
        )

        st.line_chart(
            hist[
                [
                    "MACD",
                    "MACD_SIGNAL"
                ]
            ]
        )
    elif analysis_menu == "Volume":

        st.subheader(
            "Volume"
        )

        st.bar_chart(
            hist["Volume"]
            .tail(30)
        )

        avg_vol = (
            hist["Volume"]
            .tail(20)
            .mean()
        )

        ratio = round(
            hist["Volume"]
            .iloc[-1]
            / avg_vol,
            2
        )

        st.metric(
            "Volume Ratio",
            f"{ratio}x"
        )

    elif analysis_menu == "OBV":

        st.subheader(
             "📊 On Balance Volume (OBV)"
        )

        st.line_chart(
             hist["OBV"]
        )

        obv_now = hist["OBV"].iloc[-1]
        obv_20 = hist["OBV"].iloc[-20]

    if obv_now > obv_20:

        st.success(
            """
✅ OBV Sedang Naik

Menandakan volume cenderung masuk
ke saham (akumulasi).

Buyer lebih dominan daripada seller.

Biasanya mendukung tren naik.
"""
        )

    else:

        st.warning(
            """
⚠️ OBV Sedang Turun

Menandakan volume keluar
dari saham (distribusi).

Seller lebih dominan daripada buyer.

Waspadai pelemahan harga.
"""
        )

        st.divider()

        st.subheader(
           "📖 Cara Membaca OBV"
        )

        st.info(
            """
✅ OBV Naik

Volume masuk ke saham.

Mengindikasikan akumulasi.

--------------------------------

✅ Harga Naik + OBV Naik

Sinyal bullish paling sehat.

Breakout lebih valid.

--------------------------------

🔥 Harga Sideways + OBV Naik

Smart money mulai masuk.

Sering muncul sebelum kenaikan harga.

--------------------------------

⚠️ Harga Naik + OBV Turun

Divergence bearish.

Harga naik tetapi volume keluar.

Waspadai distribusi.

--------------------------------

⚠️ Harga Turun + OBV Turun

Tekanan jual masih dominan.

Trend masih lemah.
"""
    )


    elif analysis_menu == "Average Down":

        row = portfolio_df[
            portfolio_df["Ticker"]
            == ticker
        ].iloc[0]

        current_lot = int(
            row["Lot"]
        )

        avg_buy = float(
            row["Avg Buy"]
        )

        add_lot = st.selectbox(
            "Tambah Lot",
            [1,2,5,10,20,50]
        )

        current_shares = (
            current_lot
            * 100
        )

        add_shares = (
            add_lot
            * 100
        )

        new_avg = (
            (
                current_shares
                * avg_buy
            )
            +
            (
                add_shares
                * close
            )
        ) / (
            current_shares
            + add_shares
        )

        st.metric(
            "Current Avg",
            round(avg_buy)
        )

        st.metric(
            "Current Price",
            round(close)
        )

        st.metric(
            "New Avg",
            round(new_avg)
        )

    elif analysis_menu == "Full Analysis":

        st.metric(
            "Price",
            round(close)
        )

        st.metric(
            "Support",
            support
        )

        st.metric(
            "Resistance",
            resistance
        )

        st.metric(
            "RSI",
            round(rsi,2)
        )

        st.line_chart(
            hist[
                [
                    "Close",
                    "MA20",
                    "MA50"
                ]
            ]
        )

        st.line_chart(
            hist["OBV"]
        )

        st.dataframe(
            hist[
                [
                    "Close",
                    "Volume"
                ]
            ].tail(7)
        )
elif menu == "Portfolio Radar":

    st.title("📡 Portfolio Radar")

    if not os.path.exists(
        "portfolio.csv"
    ):

        st.warning(
            "Portfolio belum ada."
        )

        st.stop()

    portfolio_df = pd.read_csv(
        "portfolio.csv"
    )

    radar_rows = []

    for _, row in portfolio_df.iterrows():

        try:

            ticker = (
                row["Ticker"]
                + ".JK"
            )

            hist = yf.Ticker(
                ticker
            ).history(
                period="6mo"
            )

            if len(hist) < 60:

                continue

            hist["MA20"] = (
                hist["Close"]
                .rolling(20)
                .mean()
            )

            hist["MA50"] = (
                hist["Close"]
                .rolling(50)
                .mean()
            )

            close = float(
                hist["Close"].iloc[-1]
            )

            ma20 = float(
                hist["MA20"].iloc[-1]
            )

            ma50 = float(
                hist["MA50"].iloc[-1]
            )

            avg_vol = (
                hist["Volume"]
                .tail(20)
                .mean()
            )

            vol_ratio = round(
                hist["Volume"].iloc[-1]
                /
                avg_vol,
                2
            )

            # Trend
            if close > ma20 > ma50:

                trend = "🟢 Uptrend"

            elif close > ma20:

                trend = "🟡 Watch"

            else:

                trend = "🔴 Downtrend"

            # Volume Status
            if vol_ratio >= 2:

                vol_status = "🔥 Meledak"

            elif vol_ratio >= 1.5:

                vol_status = "🚀 Tinggi"

            elif vol_ratio >= 1:

                vol_status = "✅ Normal"

            elif vol_ratio >= 0.5:

                vol_status = "🟡 Rendah"

            else:

                vol_status = "😴 Sepi"

            radar_rows.append(
                {
                    "Ticker":
                    row["Ticker"],

                    "Price":
                    round(close),

                    "Vol Ratio":
                    vol_ratio,

                    "Volume":
                    vol_status,

                    "Trend":
                    trend
                }
            )

        except:
            pass

    radar_df = pd.DataFrame(
        radar_rows
    )

    if radar_df.empty:

        st.warning(
            "Tidak ada data."
        )

    else:

        st.dataframe(
            radar_df,
            hide_index=True,
            use_container_width=True
        )

        st.divider()

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "🟢 Uptrend",
                len(
                    radar_df[
                        radar_df["Trend"]
                        ==
                        "🟢 Uptrend"
                    ]
                )
            )

        with col2:

            st.metric(
                "🚀 High Volume",
                len(
                    radar_df[
                        radar_df["Vol Ratio"]
                        >= 1.5
                    ]
                )
            )

        with col3:

            st.metric(
                "😴 Sepi",
                len(
                    radar_df[
                        radar_df["Vol Ratio"]
                        < 0.5
                    ]
                )
            )

        st.divider()

        st.subheader(
            "📖 Penjelasan Volume"
        )

        volume_guide = pd.DataFrame(
            [
                [
                    "< 0.50",
                    "😴 Sangat Sepi"
                ],
                [
                    "0.50 - 0.99",
                    "🟡 Di bawah normal"
                ],
                [
                    "1.00 - 1.49",
                    "✅ Normal"
                ],
                [
                    "1.50 - 1.99",
                    "🚀 Aktivitas Tinggi"
                ],
                [
                    "≥ 2.00",
                    "🔥 Volume Meledak"
                ]
            ],
            columns=[
                "Vol Ratio",
                "Arti"
            ]
        )

        st.dataframe(
            volume_guide,
            hide_index=True,
            use_container_width=True
        )

        st.info(
            """
Vol Ratio = Volume Hari Ini ÷ Rata-rata Volume 20 Hari

Contoh:

Vol Ratio 1.20
→ volume 20% lebih besar dari rata-rata.

Vol Ratio 2.00
→ volume 2x lebih besar dari rata-rata.

Vol Ratio 3.00
→ volume 3x lebih besar dari rata-rata.

Perhatian:
Volume tinggi belum tentu bullish.

✅ Harga naik + volume tinggi
= akumulasi / breakout.

❌ Harga turun + volume tinggi
= distribusi / tekanan jual.
"""
        )



elif menu == "Breakout Scanner":

    st.title("🚀 Breakout Scanner")

    if not os.path.exists(
        "portfolio.csv"
    ):

        st.warning(
            "Portfolio belum ada."
        )

        st.stop()

    portfolio_df = pd.read_csv(
        "portfolio.csv"
    )

    breakout_rows = []

    for _, row in portfolio_df.iterrows():

        try:

            ticker = (
                row["Ticker"]
                + ".JK"
            )

            hist = yf.Ticker(
                ticker
            ).history(
                period="6mo"
            )

            if len(hist) < 60:

                continue

            hist["RSI"] = calculate_rsi(
                hist["Close"]
            )

            hist["OBV"] = calculate_obv(
                hist
            )

            resistance = (
                hist["High"]
                .tail(20)
                .iloc[:-1]
                .max()
            )

            close = float(
                hist["Close"].iloc[-1]
            )

            high = float(
                hist["High"].iloc[-1]
            )

            low = float(
                hist["Low"].iloc[-1]
            )

            open_price = float(
                hist["Open"].iloc[-1]
            )

            rsi = round(
                hist["RSI"].iloc[-1],
                2
            )

            vol_ratio = round(
                hist["Volume"].iloc[-1]
                /
                hist["Volume"]
                .tail(20)
                .mean(),
                2
            )

            breakout = (
                close > resistance
                and
                vol_ratio >= 1.5
            )

            if not breakout:

                continue
            obv_now = (
                hist["OBV"]
                .iloc[-1]
            )

            obv_avg = (
                pd.Series(
                    hist["OBV"]
                )
                .tail(20)
                .mean()
            )

            if obv_now > obv_avg:

                obv_status = (
                    "✅ Akumulasi"
                )

            else:

                obv_status = (
                    "⚠️ Distribusi"
                )

            upper_shadow = (
                high
                -
                max(
                    close,
                    open_price
                )
            )

            candle_range = (
                high - low
            )

            distribution = False

            if candle_range > 0:

                distribution = (
                    upper_shadow
                    >
                    candle_range * 0.4
                )

            close_ratio = round(
                (
                    close
                    /
                    high
                ) * 100,
                1
            )
            if close_ratio >= 98:

                close_status = (
                    "✅ Near High"
                )

            elif close_ratio >= 95:

                close_status = (
                    "🟡 OK"
                )

            else:

                close_status = (
                    "⚠️ Far High"
                )

            if distribution:

                candle_status = (
                    "⚠️ Long Upper"
                )

            else:

                candle_status = (
                    "✅ Strong"
                )
            score = 0

            if vol_ratio >= 3:

                score += 3

            elif vol_ratio >= 2:

                score += 2

            elif vol_ratio >= 1.5:

                score += 1

            if 60 <= rsi <= 75:

                score += 2

            elif 50 <= rsi < 60:

                score += 1

            if obv_status == "✅ Akumulasi":

                score += 2

            if close_ratio >= 98:

                score += 2

            if distribution:

                score -= 3
            if score >= 8:

                signal = (
                    "🔥 Strong Entry"
                )

            elif score >= 5:

                signal = (
                    "🚀 Entry"
                )

            elif score >= 3:

                signal = (
                    "👀 Watch"
                )

            else:

                signal = (
                    "⚠️ Avoid"
                )

            breakout_rows.append(
                {
                    "Ticker":
                    row["Ticker"],

                    "Close":
                    round(close),

                    "Vol Ratio":
                    vol_ratio,

                    "RSI":
                    rsi,

                    "OBV":
                    obv_status,

                    "Close":
                    close_status,

                    "Candle":
                    candle_status,

                    "Signal":
                    signal
                }
            )

        except:

            pass
    breakout_df = pd.DataFrame(
        breakout_rows
    )

    if breakout_df.empty:

        st.info(
            "Tidak ada breakout."
        )

    else:

        st.dataframe(
            breakout_df,
            hide_index=True,
            use_container_width=True
        )
        strong_entry = breakout_df[
            breakout_df["Signal"]
            ==
            "🔥 Strong Entry"
        ]

        if not strong_entry.empty:

            st.success(
                f"""
🔥 Strong Entry

{', '.join(
strong_entry['Ticker']
)}

Volume kuat
RSI sehat
OBV akumulasi
Close dekat high
"""
            )

        danger = breakout_df[
            breakout_df["Candle"]
            ==
            "⚠️ Long Upper"
        ]

        if not danger.empty:

            st.warning(
                """
⚠️ Distribution Warning

Terdapat saham dengan
ekor atas panjang.

Menandakan adanya
profit taking.
"""
            )
        st.divider()

        st.subheader(
            "📖 Panduan Entry"
        )

        st.info(
            """
🔥 Strong Entry

Volume > 3x

RSI 60-75

OBV Akumulasi

Close dekat High

Tidak ada distribusi

--------------------------------

🚀 Entry

Volume > 2x

RSI sehat

OBV naik

--------------------------------

👀 Watch

Belum semua syarat terpenuhi

--------------------------------

⚠️ Avoid

RSI terlalu tinggi

OBV distribusi

Close jauh dari high

Distribusi terdeteksi
"""
        )
        st.subheader(
            "📊 Volume Ratio"
        )

        st.info(
            """
< 1.5x
= Volume Lemah

1.5x - 2x
= Breakout Valid

2x - 3x
= Breakout Kuat

> 3x
= Strong Breakout
"""
        )
        st.subheader(
            "📈 RSI"
        )

        st.info(
            """
< 30
= Oversold

30 - 50
= Lemah

50 - 60
= Bullish Awal

60 - 70
= Bullish Sehat

70 - 80
= Mulai Panas

> 80
= Overbought
"""
        )
        st.subheader(
            "📦 OBV & Distribusi"
        )

        st.info(
            """
✅ Akumulasi

OBV naik

Buyer dominan

--------------------------------

⚠️ Distribusi

OBV turun

Seller dominan

--------------------------------

✅ Near High

Harga ditutup dekat high hari ini.

Buyer masih kuat.

--------------------------------

⚠️ Far High

Harga ditutup jauh dari high.

Waspadai distribusi.

--------------------------------

⚠️ Long Upper Shadow

Ekor atas panjang.

Menandakan pressure jual
atau profit taking.

Semakin panjang ekor atas
semakin perlu hati-hati.
"""
        )
