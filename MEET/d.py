# C:\Users\MEET\AppData\Local\Programs\Python\Python314\python.exe - m streamlit run T.py

import streamlit as st

import datetime

import pandas as pd

import matplotlib.pyplot as plt

import bcrypt

import psycopg2

from io import BytesIO
import base64

# -------------------- Streamlit Config --------------------

st.set_page_config(
    page_title="Tiffin Tracker",
    # page_icon="d.png",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get help': None,
        'Report a bug': None,
        'About': None
    }
)

# baki nu code yahan lakhvo
# -------------------- Custom Button CSS --------------------

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

# -------------------- Footer --------------------

with open("images/icons8-monzo-48.png", "rb") as f:
    img_bytes = f.read()
    img_base64 = base64.b64encode(img_bytes).decode()

# Footer with left and right icons
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
        color: red;
        animation: rainbow 8s linear infinite;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 15px;
    }}

    @keyframes rainbow {{
        0% {{ filter: hue-rotate(0deg); }}
        100% {{ filter: hue-rotate(360deg); }}
    }}
    </style>

    <div class="footer">
        <img src="data:image/png;base64,{img_base64}" width="30" />
        Made by MEET MEWADA
        <img src="data:image/png;base64,{img_base64}" width="30" />
    </div>
    """,
    unsafe_allow_html=True
)



# -------------------- Hide Streamlit Menu & Settings --------------------

st.markdown("""

    <style>

    #MainMenu {visibility: hidden;}

    footer {visibility: hidden;}

    </style>

""", unsafe_allow_html=True)
# -------------------- DB Config --------------------
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

# -------------------- DB Functions --------------------

def get_connection():
    try:
        conn = psycopg2.connect(
            host=owert,
            database=petoc,
            user=lemox,
            password=ternak,
            port=int(xoper),
            sslmode="require"   # ✅ VERY IMPORTANT
        )
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def create_table():
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(f"""

           CREATE TABLE IF NOT EXISTS {TABLE_NAME} (

               id SERIAL PRIMARY KEY,

               Date DATE,

               Time TIME,

               Name VARCHAR(50),

               Shift VARCHAR(10),

               Quantity FLOAT,

               Roti INT,

               Roti_Amount FLOAT,

               Amount FLOAT,

               Payment_Status VARCHAR(50)

           )

       """)

    conn.commit()

    cursor.close()

    conn.close()


def create_account_table():
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

                   CREATE TABLE IF NOT EXISTS account_records
                   (

                       id
                       SERIAL
                       PRIMARY
                       KEY,

                       date
                       DATE,

                       time
                       TIME,

                       name
                       VARCHAR
                   (
                       50
                   ),

                       product_name VARCHAR
                   (
                       100
                   ),

                       place_name VARCHAR
                   (
                       100
                   ),

                       total_amount FLOAT,

                       per_person_amount FLOAT,

                       payment_status VARCHAR
                   (
                       50
                   )

                       )

                   """)

    conn.commit()

    cursor.close()

    conn.close()


def fetch_all():
    conn = get_connection()

    df = pd.read_sql(
        f"SELECT id, Date, Time, Name, Shift, Quantity, Roti, Roti_Amount, Amount, Payment_Status FROM {TABLE_NAME}",
        conn)

    conn.close()

    # Convert column names to lowercase

    df.columns = [col.lower() for col in df.columns]

    return df


def insert_record(data):
    conn = get_connection()

    cursor = conn.cursor()

    for row in data:
        cursor.execute(f"""

            INSERT INTO {TABLE_NAME} (Date, Time, Name, Shift, Quantity, Roti, Roti_Amount, Amount, Payment_Status)

            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)

        """, row)

    conn.commit()

    cursor.close()

    conn.close()


def update_record(record_id, date, shift, qty, roti, amount, roti_amount, payment_status):
    conn = get_connection()
    cursor = conn.cursor()

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
    conn.close()



def update_payment(start_date, end_date, payment_status):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(f"""

        UPDATE {TABLE_NAME}

        SET Payment_Status=%s

        WHERE Date BETWEEN %s AND %s

    """, (payment_status, start_date, end_date))

    conn.commit()

    cursor.close()

    conn.close()


