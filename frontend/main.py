import streamlit as st
from streamlit_theme import st_theme

# Configure the app
st.set_page_config(
    page_title="CyberBOT",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Theme detection using st-theme
theme = st_theme()
is_dark_mode = theme.get("base") == "dark" if theme else False

# Choose correct DMML logo
dmml_logo = "assets/dmml-white.png" if is_dark_mode else "assets/dmml-black.png"

# Theme-aware color palette
heading_color = "#FFC627" if is_dark_mode else "#8C1D40"          # ASU Gold or Maroon
text_color = "#DDDDDD" if is_dark_mode else "#444444"
quote_border_color = "#FFC627"                                     # Always gold
button_color = "#8C1D40"                                           # Maroon
button_hover = "#6B0F2B"                                           # Darker Maroon

# Custom CSS
st.markdown(
    f"""
    <style>
        img {{
            border-radius: 0 !important;
        }}

        .main-container {{
            text-align: center;
            margin-top: 20px;
        }}

        .logo-container {{
            display: flex;
            justify-content: center;
        }}

        .student-access-btn {{
            display: flex;
            justify-content: center;
            margin-top: 20px;
        }}

        .stButton>button {{
            font-size: 18px;
            padding: 12px 30px;
            background-color: {button_color};
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.3s;
            display: block;
            margin: 0 auto;
        }}

        .stButton>button:hover {{
            background-color: {button_hover};
        }}

        .footer {{
            text-align: center;
            font-size: 14px;
            color: #aaa;
            margin-top: 30px;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Logos
st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
with st.container():
    col1, col2, col3 = st.columns([10, 1, 2])
    with col1:
        st.image("assets/asu_logo.png", use_container_width=True)
    with col3:
        st.image(dmml_logo, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# Heading
st.markdown(
    f"""
    <div class="main-container">
        <h1 style='color: {heading_color};'>Welcome to CyberBOT</h1>
        <p style='font-size: 20px; color: {text_color};'>
            Your AI-powered learning companion for Cloud Computing and Cybersecurity!
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Quote
st.markdown(
    f"""
    <div class="main-container">
        <blockquote style='font-size: 18px; font-style: italic; color: {text_color}; border-left: 4px solid {quote_border_color}; padding-left: 10px;'>
        "The best defense against cyberattacks is a well-trained mind and a vigilant eye." – Dr. Bruce Schneier
        </blockquote>
    </div>
    """,
    unsafe_allow_html=True,
)

# Spacer
st.markdown("<br>", unsafe_allow_html=True)

# Signup Button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Student Access / Signup"):
        st.switch_page("pages/access.py")


# Footer with styled hyperlink
st.markdown(
    f"""
    <br><hr>
    <div class="footer">
        Arizona State University<sup>®</sup> | Powered by the 
        <a href="https://dmml.asu.edu" target="_blank" style="color: {heading_color}; text-decoration: none;">
            Data Mining and Machine Learning Lab (DMML)
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)
