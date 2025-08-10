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

# === Helpers: phone/email normalization ===
def clean_phone(raw):
    """Return cleaned phone string in local Malaysian format (preserve leading zero)."""
    if pd.isna(raw) or raw is None:
        return ""
    s = str(raw).strip()
    if s == "":
        return ""
    s = re.sub(r'\.0+$', '', s)  # remove trailing .0
    digits = re.sub(r'\D', '', s)  # keep digits only
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
            required_columns = ["Email/Phone", "Name", "Org", "Clock In Date", "Time", "Clock Out Time"]
            for col in required_columns:
                if col not in att.columns:
                    att[col] = ""
            att = att[required_columns].copy()
            att["Email/Phone"] = att["Email/Phone"].apply(clean_contact_field)
            st.session_state.attendance = att
        else:
            st.session_state.attendance = pd.DataFrame(columns=["Email/Phone", "Name", "Org", "Clock In Date", "Time", "Clock Out Time"])
    except Exception as e:
        st.error(f"Error loading attendance file: {e}")
        st.session_state.attendance = pd.DataFrame(columns=["Email/Phone", "Name", "Org", "Clock In Date", "Time", "Clock Out Time"])

    try:
        if os.path.exists(ORG_FILE):
            with open(ORG_FILE, 'r', encoding='utf-8') as f:
                st.session_state.organizations = [o.strip() for o in f.read().splitlines() if o.strip()]
        else:
            st.session_state.organizations = []
    except Exception as e:
        st.error(f"Error loading organizations file: {e}")
        st.session_state.organizations = []

def save_data():
    try:
        if "Phone" in st.session_state.users:
            st.session_state.users["Phone"] = st.session_state.users["Phone"].apply(lambda x: clean_phone(x))
        if "Email" in st.session_state.users:
            st.session_state.users["Email"] = st.session_state.users["Email"].apply(lambda x: str(x).strip().lower() if x else "")

        if "Email/Phone" in st.session_state.attendance:
            st.session_state.attendance["Email/Phone"] = st.session_state.attendance["Email/Phone"].apply(clean_contact_field)

        st.session_state.users.to_csv(USERS_FILE, index=False)
        st.session_state.attendance.to_csv(ATTENDANCE_FILE, index=False)
        with open(ORG_FILE, 'w', encoding='utf-8') as f:
            f.write("\n".join(st.session_state.organizations))
    except Exception as e:
        st.error(f"Error saving data: {e}")

# === Initialize session_state defaults ===
if 'users' not in st.session_state:
    st.session_state.users = pd.DataFrame(columns=["Email", "Phone", "Name", "Gender", "Age", "Address", "Org", "Role"])
if 'attendance' not in st.session_state:
    st.session_state.attendance = pd.DataFrame(columns=["Email/Phone", "Name", "Org", "Clock In Date", "Time", "Clock Out Time"])
if 'organizations' not in st.session_state:
    st.session_state.organizations = []
if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = None
if 'last_user' not in st.session_state:
    st.session_state.last_user = None

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
    st.success("✅ Logged out successfully.")
    st.rerun()

# === Clock in/out ===
def clock_in_user(user, biometric_used="No"):
    if not user:
        st.error("User information missing. Please login or register.")
        return

    malaysia_tz = pytz.timezone("Asia/Kuala_Lumpur")
    now = datetime.now(malaysia_tz)
    today = str(now.date())

    normalized_id = get_normalized_id_from_user_dict(user)
    if not normalized_id:
        msg = "User identifier missing."
        admins = get_admins_for_org(user.get("Org"))
        if admins:
            msg += " Please contact your admin(s): " + "; ".join([f"{a['Name']} (Email: {a.get('Email') or 'N/A'}, Phone: {a.get('Phone') or 'N/A'})" for a in admins])
        else:
            msg += " Please contact IT support."
        st.error(msg)
        return

    attendance_df = st.session_state.attendance.copy()
    # ensure normalized column for comparison
    attendance_df["Email_norm"] = attendance_df["Email/Phone"].apply(lambda x: normalize_identifier(x))
    # match same id and same date and same org
    match = attendance_df[
        (attendance_df["Email_norm"] == normalized_id) &
        (attendance_df["Clock In Date"] == today) &
        (attendance_df["Org"] == (user.get("Org") or ""))
    ]
    if not match.empty:
        st.info("You have already clocked in today.")
        return

    new_row = {
        "Email/Phone": normalized_id,
        "Name": user.get("Name", ""),
        "Org": user.get("Org", ""),
        "Clock In Date": today,
        "Time": now.strftime("%H:%M:%S"),
        "Clock Out Time": ""
    }

    # append to session_state.attendance (remove helper column if present)
    st.session_state.attendance = pd.concat([attendance_df.drop(columns=["Email_norm"], errors="ignore"), pd.DataFrame([new_row])], ignore_index=True)
    save_data()
    st.success("✅ Clocked in successfully.")

