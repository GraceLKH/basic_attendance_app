import streamlit as st
import pandas as pd
from datetime import datetime
import os
import pytz
import re

# === Files ===
USERS_FILE = "users.csv"
ATTENDANCE_FILE = "attendance.csv"
ORG_FILE = "orgs.csv"
ORG_PASSWORD_FILE = "org_passwords.csv"  # New file for per-org admin passwords
DEFAULT_ADMIN_PASSWORD = "admin123"  # Default password for new orgs

# === Helpers: phone/email normalization ===
def clean_phone(raw):
    if pd.isna(raw) or raw is None:
        return ""
    s = str(raw).strip()
    if s == "":
        return ""
    s = re.sub(r'\.0+$', '', s)
    digits = re.sub(r'\D', '', s)
    if digits == "":
        return ""
    if digits.startswith("60") and len(digits) > 2:
        digits = "0" + digits[2:]
    if not digits.startswith("0") and len(digits) == 9:
        digits = "0" + digits
    return digits

def clean_contact_field(raw):
    if pd.isna(raw) or raw is None:
        return ""
    s = str(raw).strip()
    if s == "":
        return ""
    if "@" in s:
        return s.lower()
    return clean_phone(s)

def normalize_identifier(identifier):
    if pd.isna(identifier) or identifier is None:
        return ""
    s = str(identifier).strip()
    if s == "":
        return ""
    if "@" in s:
        return s.lower()
    return clean_phone(s)

# === Load and Save ===
def load_data():
    try:
        if os.path.exists(USERS_FILE):
            users = pd.read_csv(USERS_FILE, dtype=str).fillna("")
            for c in ["Email", "Phone", "Name", "Gender", "Age", "Address", "Org", "Role"]:
                if c not in users.columns:
                    users[c] = ""
            users["Email"] = users["Email"].apply(lambda x: str(x).strip().lower() if x else "")
            users["Phone"] = users["Phone"].apply(lambda x: clean_phone(x))
            st.session_state.users = users[["Email", "Phone", "Name", "Gender", "Age", "Address", "Org", "Role"]].copy()
        else:
            st.session_state.users = pd.DataFrame(columns=["Email", "Phone", "Name", "Gender", "Age", "Address", "Org", "Role"])
    except Exception as e:
        st.error(f"Error loading users file: {e}")
        st.session_state.users = pd.DataFrame(columns=["Email", "Phone", "Name", "Gender", "Age", "Address", "Org", "Role"])

    try:
        if os.path.exists(ATTENDANCE_FILE):
            att = pd.read_csv(ATTENDANCE_FILE, dtype=str).fillna("")
            required_columns = ["Email", "Phone", "Name", "Org", "Clock In Date", "Time", "Clock Out Time"]
            for col in required_columns:
                if col not in att.columns:
                    att[col] = ""
            att["Email"] = att["Email"].apply(lambda x: str(x).strip().lower())
            att["Phone"] = att["Phone"].apply(clean_phone)
            st.session_state.attendance = att[required_columns].copy()
        else:
            st.session_state.attendance = pd.DataFrame(columns=["Email", "Phone", "Name", "Org", "Clock In Date", "Time", "Clock Out Time"])
    except Exception as e:
        st.error(f"Error loading attendance file: {e}")
        st.session_state.attendance = pd.DataFrame(columns=["Email", "Phone", "Name", "Org", "Clock In Date", "Time", "Clock Out Time"])

    try:
        if os.path.exists(ORG_FILE):
            with open(ORG_FILE, 'r', encoding='utf-8') as f:
                st.session_state.organizations = [o.strip() for o in f.read().splitlines() if o.strip()]
        else:
            st.session_state.organizations = []
    except Exception as e:
        st.error(f"Error loading organizations file: {e}")
        st.session_state.organizations = []

    # Load per-organization admin passwords
    if os.path.exists(ORG_PASSWORD_FILE):
        try:
            pw_df = pd.read_csv(ORG_PASSWORD_FILE, dtype=str).fillna("")
            st.session_state.org_admin_passwords = dict(zip(pw_df["Org"], pw_df["Password"]))
        except:
            st.session_state.org_admin_passwords = {}
    else:
        st.session_state.org_admin_passwords = {}

