import streamlit as st
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import bcrypt
import psycopg2
from io import BytesIO
import base64
import time
from datetime import date
from dateutil.relativedelta import relativedelta
from streamlit_extras.radial_menu import *
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
    div.stButton > button {
        background-color: red !important;
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 0.6em 1em;
        font-weight: bold;
    }

    div.stButton > button:hover {
        background-color: darkred !important;
        color: white !important;
    }

    div.stDownloadButton > button {
        background-color: red !important;
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 0.6em 1em;
        font-weight: bold;
    }
    div.stDownloadButton > button:hover {
        background-color: darkred !important;
        color: white !important;
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
@st.cache_data(ttl=0.5)
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


# ==========================
# GET DATABASE CONNECTION
# ==========================
try:
    conn = get_db()

except (
    psycopg2.InterfaceError,
    psycopg2.OperationalError,
    psycopg2.DatabaseError,
):
    get_db.clear()

    st.error("🔴 Database is currently offline.")
    st.warning("Please wait a few moments and try again.")
    st.stop()

except Exception:
    st.error("❌ Unable to connect to the database.")
    st.stop()

@st.cache_data
def load_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()
@st.cache_data(ttl=30)
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
@st.cache_resource
def insert_record(data):
    conn = get_db()
    cursor = conn.cursor()

    for row in data:
        cursor.execute(f"""

            INSERT INTO {TABLE_NAME} (Date, Day, Time, Name, Shift, Quantity, Roti, Roti_Amount, Amount, Payment_Status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, row)

    conn.commit()
    cursor.close()
    fetch_all.clear()
@st.cache_resource
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
@st.cache_resource
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
    df = fetch_all()
    if df.empty:
        st.info("No Tiffin records available to delete.")
        return

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    names = df['name'].unique().tolist()

    option = st.radio("Delete by:", ["Date Range", "Name"], index=0)

    conn = get_db()
    cursor = conn.cursor()

    if option == "Date Range":
        from_date = st.date_input("From Date", value=min_date, min_value=min_date, max_value=max_date)
        to_date = st.date_input("To Date", value=max_date, min_value=min_date, max_value=max_date)

        if st.button("Delete Tiffin Records by Date"):
            if from_date > to_date:
                st.error("❎ Start Date cannot be after End Date.")
            else:
                cursor.execute("""
                    DELETE FROM tiffin
                    WHERE date BETWEEN %s AND %s
                """, (from_date, to_date))
                deleted_count = cursor.rowcount
                conn.commit()
                st.success(f"✅ Deleted {deleted_count} Tiffin record(s) from {from_date} to {to_date}.")

    else:  # Delete by Name
        selected_name = st.selectbox("Select Name", ["-- SELECT --"] + names)
        if st.button("Delete Tiffin Records by Name"):
            if selected_name == "-- SELECT --":
                st.warning("⚠️ Please select a name.")
            else:
                cursor.execute("""
                    DELETE FROM tiffin
                    WHERE name = %s
                """, (selected_name,))
                deleted_count = cursor.rowcount
                conn.commit()
                st.success(f"✅ Deleted {deleted_count} Tiffin record(s) for {selected_name}.")

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
    conn = get_db()
    df = pd.read_sql("SELECT * FROM account_records ORDER BY date DESC, time DESC", conn)
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
            st.rerun()   # 🔥 IMPORTANT FIX
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
    conn = get_db()

    df = pd.read_sql(
        "SELECT * FROM account_records ORDER BY date DESC, time DESC",
        conn
    )

    df = df.drop(columns=["time"], errors="ignore")

    df["payment_status"] = df["payment_status"].astype(str).str.upper()

    if df.empty:

        st.info("No account records available.")

    else:

        # --- Name wise color ---

        def color_name(val):

            colors = {
                "MEET": "#FF0033",
                "YASH": "#bfff00",
                "DHRUMIL": "#00bfff"
            }
            if str(val).upper() in colors:
                return f"color: {colors[str(val).upper()]}; font-weight: bold;"

            return ""

        # --- Payment Status wise color ---

        def color_payment(val):
            if str(val).lower() == "payment done":
                return "color: #83FFE6; font-weight:bold"
            elif str(val).lower() == "pending":
                return "color: #C768FF; font-weight:bold"
            elif str(val).lower() == "paid":
                return "color: #0046FF; font-weight:bold"
            return ""

        # --- Apply both styles ---

        styled_df = (
            df.style
            .format(precision=0)
            .map(color_name, subset=["name"])
            .map(color_payment, subset=["payment_status"])
        )

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
    conn = get_db()  # Replace with your DB connection
    df = pd.read_sql("SELECT * FROM account_records ORDER BY date DESC, time DESC", conn)

    if df.empty:
        st.info("No account records available.")
        st.stop()

    # --- Color functions ---
    def color_name(val):
        colors = {"MEET": "#FF0033", "YASH": "#bfff00", "DHRUMIL": "#00bfff"}
        return f"color: {colors[val.upper()]}; font-weight: bold;" if str(val).upper() in colors else ""

    def color_payment(val):
        val_lower = str(val).lower()
        if val_lower == "payment done":
            return "color: #059212; font-weight:bold;"  # greenish
        elif val_lower in ["pending", "payment pending"]:
            return "color: #76153C; font-weight:bold;"  # pink/purple
        elif val_lower == "paid":
            return "color: goldenrod; font-weight:bold;"
        elif val_lower == "not involved":
            return "color: #FCDC2A; font-weight:bold;"  # neutral yellow-green
        return ""

    # --- Show all records on top with color ---
    styled_df = df.style.map(color_name, subset=["name"]).map(color_payment, subset=["payment_status"])
    st.dataframe(styled_df)

    # --- Single selectbox with all Name-Date-Place combinations ---
    record_options = [f"{row['name']} - {row['date']} - {row['place_name']}" for _, row in df.iterrows()]
    selected_record = st.selectbox("Select Record to Edit", ["-- TYPE OR  SELECT --"] + record_options)

    # --- Stop if no selection ---
    if selected_record == "-- TYPE OR  SELECT --":
        st.warning("⚠️ Please select a record to edit.")
        st.stop()

    # --- Extract record based on selection ---
    name, date_str, place = selected_record.split(" - ")
    date_obj = pd.to_datetime(date_str).date()
    filtered_df = df[
        (df['name'] == name) &
        (pd.to_datetime(df['date']).dt.date == date_obj) &
        (df['place_name'] == place)
    ]

    if filtered_df.empty:
        st.warning("⚠️ Selected record not found!")
        st.stop()

    # --- Show filtered record ---
    st.dataframe(filtered_df)

    # --- Editable inputs ---
    record = filtered_df.iloc[0]
    st.write("### ✏️ Edit Selected Record")
    edit_product = st.text_input("Product Name", str(record['product_name']))
    edit_place = st.text_input("Place Name", str(record['place_name']))
    edit_total = st.number_input("Total Amount", value=float(record['total_amount']))
    edit_per_person = st.number_input("Per Person Amount", value=float(record['per_person_amount']))
    payment_options = ["Pending", "Payment Done", "Paid"]
    edit_payment = st.selectbox(
        "Payment Status",
        payment_options,
        index=payment_options.index(str(record['payment_status']))
    )

    # --- Save changes button ---
    if st.button("Save Changes"):
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE account_records
            SET product_name=%s,
                place_name=%s,
                total_amount=%s,
                per_person_amount=%s,
                payment_status=%s
            WHERE id = %s
        """, (
            str(edit_product),
            str(edit_place),
            float(edit_total),
            float(edit_per_person),
            str(edit_payment),
            int(record['id'])
        ))
        conn.commit()
        cursor.close()
        st.success("✅ Record updated successfully!")
        fetch_all.clear()
st.sidebar.image("images/me.png", use_container_width=True)
st.markdown("""
  <style>

  /* MAIN APP */
  .stApp{
  background:
  linear-gradient(
  180deg,
  #00C1D0 0%,
  #c98d47 40%,
  #0a1144 100%
  );

  color:white;
  }

  /* Containers */
  [data-testid="stVerticalBlock"]{
  border-radius:20px;
  }

  /* Inputs */

  .stSelectbox,
  .stDateInput,
  .stNumberInput{
  background:rgba(255,255,255,.03);
  border-radius:18px;
  }

  /* Buttons */

  .stButton button{

  background:
  linear-gradient(
  90deg,
  #2563EB,
  #7C3AED
  );

  color:white;

  border:none;

  border-radius:16px;

  font-weight:700;

  height:50px;
  }

  /* Dataframe */

  [data-testid="stDataFrame"]{

  background:
  rgba(255,255,255,.03);

  border-radius:20px;

  }

  </style>
  """, unsafe_allow_html=True)
st.markdown("""
  <style>

  /* Sidebar bg color */

  [data-testid="stSidebar"]{
  background:
  linear-gradient(
  180deg,
  #020617,
  #050B1C,
  #17068E
  );

  border-right:
  1px solid rgba(130,80,255,.4);
  }

  /* Hide default */

  [data-testid="stSidebarNav"]{
  display:none;
  }

  /* Logo */

  .logo{
  padding:25px;
  margin-bottom:15px;

  border-radius:24px;

  background:
  linear-gradient(
  135deg,
  rgba(10,20,50,.95),
  rgba(80,20,140,.25)
  );

  text-align:center;

  border:
  1px solid rgba(120,120,255,.4);

  backdrop-filter:blur(20px);

  box-shadow:
  0 0 35px rgba(70,70,255,.3);
  }

  .logoicon{
  font-size:70px;
  }

  .logotitle{

  font-size:42px;

  font-weight:900;

  background:
  linear-gradient(
  90deg,
  #1DA1FF,
  #A855F7
  );

  -webkit-background-clip:text;

  color:transparent;
  }

  .subtitle{
  color:#ddd;
  font-size:15px;
  }

  /* Cards */

  .card{

  padding:15px;

  margin-bottom:12px;

  border-radius:18px;

  background:
  rgba(255,255,255,.03);

  border:
  1px solid rgba(255,255,255,.08);

  color:white;

  box-shadow:
  0 0 18px rgba(0,0,0,.25);
  }

  .green{
  color: #39FF14;
  }

  .red{
  color: #FF073A;
  }

  .version{

  padding:18px;

  border-radius:18px;

  text-align:center;

  margin-top:20px;

  background:
  linear-gradient(
  90deg,
  #1D4ED8,
  #7E22CE
  );

  color:white;

  font-size:36px;

  font-weight:900;

  box-shadow:
  0 0 30px rgba(130,80,255,.4);

  }

  .ver{
  font-size:18px;
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
      🍱
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

    menu = None

    with st.sidebar:
        # ONLY AFTER LOGIN
        if st.session_state.get("logged_in", False):

            st.markdown("""
              <div style="
              font-size:22px;
              font-weight:800;
              color:#ffffff;
              margin-bottom:10px;
              ">
              📌 NAVIGATION
              </div>
              """, unsafe_allow_html=True)

            menu = st.selectbox(
                "",
                [
                    "➕ Add Tiffin Entry",
                    "🔎 View Tiffin Records",
                    "🗃️ Analytics Dashboard",
                    "💳 Update Payment Status",
                    "⬇️ Export Data",
                    "❎ Remove Tiffin Records",
                    "🛠️ Edit Tiffin Records",
                    "💳 Add Expense Entry",
                    "🔍 View Expense Records",
                    "❎ Remove Expense Records",
                    "✏️ Edit Expense Details",
                ],
                label_visibility="collapsed"
            )

            st.divider()


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

    if menu == "❎ Remove Tiffin Records":
        delete_tiffin_page()

    elif menu == "❎ Remove Expense Records":
        delete_account_page()

    # -------------------- Add Record --------------------

    elif menu == "➕ Add Tiffin Entry":

        img_base64 = load_image("images/add.png")

        # Display icon + text side by side
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 8px; font-size: 1.25rem;">
                <img src="data:image/png;base64,{img_base64}" width="30" />
                <span>Add New Record</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        current_time = datetime.datetime.now().strftime("%H:%M:%S")

        shift = st.selectbox("Select Shift", ["-- SELECT DAY --", "DAY", "NIGHT"])

        if shift == "-- SELECT DAY --":
            st.warning("Please select a shift")
            st.stop()

        # ⬇️ Add this to let user pick a date
        selected_date = st.date_input("📅 Select Date", datetime.date.today())

        tiffin_qty = st.selectbox("Select Tiffin Quantity", ["-- SELECT Quantity --"] + [1, 2, 3, 4, 5, 6])

        if tiffin_qty == "-- SELECT Quantity --":
            st.warning("Please select tiffin quantity")
            st.stop()

        st.markdown("### Select Name(s)")
        names = ["MEET", "YASH", "DHRUMIL"]
        cols = st.columns(len(names))
        selected_names = []
        for i, name in enumerate(names):
            if cols[i].checkbox(name):
                selected_names.append(name)
        if not selected_names:
            st.warning("Please select at least one name")

            st.stop()
        roti_qty = {}
        roti_rate = 7
        if shift == "DAY":
            st.markdown("### Enter Roti Quantity per Person")
            for name in selected_names:
                roti_qty[name] = st.number_input(f"{name} Roti Quantity", min_value=0, value=0, step=1)
        else:
            for name in selected_names:
                roti_qty[name] = 0

        per_person_qty = round(float(tiffin_qty) / len(selected_names), 2)
        per_person_amount = round(90 * per_person_qty, 2)
        st.markdown("### Tiffin Amount per Person")

        name_colors = {
            "MEET": "#FF0033",
            "YASH": "#bfff00",
            "DHRUMIL": "#00bfff"
        }

        for name in names:
            color = name_colors.get(name, "#000000")  # Default Black

            if name in selected_names:
                person_roti_qty = roti_qty.get(name, 0)
                person_roti_amount = person_roti_qty * roti_rate
                person_total = per_person_amount + person_roti_amount
                st.markdown("---")

                st.markdown(
                    f"""
                    <span style='color:{color}; font-size:20px; font-weight:bold;'>
                        {name}
                    </span>

                    - Tiffin Quantity: {per_person_qty:.2f}
                    - Tiffin Charges: ₹{per_person_amount:.2f}
                    - Roti: {person_roti_qty} Nos (₹{person_roti_amount:.2f})
                    - **Total Payable: ₹{person_total:.2f}**
                    """,
                    unsafe_allow_html=True

                )

            else:
                st.markdown("---")
                st.markdown(
                    f"""
                    <span style='color:{color}; font-weight:700; font-size:18px;'>
                        {name}
                    </span>
                    — <span style='color:red; font-weight:700;'>
                        No Tiffin Ordered Today
                    </span>
                    """,
                    unsafe_allow_html=True
                )

        # Billing Summary
        total_tiffin_amount = round(
            per_person_amount * len(selected_names), 2
        )

        total_roti_amount = round(
            sum(roti_qty.get(name, 0) * roti_rate for name in selected_names),
            2
        )

        total_amount = total_tiffin_amount + total_roti_amount

        st.markdown("---")
        st.markdown("### Billing Summary")

        st.markdown(
            f"**Total Tiffin Charges:** ₹{total_tiffin_amount:,.2f}"
        )

        if shift == "DAY":
            st.markdown(
                f"**Total Roti Charges:** ₹{total_roti_amount:,.2f}"
            )

        st.markdown("---")

        st.markdown(
            f"""
            <h3>
                Total Amount Payable:
                <span style='color:#39FF14;'>
                    ₹{total_amount:,.2f}
                </span>
            </h3>
            """,
            unsafe_allow_html=True
        )

        if st.button("Save Record"):
            data_to_insert = []

            for name in selected_names:  # ✅ only selected लोग
                qty = per_person_qty
                amount = per_person_amount
                payment_status = "PAYMENT PENDING"

                roti = roti_qty.get(name, 0)
                roti_amount = roti * roti_rate
                total_individual_amount = round(amount + roti_amount, 2)
                day = selected_date.strftime("%A").upper()

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

                data_to_insert.append(row)

            insert_record(data_to_insert)
            st.success("Record(s) added successfully!")

    # -------------------- Records --------------------

    elif menu == "🔎 View Tiffin Records":

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

        df = fetch_all()

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

            def color_shift(val):
                val_lower = str(val).lower()

                if val_lower == "day":
                    return "color: #FF8F00; font-weight:bold;"
                elif val_lower == "night":
                    return "color: #3B9797; font-weight:bold;"
                return ""

            def color_payment(val):
                val_lower = str(val).lower()

                if val_lower == "payment done":
                    return "color: #73FF00; font-weight:bold;"
                elif val_lower in ["pending", "payment pending"]:
                    return "color: #FF0095; font-weight:bold;"
                elif val_lower == "paid":
                    return "color: goldenrod; font-weight:bold;"
                elif val_lower == "not involved":
                    return "color: #FCDC2A; font-weight:bold;"
                return ""

            def color_name(val):
                colors = {
                    "MEET": "#FF0033",
                    "YASH": "#bfff00",
                    "DHRUMIL": "#00bfff"
                }

                return (
                    f"color: {colors.get(val.upper())}; font-weight: bold;"
                    if str(val).upper() in colors
                    else ""
                )

            def color_day(val):
                colors = {
                    "MONDAY": "#BF00FF",
                    "TUESDAY": "#0000FF",
                    "WEDNESDAY": "#7DF9FF",
                    "THURSDAY": "#72FF13",
                    "FRIDAY": "#FFFC00",
                    "SATURDAY": "#FF5C00",
                    "SUNDAY": "#E60000"
                }

                return (
                    f"color: {colors.get(str(val).upper(), 'white')}; font-weight:bold;"
                )

            # =========================
            # APPLY STYLING
            # =========================
            styled_df = (
                df.style
                .map(color_payment, subset=["payment_status"])
                .map(color_name, subset=["name"])
                .map(color_shift, subset=["shift"])
                .map(color_day, subset=["day"])

            )

            st.dataframe(styled_df, use_container_width=True)
    # -------------------- Chart --------------------

    elif menu == "🗃️ Analytics Dashboard":

        img_base64 = load_image("images/chart.png")

        st.markdown(

            f"""

            <div style="display: flex; align-items: center; gap: 8px; font-size: 1.25rem;"><img src="data:image/png;base64,{img_base64}" width="30" /><span>Analytics Dashboard</span>

            </div>

            """,

            unsafe_allow_html=True

        )

        df = fetch_all()

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
                to_date_default = from_date_default + relativedelta(months=1)
            else:
                to_date_default = today.replace(day=10)
                from_date_default = to_date_default - relativedelta(months=1)

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
                (df["date"] < pd.to_datetime(to_date) + pd.Timedelta(days=1))
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

                def color_name(val):
                    return (
                        f"color: {color_map.get(str(val).upper(), 'white')}; "
                        f"font-weight: bold;"
                    )

                # ======================================================
                # ✅ SHOW SUMMARY TABLE
                # ======================================================

                st.markdown("### 📝 Summary")

                try:
                    styled_df = (
                        display_df.style
                        .map(color_name, subset=["Name"])
                    )

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

    elif menu == "🛠️ Edit Tiffin Records":

        img_base64 = load_image("images/edit.png")

        st.markdown(
            f"""<div style="display: flex; align-items: center; gap: 8px; font-size: 1.25rem;">
                <img src="data:image/png;base64,{img_base64}" width="30" />
                <span>Edit Existing Record</span>
            </div>
            """,

            unsafe_allow_html=True

        )

        # --- Fetch records ---

        df = fetch_all()

        if df.empty:

            st.info("No records to edit.")

        else:

            df_reset = df.copy()

            # --- Color functions ---

            def color_name(val):

                colors = {"MEET": "#FF0033", "YASH": "#bfff00", "DHRUMIL": "#00bfff"}

                return f"color: {colors[val.upper()]}; font-weight: bold;" if str(val).upper() in colors else ""

            def color_payment(val):

                val_lower = str(val).lower()

                if val_lower == "payment done":

                    return "color: #059212; font-weight:bold;"  # greenish

                elif val_lower in ["pending", "payment pending"]:

                    return "color: #76153C; font-weight:bold;"  # pink/purple

                elif val_lower == "paid":

                    return "color: goldenrod; font-weight:bold;"

                elif val_lower == "not involved":

                    return "color: #FCDC2A; font-weight:bold;"  # neutral yellow-green

                return ""

            # --- Display styled dataframe ---

            styled_df = df_reset.style.map(color_name, subset=["name"]).map(color_payment,
                                                                                      subset=["payment_status"])

            st.dataframe(styled_df, use_container_width=True)

            # --- Selectbox to choose record ---

            record_options = [f"{row['id']} - {row['name']} - {row['date']}" for _, row in df_reset.iterrows()]

            selected_record = st.selectbox("Select Record for Edit", ["-- Select --"] + record_options)

            # --- Show edit fields only after selection ---

            if selected_record != "-- Select --":

                selected_id = int(selected_record.split(" - ")[0])

                record = df_reset[df_reset['id'] == selected_id].iloc[0]

                st.session_state['edit_record_id'] = record['id']

                st.session_state['edit_values'] = record

                values = st.session_state['edit_values']

                # Convert string date to datetime.date object

                if isinstance(values['date'], str):

                    current_date = datetime.datetime.strptime(values['date'], "%Y-%m-%d").date()

                else:

                    current_date = values['date']

                # --- Editable fields ---

                edit_date = st.date_input("📅 Edit Date", current_date)

                edit_shift = st.selectbox("Shift", ["DAY", "NIGHT"], index=["DAY", "NIGHT"].index(values['shift']))

                edit_qty = st.number_input("Quantity", min_value=0.0, value=float(values['quantity']))

                edit_roti = st.numFber_input("Roti Quantity", min_value=0, value=int(values['roti']))

                roti_amount = edit_roti * 7

                tiffin_amount = round(90 * edit_qty, 2)

                final_amount = tiffin_amount + roti_amount if edit_shift == "DAY" else tiffin_amount

                st.info(f"💰 Final Amount: ₹{final_amount}")

                # --- Determine payment status ---

                if edit_qty == 0 and edit_roti == 0:

                    default_payment_status = "Not Involved"

                else:

                    default_payment_status = values['payment_statusF'] if values[
                                                                             'payment_status'].lower() != "not involved" else "PAYMENT PENDING"

                payment_status = st.selectbox(

                    "Payment Status",

                    ["Not Involved", "PAYMENT PENDING", "PAYMENT DONE"],

                    index=["Not Involved", "PAYMENT PENDING", "PAYMENT DONE"].index(default_payment_status)

                )

                # --- Save changes ---

                if st.button("Save Changes"):
                    update_record(

                        record_id=int(st.session_state['edit_record_id']),

                        date=edit_date,

                        shift=edit_shift,

                        qty=float(edit_qty),

                        roti=int(edit_roti),

                        amount=float(final_amount),

                        roti_amount=float(roti_amount),

                        payment_status=payment_status

                    )

                    st.success("Record updated successfully!")

                    # Clear session state

                    del st.session_state['edit_values']

                    del st.session_state['edit_record_id']

    # -------------------- Payment Method --------------------

    elif menu == "💳 Update Payment Status":

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
        df = fetch_all()

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

    def color_name(val):

        colors = {"MEET": "#FF0033", "YASH": "#bfff00", "DHRUMIL": "#00bfff"}

        return colors.get(str(val).upper(), None)

    def color_payment(val):

        val_lower = str(val).lower()

        if val_lower == "PAYMENT DONE":
            return "#059212"

        elif val_lower in ["pending", "PAYMENT PENDING"]:
            return "#76153C"

        elif val_lower == "paid":
            return "goldenrod"

        elif val_lower == "not involved":
            return "#FCDC2A"

        return None

    # --- Streamlit menu ---

    if menu == "⬇️ Export Data":

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

        df = fetch_all()

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

                def color_shift(val):
                    if str(val).lower() == "day":
                        return "#FF8F00"
                    elif str(val).lower() == "night":
                        return "#3B9797"
                    return None

                def color_name(val):

                    colors = {
                        "MEET": "#FF0033",
                        "YASH": "#bfff00",
                        "DHRUMIL": "#00bfff",
                        "TOTAL": "#9929EA"
                    }

                    return colors.get(str(val).upper(), None)

                def color_payment(val):

                    val_lower = str(val).lower()

                    if val_lower == "payment done":
                        return "#73FF00"
                    elif val_lower in ["pending", "payment pending"]:
                        return "#FF0095"
                    elif val_lower == "paid":
                        return "goldenrod"
                    elif val_lower == "not involved":
                        return "#FCDC2A"
                    if val_lower == "payment done":
                        return "color: #73FF00; font-weight:bold;"
                    elif val_lower in ["pending", "payment pending"]:
                        return "color: #FF0095; font-weight:bold;"
                    elif val_lower == "paid":
                        return "color: goldenrod; font-weight:bold;"
                    elif val_lower == "not involved":
                        return "color: #FCDC2A; font-weight:bold;"
                    return ""

                def color_day(val):
                    colors = {
                        "MONDAY": "#BF00FF",
                        "TUESDAY": "#0000FF",
                        "WEDNESDAY": "#7DF9FF",
                        "THURSDAY": "#72FF13",
                        "FRIDAY": "#FFFC00",
                        "SATURDAY": "#FF5C00",
                        "SUNDAY": "#E60000"
                    }

                    return (
                        f"color: {colors.get(str(val).upper(), 'white')}; font-weight:bold;"
                    )
                # ---------- Streamlit Table Styling ----------

                def style_table(df):

                    styler = df.style.map(
                        lambda v: f"color: {color_name(v)}; font-weight:bold;" if color_name(v) else "",
                        subset=['name']
                    )

                    styler = styler.map(
                        lambda v: f"color: {color_payment(v)};font-weight:bold;" if color_payment(v) else "",
                        subset=['payment_status']
                    )

                    if 'shift' in df.columns:
                        styler = styler.map(
                            lambda v: f"color: {color_shift(v)};font-weight:bold;" if color_shift(v) else "",
                            subset=['shift']
                        )

                    if 'day' in df.columns:
                        styler = styler.map(
                            lambda v: f"color: {color_day(v)};font-weight:bold;" if color_day(v) else "",
                            subset=['day']
                        )
                    return styler

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

                def color_summary_name(val):

                    colors = {
                        "MEET": "#FF0033",
                        "YASH": "#bfff00",
                        "DHRUMIL": "#00bfff",
                        "TOTAL": "#9929EA"
                    }

                    return f"color: {colors.get(str(val).upper(), 'white')}; font-weight:bold;"

                styled_summary = summary_df.style.map(
                    color_summary_name,
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

                            color = color_name(val)

                            if color:
                                cell_format = workbook.add_format({
                                    'font_color': color,
                                    'bold': True
                                })

                                worksheet.write(row_num, name_col_idx, val, cell_format)

                        # ---------- Payment Status Coloring ----------

                        payment_col_idx = filtered_df.columns.get_loc("payment_status")

                        for row_num, val in enumerate(filtered_df['payment_status'], start=1):

                            color = color_payment(val)

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

                                color = color_shift(val)

                                if color:
                                    cell_format = workbook.add_format({
                                        'font_color': color,
                                        'bold': True

                                    })

                                    worksheet.write(row_num, shift_col_idx, val, cell_format)

                        # ---------- Day Coloring ----------

                        if 'day' in filtered_df.columns:

                            day_col_idx = filtered_df.columns.get_loc("day")

                            day_colors = {
                                "MONDAY": "#FF3B30",
                                "TUESDAY": "#FF9500",
                                "WEDNESDAY": "#FFD60A",
                                "THURSDAY": "#34C759",
                                "FRIDAY": "#00C7BE",
                                "SATURDAY": "#007AFF",
                                "SUNDAY": "#AF52DE"
                            }

                            for row_num, val in enumerate(filtered_df['day'], start=1):

                                color = day_colors.get(str(val).upper())

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

    elif menu == "💳 Add Expense Entry":
        account_page()
    elif menu == "🔍 View Expense Records":
        account_records_page()
    elif menu == "✏️ Edit Expense Details":
        edit_account_page()
if __name__ == "__main__":
    try:
        app()

    except psycopg2.OperationalError:
        st.error("🔴 Database is currently offline.")

    except FileNotFoundError:
        st.error("📂 Required file is missing.")

    except Exception as e:
        st.error("⚠️ Something went wrong.")
