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
ORG_PASSWORD_FILE = "org_passwords.csv"  # per-org admin passwords
DEFAULT_ADMIN_PASSWORD = "admin123"  # Default password for new orgs

# === Translation dictionary (English / 中文) ===
t = {
    "English": {
        "nav_page":"Navigation Page & Language Setting",
        "language_label": "🌐 Language",
        "title": "⏱️ Attendance App",
        "menu": "Menu",
        "login": "🔑 Login",
        "register": "📝 Register",
        "create_org": "👨‍💼 Create Organization",
        "clock_in_out": "⏰ Clock In / Clock Out",
        "edit_profile": "✏️ Edit Profile",
        "admin_view": "📊 Admin View",
        "logout": "🚪 Logout",
        "login_header": "🔑 Login",
        "login_identifier": "Email or Phone",
        "login_button": "Login",
        "login_success": "✅ Logged in as {name} ({role})",
        "user_not_found": "❌ User not found. Please register first.",
        "logout_success": "✅ Logged out successfully.",
        "register_header": "📝 User Registration",
        "reg_email": "Email (e.g., xyz@gmail.com)",
        "reg_phone": "Phone (e.g., 0123456789)",
        "reg_name": "Full Name",
        "reg_gender": "Gender",
        "reg_age": "Age",
        "reg_address": "Home Address (Optional)",
        "reg_org_select": "Select Organization",
        "reg_org_text": "Organization (ask admin to create if unsure)",
        "reg_button": "Register",
        "registered_success": "✅ Registered {role} successfully!",
        "create_org_header": "👨‍💼 Create Organization (Admin)",
        "create_email": "Admin Email (e.g., xyz@gmail.com)",
        "create_phone": "Admin Phone (e.g., 0123456789)",
        "create_name": "Admin Name",
        "create_gender": "Gender",
        "create_age": "Age",
        "create_address": "Address",
        "create_org": "New Organization Name",
        "create_org_button": "Create Organization and Register Admin",
        "create_org_empty": "Organization name cannot be empty.",
        "clock_in_header": "⏰ Clock In / Clock Out",
        "clock_in_button": "Clock In",
        "clock_out_button": "Clock Out",
        "clockin_success": "✅ Clocked in successfully.",
        "clockout_success": "✅ Clocked out successfully.",
        "already_clocked_in": "You have already clocked in today.",
        "no_active_clockin": "No active clock-in found for today.",
        "already_clocked_out": "You have already clocked out today.",
        "attendance_records": "⏱ Your Attendance Records",
        "no_records": "No attendance records found.",
        "edit_profile_header": "✏️ Edit Profile",
        "email_label": "Email",
        "phone_label": "Phone",
        "name_label": "Name",
        "gender_label": "Gender",
        "age_label": "Age",
        "address_label": "Address",
        "organization_label": "Organization",
        "save_changes_button": "Save Changes",
        "profile_updated": "✅ Profile updated successfully.",
        "user_not_found": "User not found.",
        "admin_only": "Access denied. Admin only.",
        "no_org_assigned": "You are not assigned to an organization.",
        "admin_password_prompt": "Enter admin password",
        "unlock_admin": "Unlock Admin View",
        "access_granted": "✅ Access granted.",
        "access_denied_pwd": "❌ Incorrect password.",
        "attendance_records_org": "⏱ Attendance Records ({org})",
        "download_att_csv": "Download {org} Attendance CSV",
        "user_management_org": "👥 User Management ({org})",
        "download_users_csv": "Download {org} Users CSV",
        "reset_admin_pwd_header": "🔐 Reset Admin Password for Your Organization",
        "old_admin_pwd": "Enter old admin password",
        "new_admin_pwd": "Enter new admin password",
        "confirm_new_admin_pwd": "Confirm new admin password",
        "reset_admin_pwd_button": "Reset Admin Password",
        "all_fields_required": "All fields are required.",
        "old_pwd_wrong": "Old admin password is incorrect.",
        "pwd_confirm_mismatch": "New password and confirmation do not match.",
        "pwd_same_old": "New password must be different from the old password.",
        "admin_pwd_changed": "✅ Admin password changed successfully.",
        "either_email_phone_required": "Either Email or Phone must be provided.",
        "user_exists": "User already exists!",
        "missing_user_info": "User information missing. Please login or register.",
        "user_identifier_missing": "User identifier missing. Please contact your admin.",
        "save_error": "Error saving data: {error}",
        "load_users_error": "Error loading users file: {error}",
        "load_attendance_error": "Error loading attendance file: {error}",
        "load_orgs_error": "Error loading organizations file: {error}",
        "password_empty": "Password cannot be empty",
        "password_reset_header": "🔄 Reset User Password",
        "password_reset_email": "Email of user to reset password",
        "password_reset_new": "New password",
        "password_reset_success": "✅ Password reset for {email}",
        "unlock_admin_incorrect": "❌ Incorrect password.",
        "organizations_label": "Organizations",
    },
    "中文": {
        "nav_page":"导航页面 & 语言设置",
        "language_label": "🌐 语言",
        "title": "⏱️ 考勤系统",
        "menu": "菜单",
        "login": "🔑 登录",
        "register": "📝 注册",
        "create_org": "👨‍💼 创建组织",
        "clock_in_out": "⏰ 签到 / 签退",
        "edit_profile": "✏️ 编辑资料",
        "admin_view": "📊 管理员界面",
        "logout": "🚪 退出登录",
        "login_header": "🔑 登录",
        "login_identifier": "电子邮箱或手机号",
        "login_button": "登录",
        "login_success": "✅ 已登录：{name} ({role})",
        "user_not_found": "❌ 未找到用户。请先注册。",
        "logout_success": "✅ 已成功登出。",
        "register_header": "📝 用户注册",
        "reg_email": "邮箱 (例如: xyz@gmail.com)",
        "reg_phone": "电话 (例如: 0123456789)",
        "reg_name": "姓名",
        "reg_gender": "性别",
        "reg_age": "年龄",
        "reg_address": "住址（可选）",
        "reg_org_select": "选择组织",
        "reg_org_text": "组织名称（不确定请联系管理员）",
        "reg_button": "注册",
        "registered_success": "✅ 已成功注册 {role}！",
        "create_org_header": "👨‍💼 创建组织（管理员）",
        "create_email": "管理员邮箱 (例如: xyz@gmail.com)",
        "create_phone": "管理员电话 (例如: 0123456789)",
        "create_name": "管理员姓名",
        "create_gender": "性别",
        "create_age": "年龄",
        "create_address": "地址",
        "create_org": "新组织名称",
        "create_org_button": "创建组织并注册管理员",
        "create_org_empty": "组织名称不能为空。",
        "clock_in_header": "⏰ 签到 / 签退",
        "clock_in_button": "签到",
        "clock_out_button": "签退",
        "clockin_success": "✅ 签到成功。",
        "clockout_success": "✅ 签退成功。",
        "already_clocked_in": "您今天已签到。",
        "no_active_clockin": "找不到有效的签到记录。",
        "already_clocked_out": "您今天已签退。",
        "attendance_records": "⏱您的考勤记录",
        "no_records": "暂无考勤记录。",
        "edit_profile_header": "✏️ 编辑资料",
        "email_label": "邮箱",
        "phone_label": "电话",
        "name_label": "姓名",
        "gender_label": "性别",
        "age_label": "年龄",
        "address_label": "地址",
        "organization_label": "组织",
        "save_changes_button": "保存更改",
        "profile_updated": "✅ 个人资料已更新。",
        "user_not_found": "未找到用户。",
        "admin_only": "访问被拒。仅限管理员。",
        "no_org_assigned": "您未被分配到任何组织。",
        "admin_password_prompt": "输入管理员密码",
        "unlock_admin": "解锁管理员视图",
        "access_granted": "✅ 访问已授权。",
        "access_denied_pwd": "❌ 密码错误。",
        "attendance_records_org": "⏱ 考勤记录 ({org})",
        "download_att_csv": "下载 {org} 考勤 CSV",
        "user_management_org": "👥 用户管理 ({org})",
        "download_users_csv": "下载 {org} 用户 CSV",
        "reset_admin_pwd_header": "🔐 重置您组织的管理员密码",
        "old_admin_pwd": "输入旧管理员密码",
        "new_admin_pwd": "输入新管理员密码",
        "confirm_new_admin_pwd": "确认新管理员密码",
        "reset_admin_pwd_button": "重置管理员密码",
        "all_fields_required": "所有字段均为必填项。",
        "old_pwd_wrong": "旧管理员密码不正确。",
        "pwd_confirm_mismatch": "新密码与确认不匹配。",
        "pwd_same_old": "新密码必须不同于旧密码。",
        "admin_pwd_changed": "✅ 管理员密码已更改。",
        "either_email_phone_required": "必须填写邮箱或电话其中之一。",
        "user_exists": "用户已存在！",
        "missing_user_info": "用户信息缺失。请登录或注册。",
        "user_identifier_missing": "用户标识缺失。请联系您的管理员。",
        "save_error": "保存数据出错：{error}",
        "load_users_error": "加载用户文件出错：{error}",
        "load_attendance_error": "加载考勤文件出错：{error}",
        "load_orgs_error": "加载组织文件出错：{error}",
        "password_empty": "密码不能为空",
        "password_reset_header": "🔄 重置用户密码",
        "password_reset_email": "要重置密码的用户邮箱",
        "password_reset_new": "新密码",
        "password_reset_success": "✅ 已为 {email} 重置密码",
        "unlock_admin_incorrect": "❌ 密码错误。",
        "organizations_label": "组织列表",
    }
}

