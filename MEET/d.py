import streamlit as st

import datetime

import pandas as pd

import matplotlib.pyplot as plt

import bcrypt

import psycopg2

from io import BytesIO

# -------------------- Streamlit Config --------------------

st.set_page_config(
    page_title="MEET_MEWADA",
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

st.markdown("""

    <style>

    .footer {

        position: fixed;

        left: 0;

        bottom: 0;

        width: 100%;

        background-color: transparent;

        color: white;

        text-align: center;

        padding: 10px;

    }

    </style>

    <div class="footer">

        Made️ by MEET MEWADA

    </div>

""", unsafe_allow_html=True)

# -------------------- Hide Streamlit Menu & Settings --------------------

st.markdown("""

    <style>

    #MainMenu {visibility: hidden;}

    footer {visibility: hidden;}

    </style>

""", unsafe_allow_html=True)
# -------------------- DB Config --------------------
DB_NAME = "tifin_db"
DB_USER = "avnadmin"
DB_PASS = "AVNS_sULyoOO-Tc37Z1v4cU2"  # Aiven માંથી regenerate કરો
DB_HOST = "pg-19531148-mevadameet916-4098.b.aivencloud.com"
DB_PORT = 10003
TABLE_NAME = "tiffin"
HEADERS = ["Date", "Time", "Name", "Shift", "Quantity", "Roti", "Roti_Amount", "Amount", "Payment_Status"]


# -------------------- DB Functions --------------------

def get_connection():
    return psycopg2.connect(

        host=DB_HOST,

        database=DB_NAME,

        user=DB_USER,

        password=DB_PASS,

        port=DB_PORT

    )


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


def delete_records(start_date, end_date):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(f"""

        DELETE FROM {TABLE_NAME}

        WHERE Date BETWEEN %s AND %s

    """, (start_date, end_date))

    deleted_count = cursor.rowcount

    conn.commit()

    cursor.close()

    conn.close()

    return deleted_count


# -------------------- Login --------------------

LOGIN_USER_HASH = b"$2b$12$tAAm6RQ775w8WJBW9brlXuHDgiYuMn3UcKI5gKRm4CCIbNp9lHXfi"

LOGIN_PASS_HASH = b"$2b$12$xfVNu267cnWT0hjsrzoWQ.AOYvxcm9GdWjjAlmcSG8IFBGf3IuP62"


def login():
    st.title("🍱 Tiffin Tracker - Login")

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
    st.subheader("💳 Add Monthly Expense")

    names = ["MEET", "YASH", "BIREN", "DHRUMIL"]

    paid_by = st.selectbox("Who Paid?", names)

    date = st.date_input("Date", value=datetime.date.today())

    time = st.time_input("Time", value=datetime.datetime.now().time())

    product_name = st.text_input("Product Name")

    place_name = st.text_input("Place Name")

    total_amount = st.number_input("Total Amount", min_value=0.0, value=0.0, step=0.01)

    if st.button("Save Expense"):

        per_person_amount = round(total_amount / 4, 2)

        conn = get_connection()

        cursor = conn.cursor()

        for name in names:
            payment_status = "Paid" if name == paid_by else "Pending"

            cursor.execute("""

                           INSERT INTO account_records (date, time, name, product_name, place_name, total_amount,
                                                        per_person_amount, payment_status)

                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)

                           """, (date, time, name, product_name, place_name, total_amount, per_person_amount,

                                 payment_status))

        conn.commit()

        cursor.close()

        conn.close()

        st.success(f"Expense added successfully! Each person owes ₹{per_person_amount}")


# -------------------- Account Records Page --------------------

def account_records_page():
    st.subheader("📄 Account Records")

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

                "BIREN": "#00ff80",

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
    st.subheader("✏️ Edit Account Details")

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


# -------------------- Run App --------------------

def app():
    create_table()  # Ensure table exists

    create_account_table()  # New account_records table

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        login()

        return

    st.title("📊 Tiffin Tracker System") 

    menu = st.sidebar.selectbox("Menu", ["Add Record", "Records", "Chart", "Edit",

                                         "Payment Method", "Download", "Delete",

                                         "Account", "Account Records", "Edit Account Details"])

    # -------------------- Add Record --------------------

    if menu == "Add Record":

        st.subheader("➕ Add New Record")

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

        names = ["MEET", "YASH", "BIREN", "DHRUMIL"]

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

        per_person_amount = round(85 * per_person_qty, 2)

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

    elif menu == "Records":

        st.subheader("📄 All Records")

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

                    "BIREN": "#00ff80",

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

    elif menu == "Chart":

        st.subheader("📊 Monthly Tiffin Orders Chart")

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

                colors = {"MEET": "#6B0848", "YASH": "#856C8B", "BIREN": "#C499F3", "DHRUMIL": "#DD5353"}

                color_list = [colors.get(name, "gray") for name in summary.index]

                fig, ax = plt.subplots()

                ax.pie(summary, labels=summary.index, autopct='%1.1f%%', colors=color_list, startangle=90)

                ax.set_title("📊 Monthly Tiffin Orders by User")

                st.pyplot(fig)



    # -------------------- Edit --------------------

    elif menu == "Edit":

        st.subheader("✏️ Edit Existing Record")

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

                tiffin_amount = round(85 * edit_qty, 2)

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

    elif menu == "Payment Method":

        st.subheader("💳 Update Payment Status")

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

                    st.error("❌ Start Date cannot be after End Date.")

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

    elif menu == "Download":

        st.subheader("📥 Download Records")

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

                st.error("❌ Start Date cannot be after End Date.")

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

    elif menu == "Delete":

        st.subheader("🗑️ Delete Records by Date")

        df = fetch_all()

        if df.empty:

            st.info("No records available to delete.")

        else:

            df['date'] = pd.to_datetime(df['date'], errors='coerce')

            min_date = df['date'].min().date() if not df['date'].isna().all() else datetime.date.today()

            max_date = df['date'].max().date() if not df['date'].isna().all() else datetime.date.today()

            from_date = st.date_input("From Date", value=min_date, key="delete_from")

            to_date = st.date_input("To Date", value=max_date, key="delete_to")

            if st.button("Delete Records"):

                if from_date > to_date:

                    st.error("❌ Start Date cannot be after End Date.")

                else:

                    # Generate all dates in range

                    date_range = pd.date_range(start=from_date, end=to_date).date

                    db_dates = set(df['date'].dropna().dt.date)

                    # Check if all dates in range exist in DB

                    if all(d in db_dates for d in date_range):

                        deleted_count = delete_records(from_date, to_date)

                        st.success(f"✅ {deleted_count} record(s) deleted from {from_date} to {to_date}.")

                    else:

                        st.warning("⚠️ Cannot delete: Some dates in the range do not exist in the records.")



    elif menu == "Account":

        account_page()

    elif menu == "Account Records":

        account_records_page()

    elif menu == "Edit Account Details":

        edit_account_page()


# -------------------- Run App --------------------

if __name__ == "__main__":
    app()
