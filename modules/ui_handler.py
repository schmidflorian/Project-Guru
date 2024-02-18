
from typing import List, Tuple
import os
from dotenv import load_dotenv
import streamlit as st
from PyPDF2 import PdfReader


class UIHandler:
    @staticmethod
    def initialize_chat_history():
        return st.session_state.get("chat_history", [])

    @staticmethod
    def append_to_chat_history(chat_history: List[Tuple[str, str]], role: str, message: str):
        chat_history.append((role, message))
        st.session_state.chat_history = chat_history

    @staticmethod
    def extract_pdf_text(pdf):
        pdf_reader = PdfReader(pdf)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text

    @staticmethod
    def get_user_question(tab):
        with tab:
            return st.text_input("Frag etwas zur Wissensdatenbank")

    @staticmethod
    def display_conversation(tab, chat_history):
        with tab:
            st.write("Unterhaltung:")
            for role, message in chat_history:
                if role == "User":
                    st.write(f"👤: {message}")
                else:
                    st.write(f"🤖: {message}")
