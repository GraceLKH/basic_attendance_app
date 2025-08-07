import streamlit as st
import pandas as pd
import os
from datetime import datetime

# File to store registered users
USER_DATA_FILE = 'users.csv'

# Today's date for attendance
today = datetime.now().strftime('%Y%m%d')
ATTENDANCE_FILE = f'attendance_{today}.csv'

# Ensure user and attendance files exist with proper headers
if not os.path.exists(USER_DATA_FILE):
    pd.DataFrame(columns=["Email", "Phone", "Name", "Gender", "Age", "Home Address"]).to_csv(USER_DATA_FILE, index=False)

if not os.path.exists(ATTENDANCE_FILE):
    pd.DataFrame(columns=["Email/Phone", "Name", "Clock-in Time"]).to_csv(ATTENDANCE_FILE, index=False)

# Load existing data
users_df = pd.read_csv(USER_DATA_FILE)
attendance_df = pd.read_csv(ATTENDANCE_FILE)

st.title("📌 Biometric-Style Attendance App (Email or Phone Clock-in)")

# Choose between Register or Clock In
mode = st.radio("Choose Mode", ["Register (First Time or Update)", "Clock In"])

if mode == "Register (First Time or Update)":
    st.subheader("🔐 Register or Update Your Info")
    name = st.text_input("Full Name")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    age = st.number_input("Age", min_value=1, max_value=100, step=1)
    phone = st.text_input("Phone Number (Required)")
    email = st.text_input("Email Address (Optional)")
    address = st.text_area("Home Address (Optional)")

    if st.button("Register / Update"):
        if not name or not phone:
            st.warning("Full Name and Phone Number are required.")
        else:
            updated = False
            index = None

            # Check if phone or email already exists
            if phone in users_df["Phone"].values:
                index = users_df[users_df["Phone"] == phone].index[0]
                updated = True
            elif email and email in users_df["Email"].values:
                index = users_df[users_df["Email"] == email].index[0]
                updated = True

            new_data = {"Email": email, "Phone": phone, "Name": name, "Gender": gender, "Age": age, "Home Address": address}

            if updated:
                for col, val in new_data.items():
                    users_df.at[index, col] = val
                users_df.to_csv(USER_DATA_FILE, index=False)
                st.success("🔁 Information updated successfully.")
            else:
                new_user = pd.DataFrame([new_data])
                new_user.to_csv(USER_DATA_FILE, mode='a', header=False, index=False)
                st.success("✅ Registration successful. You can now clock in using your email or phone.")

elif mode == "Clock In":
    st.subheader("⏰ Clock In")
    identifier = st.text_input("Enter your registered Email or Phone Number")

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

# Admin View
st.markdown("---")
if st.checkbox("🔒 Admin Access: View Today's Attendance"):
    admin_password = st.text_input("Enter admin password", type="password")
    if admin_password == "admin123":
        st.success("Admin access granted.")
        st.dataframe(pd.read_csv(ATTENDANCE_FILE))
    elif admin_password:
        st.error("Access denied.")
