from dotenv import load_dotenv
import streamlit as st
import os
import PyPDF2
from transformers import pipeline
import edge_tts
import asyncio

# Load environment variables
load_dotenv()

# Load summarization pipeline
summarization_pipeline = pipeline("summarization", model="Falconsai/text_summarization")

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to generate summary
def summarize_text(text):
    summary = summarization_pipeline(text, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
    return summary

# Function to convert text to speech using EdgeTTS
async def text_to_speech(text, output_file="output.mp3"):
    communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
    await communicate.save(output_file)
    return output_file

# Initialize Streamlit app
st.set_page_config(page_title="PDF Summarizer with Text-to-Speech", page_icon="📄")
st.header("PDF Summarizer with Text-to-Speech")

# File uploader for PDF
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file is not None:
    # Extract text from PDF
    text = extract_text_from_pdf(uploaded_file)
    st.subheader("Extracted Text from PDF")
    st.write(text)  # Display extracted text (optional)

    # Summarize the text
    st.subheader("Summary of the PDF")
    with st.spinner("Generating summary..."):
        summary = summarize_text(text)
        st.write(summary)

    # Text-to-Speech Conversion
    st.subheader("Text-to-Speech")
    if st.button("Convert Summary to Speech"):
        with st.spinner("Generating audio..."):
            # Convert summary to speech
            output_file = asyncio.run(text_to_speech(summary))
            st.success("Audio generated successfully!")

            # Play audio
            st.audio(output_file, format="audio/mp3")

            # Download audio
            with open(output_file, "rb") as f:
                st.download_button(
                    label="Download Audio",
                    data=f,
                    file_name="summary_audio.mp3",
                    mime="audio/mp3"
                )