def delete_tiffin_page():
    # PNG file load & encode
    with open("images/icons8-delete-50.png", "rb") as f:
        img_bytes = f.read()
        img_base64 = base64.b64encode(img_bytes).decode()

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

    conn = get_connection()
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
    conn.close()


def delete_account_page():
    # PNG file load & encode
    with open("images/icons8-delete-100.png", "rb") as f:
        img_bytes = f.read()
        img_base64 = base64.b64encode(img_bytes).decode()

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
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM account_records ORDER BY date DESC, time DESC", conn)
    names = df['name'].unique().tolist() if not df.empty else []
    conn.close()

    if df.empty:
        st.info("No Account records available to delete.")
        return

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()

    option = st.radio("Delete by:", ["Date Range", "Name"], index=0)

    conn = get_connection()
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
    conn.close()
# -------------------- Login --------------------

LOGIN_USER_HASH = b"$2b$12$tAAm6RQ775w8WJBW9brlXuHDgiYuMn3UcKI5gKRm4CCIbNp9lHXfi"

LOGIN_PASS_HASH = b"$2b$12$xfVNu267cnWT0hjsrzoWQ.AOYvxcm9GdWjjAlmcSG8IFBGf3IuP62"


def login():
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
    st.markdown(
        """
        <div style="display: flex; 
                    justify-content: center; 
                    align-items: center; 
                    gap: 8px;">
            <img src="data:image/mt.png;base64,{}" width="35">
            <h3 style="margin:0;">LOGIN</h3>
        </div>
        """.format(
            base64.b64encode(open("images/icons8-login-50.png", "rb").read()).decode()
        ),
        unsafe_allow_html=True
    )
    username = st.text_input("Username", key="user")

    password = st.text_input("Password", type="password", key="pass")

    if st.button("Login"):

        if bcrypt.checkpw(username.encode(), LOGIN_USER_HASH) and bcrypt.checkpw(password.encode(), LOGIN_PASS_HASH):

            st.session_state['logged_in'] = True

            st.success("Logged in successfully!")

        else:

            st.error("Invalid credentials")


# -------------------- Account Page --------------------

