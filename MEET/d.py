import streamlit as st
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import bcrypt
import base64
import json

# -------------------- Streamlit Config --------------------
st.set_page_config(
    page_title="MEET",
    page_icon="MEET/images.png",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.set_page_config(page_title="MEET", layout="wide")

# ----- Footer -----
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
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------- Global Styles --------------------
st.markdown("""
<style>
div.stButton > button {
    background-color: red;
    color: white;
    border-radius: 5px;
    height: 3em;
    width: 100%;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
body, .block-container, .stApp {
    background-color: #0e1117 !important;
    color: #FFFFFF !important;
    font-weight: bold !important;
}
.css-1d391kg {background-color: #0e1117 !important;}
h1, h2, h3, h4, h5, h6, p, textarea, label {color: #FFFFFF !important; font-weight: bold !important;}
.dataframe, table {color: #FFFFFF !important; background-color: #1c1f26 !important; font-weight: bold !important;}
</style>
""", unsafe_allow_html=True)

# -------------------- Login --------------------
# Hashed credentials (no .env needed)
LOGIN_USER_HASH = b"$2b$12$BLSiegHi9JZpmhFKKGnODu5SNS9Obqswd4GTcHiuUQ3iYZ0pzSlM2"
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

# -------------------- Excel Setup --------------------
EXCEL_FILE = r"C:\TIFIN SERVICE\TIFIN\t1.xlsx"
HEADERS = ["Date", "Time", "Name", "Shift", "Quantity", "Roti", "Roti Amount", "Amount", "Payment Status"]

def get_data(file_path=EXCEL_FILE):
    try:
        df = pd.read_excel(file_path)
        for col in HEADERS:
            if col not in df.columns:
                df[col] = 0 if col in ['Quantity', 'Roti', 'Roti Amount', 'Amount'] else "EMPTY"
        return df
    except FileNotFoundError:
        df = pd.DataFrame(columns=HEADERS)
        df.to_excel(file_path, index=False)
        return df

def save_data(df, file_path=EXCEL_FILE):
    df.to_excel(file_path, index=False)

# -------------------- Sidebar Logo --------------------
st.sidebar.markdown("""
<style>
.sidebar .sidebar-content {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 100vh;
}
.sidebar .sidebar-content div:last-child { margin-top: auto; }
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("<div></div>", unsafe_allow_html=True)

# -------------------- Main App --------------------
def app():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        login()
        return

    st.title("📊 Tiffin Tracker System")
    menu = st.sidebar.selectbox("Menu", ["Add Record", "Records", "Chart", "Edit", "Payment Method", "Download Excel"])

    # -------------------- Add Record --------------------
    if menu == "Add Record":
        st.subheader("➕ Add New Record")
        today = datetime.date.today().strftime("%Y-%m-%d")
        current_time = datetime.datetime.now().strftime("%H:%M:%S")

        shift = st.selectbox("Select Shift", ["-- SELECT DAY --", "Day", "Night"])
        if shift == "-- SELECT DAY --":
            st.warning("Please select a shift")
            st.stop()

        tiffin_qty = st.selectbox("Select Tiffin Quantity", ["-- SELECT Quantity --"] + [1,2,3,4,5,6])
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
                st.write(f"{name}: Qty = {per_person_qty:.2f}, Amount = ₹{per_person_amount:.2f}, Roti = {roti_qty.get(name,0)}")
            else:
                st.write(f"{name}: No Tiffin Today → Qty = 0.00, Amount = 0.00, Roti = 0")

        total_tiffin_amount = round(per_person_amount * len(selected_names),2)
        total_roti_amount = round(sum([roti_qty.get(name,0)*roti_rate for name in selected_names]),2)
        total_amount = total_tiffin_amount + total_roti_amount

        st.markdown(f"### 💰 Total Tiffin Amount: ₹{total_tiffin_amount:.2f}")
        if shift == "Day":
            st.markdown(f"### 💰 Total Roti Amount: ₹{total_roti_amount:.2f}")
        st.markdown(f"### 🏆 Final Total Amount: ₹{total_amount:.2f}")

        if st.button("Save Record"):
            df = get_data()
            for name in names:
                if name in selected_names:
                    qty = per_person_qty
                    amount = per_person_amount
                else:
                    qty = 0.00
                    amount = 0.00
                roti = roti_qty.get(name,0)
                roti_amount = roti * roti_rate
                total_individual_amount = round(amount + roti_amount,2)
                new_row = [today, current_time, name, shift, qty, roti, roti_amount, total_individual_amount, "Payment Pending"]
                df.loc[len(df)] = new_row
            save_data(df)
            st.success("Record(s) added successfully!")

    # -------------------- Records --------------------
    elif menu == "Records":
        st.subheader("📄 All Records")

        table_placeholder = st.empty()
        df = get_data()
        if df.empty:
            st.info("No records available")
            table_placeholder.dataframe(pd.DataFrame(columns=HEADERS))
        else:
            df_reset = df.reset_index(drop=True)
            df_reset.index += 1

            def color_name(val):
                color_map = {
                    "MEET": "#FE7743",
                    "YASH": "#D76C82",
                    "BIREN": "#FFD36E",
                    "DHRUMIL": "#9EDE73"
                }
                return f"color: {color_map.get(val, 'black')}"

            def color_payment(val):
                if str(val).strip().lower() == "payment pending":
                    return "color: #FFE100"
                elif str(val).strip().lower() == "payment done":
                    return "color: #56DFCF"
                return "color: black"

            styled_df = (
                df_reset
                .style
                .applymap(color_name, subset=["Name"])
                .applymap(color_payment, subset=["Payment Status"])
                .format(precision=1)
            )
            table_placeholder.dataframe(styled_df)

        if st.button("🔄 Refresh Data"):
            df = get_data()
            if df.empty:
                st.info("No records available")
                table_placeholder.dataframe(pd.DataFrame(columns=HEADERS))
            else:
                df_reset = df.reset_index(drop=True)
                df_reset.index += 1
                styled_df = (
                    df_reset
                    .style
                    .applymap(color_name, subset=["Name"])
                    .applymap(color_payment, subset=["Payment Status"])
                    .format(precision=1)
                )
                table_placeholder.dataframe(styled_df)
            st.success("Data refreshed ✅")

    # -------------------- Chart --------------------
    elif menu == "Chart":
        st.subheader("📊 Monthly Tiffin Orders Chart")
        df = get_data()
        if df.empty:
            st.info("No records to plot.")
        else:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            today_dt = datetime.date.today()
            current_month_df = df[(df['Date'].dt.month == today_dt.month) & (df['Date'].dt.year == today_dt.year)]
            if current_month_df.empty:
                st.info("No orders found for this month.")
            else:
                summary_df = current_month_df.groupby('Name').agg({"Quantity":"sum","Amount":"sum"}).reset_index()
                st.markdown("### 📝 Summary of This Month")
                st.dataframe(summary_df)
                summary = summary_df.set_index('Name')['Quantity']
                colors = {"MEET":"#6B0848","YASH":"#856C8B","BIREN":"#C499F3","DHRUMIL":"#DD5353"}
                color_list = [colors.get(name,"gray") for name in summary.index]
                fig, ax = plt.subplots()
                ax.pie(summary, labels=summary.index, autopct='%1.1f%%', colors=color_list, startangle=90)
                ax.set_title("📊 Monthly Tiffin Orders by User")
                st.pyplot(fig)

    # -------------------- Edit --------------------
    elif menu == "Edit":
        st.subheader("✏️ Edit Existing Record")
        df = get_data()

        if df.empty:
            st.info("No records to edit.")
        else:
            df_reset = df.reset_index(drop=True)
            df_reset.index += 1

            def color_name(val):
                color_map = {"MEET": "#FE7743","YASH": "#D76C82","BIREN": "#FFD36E","DHRUMIL": "#9EDE73"}
                return f"color: {color_map.get(val, 'black')}"

            def color_payment(val):
                if str(val).strip().lower() == "payment pending":
                    return "color: #FFE100"
                elif str(val).strip().lower() == "payment done":
                    return "color: #56DFCF"
                return "color: black"

            styled_df = df_reset.style.applymap(color_name, subset=["Name"]).applymap(color_payment, subset=["Payment Status"])
            table_placeholder = st.empty()
            table_placeholder.dataframe(styled_df)

            if st.button("🔄 Refresh Data"):
                df = get_data()
                df_reset = df.reset_index(drop=True)
                df_reset.index += 1
                styled_df = df_reset.style.applymap(color_name, subset=["Name"]).applymap(color_payment, subset=["Payment Status"])
                table_placeholder.dataframe(styled_df)
                st.success("Data refreshed ✅")

            col1, col2, col3 = st.columns([1, 2, 2])
            sr_no = col1.number_input("Enter Sr No", min_value=1, max_value=len(df_reset), step=1)
            name_edit = col2.selectbox("Select Name", ["-- SELECT --"] + ["MEET", "YASH", "BIREN", "DHRUMIL"])
            date_edit = col3.date_input("Select Date")

            if st.button("Load Record"):
                if name_edit == "-- SELECT --":
                    st.error("Please select Name")
                else:
                    df_row = df_reset.iloc[sr_no - 1]
                    if pd.to_datetime(df_row['Date']).date() != date_edit or df_row['Name'] != name_edit:
                        st.error("Date or Name does not match the selected row")
                    else:
                        st.session_state['edit_row_index'] = sr_no - 1
                        st.session_state['edit_values'] = df_row.to_dict()
                        st.success("Record loaded. You can now edit fields below.")

            if 'edit_values' in st.session_state:
                values = st.session_state['edit_values']
                edit_shift = st.selectbox("Shift", ["Day", "Night"], index=["Day", "Night"].index(values['Shift']))
                edit_qty = st.number_input("Quantity", min_value=0.0, value=float(values['Quantity']))
                edit_roti = st.number_input("Roti Quantity", min_value=0, value=int(values['Roti']))

                roti_amount = edit_roti * 5
                tiffin_amount = round(85 * edit_qty, 2)
                final_amount = tiffin_amount + roti_amount if edit_shift == "Day" else tiffin_amount
                st.info(f"💰 Final Amount: ₹{final_amount}")

                if st.button("Save Changes"):
                    df.loc[st.session_state['edit_row_index']] = [
                        values['Date'], values['Time'], values['Name'],
                        edit_shift, edit_qty, edit_roti, roti_amount, final_amount,
                        values.get("Payment Status", "Payment Pending")
                    ]
                    save_data(df)
                    st.success("Record updated successfully!")
                    del st.session_state['edit_values']
                    del st.session_state['edit_row_index']
                    df_reset = df.reset_index(drop=True)
                    df_reset.index += 1
                    table_placeholder.dataframe(df_reset)

    # -------------------- Payment Method --------------------
    elif menu == "Payment Method":
        st.subheader("💳 Update Payment Status")
        df = get_data()
        if df.empty:
            st.info("No records available.")
        else:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            min_date = df['Date'].min().date() if not df['Date'].isna().all() else datetime.date.today()
            max_date = df['Date'].max().date() if not df['Date'].isna().all() else datetime.date.today()
            start_date = st.date_input("Start Date", value=min_date)
            end_date = st.date_input("End Date", value=max_date)
            selected_payment = st.selectbox("Payment Status to Update", ["-- SELECT --","Payment Pending","Payment Done"])
            if st.button("Update Payments"):
                if selected_payment != "-- SELECT --":
                    mask = (df['Date'].dt.date>=start_date)&(df['Date'].dt.date<=end_date)
                    df.loc[mask,'Payment Status'] = selected_payment
                    save_data(df)
                    st.success(f"{mask.sum()} record(s) updated.")

    # -------------------- Download Excel --------------------
    elif menu == "Download Excel":
        st.subheader("💾 Download Excel File")
        with open(EXCEL_FILE,"rb") as f:
            st.download_button(
                label="Download Excel",
                data=f,
                file_name="t1.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# -------------------- Run App --------------------
if __name__=="__main__":
    app()



