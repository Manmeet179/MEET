
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
import re
from datetime import date
from dateutil.relativedelta import relativedelta
from streamlit_extras.radial_menu import *
from streamlit_option_menu import option_menu

# App-wide interface translation for the most common controls and headings.
# User-entered data, names and notes are intentionally left unchanged.
_UI_TRANSLATIONS = {
    "ગુજરાતી": {
        "Smart Home":"સ્માર્ટ હોમ", "Add Tiffin Entry":"ટિફિન ઉમેરો", "LogSync":"લોગ સિંક",
        "Tiffin Records":"ટિફિન રેકોર્ડ્સ", "View Records":"રેકોર્ડ જુઓ", "Edit Records":"રેકોર્ડ સંપાદિત કરો",
        "Remove Records":"રેકોર્ડ દૂર કરો", "EXPENSES":"ખર્ચ", "Settlement":"સેટલમેન્ટ",
        "Update Payment Status":"ચુકવણી સ્થિતિ અપડેટ કરો", "Export Data":"ડેટા એક્સપોર્ટ કરો",
        "Settings":"સેટિંગ્સ", "Navigation":"નેવિગેશન", "Recent Activity":"તાજેતરની પ્રવૃત્તિ",
        "Individual Monthly Snapshot":"વ્યક્તિગત માસિક સારાંશ", "Analytics Overview":"વિશ્લેષણ સારાંશ",
        "Monthly Summary":"માસિક સારાંશ", "Tiffin Orders by User":"વપરાશકર્તા મુજબ ટિફિન ઓર્ડર",
        "Date":"તારીખ", "From Date":"શરૂઆતની તારીખ", "To Date":"અંતિમ તારીખ", "Search":"શોધો",
        "Save User":"વપરાશકર્તા સાચવો", "Edit user settings":"વપરાશકર્તા સેટિંગ્સ સંપાદિત કરો",
        "Display name":"દર્શાવવાનું નામ", "Active user":"સક્રિય વપરાશકર્તા", "Language":"ભાષા",
        "Name / accent color":"નામનો રંગ", "Change DP":"DP બદલો", "Save Settings":"સેટિંગ્સ સાચવો",
        "View Tiffin Records":"ટિફિન રેકોર્ડ જુઓ", "Edit Tiffin Records":"ટિફિન રેકોર્ડ સંપાદિત કરો",
        "Remove Tiffin Records":"ટિફિન રેકોર્ડ દૂર કરો", "No records available":"કોઈ રેકોર્ડ ઉપલબ્ધ નથી",
        "Select Record for Edit":"સંપાદન માટે રેકોર્ડ પસંદ કરો", "Confirm Delete":"ડિલીટની પુષ્ટિ કરો",
        "Cancel":"રદ કરો", "Save":"સાચવો", "Submit":"સબમિટ કરો", "Logout":"લૉગઆઉટ",
        "Tiffin Quantity":"ટિફિનની સંખ્યા", "Who ordered today?":"આજે કોને ટિફિન લીધું?",
        "Monthly Summary":"માસિક સારાંશ", "Payment Status":"ચુકવણી સ્થિતિ",
    },
    "Hindi": {
        "Smart Home":"स्मार्ट होम", "Add Tiffin Entry":"टिफिन जोड़ें", "LogSync":"लॉग सिंक",
        "Tiffin Records":"टिफिन रिकॉर्ड", "View Records":"रिकॉर्ड देखें", "Edit Records":"रिकॉर्ड संपादित करें",
        "Remove Records":"रिकॉर्ड हटाएँ", "EXPENSES":"खर्च", "Settlement":"सेटलमेंट",
        "Update Payment Status":"भुगतान स्थिति अपडेट करें", "Export Data":"डेटा एक्सपोर्ट करें",
        "Settings":"सेटिंग्स", "Navigation":"नेविगेशन", "Recent Activity":"हाल की गतिविधि",
        "Individual Monthly Snapshot":"व्यक्तिगत मासिक सारांश", "Analytics Overview":"विश्लेषण सारांश",
        "Monthly Summary":"मासिक सारांश", "Tiffin Orders by User":"उपयोगकर्ता के अनुसार टिफिन ऑर्डर",
        "Date":"तारीख", "From Date":"शुरुआती तारीख", "To Date":"अंतिम तारीख", "Search":"खोजें",
        "Save User":"उपयोगकर्ता सहेजें", "Edit user settings":"उपयोगकर्ता सेटिंग्स संपादित करें",
        "Display name":"प्रदर्शित नाम", "Active user":"सक्रिय उपयोगकर्ता", "Language":"भाषा",
        "Name / accent color":"नाम का रंग", "Change DP":"DP बदलें", "Save Settings":"सेटिंग्स सहेजें",
        "View Tiffin Records":"टिफिन रिकॉर्ड देखें", "Edit Tiffin Records":"टिफिन रिकॉर्ड संपादित करें",
        "Remove Tiffin Records":"टिफिन रिकॉर्ड हटाएँ", "No records available":"कोई रिकॉर्ड उपलब्ध नहीं है",
        "Select Record for Edit":"संपादन के लिए रिकॉर्ड चुनें", "Confirm Delete":"हटाने की पुष्टि करें",
        "Cancel":"रद्द करें", "Save":"सहेजें", "Submit":"जमा करें", "Logout":"लॉगआउट",
        "Tiffin Quantity":"टिफिन की मात्रा", "Who ordered today?":"आज किसने टिफिन लिया?",
        "Payment Status":"भुगतान स्थिति",
    },
}

def _translate_ui_value(value):
    lang = st.session_state.get("_app_language", "English")
    mapping = _UI_TRANSLATIONS.get(lang, {})
    if isinstance(value, str):
        # Replace longer labels first to avoid translating a substring prematurely.
        for src in sorted(mapping, key=len, reverse=True):
            value = value.replace(src, mapping[src])
        return value
    if isinstance(value, list):
        return [_translate_ui_value(v) for v in value]
    if isinstance(value, tuple):
        return tuple(_translate_ui_value(v) for v in value)
    return value

# Wrap visible Streamlit labels once; translation follows the selected app language.
if not st.session_state.get("_ui_translation_wrapped", False):
    for _ui_method_name in ("markdown", "caption", "title", "header", "subheader", "write", "info", "warning", "error", "success", "button", "checkbox", "radio", "selectbox", "text_input", "text_area", "date_input", "number_input", "file_uploader", "form_submit_button", "toggle", "multiselect", "metric", "expander"):
        _original_ui_method = getattr(st, _ui_method_name, None)
        if _original_ui_method is None:
            continue
        def _make_translator(original):
            def _translated_method(*args, **kwargs):
                args = tuple(_translate_ui_value(v) for v in args)
                kwargs = {k: _translate_ui_value(v) for k, v in kwargs.items()}
                return original(*args, **kwargs)
            return _translated_method
        setattr(st, _ui_method_name, _make_translator(_original_ui_method))
    st.session_state["_ui_translation_wrapped"] = True

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
        animation: none;
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
@st.cache_data(ttl=60, show_spinner=False)
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


@st.cache_data(ttl=30, show_spinner=False)
def _load_saved_name_colors():
    """Load per-user colors from persistent settings; fall back safely if unavailable."""
    colors = dict(DEFAULT_NAME_COLORS)
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("SELECT username, accent_color FROM app_user_profiles WHERE active=TRUE")
            for username, color in cur.fetchall():
                if username and color:
                    colors[str(username).upper()] = str(color)
    except Exception:
        pass
    return colors