def account_page():
    with open("images/icons8-expense-100.png", "rb") as f:
        img_bytes = f.read()
        img_base64 = base64.b64encode(img_bytes).decode()

    # Display icon + text side by side
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
    time = st.time_input("Time", value=datetime.datetime.now().time())

    product_name = st.text_input("Product Name")
    place_name = st.text_input("Place Name")

    total_amount = st.number_input("Total Amount", min_value=0.0, value=0.0, step=0.01)

    st.write("Select who was present (including payer):")
    participants = []

    for name in names:
        # Payer checkbox is always checked by default
        default_checked = True if name == paid_by else False
        if st.checkbox(name, value=default_checked):
            participants.append(name)

    if st.button("Save Expense"):
        # Split only among participants
        if len(participants) == 0:
            st.warning("Select at least one participant.")
            return

        per_person_amount = round(total_amount / len(participants), 2)

        conn = get_connection()
        cursor = conn.cursor()

        for name in names:
            if name in participants:
                # Participant – check if payer or not
                payment_status = "Paid" if name == paid_by else "Pending"
                person_amount = per_person_amount
            else:
                # Not participated
                payment_status = "Not Involved"
                person_amount = 0

            cursor.execute("""
                INSERT INTO account_records 
                (date, time, name, product_name, place_name, total_amount,
                 per_person_amount, payment_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                date,
                time,
                name,
                product_name,
                place_name,
                total_amount,
                person_amount,
                payment_status
            ))

        conn.commit()
        cursor.close()
        conn.close()

        st.success(f"Expense added successfully! Each participant owes ₹{per_person_amount}")

# -------------------- Account Records Page --------------------

def account_records_page():
    # PNG file load & encode
    with open("images/icons8-google-sheets-100.png", "rb") as f:
        img_bytes = f.read()
        img_base64 = base64.b64encode(img_bytes).decode()

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
    conn = get_connection()

    df = pd.read_sql("SELECT * FROM account_records ORDER BY date DESC, time DESC", conn)

    conn.close()

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

                return "color: green;"

            elif str(val).lower() == "pending":

                return "color: pink;"

            elif str(val).lower() == "paid":

                return "color: goldenrod;"  # yellow font

            return ""

        # --- Apply both styles ---

        styled_df = (

            df.style

            .applymap(color_name, subset=["name"])

            .applymap(color_payment, subset=["payment_status"])

        )

        st.dataframe(styled_df, use_container_width=True)


def edit_account_page():
    # PNG file load & encode
    with open("images/icons8-edit-property-100.png", "rb") as f:
        img_bytes = f.read()
        img_base64 = base64.b64encode(img_bytes).decode()

    # Display icon + text side by side
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 8px; font-size: 1.25rem;">
            <img src="data:image/png;base64,{img_base64}" width="30" />
            <span>✏️ Edit Account Details</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    # ---------------- Fetch account records ----------------

    conn = get_connection()

    df = pd.read_sql("SELECT * FROM account_records ORDER BY date DESC, time DESC", conn)

    conn.close()

    if df.empty:
        st.info("No account records available.")

        return

    # ---------------- Filters (Bottom Inputs) ----------------

    names = df['name'].unique().tolist()

    selected_name = st.selectbox("Select Name", ["-- SELECT NAME --"] + names, key="name_filter")

    min_date = df['date'].min()

    max_date = df['date'].max()

    selected_date = st.date_input("Select Date", value=None, min_value=min_date, max_value=max_date, key="date_filter")

    record_ids = df['id'].unique().tolist()

    selected_id = st.selectbox("Select Record ID", ["-- SELECT ID --"] + [str(rid) for rid in record_ids],
                               key="id_filter")

    # ---------------- Validate Selection ----------------

    if selected_name == "-- SELECT NAME --" or selected_id == "-- SELECT ID --":
        st.warning("⚠️ Please select both Name and Record ID to edit a record.")

        st.stop()  # Stop execution until proper selection

    # ---------------- Filter dataframe ----------------

    filtered_df = df.copy()

    filtered_df = filtered_df[(filtered_df['name'] == selected_name) &

                              (filtered_df['id'] == int(selected_id))]

    if selected_date:
        filtered_df = filtered_df[pd.to_datetime(filtered_df['date']).dt.date == selected_date]

    # ---------------- Show Table on Top ----------------

    st.write("### 📋 Filtered Records")

    if filtered_df.empty:
        st.warning("⚠️ No record found for the selected Name and ID!")

        return  # Stop further execution

    st.dataframe(filtered_df)

    # ---------------- Edit Record Inputs (Bottom) ----------------

    record = filtered_df.iloc[0]  # Safe now because filtered_df is not empty

    edit_product = str(record['product_name'])

    edit_place = str(record['place_name'])

    edit_total = float(record['total_amount'])

    edit_per_person = float(record['per_person_amount'])

    payment_options = ["Pending", "Payment Done", "Paid"]

    edit_payment = str(record['payment_status'])

    st.write("### ✏️ Edit Selected Record")

    edit_product = st.text_input("Product Name", edit_product)

    edit_place = st.text_input("Place Name", edit_place)

    edit_total = st.number_input("Total Amount", value=edit_total)

    edit_per_person = st.number_input("Per Person Amount", value=edit_per_person)

    edit_payment = st.selectbox("Payment Status", payment_options, index=payment_options.index(edit_payment))

    if st.button("Save Changes"):
        conn = get_connection()

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

                           int(record['id'])  # Convert numpy.int64 → int

                       ))

        conn.commit()

        cursor.close()

        conn.close()

        st.success("✅ Record updated successfully!")


# -------------------- Sidebar Logo --------------------

st.sidebar.image("images/me.png", use_container_width=True)


# -------------------- Run App --------------------

def app():
    create_table()  # Ensure table exists

    create_account_table()  # New account_records table

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

    menu = st.sidebar.selectbox("Navigation", [
        "➕ Add Tiffin Entry",
        "🔎 View Tiffin Records",
        "❎ Remove Tiffin Records",
        "🛠️ Edit Tiffin Records",
        "💳 Add Expense Entry",
        "🔍 View Expense Records",
        "❎ Remove Expense Records",
        "✏️ Edit Expense Details",
        "🗃️ Analytics Dashboard",
        "💳 Update Payment Status",
        "⬇️ Export Data",
    ])

    if menu == "❎ Remove Tiffin Records":
        delete_tiffin_page()

    elif menu == "❎ Remove Expense Records":
        delete_account_page()

    # -------------------- Add Record --------------------

    if menu == "➕ Add Tiffin Entry":

        with open("images/icons8-edit-property-100.png", "rb") as f:
            img_bytes = f.read()
            img_base64 = base64.b64encode(img_bytes).decode()

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

        shift = st.selectbox("Select Shift", ["-- SELECT DAY --", "Day", "Night"])

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

        roti_rate = 5

        if shift == "Day":

            st.markdown("### Enter Roti Quantity per Person")

            for name in selected_names:
                roti_qty[name] = st.number_input(f"{name} Roti Quantity", min_value=0, value=0, step=1)

        else:

            for name in selected_names:
                roti_qty[name] = 0

        per_person_qty = round(float(tiffin_qty) / len(selected_names), 2)

        per_person_amount = round(90 * per_person_qty, 2)

        st.markdown("### Tiffin Amount per Person")

        for name in names:

            if name in selected_names:

                st.write(
                    f"{name}: Qty = {per_person_qty:.2f}, Amount = ₹{per_person_amount:.2f}, Roti = {roti_qty.get(name, 0)}")

            else:

                st.write(f"{name}: No Tiffin Today → Qty = 0.00, Amount = 0.00, Roti = 0")

        total_tiffin_amount = round(per_person_amount * len(selected_names), 2)

        total_roti_amount = round(sum([roti_qty.get(name, 0) * roti_rate for name in selected_names]), 2)

        total_amount = total_tiffin_amount + total_roti_amount

        st.markdown(f"### 💰 Total Tiffin Amount: ₹{total_tiffin_amount:.2f}")

        if shift == "Day":
            st.markdown(f"### 💰 Total Roti Amount: ₹{total_roti_amount:.2f}")

        st.markdown(f"### 🏆 Final Total Amount: ₹{total_amount:.2f}")

        if st.button("Save Record"):

            data_to_insert = []

            for name in names:

                if name in selected_names:

                    qty = per_person_qty

                    amount = per_person_amount

                else:

                    qty = 0.00

                    amount = 0.00

                roti = roti_qty.get(name, 0)

                roti_amount = roti * roti_rate

                total_individual_amount = round(amount + roti_amount, 2)

                row = [selected_date, current_time, name, shift, qty, roti, roti_amount, total_individual_amount, "Payment Pending"]


                data_to_insert.append(row)

            insert_record(data_to_insert)

            st.success("Record(s) added successfully!")



    # -------------------- Records --------------------

    elif menu == "🔎 View Tiffin Records":

        # PNG file load & encode
        with open("images/icons8-view-50.png", "rb") as f:
            img_bytes = f.read()
            img_base64 = base64.b64encode(img_bytes).decode()

        # Display icon + text side by side (similar to st.subheader)
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

            # Font color for Payment Status

            def color_payment(val):

                if str(val).lower() == "payment done":

                    return "color: green;"

                elif str(val).lower() in ["pending", "payment pending"]:

                    return "color: pink;"

                elif str(val).lower() == "paid":

                    return "color: goldenrod;"  # yellow font

                return ""

            # Font color for Name

            def color_name(val):

                colors = {

                    "MEET": "#FF0033",

                    "YASH": "#bfff00",

                    "DHRUMIL": "#00bfff"

                }

                return f"color: {colors[val.upper()]}; font-weight: bold;" if str(val).upper() in colors else ""

            styled_df = (

                df.style

                .applymap(color_payment, subset=["payment_status"])

                .applymap(color_name, subset=["name"])

            )

            st.dataframe(styled_df, use_container_width=True)





    # -------------------- Chart --------------------

    elif menu == "🗃️ Analytics Dashboard":

        # PNG file load & encode
        with open("images/icons8-statistics-100.png", "rb") as f:
            img_bytes = f.read()
            img_base64 = base64.b64encode(img_bytes).decode()

        # Display icon + text side by side
        st.markdown(
            f"""
                  <div style="display: flex; align-items: center; gap: 8px; font-size: 1.25rem;">
                      <img src="data:image/png;base64,{img_base64}" width="30" />
                      <span>Analytics Dashboard</span>
                  </div>
                  """,
            unsafe_allow_html=True
        )
        df = fetch_all()  # fetch from DB

        if df.empty:

            st.info("No records to plot.")

        else:

            df['date'] = pd.to_datetime(df['date'], errors='coerce')

            today_dt = datetime.date.today()

            current_month_df = df[(df['date'].dt.month == today_dt.month) & (df['date'].dt.year == today_dt.year)]

            if current_month_df.empty:

                st.info("No orders found for this month.")

            else:

                summary_df = current_month_df.groupby('name').agg({"quantity": "sum", "amount": "sum"}).reset_index()

                st.markdown("### 📝 Summary of This Month")

                st.dataframe(summary_df)

                summary = summary_df.set_index('name')['quantity']

                colors = {"MEET": "#6B0848", "YASH": "#906C8B", "DHRUMIL": "#DD5353"}

                color_list = [colors.get(name, "gray") for name in summary.index]

                fig, ax = plt.subplots()

                ax.pie(summary, labels=summary.index, autopct='%1.1f%%', colors=color_list, startangle=90)

                ax.set_title("📊 Monthly Tiffin Orders by User")

                st.pyplot(fig)



    # -------------------- Edit --------------------

    elif menu == "🛠️ Edit Tiffin Records":

        with open("images/icons8-edit-property-100.png", "rb") as f:
            img_bytes = f.read()
            img_base64 = base64.b64encode(img_bytes).decode()

        # Display icon + text side by side
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 8px; font-size: 1.25rem;">
                <img src="data:image/png;base64,{img_base64}" width="30" />
                <span>✏️ Edit Existing Record</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        df = fetch_all()

        if df.empty:

            st.info("No records to edit.")

        else:

            df_reset = df.copy()

            st.dataframe(df_reset)

            # Select record to edit

            sr_no = st.number_input("Enter Sr No to Edit", min_value=1, max_value=len(df_reset), step=1)

            if st.button("Load Record"):
                record = df_reset.iloc[sr_no - 1]

                st.session_state['edit_record_id'] = record['id']

                st.session_state['edit_values'] = record

            if 'edit_values' in st.session_state:

                values = st.session_state['edit_values']

                # Convert string date to datetime.date object if needed
                if isinstance(values['date'], str):
                    current_date = datetime.datetime.strptime(values['date'], "%Y-%m-%d").date()
                else:
                    current_date = values['date']

                edit_date = st.date_input("📅 Edit Date", current_date)

                edit_shift = st.selectbox("Shift", ["Day", "Night"], index=["Day", "Night"].index(values['shift']))

                edit_qty = st.number_input("Quantity", min_value=0.0, value=float(values['quantity']))

                edit_roti = st.number_input("Roti Quantity", min_value=0, value=int(values['roti']))

                roti_amount = edit_roti * 5

                tiffin_amount = round(90 * edit_qty, 2)

                final_amount = tiffin_amount + roti_amount if edit_shift == "Day" else tiffin_amount

                st.info(f"💰 Final Amount: ₹{final_amount}")

                payment_status = st.selectbox("Payment Status", ["Payment Pending", "Payment Done"],

                                              index=["Payment Pending", "Payment Done"].index(values['payment_status']))

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

                    del st.session_state['edit_values']

                    del st.session_state['edit_record_id']



    # -------------------- Payment Method --------------------

    elif menu == "💳 Update Payment Status":

        # PNG file load & encode
        with open("images/icons8-payment-history-48.png", "rb") as f:
            img_bytes = f.read()
            img_base64 = base64.b64encode(img_bytes).decode()

        # Display icon + text side by side
        st.markdown(
            f"""
                  <div style="display: flex; align-items: center; gap: 8px; font-size: 1.25rem;">
                      <img src="data:image/png;base64,{img_base64}" width="30" />
                      <span>Update Payment Status</span>
                  </div>
                  """,
            unsafe_allow_html=True
        )
        df = fetch_all()

        if df.empty:

            st.info("No records available.")

        else:

            df['date'] = pd.to_datetime(df['date'], errors='coerce')

            min_date = df['date'].min().date() if not df['date'].isna().all() else datetime.date.today()

            max_date = df['date'].max().date() if not df['date'].isna().all() else datetime.date.today()

            start_date = st.date_input("Start Date", value=min_date, key="payment_start")

            end_date = st.date_input("End Date", value=max_date, key="payment_end")

            selected_payment = st.selectbox("Payment Status to Update",

                                            ["-- SELECT --", "Payment Pending", "Payment Done"])

            if st.button("Update Payments"):

                if start_date > end_date:

                    st.error("❎ Start Date cannot be after End Date.")

                else:

                    # Check if all dates in range exist in DB

                    date_range = pd.date_range(start=start_date, end=end_date).date

                    db_dates = set(df['date'].dropna().dt.date)

                    if all(d in db_dates for d in date_range):

                        if selected_payment != "-- SELECT --":
                            update_payment(start_date, end_date, selected_payment)

                            st.success(f"✅ Payment status updated successfully for {start_date} to {end_date}")

                    else:

                        st.warning("⚠️ Cannot update: Some dates in the range do not exist in the records.")



    # -------------------- Download --------------------

    elif menu == "⬇️ Export Data":

        # PNG file load & encode
        with open("images/icons8-microsoft-excel-2025-48.png", "rb") as f:
            img_bytes = f.read()
            img_base64 = base64.b64encode(img_bytes).decode()

        # Display icon + text side by side
        st.markdown(
            f"""
                        <div style="display: flex; align-items: center; gap: 8px; font-size: 1.25rem;">
                            <img src="data:image/png;base64,{img_base64}" width="30" />
                            <span>Dowanload Tifffin Exces</span>
                        </div>
                        """,
            unsafe_allow_html=True
        )
        df = fetch_all()

        if df.empty:

            st.info("No records available for download")

        else:

            df['date'] = pd.to_datetime(df['date'], errors='coerce')

            min_date = df['date'].min().date() if not df['date'].isna().all() else datetime.date.today()

            max_date = df['date'].max().date() if not df['date'].isna().all() else datetime.date.today()

            from_date = st.date_input("From Date", value=min_date, key="download_from")

            to_date = st.date_input("To Date", value=max_date, key="download_to")

            if from_date > to_date:

                st.error("❎ Start Date cannot be after End Date.")

            else:

                date_range = pd.date_range(start=from_date, end=to_date).date

                db_dates = set(df['date'].dropna().dt.date)

                if all(d in db_dates for d in date_range):

                    filtered_df = df[

                        (df['date'] >= pd.to_datetime(from_date)) & (df['date'] <= pd.to_datetime(to_date))]

                    st.markdown(f"### Records from {from_date} to {to_date}")

                    st.dataframe(filtered_df)

                    if not filtered_df.empty:
                        output = BytesIO()

                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            filtered_df.to_excel(writer, index=False, sheet_name="Tiffin Records")

                        processed_data = output.getvalue()

                        st.download_button(

                            label="⬇️ Download Excel",

                            data=processed_data,

                            file_name=f"Tiffin_Records_{from_date}_to_{to_date}.xlsx",

                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

                        )

                else:

                    st.warning("⚠️ Cannot download: Some dates in the range do not exist in the records.")

                # -------------------- Delete --------------------

    # st.markdown("""
    # <style>
    # .custom-header {
    #     position: fixed;
    #     top: 0;
    #     left: 0;
    #     width: 100%;
    #     background: black;
    #     color: white;
    #     text-align: center;
    #     padding: 10px;
    #     z-index: 9999;
    # }
    # .main-container {
    #     margin-top: 80px;  /* Push content below header */
    # }
    # </style>
    #
    #
    # """, unsafe_allow_html=True)
    #
    # # --- Place the menu as a normal selectbox (not sidebar) ---
    # menu = st.selectbox("Menu", [
    #     "Add Record", "Records", "Delete Tiffin",
    #     "Account", "Account Records", "Delete Account", "Edit Account Details",
    #     "Chart", "Edit",
    #     "Payment Method", "Download",
    # ])
    #
    # # --- Handle menu options ---
    # if menu == "Delete Tiffin":
    #     st.write("Delete Tiffin Page")  # replace with delete_tiffin_page()
    # elif menu == "Delete Account":
    #     st.write("Delete Account Page")  # replace with delete_account_page()
    # else:
    #     st.write(f"Selected: {menu}")

    elif menu == "💳 Add Expense Entry":

        account_page()

    elif menu == "🔍 View Expense Records":

        account_records_page()

    elif menu == "✏️ Edit Expense Details":

        edit_account_page()


# -------------------- Run App --------------------

if __name__ == "__main__":
    app()

