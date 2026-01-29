import streamlit as st
from supabase import create_client
import bcrypt
import re
import time
from datetime import datetime

st.set_page_config(
    page_title="User Authentication System",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)


st.markdown("""
<style>
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0px); }
}
@keyframes slideIn {
    from { transform: translateX(-20px); opacity: 0; }
    to { transform: translateX(0px); opacity: 1; }
}
.main-container {
    animation: fadeIn 0.8s ease-in-out;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 40px;
    border-radius: 15px;
    box-shadow: 0 8px 32px rgba(31,38,135,0.37);
}
</style>
""", unsafe_allow_html=True)

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "page" not in st.session_state:
    st.session_state.page = "home"

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())


def register_user(username, email, password, confirm_password):
    if not username or not email or not password:
        st.warning("⚠️ Please fill all fields")
        return False

    if len(username) < 3:
        st.warning("⚠️ Username must be at least 3 characters")
        return False

    if len(password) < 6:
        st.warning("⚠️ Password must be at least 6 characters")
        return False

    if password != confirm_password:
        st.warning("⚠️ Passwords do not match")
        return False

    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        st.warning("⚠️ Invalid email")
        return False

    try:
        supabase.table("users").insert({
            "username": username,
            "email": email,
            "password": hash_password(password)
        }).execute()
        return True
    except:
        st.error("❌ Username or Email already exists")
        return False

def login_user(username, password):
    try:
        res = supabase.table("users") \
            .select("password") \
            .eq("username", username) \
            .single() \
            .execute()
        return verify_password(password, res.data["password"])
    except:
        return False

def get_user_count():
    return supabase.table("users").select("id", count="exact").execute().count

st.markdown("<h1 style='text-align:center;color:#667eea;'>🔐 Secure Auth</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#666;'>Login or Register to Continue</p>", unsafe_allow_html=True)
st.markdown("---")

with st.sidebar:
    mode = st.radio("Choose an option", ["🔑 Login", "📝 Register"])
    st.markdown("---")
    st.metric("Total Users", get_user_count())
    st.metric("Status", "Online" if st.session_state.logged_in else "Offline")


if st.session_state.logged_in:
    col1, col2, col3, col4, col5 = st.columns(5)
    if col1.button("🏠 Home"): st.session_state.page = "home"
    if col2.button("👤 Profile"): st.session_state.page = "profile"
    if col3.button("📊 Dashboard"): st.session_state.page = "dashboard"
    if col4.button("⚙️ Settings"): st.session_state.page = "settings"
    if col5.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

    st.markdown("---")

    if st.session_state.page == "home":
        st.markdown(f"""
        <div style='text-align:center;padding:30px;'>
            <h1 style='color:#667eea;'>Welcome Back 👋</h1>
            <h2 style='color:#764ba2;'>{st.session_state.username}</h2>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()

    elif st.session_state.page == "profile":
        st.subheader("👤 User Profile")
        st.write("Username:", st.session_state.username)
        st.write("Member Since:", datetime.now().strftime("%B %d, %Y"))

    elif st.session_state.page == "dashboard":
        st.subheader("📊 Dashboard")
        st.metric("Total Sessions", 24)
        st.metric("Tasks Completed", 156)

    elif st.session_state.page == "settings":
        st.subheader("⚙️ Settings")
        st.toggle("Email Notifications", True)
        st.toggle("Push Notifications", True)


else:
    if mode == "🔑 Login":
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                if login_user(u, p):
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.success("✅ Login Successful")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")

    else:
        with st.form("register"):
            u = st.text_input("Username")
            e = st.text_input("Email")
            p = st.text_input("Password", type="password")
            cp = st.text_input("Confirm Password", type="password")
            if st.form_submit_button("Register"):
                if register_user(u, e, p, cp):
                    st.success("✅ Registration Successful")
                    st.balloons()
                    time.sleep(1)
                    st.rerun()


st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#999;font-size:12px;'>
<p>🔐 Secure Authentication System | Streamlit + Supabase</p>
<p>© 2026 All Rights Reserved</p>
</div>
""", unsafe_allow_html=True)
