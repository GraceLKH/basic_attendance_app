import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ---------- File Configuration ----------
USER_DATA_FILE = 'users.csv'
today = datetime.now().strftime('%Y%m%d')
ATTENDANCE_FILE = f'attendance_{today}.csv'

# ---------- Initialize Data Files ----------
if not os.path.exists(USER_DATA_FILE):
    pd.DataFrame(columns=["Email", "Name", "Gender", "Age", "Phone", "Home Address"]).to_csv(USER_DATA_FILE, index=False)

if not os.path.exists(ATTENDANCE_FILE):
    pd.DataFrame(columns=["Email", "Name", "Clock-in Time"]).to_csv(ATTENDANCE_FILE, index=False)

# ---------- Load Data ----------
users_df = pd.read_csv(USER_DATA_FILE)
attendance_df = pd.read_csv(ATTENDANCE_FILE)

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Biometric Attendance App", layout="centered")
st.title("📌 Biometric-Style Attendance Clock-in App (Email Only)")

mode = st.radio("Choose Mode", ["Register (First Time)", "Clock In"])

# ---------- Registration ----------
if mode == "Register (First Time)":
    st.subheader("🔐 Register Your Info")
    name = st.text_input("Full Name")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    age = st.number_input("Age", min_value=1, max_value=100, step=1)
    phone = st.text_input("Phone Number (Optional)")
    email = st.text_input("Email Address (Required)")
    address = st.text_area("Home Address (Optional)")

    if st.button("Register"):
        if not name or not email:
            st.warning("⚠️ Name and Email are required.")
        elif email in users_df["Email"].values:
            st.warning("⚠️ This email is already registered.")
        else:
            new_user = pd.DataFrame([[email, name, gender, age, phone, address]],
                                    columns=users_df.columns)
            new_user.to_csv(USER_DATA_FILE, mode='a', header=False, index=False)
            st.success("✅ Registration successful. You can now clock in using your email.")

# ---------- Clock In ----------
elif mode == "Clock In":
    st.subheader("⏰ Clock In")
    email = st.text_input("Enter your registered Email")

    if st.button("Clock In"):
        user_row = users_df[users_df["Email"] == email]

        if user_row.empty:
            st.error("❌ Email not found. Please register first.")
        elif email in attendance_df["Email"].values:
            st.info("✅ You already clocked in today.")
        else:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            name = user_row.iloc[0]["Name"]
            new_entry = pd.DataFrame([[email, name, now]], columns=attendance_df.columns)
            new_entry.to_csv(ATTENDANCE_FILE, mode='a', header=False, index=False)
            st.success(f"✅ Clock-in recorded at {now}")

# ---------- Admin Panel ----------
st.markdown("---")
if st.checkbox("🔒 Admin Access: View Today's Attendance"):
    admin_password = st.text_input("Enter admin password", type="password")
    if admin_password == "admin123":  # You can change this password
        st.success("🔓 Access granted.")
        st.dataframe(pd.read_csv(ATTENDANCE_FILE))
    elif admin_password:
        st.error("❌ Incorrect password.")