# Helper to fetch translated text and format with kwargs
def tr(key, **kwargs):
    lang = st.session_state.get("language", "English")
    text = t.get(lang, {}).get(key, key)
    try:
        return text.format(**kwargs)
    except Exception:
        return text

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
        st.error(tr("load_users_error", error=str(e)))
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
        st.error(tr("load_attendance_error", error=str(e)))
        st.session_state.attendance = pd.DataFrame(columns=["Email", "Phone", "Name", "Org", "Clock In Date", "Time", "Clock Out Time"])

    try:
        if os.path.exists(ORG_FILE):
            with open(ORG_FILE, 'r', encoding='utf-8') as f:
                st.session_state.organizations = [o.strip() for o in f.read().splitlines() if o.strip()]
        else:
            st.session_state.organizations = []
    except Exception as e:
        st.error(tr("load_orgs_error", error=str(e)))
        st.session_state.organizations = []

    # Load per-organization admin passwords
    if os.path.exists(ORG_PASSWORD_FILE):
        try:
            pw_df = pd.read_csv(ORG_PASSWORD_FILE, dtype=str).fillna("")
            if "Org" in pw_df.columns and "Password" in pw_df.columns:
                st.session_state.org_admin_passwords = dict(zip(pw_df["Org"], pw_df["Password"]))
            else:
                st.session_state.org_admin_passwords = {}
        except Exception:
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
        st.error(tr("save_error", error=str(e)))