def get_name_color(value):
    key = str(value).upper()
    try:
        return _load_saved_name_colors().get(key, NAME_COLORS.get(key))
    except Exception:
        return NAME_COLORS.get(key)


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

    names = _active_names()

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

            _nav_original_options = [
                "Smart Home", "Add Tiffin Entry", "LogSync", "Tiffin Records",
                "EXPENSES", "Settlement", "Update Payment Status", "Export Data", "Settings"
            ]
            menu = option_menu(
                menu_title=None,
                options=[_translate_ui_value(label) for label in _nav_original_options],

icons=[
    "house-heart",
    "plus-circle",
    "magic",
    "collection",
    "wallet2",
    "arrow-left-right",
    "credit-card",
    "download",
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
            # Keep internal routing names stable even when the sidebar is translated.
            menu = next((label for label in _nav_original_options if _translate_ui_value(label) == menu), menu)
            # The sidebar is rendered at module level; persist its choice for app() routing.
            st.session_state["active_menu"] = menu

        else:
            menu = None
            st.session_state.pop("active_menu", None)

        if st.session_state.get("logged_in", False):
            st.markdown("---")
            if st.button("↪️ Logout", use_container_width=True, key="premium_logout"):
                smart_logout()
    # --------------------
    # Login Status
    # --------------------
    with st.sidebar:
        # Do not contact PostgreSQL before login. This keeps the login screen fast.
        is_logged = st.session_state.get("logged_in", False)
        db_connected = check_db_connection() if is_logged else None

        # Database Status
        db_status = ("Connected" if db_connected else "Disconnected") if is_logged else "Login required"
        db_color = ("green" if db_connected else "red") if is_logged else "gray"

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

TOKEN = st.secrets["AIVEN_TOKEN"]
PROJECT = st.secrets["AIVEN_PROJECT"]
SERVICE = st.secrets["AIVEN_SERVICE"]

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


@st.cache_data(ttl=300, show_spinner=False)
def get_billing_rates():
    """Return cached global tiffin and roti rates; refresh at most every 5 minutes."""
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS app_settings (
                setting_key TEXT PRIMARY KEY,
                setting_value NUMERIC NOT NULL
            )
        """)
        cur.execute("""
            INSERT INTO app_settings (setting_key, setting_value)
            VALUES (%s, %s)
            ON CONFLICT (setting_key) DO NOTHING
        """, ("tiffin_rate", 90))
        cur.execute("""
            INSERT INTO app_settings (setting_key, setting_value)
            VALUES (%s, %s)
            ON CONFLICT (setting_key) DO NOTHING
        """, ("roti_rate", 7))
        conn.commit()
        cur.execute("""
            SELECT setting_key, setting_value
            FROM app_settings
            WHERE setting_key IN ('tiffin_rate', 'roti_rate')
        """)
        values = {k: float(v) for k, v in cur.fetchall()}
        return values.get("tiffin_rate", 90.0), values.get("roti_rate", 7.0)
    finally:
        cur.close()


def save_billing_rates(tiffin_rate, roti_rate):
    """Persist global billing rates."""
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS app_settings (
                setting_key TEXT PRIMARY KEY,
                setting_value NUMERIC NOT NULL
            )
        """)
        for key, value in (("tiffin_rate", tiffin_rate), ("roti_rate", roti_rate)):
            cur.execute("""
                INSERT INTO app_settings (setting_key, setting_value)
                VALUES (%s, %s)
                ON CONFLICT (setting_key)
                DO UPDATE SET setting_value = EXCLUDED.setting_value
            """, (key, float(value)))
        conn.commit()
        get_billing_rates.clear()
    finally:
        cur.close()


def database_settings_page():
    st.markdown("""
    <h4 style="margin-bottom:0;">
    ⚙️ Settings
    </h4>
    """, unsafe_allow_html=True)

    st.divider()

    # =========================================================
    # GLOBAL BILLING RATES
    # =========================================================

    current_tiffin_rate, current_roti_rate = get_billing_rates()

    st.subheader("💰 Global Billing Rates")

    rate_col1, rate_col2 = st.columns(2)

    with rate_col1:
        new_tiffin_rate = st.number_input(
            "🍱 Tiffin Rate (₹)",
            min_value=0.0,
            value=float(current_tiffin_rate),
            step=1.0,
            key="global_tiffin_rate"
        )

    with rate_col2:
        new_roti_rate = st.number_input(
            "🫓 Roti Rate (₹)",
            min_value=0.0,
            value=float(current_roti_rate),
            step=1.0,
            key="global_roti_rate"
        )

    if st.button("💾 Save Billing Rates", use_container_width=True, key="save_global_billing_rates"):
        if new_tiffin_rate <= 0 or new_roti_rate <= 0:
            st.error("⚠️ Rates must be greater than 0.")
        else:
            save_billing_rates(new_tiffin_rate, new_roti_rate)
            st.success("✅ Global billing rates updated successfully.")
            st.rerun()

    st.caption(
        f"Current rates: Tiffin ₹{current_tiffin_rate:g} • Roti ₹{current_roti_rate:g}. "
        "These rates are used throughout LUNCHLOGIX."
    )

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
    # ON-DEMAND CURRENT STATUS
    # =========================

    if st.button("🔄 Check Database Status", key="check_database_status_now"):
        st.session_state["db_status_snapshot"] = check_aiven_status()

    if "db_status_snapshot" in st.session_state:
        state = st.session_state["db_status_snapshot"]
        if state == "RUNNING":
            st.success("🟢 LUNCHLOGIX Database Control • Running")
        elif state in ["REBUILDING", "POWERING_ON", "BUILDING"]:
            st.warning(f"🟡 LUNCHLOGIX Database Control • {state}")
        else:
            st.error(f"🔴 LUNCHLOGIX Database Control • {state}")
    else:
        st.caption("Database status has not been checked yet. Press the button above to check it.")

    st.caption("LUNCHLOGIX Database Control • MANMEET'S DATABASE")




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

    # Manual-entry user list comes from Settings; newly added active users appear here.
    names = _active_names()
    selected_names = []
    try:
        _profiles_for_avatars = smart_users(True)
        _avatar_map = {str(r["username"]).upper(): r.get("dp_data") for _, r in _profiles_for_avatars.iterrows()}
    except Exception:
        _avatar_map = {}

    # Compact WhatsApp-like avatar + name next to the selection checkbox.
    for start_idx in range(0, len(names), 3):
        row_names = names[start_idx:start_idx + 3]
        cols = st.columns(len(row_names))
        for col, name in zip(cols, row_names):
            with col:
                avatar_col, check_col = st.columns([0.8, 2.2])
                dp_value = _avatar_map.get(name)
                if dp_value:
                    try:
                        avatar_col.image(base64.b64decode(dp_value), width=34)
                    except Exception:
                        avatar_col.markdown("👤")
                else:
                    avatar_col.markdown("👤")
                selected = check_col.checkbox(name, key=f"person_{name}")
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

    tiffin_rate, roti_rate = get_billing_rates()

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
        tiffin_rate * per_person_qty,
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

# =========================================================
# LogSync
# =========================================================

SMART_PERSONS = {
    "D": "DHRUMIL",
    "Y": "YASH",
    "M": "MEET",
}


def _clean_whatsapp_line(line):
    """Remove WhatsApp timestamp/sender prefix but keep the actual message."""
    line = str(line).strip()
    # Example: [23/06, 8:43 pm] 𝐌𝐀𝐍𝐌𝐄𝐄𝐓 ❤‍🔥: D 21/06
    line = re.sub(r"^\s*\[\d{1,2}/\d{1,2},[^\]]+\]\s*[^:]*:\s*", "", line)
    return line.strip()


def smart_split_blocks(raw_text):
    """Split pasted text into D dd/mm blocks, even when multiple fields are on one line.

    Supports both:
      D 03/10\nTotal 1\nM - Y1M1\nN -\nRoti - 14
    and:
      D 03/10 Total 1 M - Y1M1 N - Roti - 14

    WhatsApp timestamp/sender prefixes and unrelated chat are ignored.
    """
    text = str(raw_text or "").replace("\r", "")
    # Remove WhatsApp sender prefixes anywhere they begin a line.
    text = re.sub(r"(?m)^\s*\[\d{1,2}/\d{1,2},[^\]]+\]\s*[^:]*:\s*", "", text)

    # A real block starts wherever D dd/mm occurs at a word boundary.
    matches = list(re.finditer(r"(?i)(?<![A-Za-z0-9])D\s+(\d{1,2})\s*/\s*(\d{1,2})(?!\d)", text))
    blocks = []
    for i, m in enumerate(matches):
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        segment = text[m.end():end_pos].strip()
        blocks.append({
            "day": int(m.group(1)),
            "month": int(m.group(2)),
            "lines": [segment] if segment else [],
        })
    return blocks


def _parse_person_entries(value, fallback_total=None):
    """Parse D1M4Y1, DY3, YDM1, and bare m/d/y forms."""
    text_value = re.sub(r"\s+", "", str(value or "")).upper()
    text_value = re.sub(r"[^DMY0-9.]", "", text_value)
    if not text_value:
        return {}

    # Shared tiffin: DY1 / YD3 / YDM1 / MYD3 etc.
    shared = re.fullmatch(r"([DMY]{2,3})(\d+(?:\.\d+)?)?", text_value)
    if shared and len(set(shared.group(1))) == len(shared.group(1)):
        people = [SMART_PERSONS[c] for c in shared.group(1)]
        qty = float(shared.group(2)) if shared.group(2) else None
        if qty is None:
            qty = float(fallback_total or 1)
        per_person = qty / len(people)
        return {person: per_person for person in people}

    # Separate tiffins: D1M1Y1. Bare single person uses the block total.
    matches = list(re.finditer(r"([DMY])(\d+(?:\.\d+)?)?", text_value))
    if not matches:
        return {}

    result = {}
    for match in matches:
        code = match.group(1)
        qty_text = match.group(2)
        qty = float(qty_text) if qty_text is not None else None
        result[SMART_PERSONS[code]] = result.get(SMART_PERSONS[code], 0.0) + (qty if qty is not None else 0.0)

    # If there is exactly one bare person, Total is its quantity.
    if len(matches) == 1 and matches[0].group(2) is None:
        person = SMART_PERSONS[matches[0].group(1)]
        result[person] = float(fallback_total or 1)

    return result


def _normalise_qty(value):
    value = float(value or 0)
    return int(value) if value.is_integer() else round(value, 2)


def parse_smart_log_block(block, year=None):
    """Parse one D dd/mm block into database-ready rows."""
    year = int(year or datetime.date.today().year)
    day = block["day"]
    month = block["month"]

    try:
        parsed_date = datetime.date(year, month, day)
    except ValueError:
        return None, "Invalid date: %02d/%02d" % (day, month)

    total_tiffin = None
    shift_values = {"DAY": {}, "NIGHT": {}}
    roti_amount_input = 0.0

    # Join lines so a single-line WhatsApp paste works exactly like multiline input.
    content = " ".join(_clean_whatsapp_line(x) for x in block.get("lines", []) if str(x).strip())
    content = re.sub(r"\s+", " ", content).strip()

    total_match = re.search(r"(?i)\bTOTAL\s*(?:-|:)??\s*(\d+(?:\.\d+)?)", content)
    if total_match:
        total_tiffin = float(total_match.group(1))

    # Capture M/N sections until the next M/N/ROTI marker.
    section_matches = list(re.finditer(
        r"(?i)(?:^|\s)(M|N)\s*-\s*(.*?)(?=\s+(?:M|N)\s*-|\s+ROTI\s*-|$)",
        content
    ))
    for sm in section_matches:
        shift = "DAY" if sm.group(1).upper() == "M" else "NIGHT"
        shift_values[shift] = _parse_person_entries(
            sm.group(2), fallback_total=total_tiffin
        )

    roti_match = re.search(r"(?i)\bROTI\s*-\s*(\d+(?:\.\d+)?)", content)
    if roti_match:
        roti_amount_input = float(roti_match.group(1))

    tiffin_rate, roti_rate = get_billing_rates()

    # Roti can be written as quantity OR amount.
    # Example with ₹7 rate:
    #   Roti - 2  -> 2 rotis -> ₹14
    #   Roti - 14 -> ₹14     -> 2 rotis
    #   Roti - 21 -> ₹21     -> 3 rotis
    # Values greater than the rate and exactly divisible by the rate are treated as amount.
    if roti_amount_input <= 0:
        roti_qty = 0
        roti_amount = 0.0
    elif (
        roti_amount_input > roti_rate
        and abs((roti_amount_input / roti_rate) - round(roti_amount_input / roti_rate)) < 1e-9
    ):
        roti_amount = round(roti_amount_input, 2)
        roti_qty = int(round(roti_amount / roti_rate))
    else:
        roti_qty = int(round(roti_amount_input))
        roti_amount = round(roti_qty * roti_rate, 2)

    rows = []
    for shift in ("DAY", "NIGHT"):
        for name, qty in shift_values[shift].items():
            qty = _normalise_qty(qty)
            if qty <= 0:
                continue

            person_roti = 0
            person_roti_amount = 0.0
            if shift == "DAY" and roti_qty > 0:
                # Default roti owner: DHRUMIL if present in Morning, otherwise first Morning person.
                day_people = list(shift_values["DAY"].keys())
                owner = "DHRUMIL" if "DHRUMIL" in day_people else (day_people[0] if day_people else None)
                if name == owner:
                    person_roti = roti_qty
                    person_roti_amount = roti_amount

            rows.append({
                "Date": parsed_date,
                "Day": parsed_date.strftime("%A").upper(),
                "Time": datetime.datetime.now().strftime("%H:%M:%S"),
                "Name": name,
                "Shift": shift,
                "Quantity": qty,
                "Roti": person_roti,
                "Roti_Amount": person_roti_amount,
                "Amount": round(qty * tiffin_rate + person_roti_amount, 2),
                "Payment_Status": "PAYMENT PENDING",
            })

    if not rows:
        return None, "No tiffin/person data found"

    return {
        "date": parsed_date,
        "total": total_tiffin,
        "rows": rows,
        "roti_qty": roti_qty,
        "roti_amount": roti_amount,
        "tiffin_rate": tiffin_rate,
        "roti_rate": roti_rate,
    }, None


def _db_duplicate_keys():
    """Return existing (full date, name, shift) keys from the database."""
    df = fetch_all()
    if df.empty:
        return set()
    result = set()
    for _, row in df.iterrows():
        d = pd.to_datetime(row.get("date"), errors="coerce")
        if pd.isna(d):
            continue
        result.add((d.date(), str(row.get("name", "")).upper(), str(row.get("shift", "")).upper()))
    return result


def smart_log_parser_page():
    st.subheader("🧠 LogSync")
    st.caption("Paste WhatsApp messages. Only blocks beginning with D dd/mm are processed.")

    raw_text = st.text_area(
        "📋 Paste WhatsApp Messages",
        height=300,
        placeholder="Paste your WhatsApp messages here...",
        key="smart_log_text"
    )

    if not raw_text.strip():
        st.info("Paste your WhatsApp log above to start LogSync.")
        return

    # Use current year for dd/mm input. A year selector is provided for duplicate safety.
    parse_year = st.number_input(
        "📅 Year",
        min_value=2000,
        max_value=2100,
        value=datetime.date.today().year,
        step=1,
        key="smart_parser_year"
    )

    blocks = smart_split_blocks(raw_text)
    if not blocks:
        st.warning("⚠️ No valid D dd/mm blocks found. Other WhatsApp messages are ignored.")
        return

    parsed = []
    errors = []
    seen_dates = {}

    for block in blocks:
        result, error = parse_smart_log_block(block, year=parse_year)
        if error:
            errors.append(error)
            continue
        parsed.append(result)

    # Same date inside the pasted text: take neither occurrence.
    valid_after_internal_duplicate = []
    duplicate_pasted_dates = set()
    for item in parsed:
        d = item["date"]
        seen_dates[d] = seen_dates.get(d, 0) + 1
    for d, count in seen_dates.items():
        if count > 1:
            duplicate_pasted_dates.add(d)

    for item in parsed:
        if item["date"] not in duplicate_pasted_dates:
            valid_after_internal_duplicate.append(item)

    if duplicate_pasted_dates:
        for d in sorted(duplicate_pasted_dates):
            st.error(f"❌ Duplicate date in pasted text: {d.strftime('%d/%m/%Y')} — neither entry will be saved.")

    if errors:
        for error in errors:
            st.warning(f"⚠️ {error}")

    if not valid_after_internal_duplicate:
        return

    existing_keys = _db_duplicate_keys()
    preview_rows = []
    save_rows = []

    for item in valid_after_internal_duplicate:
        for row in item["rows"]:
            key = (row["Date"], row["Name"].upper(), row["Shift"].upper())
            if key in existing_keys:
                status = "Already Exists"
            else:
                status = "New"
                save_rows.append(row)
            preview_rows.append({
                # Keep the same column names/structure as View Tiffin Records
                # so the existing Name / Shift / Day colors apply directly.
                "date": row["Date"].strftime("%d/%m/%Y"),
                "day": row["Date"].strftime("%A"),
                "name": row["Name"],
                "shift": row["Shift"],
                "quantity": row["Quantity"],
                "roti": row["Roti"],
                "roti_amount": row["Roti_Amount"],
                "amount": row["Amount"],
                "payment_status": row.get("Payment_Status", "PENDING"),
            })

    st.divider()
    st.subheader("👀 Parsed Preview")

    preview_df = pd.DataFrame(preview_rows)
    if not preview_df.empty:
        # Same table structure, number formatting and colors as View Tiffin Records.
        numeric_cols = ["quantity", "amount", "roti", "roti_amount"]
        for col in numeric_cols:
            if col in preview_df.columns:
                preview_df[col] = preview_df[col].apply(
                    lambda x: f"{float(x):.2f}" if float(x) % 1 else f"{int(float(x))}"
                )

        styled_preview = style_table(preview_df)
        st.dataframe(styled_preview, use_container_width=True, hide_index=True)

    tiffin_rate, roti_rate = get_billing_rates()

    # =========================================================
    # SMART PARSER TOTALS
    # =========================================================
    new_df = pd.DataFrame(save_rows)
    all_df = pd.DataFrame([r for item in valid_after_internal_duplicate for r in item["rows"]])

    if not all_df.empty:
        all_df["Quantity"] = pd.to_numeric(all_df["Quantity"], errors="coerce").fillna(0)
        all_df["Roti"] = pd.to_numeric(all_df["Roti"], errors="coerce").fillna(0)
        all_df["Roti_Amount"] = pd.to_numeric(all_df["Roti_Amount"], errors="coerce").fillna(0)
        all_df["Amount"] = pd.to_numeric(all_df["Amount"], errors="coerce").fillna(0)

        # Tiffin-only subtotal excludes roti amount.
        tiffin_subtotal = round((all_df["Quantity"] * float(tiffin_rate)).sum(), 2)
        roti_qty_total = round(all_df["Roti"].sum(), 2)
        roti_amount_total = round(all_df["Roti_Amount"].sum(), 2)
        grand_total = round(tiffin_subtotal + roti_amount_total, 2)

        st.markdown("### 🧾 Summary Totals")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🍱 Tiffin Sub Total", f"₹{tiffin_subtotal:g}")
        c2.metric("🫓 Roti Qty Total", f"{roti_qty_total:g}")
        c3.metric("🫓 Roti Amt Total", f"₹{roti_amount_total:g}")
        c4.metric("💰 Grand Total", f"₹{grand_total:g}")

        # Separate total for each of the 3 people.
        person_summary = []
        for person in ("DHRUMIL", "YASH", "MEET"):
            p = all_df[all_df["Name"].str.upper() == person]
            qty_total = round(p["Quantity"].sum(), 2) if not p.empty else 0
            roti_qty_person = round(p["Roti"].sum(), 2) if not p.empty else 0
            roti_amt_person = round(p["Roti_Amount"].sum(), 2) if not p.empty else 0
            total_person = round(p["Amount"].sum(), 2) if not p.empty else 0
            tiffin_subtotal_person = round(qty_total * float(tiffin_rate), 2)
            person_summary.append({
                "Name": person,
                "Tiffin Qty": qty_total,
                "Tiffin Sub Total": tiffin_subtotal_person,
                "Roti Qty": roti_qty_person,
                "Roti Amount": roti_amt_person,
                "Total": total_person,
            })

        st.markdown("### 👥 Separate Total — 3 Persons")
        person_df = pd.DataFrame(person_summary)
        person_df["Tiffin Qty"] = person_df["Tiffin Qty"].apply(lambda x: int(x) if float(x).is_integer() else round(x, 2))
        person_df["Tiffin Sub Total"] = person_df["Tiffin Sub Total"].apply(lambda x: f"₹{float(x):g}")
        person_df["Roti Qty"] = person_df["Roti Qty"].apply(lambda x: int(x) if float(x).is_integer() else round(x, 2))
        person_df["Roti Amount"] = person_df["Roti Amount"].apply(lambda x: f"₹{float(x):g}")
        person_df["Total"] = person_df["Total"].apply(lambda x: f"₹{float(x):g}")
        st.dataframe(style_table(person_df), use_container_width=True, hide_index=True)

    st.caption(f"Global rates: Tiffin ₹{tiffin_rate:g} • Roti ₹{roti_rate:g}")

    if save_rows:
        st.info(f"🆕 {len(save_rows)} new record(s) ready to save.")
    else:
        st.success("✅ No new records to save. All parsed records already exist or were duplicates.")

    if st.button(
        "💾 SAVE NEW RECORDS",
        use_container_width=True,
        type="primary",
        disabled=not save_rows,
        key="smart_parser_save"
    ):
        insert_data = []
        for row in save_rows:
            insert_data.append([
                row["Date"], row["Day"], row["Time"], row["Name"], row["Shift"],
                row["Quantity"], row["Roti"], row["Roti_Amount"], row["Amount"], row["Payment_Status"]
            ])
        insert_record(insert_data)
        st.success(f"✅ {len(insert_data)} record(s) saved successfully.")
        st.rerun()



def smart_track_page():
    """
    Compact real-time billing-cycle tracker.
    Billing cycle follows the existing LUNCHLOGIX convention:
    10th of a month through the 9th of the following month.
    """
    df = fetch_all_with_loader()

    st.markdown("""
    <style>
    .smart-head{display:flex;align-items:center;justify-content:space-between;gap:10px;margin:0 0 8px 0}
    .smart-title{font-size:1.45rem;font-weight:900;letter-spacing:.2px;margin:0}
    .smart-sub{font-size:.72rem;opacity:.72;margin-top:1px}
    .st-card{border:1px solid rgba(148,163,184,.18);border-radius:12px;padding:9px 10px;min-height:67px;background:rgba(15,23,42,.42);box-shadow:0 4px 18px rgba(0,0,0,.10)}
    .st-k{font-size:.66rem;opacity:.68;text-transform:uppercase;letter-spacing:.7px}
    .st-v{font-size:1.05rem;font-weight:850;line-height:1.15;margin-top:4px}
    .st-mini{font-size:.65rem;opacity:.65;margin-top:2px}
    .track-wrap{margin:7px 0 10px 0;padding:9px 8px 7px 8px;border-radius:12px;border:1px solid rgba(148,163,184,.18);background:rgba(2,6,23,.28)}
    .track-line{position:relative;height:24px;margin:0 3%}
    .track-base{position:absolute;left:0;right:0;top:11px;height:2px;background:rgba(148,163,184,.28);border-radius:9px}
    .track-progress{position:absolute;left:0;top:11px;height:2px;background:linear-gradient(90deg,#38bdf8,#8b5cf6);border-radius:9px}
    .track-dot{position:absolute;top:5px;width:13px;height:13px;margin-left:-6px;border-radius:50%;background:#0f172a;border:2px solid #94a3b8}
    .track-dot.active{border-color:#38bdf8;background:#38bdf8;box-shadow:0 0 0 4px rgba(56,189,248,.14)}
    .track-dot.end{border-color:#8b5cf6}
    .track-label{display:flex;justify-content:space-between;font-size:.62rem;opacity:.68;margin:2px 3% 0 3%}
    .track-now{text-align:center;font-size:.68rem;font-weight:800;margin-top:5px}
    .smart-section{font-size:.86rem;font-weight:850;margin:8px 0 4px 0}
    .user-chip{display:flex;justify-content:space-between;align-items:center;padding:6px 8px;margin:3px 0;border-radius:8px;background:rgba(148,163,184,.07);border:1px solid rgba(148,163,184,.10);font-size:.72rem}
    .user-chip b{font-size:.76rem}.user-chip span{opacity:.72}.small-note{font-size:.62rem;opacity:.58}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="smart-head">
      <div>
        <div class="smart-title">📍 Smart Track</div>
        <div class="smart-sub">Billing cycle • live progress • user • payment • tiffin analytics</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.info("No tiffin records available for Smart Track.")
        return

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    for col in ["quantity", "roti", "roti_amount", "amount"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["name"] = df["name"].astype(str).str.upper()
    df["payment_status"] = df["payment_status"].astype(str).str.upper()

    today = datetime.date.today()
    if today.day >= 10:
        cycle_start = today.replace(day=10)
        cycle_end = cycle_start + relativedelta(months=1) - relativedelta(days=1)
    else:
        cycle_end = today.replace(day=9)
        cycle_start = cycle_end - relativedelta(months=1) + relativedelta(days=1)

    cycle_df = df[
        (df["date"].dt.date >= cycle_start) &
        (df["date"].dt.date <= cycle_end)
    ].copy()

    total_days = (cycle_end - cycle_start).days + 1
    elapsed_days = max(0, min(total_days, (today - cycle_start).days + 1))
    remaining_days = max(0, total_days - elapsed_days)
    progress = min(100.0, max(0.0, elapsed_days / total_days * 100))

    total_tiffin = cycle_df["quantity"].sum() if not cycle_df.empty else 0
    total_roti = cycle_df["roti"].sum() if not cycle_df.empty else 0
    total_payment = cycle_df["amount"].sum() if not cycle_df.empty else 0

    users = sorted([x for x in cycle_df["name"].dropna().unique().tolist() if x and x != "NAN"])
    user_count = len(users)

    paid_mask = cycle_df["payment_status"].isin(["PAYMENT DONE", "PAID", "DONE"])
    pending_mask = cycle_df["payment_status"].isin(["PAYMENT PENDING", "PENDING"])
    paid_amount = cycle_df.loc[paid_mask, "amount"].sum() if not cycle_df.empty else 0
    pending_amount = cycle_df.loc[pending_mask, "amount"].sum() if not cycle_df.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (c1, "TODAY", today.strftime("%d %b")),
        (c2, "DAYS LEFT", str(remaining_days)),
        (c3, "USERS", str(user_count)),
        (c4, "TOTAL TIFFIN", f"{total_tiffin:g}"),
    ]
    for col, label, value in cards:
        col.markdown(
            f'<div class="st-card"><div class="st-k">{label}</div><div class="st-v">{value}</div></div>',
            unsafe_allow_html=True,
        )

    progress_px = f"{progress:.2f}%"
    st.markdown(
        f"""
        <div class="track-wrap">
          <div class="track-line">
            <div class="track-base"></div>
            <div class="track-progress" style="width:{progress_px};"></div>
            <div class="track-dot active" style="left:0%;"></div>
            <div class="track-dot active" style="left:{progress_px};"></div>
            <div class="track-dot end" style="left:100%;"></div>
          </div>
          <div class="track-label">
            <span>{cycle_start.strftime("%d/%m/%Y")}</span>
            <span>{cycle_end.strftime("%d/%m/%Y")}</span>
          </div>
          <div class="track-now">Day {elapsed_days}/{total_days} • {progress:.0f}% complete • {remaining_days} day(s) remaining</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    p1, p2, p3, p4 = st.columns(4)
    metric_cards = [
        (p1, "MONTH PAYMENT", f"₹{total_payment:,.0f}", "all recorded amount"),
        (p2, "PAID", f"₹{paid_amount:,.0f}", "payment done"),
        (p3, "PENDING", f"₹{pending_amount:,.0f}", "payment pending"),
        (p4, "ROTI", f"{total_roti:g}", "cycle quantity"),
    ]
    for col, label, value, note in metric_cards:
        col.markdown(
            f'<div class="st-card"><div class="st-k">{label}</div><div class="st-v">{value}</div><div class="st-mini">{note}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="smart-section">👥 User Track</div>', unsafe_allow_html=True)
    user_rows = []
    for person in ("MEET", "YASH", "DHRUMIL"):
        p = cycle_df[cycle_df["name"] == person]
        qty = p["quantity"].sum() if not p.empty else 0
        amt = p["amount"].sum() if not p.empty else 0
        pending = p.loc[p["payment_status"].isin(["PAYMENT PENDING", "PENDING"]), "amount"].sum() if not p.empty else 0
        user_rows.append((person, qty, amt, pending))

    if cycle_df.empty:
        st.caption("No records in the current billing cycle.")
    else:
        uc1, uc2, uc3 = st.columns(3)
        for col, (person, qty, amt, pending) in zip((uc1, uc2, uc3), user_rows):
            name_color = get_name_color(person) or "#ffffff"
            col.markdown(
                f'<div class="user-chip"><b style="color:{name_color};">{person}</b><span>{qty:g} tiffin • ₹{amt:,.0f} • ₹{pending:,.0f} pending</span></div>',
                unsafe_allow_html=True,
            )

    st.markdown('<div class="smart-section">📊 Live Analytics</div>', unsafe_allow_html=True)
    chart_left, chart_right = st.columns(2)

    daily = cycle_df.groupby(cycle_df["date"].dt.date)["quantity"].sum() if not cycle_df.empty else pd.Series(dtype=float)
    full_dates = pd.date_range(cycle_start, cycle_end)
    daily = daily.reindex([x.date() for x in full_dates], fill_value=0)

    with chart_left:
        fig, ax = plt.subplots(figsize=(4.2, 2.0))
        ax.plot(range(1, len(daily) + 1), daily.values, marker="o", markersize=2.5, linewidth=1.5)
        ax.axvline(elapsed_days, linestyle="--", linewidth=0.8)
        ax.set_title("Daily Tiffin", fontsize=9, pad=5)
        ax.set_xlabel("Cycle day", fontsize=7)
        ax.set_ylabel("Qty", fontsize=7)
        ax.tick_params(labelsize=6)
        ax.grid(alpha=.18, linewidth=.5)
        fig.tight_layout(pad=.8)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    with chart_right:
        chart_users = [x[0] for x in user_rows]
        chart_qty = [float(x[1]) for x in user_rows]
        fig, ax = plt.subplots(figsize=(4.2, 2.0))
        bars = ax.bar(chart_users, chart_qty)
        ax.set_title("User Tiffin", fontsize=9, pad=5)
        ax.set_ylabel("Qty", fontsize=7)
        ax.tick_params(labelsize=6)
        ax.grid(axis="y", alpha=.18, linewidth=.5)
        ax.bar_label(bars, fmt="%.0f", fontsize=6, padding=2)
        fig.tight_layout(pad=.8)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    with st.expander("📅 Day-wise detail", expanded=False):
        if cycle_df.empty:
            st.caption("No day-wise data.")
        else:
            detail = (
                cycle_df.groupby(cycle_df["date"].dt.date)
                .agg(Tiffin=("quantity", "sum"), Roti=("roti", "sum"), Payment=("amount", "sum"), Users=("name", "nunique"))
                .reset_index()
            )
            detail["Date"] = pd.to_datetime(detail["date"]).dt.strftime("%d/%m")
            detail = detail[["Date", "Tiffin", "Roti", "Payment", "Users"]]
            detail["Tiffin"] = detail["Tiffin"].apply(lambda x: int(x) if float(x).is_integer() else round(float(x), 2))
            detail["Roti"] = detail["Roti"].apply(lambda x: int(x) if float(x).is_integer() else round(float(x), 2))
            detail["Payment"] = detail["Payment"].apply(lambda x: f"₹{float(x):,.0f}")
            st.dataframe(detail, use_container_width=True, hide_index=True)

    st.markdown(
        f'<div class="small-note">Live date: {today.strftime("%d/%m/%Y")} • Cycle: {cycle_start.strftime("%d/%m/%Y")} → {cycle_end.strftime("%d/%m/%Y")} • Updated from current tiffin records.</div>',
        unsafe_allow_html=True,
    )



# =========================================================
# PREMIUM SMART LAYER — preserves existing DB/login flow
# =========================================================

DEFAULT_USERS = ["MEET", "YASH", "DHRUMIL"]
SMART_ACCENT_DEFAULT = "#FF6B35"
DEFAULT_NAME_COLORS = {
    "MEET": "#FF0033",
    "YASH": "#bfff00",
    "DHRUMIL": "#00bfff",
    "TOTAL": "#9929EA",
}

def _ensure_smart_tables():
    # DDL/default inserts are expensive on every Streamlit rerun. Do this once
    # per session, then let normal page reads use lightweight SELECT queries.
    if st.session_state.get("_smart_tables_ready", False):
        return
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS app_user_profiles (
                username TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                active BOOLEAN NOT NULL DEFAULT TRUE,
                language TEXT NOT NULL DEFAULT 'English',
                theme TEXT NOT NULL DEFAULT 'Dark',
                accent_color TEXT NOT NULL DEFAULT '#FF6B35',
                currency TEXT NOT NULL DEFAULT '₹',
                dp_data TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS smart_preferences (
                setting_key TEXT PRIMARY KEY,
                setting_value TEXT NOT NULL
            )
        """)
        for username in DEFAULT_USERS:
            cur.execute("""
                INSERT INTO app_user_profiles (username, display_name, accent_color)
                VALUES (%s, %s, %s)
                ON CONFLICT (username) DO NOTHING
            """, (username, username, DEFAULT_NAME_COLORS[username]))
            # Migrate untouched legacy default colors to the requested user colors.
            cur.execute("""
                UPDATE app_user_profiles
                SET accent_color=%s
                WHERE username=%s AND LOWER(accent_color)=LOWER(%s)
            """, (DEFAULT_NAME_COLORS[username], username, SMART_ACCENT_DEFAULT))
        defaults = {
            "language": "English",
            "theme": "Dark",
            "accent_color": SMART_ACCENT_DEFAULT,
            "currency": "₹",
            "notifications": "true",
            "confirm_delete": "true",
            "compact_cards": "true",
            "auto_refresh": "true",
            "month_start_day": "10",
        }
        for k, v in defaults.items():
            cur.execute("""
                INSERT INTO smart_preferences (setting_key, setting_value)
                VALUES (%s, %s)
                ON CONFLICT (setting_key) DO NOTHING
            """, (k, str(v)))
        conn.commit()
        st.session_state["_smart_tables_ready"] = True
    finally:
        cur.close()

def smart_pref(key, default=None):
    try:
        _ensure_smart_tables()
        cur = get_db().cursor()
        cur.execute("SELECT setting_value FROM smart_preferences WHERE setting_key=%s", (key,))
        row = cur.fetchone()
        cur.close()
        return row[0] if row else default
    except Exception:
        return default

def save_smart_pref(key, value):
    _ensure_smart_tables()
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO smart_preferences(setting_key, setting_value)
            VALUES (%s,%s)
            ON CONFLICT(setting_key) DO UPDATE SET setting_value=EXCLUDED.setting_value
        """, (key, str(value)))
        conn.commit()
    finally:
        cur.close()

def smart_users(active_only=True):
    _ensure_smart_tables()
    q = "SELECT username, display_name, active, language, theme, accent_color, currency, dp_data FROM app_user_profiles"
    if active_only:
        q += " WHERE active=TRUE"
    q += " ORDER BY username"
    return pd.read_sql(q, get_db())

def _active_names():
    try:
        df = smart_users(True)
        names = df["username"].astype(str).str.upper().tolist()
        return names or DEFAULT_USERS.copy()
    except Exception:
        return DEFAULT_USERS.copy()

def _current_cycle():
    today = datetime.date.today()
    if today.day >= 10:
        start = today.replace(day=10)
        end = (today + relativedelta(months=1)).replace(day=9)
    else:
        start = (today - relativedelta(months=1)).replace(day=10)
        end = today.replace(day=9)
    return start, end

def _smart_card(col, label, value, note="", accent=None, avatar_data=None):
    accent = accent or SMART_ACCENT_DEFAULT
    avatar_html = ""
    if avatar_data:
        try:
            avatar_html = f'<img class="snapshot-avatar" src="data:image/png;base64,{avatar_data}" />'
        except Exception:
            avatar_html = ""
    if not avatar_html:
        initials = str(label)[:1].upper()
        avatar_html = f'<span class="snapshot-avatar-fallback">{initials}</span>'
    col.markdown(f"""
    <div class="premium-card" style="--accent:{accent}">
      <div class="snapshot-heading">{avatar_html}<div class="premium-label">{label}</div></div>
      <div class="premium-value">{value}</div>
      <div class="premium-note">{note}</div>
    </div>
    """, unsafe_allow_html=True)

def _expense_groups(df):
    """Build expense events from the existing account_records rows."""
    if df.empty:
        return pd.DataFrame()
    x = df.copy()
    x["date"] = pd.to_datetime(x["date"], errors="coerce")
    x["total_amount"] = pd.to_numeric(x["total_amount"], errors="coerce").fillna(0)
    x["per_person_amount"] = pd.to_numeric(x["per_person_amount"], errors="coerce").fillna(0)
    x["payment_status"] = x["payment_status"].astype(str).str.upper()
    # Existing app writes one row per participant. Group the shared expense.
    group_cols = ["date", "product_name", "place_name", "total_amount"]
    if "time" in x.columns:
        # time is useful where multiple same-day expenses have identical descriptions
        group_cols.append("time")
    rows = []
    for key, g in x.groupby(group_cols, dropna=False):
        payer_rows = g[g["payment_status"].isin(["PAID", "PAYMENT DONE"])]
        payer = str(payer_rows.iloc[0]["name"]) if not payer_rows.empty else ""
        participants = g[g["payment_status"] != "NOT INVOLVED"]["name"].astype(str).tolist()
        share = float(g["per_person_amount"].iloc[0]) if not g.empty else 0
        total = float(g["total_amount"].iloc[0]) if not g.empty else 0
        rows.append({
            "date": g["date"].iloc[0],
            "product_name": str(g["product_name"].iloc[0]),
            "place_name": str(g["place_name"].iloc[0]),
            "total_amount": total,
            "payer": payer,
            "participants": participants,
            "share": share,
        })
    return pd.DataFrame(rows)

def premium_dashboard_page():
    _ensure_smart_tables()
    start, end = _current_cycle()
    tdf = fetch_all_with_loader()
    edf = fetch_account_records_with_loader()
    if not tdf.empty:
        tdf["date"] = pd.to_datetime(tdf["date"], errors="coerce")
        cycle = tdf[(tdf["date"].dt.date >= start) & (tdf["date"].dt.date <= end)].copy()
    else:
        cycle = pd.DataFrame()

    eg = _expense_groups(edf)
    if not eg.empty:
        expenses_cycle = eg[(eg["date"].dt.date >= start) & (eg["date"].dt.date <= end)]
    else:
        expenses_cycle = pd.DataFrame()

    total_tiffin = float(cycle["quantity"].sum()) if not cycle.empty else 0
    tiffin_amount = float(cycle["amount"].sum()) if not cycle.empty else 0
    expense_total = float(expenses_cycle["total_amount"].sum()) if not expenses_cycle.empty else 0
    days = (end - start).days + 1
    elapsed = max(0, min((datetime.date.today() - start).days + 1, days))
    remaining = max(0, days - elapsed)
    progress = (elapsed / days * 100) if days else 0

    st.markdown("""
    <div class="premium-hero">
      <div class="hero-kicker">LUNCHLOGIX • PREMIUM</div>
      <div class="hero-title">Smart Tiffin & Expense</div>
      <div class="hero-sub">Your daily records, monthly billing and settlement — together.</div>
    </div>
    """, unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    _smart_card(c1, "TIFFIN", f"{total_tiffin:g}", "current cycle")
    _smart_card(c2, "TIFFIN BILL", f"₹{tiffin_amount:,.0f}", f"{start:%d %b} → {end:%d %b}")
    _smart_card(c3, "EXPENSES", f"₹{expense_total:,.0f}", "outside / shared")
    _smart_card(c4, "REMAINING", str(remaining), f"days • {progress:.0f}% complete")

    st.markdown(f"""
    <div class="cycle-track">
      <div class="cycle-line"><span style="width:{progress:.2f}%"></span></div>
      <div class="cycle-labels"><b>{start:%d/%m/%Y}</b><b>DAY {elapsed}/{days}</b><b>{end:%d/%m/%Y}</b></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 👥 Individual Monthly Snapshot")
    users = _active_names()
    try:
        profile_df = smart_users(True)
        dp_by_user = {str(r["username"]).upper(): r.get("dp_data") for _, r in profile_df.iterrows()}
    except Exception:
        dp_by_user = {}
    cols = st.columns(max(1, min(3, len(users))))
    for col, name in zip(cols, users):
        p = cycle[cycle["name"].astype(str).str.upper() == name] if not cycle.empty else pd.DataFrame()
        qty = float(p["quantity"].sum()) if not p.empty else 0
        amt = float(p["amount"].sum()) if not p.empty else 0
        dp_value = dp_by_user.get(name)
        _smart_card(col, name, f"{qty:g} tiffin", f"₹{amt:,.0f} tiffin bill", get_name_color(name) or SMART_ACCENT_DEFAULT, dp_value)

    # Combined Analytics Dashboard: summary table and user-wise chart.
    st.markdown("### 📊 Analytics Overview")
    if cycle.empty:
        st.info("No tiffin data in this billing cycle.")
    else:
        tiffin_rate, _ = get_billing_rates()
        analytics_source = cycle.copy()
        analytics_source["name"] = analytics_source["name"].astype(str).str.upper()
        analytics = analytics_source.groupby("name", as_index=False).agg(
            tiffin_qty=("quantity", "sum"),
            total_roti=("roti", "sum"),
            roti_amount=("roti_amount", "sum"),
        )
        analytics["tiffin_amount"] = analytics["tiffin_qty"] * tiffin_rate
        analytics["final_amount"] = analytics["tiffin_amount"] + analytics["roti_amount"]
        total_row = pd.DataFrame([{
            "name": "TOTAL",
            "tiffin_qty": analytics["tiffin_qty"].sum(),
            "tiffin_amount": analytics["tiffin_amount"].sum(),
            "total_roti": analytics["total_roti"].sum(),
            "roti_amount": analytics["roti_amount"].sum(),
            "final_amount": analytics["final_amount"].sum(),
        }])
        table_df = pd.concat([analytics, total_row], ignore_index=True)
        table_df = table_df[["name", "tiffin_qty", "tiffin_amount", "total_roti", "roti_amount", "final_amount"]]
        table_df.columns = ["Name", "Tiffin Qty", "Tiffin Amount", "Total Roti", "Roti Amount", "Final Amount"]
        display_df = table_df.copy()
        for col in ["Tiffin Qty", "Tiffin Amount", "Total Roti", "Roti Amount", "Final Amount"]:
            display_df[col] = pd.to_numeric(display_df[col], errors="coerce").fillna(0).map(
                lambda v: f"{v:.2f}" if float(v) % 1 else f"{int(v)}"
            )
        st.markdown("#### 🧾 Monthly Summary")
        try:
            st.dataframe(style_table(display_df), use_container_width=True, hide_index=True)
        except Exception:
            st.dataframe(display_df, use_container_width=True, hide_index=True)

        pie_data = analytics[analytics["tiffin_qty"] > 0].copy()
        st.markdown("#### 🍱 Tiffin Orders by User")
        if pie_data.empty:
            st.info("No positive tiffin quantities to chart.")
        else:
            pie_colors = [get_name_color(n) or "#8B5CF6" for n in pie_data["name"]]
            fig, ax = plt.subplots(figsize=(5, 3.2))
            ax.pie(
                pie_data["tiffin_qty"].astype(float).values,
                labels=pie_data["name"],
                autopct="%1.1f%%",
                startangle=90,
                colors=pie_colors,
            )
            ax.axis("equal")
            fig.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

    st.markdown("### 🧾 Recent Activity")
    if not tdf.empty:
        # Match the View Records table structure, styling and number formatting.
        recent = tdf.sort_values("date", ascending=False).head(8).copy()
        if "time" in recent.columns:
            recent = recent.drop(columns=["time"])
        if "date" in recent.columns:
            recent["date"] = pd.to_datetime(recent["date"], errors="coerce").dt.strftime("%d/%m/%Y")
        for _col in ["quantity", "amount", "roti", "roti_amount"]:
            if _col in recent.columns:
                recent[_col] = pd.to_numeric(recent[_col], errors="coerce").fillna(0).map(
                    lambda v: f"{v:.2f}" if float(v) % 1 else f"{int(v)}"
                )
        st.dataframe(style_table(recent), use_container_width=True, hide_index=True)

def smart_expense_page():
    _ensure_smart_tables()
    users = _active_names()
    st.markdown("### 💳 Smart Expense")
    st.caption("Enter one shared expense. The app calculates who paid, who owes and the final settlement automatically.")

    c1,c2 = st.columns(2)
    with c1:
        expense_date = st.date_input("Date", datetime.date.today(), key="smart_exp_date")
        product = st.text_input("What was it?", placeholder="Dinner, movie, travel…", key="smart_exp_product")
    with c2:
        place = st.text_input("Place / Note", placeholder="Restaurant / location", key="smart_exp_place")
        total = st.number_input("Total Amount (₹)", min_value=0.0, step=10.0, key="smart_exp_total")

    payer = st.selectbox("Who paid?", users, key="smart_exp_payer")
    participants = st.multiselect("Who was involved?", users, default=users, key="smart_exp_participants")

    if participants and total > 0:
        share = round(total / len(participants), 2)
        st.markdown(f"""
        <div class="expense-preview">
          <b>₹{total:,.2f}</b> total • <b>₹{share:,.2f}</b> each • paid by <b>{payer}</b>
        </div>
        """, unsafe_allow_html=True)

        if st.button("➕ Save Expense", type="primary", use_container_width=True):
            conn = get_db(); cur = conn.cursor()
            try:
                now = datetime.datetime.now().time().replace(microsecond=0)
                for name in users:
                    involved = name in participants
                    status = "PAID" if name == payer and involved else ("PENDING" if involved else "NOT INVOLVED")
                    cur.execute("""
                        INSERT INTO account_records
                        (date, name, product_name, place_name, total_amount, per_person_amount, payment_status)
                        VALUES (%s,%s,%s,%s,%s,%s,%s)
                    """, (expense_date, name, product or "Shared Expense", place or "", total, share if involved else 0, status))
                conn.commit()
                st.success("Expense saved. Settlement has been recalculated.")
                st.rerun()
            except Exception as e:
                conn.rollback()
                st.error(f"Could not save expense: {e}")
            finally:
                cur.close()

def settlement_page():
    _ensure_smart_tables()
    start, end = _current_cycle()
    edf = fetch_account_records_with_loader()
    eg = _expense_groups(edf)
    if not eg.empty:
        eg = eg[(eg["date"].dt.date >= start) & (eg["date"].dt.date <= end)]
    users = _active_names()
    net = {u: 0.0 for u in users}

    for _, e in eg.iterrows() if not eg.empty else []:
        participants = e["participants"]
        share = float(e["share"])
        payer = str(e["payer"]).upper()
        for u in participants:
            u = str(u).upper()
            if u in net:
                net[u] -= share
        if payer in net:
            net[payer] += float(e["total_amount"])

    # Positive = should receive; negative = should pay.
    st.markdown("### 🤝 Month-End Settlement")
    st.caption(f"{start:%d/%m/%Y} → {end:%d/%m/%Y} • Positive balance means money to receive.")

    cols = st.columns(max(1, min(3, len(users))))
    for col, u in zip(cols, users):
        val = round(net.get(u,0),2)
        _smart_card(col, u, f"₹{abs(val):,.2f}", "to receive" if val > 0.005 else ("to pay" if val < -0.005 else "settled"), get_name_color(u) or SMART_ACCENT_DEFAULT)

    creditors = [[u,v] for u,v in net.items() if v > .005]
    debtors = [[u,-v] for u,v in net.items() if v < -.005]
    transfers = []
    i=j=0
    while i < len(debtors) and j < len(creditors):
        amount = round(min(debtors[i][1], creditors[j][1]),2)
        if amount > 0:
            transfers.append((debtors[i][0], creditors[j][0], amount))
        debtors[i][1] -= amount; creditors[j][1] -= amount
        if debtors[i][1] <= .005: i += 1
        if creditors[j][1] <= .005: j += 1

    st.markdown("### 💸 Who Pays Whom")
    if transfers:
        for debtor, creditor, amount in transfers:
            st.markdown(f"""
            <div class="settle-row"><b>{debtor}</b><span>→</span><b>{creditor}</b><strong>₹{amount:,.2f}</strong></div>
            """, unsafe_allow_html=True)
    else:
        st.success("Everyone is settled for this cycle 🎉")

    if not eg.empty:
        st.markdown("### 🧾 Expense History")
        show = eg.copy()
        show["date"] = show["date"].dt.strftime("%d/%m/%Y")
        show["participants"] = show["participants"].apply(lambda x: ", ".join(x))
        show["total_amount"] = show["total_amount"].map(lambda x: f"₹{x:,.2f}")
        show["share"] = show["share"].map(lambda x: f"₹{x:,.2f}")
        st.dataframe(show[["date","product_name","place_name","total_amount","payer","participants","share"]],
                     use_container_width=True, hide_index=True)

def smart_data_page():
    _ensure_smart_tables()
    start, end = _current_cycle()
    tdf = fetch_all_with_loader()
    edf = fetch_account_records_with_loader()
    st.markdown("### 📦 Data Center")
    tab1, tab2 = st.tabs(["🍱 Tiffin Data", "💳 Expense Data"])
    with tab1:
        if not tdf.empty:
            x = tdf.copy()
            x["date"] = pd.to_datetime(x["date"], errors="coerce")
            x = x[(x["date"].dt.date >= start) & (x["date"].dt.date <= end)]
            st.dataframe(x, use_container_width=True, hide_index=True)
            st.download_button("⬇️ Download Tiffin CSV", x.to_csv(index=False).encode("utf-8"),
                               f"tiffin_{start}_{end}.csv", "text/csv", use_container_width=True)
        else: st.info("No tiffin data.")
    with tab2:
        if not edf.empty:
            x = edf.copy()
            x["date"] = pd.to_datetime(x["date"], errors="coerce")
            x = x[(x["date"].dt.date >= start) & (x["date"].dt.date <= end)]
            st.dataframe(x, use_container_width=True, hide_index=True)
            st.download_button("⬇️ Download Expense CSV", x.to_csv(index=False).encode("utf-8"),
                               f"expenses_{start}_{end}.csv", "text/csv", use_container_width=True)
        else: st.info("No expense data.")

def smart_settings_page():
    # Fast path: table creation is guarded per session, and both settings
    # datasets are read through one DB connection. Large DP base64 blobs are
    # deliberately not fetched just to draw the settings list.
    _ensure_smart_tables()
    st.markdown("## ⚙️ Premium Settings")
    st.caption("Fast settings • Tiffin records are entered manually; no automatic tiffin entry runs here.")

    conn = None
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("SELECT username, display_name, active, language, theme, accent_color, currency, dp_data FROM app_user_profiles ORDER BY username")
            profile_rows = cur.fetchall()
            profile_cols = [d[0] for d in cur.description]
            profiles = pd.DataFrame(profile_rows, columns=profile_cols)
            cur.execute("SELECT setting_key, setting_value FROM smart_preferences")
            pref_rows = cur.fetchall()
            prefs = dict(pref_rows)
    except Exception as exc:
        st.error(f"Could not load settings: {exc}")
        return
    finally:
        # get_db may return a pooled/shared connection; don't force-close it here.
        pass

    st.markdown("### 👥 Users")
    st.caption("Select a user's Name / accent color and save it. That color is used across app tables, user cards, and analytics. User deletion removes the profile only; historical records remain.")
    for _, row in profiles.iterrows():
        avatar_col, name_col = st.columns([0.6, 5.4])
        if row.get("dp_data"):
            try:
                avatar_col.image(base64.b64decode(row["dp_data"]), width=42)
            except Exception:
                avatar_col.markdown("<div style='width:42px;height:42px;border-radius:50%;background:#64748b;'></div>", unsafe_allow_html=True)
        else:
            initials = str(row.get("display_name") or row["username"])[:1].upper()
            avatar_col.markdown(f"<div style='width:42px;height:42px;border-radius:50%;background:#64748b;color:white;display:flex;align-items:center;justify-content:center;font-weight:700'>{initials}</div>", unsafe_allow_html=True)
        name_col.markdown(f"**{row['display_name']}**  <small style='color:#94a3b8'>{row['username']}</small>", unsafe_allow_html=True)
        with st.expander("Edit user settings", expanded=False):
            c1, c2 = st.columns(2)
            with c1:
                new_name = st.text_input("Display name", row["display_name"], key=f"sn_{row['username']}")
                active = st.toggle("Active user", bool(row["active"]), key=f"sa_{row['username']}")
                languages = ["English", "ગુજરાતી", "Hindi"]
                language = st.selectbox("Language", languages, index=languages.index(row["language"]) if row["language"] in languages else 0, key=f"sl_{row['username']}")
                themes = ["Dark", "Light", "System"]
                theme = st.selectbox("Theme", themes, index=themes.index(row["theme"]) if row["theme"] in themes else 0, key=f"st_{row['username']}")
            with c2:
                color = st.color_picker("Name / accent color", row["accent_color"] or SMART_ACCENT_DEFAULT, key=f"sc_{row['username']}")
                currencies = ["₹", "$", "€", "£"]
                currency = st.selectbox("Currency", currencies, index=currencies.index(row["currency"]) if row["currency"] in currencies else 0, key=f"su_{row['username']}")
                dp = st.file_uploader("Change DP", type=["png", "jpg", "jpeg"], key=f"dp_{row['username']}")
                if st.button("Save User", key=f"saveu_{row['username']}", type="primary"):
                    conn = get_db()
                    try:
                        with conn.cursor() as cur:
                            if dp is not None:
                                dp_data = base64.b64encode(dp.getvalue()).decode()
                                cur.execute("""UPDATE app_user_profiles SET display_name=%s,active=%s,language=%s,theme=%s,accent_color=%s,currency=%s,dp_data=%s WHERE username=%s""",
                                            (new_name, active, language, theme, color, currency, dp_data, row["username"]))
                            else:
                                cur.execute("""UPDATE app_user_profiles SET display_name=%s,active=%s,language=%s,theme=%s,accent_color=%s,currency=%s WHERE username=%s""",
                                            (new_name, active, language, theme, color, currency, row["username"]))
                        conn.commit()
                    finally:
                        pass
                    _load_saved_name_colors.clear()
                    st.success("User settings saved.")
                    st.rerun()

            delete_key = f"pending_delete_user_{row['username']}"
            if st.button("🗑️ Delete User", key=f"deleteu_{row['username']}", use_container_width=True):
                st.session_state[delete_key] = True

            if st.session_state.get(delete_key, False):
                st.warning(f"Confirm deletion of {row['username']}. This removes the user profile from the database; existing tiffin/expense history will be kept.")
                otp = st.text_input("Enter delete OTP", type="password", key=f"delete_otp_{row['username']}", max_chars=4)
                otp_col1, otp_col2 = st.columns(2)
                with otp_col1:
                    if st.button("Confirm Delete", key=f"confirm_delete_{row['username']}", type="primary", use_container_width=True):
                        if otp == "1795":
                            conn = get_db()
                            try:
                                with conn.cursor() as cur:
                                    cur.execute("DELETE FROM app_user_profiles WHERE username=%s", (row["username"],))
                                conn.commit()
                            finally:
                                pass
                            _load_saved_name_colors.clear()
                            st.session_state.pop(delete_key, None)
                            st.session_state.pop(f"delete_otp_{row['username']}", None)
                            st.success(f"{row['username']} profile deleted from the database.")
                            st.rerun()
                        else:
                            st.error("Incorrect OTP. User was not deleted.")
                with otp_col2:
                    if st.button("Cancel", key=f"cancel_delete_{row['username']}", use_container_width=True):
                        st.session_state.pop(delete_key, None)
                        st.session_state.pop(f"delete_otp_{row['username']}", None)
                        st.rerun()

    st.markdown("### ➕ Add User")
    add_col1, add_col2 = st.columns([2, 1])
    with add_col1:
        new_user = st.text_input("New user name", placeholder="e.g. RAHUL", key="new_smart_user").strip().upper()
    with add_col2:
        st.write("")
        st.write("")
        if st.button("Add User", use_container_width=True, type="primary", key="add_smart_user"):
            if not new_user:
                st.warning("Enter a user name.")
            elif len(new_user) > 40 or not re.match(r"^[A-Z0-9 _-]+$", new_user):
                st.warning("Use only letters, numbers, spaces, _ or -.")
            else:
                conn = get_db()
                try:
                    with conn.cursor() as cur:
                        cur.execute("""INSERT INTO app_user_profiles(username, display_name, accent_color) VALUES (%s,%s,%s) ON CONFLICT(username) DO UPDATE SET active=TRUE""", (new_user, new_user, "#8B5CF6"))
                    conn.commit()
                finally:
                    pass
                _load_saved_name_colors.clear()
                st.success(f"{new_user} added.")
                st.rerun()

    st.markdown("### 🧩 App Controls")
    pref_controls = [
        ("notifications", "Notifications"),
        ("confirm_delete", "Confirm before delete"),
        ("compact_cards", "Compact premium cards"),
        ("auto_refresh", "Auto refresh data"),
        ("animation_theme", "Sunset animation theme"),
        ("show_balance", "Show balance on dashboard"),
        ("show_tiffin_amount", "Show tiffin amount"),
        ("show_expense_amount", "Show expense amount"),
        ("show_month_progress", "Show month progress"),
        ("compact_tables", "Compact tables"),
        ("csv_export_enabled", "CSV export enabled"),
    ]
    pending = {}
    with st.form("fast_settings_form"):
        cols = st.columns(2)
        for n, (key, label) in enumerate(pref_controls):
            with cols[n % 2]:
                pending[key] = st.toggle(label, value=str(prefs.get(key, "true")).lower() == "true", key=f"fast_pref_{key}")
        c1, c2 = st.columns(2)
        with c1:
            app_langs = ["English", "ગુજરાતી", "Hindi"]
            current_lang = prefs.get("language", "English")
            pending["language"] = st.selectbox("App language", app_langs, index=app_langs.index(current_lang) if current_lang in app_langs else 0, key="fast_app_language")
        save_settings = st.form_submit_button("💾 Save Settings", type="primary", use_container_width=True)

    if save_settings:
        conn = get_db()
        try:
            with conn.cursor() as cur:
                for key, value in pending.items():
                    cur.execute("""INSERT INTO smart_preferences(setting_key,setting_value) VALUES (%s,%s) ON CONFLICT(setting_key) DO UPDATE SET setting_value=EXCLUDED.setting_value""", (key, str(value).lower() if isinstance(value, bool) else str(value)))
            conn.commit()
        finally:
            pass
        st.session_state["_app_language"] = pending.get("language", "English")
        st.success("Settings saved.")
        st.rerun()


def smart_logout():
    st.session_state["logged_in"] = False
    for k in ["menu","tiffin_saved_signature"]:
        st.session_state.pop(k, None)
    st.rerun()



st.markdown("""
<style>
.premium-hero{padding:24px;border-radius:24px;background:linear-gradient(135deg,rgba(255,107,53,.22),rgba(139,92,246,.18));border:1px solid rgba(255,255,255,.12);box-shadow:0 18px 50px rgba(0,0,0,.18);margin-bottom:18px}
.hero-kicker{font-size:11px;letter-spacing:2px;font-weight:800;opacity:.7}.hero-title{font-size:30px;font-weight:900;margin-top:5px}.hero-sub{opacity:.72;margin-top:4px}
.premium-card{border:1px solid rgba(255,255,255,.10);border-left:3px solid var(--accent);border-radius:18px;padding:14px 15px;min-height:94px;background:rgba(10,15,28,.62);box-shadow:0 10px 28px rgba(0,0,0,.12);margin-bottom:12px}
.snapshot-heading{display:flex;align-items:center;gap:9px;margin-bottom:8px}.snapshot-avatar{width:30px;height:30px;object-fit:cover;border-radius:50%;flex:0 0 30px;border:1px solid rgba(255,255,255,.25)}.snapshot-avatar-fallback{width:30px;height:30px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;flex:0 0 30px;background:rgba(255,255,255,.15);font-size:13px;font-weight:800}.premium-label{font-size:10px;letter-spacing:1.2px;font-weight:800;opacity:.6}.premium-value{font-size:23px;font-weight:900;margin-top:4px}.premium-note{font-size:11px;opacity:.62;margin-top:2px}
.cycle-track{padding:12px 4px 18px}.cycle-line{height:7px;border-radius:99px;background:rgba(255,255,255,.10);overflow:hidden}.cycle-line span{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,#FF6B35,#8B5CF6)}.cycle-labels{display:flex;justify-content:space-between;font-size:10px;opacity:.65;margin-top:6px}
.expense-preview{padding:16px;border-radius:16px;background:rgba(255,107,53,.10);border:1px solid rgba(255,107,53,.28);margin:12px 0}
.settle-row{display:grid;grid-template-columns:1fr auto 1fr auto;gap:12px;align-items:center;padding:14px 16px;margin:7px 0;border-radius:15px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08)}
</style>
""", unsafe_allow_html=True)

def app():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        login()
        return

    if "_app_language" not in st.session_state:
        try:
            _lang_conn = get_db()
            with _lang_conn.cursor() as _lang_cur:
                _lang_cur.execute("SELECT setting_value FROM smart_preferences WHERE setting_key='language'")
                _lang_row = _lang_cur.fetchone()
            st.session_state["_app_language"] = _lang_row[0] if _lang_row and _lang_row[0] in ("English", "ગુજરાતી", "Hindi") else "English"
        except Exception:
            st.session_state["_app_language"] = "English"

    # Persisted background animation preference: OFF means a plain black background.
    try:
        _theme_conn = get_db()
        with _theme_conn.cursor() as _theme_cur:
            _theme_cur.execute("SELECT setting_value FROM smart_preferences WHERE setting_key='animation_theme'")
            _theme_row = _theme_cur.fetchone()
        _animation_enabled = str(_theme_row[0]).lower() == "true" if _theme_row else True
    except Exception:
        _animation_enabled = True
    if not _animation_enabled:
        st.markdown("""<style>
        html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] > .main,
        [data-testid="stHeader"], [data-testid="stToolbar"] {background:#000000 !important;background-image:none !important;}
        [data-testid="stAppViewContainer"]::before,[data-testid="stAppViewContainer"]::after,
        [data-testid="stApp"]::before,[data-testid="stApp"]::after,
        .sun,.moon,.stars,.clouds,.cloud1,.cloud2,.cloud3,.cloud4,.cloud5,.cloud6,
        .sunset,.sunrise,.sunset-animation,.background-animation,.animated-background,
        [class*="sun"],[class*="moon"],[class*="star"],[class*="cloud"],[class*="sky"] {
            display:none !important; visibility:hidden !important; opacity:0 !important;
            animation:none !important; transition:none !important; background-image:none !important;
        }
        [data-testid="stAppViewContainer"] * {background-image:none !important;}
        </style>""", unsafe_allow_html=True)

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

    # Load billing rates once per app run so every page can safely use them.
    tiffin_rate, roti_rate = get_billing_rates()

    # Sidebar navigation is created outside app(); read its selected item from session state.
    menu = st.session_state.get("active_menu", "Smart Home")

    # Keep view/edit/delete workflows together under one Tiffin Records page.
    if menu == "Tiffin Records":
        tiffin_action = st.radio(
            "Tiffin records action",
            ["View Records", "Edit Records", "Remove Records"],
            horizontal=True,
            key="unified_tiffin_action",
        )
        menu = {
            "View Records": "View Tiffin Records",
            "Edit Records": "Edit Tiffin Records",
            "Remove Records": "Remove Tiffin Records",
        }[tiffin_action]

    if menu == "Smart Home":
        premium_dashboard_page()

    elif menu == "EXPENSES":
        st.markdown("## 💳 EXPENSES")
        st.caption("Manage expenses manually. Nothing is saved, edited, or deleted unless you choose the relevant action.")
        expense_section = st.radio(
            "Expense section",
            ["Smart Expenses", "Edit Expenses", "Remove Expense"],
            horizontal=True,
            key="expenses_subpage",
            label_visibility="collapsed",
        )
        if expense_section == "Edit Expenses":
            edit_account_page()
        elif expense_section == "Remove Expense":
            delete_account_page()
        elif expense_section == "Smart Expenses":
            smart_expense_page()

    elif menu == "Settlement":
        settlement_page()

    elif menu == "Remove Tiffin Records":
        delete_tiffin_page()

    # -------------------- Add Record --------------------
    elif menu == "Add Tiffin Entry":
        add_tiffin_page()

    elif menu == "LogSync":
        smart_log_parser_page()

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

                tiffin_rate, roti_rate = get_billing_rates()
                roti_amount = edit_roti * roti_rate

                tiffin_amount = round(

                    tiffin_rate * edit_qty,

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
                        pd.to_numeric(summary_df["total_tiffin"], errors="coerce") * tiffin_rate
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

    elif menu == "Settings":
        smart_settings_page()
        st.divider()
        if st.button("🛠️ Open Advanced Database Control", key="open_advanced_db_control", use_container_width=True):
            st.session_state["show_advanced_db_control"] = not st.session_state.get("show_advanced_db_control", False)
        if st.session_state.get("show_advanced_db_control", False):
            st.caption("Advanced controls load only when opened. Database status is checked only when requested or during a start/stop operation.")
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
