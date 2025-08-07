import streamlit as st
import pandas as pd
from datetime import datetime
import os

# === Persistent Storage (CSV files) ===
USERS_FILE = "users.csv"
ATTENDANCE_FILE = "attendance.csv"
ORG_FILE = "orgs.csv"

# === Load Data from Files ===
def load_data():
    if os.path.exists(USERS_FILE):
        st.session_state.users = pd.read_csv(USERS_FILE)
    else:
        st.session_state.users = pd.DataFrame(columns=["Email", "Phone", "Name", "Gender", "Age", "Address", "Org", "Role"])

    if os.path.exists(ATTENDANCE_FILE):
        st.session_state.attendance = pd.read_csv(ATTENDANCE_FILE)
    else:
        st.session_state.attendance = pd.DataFrame(columns=["Email/Phone", "Name", "Org", "Clock In Date", "Time", "Biometric Used"])

    if os.path.exists(ORG_FILE):
        with open(ORG_FILE, 'r') as f:
            st.session_state.organizations = f.read().splitlines()
    else:
        st.session_state.organizations = []

# === Save Data to Files ===
def save_data():
    st.session_state.users.to_csv(USERS_FILE, index=False)
    st.session_state.attendance.to_csv(ATTENDANCE_FILE, index=False)
    with open(ORG_FILE, 'w') as f:
        f.write('\n'.join(st.session_state.organizations))

# === Initialize session state ===
if 'users' not in st.session_state:
    load_data()

# === Helper functions ===
def get_user(identifier):
    identifier = str(identifier).strip().lower()
    users = st.session_state.users
    return users[(users['Email'].str.lower() == identifier) | (users['Phone'].astype(str) == identifier)]

def get_user_org(identifier):
    user = get_user(identifier)
    return user['Org'].values[0] if not user.empty else None

def register_user(email, phone, name, gender, age, address, org, role="user"):
    users = st.session_state.users
    email = email.strip().lower() if email else ""
    phone = str(phone).strip() if phone else ""

    if email == '' and phone == '':
        st.warning("Either email or phone must be provided.")
        return

    existing_user = users[(users["Email"].str.lower() == email) | (users["Phone"].astype(str) == phone)]
    if not existing_user.empty:
        st.warning("User already exists!")
        return

    if org and org not in st.session_state.organizations:
        st.session_state.organizations.append(org)

    new_row = {
        "Email": email,
        "Phone": phone,
        "Name": name,
        "Gender": gender,
        "Age": age,
        "Address": address,
        "Org": org,
        "Role": role
    }

    st.session_state.users = pd.concat([users, pd.DataFrame([new_row])], ignore_index=True)
    save_data()
    st.success(f"✅ Registered {role} successfully!")

def clock_in_user(identifier, org, biometric_used):
    identifier = str(identifier).strip().lower()
    users = st.session_state.users
    attendance = st.session_state.attendance
    user = get_user(identifier)

    if user.empty:
        st.error("❌ Identifier not found. Please register first.")
        return

    user_email = user['Email'].values[0]
    user_phone = str(user['Phone'].values[0])
    user_name = user['Name'].values[0]
    user_org = user['Org'].values[0]
    today = datetime.today().date()

    normalized_id = user_email if user_email else user_phone

    if "Clock In Date" not in attendance.columns:
        attendance["Clock In Date"] = ""

    existing = attendance[(attendance['Email/Phone'].str.lower() == normalized_id.lower()) &
                          (attendance['Clock In Date'] == str(today)) &
                          (attendance['Org'] == user_org)]

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

    st.session_state.attendance = pd.concat([attendance, pd.DataFrame([new_row])], ignore_index=True)
    save_data()
    st.success("✅ Clocked in successfully.")

def admin_view(identifier):
    identifier = str(identifier).strip().lower()
    users = st.session_state.users
    attendance = st.session_state.attendance
    admin_user = get_user(identifier)

    if admin_user.empty or admin_user["Role"].values[0] != "admin":
        st.error("Access denied. Admin only.")
        return

    org = admin_user["Org"].values[0]
    org_attendance = attendance[attendance["Org"] == org]

    st.subheader(f"⏱️ Attendance Records for {org}")
    st.dataframe(org_attendance)

    csv = org_attendance.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, f"{org}_attendance.csv", "text/csv")

# === Streamlit UI ===
st.title("⏱️ Attendance App")

menu = st.sidebar.selectbox("Menu", ["Register", "Clock In", "Admin View", "Create Organization"])

# === Create Organization (Admin) ===
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

# === User Registration ===
if menu == "Register":
    st.subheader("📝 User Registration")
    email = st.text_input("Email (Either Email or Phone required)")
    phone = st.text_input("Phone (Either Email or Phone required)")
    name = st.text_input("Full Name")
    gender = st.selectbox("Gender", ["Male", "Female"])
    age = st.number_input("Age", min_value=10, max_value=100)
    address = st.text_input("Home Address (Optional)")

    if st.session_state.organizations:
        org = st.selectbox("Select Organization", st.session_state.organizations)
        if st.button("Register"):
            register_user(email, phone, name, gender, age, address, org, "user")
    else:
        st.warning("No organizations available. Please ask admin to create one.")

# === Clock In ===
if menu == "Clock In":
    st.subheader("⏱️ Clock In")
    st.info("You only need to enter either Email or Phone.")

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
        if not org and st.session_state.organizations:
            org = st.selectbox("Select Organization", st.session_state.organizations)
        elif not org:
            st.warning("No organizations found. Please register first.")

    remember_me = st.checkbox("Remember Me for future clock-ins", value=True)
    biometric_used = "Yes" if use_saved else "No"

    if st.button("Clock In"):
        if id_input:
            clock_in_user(id_input, org, biometric_used)
            user_row = get_user(id_input)
            if remember_me and not user_row.empty:
                st.session_state.last_user = user_row.iloc[0].to_dict()
        else:
            st.error("Please enter your Email or Phone.")

# === Admin View ===
if menu == "Admin View":
    st.subheader("🔐 Admin Login to View Attendance")
    admin_input = st.text_input("Admin Email or Phone")
    if st.button("View Attendance"):
        admin_view(admin_input)