# === Initialize session_state defaults ===
if 'language' not in st.session_state:
    st.session_state.language = "English"
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
if 'admin_password' not in st.session_state:
    st.session_state.admin_password = DEFAULT_ADMIN_PASSWORD

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
        st.error(tr("password_empty"))
        return False
    st.session_state.admin_password = new_password
    st.success(tr("admin_pwd_changed"))
    return True

def reset_user_password_ui():
    st.subheader(tr("password_reset_header"))
    email = st.text_input(tr("password_reset_email"), key="reset_email")
    if not email:
        return False
    if email not in st.session_state.users['Email'].values:
        st.error(tr("user_not_found"))
        return False

    new_password = st.text_input(tr("password_reset_new"), type="password", key="reset_new_password")
    if not new_password:
        st.error(tr("password_empty"))
        return False

    st.success(tr("password_reset_success", email=email))
    return True

def validate_password(password):
    if password == st.session_state.admin_password:
        return True
    else:
        st.error(tr("access_denied_pwd"))
        return False

# === Registration ===
def register_user(email, phone, name, gender, age, address, org, role="user"):
    email_norm = str(email).strip().lower() if email and "@" in str(email) else ""
    phone_norm = clean_phone(phone)

    if email_norm == "" and phone_norm == "":
        st.warning(tr("either_email_phone_required"))
        return

    users = st.session_state.users.copy()
    users["Email_norm"] = users["Email"].apply(lambda x: normalize_identifier(x))
    users["Phone_norm"] = users["Phone"].apply(lambda x: normalize_identifier(x))
    if ((email_norm and (users["Email_norm"] == email_norm).any()) or
            (phone_norm and (users["Phone_norm"] == phone_norm).any())):
        st.warning(tr("user_exists"))
        return

    if org and org not in st.session_state.organizations:
        st.session_state.organizations.append(org)
        # create default admin password for new org
        st.session_state.org_admin_passwords[org] = st.session_state.org_admin_passwords.get(org, DEFAULT_ADMIN_PASSWORD)

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
    st.success(tr("registered_success", role=role))