def clock_out_user(user):
    if not user:
        st.error("User information missing. Please login or register.")
        return

    malaysia_tz = pytz.timezone("Asia/Kuala_Lumpur")
    now = datetime.now(malaysia_tz)
    today = str(now.date())

    normalized_id = get_normalized_id_from_user_dict(user)
    if not normalized_id:
        msg = "User identifier missing."
        admins = get_admins_for_org(user.get("Org"))
        if admins:
            msg += " Please contact your admin(s): " + "; ".join(
                [f"{a['Name']} (Email: {a.get('Email') or 'N/A'}, Phone: {a.get('Phone') or 'N/A'})" for a in admins]
            )
        else:
            msg += " Please contact IT support."
        st.error(msg)
        return

    attendance_df = st.session_state.attendance.copy()
    attendance_df["Email_norm"] = attendance_df["Email/Phone"].apply(lambda x: normalize_identifier(x))
    attendance_df["Clock Out Time"] = attendance_df["Clock Out Time"].fillna("").astype(str)

    # Find today's record for this user/org
    today_records = attendance_df[
        (attendance_df["Email_norm"] == normalized_id) &
        (attendance_df["Clock In Date"] == today) &
        (attendance_df["Org"] == (user.get("Org") or ""))
    ]

    if today_records.empty:
        msg = "No active clock-in found for today."
        admins = get_admins_for_org(user.get("Org"))
        if admins:
            msg += " Please contact your admin(s): " + "; ".join(
                [f"{a['Name']} (Email: {a.get('Email') or 'N/A'}, Phone: {a.get('Phone') or 'N/A'})" for a in admins]
            )
        else:
            msg += " Please contact IT support."
        st.warning(msg)
        return

    # If already clocked out
    if (today_records["Clock Out Time"] != "").any():
        st.info("You have already clocked out today.")
        return

    # Update Clock Out Time in session state
    indices = today_records.index
    st.session_state.attendance.loc[indices, "Clock Out Time"] = now.strftime("%H:%M:%S")
    save_data()
    st.success("✅ Clocked out successfully.")

    # Update the actual dataframe in session_state by index
    indices = attendance_df[mask].index
    # Use st.session_state.attendance's index to set Clock Out Time
    st.session_state.attendance.loc[indices, "Clock Out Time"] = now.strftime("%H:%M:%S")
    save_data()
    st.success("✅ Clocked out successfully.")

# === Admin view & org management ===
def admin_view(user):
    """Admin-only area: view all records and manage orgs."""
    if not user or user.get("Role", "").lower() != "admin":
        msg = "Access denied. Admin only."
        # also show contact admins for user's org (if available)
        if user:
            admins = get_admins_for_org(user.get("Org"))
            if admins:
                msg += " Please contact your admin(s): " + "; ".join([f"{a['Name']} (Email: {a.get('Email') or 'N/A'}, Phone: {a.get('Phone') or 'N/A'})" for a in admins])
            else:
                msg += " Please contact IT support."
        st.error(msg)
        return

    st.subheader("⏱ Attendance Records (All Organizations)")
    st.dataframe(st.session_state.attendance)

    csv = st.session_state.attendance.to_csv(index=False).encode('utf-8')
    st.download_button("Download All Attendance CSV", csv, "all_attendance.csv", "text/csv")

    st.markdown("---")
    st.subheader("🏢 Manage Organizations")

    # show existing organizations
    if not st.session_state.organizations:
        st.info("No organizations exist yet. Create one below.")
        new_org_name = st.text_input("New Organization Name", key="admin_new_org")
        if st.button("Create Organization"):
            if new_org_name.strip():
                st.session_state.organizations.append(new_org_name.strip())
                save_data()
                st.success(f"✅ Created organization '{new_org_name.strip()}'")
            else:
                st.warning("Organization name is required.")
        return

    # Rename Org
    org_to_rename = st.selectbox("Select Organization to Rename", st.session_state.organizations, key="rename_org")
    new_name = st.text_input("New Organization Name", key="new_org_name")
    if st.button("Rename Organization"):
        if new_name and new_name.strip() and new_name not in st.session_state.organizations:
            # update lists and user/attendance records
            st.session_state.organizations = [new_name if o == org_to_rename else o for o in st.session_state.organizations]
            st.session_state.users.loc[st.session_state.users["Org"] == org_to_rename, "Org"] = new_name
            st.session_state.attendance.loc[st.session_state.attendance["Org"] == org_to_rename, "Org"] = new_name
            save_data()
            st.success(f"✅ Renamed '{org_to_rename}' to '{new_name}'.")
        else:
            st.warning("Invalid or duplicate name.")

    st.markdown("---")
    # Delete org with transfer option
    org_to_delete = st.selectbox("Select Organization to Delete", st.session_state.organizations, key="delete_org")
    transfer_org = st.text_input("Transfer members to (existing or new org name)", key="transfer_org_name")
    if st.button("Delete Organization and Transfer Members"):
        if not transfer_org.strip():
            st.warning("Please enter a target organization name to transfer members.")
        else:
            transfer_org = transfer_org.strip()
            # create transfer org if not exists
            if transfer_org not in st.session_state.organizations:
                st.session_state.organizations.append(transfer_org)
            # transfer users and attendance
            st.session_state.users.loc[st.session_state.users["Org"] == org_to_delete, "Org"] = transfer_org
            st.session_state.attendance.loc[st.session_state.attendance["Org"] == org_to_delete, "Org"] = transfer_org
            # remove old org
            st.session_state.organizations = [o for o in st.session_state.organizations if o != org_to_delete]
            save_data()
            st.success(f"✅ Transferred members from '{org_to_delete}' to '{transfer_org}' and deleted '{org_to_delete}'.")

