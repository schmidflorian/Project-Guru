
from typing import List, Tuple
import os
from dotenv import load_dotenv
import streamlit as st
from PyPDF2 import PdfReader
from modules.pdf_chunker import get_chunks

from langchain.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback
from modules.UI_Handler import UIHandler
from langchain.prompts import PromptTemplate
from base64 import b64encode
from modules.pdf_extractor import get_pdf_file_paths
from modules.pdf_chunker import get_documents_from_file
from pathlib import Path

prompt_template1 = """You are thorough expert in SIA standards in switzerland that provides helpfull and 100 percent accurate answers to the question asked by the user. 

Here is an exampe of a perfect answer structure:

Ja, es gibt spezielle Maßnahmen und Empfehlungen, um sicherzustellen, dass die Baustoffe trocken bleiben. Gemäß Abschnitt 4.2.1 der Norm 271_d_2021 sind Baustoffe trocken zu halten und der Untergrund muss bei Sichtprüfung besenrein, ebenflächig, frei von Überzähnen, entsprechend trocken und trittfest sein. Zusätzlich werden in Abschnitt 2.4.2 spezifische Anforderungen für den wasserdichten Witterungsschutz während der Bauzeit genannt. Diese Maßnahmen und Empfehlungen dienen dazu, sicherzustellen, dass die Baustoffe vor Feuchtigkeit geschützt bleiben.

Paragraph: (put the paragraph number here) Page: (put the page number here) Document Title: (Put the document title number here)

Here is the question: {question}

ONLY USE GERMAN FOR YOUR ANSWERS!

Make sure you find the exact answer to the question and provide the user with the most accurate information. PLEASE DO NOT PROVIDE ANY FALSE INSFORMATION IF YOU ARE NOT SURE ABOUT THE ANSWER.

When you are ready, please provide the answer to the question with the paragraph number and page number of where you found the answer. End your answer with the document title PLEASE!.

"""

prompt_template2 = """
Subject Expertise: You are recognized as a thorough expert in SIA (Swiss Society of Engineers and Architects) standards within Switzerland. Your role is to provide helpful, accurate, and 100 percent reliable answers to user inquiries based on these standards.

Answer Structure: Please adhere to the following structure for your responses:
Initial Confirmation: Start with a direct answer to the user's question.
Detailed Explanation: Follow with a detailed explanation, citing specific measures and recommendations as applicable.
Reference Citation: Conclude with the exact paragraph number, page number, and document title from the SIA standards that support your answer.

Example of a Perfect Answer:
"Ja, es gibt spezielle Maßnahmen und Empfehlungen, um sicherzustellen, dass die Baustoffe trocken bleiben. Gemäß Abschnitt 4.2.1 der Norm 271_d_2021 sind Baustoffe trocken zu halten und der Untergrund muss bei Sichtprüfung besenrein, ebenflächig, frei von Überzähnen, entsprechend trocken und trittfest sein. Zusätzlich werden in Abschnitt 2.4.2 spezifische Anforderungen für den wasserdichten Witterungsschutz während der Bauzeit genannt. Diese Maßnahmen und Empfehlungen dienen dazu, sicherzustellen, dass die Baustoffe vor Feuchtigkeit geschützt bleiben.

Paragraph: (insert paragraph number here)
Page: (insert page number here)
Document Title: (insert document title here)"

Here is the question: {question}


Language Requirement: Your answers must be provided in German ONLY.

Accuracy Assurance: It is imperative to deliver the most accurate information possible. If you are uncertain about the answer, please do not provide potentially false information. Instead, state that the answer is not within your current knowledge base.
Question Handling: When you receive a question, integrate it seamlessly into your response, ensuring you address the query fully.
Final Note: Upon completing your answer, please include the paragraph number and page number where you found the information, and conclude with the document title.
"""
prompt_template = """


Here is the question: {question}
Give as much detail as possible in your answer.
Make sure you answer is german only, and provide page number and THE EXACT paragraph number of where you found the information.


"""

prompt = PromptTemplate.from_template(prompt_template)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=3000, chunk_overlap=200, length_function=len)