# === Login ===
def login_ui():
    st.subheader(tr("login_header"))
    identifier = st.text_input(tr("login_identifier"), key="login_identifier")
    if st.button(tr("login_button")):
        user_row = get_user(identifier)
        if not user_row.empty:
            st.session_state.logged_in_user = user_row.iloc[0].to_dict()
            st.session_state.last_user = st.session_state.logged_in_user
            st.success(tr("login_success", name=st.session_state.logged_in_user.get("Name","(No name)"), role=st.session_state.logged_in_user.get("Role","user")))
            st.rerun()
        else:
            st.error(tr("user_not_found"))

def logout():
    st.session_state.logged_in_user = None
    st.session_state.admin_authenticated = False
    st.success(tr("logout_success"))
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
    st.subheader(tr("edit_profile_header"))
    old_email = user.get("Email", "")
    old_phone = user.get("Phone", "")

    email = st.text_input(tr("email_label"), value=old_email)
    phone = st.text_input(tr("phone_label"), value=old_phone)
    name = st.text_input(tr("name_label"), value=user.get("Name", ""))
    gender = st.selectbox(tr("gender_label"), ["Male", "Female", "Other"],
                          index=["Male", "Female", "Other"].index(user.get("Gender", "Male")) if user.get("Gender") in ["Male", "Female", "Other"] else 0)
    age = st.number_input(tr("age_label"), min_value=0, max_value=200, value=int(user.get("Age", "0")) if user.get("Age") and user.get("Age").isdigit() else 0)
    address = st.text_input(tr("address_label"), value=user.get("Address", ""))

    if st.session_state.organizations:
        org_default_index = st.session_state.organizations.index(user.get("Org")) if user.get("Org") in st.session_state.organizations else 0
        org = st.selectbox(tr("organization_label"), st.session_state.organizations, index=org_default_index)
    else:
        org = st.text_input(tr("organization_label"), value=user.get("Org", ""))

    if st.button(tr("save_changes_button")):
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
            st.success(tr("profile_updated"))
        else:
            st.error(tr("user_not_found"))

# === Clock in/out ===
def clock_in_user(user):
    if not user:
        st.error(tr("missing_user_info"))
        return

    malaysia_tz = pytz.timezone("Asia/Kuala_Lumpur")
    now = datetime.now(malaysia_tz)
    today = str(now.date())

    if not user.get("Email") and not user.get("Phone"):
        st.error(tr("user_identifier_missing"))
        return

    attendance_df = st.session_state.attendance.copy()
    match = attendance_df[
        (attendance_df["Email"] == (user.get("Email") or "")) &
        (attendance_df["Phone"] == (user.get("Phone") or "")) &
        (attendance_df["Clock In Date"] == today) &
        (attendance_df["Org"] == (user.get("Org") or ""))
    ]
    if not match.empty:
        st.info(tr("already_clocked_in"))
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
    st.success(tr("clockin_success"))

