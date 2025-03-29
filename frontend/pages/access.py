import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="CyberBOT - Student Access",
    page_icon="🔐",
    layout="centered",
)

# Custom CSS
st.markdown(
    """
    <style>
        .container {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .content {
            flex: 1;
        }
        .image-container {
            flex: 0.6;
            text-align: center;
        }
        img {
            max-width: 80%;
            height: auto;
        }
        h2 {
            font-size: 24px;
            color: #4CAF50;
            text-align: center;
            margin-bottom: 10px;
        }
        p {
            font-size: 18px;
            color: #555;
            text-align: center;
        }
        .form-container {
            margin-top: 20px;
        }
        .stTabs [data-baseweb="tab-list"] {
            justify-content: center;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Tabs for Student Access and Sign Up
tab1, tab2 = st.tabs(["🎓 Student Access", "Sign Up"])

# 🎓 **Student Access (Login) Tab**
with tab1:
    st.markdown("<h2>Student Access to CyberBOT</h2>", unsafe_allow_html=True)
    
    with st.form("login_form", clear_on_submit=True):
        login_input = st.text_input("Email or Username", placeholder="Enter your email or username")
        password = st.text_input("Password", type="password", placeholder="Enter your password", help="Make sure to use a strong password.")
        col_a, col_b, col_c = st.columns([3, 2, 3])
        with col_b:
            login_button = st.form_submit_button("Access CyberBOT")

        if login_button:
            if not login_input or not password:
                st.error("Please fill in both fields")
            else: 
                payload = {"password": password}
                login_input = login_input.strip()
                if "@" in login_input:
                    payload["email"] = login_input.lower()
                else:
                    payload["username"] = login_input

                response = requests.post(f"{API_URL}/login", json=payload)

                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Debug: Login API response: {data}")
                    st.success("Login successful! 🎉")

                    if "user_id" in data:
                        st.session_state["user_id"] = data["user_id"]
                        print(f"✅ Debug: Stored user_id = {st.session_state['user_id']}")

                        # Reset chat history state so it reloads fresh in chat UI
                        st.session_state["chat_history"] = []
                        st.session_state["last_loaded_user_id"] = None
                    else:
                        print("❌ Debug: `user_id` missing from login response.")

                    # Store login session
                    st.session_state["logged_in"] = True
                    if "@" in login_input:
                        st.session_state["email"] = login_input.lower()
                        st.session_state["username"] = None
                    else:
                        st.session_state["username"] = login_input
                        st.session_state["email"] = None
                    # st.rerun()
                    st.switch_page("pages/chat.py")

                else:
                    try:
                        error_message = response.json().get("detail", "Invalid credentials")
                    except:
                        error_message = "An unexpected error occurred. Please try again."

                    st.error(f"Login failed: {error_message}")

# 📝 **Sign Up Tab (Now Correctly Indented)**
with tab2:
    st.markdown("<h2>Create Your CyberBOT Account</h2>", unsafe_allow_html=True)

    with st.form("signup_form", clear_on_submit=True):
        email = st.text_input("Email Address", placeholder="Enter your email")
        username = st.text_input("Username", placeholder="Choose a username")
        password = st.text_input("Password", type="password", placeholder="Create a password")
        col_a, col_b, col_c = st.columns([5, 3, 4])
        with col_b:
            signup_button = st.form_submit_button("Sign Up")
        
        if signup_button:
            if email and username and password:
                if not email.lower().endswith("@asu.edu"):
                    st.error("⚠️ Registration is restricted to @asu.edu email addresses only.")
                    print("❌ Debug: `email` is not ending with @asu.edu")
                else:
                    response = requests.post(
                        f"{API_URL}/register",
                        json={"email": email, "username": username, "password": password}
                    )

                    if response.status_code == 200:
                        data = response.json()  # ✅ Extract response data
                        st.success("🎉 Account created successfully! Redirecting to chat...")

                        # ✅ Store `user_id` after signup
                        if "user_id" in data:
                            st.session_state["user_id"] = data["user_id"]
                            print(f"✅ Debug: Stored user_id after signup: {st.session_state['user_id']}")
                        else:
                            print("❌ Debug: `user_id` missing from signup response.")

                        # ✅ Store session details
                        st.session_state["logged_in"] = True
                        st.session_state["email"] = email
                        st.session_state["username"] = username

                        print(f"✅ Debug: Stored session state after signup: {st.session_state}")

                        # Redirect to chat
                        st.switch_page("pages/chat.py")

                    else:
                        try:
                            error_msg = response.json().get("detail", "Unknown error from backend.")
                            print(f"❌ Registration failed. API response status: {response.status_code}")
                            print(f"❌ API error detail: {error_msg}")
                            st.error(f"⚠️ Registration failed: {error_msg}")
                        except Exception as e:
                            print(f"❌ Registration failed. Could not parse error: {e}")
                            st.error("⚠️ Registration failed due to an unexpected error.")
            else:
                st.error("⚠️ Please fill in all fields.")
                print("❌ Registration form error: One or more fields missing.")