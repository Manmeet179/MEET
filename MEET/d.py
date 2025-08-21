import streamlit as st
from datetime import datetime, date
import pandas as pd
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
import bcrypt

# -------------------- Page Config --------------------
st.set_page_config(
    page_title="MEET",
    page_icon="logo/images.png",
    layout="centered",
    initial_sidebar_state="expanded"
)

# -------------------- Hide Streamlit Menu & Footer --------------------
st.markdown("""
<style>
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
div.stButton > button {
    background-color: #FF4B4B !important;
    color: white !important;
    font-weight: bold !important;
    border-radius: 5px;
    height: 3em;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# -------------------- Load Environment Variables --------------------
load_dotenv()
LOGIN_USER_HASH = os.getenv("LOGIN_USER").encode('utf-8')
LOGIN_PASS_HASH = os.getenv("LOGIN_PASS").encode('utf-8')

# -------------------- Login Function --------------------
def login():
    st.title("🍱 Tiffin Tracker - Login")
    username = st.text_input("Username", key="user")
    password = st.text_input("Password", type="password", key="pass")

    if st.button("Login"):
        if bcrypt.checkpw(username.encode('utf-8'), LOGIN_USER_HASH) and bcrypt.checkpw(password.encode('utf-8'), LOGIN_PASS_HASH):
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

st.sidebar.image("logo/images.png", use_container_width=True)

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
        today = date.today().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")

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
        selected_names = [name for i, name in enumerate(names) if cols[i].checkbox(name)]

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
                qty = per_person_qty if name in selected_names else 0.0
                amount = per_person_amount if name in selected_names else 0.0
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
        df = get_data()
        if df.empty:
            st.info("No records available")
            st.dataframe(pd.DataFrame(columns=HEADERS))
        else:
            df_reset = df.reset_index(drop=True)
            df_reset.index += 1
            st.dataframe(df_reset)

    # -------------------- Chart --------------------
    elif menu == "Chart":
        st.subheader("📊 Monthly Tiffin Orders Chart")
        df = get_data()
        if df.empty:
            st.info("No records to plot.")
        else:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            today_dt = date.today()
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