# === App UI ===
st.title("⏱️ Attendance App")

# Sidebar menu depends on login state
if not st.session_state.logged_in_user:
    menu = st.sidebar.selectbox("Menu", ["Login", "Register", "Create Organization"])
else:
    role = st.session_state.logged_in_user.get("Role", "").lower()
    if role == "admin":
        menu = st.sidebar.selectbox("Menu", ["Clock In / Out", "Admin View", "Logout"])
    else:
        menu = st.sidebar.selectbox("Menu", ["Clock In / Out", "Logout"])

    st.sidebar.write(f"👤 Logged in as: **{st.session_state.logged_in_user.get('Name','(No name)')}** ({role})")
    if st.session_state.logged_in_user.get("Org"):
        st.sidebar.write(f"🏢 Organization: **{st.session_state.logged_in_user.get('Org')}**")

# Unauthenticated flows
if not st.session_state.logged_in_user:
    if menu == "Login":
        login()
    elif menu == "Register":
        st.subheader("📝 User Registration")
        email = st.text_input("Email (e.g., xyz@gmail.com)", key="reg_email")
        phone = st.text_input("Phone (e.g., 0123456789)", key="reg_phone")
        name = st.text_input("Full Name", key="reg_name")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="reg_gender")
        age = st.number_input("Age", min_value=10, max_value=120, key="reg_age")
        address = st.text_input("Home Address (Optional)", key="reg_address")

        if st.session_state.organizations:
            org = st.selectbox("Select Organization", st.session_state.organizations, key="reg_org_select")
        else:
            org = st.text_input("Organization (ask admin to create if unsure)", key="reg_org_text")

        if st.button("Register"):
            chosen_org = org if org else ""
            register_user(email, phone, name, gender, age, address, chosen_org, "user")

    elif menu == "Create Organization":
        st.subheader("👨‍💼 Create Organization (Admin)")
        email = st.text_input("Admin Email", key="create_email")
        phone = st.text_input("Admin Phone", key="create_phone")
        name = st.text_input("Admin Name", key="create_name")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="create_gender")
        age = st.number_input("Age", min_value=0, max_value=200, key="create_age")
        address = st.text_input("Address", key="create_address")
        org = st.text_input("New Organization Name", key="create_org")

        if st.button("Create Organization and Register Admin"):
            if not org or not org.strip():
                st.warning("Organization name is required.")
            else:
                register_user(email, phone, name, gender, age, address, org.strip(), "admin")

# Authenticated flows
else:
    if menu == "Clock In / Out":
        st.subheader("⏱ Clock In / Clock Out")
        malaysia_tz = pytz.timezone("Asia/Kuala_Lumpur")
        st.info(f"🕒 Current Time: {datetime.now(malaysia_tz).strftime('%Y-%m-%d %H:%M:%S')}")
        st.write("")  # spacing

        # Provide some convenience: show last used profile or allow using current logged-in user
        use_saved = st.checkbox("Use saved profile (remembered)", value=True)
        if use_saved and st.session_state.last_user:
            st.success(f"Welcome back, {st.session_state.last_user.get('Name','(No name)')} from {st.session_state.last_user.get('Org','(No org)')}")
            display_user = st.session_state.last_user
        else:
            display_user = st.session_state.logged_in_user

        # Biometric simulation toggle (keeps backward compatibility)
        biometric_used = st.checkbox("Simulate biometric used for this clock action?", value=False)
        biometric_val = "Yes" if biometric_used else "No"

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Clock In"):
                clock_in_user(display_user, biometric_used=biometric_val)
                # after successful clock-in, store last_user
                if display_user:
                    st.session_state.last_user = display_user
        with col2:
            if st.button("🛑 Clock Out"):
                clock_out_user(display_user)

        st.markdown("---")
        st.subheader("Your Today's Attendance")
        # Filter today's attendance for the user's normalized id
        user_norm = get_normalized_id_from_user_dict(display_user) if display_user else ""
        if user_norm:
            today = str(datetime.now(pytz.timezone("Asia/Kuala_Lumpur")).date())
            df = st.session_state.attendance[
                (st.session_state.attendance["Email/Phone"].apply(lambda x: normalize_identifier(x)) == user_norm) &
                (st.session_state.attendance["Clock In Date"] == today)
            ]
            if df.empty:
                st.info("No attendance record for today yet.")
            else:
                st.dataframe(df)
        else:
            st.info("No user identifier available to show today's attendance.")

    elif menu == "Admin View":
        admin_view(st.session_state.logged_in_user)

    elif menu == "Logout":
        logout() 
