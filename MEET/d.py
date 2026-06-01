elif menu == "🔎 View Tiffin Records":

    import base64
    import pandas as pd
    import streamlit as st

    # PNG file load & encode
    with open("images/view.png", "rb") as f:
        img_bytes = f.read()
        img_base64 = base64.b64encode(img_bytes).decode()

    # Header
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 8px; font-size: 1.25rem;">
            <img src="data:image/png;base64,{img_base64}" width="30" />
            <span>All Records</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    df = fetch_all()

    if df.empty:
        st.info("No records available")

    else:

        # ======================================================
        # ❌ Remove time column
        # ======================================================
        if "time" in df.columns:
            df = df.drop(columns=["time"])

        # ======================================================
        # 🔠 CAPITAL CONVERSION (NEW ADD)
        # ======================================================
        if "payment_status" in df.columns:
            df["payment_status"] = df["payment_status"].astype(str).str.strip().upper()

        if "shift" in df.columns:
            df["shift"] = df["shift"].astype(str).str.strip().upper()

        # ======================================================
        # 📅 Convert date
        # ======================================================
        df["date"] = pd.to_datetime(df["date"], dayfirst=True)

        # ============================================
        # 🔽 VIEW RECORD BY
        # ============================================
        view_type = st.selectbox(
            "View Record By",
            ["Date Wise", "Name Wise"]
        )

        # ============================================
        # DATE WISE
        # ============================================
        if view_type == "Date Wise":
            df = df.sort_values(by="date", ascending=True)

        # ============================================
        # NAME WISE
        # ============================================
        elif view_type == "Name Wise":

            name_order = {
                "MEET": 1,
                "YASH": 2,
                "DHRUMIL": 3
            }

            df["name_order"] = df["name"].str.upper().map(name_order)

            df = df.sort_values(
                by=["name_order", "date"],
                ascending=[True, True]
            )

            df = df.drop(columns=["name_order"])

        # ============================================
        # DATE FORMAT
        # ============================================
        df["date"] = df["date"].dt.strftime("%d/%m/%Y")

        # ============================================
        # NUMBER FORMAT
        # ============================================
        numeric_cols = ["quantity", "amount", "roti", "roti_amount"]

        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].apply(
                    lambda x: f"{x:.2f}" if float(x) % 1 else f"{int(x)}"
                )

        # ============================================
        # 🎨 PAYMENT STATUS COLOR (UPDATED)
        # ============================================
        def color_payment(val):

            val = str(val).upper().strip()

            if val == "PAYMENT DONE":
                return "color: #28a745; font-weight:bold;"   # Green

            elif val == "PAID":
                return "color: #ffc107; font-weight:bold;"   # Golden

            return ""

        # ============================================
        # 🌙 SHIFT COLOR (NEW ADD)
        # ============================================
        def color_shift(val):

            val = str(val).upper().strip()

            if val == "DAY":
                return "color: #1E90FF; font-weight:bold;"

            elif val == "NIGHT":
                return "color: #8A2BE2; font-weight:bold;"

            return ""

        # ============================================
        # 👤 NAME COLOR (same)
        # ============================================
        def color_name(val):

            colors = {
                "MEET": "#FF0033",
                "YASH": "#bfff00",
                "DHRUMIL": "#00bfff"
            }

            return (
                f"color: {colors.get(str(val).upper(), '')}; font-weight: bold;"
                if str(val).upper() in colors
                else ""
            )

        # ============================================
        # STYLE APPLY (UPDATED)
        # ============================================
        styled_df = (
            df.style
            .map(color_payment, subset=["payment_status"])
            .map(color_shift, subset=["shift"])
            .map(color_name, subset=["name"])
        )

        st.dataframe(styled_df, use_container_width=True)