def get_qa_chain():
    llm = OpenAI(model_name=os.getenv("OPENAI_MODEL_NAME"))
    return load_qa_chain(llm, chain_type="stuff")


@st.cache_data
def create_knowledge_base_from_pdfs():
    embeddings = OpenAIEmbeddings()
    try:
        #raise TypeError("Only integers are allowed")
        print("~Try to load local knowledge base...")
        local = FAISS.load_local("faiss_index", embeddings)
        print("~Local Knowledge base found!")
        return local
    except:
        print("~No knowledge base found, create...")
        chunks = get_chunks(text_splitter, get_pdf_file_paths())
        knowledge_base = get_knowledge_base(chunks, embeddings)
        knowledge_base.save_local("faiss_index")
    return knowledge_base


def get_knowledge_base(chunks, embeddings):
    return FAISS.from_documents(chunks, embeddings)


def show_pdf(tab, file_path, page_number):
    if file_path is None:
        return
    with open(file_path, "rb") as f:
        base64_pdf = b64encode(f.read()).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}#page={page_number}" width="800" height="800" type="application/pdf"></iframe>'
    with tab:
        st.markdown(pdf_display, unsafe_allow_html=True)


def main():
    load_dotenv()
    st.set_page_config(page_title="ERNE Projekt-Guru")
    tab_chat, tab_knowledge_base = st.tabs(["Chat", "Wissen"])
    with tab_chat:
        st.header("ERNE Projekt-Guru 💬")

        ui = UIHandler()

        # Initialize chat history
        chat_history = ui.initialize_chat_history()

        print("New PDF, Creating Knowledge base...")
        st.session_state.knowledge_base = create_knowledge_base_from_pdfs()
        print("Done creating knowledge base")
        # callback to handle file upload

    with tab_knowledge_base:
        st.header("Wissen 🧑‍🎓")
        st.file_uploader("Zusätzliches PDF zur Wissensdatenbank hinzufügen", type="pdf",
                         key="pdf", on_change=handle_file_upload)
        # File uploader with on_change callback
        list_of_files = [file.stem for file in Path(
            r"\\ernesrv105.erne.net\Offerten Intrexx\2023_EHB_316968\01 Ausschreibung\Test Projektguru").rglob("*.pdf")]
        for file in list_of_files:
            st.markdown(f"* 📄 {file}")

    # Extract the text
    if "knowledge_base" in st.session_state:
        knowledge_base = st.session_state.knowledge_base
        knowledge_base = create_knowledge_base_from_pdfs()
        # Show user input
        user_question = ui.get_user_question(tab_chat)

        if user_question:

            docs = knowledge_base.similarity_search_with_relevance_scores(
                user_question)
            relevance_score = docs[0][1]

            metadata = None
            if relevance_score == docs[0][1] < .5:
                docs = []
            else:
                metadata = docs[0][0].metadata

            docs = [document for document, _ in docs]
            chain = get_qa_chain()

            with get_openai_callback() as cb:
                # prmompt formatted string
                prompt_string = prompt.format(question=user_question)

                response = chain.run(input_documents=docs,
                                     question=prompt_string)

                new_response = response
                if relevance_score > .5:
                    new_response = response + "\n\n" + \
                        "Relevanz: " + str(relevance_score.round(2))

            # Append the conversation to the chat history with different icons
            ui.append_to_chat_history(chat_history, "User", user_question)
            ui.append_to_chat_history(chat_history, "AI", new_response)

            # Display the entire conversation with icons
            ui.display_conversation(tab_chat, chat_history)
            print("~page",  metadata['page'])
            if metadata:
                print("~metadata", metadata['source'])
                show_pdf(tab_chat, metadata['source'], metadata['page'])


def handle_file_upload():
    pdf = st.session_state.pdf
    tmp_location = os.path.join('resources/pdfs', pdf.name)
    with open(tmp_location, "wb") as f:
        f.write(pdf.getbuffer())

    if pdf is not None:
        chunks = get_documents_from_file(text_splitter, tmp_location)
        knowledge_base = st.session_state.knowledge_base
        knowledge_base.add_documents(chunks)
        knowledge_base.save_local("faiss_index")
        st.session_state.knowledge_base = knowledge_base


if __name__ == '__main__':
    main()