def save_data():
    try:
        if "Phone" in st.session_state.users:
            st.session_state.users["Phone"] = st.session_state.users["Phone"].apply(lambda x: clean_phone(x))
        if "Email" in st.session_state.users:
            st.session_state.users["Email"] = st.session_state.users["Email"].apply(lambda x: str(x).strip().lower() if x else "")

        if "Phone" in st.session_state.attendance:
            st.session_state.attendance["Phone"] = st.session_state.attendance["Phone"].apply(clean_phone)
        if "Email" in st.session_state.attendance:
            st.session_state.attendance["Email"] = st.session_state.attendance["Email"].apply(lambda x: str(x).strip().lower() if x else "")

        st.session_state.users.to_csv(USERS_FILE, index=False)
        st.session_state.attendance.to_csv(ATTENDANCE_FILE, index=False)
        with open(ORG_FILE, 'w', encoding='utf-8') as f:
            f.write("\n".join(st.session_state.organizations))

        # Save per-org admin passwords
        pd.DataFrame([
            {"Org": org, "Password": pw}
            for org, pw in st.session_state.org_admin_passwords.items()
        ]).to_csv(ORG_PASSWORD_FILE, index=False)
    except Exception as e:
        st.error(f"Error saving data: {e}")

# === Initialize session_state defaults ===
if 'users' not in st.session_state:
    st.session_state.users = pd.DataFrame(columns=["Email", "Phone", "Name", "Gender", "Age", "Address", "Org", "Role"])
if 'attendance' not in st.session_state:
    st.session_state.attendance = pd.DataFrame(columns=["Email", "Phone", "Name", "Org", "Clock In Date", "Time", "Clock Out Time"])
if 'organizations' not in st.session_state:
    st.session_state.organizations = []
if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = None
if 'last_user' not in st.session_state:
    st.session_state.last_user = None
if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False
if 'org_admin_passwords' not in st.session_state:
    st.session_state.org_admin_passwords = {}

load_data()

# === User/Org helper functions ===
def get_user(identifier):
    identifier_norm = normalize_identifier(identifier)
    if identifier_norm == "":
        return pd.DataFrame()
    users = st.session_state.users.copy()
    users["Email_norm"] = users["Email"].apply(lambda x: normalize_identifier(x))
    users["Phone_norm"] = users["Phone"].apply(lambda x: normalize_identifier(x))
    match = users[(users["Email_norm"] == identifier_norm) | (users["Phone_norm"] == identifier_norm)]
    return match.drop(columns=["Email_norm", "Phone_norm"], errors="ignore")

def get_user_by_row(row):
    if row is None:
        return None
    return {
        "Email": row.get("Email", ""),
        "Phone": row.get("Phone", ""),
        "Name": row.get("Name", ""),
        "Gender": row.get("Gender", ""),
        "Age": row.get("Age", ""),
        "Address": row.get("Address", ""),
        "Org": row.get("Org", ""),
        "Role": row.get("Role", "")
    }

def get_normalized_id_from_user_dict(user):
    if not user:
        return ""
    if user.get("Email") and str(user.get("Email")).strip():
        return normalize_identifier(user.get("Email"))
    if user.get("Phone") and str(user.get("Phone")).strip():
        return normalize_identifier(user.get("Phone"))
    return ""

def get_admins_for_org(org):
    admins = st.session_state.users[
        (st.session_state.users["Org"] == org) &
        (st.session_state.users["Role"].str.lower() == "admin")
    ]
    if admins.empty:
        return []
    return admins[["Name", "Email", "Phone"]].fillna("").to_dict("records")

# === Password Management ===
def change_admin_password(new_password):
    if not new_password:
        st.error("Password cannot be empty")
        return False
    st.session_state.admin_password = new_password
    st.success("✅ Admin password changed successfully")
    return True

