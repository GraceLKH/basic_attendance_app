import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Biometric Attendance App", layout="centered")

# --- Initialize CSV files if they don't exist ---
if not os.path.exists("users.csv"):
    pd.DataFrame(columns=["Email", "Phone", "Name", "Org"]).to_csv("users.csv", index=False)

if not os.path.exists("attendance.csv"):
    pd.DataFrame(columns=["Email", "Phone", "Name", "Clock In Time", "Clock In Date", "Org", "Biometric Used"]).to_csv("attendance.csv", index=False)

# --- Load users ---
def load_users():
    return pd.read_csv("users.csv")

# --- Save user profile ---
def save_user_profile(email, phone, name, org):
    users = load_users()
    if ((users['Email'] == email) | (users['Phone'] == phone)).any():
        st.warning("User already exists with this email or phone.")
    else:
        new_user = pd.DataFrame([[email, phone, name, org]], columns=["Email", "Phone", "Name", "Org"])
        new_user.to_csv("users.csv", mode='a', header=False, index=False)
        st.success("User profile saved successfully!")

# --- Clock in user ---
def clock_in_user(email, phone, biometric_used):
    users = load_users()

    match = users[(users['Email'] == email) | (users['Phone'] == phone)]
    if match.empty:
        st.error("User does not exist. Please register first.")
        return

    name = match.iloc[0]['Name']
    org = match.iloc[0]['Org']

    now = datetime.now()
    new_record = pd.DataFrame([[email, phone, name, now.strftime("%H:%M:%S"), now.strftime("%Y-%m-%d"), org, biometric_used]],
                              columns=["Email", "Phone", "Name", "Clock In Time", "Clock In Date", "Org", "Biometric Used"])
    new_record.to_csv("attendance.csv", mode='a', header=False, index=False)
    st.success(f"{name} clocked in at {now.strftime('%H:%M:%S')} on {now.strftime('%Y-%m-%d')} under {org}.")

# --- Admin View ---
def admin_view(org):
    st.subheader(f"Admin Panel - Organization: {org}")

    if not os.path.exists("attendance.csv"):
        st.warning("No attendance records found.")
        return

    attendance = pd.read_csv("attendance.csv")

    if "Org" not in attendance.columns:
        st.warning("Attendance data does not contain organization information.")
        return

    org_attendance = attendance[attendance["Org"] == org]

    if org_attendance.empty:
        st.info("No attendance records for your organization yet.")
        return

    st.dataframe(org_attendance)

    csv = org_attendance.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, f"{org}_attendance.csv", "text/csv")

# --- Main App ---
st.title("Biometric Attendance System")

menu = st.sidebar.selectbox("Choose Option", ["Register", "Clock In", "Admin View"])

# --- Register Page ---
if menu == "Register":
    st.subheader("Register New User")
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    org = st.text_input("Organization Name")

    if st.button("Register"):
        if name and (email or phone) and org:
            save_user_profile(email, phone, name, org)
        else:
            st.warning("Please fill in all required fields.")

# --- Clock In Page ---
elif menu == "Clock In":
    st.subheader("Clock In")
    use_biometric = st.checkbox("Simulate Biometric Authentication")

    if use_biometric:
        st.info("Biometric data recognized. Auto-filling user profile...")
        users = load_users()
        if not users.empty:
            selected_user = st.selectbox("Select your profile", users['Name'])
            user_info = users[users['Name'] == selected_user].iloc[0]
            email = user_info['Email']
            phone = user_info['Phone']
            biometric_used = True

            if st.button("Clock In"):
                clock_in_user(email, phone, biometric_used)
        else:
            st.warning("No registered users found.")
    else:
        st.info("Manual clock in")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        biometric_used = False

        if st.button("Clock In"):
            if email or phone:
                clock_in_user(email, phone, biometric_used)
            else:
                st.warning("Enter at least Email or Phone to clock in.")

# --- Admin View Page ---
elif menu == "Admin View":
    st.subheader("Admin Panel")
    org = st.text_input("Enter your organization name to view attendance")

    if st.button("View Attendance"):
        if org:
            admin_view(org)
        else:
            st.warning("Enter organization name.")
