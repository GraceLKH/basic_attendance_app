import streamlit as st
import pandas as pd
import datetime
import os

DATA_FILE = "attendance_data.csv"
ADMIN_PASSWORD = "admin123"  # Change to your secure admin password


def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, dtype={"Phone": str})
    else:
        df = pd.DataFrame(columns=[
            "Email", "Phone", "Name", "Gender", "Age", "Home Address",
            "Clock In Date", "Clock In Time", "Used Biometric"
        ])
    return df


def save_data(df):
    df.to_csv(DATA_FILE, index=False)


def register_user(email, phone, name, gender, age, address):
    df = load_data()
    if not ((df['Email'] == email) | (df['Phone'] == phone)).any():
        new_user = pd.DataFrame([{
            "Email": email,
            "Phone": phone,
            "Name": name,
            "Gender": gender,
            "Age": age,
            "Home Address": address,
            "Clock In Date": "",  # No clock in yet
            "Clock In Time": "",
            "Used Biometric": ""
        }])
        df = pd.concat([df, new_user], ignore_index=True)
        save_data(df)
        st.success("✅ Registration successful!")
    else:
        st.warning("⚠️ User already registered.")


def clock_in(identifier, biometric_used):
    df = load_data()
    today = datetime.date.today().strftime("%Y-%m-%d")
    now_time = datetime.datetime.now().strftime("%H:%M:%S")

    user_idx = df[(df["Email"] == identifier) | (df["Phone"] == identifier)].index

    if not user_idx.empty:
        user_row = df.loc[user_idx[0]]

        # Check if already clocked in today
        if user_row["Clock In Date"] == today:
            st.info("ℹ️ You have already clocked in today.")
        else:
            df.at[user_idx[0], "Clock In Date"] = today
            df.at[user_idx[0], "Clock In Time"] = now_time
            df.at[user_idx[0], "Used Biometric"] = biometric_used
            save_data(df)
            st.success(f"✅ Clocked in at {now_time}")
    else:
        st.error("❌ Identifier not found. Please register first.")


def admin_panel():
    st.subheader("🔐 Admin Panel")
    password = st.text_input("Enter Admin Password", type="password")
    if password == ADMIN_PASSWORD:
        df = load_data()
        st.success("✅ Access granted.")
        st.dataframe(df)
        st.download_button("📥 Download Attendance CSV", df.to_csv(index=False), file_name="attendance.csv")
    else:
        if password:
            st.error("❌ Incorrect password")


# Streamlit UI
st.title("📋 Basic Attendance App")
menu = st.sidebar.selectbox("Menu", ["Register", "Clock In", "Admin"])

if menu == "Register":
    st.header("📝 Register")
    email = st.text_input("Email (optional but required if no phone)").strip()
    phone = st.text_input("Phone (optional but required if no email)").strip()
    name = st.text_input("Full Name")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    age = st.number_input("Age", min_value=1, max_value=100, step=1)
    address = st.text_area("Home Address (Optional)")

    if st.button("Register"):
        if email or phone:
            register_user(email, phone, name, gender, age, address)
        else:
            st.error("❌ Please provide at least Email or Phone.")

elif menu == "Clock In":
    st.header("⏰ Clock In")
    identifier = st.text_input("Enter your Email or Phone").strip()
    biometric = st.checkbox("Use Biometric (Fingerprint)?")

    if st.button("Clock In"):
        if identifier:
            clock_in(identifier, "Yes" if biometric else "No")
        else:
            st.error("❌ Please enter your Email or Phone.")

elif menu == "Admin":
    admin_panel()