def reset_user_password():
    st.subheader("🔄 Reset User Password")
    email = st.text_input("Email of user to reset password", key="reset_email")
    if not email:
        return False
    if email not in st.session_state.users['Email'].values:
        st.error("User not found")
        return False

    new_password = st.text_input("New password", type="password", key="reset_new_password")
    if not new_password:
        st.error("Password cannot be empty")
        return False

    st.success(f"✅ Password reset for {email}")
    return True

def validate_password(password):
    if password == st.session_state.admin_password:
        return True
    else:
        st.error("Incorrect admin password")
        return False

# === Registration ===
def register_user(email, phone, name, gender, age, address, org, role="user"):
    email_norm = str(email).strip().lower() if email and "@" in str(email) else ""
    phone_norm = clean_phone(phone)

    if email_norm == "" and phone_norm == "":
        st.warning("Either Email or Phone must be provided.")
        return

    users = st.session_state.users.copy()
    users["Email_norm"] = users["Email"].apply(lambda x: normalize_identifier(x))
    users["Phone_norm"] = users["Phone"].apply(lambda x: normalize_identifier(x))
    if ((email_norm and (users["Email_norm"] == email_norm).any()) or
            (phone_norm and (users["Phone_norm"] == phone_norm).any())):
        st.warning("User already exists!")
        return

    if org and org not in st.session_state.organizations:
        st.session_state.organizations.append(org)

    new_row = {
        "Email": email_norm,
        "Phone": phone_norm,
        "Name": name.strip() if name else "",
        "Gender": gender if gender else "",
        "Age": str(age) if age != "" else "",
        "Address": address if address else "",
        "Org": org if org else "",
        "Role": role
    }

    st.session_state.users = pd.concat([st.session_state.users, pd.DataFrame([new_row])], ignore_index=True)
    save_data()
    st.success(f"✅ Registered {role} successfully!")

# === Login ===
def login():
    st.subheader("🔑 Login")
    identifier = st.text_input("Email or Phone", key="login_identifier")
    if st.button("Login"):
        user_row = get_user(identifier)
        if not user_row.empty:
            st.session_state.logged_in_user = user_row.iloc[0].to_dict()
            st.session_state.last_user = st.session_state.logged_in_user
            st.success(f"✅ Logged in as {st.session_state.logged_in_user.get('Name','(No name)')} ({st.session_state.logged_in_user.get('Role','user')})")
            st.rerun()
        else:
            st.error("❌ User not found. Please register first.")

def logout():
    st.session_state.logged_in_user = None
    st.session_state.admin_authenticated = False
    st.success("✅ Logged out successfully.")
    st.rerun()

# === Profile Edit Functions ===
def update_attendance_records(old_email, old_phone, new_email, new_phone, new_name, new_org):
    if old_email:
        mask = st.session_state.attendance["Email"] == old_email
        st.session_state.attendance.loc[mask, "Email"] = new_email
        st.session_state.attendance.loc[mask, "Phone"] = new_phone
        st.session_state.attendance.loc[mask, "Name"] = new_name
        st.session_state.attendance.loc[mask, "Org"] = new_org

    if old_phone:
        mask = st.session_state.attendance["Phone"] == old_phone
        st.session_state.attendance.loc[mask, "Email"] = new_email
        st.session_state.attendance.loc[mask, "Phone"] = new_phone
        st.session_state.attendance.loc[mask, "Name"] = new_name
        st.session_state.attendance.loc[mask, "Org"] = new_org

    save_data()

