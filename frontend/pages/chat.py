import streamlit as st
import requests
import json

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="CyberBOT - Chat",
    page_icon="🤖",
)

# ✅ Ensure user is logged in
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("⚠️ Please log in to access CyberBOT.")
    st.stop()

# ✅ Ensure `user_id` exists
if "user_id" not in st.session_state or not st.session_state["user_id"]:
    st.warning("⚠️ Missing user session. Please log out and log in again.")
    st.stop()

user_id = st.session_state["user_id"]

# 🔄 Load stored Q/A history from DB only if it's not loaded OR user switched
if (
    "chat_history" not in st.session_state
    or "last_loaded_user_id" not in st.session_state
    or st.session_state["last_loaded_user_id"] != user_id
):
    try:
        history_response = requests.get(f"{API_URL}/questions/{user_id}")
        if history_response.status_code == 200:
            data = history_response.json()
            st.session_state["chat_history"] = [{"user": qa["question"], "bot": qa["answer"]} for qa in data]
            st.session_state["last_loaded_user_id"] = user_id  # ✅ Mark which user's history was loaded
        else:
            st.warning("⚠️ Could not load stored chat history from server.")
            st.session_state["chat_history"] = []
            st.session_state["last_loaded_user_id"] = user_id
    except Exception as e:
        st.warning(f"⚠️ Error loading history: {e}")
        st.session_state["chat_history"] = []
        st.session_state["last_loaded_user_id"] = user_id

# Sidebar Logout
with st.sidebar:
    st.markdown("### User Session")
    user_display = st.session_state.get("username", st.session_state.get("email", "User"))
    st.info(f"👤 Logged in as: **{user_display}**")

    if st.button("Logout 🚪"):
        # del st.session_state["logged_in"]
        # del st.session_state["email"]
        # del st.session_state["username"]
        # del st.session_state["user_id"]
        # del st.session_state["chat_history"]
        # del st.session_state["last_loaded_user_id"]
        # st.success("You have been logged out.")
        # st.switch_page("pages/access.py")
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("You have been logged out.")
        st.rerun()

# 📢 **Chat UI**
st.markdown("<h2 style='text-align: center;'>CyberBOT</h2>", unsafe_allow_html=True)

# ✅ Initialize chat history if missing
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# 💬 **Display Chat History**
st.markdown("### Your Learning History 📖")
if not st.session_state["chat_history"]:
    st.info("Dive In – Start Building Your Knowledge Library!")

for chat in st.session_state["chat_history"]:
    with st.container():
        st.markdown(f"🧑‍💻 **You:** {chat['user']}")
        st.markdown(f"🤖 **CyberBOT:** {chat['bot']}")

# ✍ **Chat Input Box**
with st.form("chat_form", clear_on_submit=True):
    user_message = st.text_input("Type your question on cloud or cybersecurity – let’s learn together!")
    send_button = st.form_submit_button("Ask CyberBOT")

# 🤖 **Chat Processing**
if send_button:
    if not user_message.strip():
        st.error("⚠️ Please enter a valid question.")
    else:
        # ✅ Send message to FastAPI `/query` endpoint
        response = requests.post(f"{API_URL}/query", json={
            "user_id": user_id,
            "question": user_message
        })

        if response.status_code == 200:
            data = response.json()
            bot_response = data.get("generated_answer", "🤖 AI did not respond.")
            validation_result = data.get("validation_result", "Error")
            confidence_score = data.get("confidence_score", 0.0)

            # ✅ Debugging: Print AI response
            print(f"💬 User asked: {user_message}")
            print(f"🤖 AI responded: {bot_response}")
            print(f"📜 Validation Result: {validation_result} | Confidence Score: {confidence_score}")

            # ✅ Ensure response is valid before storing
            if not bot_response.strip():
                bot_response = "⚠️ Sorry, I couldn't generate an answer."

            # ✅ Store the question-answer pair in the database
            store_payload = {
                "user_id": user_id,  # Ensure user_id is included
                "question": user_message,
                "answer": bot_response,
                "validation_result": validation_result,
                "confidence_score": confidence_score
            }

            # ✅ Debug: Print the request payload before sending
            print(f"📝 Debug: Payload sent to `/questions/`: {store_payload}")

            # ✅ Store the question-answer pair in the database
            store_response = requests.post(
                f"{API_URL}/questions/",
                data=json.dumps(store_payload),
                headers={"Content-Type": "application/json"}
            )

            # ✅ Debug API response
            print(f"📝 Debug: `/questions/` API response: {store_response.status_code} - {store_response.text}")

            if store_response.status_code != 200:
                st.warning(f"⚠️ Failed to store the chat history: {store_response.text}")

        else:
            bot_response = "⚠️ Failed to get a response from AI."
            print(f"❌ Debug: API `/query` request failed: {response.status_code} - {response.text}")

        # ✅ Store response in chat history
        st.session_state["chat_history"].append(
            {"user": user_message, "bot": bot_response}
        )
        st.rerun()