def clock_out_user(user):
    if not user:
        st.error(tr("missing_user_info"))
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
        st.warning(tr("no_active_clockin"))
        return

    if (today_records["Clock Out Time"] != "").any():
        st.info(tr("already_clocked_out"))
        return

    st.session_state.attendance.loc[today_records.index, "Clock Out Time"] = now.strftime("%H:%M:%S")
    save_data()
    st.success(tr("clockout_success"))

# === Admin view ===
def admin_view(user):
    if not user or user.get("Role", "").lower() != "admin":
        st.error(tr("admin_only"))
        return

    org = user.get("Org", "")
    if not org:
        st.error(tr("no_org_assigned"))
        return

    if not st.session_state.admin_authenticated:
        pwd = st.text_input(tr("admin_password_prompt"), type="password")
        if st.button(tr("unlock_admin")):
            correct_pwd = st.session_state.org_admin_passwords.get(org, DEFAULT_ADMIN_PASSWORD)
            if pwd == correct_pwd:
                st.session_state.admin_authenticated = True
                st.success(tr("access_granted"))
                st.rerun()
            else:
                st.error(tr("unlock_admin_incorrect"))
        return

    # Show only this org's attendance
    st.subheader(tr("attendance_records_org", org=org))
    org_attendance = st.session_state.attendance[
        st.session_state.attendance["Org"] == org
    ].reset_index(drop=True)

    st.dataframe(org_attendance)
    csv = org_attendance.to_csv(index=False).encode('utf-8')
    st.download_button(
        tr("download_att_csv", org=org),
        csv,
        f"{org}_attendance.csv",
        "text/csv"
    )

    st.subheader(tr("user_management_org", org=org))
    org_users = st.session_state.users[
        st.session_state.users["Org"] == org
    ].reset_index(drop=True)

    st.dataframe(org_users)
    csv_users = org_users.to_csv(index=False).encode('utf-8')
    st.download_button(
        tr("download_users_csv", org=org),
        csv_users,
        f"{org}_users.csv",
        "text/csv"
    )

    st.markdown("---")
    st.subheader(tr("reset_admin_pwd_header"))
    old_pwd = st.text_input(tr("old_admin_pwd"), type="password", key="old_admin_pwd")
    new_pwd = st.text_input(tr("new_admin_pwd"), type="password", key="new_admin_pwd")
    confirm_new_pwd = st.text_input(tr("confirm_new_admin_pwd"), type="password", key="confirm_new_admin_pwd")

    if st.button(tr("reset_admin_pwd_button")):
        correct_pwd = st.session_state.org_admin_passwords.get(org, DEFAULT_ADMIN_PASSWORD)
        if not old_pwd or not new_pwd or not confirm_new_pwd:
            st.error(tr("all_fields_required"))
        elif old_pwd != correct_pwd:
            st.error(tr("old_pwd_wrong"))
        elif new_pwd != confirm_new_pwd:
            st.error(tr("pwd_confirm_mismatch"))
        elif new_pwd == old_pwd:
            st.error(tr("pwd_same_old"))
        else:
            st.session_state.org_admin_passwords[org] = new_pwd
            save_data()
            st.success(tr("admin_pwd_changed"))

# === App UI ===
# Language selector in sidebar
st.sidebar.title(tr("nav_page"))
language_choice = st.sidebar.selectbox(
    tr("language_label"),
    ["English", "中文"],
    index=0 if st.session_state.language == "English" else 1
)
st.session_state.language = language_choice

st.title(tr("title"))

# Sidebar menu logic
if not st.session_state.logged_in_user:
    menu = st.sidebar.selectbox(tr("menu"), [tr("login"), tr("register"), tr("create_org")])