# === Profile Edit ===
def edit_profile(user):
    st.subheader("✏️ Edit Profile")
    old_email = user.get("Email", "")
    old_phone = user.get("Phone", "")

    email = st.text_input("Email", value=old_email)
    phone = st.text_input("Phone", value=old_phone)
    name = st.text_input("Name", value=user.get("Name", ""))
    gender = st.selectbox("Gender", ["Male", "Female", "Other"],
                          index=["Male", "Female", "Other"].index(user.get("Gender", "Male")) if user.get("Gender") in ["Male", "Female", "Other"] else 0)
    age = st.number_input("Age", min_value=0, max_value=200, value=int(user.get("Age", "0")) if user.get("Age") and user.get("Age").isdigit() else 0)
    address = st.text_input("Address", value=user.get("Address", ""))

    if st.session_state.organizations:
        org_default_index = st.session_state.organizations.index(user.get("Org")) if user.get("Org") in st.session_state.organizations else 0
        org = st.selectbox("Organization", st.session_state.organizations, index=org_default_index)
    else:
        org = st.text_input("Organization", value=user.get("Org", ""))

    if st.button("Save Changes"):
        idx = st.session_state.users[
            (st.session_state.users["Email"] == old_email) &
            (st.session_state.users["Phone"] == old_phone)
        ].index

        if not idx.empty:
            old_name = user.get("Name", "")
            old_org = user.get("Org", "")

            st.session_state.users.loc[idx[0], ["Email", "Phone", "Name", "Gender", "Age", "Address", "Org"]] = [
                email, phone, name, gender, str(age), address, org
            ]

            if email != old_email or phone != old_phone or name != old_name or org != old_org:
                update_attendance_records(old_email, old_phone, email, phone, name, org)

            save_data()
            st.session_state.logged_in_user = get_user_by_row(st.session_state.users.loc[idx[0]])
            st.success("✅ Profile updated successfully.")
        else:
            st.error("User not found.")

# === Clock in/out ===
def clock_in_user(user):
    if not user:
        st.error("User information missing. Please login or register.")
        return

    malaysia_tz = pytz.timezone("Asia/Kuala_Lumpur")
    now = datetime.now(malaysia_tz)
    today = str(now.date())

    if not user.get("Email") and not user.get("Phone"):
        st.error("User identifier missing. Please contact your admin.")
        return

    attendance_df = st.session_state.attendance.copy()
    match = attendance_df[
        (attendance_df["Email"] == (user.get("Email") or "")) &
        (attendance_df["Phone"] == (user.get("Phone") or "")) &
        (attendance_df["Clock In Date"] == today) &
        (attendance_df["Org"] == (user.get("Org") or ""))
    ]
    if not match.empty:
        st.info("You have already clocked in today.")
        return

    new_row = {
        "Email": user.get("Email", ""),
        "Phone": user.get("Phone", ""),
        "Name": user.get("Name", ""),
        "Org": user.get("Org", ""),
        "Clock In Date": today,
        "Time": now.strftime("%H:%M:%S"),
        "Clock Out Time": ""
    }

    st.session_state.attendance = pd.concat([attendance_df, pd.DataFrame([new_row])], ignore_index=True)
    save_data()
    st.success("✅ Clocked in successfully.")

def clock_out_user(user):
    if not user:
        st.error("User information missing. Please login or register.")
        return

    malaysia_tz = pytz.timezone("Asia/Kuala_Lumpur")
    now = datetime.now(malaysia_tz)
    today = str(now.date())

    attendance_df = st.session_state.attendance.copy()
    today_records = attendance_df[
        (attendance_df["Email"] == (user.get("Email") or "")) &
        (attendance_df["Phone"] == (user.get("Phone") or "")) &
        (attendance_df["Clock In Date"] == today) &
        (attendance_df["Org"] == (user.get("Org") or ""))
    ]

    if today_records.empty:
        st.warning("No active clock-in found for today.")
        return

    if (today_records["Clock Out Time"] != "").any():
        st.info("You have already clocked out today.")
        return

    st.session_state.attendance.loc[today_records.index, "Clock Out Time"] = now.strftime("%H:%M:%S")
    save_data()
    st.success("✅ Clocked out successfully.")

