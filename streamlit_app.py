import streamlit as st
import pandas as pd
from datetime import datetime

# Initialize session state
if 'users' not in st.session_state:
    st.session_state.users = pd.DataFrame(columns=["Email", "Phone", "Name", "Gender", "Age", "Home Address", "Org", "Role"])
if 'attendance' not in st.session_state:
    st.session_state.attendance = pd.DataFrame(columns=["Email/Phone", "Name", "Org", "Clock In Date", "Time", "Biometric Used"])

# Helper functions
def get_user(identifier):
    users = st.session_state.users
    return users[(users['Email'] == identifier) | (users['Phone'] == identifier)]

def get_user_org(identifier):
    user = get_user(identifier)
    return user['Org'].values[0] if not user.empty else None

def register_user(email, phone, name, gender, age, address, org, role):
    if not email and not phone:
        st.error("Please provide at least Email or Phone.")
        return

    if get_user(email).empty and get_user(phone).empty:
        new_row = {
            "Email": email,
            "Phone": str(phone),
            "Name": name,
            "Gender": gender,
            "Age": age,
            "Home Address": address,
            "Org": org,
            "Role": role
        }
        st.session_state.users = pd.concat([st.session_state.users, pd.DataFrame([new_row])], ignore_index=True)
        st.success("User registered successfully.")
    else:
        st.warning("User already exists.")

def clock_in_user(identifier, org, biometric_used):
    users = st.session_state.users
    attendance = st.session_state.attendance
    user = get_user(identifier)

    if user.empty:
        st.error("❌ Identifier not found. Please register first.")
        return

    # Normalize the identifier for consistent matching and logging
    user_email = user['Email'].values[0]
    user_phone = user['Phone'].values[0]
    user_name = user['Name'].values[0]
    user_org = user['Org'].values[0]
    today = datetime.today().date()

    # Prefer email if available, else phone
    normalized_id = user_email if user_email else user_phone

    existing = attendance[
        (attendance['Email/Phone'] == normalized_id) &
        (attendance['Clock In Date'] == str(today)) &
        (attendance['Org'] == user_org)
    ]

    if not existing.empty:
        st.info("You have already clocked in today.")
        return

    new_row = {
        "Email/Phone": normalized_id,
        "Name": user_name,
        "Org": user_org,
        "Clock In Date": str(today),
        "Time": datetime.now().strftime("%H:%M:%S"),
        "Biometric Used": biometric_used
    }

    st.session_state.attendance = pd.concat([st.session_state.attendance, pd.DataFrame([new_row])], ignore_index=True)
    st.success("✅ Clocked in successfully.")

def admin_view(identifier):
    users = st.session_state.users
    attendance = st.session_state.attendance
    admin_user = get_user(identifier)

    if admin_user.empty or admin_user["Role"].values[0] != "admin":
        st.error("Access denied. Admin only.")
        return

    org = admin_user["Org"].values[0]
    org_attendance = attendance[attendance["Org"] == org]

    st.subheader(f"⏱️Attendance Records for {org}")
    st.dataframe(org_attendance)

    csv = org_attendance.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, f"{org}_attendance.csv", "text/csv")

# Streamlit UI
st.title("⏱️ Attendance App")

menu = st.sidebar.selectbox("Menu", ["Register", "Clock In", "Admin View", "Create Organization"])

# Create Organization (Admin)
if menu == "Create Organization":
    st.subheader("👨‍💼 Create Organization")
    st.info("This section is for admin to create organizations and register themselves.")

    email = st.text_input("Email (Either Email or Phone required)")
    phone = st.text_input("Phone (Either Email or Phone required)")
    name = st.text_input("Admin Name")
    gender = st.selectbox("Gender", ["Male", "Female"])
    age = st.number_input("Age", min_value=18, max_value=100)
    address = st.text_input("Home Address (Optional)")
    org = st.text_input("New Organization Name")

    if st.button("Create Organization"):
        if org:
            register_user(email, phone, name, gender, age, address, org, "admin")
        else:
            st.warning("Organization name is required.")

# User Registration
if menu == "Register":
    st.subheader("📝 User Registration")
    email = st.text_input("Email (Either Email or Phone required)")
    phone = st.text_input("Phone (Either Email or Phone required)")
    name = st.text_input("Full Name")
    gender = st.selectbox("Gender", ["Male", "Female"])
    age = st.number_input("Age", min_value=10, max_value=100)
    address = st.text_input("Home Address (Optional)")
    orgs = st.session_state.users['Org'].unique().tolist()
    org = st.selectbox("Select Organization", orgs)

    if st.button("Register"):
        register_user(email, phone, name, gender, age, address, org, "user")

# Clock In
if menu == "Clock In":
    st.subheader("⏱️ Clock In")
    st.info("You only need to enter either Email or Phone.")

    # Check if user wants to auto-use saved profile
    use_saved = st.checkbox("Use saved profile")
    id_input = ""
    org = None

    if use_saved and "last_user" in st.session_state:
        last = st.session_state.last_user
        id_input = last.get("Email") or last.get("Phone")
        org = last.get("Org")
        st.success(f"Welcome back, {last.get('Name')} from {org}")
    else:
        id_input = st.text_input("Email or Phone")
        org = get_user_org(id_input)
        if not org:
            orgs = st.session_state.users['Org'].unique().tolist()
            if orgs:
                org = st.selectbox("Select Organization", orgs)
            else:
                st.warning("No organizations found. Please register first.")

    remember_me = st.checkbox("Remember Me for future clock-ins", value=True)
    biometric_used = "Yes" if use_saved else "No"

    if st.button("Clock In"):
        if id_input:
            clock_in_user(id_input, org, biometric_used)

            # Save preference if enabled
            user_row = get_user(id_input)
            if remember_me and not user_row.empty:
                st.session_state.last_user = user_row.iloc[0].to_dict()
        else:
            st.error("Please enter your Email or Phone.")

# Admin View
if menu == "Admin View":
    st.subheader("🔐 Admin Login to View Attendance")
    admin_input = st.text_input("Admin Email or Phone")
    if st.button("View Attendance"):
        admin_view(admin_input)
