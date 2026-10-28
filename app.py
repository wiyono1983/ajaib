import streamlit as st
import pandas as pd
import yfinance as yf
import os
import requests
import matplotlib.pyplot as plt
from io import BytesIO

def get_support_resistance(hist):

    highs = hist["High"].reset_index(drop=True)
    lows = hist["Low"].reset_index(drop=True)

    swing_highs = []
    swing_lows = []

    for i in range(2, len(hist)-2):

        # Pivot High
        if (
            highs[i] > highs[i-1]
            and highs[i] > highs[i-2]
            and highs[i] > highs[i+1]
            and highs[i] > highs[i+2]
        ):
            swing_highs.append(highs[i])

        # Pivot Low
        if (
            lows[i] < lows[i-1]
            and lows[i] < lows[i-2]
            and lows[i] < lows[i+1]
            and lows[i] < lows[i+2]
        ):
            swing_lows.append(lows[i])

    current_price = hist["Close"].iloc[-1]

    support_candidates = [
        x for x in swing_lows
        if x < current_price
    ]

    resistance_candidates = [
        x for x in swing_highs
        if x > current_price
    ]

    if len(support_candidates):
        support = max(support_candidates)
    else:
        support = current_price * 0.95

    if len(resistance_candidates):
        resistance = min(resistance_candidates)
    else:
        resistance = current_price * 1.10

    return round(support), round(resistance)


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
    ["Saham"]
)