# === Admin view ===
def admin_view(user):
    if not user or user.get("Role", "").lower() != "admin":
        st.error("Access denied. Admin only.")
        return

    org = user.get("Org", "")
    if not org:
        st.error("You are not assigned to an organization.")
        return

    if not st.session_state.admin_authenticated:
        pwd = st.text_input("Enter admin password", type="password")
        if st.button("Unlock Admin View"):
            correct_pwd = st.session_state.org_admin_passwords.get(org, DEFAULT_ADMIN_PASSWORD)
            if pwd == correct_pwd:
                st.session_state.admin_authenticated = True
                st.success("✅ Access granted.")
                st.rerun()
            else:
                st.error("❌ Incorrect password.")
        return

    # Show only this org's attendance
    st.subheader(f"⏱ Attendance Records ({org})")
    org_attendance = st.session_state.attendance[
        st.session_state.attendance["Org"] == org
    ].reset_index(drop=True)  # Reset index to start from 0

    st.dataframe(org_attendance)
    csv = org_attendance.to_csv(index=False).encode('utf-8')
    st.download_button(
        f"Download {org} Attendance CSV",
        csv,
        f"{org}_attendance.csv",
        "text/csv"
    )

    st.subheader(f"👥 User Management ({org})")
    org_users = st.session_state.users[
        st.session_state.users["Org"] == org
    ].reset_index(drop=True)  # Reset index to start from 0

    st.dataframe(org_users)
    csv_users = org_users.to_csv(index=False).encode('utf-8')
    st.download_button(
        f"Download {org} Users CSV",
        csv_users,
        f"{org}_users.csv",
        "text/csv"
    )

    st.markdown("---")
    st.subheader("🔐 Reset Admin Password for Your Organization")
    old_pwd = st.text_input("Enter old admin password", type="password", key="old_admin_pwd")
    new_pwd = st.text_input("Enter new admin password", type="password", key="new_admin_pwd")
    confirm_new_pwd = st.text_input("Confirm new admin password", type="password", key="confirm_new_admin_pwd")

    if st.button("Reset Admin Password"):
        correct_pwd = st.session_state.org_admin_passwords.get(org, DEFAULT_ADMIN_PASSWORD)
        if not old_pwd or not new_pwd or not confirm_new_pwd:
            st.error("All fields are required.")
        elif old_pwd != correct_pwd:
            st.error("Old admin password is incorrect.")
        elif new_pwd != confirm_new_pwd:
            st.error("New password and confirmation do not match.")
        elif new_pwd == old_pwd:
            st.error("New password must be different from the old password.")
        else:
            st.session_state.org_admin_passwords[org] = new_pwd
            save_data()
            st.success("✅ Admin password changed successfully.")

# === Registration modifications for new org password ===
def register_user(email, phone, name, gender, age, address, org, role="user"):
    email_norm = str(email).strip().lower() if email and "@" in str(email) else ""
    phone_norm = clean_phone(phone)
    if email_norm == "" and phone_norm == "":
        st.warning("Either Email or Phone must be provided.")
        return
    users = st.session_state.users.copy()
    users["Email_norm"] = users["Email"].apply(lambda x: normalize_identifier(x))
    users["Phone_norm"] = users["Phone"].apply(lambda x: normalize_identifier(x))
    if ((email_norm and (users["Email_norm"] == email_norm).any()) or
            (phone_norm and (users["Phone_norm"] == phone_norm).any())):
        st.warning("User already exists!")
        return
    if org and org not in st.session_state.organizations:
        st.session_state.organizations.append(org)
        st.session_state.org_admin_passwords[org] = DEFAULT_ADMIN_PASSWORD
    new_row = {
        "Email": email_norm,
        "Phone": phone_norm,
        "Name": name.strip() if name else "",
        "Gender": gender if gender else "",
        "Age": str(age) if age != "" else "",
        "Address": address if address else "",
        "Org": org if org else "",
        "Role": role
    }
    st.session_state.users = pd.concat([st.session_state.users, pd.DataFrame([new_row])], ignore_index=True)
    save_data()
    st.success(f"✅ Registered {role} successfully!")

