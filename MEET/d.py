import streamlit as st
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import bcrypt
import psycopg2
from io import BytesIO
import base64
import time
import requests
from datetime import date
from dateutil.relativedelta import relativedelta
from streamlit_extras.radial_menu import *
from streamlit_option_menu import option_menu

st.set_page_config(
    page_title="LUNCHLOGIX",
    page_icon="images/d.png",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get help': None,
        'Report a bug': None,
        'About': None
    }
)
st.markdown("""
<style>

/* =========================================================
   SIDEBAR = FIXED HEIGHT / NO VISIBLE SECOND SCROLLBAR
   ========================================================= */

/* Sidebar outer container */
section[data-testid="stSidebar"] {
    height: 100vh !important;
    overflow: hidden !important;
}

/* Sidebar main content */
section[data-testid="stSidebar"] > div {
    height: 100vh !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;

    /* Hide scrollbar - Chrome / Edge */
    scrollbar-width: none !important;
    -ms-overflow-style: none !important;
}

/* Hide scrollbar - Chrome / Edge / Safari */
section[data-testid="stSidebar"] > div::-webkit-scrollbar {
    display: none !important;
    width: 0 !important;
}

/* Keep sidebar content inside viewport */
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    min-height: 100vh !important;
    overflow-x: hidden !important;
}

/* Prevent horizontal overflow */
section[data-testid="stSidebar"] * {
    max-width: 100%;
}

/* =========================================================
   MAIN PAGE
   ========================================================= */

.main {
    overflow-x: hidden !important;
}

</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>

/* ================================
   GLOBAL TOP SPACING - 20px
   ================================ */

[data-testid="stAppViewContainer"] .main .block-container {
    padding-top: 20px !important;
}


/* Hide Streamlit Spinner */
[data-testid="stSpinner"] {
    display: none !important;
}

/* Hide Running indicator */
[data-testid="stStatusWidget"] {
    display: none !important;
}

/* Hide top loading animation */
div[data-testid="stDecoration"] {
    display: none !important;
}


/* ================================
   BUTTON DESIGN
   ================================ */

div.stButton > button {
    background-color: red !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6em 1em !important;
    font-weight: bold !important;
}

div.stButton > button:hover {
    background-color: darkred !important;
    color: white !important;
}

/* =========================================================
   SAVE BUTTON - ALWAYS REACHABLE
   ========================================================= */
div[data-testid="stButton"]:has(button[kind="primary"]) {
    position: sticky !important;
    bottom: 12px !important;
    z-index: 9999 !important;
    padding: 6px 0 !important;
    background: rgba(2, 6, 23, 0.90) !important;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border-radius: 10px;
}


/* Download Button */

div.stDownloadButton > button {
    background-color: red !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6em 1em !important;
    font-weight: bold !important;
}

div.stDownloadButton > button:hover {
    background-color: darkred !important;
    color: white !important;
}



/* =========================================================
   REUSABLE LOADER BAR
   ========================================================= */
.loaderWrap {
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 8px 0;
}

.loaderBar {
    width: calc(160px / 0.707);
    height: 10px;
    background: #F9F9F9;
    border-radius: 10px;
    border: 1px solid #006DFE;
    position: relative;
    overflow: hidden;
}

.loaderBar::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    border-radius: 5px;
    background: repeating-linear-gradient(45deg, #0031F2 0 30px, #006DFE 0 40px) right/200% 100%;
    animation: fillProgress 6s ease-in-out infinite, lightEffect 1s infinite linear;
    animation-fill-mode: forwards;
}

@keyframes fillProgress {
    0% { width: 0; }
    33% { width: 33.333%; }
    66% { width: 66.67%; }
    100% { width: 100%; }
}

@keyframes lightEffect {
    0%, 20%, 40%, 60%, 80%, 100% {
        background: repeating-linear-gradient(45deg, #0031F2 0 30px, #006DFE 0 40px) right/200% 100%;
    }
    10%, 30%, 50%, 70%, 90% {
        background: repeating-linear-gradient(45deg, #0031F2 0 30px, #006DFE 0 40px, rgba(255, 255, 255, 0.3) 0 40px) right/200% 100%;
    }
}

</style>
""", unsafe_allow_html=True)
with open("images/icons8-monzo-48.png", "rb") as f:
    img_bytes = f.read()
    img_base64 = base64.b64encode(img_bytes).decode()
