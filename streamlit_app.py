import streamlit as st
import pandas as pd
import datetime
import os
import base64

# File to store user registration
USER_DATA_FILE = "users.csv"
ATTENDANCE_LOG_FILE = "attendance_log.csv"

# Ensure files exist
if not os.path.exists(USER_DATA_FILE):
    pd.DataFrame(columns=["Email", "Phone", "Name", "Gender", "Age", "Home Address"]).to_csv(USER_DATA_FILE, index=False)

if not os.path.exists(ATTENDANCE_LOG_FILE):
    pd.DataFrame(columns=["Identifier", "Name", "Clock In Time", "Date", "Biometric"]).to_csv(ATTENDANCE_LOG_FILE, index=False)

# Load user data
user_df = pd.read_csv(USER_DATA_FILE, dtype={"Phone": str})
attendance_df = pd.read_csv(ATTENDANCE_LOG_FILE, dtype={"Identifier": str})

# Title
st.title("📋 Biometric Attendance System")

menu = st.sidebar.selectbox("Select Action", ["Register", "Clock In", "Admin Panel"])

# ------------------------------------
# 🔹 1. REGISTER
# ------------------------------------
if menu == "Register":
    st.header("📝 User Registration")
    with st.form("register_form"):
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        name = st.text_input("Full Name")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        age = st.number_input("Age", min_value=1, step=1)
        address = st.text_area("Home Address (optional)")
        submitted = st.form_submit_button("Register")

    if submitted:
        if not email and not phone:
            st.error("❌ Please provide either Email or Phone number.")
        else:
            identifier = email if email else phone
            if ((user_df['Email'] == email) | (user_df['Phone'] == phone)).any():
                st.warning("⚠️ Email or phone already registered.")
            else:
                new_user = pd.DataFrame([{
                    "Email": email,
                    "Phone": phone,
                    "Name": name,
                    "Gender": gender,
                    "Age": age,
                    "Home Address": address
                }])
                user_df = pd.concat([user_df, new_user], ignore_index=True)
                user_df.to_csv(USER_DATA_FILE, index=False)
                st.success("✅ Registration successful!")

# ------------------------------------
# 🔹 2. CLOCK IN
# ------------------------------------
elif menu == "Clock In":
    st.header("⏰ Daily Clock-In")
    identifier_input = st.text_input("Enter your Email or Phone to Clock In")
    photo = st.camera_input("📷 Capture Biometric Photo (Required)")

    if st.button("Clock In"):
        if not identifier_input:
            st.error("❌ Please enter Email or Phone.")
        elif photo is None:
            st.error("❌ Please capture biometric photo.")
        else:
            # Match user
            matched = user_df[(user_df["Email"] == identifier_input) | (user_df["Phone"] == identifier_input)]
            if matched.empty:
                st.error("❌ Identifier not found. Please register first.")
            else:
                today = datetime.date.today().strftime("%Y-%m-%d")
                already_clocked = attendance_df[
                    (attendance_df["Identifier"] == identifier_input) &
                    (attendance_df["Date"] == today)
                ]
                if not already_clocked.empty:
                    st.warning("⚠️ Already clocked in today.")
                else:
                    clock_in_time = datetime.datetime.now().strftime("%H:%M:%S")
                    biometric_b64 = base64.b64encode(photo.getvalue()).decode('utf-8')

                    attendance_df = pd.concat([attendance_df, pd.DataFrame([{
                        "Identifier": identifier_input,
                        "Name": matched.iloc[0]["Name"],
                        "Clock In Time": clock_in_time,
                        "Date": today,
                        "Biometric": biometric_b64
                    }])], ignore_index=True)

                    attendance_df.to_csv(ATTENDANCE_LOG_FILE, index=False)
                    st.success("✅ Clock-in successful!")

# ------------------------------------
# 🔹 3. ADMIN PANEL
# ------------------------------------
elif menu == "Admin Panel":
    st.header("🔐 Admin Panel")
    admin_password = st.text_input("Enter Admin Password", type="password")
    
    if admin_password == "admin123":  # Change this to a secure password
        st.success("✅ Access granted.")
        st.subheader("📅 Attendance Records")

        attendance_df = pd.read_csv(ATTENDANCE_LOG_FILE, dtype={"Identifier": str})
        st.dataframe(attendance_df)

        csv = attendance_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Attendance CSV", data=csv, file_name="attendance_log.csv", mime="text/csv")
    elif admin_password:
        st.error("❌ Incorrect password.")
