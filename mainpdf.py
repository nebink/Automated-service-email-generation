import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio import Portfolio
from utils import clean_text
import PyPDF2 

def create_streamlit_app(llm, portfolio, clean_text):
    st.title("📧 Cold Mail Generator")

    # Input section for URL or PDF
    url_input = st.text_input("Enter a URL:", value="https://jobs.nike.com/job/R-46909?from=job%20search%20funnel")
    pdf_file = st.file_uploader("Or upload a job description PDF", type=["pdf"])
    submit_button = st.button("Submit")

    if submit_button:
        try:
            if pdf_file:  # If a PDF is uploaded
                # Extract text from PDF
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                data = " ".join([page.extract_text() for page in pdf_reader.pages])
            elif url_input:  # If a URL is provided
                loader = WebBaseLoader([url_input])
                data = clean_text(loader.load().pop().page_content)
            else:
                st.error("Please provide a URL or upload a PDF.")
                return

            # Existing pipeline
            portfolio.load_portfolio()
            jobs = llm.extract_jobs(data)
            for job in jobs:
                skills = job.get('skills', [])
                links = portfolio.query_links(skills)
                email = llm.write_mail(job, links)
                st.code(email, language='markdown')
        except Exception as e:
            st.error(f"An Error Occurred: {e}")

if __name__ == "__main__":
    chain = Chain()  # Ensure necessary objects are initialized
    portfolio = Portfolio()
    create_streamlit_app(chain, portfolio, clean_text)