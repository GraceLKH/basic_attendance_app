import streamlit as st
import pandas as pd
from datetime import datetime
import os

# File to store user info
USER_INFO_FILE = "user_info.csv"
ATTENDANCE_FILE = "attendance_log.csv"
ADMIN_PASSWORD = "admin123"  # Change this for security

# Initialize files
if not os.path.exists(USER_INFO_FILE):
    pd.DataFrame(columns=["Email", "Phone", "Name", "Gender", "Age", "Home Address"]).to_csv(USER_INFO_FILE, index=False)

if not os.path.exists(ATTENDANCE_FILE):
    pd.DataFrame(columns=["Email", "Phone", "Name", "Clock-In Date", "Clock-In Time"]).to_csv(ATTENDANCE_FILE, index=False)

# Load data
user_df = pd.read_csv(USER_INFO_FILE, dtype={"Phone": str})
attendance_df = pd.read_csv(ATTENDANCE_FILE, dtype={"Phone": str})

st.title("📌 Basic Attendance System")

# Sidebar Navigation
menu = st.sidebar.selectbox("Select Action", ["Register", "Clock In", "Admin Panel"])

# --- Register ---
if menu == "Register":
    st.header("📋 User Registration")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    name = st.text_input("Full Name")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    age = st.number_input("Age", min_value=0, max_value=120, step=1)
    address = st.text_area("Home Address (optional)")

    if st.button("Register"):
        if not email and not phone:
            st.error("Please enter at least Email or Phone.")
        else:
            # Check if user already exists by either identifier
            match = user_df[(user_df["Email"] == email) | (user_df["Phone"] == phone)]

            if not match.empty:
                # Update record
                idx = match.index[0]
                user_df.at[idx, "Email"] = email if email else user_df.at[idx, "Email"]
                user_df.at[idx, "Phone"] = phone if phone else user_df.at[idx, "Phone"]
                user_df.at[idx, "Name"] = name
                user_df.at[idx, "Gender"] = gender
                user_df.at[idx, "Age"] = age
                user_df.at[idx, "Home Address"] = address
                st.success("✅ User info updated.")
            else:
                # Append new user
                new_user = {
                    "Email": email,
                    "Phone": phone,
                    "Name": name,
                    "Gender": gender,
                    "Age": age,
                    "Home Address": address
                }
                user_df = pd.concat([user_df, pd.DataFrame([new_user])], ignore_index=True)
                st.success("✅ User registered successfully.")

            user_df.to_csv(USER_INFO_FILE, index=False)

# --- Clock In ---
elif menu == "Clock In":
    st.header("🕓 Clock In")

    identifier = st.text_input("Enter Email or Phone")

    if st.button("Clock In Now"):
        user = user_df[(user_df["Email"] == identifier) | (user_df["Phone"] == identifier)]

        if user.empty:
            st.error("❌ Identifier not found. Please register first.")
        else:
            now = datetime.now()
            current_date = now.strftime("%Y-%m-%d")
            current_time = now.strftime("%H:%M:%S")

            user_info = user.iloc[0]
            log = {
                "Email": user_info["Email"],
                "Phone": user_info["Phone"],
                "Name": user_info["Name"],
                "Clock-In Date": current_date,
                "Clock-In Time": current_time
            }

            attendance_df = pd.concat([attendance_df, pd.DataFrame([log])], ignore_index=True)
            attendance_df.to_csv(ATTENDANCE_FILE, index=False)
            st.success(f"✅ Clocked in at {current_time} on {current_date}.")

# --- Admin Panel ---
elif menu == "Admin Panel":
    st.header("🔒 Admin Panel")
    password = st.text_input("Enter Admin Password", type="password")

    if password == ADMIN_PASSWORD:
        st.success("🔓 Access granted.")

        st.subheader("📊 Attendance Records")
        st.dataframe(attendance_df)

        csv = attendance_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Attendance CSV", csv, "attendance.csv", "text/csv")
    else:
        if password:
            st.error("❌ Invalid password.")