if menu == "Saham":

    submenu = st.sidebar.radio(
        "Menu Saham",
        [
            "IDX Nexus",
            "Portfolio Radar",
            "Analisa Saham",
            "Breakout Scanner",
            "Take Profit Analyzer",
            "OBV Forecast",
            "Stock Entry Analyzer",
            "Market Movers",
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

menu = submenu



# =========================
# PAGES
# =========================
                
if menu == "IDX Nexus":


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

            support, resistance = get_support_resistance(
                hist
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
                    "Ticker": row["Ticker"],

                    "Price": round(close),

                    "Vol Ratio": vol_ratio,

                    "RSI": rsi,

                    "OBV": obv_status,

                    "Close Status": close_status,

                    "Candle": candle_status,

                    "Signal": signal
                }

            #    {
               #     "Ticker":
           #         row["Ticker"],

               #     "Close":
               #     round(close),

              #      "Vol Ratio":
           #         vol_ratio,

                #    "RSI":
                #    rsi,

                 #   "OBV":
               #     obv_status,

              #      "Close":
                #    close_status,

               #     "Candle":
                 #   candle_status,

               #     "Signal":
               #     signal
             #   }
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
    
    support, resistance = get_support_resistance(
        hist
    )

    analysis_menu = st.selectbox(
        "Analisa",
        [
            "Dashboard",
            "Support Resistance",
            "RSI MACD",
            "Volume",
            "OBV",
            "Average Down",
            "Full Analysis"
        ]
    )

    if analysis_menu == "Dashboard":

        c1, c2, c3, c4 = st.columns(4)

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
            round(rsi, 2)
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

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Support",
                support
            )

        with col2:
            st.metric(
                "Resistance",
                resistance
            )

        st.line_chart(
            hist["Close"]
        )

    elif analysis_menu == "RSI MACD":

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "RSI",
            round(rsi, 2)
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
            "📊 Volume Analysis"
        )

        st.bar_chart(
            hist["Volume"].tail(30)
        )

        avg_vol = (
            hist["Volume"]
            .tail(20)
            .mean()
        )

        ratio = round(
            hist["Volume"].iloc[-1]
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

Menandakan volume masuk ke saham.

Terjadi akumulasi.

Buyer lebih dominan.

Mendukung tren naik.
"""
            )

        else:

            st.warning(
                """
⚠️ OBV Sedang Turun

Menandakan volume keluar dari saham.

Terjadi distribusi.

Seller lebih dominan.

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

Bullish sehat.

Breakout lebih valid.

--------------------------------

🔥 Harga Sideways + OBV Naik

Smart money mulai masuk.

--------------------------------

⚠️ Harga Naik + OBV Turun

Bearish divergence.

--------------------------------

⚠️ Harga Turun + OBV Turun

Tekanan jual masih dominan.
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
            [1, 2, 5, 10, 20, 50]
        )

        current_shares = (
            current_lot * 100
        )

        add_shares = (
            add_lot * 100
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

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Current Avg",
            round(avg_buy)
        )

        c2.metric(
            "Current Price",
            round(close)
        )

        c3.metric(
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
            round(rsi, 2)
        )

        st.subheader(
            "Price Trend"
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

        st.subheader(
            "OBV"
        )

        st.line_chart(
            hist["OBV"]
        )

        st.subheader(
            "Recent Data"
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

elif menu == "Take Profit Analyzer":

    st.title("🎯 Smart Take Profit Analyzer")

    if not os.path.exists("portfolio.csv"):

        st.warning("Portfolio belum ada.")
        st.stop()

    portfolio_df = pd.read_csv(
        "portfolio.csv"
    )

    result_rows = []

    total_profit = 0

    for _, row in portfolio_df.iterrows():

        try:

            ticker = row["Ticker"]

            avg_buy = float(
                row["Avg Buy"]
            )

            lot = int(
                row["Lot"]
            )

            shares = (
                lot * 100
            )

            hist = yf.Ticker(
                ticker + ".JK"
            ).history(
                period="1y"
            )

            if len(hist) < 60:

                continue

            hist["RSI"] = calculate_rsi(
                hist["Close"]
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

            profit_pct = round(
                (
                    (
                        close
                        -
                        avg_buy
                    )
                    /
                    avg_buy
                )
                * 100,
                2
            )

            market_value = (
                close
                * shares
            )

            cost_value = (
                avg_buy
                * shares
            )

            unrealized_profit = (
                market_value
                - cost_value
            )

            total_profit += (
                unrealized_profit
            )
            support, resistance = get_support_resistance(
                hist
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

            tr = pd.concat(
                [
                    hist["High"]
                    -
                    hist["Low"],

                    abs(
                        hist["High"]
                        -
                        hist["Close"].shift()
                    ),

                    abs(
                        hist["Low"]
                        -
                        hist["Close"].shift()
                    )
                ],
                axis=1
            ).max(axis=1)

            atr = (
                tr
                .rolling(14)
                .mean()
                .iloc[-1]
            )

            tp1 = round(
                close + atr
            )

            tp2 = round(
                close + (atr * 2)
            )

            tp3 = round(
                close + (atr * 3)
            )

            high20 = (
                hist["High"]
                .tail(20)
                .max()
            )

            trailing_stop = round(
                high20 * 0.93
            )

            score = 0

            reasons = []

            #===================
            # PROFIT SCORE
            #===================

            if profit_pct >= 50:

                score += 4
                reasons.append(
                    "Profit>50%"
                )

            elif profit_pct >= 30:

                score += 3
                reasons.append(
                    "Profit>30%"
                )

            elif profit_pct >= 15:

                score += 2
                reasons.append(
                    "Profit>15%"
                )

            elif profit_pct >= 10:

                score += 1
                reasons.append(
                    "Profit>10%"
                )

            #===================
            # RSI
            #===================

            if rsi >= 80:

                score += 3
                reasons.append(
                    "RSI Extreme"
                )

            elif rsi >= 75:

                score += 2
                reasons.append(
                    "RSI Panas"
                )

            #===================
            # RESISTANCE
            #===================

            if close >= (
                resistance * 0.98
            ):

                score += 2
                reasons.append(
                    "Near Resistance"
                )

            #===================
            # DISTRIBUSI
            #===================

            if distribution:

                score += 3
                reasons.append(
                    "Distribusi"
                )

            #===================
            # VOLUME
            #===================

            if vol_ratio < 1:

                score += 1
                reasons.append(
                    "Volume Lemah"
                )

            #===================
            # TRAILING STOP
            #===================

            if close < trailing_stop:

                score += 4
                reasons.append(
                    "Break Trail"
                )

            #===================
            # PROFIT + RSI
            #===================

            if (
                profit_pct > 30
                and
                rsi > 70
            ):

                score += 2

                reasons.append(
                    "Profit+RSI"
                )

            #===================
            # FINAL SIGNAL
            #===================

            if score >= 10:

                signal = (
                    "🔴 SELL ALL"
                )

                action = (
                    "Jual 100%"
                )

            elif score >= 7:

                signal = (
                    "🟠 TAKE PROFIT"
                )

                action = (
                    "Jual 50%"
                )

            elif score >= 4:

                signal = (
                    "🟡 PARTIAL TP"
                )

                action = (
                    "Jual 25%"
                )

            else:

                signal = (
                    "🟢 HOLD"
                )

                action = (
                    "Hold"
                )

            result_rows.append(
                {
                    "Ticker":
                    ticker,

                    "Lot":
                    lot,

                    "Avg Buy":
                    round(avg_buy),

                    "Price":
                    round(close),

                    "Profit %":
                    profit_pct,

                    "Profit Rp":
                    round(
                        unrealized_profit
                    ),

                    "RSI":
                    round(rsi,1),

                    "TP1":
                    tp1,

                    "TP2":
                    tp2,

                    "TP3":
                    tp3,

                    "Trail":
                    trailing_stop,

                    "Signal":
                    signal,

                    "Action":
                    action,

                    "Reason":
                    ", ".join(
                        reasons
                    )
                }
            )

        except:
            pass

    tp_df = pd.DataFrame(
        result_rows
    )

    if tp_df.empty:

        st.warning(
            "Tidak ada data."
        )

    else:

        st.metric(
            "💰 Total Unrealized Profit",
            f"Rp {total_profit:,.0f}"
        )

        st.dataframe(
            tp_df,
            hide_index=True,
            use_container_width=True
        )

        st.divider()

        st.subheader(
            "🔴 SELL ALL"
        )

        sell_all = tp_df[
            tp_df["Signal"]
            ==
            "🔴 SELL ALL"
        ]

        if not sell_all.empty:

            st.dataframe(
                sell_all,
                hide_index=True,
                use_container_width=True
            )

        st.divider()

        st.subheader(
            "🟠 TAKE PROFIT"
        )

        tp50 = tp_df[
            tp_df["Signal"]
            ==
            "🟠 TAKE PROFIT"
        ]

        if not tp50.empty:

            st.dataframe(
                tp50,
                hide_index=True,
                use_container_width=True
            )

        st.divider()

        st.subheader(
            "🟢 HOLD"
        )

        hold_df = tp_df[
            tp_df["Signal"]
            ==
            "🟢 HOLD"
        ]

        if not hold_df.empty:

            st.dataframe(
                hold_df,
                hide_index=True,
                use_container_width=True
            )

        st.divider()

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Hold",
            len(
                tp_df[
                    tp_df["Signal"]
                    ==
                    "🟢 HOLD"
                ]
            )
        )

        c2.metric(
            "Partial",
            len(
                tp_df[
                    tp_df["Signal"]
                    ==
                    "🟡 PARTIAL TP"
                ]
            )
        )

        c3.metric(
            "TP",
            len(
                tp_df[
                    tp_df["Signal"]
                    ==
                    "🟠 TAKE PROFIT"
                ]
            )
        )

        c4.metric(
            "Sell All",
            len(
                tp_df[
                    tp_df["Signal"]
                    ==
                    "🔴 SELL ALL"
                ]
            )
        )

        st.divider()

        wa_text = (
            "🎯 TAKE PROFIT ANALYZER\n\n"
        )

        for _, r in tp_df.iterrows():

            wa_text += (
                f"{r['Ticker']}\n"
                f"Avg : {r['Avg Buy']:,.0f}\n"
                f"Now : {r['Price']:,.0f}\n"
                f"Profit : {r['Profit %']}%\n"
                f"RSI : {r['RSI']}\n"
                f"Signal : {r['Signal']}\n"
                f"Action : {r['Action']}\n"
                f"{r['Reason']}\n\n"
            )

        st.subheader(
            "📱 Copy To WhatsApp"
        )

        st.code(
            wa_text,
            language="text"
        )
elif menu == "OBV Forecast":

    st.title("📦 OBV Forecast Portfolio")

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

    rows = []

    for _, row in portfolio_df.iterrows():

        try:

            ticker = row["Ticker"]

            avg_buy = float(
                row["Avg Buy"]
            )

            lot = int(
                row["Lot"]
            )

            shares = lot * 100

            hist = yf.Ticker(
                ticker + ".JK"
            ).history(
                period="1y"
            )

            if len(hist) < 100:

                continue

            hist["OBV"] = calculate_obv(
                hist
            )

            current_price = float(
                hist["Close"].iloc[-1]
            )

            profit_pct = round(
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

            profit_rp = round(
                (
                    current_price
                    - avg_buy
                )
                * shares
            )
            support, resistance = get_support_resistance(
                hist
            )
         

            obv_now = (
                hist["OBV"]
                .iloc[-1]
            )

            obv_ma5 = (
                pd.Series(
                    hist["OBV"]
                )
                .tail(5)
                .mean()
            )

            obv_ma20 = (
                pd.Series(
                    hist["OBV"]
                )
                .tail(20)
                .mean()
            )
            if abs(obv_ma20) > 0:

                obv_strength = round(
                obv_now
                /
                abs(obv_ma20),
                2
            )

            else:

                obv_strength = 0

         #   obv_strength = round(
            #    obv_now
              #  /
            #    abs(obv_ma20),
             #   2
           # )

            if obv_ma5 > obv_ma20:

                bandar = (
                    "✅ Akumulasi"
                )

            else:

                bandar = (
                    "⚠️ Distribusi"
                )

            score = 0

            if obv_strength > 1.5:
                score += 4

            elif obv_strength > 1.2:
                score += 3

            elif obv_strength > 1:
                score += 2

            if bandar == "✅ Akumulasi":
                score += 2

            if current_price >= resistance * 0.95:
                score += 2

            if current_price > avg_buy:
                score += 1

            # Forecast

            if score >= 7:

                forecast = (
                    "🔥 Sangat Bullish"
                )

                target = round(
                    resistance * 1.15
                )

            elif score >= 5:

                forecast = (
                    "🚀 Bullish"
                )

                target = round(
                    resistance * 1.10
                )

            elif score >= 3:

                forecast = (
                    "✅ Watch"
                )

                target = round(
                    resistance * 1.05
                )

            else:

                forecast = (
                    "⏸ Sideways"
                )

                target = resistance

            upside = round(
                (
                    (
                        target
                        -
                        current_price
                    )
                    /
                    current_price
                )
                * 100,
                2
            )

            # Action

            if (
                profit_pct > 50
                and bandar == "⚠️ Distribusi"
            ):

                action = (
                    "🔴 TP Semua"
                )

            elif (
                profit_pct > 25
                and bandar == "⚠️ Distribusi"
            ):

                action = (
                    "🟠 TP 50%"
                )

            elif (
                profit_pct < 0
                and bandar == "✅ Akumulasi"
            ):

                action = (
                    "🟢 Avg Down Watch"
                )

            else:

                action = (
                    "✅ Hold"
                )

            rows.append(
                {
                    "Ticker":
                    ticker,

                    "Lot":
                    lot,

                    "Avg":
                    round(avg_buy),

                    "Price":
                    round(current_price),

                    "P/L %":
                    profit_pct,

                    "P/L Rp":
                    profit_rp,

                    "Support":
                    support,

                    "Resistance":
                    resistance,

                    "OBV":
                    obv_strength,

                    "Bandar":
                    bandar,

                    "Forecast":
                    forecast,

                    "Target":
                    target,

                    "Upside %":
                    upside,

                    "Action":
                    action,

                    "Score":
                    score
                }
            )

        except:
            pass

    forecast_df = pd.DataFrame(
        rows
    )

    if forecast_df.empty:

        st.warning(
            "Tidak ada data."
        )

    else:

        forecast_df = (
            forecast_df
            .sort_values(
                "Score",
                ascending=False
            )
        )

        st.dataframe(
            forecast_df[
                [
                    "Ticker",
                    "Lot",
                    "Avg",
                    "Price",
                    "P/L %",
                    "P/L Rp",
                    "Support",
                    "Resistance",
                    "OBV",
                    "Bandar",
                    "Forecast",
                    "Target",
                    "Upside %",
                    "Action"
                ]
            ],
            hide_index=True,
            use_container_width=True
        )

        st.divider()

        st.subheader(
            "🏆 Top Forecast"
        )

        st.dataframe(
            forecast_df.head(5),
            hide_index=True,
            use_container_width=True
        )

        st.divider()

        st.subheader(
            "📖 Interpretasi"
        )

        st.info(
            """
✅ Akumulasi

Bandar masih mengumpulkan saham.

OBV 5 hari lebih kuat dari OBV 20 hari.

--------------------------------

⚠️ Distribusi

Bandar mulai melepas saham.

Perlu waspada.

--------------------------------

🔥 Sangat Bullish

Target berpotensi naik >10%.

Probabilitas breakout tinggi.

--------------------------------

🟢 Avg Down Watch

Sedang rugi tetapi bandar masih akumulasi.

Layak masuk watchlist averaging.

--------------------------------

🟠 TP 50%

Profit sudah besar dan ada tanda distribusi.

Pertimbangkan realisasi sebagian profit.

--------------------------------

🔴 TP Semua

Profit sudah tinggi dan distribusi kuat.

Prioritaskan pengamanan profit.
"""
        )


    
                                    
elif menu == "Market Movers":

    st.title("🔥 Market Movers")

    if not os.path.exists("portfolio.csv"):

        st.warning("Portfolio belum ada.")
        st.stop()

    portfolio_df = pd.read_csv(
        "portfolio.csv"
    )

    rows = []

    for _, row in portfolio_df.iterrows():

        try:

            ticker = row["Ticker"]

            hist = yf.Ticker(
                ticker + ".JK"
            ).history(
                period="3mo"
            )

            if len(hist) < 30:

                continue

            hist["RSI"] = calculate_rsi(
                hist["Close"]
            )

            current = float(
                hist["Close"].iloc[-1]
            )

            prev = float(
                hist["Close"].iloc[-2]
            )

            gain_pct = round(
                (
                    (current - prev)
                    / prev
                ) * 100,
                2
            )

            avg_vol = (
                hist["Volume"]
                .tail(20)
                .mean()
            )

            vol_ratio = round(
                hist["Volume"].iloc[-1]
                / avg_vol,
                2
            )

            rsi = round(
                hist["RSI"].iloc[-1],
                2
            )

            signal = "👀 Watch"

            if (
                gain_pct > 5
                and vol_ratio > 2
                and rsi > 60
            ):

                signal = "🔥 HOT"

            elif (
                gain_pct > 2
                and vol_ratio > 1.5
            ):

                signal = "🚀 Momentum"

            rows.append(
                {
                    "Ticker": ticker,
                    "Price": round(current),
                    "Gain %": gain_pct,
                    "RSI": rsi,
                    "Vol Ratio": vol_ratio,
                    "Signal": signal
                }
            )

        except:
            pass

    movers_df = pd.DataFrame(
        rows
    )

    if movers_df.empty:

        st.warning(
            "Tidak ada data."
        )

    else:

        movers_df = movers_df.sort_values(
            "Gain %",
            ascending=False
        )

        st.subheader(
            "🏆 Top Gainer Portfolio"
        )

        st.dataframe(
            movers_df,
            hide_index=True,
            use_container_width=True
        )

        st.divider()

        hot_df = movers_df[
            movers_df["Signal"]
            == "🔥 HOT"
        ]

        if not hot_df.empty:

            st.success(
                f"""
🔥 HOT STOCKS

{', '.join(
    hot_df['Ticker']
)}
"""
            )

        st.divider()

        st.subheader(
            "📖 Interpretasi"
        )

        st.info(
            """
🔥 HOT

Gain > 5%

RSI > 60

Volume > 2x rata-rata

------------------------

🚀 MOMENTUM

Gain > 2%

Volume > 1.5x

------------------------

👀 WATCH

Belum ada momentum kuat
"""
        )
elif menu == "Stock Entry Analyzer":

    st.title("🔎 Smart Entry Analyzer")

    ticker = st.text_input(
        "Kode Saham",
        placeholder="BBCA"
    )

    if ticker:

        try:

            ticker = ticker.upper().strip()

            hist = yf.Ticker(
                ticker + ".JK"
            ).history(
                period="1y"
            )

            if hist.empty:

                st.warning(
                    "Data tidak ditemukan."
                )

                st.stop()

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

            rsi = float(
                hist["RSI"].iloc[-1]
            )

            macd = float(
                hist["MACD"].iloc[-1]
            )

            signal = float(
                hist["MACD_SIGNAL"].iloc[-1]
            )

            # PIVOT SUPPORT RESISTANCE
            support, resistance = get_support_resistance(
                hist
            )

            buy_zone_1 = support

            buy_zone_2 = round(
                support * 1.03
            )

            stoploss = round(
                support * 0.97
            )

            avg_vol = (
                hist["Volume"]
                .tail(20)
                .mean()
            )

            vol_ratio = round(
                hist["Volume"].iloc[-1]
                / avg_vol,
                2
            )

            obv_now = (
                hist["OBV"]
                .iloc[-1]
            )

            obv_ma5 = (
                pd.Series(
                    hist["OBV"]
                )
                .tail(5)
                .mean()
            )

            obv_ma20 = (
                pd.Series(
                    hist["OBV"]
                )
                .tail(20)
                .mean()
            )

            if obv_ma5 > obv_ma20:

                obv_status = "✅ Akumulasi"

            else:

                obv_status = "⚠️ Distribusi"

            if abs(obv_ma20) > 0:

                obv_strength = round(
                    obv_now / abs(obv_ma20),
                    2
                )

            else:

                obv_strength = 0

            score = 0
            reasons = []

            # RSI

            if 55 <= rsi <= 70:

                score += 2
                reasons.append(
                    "RSI Bullish"
                )

            elif rsi > 70:

                score -= 1
                reasons.append(
                    "RSI Panas"
                )

            # MACD

            if macd > signal:

                score += 2
                reasons.append(
                    "MACD Bullish"
                )

            # OBV

            if obv_status == "✅ Akumulasi":

                score += 3
                reasons.append(
                    "Bandar Akumulasi"
                )

            # Volume

            if vol_ratio >= 1.5:

                score += 2
                reasons.append(
                    "Volume Tinggi"
                )

            elif vol_ratio >= 1:

                score += 1

            # Dekat Resistance

            if close >= resistance * 0.95:

                score += 2
                reasons.append(
                    "Dekat Breakout"
                )

            # Final Recommendation

            if score >= 8:

                recommendation = (
                    "🔥 STRONG BUY"
                )

            elif score >= 5:

                recommendation = (
                    "🚀 BUY"
                )

            elif score >= 3:

                recommendation = (
                    "👀 WATCHLIST"
                )

            else:

                recommendation = (
                    "⚠️ WAIT"
                )

            target1 = round(
                resistance * 1.05
            )

            target2 = round(
                resistance * 1.15
            )

            upside1 = round(
                (
                    (target1 - close)
                    / close
                ) * 100,
                2
            )

            upside2 = round(
                (
                    (target2 - close)
                    / close
                ) * 100,
                2
            )

            risk = round(
                (
                    (close - stoploss)
                    / close
                ) * 100,
                2
            )

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "Price",
                round(close)
            )

            c2.metric(
                "RSI",
                round(rsi, 2)
            )

            c3.metric(
                "Vol Ratio",
                vol_ratio
            )

            c4.metric(
                "Score",
                score
            )

            st.divider()

            st.dataframe(
                pd.DataFrame([
                    {
                        "Support":
                        support,

                        "Buy Area":
                        f"{buy_zone_1}-{buy_zone_2}",

                        "Resistance":
                        resistance,

                        "Stop Loss":
                        stoploss,

                        "Target 1":
                        target1,

                        "Target 2":
                        target2
                    }
                ]),
                hide_index=True,
                use_container_width=True
            )

            st.success(
                recommendation
            )

            st.write(
                f"""
OBV : {obv_status}

OBV Strength : {obv_strength}

MACD : {round(macd,2)}

Signal : {round(signal,2)}
"""
            )

            st.divider()

            st.subheader(
                "Risk Reward"
            )

            c1,c2,c3 = st.columns(3)

            c1.metric(
                "Risk %",
                risk
            )

            c2.metric(
                "Target1 %",
                upside1
            )

            c3.metric(
                "Target2 %",
                upside2
            )

            st.divider()

            st.info(
                f"""
Rekomendasi : {recommendation}

Alasan :
{', '.join(reasons)}

Support : {support}

Resistance : {resistance}

Stop Loss : {stoploss}

Target 1 : {target1}

Target 2 : {target2}

Bandar :
{obv_status}
"""
            )

        except Exception as e:

            st.error(
                f"Error: {e}"
            )