else:
    role = st.session_state.logged_in_user.get("Role", "").lower()
    if role == "admin":
        menu = st.sidebar.selectbox(tr("menu"), [tr("clock_in_out"), tr("edit_profile"), tr("admin_view"), tr("logout")])
    else:
        menu = st.sidebar.selectbox(tr("menu"), [tr("clock_in_out"), tr("edit_profile"), tr("logout")])

    st.sidebar.write(tr("login_success", name=st.session_state.logged_in_user.get('Name','(No name)'), role=role))
    if st.session_state.logged_in_user.get("Org"):
        st.sidebar.write(f"🏢 {tr('organization_label')}: **{st.session_state.logged_in_user.get('Org')}**")

# --- Unauthenticated flows ---
if not st.session_state.logged_in_user:
    if menu == tr("login"):
        login_ui()

    elif menu == tr("register"):
        st.subheader(tr("register_header"))
        email = st.text_input(tr("reg_email"), key="reg_email")
        phone = st.text_input(tr("reg_phone"), key="reg_phone")
        name = st.text_input(tr("reg_name"), key="reg_name")
        gender = st.selectbox(tr("reg_gender"), ["Male", "Female", "Other"], key="reg_gender")
        age = st.number_input(tr("reg_age"), min_value=0, max_value=200, key="reg_age")
        address = st.text_input(tr("reg_address"), key="reg_address")

        if st.session_state.organizations:
            org = st.selectbox(tr("reg_org_select"), st.session_state.organizations, key="reg_org_select")
        else:
            org = st.text_input(tr("reg_org_text"), key="reg_org_text")

        if st.button(tr("reg_button")):
            register_user(email, phone, name, gender, age, address, org if org else "", "user")

    elif menu == tr("create_org"):
        st.subheader(tr("create_org_header"))
        email = st.text_input(tr("create_email"), key="create_email")
        phone = st.text_input(tr("create_phone"), key="create_phone")
        name = st.text_input(tr("create_name"), key="create_name")
        gender = st.selectbox(tr("create_gender"), ["Male", "Female", "Other"], key="create_gender")
        age = st.number_input(tr("create_age"), min_value=0, max_value=200, key="create_age")
        address = st.text_input(tr("create_address"), key="create_address")
        org = st.text_input(tr("create_org"), key="create_org")

        if st.button(tr("create_org_button")):
            if not org or not org.strip():
                st.error(tr("create_org_empty"))
            else:
                if org.strip() not in st.session_state.organizations:
                    st.session_state.organizations.append(org.strip())
                    st.session_state.org_admin_passwords[org.strip()] = DEFAULT_ADMIN_PASSWORD
                register_user(email, phone, name, gender, age, address, org.strip(), "admin")
                st.success(tr("registered_success", role="admin"))

else:
    # Logged in users
    if menu == tr("logout"):
        logout()

    elif menu == tr("edit_profile"):
        edit_profile(st.session_state.logged_in_user)

    elif menu == tr("clock_in_out"):
        st.subheader(tr("clock_in_header"))

        # Show clock in/out buttons
        if st.button(tr("clock_in_button")):
            clock_in_user(st.session_state.logged_in_user)

        if st.button(tr("clock_out_button")):
            clock_out_user(st.session_state.logged_in_user)

        st.markdown("---")
        st.subheader(tr("attendance_records"))
        # Show user's own attendance records
        user = st.session_state.logged_in_user
        user_attendance = st.session_state.attendance[
            (st.session_state.attendance["Email"] == (user.get("Email") or "")) &
            (st.session_state.attendance["Phone"] == (user.get("Phone") or "")) &
            (st.session_state.attendance["Org"] == (user.get("Org") or ""))
        ].sort_values(by=["Clock In Date", "Time"], ascending=[False, False])

        if user_attendance.empty:
            st.info(tr("no_records"))
        else:
            st.dataframe(user_attendance.reset_index(drop=True))

    elif menu == tr("admin_view"):
        admin_view(st.session_state.logged_in_user)
