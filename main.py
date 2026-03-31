from groq_utility import generate_response, _load_local_env
import streamlit as st
import io
import os

CSS = """
<style>
.history-wrap{max-height: 400px; overflow-y: auto; padding-right: 6px;}
.qa-card{
    border: 1px solid #e6e6e6;
    background: #ffffff;
    border-radius: 8px;
    padding: 14px 16px;
    margin: 10px 0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
.q{font-weight: 700; color: #0a6ebd; margin-bottom: 8px;}
.a{white-space: pre-wrap; color: #333;line-height: 1.5;}
</style>
"""

def export_bytes(history):
    text = "".join([f"Q{i}: {h['question']}\nA{i}: {h['answer']}\n\n" for i, h in enumerate(history, 1)])
    return io.BytesIO(text.encode("utf-8"))

def setup_ui():
    _load_local_env()
    st.set_page_config(page_title="AI Teaching Assistant", layout="centered")
    st.title("🤖 AI Teaching Assistant")
    st.write("Ask me what you want to learn! I can help with explanations, examples, and more.")
    st.session_state.setdefault("history", [])

    if not os.getenv("GROQ_API_KEY"):
        st.info('Add your Groq key in a local `.env` file: `GROQ_API_KEY="your_groq_api_key"`')

    col_clear, col_export = st.columns([1, 2])
    with col_clear:
        if st.button("🧹Clear History"):
            st.session_state.history = []
            st.rerun()

    with col_export:
        if st.session_state["history"]:
            st.download_button(
                "📥 Export History",
                data=export_bytes(st.session_state.history),
                file_name="chat_history.txt",
                mime="text/plain",
            )
    user_input = st.text_input("Your question:")
    if st.button("Ask"):
        q = user_input.strip()
        if q:
            with st.spinner("Generating answer..."):
                a = generate_response(q, temperature=0.5, max_tokens=65536)
                st.session_state.history.append({"question": q, "answer": a})
                st.rerun()
        else:
            st.warning("Please enter a question before asking.")
    
    st.markdown("### Conversation History")
    st.markdown(CSS, unsafe_allow_html=True)

    cards = []
    for i, h in enumerate(st.session_state.history, 1):
        cards.append(f'<div class="qa-card"><div class="q">Q{i}: {h["question"]}</div><div class="a">A{i}: {h["answer"]}</div></div>')
    st.markdown('<div class="history-wrap">' + "".join(cards) + "</div>", unsafe_allow_html=True)

def main():
    setup_ui()

if __name__ == "__main__":
    main()
