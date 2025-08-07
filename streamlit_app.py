import streamlit as st
import pandas as pd
import os
from datetime import datetime

# File to store registered users
USER_DATA_FILE = 'users.csv'

# Get today’s date for attendance
today = datetime.now().strftime('%Y%m%d')
ATTENDANCE_FILE = f'attendance_{today}.csv'

# Initialize user and attendance data
if not os.path.exists(USER_DATA_FILE):
    pd.DataFrame(columns=["Email", "Phone", "Name", "Gender", "Age", "Home Address"]).to_csv(USER_DATA_FILE, index=False)

if not os.path.exists(ATTENDANCE_FILE):
    pd.DataFrame(columns=["Email/Phone", "Name", "Clock-in Time"]).to_csv(ATTENDANCE_FILE, index=False)

# Load existing data
users_df = pd.read_csv(USER_DATA_FILE)
attendance_df = pd.read_csv(ATTENDANCE_FILE)

st.title("📌 Basic Attendance App (Email or Phone)")

# Choose between register or clock-in
mode = st.radio("Choose Mode", ["Register (First Time)", "Clock In"])

if mode == "Register (First Time)":
    st.subheader("🔐 Register Your Info")
    name = st.text_input("Full Name")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    age = st.number_input("Age", min_value=1, max_value=100, step=1)
    email = st.text_input("Email Address (Optional)")
    phone = st.text_input("Phone Number (Optional)")
    address = st.text_area("Home Address (Optional)")

    if st.button("Register"):
        if not email and not phone:
            st.warning("You must provide at least an Email or Phone Number.")
        elif (email in users_df["Email"].values) or (phone in users_df["Phone"].values):
            st.warning("This Email or Phone is already registered.")
        else:
            new_user = pd.DataFrame([[email, phone, name, gender, age, address]], columns=users_df.columns)
            new_user.to_csv(USER_DATA_FILE, mode='a', header=False, index=False)
            st.success("✅ Registration successful. You can now clock in using your Email or Phone.")

elif mode == "Clock In":
    st.subheader("⏰ Clock In")
    identifier = st.text_input("Enter your registered Email or Phone")

    if st.button("Clock In"):
        user_row = users_df[(users_df["Email"] == identifier) | (users_df["Phone"] == identifier)]

        if user_row.empty:
            st.error("❌ Identifier not found. Please register first.")
        elif identifier in attendance_df["Email/Phone"].values:
            st.info("✅ You already clocked in today.")
        else:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            name = user_row.iloc[0]["Name"]
            new_entry = pd.DataFrame([[identifier, name, now]], columns=attendance_df.columns)
            new_entry.to_csv(ATTENDANCE_FILE, mode='a', header=False, index=False)
            st.success(f"✅ Clock-in recorded at {now}")

# Admin Section
st.markdown("---")
if st.checkbox("🔒 Admin Access: View Today's Attendance"):
    admin_password = st.text_input("Enter admin password", type="password")
    if admin_password == "admin123":  # Change this securely in production
        st.success("Admin access granted.")
        st.dataframe(pd.read_csv(ATTENDANCE_FILE))
    elif admin_password:
        st.error("Access denied.")