st.markdown(
    f"""
    <style>
    .footer {{
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: transparent;
        text-align: center;
        padding: 10px;
        font-size: 22px;
        font-weight: bold;
        animation: colorchange 0.15s infinite;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 15px;
    }}

    @keyframes colorchange {{
        2.5% {{ color: #3498DB; }}

    }}
    </style>

    <div class="footer">
        <img src="data:image/png;base64,{img_base64}" width="30">
        Made by MEET MEWADA
        <img src="data:image/png;base64,{img_base64}" width="30">
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)
# petoc = "tiffin_db"
# lemox = "postgres"
# ternak = "1234"
# owert = "localhost"
# xoper = 5432
def show_loader(target):
    """Render the supplied loader inside a placeholder."""
    target.markdown(
        """
        <div class="loaderWrap">
            <div class="loaderBar"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def fetch_all_with_loader():
    """Fetch cached tiffin records while showing the reusable loader."""
    loader_box = st.empty()
    show_loader(loader_box)
    try:
        return fetch_all()
    finally:
        loader_box.empty()


def fetch_account_records_with_loader():
    """Fetch account records while showing the reusable loader."""
    loader_box = st.empty()
    show_loader(loader_box)
    try:
        conn = get_db()
        return pd.read_sql(
            "SELECT * FROM account_records ORDER BY date DESC, time DESC",
            conn,
        )
    finally:
        loader_box.empty()


def insert_record_with_loader(data):
    """Insert records while showing the reusable loader."""
    loader_box = st.empty()
    show_loader(loader_box)
    try:
        insert_record(data)
    finally:
        loader_box.empty()


def run_with_loader(func, *args, **kwargs):
    """Run a database operation while showing the same loader."""
    loader_box = st.empty()
    show_loader(loader_box)
    try:
        return func(*args, **kwargs)
    finally:
        loader_box.empty()


TABLE_NAME = "tiffin"
petoc = "defaultdb"
lemox = "avnadmin"
ternak = "AVNS_LovPCygG-7HQB0xs0Su"
owert = "pg-e6a0b32-manmeet2756-50e1.d.aivencloud.com"
xoper = 19632


@st.cache_resource
def get_db():
    return psycopg2.connect(
        host=owert,
        database=petoc,
        user=lemox,
        password=ternak,
        port=int(xoper),
        sslmode="require",
        connect_timeout=5,
        keepalives=1,
        keepalives_idle=30,
        keepalives_interval=10,
        keepalives_count=5
    )


# ==========================
# DATABASE STATUS CHECK
# Checks only every 15 seconds
# ==========================
@st.cache_data(ttl=15, show_spinner=False)
def check_db_connection():
    try:
        conn = get_db()

        # Test cached connection
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()

        return True

    except (
            psycopg2.InterfaceError,
            psycopg2.OperationalError,
            psycopg2.DatabaseError,
    ):
        # Remove broken cached connection
        get_db.clear()
        return False

    except Exception:
        get_db.clear()
        return False


@st.cache_data
def load_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# =========================================================
# CENTRALIZED COLORS / TABLE STYLING
# =========================================================
# All name/payment/shift/day colors live here only once.
# Every table reuses these same functions.

NAME_COLORS = {
    "MEET": "#FF0033",
    "YASH": "#bfff00",
    "DHRUMIL": "#00bfff",
    "TOTAL": "#9929EA",
}

PAYMENT_COLORS = {
    "PAYMENT DONE": "#73FF00",
    "PENDING": "#FF0095",
    "PAYMENT PENDING": "#FF0095",
    "PAID": "goldenrod",
    "NOT INVOLVED": "#FCDC2A",
}

SHIFT_COLORS = {
    "DAY": "#FF8F00",
    "NIGHT": "#3B9797",
}

DAY_COLORS = {
    "MONDAY": "#BF00FF",
    "TUESDAY": "#0000FF",
    "WEDNESDAY": "#7DF9FF",
    "THURSDAY": "#72FF13",
    "FRIDAY": "#FFFC00",
    "SATURDAY": "#FF5C00",
    "SUNDAY": "#E60000",
}


def get_name_color(value):
    return NAME_COLORS.get(str(value).upper())


def get_payment_color(value):
    return PAYMENT_COLORS.get(str(value).upper())


def get_shift_color(value):
    return SHIFT_COLORS.get(str(value).upper())


def get_day_color(value):
    return DAY_COLORS.get(str(value).upper())


def color_name(value):
    color = get_name_color(value)
    return f"color: {color}; font-weight: bold;" if color else ""


def color_payment(value):
    color = get_payment_color(value)
    return f"color: {color}; font-weight: bold;" if color else ""


def color_shift(value):
    color = get_shift_color(value)
    return f"color: {color}; font-weight: bold;" if color else ""


def color_day(value):
    color = get_day_color(value)
    return f"color: {color}; font-weight: bold;" if color else ""


def style_table(df):
    """Apply common colors to every matching column automatically."""
    styler = df.style
    if "name" in df.columns:
        styler = styler.map(color_name, subset=["name"])
    if "Name" in df.columns:
        styler = styler.map(color_name, subset=["Name"])
    if "payment_status" in df.columns:
        styler = styler.map(color_payment, subset=["payment_status"])
    if "shift" in df.columns:
        styler = styler.map(color_shift, subset=["shift"])
    if "day" in df.columns:
        styler = styler.map(color_day, subset=["day"])
    return styler


@st.cache_data(ttl=30, show_spinner=False)
def fetch_all():
    conn = get_db()

    query = f"""
    SELECT
        id,
        Date,
        Day,
        Time,
        Name,
        Shift,
        Quantity,
        Roti,
        Roti_Amount,
        Amount,
        Payment_Status
    FROM {TABLE_NAME}
    ORDER BY Date DESC
    """

    df = pd.read_sql(query, conn)

    df.columns = [c.lower() for c in df.columns]

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    return df


def insert_record(data):
    conn = get_db()
    cursor = conn.cursor()

    cursor.executemany(
        f"""
        INSERT INTO {TABLE_NAME}
        (Date, Day, Time, Name, Shift, Quantity, Roti, Roti_Amount, Amount, Payment_Status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        data
    )

    conn.commit()
    cursor.close()
    fetch_all.clear()


def update_record(record_id, date, shift, qty, roti, amount, roti_amount, payment_status):
    conn = get_db()
    cursor = conn.cursor()
    day = date.strftime("%A").upper()

    query = f"""
        UPDATE {TABLE_NAME}
        SET date = %s,
            Shift = %s,
            Quantity = %s,
            Roti = %s,
            Amount = %s,
            Roti_Amount = %s,
            Payment_Status = %s
        WHERE id = %s
    """

    params = (date, shift, qty, roti, amount, roti_amount, payment_status, record_id)

    cursor.execute(query, params)

    conn.commit()
    cursor.close()
    fetch_all.clear()


def update_payment(start_date, end_date, payment_status):
    conn = get_db()

    cursor = conn.cursor()

    cursor.execute(f"""

        UPDATE {TABLE_NAME}

        SET Payment_Status=%s

        WHERE Date BETWEEN %s AND %s

    """, (payment_status, start_date, end_date))

    conn.commit()

    cursor.close()
    fetch_all.clear()


def delete_tiffin_page():

    # PNG file load & encode
    img_base64 = load_image("images/delete.png")

    # Display icon + text side by side
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 8px; font-size: 1.25rem;">
            <img src="data:image/png;base64,{img_base64}" width="30" />
            <span>Delete Tiffin Records</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Fetch all records
    df = fetch_all_with_loader()
    if df.empty:
        st.info("No Tiffin records available to delete.")
        return

    # Convert date column
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Remove invalid dates
    df = df.dropna(subset=['date'])

    if df.empty:
        st.info("No valid Tiffin records available to delete.")
        return

    # Available names
    names = sorted(df['name'].dropna().unique().tolist())

    # Delete option
    option = st.radio(
        "Delete by:",
        [
            "Date Range",
            "Name",
            "Specific Record"
        ],
        index=0
    )

    conn = get_db()
    cursor = conn.cursor()

    # =========================================================
    # 1. DELETE BY DATE RANGE
    # =========================================================

    if option == "Date Range":

        min_date = df['date'].min().date()
        max_date = df['date'].max().date()

        from_date = st.date_input(
            "From Date",
            value=min_date,
            min_value=min_date,
            max_value=max_date
        )

        to_date = st.date_input(
            "To Date",
            value=max_date,
            min_value=min_date,
            max_value=max_date
        )

        if st.button(
            "Delete Tiffin Records by Date",
            type="primary"
        ):

            if from_date > to_date:

                st.error(
                    "❎ Start Date cannot be after End Date."
                )

            else:

                cursor.execute(
                    """
                    DELETE FROM tiffin
                    WHERE date BETWEEN %s AND %s
                    """,
                    (
                        from_date,
                        to_date
                    )
                )

                deleted_count = cursor.rowcount

                conn.commit()

                st.success(
                    f"✅ Deleted {deleted_count} Tiffin record(s) "
                    f"from {from_date} to {to_date}."
                )

    # =========================================================
    # 2. DELETE BY NAME
    # =========================================================

    elif option == "Name":

        selected_name = st.selectbox(
            "Select Name",
            ["-- SELECT --"] + names
        )

        if st.button(
            "Delete Tiffin Records by Name",
            type="primary"
        ):

            if selected_name == "-- SELECT --":

                st.warning(
                    "⚠️ Please select a name."
                )

            else:

                cursor.execute(
                    """
                    DELETE FROM tiffin
                    WHERE name = %s
                    """,
                    (selected_name,)
                )

                deleted_count = cursor.rowcount

                conn.commit()

                st.success(
                    f"✅ Deleted {deleted_count} Tiffin record(s) "
                    f"for {selected_name}."
                )

    # =========================================================
    # 3. DELETE SPECIFIC RECORD
    # =========================================================

    else:

        st.markdown(
            "### 🎯 Delete Specific Tiffin Record"
        )

        # -----------------------------
        # Select Name
        # -----------------------------

        selected_name = st.selectbox(
            "Select Name",
            ["-- SELECT --"] + names,
            key="delete_specific_name"
        )

        if selected_name != "-- SELECT --":

            # Filter records for selected person
            person_df = df[
                df['name'] == selected_name
            ].copy()

            # -----------------------------
            # Select Date
            # -----------------------------

            available_dates = sorted(
                person_df['date']
                .dt.date
                .unique()
                .tolist()
            )

            selected_date = st.selectbox(
                "Select Date",
                available_dates,
                key="delete_specific_date"
            )

            # Filter date
            date_df = person_df[
                person_df['date'].dt.date == selected_date
            ].copy()

            # -----------------------------
            # Select Shift
            # -----------------------------

            if 'shift' in date_df.columns:

                shifts = sorted(
                    date_df['shift']
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                )

            else:
                shifts = []

            if not shifts:

                st.warning(
                    "⚠️ No shift found for this record."
                )

            else:

                selected_shift = st.selectbox(
                    "Select Shift",
                    shifts,
                    key="delete_specific_shift"
                )

                # -----------------------------
                # Show selected record
                # -----------------------------

                selected_record = date_df[
                    date_df['shift'].astype(str)
                    == str(selected_shift)
                ]

                st.markdown("#### Selected Record")

                st.dataframe(
                    selected_record,
                    use_container_width=True,
                    hide_index=True
                )

                st.warning(
                    f"⚠️ You are about to delete: "
                    f"**{selected_name} | "
                    f"{selected_date.strftime('%d-%m-%Y')} | "
                    f"{selected_shift}**"
                )

                # -----------------------------
                # Delete button
                # -----------------------------

                if st.button(
                    "🗑️ Delete This Record",
                    type="primary",
                    key="delete_specific_record"
                ):

                    cursor.execute(
                        """
                        DELETE FROM tiffin
                        WHERE name = %s
                          AND date = %s
                          AND shift = %s
                        """,
                        (
                            selected_name,
                            selected_date,
                            selected_shift
                        )
                    )

                    deleted_count = cursor.rowcount

                    conn.commit()

                    if deleted_count > 0:

                        st.success(
                            f"✅ Deleted successfully: "
                            f"{selected_name} | "
                            f"{selected_date.strftime('%d-%m-%Y')} | "
                            f"{selected_shift}"
                        )

                        st.rerun()

                    else:

                        st.error(
                            "❌ Record not found or already deleted."
                        )

    # Close cursor only. The connection is cached and must remain open.
    cursor.close()


def delete_account_page():
    # PNG file load & encode
    img_base64 = load_image("images/delete.png")

    # Display icon + text side by side
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 8px; font-size: 1.25rem;">
            <img src="data:image/png;base64,{img_base64}" width="30" />
            <span>Delete Account Records</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    df = fetch_account_records_with_loader()
    names = df['name'].unique().tolist() if not df.empty else []

    if df.empty:
        st.info("No Account records available to delete.")
        return

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()

    option = st.radio("Delete by:", ["Date Range", "Name"], index=0)

    conn = get_db()
    cursor = conn.cursor()

    if option == "Date Range":
        from_date = st.date_input("From Date", value=min_date, min_value=min_date, max_value=max_date, key="acc_from")
        to_date = st.date_input("To Date", value=max_date, min_value=min_date, max_value=max_date, key="acc_to")

        if st.button("Delete Account Records by Date"):
            if from_date > to_date:
                st.error("❎ Start Date cannot be after End Date.")
            else:
                cursor.execute("""
                    DELETE FROM account_records
                    WHERE date BETWEEN %s AND %s
                """, (from_date, to_date))
                deleted_count = cursor.rowcount
                conn.commit()
                st.success(f"✅ Deleted {deleted_count} Account record(s) from {from_date} to {to_date}.")

    else:  # Delete by Name
        selected_name = st.selectbox("Select Name", ["-- SELECT --"] + names, key="acc_name")
        if st.button("Delete Account Records by Name"):
            if selected_name == "-- SELECT --":
                st.warning("⚠️ Please select a name.")
            else:
                cursor.execute("""
                    DELETE FROM account_records
                    WHERE name = %s
                """, (selected_name,))
                deleted_count = cursor.rowcount
                conn.commit()
                st.success(f"✅ Deleted {deleted_count} Account record(s) for {selected_name}.")

    cursor.close()
    fetch_all.clear()


LOGIN_USER_HASH = b"$2b$12$tAAm6RQ775w8WJBW9brlXuHDgiYuMn3UcKI5gKRm4CCIbNp9lHXfi"
LOGIN_PASS_HASH = b"$2b$12$xfVNu267cnWT0hjsrzoWQ.AOYvxcm9GdWjjAlmcSG8IFBGf3IuP62"


def login():
    img_base64 = load_image("images/icons8-dinner-64.png")

    st.markdown(
        f"""
        <div style="text-align: center; display: flex; justify-content: center; align-items: center; gap: 10px;">
            <img src="data:image/png;base64,{img_base64}" width="35" />
            <h2 style="margin: 0;">LUNCHLOGIX SYSTEM</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    with open("images/icons8-authentication-100.png", "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <div style="text-align: center; display: flex; justify-content: center; align-items: center; gap: 10px;">
            <img src="data:image/png;base64,{img_base64}" width="30" />
            <h2 style="margin:0;">LOGIN</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    username = st.text_input("Username", key="user")
    password = st.text_input("Password", type="password", key="pass")

    # 🔥 important: initialize state
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if st.button("Login"):
        if bcrypt.checkpw(username.encode(), LOGIN_USER_HASH) and \
                bcrypt.checkpw(password.encode(), LOGIN_PASS_HASH):

            st.session_state["logged_in"] = True
            st.success("Logged in successfully!")
            st.rerun()  # 🔥 IMPORTANT FIX
        else:
            st.error("Invalid credentials")


def account_page():
    img_base64 = load_image("images/add.png")

    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 8px; font-size: 1.25rem;">
            <img src="data:image/png;base64,{img_base64}" width="30" />
            <span>Add Monthly Expense</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    names = ["MEET", "YASH", "DHRUMIL"]

    paid_by = st.selectbox("Who Paid?", names)
    date = st.date_input("Date", value=datetime.date.today())

    product_name = st.text_input("Product Name")
    place_name = st.text_input("Place Name")

    total_amount = st.number_input("Total Amount", min_value=0.0, value=0.0, step=0.01)

    st.write("Select who was present (including payer):")
    participants = []

    for name in names:
        default_checked = True if name == paid_by else False
        if st.checkbox(name, value=default_checked):
            participants.append(name)

    if st.button("Save Expense"):

        if len(participants) == 0:
            st.warning("Select at least one participant.")
            return

        per_person_amount = round(total_amount / len(participants), 2)

        loader_box = st.empty()
        show_loader(loader_box)

        conn = get_db()
        cursor = conn.cursor()

        for name in names:
            if name in participants:
                payment_status = "PAID" if name == paid_by else "PENDING"
                person_amount = per_person_amount
            else:
                payment_status = "NOT INVOLVED"
                person_amount = 0

            cursor.execute("""
                INSERT INTO account_records 
                (date, name, product_name, place_name, total_amount,
                 per_person_amount, payment_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                date,
                name,
                product_name,
                place_name,
                total_amount,
                person_amount,
                payment_status
            ))

        conn.commit()
        cursor.close()
        fetch_all.clear()
        loader_box.empty()
        st.success(f"Expense added successfully! Each participant owes ₹{per_person_amount}")


def account_records_page():
    # PNG file load & encode
    img_base64 = load_image("images/view.png")

    # Display icon + text side by side
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 8px; font-size: 1.25rem;">
            <img src="data:image/png;base64,{img_base64}" width="30" />
            <span>Account Records</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    df = fetch_account_records_with_loader()

    df = df.drop(columns=["time"], errors="ignore")

    df["payment_status"] = df["payment_status"].astype(str).str.upper()

    if df.empty:

        st.info("No account records available.")

    else:

        # --- Name wise color ---


        # --- Payment Status wise color ---


        # --- Apply both styles ---

        styled_df = style_table(df).format(precision=0)

        st.dataframe(styled_df, use_container_width=True)


def edit_account_page():
    # --- Load icon ---
    img_base64 = load_image("images/edit.png")

    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 8px; font-size: 1.25rem;">
            <img src="data:image/png;base64,{img_base64}" width="30" />
            <span>Edit Account Details</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- Fetch records ---
    df = fetch_account_records_with_loader()

    if df.empty:
        st.info("No account records available.")
        st.stop()

    # ----------------------------
    # Remove Time Column
    # ----------------------------
    if "time" in df.columns:
        df = df.drop(columns=["time"])

    # ----------------------------
    # Remove extra .0000
    # ----------------------------
    numeric_cols = ["total_amount", "per_person_amount"]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: int(x) if pd.notna(x) and float(x).is_integer() else round(float(x), 2)
            )

    # --- Color functions ---


    # --- Show all records ---
    styled_df = style_table(df)

    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True
    )

    # --- Select Record ---
    record_options = [
        f"{row['name']} - {row['date']} - {row['place_name']}"
        for _, row in df.iterrows()
    ]

    selected_record = st.selectbox(
        "Select Record to Edit",
        ["-- TYPE OR SELECT --"] + record_options
    )

    if selected_record == "-- TYPE OR SELECT --":
        st.warning("⚠️ Please select a record to edit.")
        st.stop()

    # --- Extract selected record ---
    name, date_str, place = selected_record.split(" - ")
    date_obj = pd.to_datetime(date_str).date()

    filtered_df = df[
        (df["name"] == name)
        & (pd.to_datetime(df["date"]).dt.date == date_obj)
        & (df["place_name"] == place)
    ]

    if filtered_df.empty:
        st.warning("⚠️ Selected record not found!")
        st.stop()

    # Remove time column if exists
    if "time" in filtered_df.columns:
        filtered_df = filtered_df.drop(columns=["time"])

    # ----------------------------
    # Format Amount Columns
    # ----------------------------
    numeric_cols = ["total_amount", "per_person_amount"]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").round(2)

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    # --- Edit Section ---
    record = filtered_df.iloc[0]

    st.write("### ✏️ Edit Selected Record")

    edit_product = st.text_input(
        "Product Name",
        str(record["product_name"])
    )

    edit_place = st.text_input(
        "Place Name",
        str(record["place_name"])
    )

    edit_total = st.number_input(
        "Total Amount",
        value=float(record["total_amount"])
    )

    edit_per_person = st.number_input(
        "Per Person Amount",
        value=float(record["per_person_amount"]),
        step=0.01,
        format="%.2f"

    )

    payment_options = [
        "Pending",
        "Payment Done",
        "Paid",
        "Not involved"
    ]

    current_payment = str(record["payment_status"]).strip()

    payment_index = next(
        (
            i
            for i, x in enumerate(payment_options)
            if x.lower() == current_payment.lower()
        ),
        0
    )

    edit_payment = st.selectbox(
        "Payment Status",
        payment_options,
        index=payment_index
    )

    # --- Save Changes ---
    if st.button("Save Changes"):
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE account_records
            SET
                product_name=%s,
                place_name=%s,
                total_amount=%s,
                per_person_amount=%s,
                payment_status=%s
            WHERE id=%s
            """,
            (
                str(edit_product),
                str(edit_place),
                float(edit_total),
                float(edit_per_person),
                str(edit_payment),
                int(record["id"]),
            ),
        )

        conn.commit()
        cursor.close()

        st.success("✅ Record updated successfully!")

        fetch_all.clear()

    st.sidebar.image(
        "images/me.png",
        use_container_width=True
    )


st.markdown("""

<style>

/* Option Menu Container */
.nav-link{
    border-radius:16px !important;
    margin:8px 0 !important;
    padding:12px 18px !important;
    transition:0.3s;
    font-size:16px !important;
    font-weight:600 !important;
    color:white !important;
}

/* Hover */
.nav-link:hover{
    background:rgba(56,189,248,.15)!important;
    transform:translateX(6px);
    box-shadow:0 0 15px rgba(56,189,248,.25);
}

/* Selected */
.nav-pills .nav-link.active{
    background:linear-gradient(
        90deg,
        #38BDF8,
        #8B5CF6
    )!important;

    color:white!important;

    border-radius:18px!important;

    box-shadow:
    0 0 20px rgba(56,189,248,.45),
    0 0 40px rgba(139,92,246,.35);
}

/* Icon */
.nav-link i{
    font-size:18px!important;
    margin-right:10px!important;
}

</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>

/* =========================================================
   🌌 REALISTIC DAY → SUNSET → NIGHT → DAWN → DAY
   ========================================================= */

.stApp {
    position: relative;
    min-height: 100vh;
    overflow: hidden;
    background: #020617;
}

.block-container {
    padding-bottom: 0 !important;
    margin-bottom: 0 !important;
}

footer {
    display: none !important;
}
/* =========================================================
   🌤️ MAIN SKY + 4 CORNERS
   ========================================================= */

.stApp::before {

    content: "";

    position: fixed;
    inset: -3%;

    z-index: 0;
    pointer-events: none;

    background:

        radial-gradient(
            circle at 0% 0%,
            rgba(255,255,255,.18),
            transparent 32%
        ),

        radial-gradient(
            circle at 100% 0%,
            rgba(255,255,255,.14),
            transparent 34%
        ),

        radial-gradient(
            circle at 0% 100%,
            rgba(255,180,100,.12),
            transparent 38%
        ),

        radial-gradient(
            circle at 100% 100%,
            rgba(255,140,100,.12),
            transparent 38%
        ),

        linear-gradient(
            180deg,
            #4B9FD4 0%,
            #86C5E5 45%,
            #DCEEF5 100%
        );

    background-size:
        150% 150%,
        150% 150%,
        160% 160%,
        160% 160%,
        100% 100%;

    background-position:
        0% 0%,
        100% 0%,
        0% 100%,
        100% 100%,
        center;

    animation:
        skyCycle 80s linear infinite,
        cornerMove 25s ease-in-out infinite alternate;

    will-change:
        background,
        background-position,
        filter,
        transform;
}


/* =========================================================
   🌌 NIGHT ATMOSPHERE
   ========================================================= */

.stApp::after {

    content: "";

    position: fixed;
    inset: -5%;

    z-index: 1;

    pointer-events: none;

    opacity: 0;

    background:

        radial-gradient(
            circle at 50% 15%,
            rgba(80,110,180,.16),
            transparent 40%
        ),

        radial-gradient(
            circle at 0% 0%,
            rgba(35,70,135,.18),
            transparent 38%
        ),

        radial-gradient(
            circle at 100% 0%,
            rgba(35,65,125,.18),
            transparent 38%
        );

    animation:
        nightLayer 80s linear infinite;
}


/* =========================================================
   ☀️ SUN — FIXED SIZE
   ========================================================= */

.stApp .sun {

    position: fixed;

    z-index: 5;

    pointer-events: none;

    font-size: 82px;

    line-height: 1;

    width: auto;
    height: auto;

    background: none;

    border: none;

    box-shadow: none;

    text-shadow:
        0 0 4px rgba(255,255,255,1),
        0 0 10px rgba(255,250,190,1),
        0 0 20px rgba(255,225,90,1),
        0 0 38px rgba(255,200,55,.90),
        0 0 60px rgba(255,165,25,.65);

    animation:
        sunPath 80s linear infinite;
}


/* =========================================================
   🌕 MOON — FIXED SIZE
   ========================================================= */

.stApp .moon {

    position: fixed;

    z-index: 5;

    pointer-events: none;

    font-size: 68px;

    line-height: 1;

    width: auto;
    height: auto;

    background: none;

    border: none;

    box-shadow: none;

    opacity: 0;

    text-shadow:
        0 0 5px rgba(255,255,255,1),
        0 0 14px rgba(240,245,255,1),
        0 0 28px rgba(215,230,255,.90),
        0 0 45px rgba(175,200,255,.70),
        0 0 70px rgba(140,175,255,.40);

    animation:
        moonPath 80s linear infinite;
}


/* =========================================================
   ⭐ STARS
   STATIC SIZE + STATIC POSITION
   NO ZOOM
   NO TWINKLE
   ========================================================= */

.stApp .stars {

    position: fixed;

    width: 3px;
    height: 3px;

    left: 0;
    top: 0;

    z-index: 4;

    pointer-events: none;

    border-radius: 50%;

    background: white;

    opacity: 0;

    box-shadow:

        7vw 15vh 0 white,
        15vw 28vh 0 rgba(255,255,255,.9),
        22vw 11vh 0 white,
        29vw 23vh 0 rgba(225,235,255,.9),
        37vw 8vh 0 white,

        44vw 20vh 0 rgba(255,255,255,.95),
        52vw 13vh 0 white,
        59vw 28vh 0 rgba(225,235,255,.9),
        67vw 9vh 0 white,
        75vw 22vh 0 rgba(255,255,255,.9),

        84vw 14vh 0 white,
        92vw 29vh 0 rgba(225,235,255,.9),

        12vw 43vh 0 white,
        34vw 38vh 0 rgba(255,255,255,.9),
        71vw 42vh 0 white;

    animation:
        starsVisibility 80s linear infinite;
}


/* =========================================================
   ☁️ CLOUDS
   ========================================================= */

.stApp .clouds {

    position: fixed;

    width: 170px;
    height: 48px;

    border-radius: 50px;

    z-index: 4;

    pointer-events: none;

    background:
        linear-gradient(
            180deg,
            rgba(255,255,255,.94),
            rgba(225,237,244,.70)
        );

    filter: blur(1px);

    box-shadow:
        0 8px 20px rgba(60,90,110,.12);

    opacity: 0;

    animation:
        cloudVisibility 80s linear infinite,
        cloudMove 48s linear infinite;
}


/* =========================================================
   ☁️ CLOUD BUMPS
   ========================================================= */

.stApp .clouds::before {

    content: "";

    position: absolute;

    width: 70px;
    height: 70px;

    left: 25px;
    bottom: 10px;

    border-radius: 50%;

    background:
        linear-gradient(
            180deg,
            rgba(255,255,255,.97),
            rgba(225,237,244,.72)
        );
}


.stApp .clouds::after {

    content: "";

    position: absolute;

    width: 82px;
    height: 82px;

    left: 75px;
    bottom: 8px;

    border-radius: 50%;

    background:
        linear-gradient(
            180deg,
            rgba(255,255,255,.97),
            rgba(225,237,244,.72)
        );
}


/* =========================================================
   ☁️ CLOUD POSITIONS
   ========================================================= */

.stApp .cloud1 {
    top: 17%;
    left: -220px;
    transform: scale(.85);
    animation-delay: 0s, 0s;
}

.stApp .cloud2 {
    top: 29%;
    left: -260px;
    transform: scale(.62);
    animation-delay: 0s, -12s;
}

.stApp .cloud3 {
    top: 11%;
    left: -240px;
    transform: scale(.55);
    animation-delay: 0s, -23s;
}

.stApp .cloud4 {
    top: 39%;
    left: -280px;
    transform: scale(.75);
    animation-delay: 0s, -30s;
}

.stApp .cloud5 {
    top: 24%;
    left: -200px;
    transform: scale(.48);
    animation-delay: 0s, -38s;
}

.stApp .cloud6 {
    top: 47%;
    left: -250px;
    transform: scale(.58);
    animation-delay: 0s, -18s;
}


/* =========================================================
   🌈 SKY COLOR CYCLE
   ========================================================= */

@keyframes skyCycle {

    /* =====================================================
       ☀️ DAY
       ===================================================== */

    0% {

        background:
            radial-gradient(
                circle at 0% 0%,
                rgba(255,255,255,.18),
                transparent 32%
            ),

            radial-gradient(
                circle at 100% 0%,
                rgba(255,255,255,.14),
                transparent 34%
            ),

            radial-gradient(
                circle at 0% 100%,
                rgba(120,200,255,.10),
                transparent 38%
            ),

            radial-gradient(
                circle at 100% 100%,
                rgba(100,180,240,.10),
                transparent 38%
            ),

            linear-gradient(
                180deg,
                #3D95D0 0%,
                #79BDE2 43%,
                #D9EDF5 100%
            );

        filter:
            brightness(1.08)
            saturate(1.05);
    }


    /* =====================================================
       ☀️ MID DAY
       ===================================================== */

    18% {

        background:
            radial-gradient(
                circle at 0% 0%,
                rgba(255,255,255,.20),
                transparent 32%
            ),

            radial-gradient(
                circle at 100% 0%,
                rgba(255,255,255,.16),
                transparent 34%
            ),

            linear-gradient(
                180deg,
                #469DD5 0%,
                #82C4E7 48%,
                #E1F0F6 100%
            );

        filter:
            brightness(1.06)
            saturate(1.08);
    }


    /* =====================================================
       🌇 SUNSET START
       ===================================================== */

    27% {

        background:
            radial-gradient(
                circle at 78% 55%,
                rgba(255,190,100,.42),
                transparent 34%
            ),

            radial-gradient(
                circle at 15% 80%,
                rgba(255,135,90,.20),
                transparent 38%
            ),

            linear-gradient(
                180deg,
                #3D78A6 0%,
                #C07B70 48%,
                #F0A060 72%,
                #F5C078 100%
            );

        filter:
            brightness(1)
            saturate(1.18);
    }


    /* =====================================================
       🌇 SUNSET
       ===================================================== */

    34% {

        background:
            radial-gradient(
                circle at 82% 60%,
                rgba(255,190,90,.62),
                transparent 30%
            ),

            linear-gradient(
                180deg,
                #315474 0%,
                #865E69 32%,
                #D06F62 56%,
                #F09A61 76%,
                #F5C17D 100%
            );

        filter:
            brightness(.94)
            saturate(1.22);
    }


    /* =====================================================
       🌆 DUSK
       ===================================================== */

    40% {

        background:
            radial-gradient(
                circle at 70% 65%,
                rgba(210,120,100,.25),
                transparent 32%
            ),

            linear-gradient(
                180deg,
                #243A59 0%,
                #4E4864 30%,
                #77536A 55%,
                #A66B68 78%,
                #C4816B 100%
            );

        filter:
            brightness(.76)
            saturate(1.08);
    }


    /* =====================================================
       🌌 NIGHT
       ===================================================== */

    46% {

        background:
            radial-gradient(
                circle at 50% 20%,
                rgba(65,90,150,.20),
                transparent 42%
            ),

            linear-gradient(
                180deg,
                #071329 0%,
                #0A1B35 38%,
                #102746 70%,
                #172C48 100%
            );

        filter:
            brightness(.62)
            saturate(.95);
    }


    /* =====================================================
       🌙 DEEP NIGHT
       ===================================================== */

    55% {

        background:
            radial-gradient(
                circle at 50% 18%,
                rgba(75,105,175,.16),
                transparent 38%
            ),

            linear-gradient(
                180deg,
                #020817 0%,
                #061226 35%,
                #091A31 68%,
                #0C2039 100%
            );

        filter:
            brightness(.50)
            saturate(.88);
    }


    /* =====================================================
       🌌 MIDNIGHT
       ===================================================== */

    68% {

        background:
            radial-gradient(
                circle at 52% 18%,
                rgba(75,105,175,.12),
                transparent 40%
            ),

            linear-gradient(
                180deg,
                #010611 0%,
                #030B1B 38%,
                #061226 70%,
                #08172B 100%
            );

        filter:
            brightness(.46)
            saturate(.82);
    }


    /* =====================================================
       🌙 PRE DAWN
       ===================================================== */

    76% {

        background:
            radial-gradient(
                circle at 15% 72%,
                rgba(100,90,150,.18),
                transparent 38%
            ),

            linear-gradient(
                180deg,
                #030B1D 0%,
                #101A36 38%,
                #292743 68%,
                #4B3850 100%
            );

        filter:
            brightness(.55)
            saturate(.92);
    }


    /* =====================================================
       🌄 DAWN
       ===================================================== */

    84% {

        background:
            radial-gradient(
                circle at 8% 75%,
                rgba(255,155,100,.28),
                transparent 38%
            ),

            linear-gradient(
                180deg,
                #172642 0%,
                #4B4964 35%,
                #B26D6B 68%,
                #E6A06D 100%
            );

        filter:
            brightness(.72)
            saturate(1.05);
    }


    /* =====================================================
       🌅 SUNRISE
       ===================================================== */

    91% {

        background:
            radial-gradient(
                circle at 8% 65%,
                rgba(255,190,100,.40),
                transparent 32%
            ),

            linear-gradient(
                180deg,
                #3479A9 0%,
                #76AFCB 40%,
                #D58A6E 75%,
                #F0B477 100%
            );

        filter:
            brightness(.92)
            saturate(1.08);
    }


    /* =====================================================
       ☀️ DAY AGAIN
       ===================================================== */

    100% {

        background:
            radial-gradient(
                circle at 0% 0%,
                rgba(255,255,255,.18),
                transparent 32%
            ),

            radial-gradient(
                circle at 100% 0%,
                rgba(255,255,255,.14),
                transparent 34%
            ),

            linear-gradient(
                180deg,
                #3D95D0 0%,
                #79BDE2 43%,
                #D9EDF5 100%
            );

        filter:
            brightness(1.08)
            saturate(1.05);
    }
}


/* =========================================================
   🌌 NIGHT ATMOSPHERE
   ========================================================= */

@keyframes nightLayer {

    0%,
    40% {
        opacity: 0;
    }

    47% {
        opacity: .30;
    }

    55%,
    70% {
        opacity: .85;
    }

    78% {
        opacity: .40;
    }

    85%,
    100% {
        opacity: 0;
    }
}


/* =========================================================
   ☀️ SUN MOVEMENT
   SAME SPEED — NO ZOOM
   ========================================================= */

@keyframes sunPath {

    /* Day */

    0% {
        left: 47%;
        top: 9%;
        opacity: 1;
    }

    /* Afternoon */

    18% {
        left: 58%;
        top: 20%;
        opacity: 1;
    }

    /* Sunset approach */

    30% {
        left: 70%;
        top: 38%;
        opacity: 1;
    }

    /* Sunset */

    37% {
        left: 82%;
        top: 58%;
        opacity: .85;
    }

    /* Gone */

    40% {
        left: 105%;
        top: 75%;
        opacity: 0;
    }

    /* Night */

    40%,
    82% {
        left: 105%;
        top: 75%;
        opacity: 0;
    }

    /* Sunrise */

    83% {
        left: -10%;
        top: 76%;
        opacity: 0;
    }

    88% {
        left: 5%;
        top: 61%;
        opacity: .55;
    }

    94% {
        left: 25%;
        top: 29%;
        opacity: .90;
    }

    /* Day */

    100% {
        left: 47%;
        top: 9%;
        opacity: 1;
    }
}


/* =========================================================
   🌕 MOON MOVEMENT
   SAME SPEED — NO ZOOM
   ========================================================= */

@keyframes moonPath {

    /* Day */

    0%,
    38% {
        left: -10%;
        top: 72%;
        opacity: 0;
    }

    /* Moonrise */

    40% {
        left: 5%;
        top: 62%;
        opacity: .35;
    }

    /* Night */

    50% {
        left: 27%;
        top: 35%;
        opacity: .80;
    }

    /* Midnight */

    60% {
        left: 50%;
        top: 12%;
        opacity: 1;
    }

    /* Late night */

    70% {
        left: 70%;
        top: 30%;
        opacity: .95;
    }

    /* Moonset */

    78% {
        left: 88%;
        top: 58%;
        opacity: .65;
    }

    /* Gone */

    82% {
        left: 105%;
        top: 76%;
        opacity: 0;
    }

    /* Day */

    82%,
    100% {
        left: 105%;
        top: 76%;
        opacity: 0;
    }
}


/* =========================================================
   ⭐ STARS
   STATIC — ONLY FADE IN/OUT
   ========================================================= */

@keyframes starsVisibility {

    0%,
    38% {
        opacity: 0;
    }

    44% {
        opacity: .30;
    }

    50% {
        opacity: .70;
    }

    56%,
    72% {
        opacity: 1;
    }

    78% {
        opacity: .50;
    }

    84%,
    100% {
        opacity: 0;
    }
}


/* =========================================================
   ☁️ CLOUD VISIBILITY
   ========================================================= */

@keyframes cloudVisibility {

    0% {
        opacity: .78;
    }

    20% {
        opacity: .82;
    }

    28% {
        opacity: .72;
    }

    35% {
        opacity: .45;
    }

    42% {
        opacity: .12;
    }

    48%,
    100% {
        opacity: 0;
    }
}


/* =========================================================
   ☁️ CLOUD MOVEMENT
   ========================================================= */

@keyframes cloudMove {

    from {
        margin-left: -220px;
    }

    to {
        margin-left: 125vw;
    }
}


/* =========================================================
   🌈 VERY SLOW CORNER LIGHT
   ========================================================= */

@keyframes cornerMove {

    0% {
        transform:
            scale(1)
            translate3d(0,0,0);
    }

    50% {
        transform:
            scale(1.018)
            translate3d(.25%,-.2%,0);
    }

    100% {
        transform:
            scale(1.035)
            translate3d(-.25%,.2%,0);
    }
}


/* =========================================================
   ✨ CONTENT ABOVE SKY
   ========================================================= */

.stApp > * {
    position: relative;
    z-index: 10;
}


/* =========================================================
   🧹 STREAMLIT CLEANUP
   ========================================================= */

html,
body {
    margin: 0 !important;
    padding: 0 !important;
}

[data-testid="stAppViewContainer"] {
    padding-bottom: 0 !important;
}

[data-testid="stAppViewContainer"] .main {
    padding-bottom: 0 !important;
}

.block-container {
    padding-bottom: 0 !important;
}

footer {
    display: none !important;
}

[data-testid="stDecoration"] {
    display: none !important;
}


/* =========================================================
   INPUTS
   ========================================================= */

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {

    background:
        rgba(5,12,24,.72);

    border:
        1px solid rgba(255,255,255,.12);

    border-radius: 14px;
}


/* =========================================================
   BUTTON
   ========================================================= */

.stButton button {

    background:
        linear-gradient(
            135deg,
            #FF1744,
            #E91E63,
            #9C5DE5
        );

    color: white;

    border: none;

    border-radius: 15px;

    font-weight: 700;

    height: 50px;

    box-shadow:
        0 8px 28px rgba(255,23,68,.25);
}


/* =========================================================
   METRIC CARDS
   ========================================================= */

[data-testid="stMetric"] {

    background:
        rgba(5,12,24,.30);

    border:
        1px solid rgba(255,255,255,.12);

    border-radius: 18px;

    padding: 16px;

    backdrop-filter: blur(10px);
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# ☀️ 🌕 ⭐ ☁️ SKY OBJECTS
# =========================================================

st.markdown("""
<div class="sun">☀️</div>

<div class="moon">🌕</div>

<div class="stars"></div>

<div class="clouds cloud1"></div>
<div class="clouds cloud2"></div>
<div class="clouds cloud3"></div>
<div class="clouds cloud4"></div>
<div class="clouds cloud5"></div>
<div class="clouds cloud6"></div>
""", unsafe_allow_html=True)


st.markdown("""
<style>

/* ===============================
   PREMIUM SIDEBAR BACKGROUND
================================ */

[data-testid="stSidebar"]{

background:
radial-gradient(
circle at top left,
rgba(56,189,248,.25),
transparent 35%
),

linear-gradient(
180deg,
#020617,
#07111F,
#0B0828
);

border-right:
1px solid rgba(255,255,255,.12);

}


/* Hide Streamlit Navigation */

[data-testid="stSidebarNav"]{
display:none;
}


/* ===============================
        LOGO CARD
================================ */

.logo{

padding:28px 15px;

border-radius:10px;

background:

linear-gradient(
145deg,
rgba(255,255,255,.12),
rgba(255,255,255,.03)
);

border:

1px solid rgba(255,255,255,.18);

backdrop-filter:
blur(25px);


box-shadow:

0 20px 50px rgba(0,0,0,.5),

inset
0 0 30px rgba(56,189,248,.15);


text-align:center;

margin-bottom:25px;

}


/* Logo Icon */

.logoicon{

font-size:75px;

filter:
drop-shadow(
0 0 25px #38BDF8
);

}


/* Logo Text */

.logotitle{

font-size:38px;

font-weight:950;

letter-spacing:2px;


background:

linear-gradient(
90deg,
#38BDF8,
#A855F7,
#F472B6
);


-webkit-background-clip:text;

color:transparent;


}


/* Subtitle */

.subtitle{

font-size:14px;

letter-spacing:3px;

color:#CBD5E1;

margin-top:5px;

}


/* ===============================
        SIDEBAR CARDS
================================ */


.card{

padding:18px;

margin-bottom:15px;


border-radius:10px;


background:

rgba(255,255,255,.06);


border:

1px solid rgba(255,255,255,.12);


backdrop-filter:

blur(20px);


box-shadow:

0 15px 40px rgba(0,0,0,.35);


transition:.3s;

color:white;

}



.card:hover{


transform:
translateY(-4px);


border-color:

rgba(56,189,248,.5);


box-shadow:

0 0 35px rgba(56,189,248,.25);


}


/* ===============================
       STATUS COLORS
================================ */


.green{

color:#22C55E;

font-weight:800;

text-shadow:

0 0 15px #22C55E;

}



.red{

color:#EF4444;

font-weight:800;

text-shadow:

0 0 15px #EF4444;

}


/* ===============================
       DATABASE LIVE CARD
================================ */


.live-dot{

height:12px;

width:12px;

background:#22C55E;

border-radius:50%;

display:inline-block;


box-shadow:

0 0 20px #22C55E;


animation:

pulse 1.5s infinite;

}


@keyframes pulse{

0%{

opacity:1;

}

50%{

opacity:.3;

}

100%{

opacity:1;

}

}



/* ===============================
        PREMIUM VERSION BOX
================================ */

.version{

position:relative;

padding:25px 15px;

border-radius:10px;


background:

linear-gradient(
145deg,
rgba(255,255,255,0.14),
rgba(255,255,255,0.04)
);


border:

1px solid rgba(255,255,255,.22);


backdrop-filter:

blur(25px);



box-shadow:

0 20px 50px rgba(0,0,0,.45),

inset 0 0 35px rgba(56,189,248,.15),

0 0 40px rgba(168,85,247,.35);



text-align:center;

color:white;


overflow:hidden;


margin-top:35px;

}


/* Animated Glow Line */

.version::before{

content:"";

position:absolute;

top:0;

left:-50%;


width:200%;

height:2px;


background:

linear-gradient(
90deg,
transparent,
#38BDF8,
#A855F7,
transparent
);


animation:

moveLine 3s linear infinite;

}



@keyframes moveLine{

0%{

transform:translateX(-30%);

}

100%{

transform:translateX(30%);

}

}



/* App Name */

.appname{


font-size:32px;


font-weight:950;


letter-spacing:3px;



background:

linear-gradient(
90deg,
#38BDF8,
#A855F7,
#F472B6
);



-webkit-background-clip:text;


color:transparent;



text-shadow:

0 0 30px rgba(56,189,248,.4);


}



/* Premium Edition */

.edition{


font-size:12px;


letter-spacing:5px;


margin-top:8px;


color:#CBD5E1;


font-weight:700;

}



/* Divider */

.version-line{


height:1px;


margin:18px 25px;


background:

linear-gradient(
90deg,
transparent,
rgba(255,255,255,.5),
transparent
);

}



/* Version Number */

.ver{


font-size:20px;


font-weight:900;


letter-spacing:2px;


color:white;



}



/* Status */

.status{


display:inline-block;


margin-top:15px;


padding:7px 18px;


border-radius:50px;



background:

rgba(34,197,94,.15);



border:

1px solid rgba(34,197,94,.4);



color:#22C55E;


font-size:13px;


font-weight:800;



box-shadow:

0 0 20px rgba(34,197,94,.35);


}
}


/* ===============================
     REMOVE PADDING
================================ */


section[data-testid="stSidebar"] > div{

padding-top:1rem;

}



</style>
""", unsafe_allow_html=True)
# --------------------
# Sidebar
# --------------------
st.markdown("""
  <style>
  .logotitle {
      font-size: 35px;  
      font-weight: bold;
  }
  </style>
  """, unsafe_allow_html=True)
with st.sidebar:
    st.markdown("""
      <div class="logo">

      <div class="logoicon">

      </div>

      <div class="logotitle">
      LUNCHLOGIX
      </div>

      <div class="subtitle">
      PREMIUM EDITION
      <br>
      Manage • Track • Grow
      </div>

      </div>
      """, unsafe_allow_html=True)

    st.markdown("---")

    # ======================
    # SIDEBAR NAVIGATION
    # ======================
    with st.sidebar:

        if st.session_state.get("logged_in", False):

            st.markdown("### 📌 Navigation")

            menu = option_menu(
                menu_title=None,
                options=[
                    "Add Tiffin Entry",
                    "View Tiffin Records",
                    "Analytics Dashboard",
                    "Update Payment Status",
                    "Export Data",
                    "Remove Tiffin Records",
                    "Edit Tiffin Records",
                    "Add Expense Entry",
                    "View Expense Records",
                    "Remove Expenses",
                    "Edit Expense Details",
                    "Settings",
                ],

icons=[
    "plus-circle",
    "search",
    "bar-chart",
    "credit-card",
    "download",
    "trash",
    "pencil-square",
    "wallet2",
    "search-heart",
    "trash3",
    "pencil",
    "gear",
                ],
                default_index=0,
                styles={
                    "container": {
                        "padding": "6px",
                        "background-color": "rgba(7 16 30)",
                        "border-radius": "-2px",
                    },
                    "nav-link": {
                        "font-size": "15px",
                        "font-weight": "600",
                        "border-radius": "-2px",
                        "margin": "6px 0",
                        "--hover-color": "rgba(72 48 22)",
                    },
                    "nav-link-selected": {
                        "background": "#ff741a",
                        "color": "white",
                    },
                },
            )

        else:
            menu = None
    # --------------------
    # Login Status
    # --------------------
    with st.sidebar:
        db_connected = check_db_connection()

        # Login Status
        is_logged = st.session_state.get("logged_in", False)

        # Database Status
        db_status = "Connected" if db_connected else "Disconnected"
        db_color = "green" if db_connected else "red"

        db_statu = "Responded" if is_logged else "Not Responded"
        db_colo = "green" if is_logged else "red"

        db_stats = "Completed" if is_logged else "Not Completed"
        db_colr = "green" if is_logged else "red"

        db_staus = "Connected" if is_logged else "Not Connected"
        db_coor = "green" if is_logged else "red"

        st.markdown("### ⚙️ SYSTEM STATUS")

        st.markdown(
            f"""
            <div class='card'>
            🗄️ Database

            <span class='{db_color}'>
            ● {db_status}
            </span>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
                  <div class='card'>
                  🖥️ Server

                  <span class='{db_coor}'>
                  ● {db_staus}
                  </span>

                  </div>
                  """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class='card'>
            📊 Analytics

            <span class='{db_colo}'>
            ● {db_statu}
            </span>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class='card'>
            🛢️ Backup

            <span class='{db_colr}'>
            ● {db_stats}
            </span>

            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("""
  <div class='version'>

  LUNCHLOGIX

  <div class='ver'>
  v1.7.09
  </div>

  </div>
  """, unsafe_allow_html=True)

# =========================
# AIVEN CONFIG
# =========================

TOKEN = st.secrets["TOKEN"]
PROJECT = st.secrets["PROJECT"]
SERVICE = st.secrets["SERVICE"]

HEADERS = {
    "Authorization": f"aivenv1 {TOKEN}",
    "Content-Type": "application/json"
}

AIVEN_URL = (
    f"https://api.aiven.io/v1/project/"
    f"{PROJECT}/service/{SERVICE}"
)


# =========================
# FAST STATUS CHECK
# =========================

@st.cache_data(ttl=1)
def check_aiven_status():
    try:

        response = requests.get(
            AIVEN_URL,
            headers=HEADERS,
            timeout=10
        )

        if response.status_code == 200:
            return response.json()["service"]["state"]


    except:

        return None

    return None


# =========================
# DATABASE ACTION
# =========================

def database_power(action):
    payload = {
        "powered": action
    }

    try:

        response = requests.put(
            AIVEN_URL,
            headers=HEADERS,
            json=payload,
            timeout=(3, 30)
        )

        return response.status_code in [200, 202], response.text


    except Exception as e:

        return False, str(e)


# =========================
# SETTINGS PAGE
# =========================


def database_settings_page():
    st.markdown("""
    <h4 style="margin-bottom:0;">
    ⚙️ Settings
    </h4>
    """, unsafe_allow_html=True)

    st.divider()

    if "db_action_running" not in st.session_state:
        st.session_state.db_action_running = False

    col1, col2 = st.columns(2)

    # =========================
    # START
    # =========================

    with col1:

        if st.button(
                "🟢 START DATABASE",
                use_container_width=True,
                disabled=st.session_state.db_action_running,
                key="start_database_btn"
        ):
            # Lock button immediately
            st.session_state.db_action_running = True
            st.rerun()

        # =========================
        # START PROCESS
        # =========================

        if st.session_state.db_action_running:

            success, error = database_power(True)

            if success:

                progress = st.progress(0)

                status_box = st.empty()

                caption_box = st.empty()

                percentage = 0

                messages = [

                    "⏳ Starting database...",
                    "🔄 Preparing database server...",
                    "🌐 Checking Aiven status...",
                    "⚙️ Loading database environment...",
                    "🔐 Creating secure connection..."

                ]

                msg = 0

                while True:

                    state = check_aiven_status()

                    if state == "RUNNING":

                        progress.progress(100)

                        caption_box.caption(
                            "🟢 LUNCHLOGIX Database Control • Connected"
                        )

                        status_box.success(
                            "Database Ready 🚀"
                        )

                        st.cache_resource.clear()

                        st.session_state.db_action_running = False

                        st.rerun()

                    else:

                        percentage = min(
                            percentage + 5,
                            97
                        )

                        progress.progress(percentage)

                        status_box.info(
                            f"🟢 {state} ... {percentage}%"
                        )

                        if msg < len(messages):
                            caption_box.caption(messages[msg])
                            msg += 1

                    time.sleep(1)

            else:

                st.session_state.db_action_running = False
                st.error(error)

    # =========================
    # STOP
    # =========================

    with col2:

        if st.button(
                "🔴 STOP DATABASE",
                use_container_width=True,
                disabled=st.session_state.db_action_running
        ):

            st.session_state.db_action_running = True

            success, error = database_power(False)

            if success:

                progress = st.progress(0)

                status_box = st.empty()

                caption_box = st.empty()

                percentage = 0

                messages = [

                    "⏳ Stopping database...",
                    "🔄 Closing connections...",
                    "🌐 Checking server status...",
                    "⚙️ Saving database state...",
                    "🔒 Shutdown safely..."

                ]

                msg = 0

                while True:

                    state = check_aiven_status()

                    if state in [
                        "POWEROFF",
                        "STOPPED"
                    ]:

                        progress.progress(100)

                        caption_box.caption(
                            "🔴 LUNCHLOGIX Database Control • Stopped"
                        )

                        status_box.success(
                            "Database Shutdown Completed 🚀"
                        )

                        st.cache_resource.clear()

                        st.session_state.db_action_running = False

                        st.rerun()



                    else:

                        percentage = min(
                            percentage + 5,
                            97
                        )

                        progress.progress(
                            percentage
                        )

                        status_box.warning(
                            f"🔴 {state} ... {percentage}%"
                        )

                        if msg < len(messages):
                            caption_box.caption(
                                messages[msg]
                            )

                            msg += 1

                    time.sleep(1)



            else:

                st.session_state.db_action_running = False

                st.error(error)

    st.divider()

    # =========================
    # CURRENT STATUS
    # =========================

    state = check_aiven_status()

    if state == "RUNNING":

        st.success(
            "🟢 LUNCHLOGIX Database Control • Running"
        )


    elif state in [
        "REBUILDING",
        "POWERING_ON",
        "BUILDING"
    ]:

        st.warning(
            f"🟡 LUNCHLOGIX Database Control • {state}"
        )


    else:

        st.error(
            f"🔴 LUNCHLOGIX Database Control • {state}"
        )

    st.caption(
        "LUNCHLOGIX Database Control • MANMEET'S DATABASE"
    )




# =========================================================
# FAST ADD TIFFIN PAGE
# =========================================================
# Only this page reruns when its widgets change.
# Existing calculations, billing and database logic remain unchanged.
@st.fragment
def add_tiffin_page():

    # =========================================================
    # SESSION STATE - DUPLICATE SAVE PROTECTION
    # =========================================================

    if "tiffin_saved_signature" not in st.session_state:
        st.session_state.tiffin_saved_signature = None

    if "tiffin_save_message" not in st.session_state:
        st.session_state.tiffin_save_message = None

    # =========================================================
    # CURRENT TIME
    # =========================================================

    current_time = datetime.datetime.now().strftime("%H:%M:%S")

    # =========================================================
    # ORDER OVERVIEW
    # =========================================================

    st.subheader("📋 Order Overview")

    col1, col2, col3 = st.columns(3)

    with col1:

        shift = st.selectbox(
            "🌓 Shift",
            [
                "-- SELECT DAY --",
                "DAY",
                "NIGHT"
            ],
            key="tiffin_shift"
        )

    with col2:

        selected_date = st.date_input(
            "📅 Billing Date",
            datetime.date.today(),
            key="tiffin_date"
        )

    with col3:

        tiffin_qty = st.selectbox(
            "🍱 Tiffin Quantity",
            [
                "-- SELECT Quantity --"
            ] + [1, 2, 3, 4, 5, 6],
            key="tiffin_quantity"
        )

    # =========================================================
    # VALIDATION
    # =========================================================

    if shift == "-- SELECT DAY --":
        st.warning(
            "⚠️ Please select a shift"
        )

        st.stop()

    if tiffin_qty == "-- SELECT Quantity --":
        st.warning(
            "⚠️ Please select tiffin quantity"
        )

        st.stop()

    st.divider()

    # =========================================================
    # PERSON SELECTION
    # =========================================================

    st.subheader("👥 Who ordered today?")

    names = [
        "MEET",
        "YASH",
        "DHRUMIL"
    ]

    cols = st.columns(3)

    selected_names = []

    for i, name in enumerate(names):

        with cols[i]:

            selected = st.checkbox(
                f"👤 {name}",
                key=f"person_{name}"
            )

            if selected:
                selected_names.append(name)

    # =========================================================
    # VALIDATION
    # =========================================================

    if not selected_names:
        st.warning(
            "⚠️ Please select at least one person"
        )

        st.stop()

    st.divider()

    # =========================================================
    # ROTI
    # =========================================================

    roti_qty = {}

    roti_rate = 7

    if shift == "DAY":

        st.subheader("🫓 Roti Details")

        roti_cols = st.columns(
            len(selected_names)
        )

        for i, name in enumerate(selected_names):
            with roti_cols[i]:
                roti_qty[name] = st.number_input(
                    f"{name} Roti Quantity",
                    min_value=0,
                    value=0,
                    step=1,
                    key=f"roti_{name}"
                )


    else:

        for name in selected_names:
            roti_qty[name] = 0

    # =========================================================
    # CALCULATION
    # =========================================================

    per_person_qty = round(
        float(tiffin_qty)
        / len(selected_names),
        2
    )

    per_person_amount = round(
        90 * per_person_qty,
        2
    )

    # =========================================================
    # INDIVIDUAL BILLING
    # =========================================================

    st.subheader("💳 Individual Billing")

    name_icons = {
        "MEET": "🔴",
        "YASH": "🟢",
        "DHRUMIL": "🔵"
    }

    for name in names:

        if name in selected_names:

            person_roti_qty = roti_qty.get(
                name,
                0
            )

            person_roti_amount = (
                    person_roti_qty
                    * roti_rate
            )

            person_total = (
                    per_person_amount
                    + person_roti_amount
            )

            person_col1, person_col2 = st.columns(
                [3, 1]
            )

            with person_col1:

                st.markdown(
                    f"### {name_icons.get(name, '👤')} {name}"
                )

            with person_col2:

                st.success(
                    "ACTIVE ORDER"
                )

            bill1, bill2, bill3, bill4 = st.columns(4)

            with bill1:

                st.metric(
                    "🍱 Tiffin",
                    f"{per_person_qty:.2f}"
                )

            with bill2:

                st.metric(
                    "₹ Tiffin",
                    f"₹{per_person_amount:,.2f}"
                )

            with bill3:

                st.metric(
                    "🫓 Roti",
                    f"{person_roti_qty} Nos"
                )

            with bill4:

                st.metric(
                    "💰 Total",
                    f"₹{person_total:,.2f}"
                )

            st.divider()


        else:

            st.info(
                f"ℹ️ {name} — No Tiffin Ordered Today"
            )

    # =========================================================
    # BILLING CALCULATION
    # =========================================================

    total_tiffin_amount = round(
        per_person_amount
        * len(selected_names),
        2
    )

    total_roti_amount = round(
        sum(
            roti_qty.get(name, 0)
            * roti_rate
            for name in selected_names
        ),
        2
    )

    total_amount = (
            total_tiffin_amount
            + total_roti_amount
    )

    # =========================================================
    # BILLING SUMMARY
    # =========================================================

    st.subheader("🧾 Final Billing Summary")

    summary1, summary2 = st.columns(2)

    with summary1:

        st.metric(
            "🍱 Total Tiffin Charges",
            f"₹{total_tiffin_amount:,.2f}"
        )

    with summary2:

        st.metric(
            "🫓 Total Roti Charges",
            f"₹{total_roti_amount:,.2f}"
        )

    st.success(
        f"💰 TOTAL AMOUNT PAYABLE: ₹{total_amount:,.2f}"
    )

    status1, status2 = st.columns(2)

    with status1:

        st.info(
            "🕐 Payment Status: PAYMENT PENDING"
        )

    with status2:

        st.info(
            f"📅 {selected_date.strftime('%d %B %Y')}"
        )

    st.divider()

    # =========================================================
    # CREATE CURRENT DATA SIGNATURE
    # =========================================================

    current_signature = (
        str(selected_date),
        str(shift),
        str(tiffin_qty),
        tuple(sorted(selected_names)),
        tuple(
            (
                name,
                roti_qty.get(name, 0)
            )
            for name in sorted(selected_names)
        )
    )

    # =========================================================
    # CHECK WHETHER SAME DATA WAS ALREADY SAVED
    # =========================================================

    already_saved = (
            st.session_state.tiffin_saved_signature
            == current_signature
    )

    # =========================================================
    # SAVE BUTTON
    # =========================================================

    if already_saved:

        st.success(
            "✅ This billing record is already saved."
        )

    # Keep the SAVE button in exactly the same place after every
    # fragment rerun. Disable it after the exact same record is saved.
    if st.button(
            "💾 SAVE BILLING RECORD",
            use_container_width=True,
            key="save_tiffin_record",
            disabled=already_saved,
            type="primary"
    ):

            # -------------------------------------------------
            # IMPORTANT:
            # Mark BEFORE INSERT
            # This prevents accidental double-click inserts.
            # -------------------------------------------------

            st.session_state.tiffin_saved_signature = (
                current_signature
            )

            # -------------------------------------------------
            # CREATE DATA
            # -------------------------------------------------

            data_to_insert = []

            for name in selected_names:
                qty = per_person_qty

                amount = per_person_amount

                payment_status = "PAYMENT PENDING"

                roti = roti_qty.get(
                    name,
                    0
                )

                roti_amount = (
                        roti * roti_rate
                )

                total_individual_amount = round(
                    amount + roti_amount,
                    2
                )

                day = selected_date.strftime(
                    "%A"
                ).upper()

                row = [
                    selected_date,
                    day,
                    current_time,
                    name,
                    shift,
                    qty,
                    roti,
                    roti_amount,
                    total_individual_amount,
                    payment_status
                ]

                data_to_insert.append(
                    row
                )

            # -------------------------------------------------
            # INSERT
            # -------------------------------------------------

            insert_record_with_loader(data_to_insert)

            # -------------------------------------------------
            # SUCCESS
            # -------------------------------------------------

            st.success(
                "✅ Record(s) added successfully!"
            )

            st.info(
                "🔒 This record is locked. "
                "Change any billing parameter to save again."
            )

def app():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        login()
        return

    # PNG file load & encode
    with open("images/icons8-dinner-64.png", "rb") as f:
        img_bytes = f.read()
        img_base64 = base64.b64encode(img_bytes).decode()

    # Display icon + heading centered
    st.markdown(
        f"""
        <div style="text-align: center; display: flex; justify-content: center; align-items: center; gap: 10px;">
            <img src="data:image/png;base64,{img_base64}" width="50" />
            <h2 style="margin: 0;">LUNCHLOGIX SYSTEM</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    if menu == "Remove Tiffin Records":
        delete_tiffin_page()

    elif menu == "Remove Expenses":
        delete_account_page()

    # -------------------- Add Record --------------------
    elif menu == "Add Tiffin Entry":
        add_tiffin_page()

    # -------------------- Records --------------------

    elif menu == "View Tiffin Records":

      # PNG file load & encode

        img_base64 = load_image("images/view.png")

        # Header UI
        st.markdown(
            f"""
              <div style="display: flex; align-items: center; gap: 8px; font-size: 1.25rem;">
                  <img src="data:image/png;base64,{img_base64}" width="30" />
                  <span>All Records</span>
              </div>
              """,
            unsafe_allow_html=True
        )

        df = fetch_all_with_loader()
        if df.empty:
            st.info("No records available")

        else:

            # Remove time column if exists
            if "time" in df.columns:
                df = df.drop(columns=["time"])

            # Convert date column properly
            df["date"] = pd.to_datetime(df["date"], dayfirst=True)

            today = datetime.date.today()

            if today.day >= 10:
                from_default = today.replace(day=10)

                if today.month == 12:
                    to_default = datetime.date(today.year + 1, 1, 9)
                else:
                    to_default = datetime.date(today.year, today.month + 1, 9)

            else:
                to_default = today.replace(day=9)

                if today.month == 1:
                    from_default = datetime.date(today.year - 1, 12, 10)
                else:
                    from_default = datetime.date(today.year, today.month - 1, 10)

            col1, col2 = st.columns(2)

            with col1:
                from_date = st.date_input(
                    "From Date",
                    value=from_default
                )

            with col2:
                to_date = st.date_input(
                    "To Date",
                    value=to_default
                )

                if from_date > to_date:
                    st.error("❎ From Date cannot be greater than To Date.")
                    st.stop()

                df = df[
                    (df["date"] >= pd.to_datetime(from_date)) &
                    (df["date"] <= pd.to_datetime(to_date))
                    ]
            # =========================
            # SEARCH BOX
            # =========================

            search = st.text_input(
                "🔍 Search",
                placeholder="Search Records..."
            ).strip().upper()

            if search:
                df = df[
                    df.astype(str)
                    .apply(lambda row: row.str.upper().str.contains(search).any(), axis=1)
                ]

            # =========================
            # SORT
            # =========================

            df = df.sort_values(by="date", ascending=False)

            # =========================
            # FORMAT DATE
            # =========================
            df["date"] = df["date"].dt.strftime("%d/%m/%Y")

            # =========================
            # NUMBER FORMAT
            # =========================
            numeric_cols = ["quantity", "amount", "roti", "roti_amount"]

            for col in numeric_cols:
                if col in df.columns:
                    df[col] = df[col].apply(
                        lambda x: f"{x:.2f}" if float(x) % 1 else f"{int(x)}"
                    )

            # =========================
            # COLORS
            # =========================





            # =========================
            # APPLY STYLING
            # =========================
            styled_df = style_table(df)

            st.dataframe(styled_df, use_container_width=True)
    # -------------------- Chart --------------------


    elif menu == "Analytics Dashboard":

        img_base64 = load_image("images/chart.png")

        st.markdown(

            f"""

            <div style="display: flex; align-items: center; gap: 8px; font-size: 1.25rem;"><img src="data:image/png;base64,{img_base64}" width="30" /><span>Analytics Dashboard</span>

            </div>

            """,

            unsafe_allow_html=True

        )

        df = fetch_all_with_loader()
        if df.empty:

            st.info("No records to plot.")


        else:

            # ✅ Date convert

            df['date'] = pd.to_datetime(df['date'], errors='coerce')

            # ✅ Remove zero quantity

            df = df[df["quantity"] > 0]

            today = date.today()

            if today.day >= 10:
                from_date_default = today.replace(day=10)
                to_date_default = from_date_default + relativedelta(months=1) - relativedelta(days=1)
            else:
                to_date_default = today.replace(day=9)
                from_date_default = to_date_default - relativedelta(months=1) + relativedelta(days=1)

            col1, col2 = st.columns(2)

            with col1:
                from_date = st.date_input(
                    "From Date",
                    value=from_date_default,
                    key="analytics_from_date"
                )

            with col2:
                to_date = st.date_input(
                    "To Date",
                    value=to_date_default,
                    key="analytics_to_date"
                )

            # Apply Filter
            df = df[
                (df["date"] >= pd.to_datetime(from_date)) &
                (df["date"] <= pd.to_datetime(to_date))
                ]

            if df.empty:
                st.warning("No data found for selected billing cycle.")
                st.stop()
            # ✅ Apply filter

            df = df[

                (df['date'] >= pd.to_datetime(from_date)) &

                (df['date'] <= pd.to_datetime(to_date))

                ]

            if df.empty:

                st.info("No orders found for selected date range.")


            else:
                # ======================================================
                # ✅ SUMMARY
                # ======================================================

                summary_df = (
                    df.groupby("name", as_index=False)
                    .agg(
                        total_tiffin=("quantity", "sum"),
                        total_roti=("roti", "sum"),
                        total_roti_amount=("roti_amount", "sum")
                    )
                )

                # ======================================================
                # ✅ AMOUNT CALCULATION
                # ======================================================

                summary_df["total_amount"] = summary_df["total_tiffin"] * 90

                summary_df["final_amount"] = (
                        summary_df["total_amount"] +
                        summary_df["total_roti_amount"]
                )

                # ======================================================
                # ✅ TOTAL ROW
                # ======================================================

                total_row = pd.DataFrame({
                    "name": ["TOTAL"],
                    "total_tiffin": [summary_df["total_tiffin"].sum()],
                    "total_roti": [summary_df["total_roti"].sum()],
                    "total_roti_amount": [summary_df["total_roti_amount"].sum()],
                    "total_amount": [summary_df["total_amount"].sum()],
                    "final_amount": [summary_df["final_amount"].sum()]
                })

                summary_df = pd.concat(
                    [summary_df, total_row],
                    ignore_index=True
                )

                # ======================================================
                # ✅ COLUMN ORDER
                # ======================================================

                summary_df = summary_df[
                    [
                        "name",
                        "total_tiffin",
                        "total_amount",
                        "total_roti",
                        "total_roti_amount",
                        "final_amount"
                    ]
                ]

                summary_df.columns = [
                    "Name",
                    "Tiffin Qty",
                    "Tiffin Amount",
                    "Total Roti",
                    "Roti Amount",
                    "Final Amount"
                ]

                # ======================================================
                # ✅ KEEP RAW COPY FOR CHARTS
                # ======================================================

                summary_df_raw = summary_df.copy()

                # ======================================================
                # ✅ DISPLAY COPY FOR TABLE
                # ======================================================

                display_df = summary_df.copy()

                numeric_cols = [
                    "Tiffin Qty",
                    "Tiffin Amount",
                    "Total Roti",
                    "Roti Amount",
                    "Final Amount"
                ]

                for col in numeric_cols:
                    display_df[col] = display_df[col].apply(
                        lambda x: f"{x:.2f}" if float(x) % 1 else f"{int(x)}"
                    )

                # ======================================================
                # ✅ COLOR MAP
                # ======================================================

                color_map = {
                    "MEET": "#FF0033",
                    "YASH": "#bfff00",
                    "DHRUMIL": "#00bfff",
                    "TOTAL": "#9929EA"
                }


                # ======================================================
                # ✅ SHOW SUMMARY TABLE
                # ======================================================

                st.markdown("### 📝 Summary")

                try:
                    styled_df = style_table(display_df)

                    st.dataframe(
                        styled_df,
                        use_container_width=True
                    )

                except Exception:
                    st.dataframe(
                        display_df,
                        use_container_width=True
                    )

                # ======================================================
                # ✅ PIE CHART
                # ======================================================

                st.markdown("### 📊 Tiffin Orders Distribution")

                pie_data = summary_df_raw[
                    summary_df_raw["Name"] != "TOTAL"
                    ].copy()

                # Convert to numeric
                pie_data["Tiffin Qty"] = pd.to_numeric(
                    pie_data["Tiffin Qty"],
                    errors="coerce"
                )

                # Remove invalid values
                pie_data = pie_data.dropna(subset=["Tiffin Qty"])

                # Keep only positive values
                pie_data = pie_data[
                    pie_data["Tiffin Qty"] > 0
                    ]

                if pie_data.empty:
                    st.info("No data available for pie chart.")
                else:

                    values = pie_data["Tiffin Qty"].astype(float).values

                    pie_colors = [
                        color_map.get(
                            str(name).upper(),
                            "#FFFFFF"
                        )
                        for name in pie_data["Name"]
                    ]

                    fig, ax = plt.subplots(
                        figsize=(6, 6)
                    )

                    ax.pie(
                        values,
                        labels=pie_data["Name"],
                        autopct="%1.1f%%",
                        startangle=90,
                        colors=pie_colors
                    )

                    ax.axis("equal")

                    ax.set_title(
                        "📊 Tiffin Orders by User"
                    )

                    st.pyplot(fig)
    # -------------------- Edit --------------------

    elif menu == "Edit Tiffin Records":

        img_base64 = load_image("images/edit.png")

        st.markdown(

            f"""

            <div style="display: flex; align-items: center; gap: 8px; font-size: 1.25rem;"><img src="data:image/png;base64,{img_base64}" width="30" /><span>Edit Existing Record</span>

            </div>

            """,

            unsafe_allow_html=True

        )

        # --- Fetch records ---

        df = fetch_all_with_loader()
        if df.empty:

            st.info("No records to edit.")


        else:

            df_reset = df.copy()

            # -------------------------

            # Color Functions

            # -------------------------



            styled_df = style_table(df_reset)

            st.dataframe(

                styled_df,

                use_container_width=True

            )

            # -------------------------

            # Select Record

            # -------------------------

            record_options = [

                f"{row['id']} - {row['name']} - {row['date']}"

                for _, row in df_reset.iterrows()

            ]

            selected_record = st.selectbox(

                "Select Record for Edit",

                ["-- Select --"] + record_options

            )

            if selected_record != "-- Select --":

                selected_id = int(

                    selected_record.split(" - ")[0]

                )

                record = (

                    df_reset[df_reset["id"] == selected_id]

                    .iloc[0]

                )

                # Session

                st.session_state["edit_record_id"] = record["id"]

                st.session_state["edit_values"] = record

                values = st.session_state["edit_values"]

                # -------------------------

                # Date

                # -------------------------

                if isinstance(values["date"], str):

                    current_date = datetime.datetime.strptime(

                        values["date"],

                        "%Y-%m-%d"

                    ).date()


                else:

                    current_date = values["date"]

                edit_date = st.date_input(

                    "📅 Edit Date",

                    current_date

                )

                # -------------------------

                # Shift

                # -------------------------

                shift_options = [

                    "DAY",

                    "NIGHT"

                ]

                current_shift = str(

                    values["shift"]

                ).upper()

                shift_index = (

                    shift_options.index(current_shift)

                    if current_shift in shift_options

                    else 0

                )

                edit_shift = st.selectbox(

                    "Shift",

                    shift_options,

                    index=shift_index

                )

                # -------------------------

                # Quantity

                # -------------------------

                edit_qty = st.number_input(

                    "Quantity",

                    min_value=0.0,

                    value=float(values["quantity"])

                )

                # -------------------------

                # Roti

                # -------------------------

                edit_roti = st.number_input(

                    "Roti Quantity",

                    min_value=0,

                    value=int(values["roti"])

                )

                # -------------------------

                # Amount Calculation

                # -------------------------

                roti_amount = edit_roti * 7

                tiffin_amount = round(

                    90 * edit_qty,

                    2

                )

                if edit_shift == "DAY":

                    final_amount = (

                            tiffin_amount + roti_amount

                    )


                else:

                    final_amount = tiffin_amount

                st.info(

                    f"💰 Final Amount: ₹{final_amount}"

                )

                # -------------------------

                # Payment Status

                # -------------------------

                if edit_qty == 0 and edit_roti == 0:

                    default_payment_status = "NOT INVOLVED"


                else:

                    default_payment_status = str(

                        values["payment_status"]

                    ).upper()

                    if default_payment_status == "NOT INVOLVED":
                        default_payment_status = "PAYMENT PENDING"

                payment_options = [

                    "NOT INVOLVED",

                    "PAYMENT PENDING",

                    "PAYMENT DONE"

                ]

                payment_index = (

                    payment_options.index(

                        default_payment_status

                    )

                    if default_payment_status in payment_options

                    else 1

                )

                payment_status = st.selectbox(

                    "Payment Status",

                    payment_options,

                    index=payment_index

                )

                # -------------------------

                # Save

                # -------------------------

                if st.button("Save Changes"):
                    update_record(

                        record_id=int(

                            st.session_state["edit_record_id"]

                        ),

                        date=edit_date,

                        shift=edit_shift,

                        qty=float(edit_qty),

                        roti=int(edit_roti),

                        amount=float(final_amount),

                        roti_amount=float(roti_amount),

                        payment_status=payment_status

                    )

                    st.success(

                        "✅ Record updated successfully!"

                    )

                    st.session_state.pop(

                        "edit_values",

                        None

                    )

                    st.session_state.pop(

                        "edit_record_id",

                        None

                    )

                    st.rerun()

    # -------------------- Payment Method --------------------

    elif menu == "Update Payment Status":

        img_base64 = load_image("images/icons8-payment-history-48.png")

        st.markdown(
            f"""
               <div style="display: flex; align-items: center; gap: 8px; font-size: 1.25rem;">
                   <img src="data:image/png;base64,{img_base64}" width="30" />
                   <span>Update Payment Status</span>
               </div>
               """,
            unsafe_allow_html=True
        )

        # -------------------- LOAD DATA --------------------
        df = fetch_all_with_loader()
        if df.empty:
            st.info("No records available.")

        else:
            # -------------------- CLEAN DATE COLUMN --------------------
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df = df.dropna(subset=["date"])

            if df.empty:
                st.warning("No valid date records found.")
            else:

                min_date = df["date"].min().date()
                max_date = df["date"].max().date()

                # -------------------- UI --------------------
                start_date = st.date_input("Start Date", value=min_date, key="payment_start")
                end_date = st.date_input("End Date", value=max_date, key="payment_end")

                selected_payment = st.selectbox(
                    "Payment Status to Update",
                    ["-- SELECT --", "PAYMENT PENDING", "PAYMENT DONE"]
                )

                # -------------------- ACTION --------------------
                if st.button("Update Payments"):

                    if start_date > end_date:
                        st.error("❎ Start Date cannot be after End Date.")

                    elif selected_payment == "-- SELECT --":
                        st.warning("⚠️ Please select a payment status.")

                    else:
                        # Build selected range
                        date_range = pd.date_range(start=start_date, end=end_date).date

                        # Existing DB dates
                        db_dates = set(df["date"].dt.date)

                        # Find missing dates
                        missing_dates = [d for d in date_range if d not in db_dates]

                        # -------------------- FIXED LOGIC --------------------
                        if missing_dates:
                            pass

                            # OPTIONAL: still update available dates instead of blocking
                            available_dates = [d for d in date_range if d in db_dates]

                            if available_dates:
                                update_payment(
                                    available_dates[0],
                                    available_dates[-1],
                                    selected_payment
                                )
                                st.success(
                                    f"✅ Updated available dates from {available_dates[0]} to {available_dates[-1]}"
                                )
                            else:
                                st.error("❌ No matching dates found to update.")

                        else:
                            # All dates exist → safe update
                            update_payment(start_date, end_date, selected_payment)
                            st.success(
                                f"✅ Payment status updated successfully for {start_date} to {end_date}"
                            )

    # -------------------- Download --------------------



    # --- Streamlit menu ---

    if menu == "Export Data":

        # PNG icon load & display
        img_base64 = load_image("images/icons8-microsoft-excel-2025-48.png")

        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 8px; font-size: 30px;">
                <img src="data:image/png;base64,{img_base64}" width="30" />
                <span>Download Tiffin Excel</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        df = fetch_all_with_loader()
        if df.empty:
            st.info("No records available for download")

        else:

            # ✅ Remove time column
            if "time" in df.columns:
                df = df.drop(columns=["time"])

            df['date'] = pd.to_datetime(df['date'], errors='coerce')

            today = datetime.date.today()

            if today.day >= 10:
                from_default = today.replace(day=10)

                if today.month == 12:
                    to_default = datetime.date(today.year + 1, 1, 9)
                else:
                    to_default = datetime.date(today.year, today.month + 1, 9)

            else:
                to_default = today.replace(day=9)

                if today.month == 1:
                    from_default = datetime.date(today.year - 1, 12, 10)
                else:
                    from_default = datetime.date(today.year, today.month - 1, 10)

            col1, col2 = st.columns(2)

            with col1:
                from_date = st.date_input(
                    "From Date",
                    value=from_default,
                    key="download_from"
                )

            with col2:
                to_date = st.date_input(
                    "To Date",
                    value=to_default,
                    key="download_to"
                )

            if from_date > to_date:
                st.error("❎ Start Date cannot be after End Date.")

            else:

                filtered_df = df[
                    (df['date'] >= pd.to_datetime(from_date)) &
                    (df['date'] <= pd.to_datetime(to_date))
                    ]

                # ✅ Only date show (remove time)
                filtered_df['date'] = pd.to_datetime(filtered_df['date']).dt.strftime('%d-%m-%Y')

                # ✅ Remove extra .00000
                numeric_cols = ["quantity", "amount", "roti", "roti_amount"]

                for col in numeric_cols:
                    if col in filtered_df.columns:
                        filtered_df[col] = filtered_df[col].apply(
                            lambda x: f"{x:.2f}" if float(x) % 1 else f"{int(x)}"
                        )

                # ---------- Color Functions ----------





                # ---------- Streamlit Table Styling ----------


                # ✅ SHOW MAIN TABLE
                st.dataframe(style_table(filtered_df), use_container_width=True)

                # =====================================================
                # ✅ SUMMARY TABLE
                # =====================================================

                summary_df = (
                    filtered_df.groupby("name", as_index=False)
                    .agg(
                        total_tiffin=("quantity", lambda x: pd.to_numeric(x, errors="coerce").sum()),

                        total_roti=("roti", lambda x: pd.to_numeric(x, errors="coerce").sum()),

                        total_roti_amount=("roti_amount", lambda x: pd.to_numeric(x, errors="coerce").sum())
                    )
                )

                # ✅ Proper Tiffin Amount
                summary_df["total_tiffin_amount"] = (
                        pd.to_numeric(summary_df["total_tiffin"], errors="coerce") * 90
                )

                # ✅ Sub Total
                summary_df["sub_total"] = (
                        summary_df["total_tiffin_amount"] +
                        summary_df["total_roti_amount"]
                )

                # =====================================================
                # ✅ COLUMN ORDER FIX
                # =====================================================

                summary_df = summary_df[[
                    "name",
                    "total_tiffin",
                    "total_tiffin_amount",
                    "total_roti",
                    "total_roti_amount",
                    "sub_total"
                ]]

                # =====================================================
                # ✅ TOTAL ROW
                # =====================================================

                total_row = pd.DataFrame({
                    "name": ["TOTAL"],

                    "total_tiffin": [
                        summary_df["total_tiffin"].sum()
                    ],

                    "total_tiffin_amount": [
                        summary_df["total_tiffin_amount"].sum()
                    ],

                    "total_roti": [
                        summary_df["total_roti"].sum()
                    ],

                    "total_roti_amount": [
                        summary_df["total_roti_amount"].sum()
                    ],

                    "sub_total": [
                        summary_df["sub_total"].sum()
                    ]
                })

                summary_df = pd.concat(
                    [summary_df, total_row],
                    ignore_index=True
                )

                # =====================================================
                # ✅ COLUMN NAMES
                # =====================================================

                summary_df.columns = [
                    "Name",
                    "Total Tiffin",
                    "Total Tiffin Amount",
                    "Total Roti",
                    "Total Roti Amount",
                    "Sub Total"
                ]

                # =====================================================
                # ✅ FORMAT SUMMARY NUMBERS
                # =====================================================

                for col in [
                    "Total Tiffin",
                    "Total Tiffin Amount",
                    "Total Roti",
                    "Total Roti Amount",
                    "Sub Total"
                ]:
                    summary_df[col] = summary_df[col].apply(
                        lambda x: f"{x:.2f}" if float(x) % 1 else f"{int(x)}"
                    )

                # =====================================================
                # ✅ SUMMARY STYLE
                # =====================================================

                st.markdown("<br><br>", unsafe_allow_html=True)


                styled_summary = summary_df.style.map(
                    color_name,
                    subset=["Name"]
                )

                st.markdown("## 📊 Summary Table")

                st.dataframe(styled_summary, use_container_width=True)

                st.markdown(f"### Records from {from_date} to {to_date}")

                # =====================================================
                # ✅ EXCEL DOWNLOAD
                # =====================================================

                if not filtered_df.empty:

                    output = BytesIO()

                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:

                        # ✅ Main Data
                        filtered_df.to_excel(writer, index=False, sheet_name="Tiffin Records")

                        workbook = writer.book
                        worksheet = writer.sheets["Tiffin Records"]

                        # ---------- Formats ----------

                        bold_format = workbook.add_format({
                            'bold': True,
                            'border': 1
                        })

                        total_format = workbook.add_format({
                            'bold': True,
                            'font_color': '#9929EA',
                            'border': 1
                        })

                        # ---------- Write Summary Table ----------

                        start_row = len(filtered_df) + 4

                        worksheet.write(start_row, 0, "SUMMARY TABLE", bold_format)

                        # Header
                        for col_num, value in enumerate(summary_df.columns.values):
                            worksheet.write(start_row + 1, col_num, value, bold_format)

                        # Data
                        for row_num, row_data in enumerate(summary_df.values):

                            for col_num, cell_data in enumerate(row_data):

                                if str(row_data[0]).upper() == "TOTAL":
                                    worksheet.write(
                                        start_row + 2 + row_num,
                                        col_num,
                                        cell_data,
                                        total_format
                                    )
                                else:
                                    worksheet.write(
                                        start_row + 2 + row_num,
                                        col_num,
                                        cell_data
                                    )

                        # ---------- Main Table Name Coloring ----------

                        name_col_idx = filtered_df.columns.get_loc("name")

                        for row_num, val in enumerate(filtered_df['name'], start=1):

                            color = get_name_color(val)

                            if color:
                                cell_format = workbook.add_format({
                                    'font_color': color,
                                    'bold': True
                                })

                                worksheet.write(row_num, name_col_idx, val, cell_format)

                        # ---------- Payment Status Coloring ----------

                        payment_col_idx = filtered_df.columns.get_loc("payment_status")

                        for row_num, val in enumerate(filtered_df['payment_status'], start=1):

                            color = get_payment_color(val)

                            if color:
                                cell_format = workbook.add_format({
                                    'font_color': color,
                                    'bold': True

                                })

                                worksheet.write(row_num, payment_col_idx, val, cell_format)

                        # ---------- Shift Coloring ----------

                        if 'shift' in filtered_df.columns:

                            shift_col_idx = filtered_df.columns.get_loc("shift")

                            for row_num, val in enumerate(filtered_df['shift'], start=1):

                                color = get_shift_color(val)

                                if color:
                                    cell_format = workbook.add_format({
                                        'font_color': color,
                                        'bold': True

                                    })

                                    worksheet.write(row_num, shift_col_idx, val, cell_format)

                        # ---------- Day Coloring ----------

                        if 'day' in filtered_df.columns:

                            day_col_idx = filtered_df.columns.get_loc("day")

                            for row_num, val in enumerate(filtered_df['day'], start=1):

                                color = get_day_color(val)

                                if color:
                                    cell_format = workbook.add_format({
                                        'font_color': color,
                                        'bold': True
                                    })

                                    worksheet.write(
                                        row_num,
                                        day_col_idx,
                                        val,
                                        cell_format
                                    )

                        # ✅ Auto column width
                        for i, col in enumerate(filtered_df.columns):
                            column_len = max(
                                filtered_df[col].astype(str).map(len).max(),
                                len(col)
                            ) + 5

                            worksheet.set_column(i, i, column_len)

                    processed_data = output.getvalue()

                    st.download_button(
                        label="⬇️ Download Excel",
                        data=processed_data,
                        file_name=f"I_MANMEET__'s_Tiffin_Records_{from_date}_to_{to_date}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                # -------------------- Delete --------------------

    elif menu == "Add Expense Entry":
        account_page()
    elif menu == "View Expense Records":
        account_records_page()
    elif menu == "Edit Expense Details":
        edit_account_page()
    elif menu == "Settings":
        database_settings_page()


if __name__ == "__main__":
    try:
        app()

    except psycopg2.OperationalError:
        st.error("🔴 Database is currently offline.")

    except FileNotFoundError:
        st.error("📂 Required file is missing.")

    except Exception as e:
        st.error("⚠️ Something went wrong.")
