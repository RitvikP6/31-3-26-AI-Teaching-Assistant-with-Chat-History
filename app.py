import streamlit as st
import io
import os
from groq_utility import generate_response, _load_local_env

# Load env
_load_local_env()

# Page config
st.set_page_config(page_title="AI Teaching Assistant", layout="centered")

# Custom CSS
st.markdown("""
<style>
.qa-card {
    border-radius: 12px;
    padding: 15px;
    margin: 10px 0;
    background: transparent;  /* ✅ same as app background */
    border: 1px solid rgba(255,255,255,0.1); /* subtle border for dark mode */
}

.q {
    font-weight: bold;
    color: #4da6ff;
}

.a {
    color: inherit; /* ✅ automatically matches theme text color */
    margin-top: 5px;
}
</style>
""", unsafe_allow_html=True)

# Title
st.title("🤖 AI Teaching Assistant")
st.write("Ask anything and learn smarter 🚀")

# Session state
if "history" not in st.session_state:
    st.session_state.history = []

# Export function
def export_chat():
    text = ""
    for i, h in enumerate(st.session_state.history, 1):
        text += f"Q{i}: {h['question']}\nA{i}: {h['answer']}\n\n"
    return io.BytesIO(text.encode())

# Buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("🧹 Clear"):
        st.session_state.history = []
        st.rerun()

with col2:
    st.download_button(
        "📥 Export",
        export_chat(),
        "chat.txt",
        disabled=not st.session_state.history
    )

# Input
question = st.text_input("💬 Ask a question")

if st.button("Ask"):
    if question.strip():
        with st.spinner("Thinking... 🤔"):
            answer = generate_response(question)

        st.session_state.history.append({
            "question": question,
            "answer": answer
        })
        st.rerun()
    else:
        st.warning("Enter a question!")

# Display history
st.subheader("📜 Chat History")

for i, chat in enumerate(st.session_state.history, 1):
    st.markdown(f"""
    <div class="qa-card">
        <div class="q">Q{i}: {chat['question']}</div>
        <div class="a">A{i}: {chat['answer']}</div>
    </div>
    """, unsafe_allow_html=True)