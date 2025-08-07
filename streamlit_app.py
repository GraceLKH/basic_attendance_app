import streamlit as st
import pandas as pd
import os
from datetime import datetime

# CSV file path
CSV_FILE = "attendance.csv"

# Load or create DataFrame
if os.path.exists(CSV_FILE):
    attendance_df = pd.read_csv(CSV_FILE, dtype=str)  # Load all columns as string
else:
    attendance_df = pd.DataFrame(columns=["Email", "Phone", "Name", "Gender", "Age", "Home Address", "Last Clock-In"])
    attendance_df.to_csv(CSV_FILE, index=False)

# Ensure all data is string type for consistent comparisons
attendance_df = attendance_df.astype(str)

# Save function
def save_data():
    attendance_df.to_csv(CSV_FILE, index=False)

# Register function
def register_user(email, phone, name, gender, age, address):
    global attendance_df

    if not email and not phone:
        st.error("❌ Please enter at least an Email or Phone number.")
        return

    # Normalize values
    email = email.strip()
    phone = phone.strip()

    # Check if user already exists by email or phone
    existing_idx = attendance_df[
        (attendance_df['Email'] == email) | (attendance_df['Phone'] == phone)
    ].index

    if not existing_idx.empty:
        # Update existing user
        attendance_df.loc[existing_idx[0], ["Email", "Phone", "Name", "Gender", "Age", "Home Address"]] = [
            email, phone, name, gender, age, address
        ]
        st.success("✅ User info updated.")
    else:
        # Append new user
        new_row = pd.DataFrame([{
            "Email": email,
            "Phone": phone,
            "Name": name,
            "Gender": gender,
            "Age": age,
            "Home Address": address,
            "Last Clock-In": ""
        }])
        attendance_df = pd.concat([attendance_df, new_row], ignore_index=True)
        st.success("✅ User registered successfully.")

    save_data()

# Clock-in function
def clock_in(identifier):
    global attendance_df
    identifier = identifier.strip()

    match = attendance_df[
        (attendance_df['Email'] == identifier) | (attendance_df['Phone'] == identifier)
    ]

    if not match.empty:
        idx = match.index[0]
        attendance_df.at[idx, "Last Clock-In"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_data()
        st.success(f"✅ Clock-in successful for {attendance_df.at[idx, 'Name']}.")
    else:
        st.error("❌ Identifier not found. Please register first.")

# Streamlit UI
st.title("📍 Basic Attendance App (Email/Phone)")

tab1, tab2 = st.tabs(["📋 Register", "🕓 Clock In"])

with tab1:
    st.subheader("Register New User")
    email = st.text_input("Email (optional but recommended)")
    phone = st.text_input("Phone (optional but recommended)")
    name = st.text_input("Name *")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    age = st.number_input("Age", min_value=0, max_value=120, step=1)
    address = st.text_area("Home Address (Optional)")

    if st.button("Register / Update"):
        if not name:
            st.error("❌ Name is required.")
        elif not email and not phone:
            st.error("❌ Please enter at least an Email or Phone number.")
        else:
            register_user(email, phone, name, gender, age, address)

with tab2:
    st.subheader("Clock In")
    identifier = st.text_input("Enter Email or Phone")
    if st.button("Clock In"):
        if not identifier:
            st.error("❌ Please enter your email or phone.")
        else:
            clock_in(identifier)

# Optional: View data
with st.expander("📄 View Attendance Data"):
    st.dataframe(attendance_df)