# === App UI ===
st.title("⏱️ Attendance App")

# Sidebar menu logic
if not st.session_state.logged_in_user:
    menu = st.sidebar.selectbox("Menu", ["Login", "Register", "Create Organization"])
else:
    role = st.session_state.logged_in_user.get("Role", "").lower()
    if role == "admin":
        menu = st.sidebar.selectbox("Menu", ["Clock In / Out", "Edit Profile", "Admin View", "Logout"])
    else:
        menu = st.sidebar.selectbox("Menu", ["Clock In / Out", "Edit Profile", "Logout"])

    st.sidebar.write(f"👤 Logged in as: **{st.session_state.logged_in_user.get('Name','(No name)')}** ({role})")
    if st.session_state.logged_in_user.get("Org"):
        st.sidebar.write(f"🏢 Organization: **{st.session_state.logged_in_user.get('Org')}**")

# --- Unauthenticated flows ---
if not st.session_state.logged_in_user:
    if menu == "Login":
        login()

    elif menu == "Register":
        st.subheader("📝 User Registration")
        email = st.text_input("Email (e.g., xyz@gmail.com)", key="reg_email")
        phone = st.text_input("Phone (e.g., 0123456789)", key="reg_phone")
        name = st.text_input("Full Name", key="reg_name")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="reg_gender")
        age = st.number_input("Age", min_value=0, max_value=200, key="reg_age")
        address = st.text_input("Home Address (Optional)", key="reg_address")

        if st.session_state.organizations:
            org = st.selectbox("Select Organization", st.session_state.organizations, key="reg_org_select")
        else:
            org = st.text_input("Organization (ask admin to create if unsure)", key="reg_org_text")

        if st.button("Register"):
            register_user(email, phone, name, gender, age, address, org if org else "", "user")

    elif menu == "Create Organization":
        st.subheader("👨‍💼 Create Organization (Admin)")
        email = st.text_input("Admin Email (e.g., xyz@gmail.com)", key="create_email")
        phone = st.text_input("Admin Phone (e.g., 0123456789)", key="create_phone")
        name = st.text_input("Admin Name", key="create_name")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="create_gender")
        age = st.number_input("Age", min_value=0, max_value=200, key="create_age")
        address = st.text_input("Address", key="create_address")
        org = st.text_input("New Organization Name", key="create_org")

        if st.button("Create Organization and Register Admin"):
            if not org or not org.strip():
                st.error("Organization name cannot be empty.")
            else:
                if org.strip() not in st.session_state.organizations:
                    st.session_state.organizations.append(org.strip())
                register_user(email, phone, name, gender, age, address, org.strip(), "admin")
                st.success(f"Organization '{org.strip()}' created with admin registered.")

else:
    # Logged in users
    if menu == "Logout":
        logout()

    elif menu == "Edit Profile":
        edit_profile(st.session_state.logged_in_user)

    elif menu == "Clock In / Out":
        st.subheader("⏰ Clock In / Clock Out")

        # Show clock in/out buttons
        if st.button("Clock In"):
            clock_in_user(st.session_state.logged_in_user)

        if st.button("Clock Out"):
            clock_out_user(st.session_state.logged_in_user)

        st.markdown("---")
        st.subheader("📅 Your Attendance Records")
        # Show user's own attendance records
        user = st.session_state.logged_in_user
        user_attendance = st.session_state.attendance[
            (st.session_state.attendance["Email"] == (user.get("Email") or "")) &
            (st.session_state.attendance["Phone"] == (user.get("Phone") or "")) &
            (st.session_state.attendance["Org"] == (user.get("Org") or ""))
        ].sort_values(by=["Clock In Date", "Time"], ascending=[False, False])

        if user_attendance.empty:
            st.info("No attendance records found.")
        else:
            st.dataframe(user_attendance.reset_index(drop=True))

    elif menu == "Admin View":
        admin_view(st.session_state.logged_in_user)
