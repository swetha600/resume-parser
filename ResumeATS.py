import streamlit as st
import os
from groq import Groq
import PyPDF2
import io

# Initialize Groq client - Use environment variable in production!
client = Groq(api_key="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")

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def analyze_resume(resume_text, job_description):
    prompt = f"""
    You are an ATS (Applicant Tracking System) expert. Analyze the following resume against the job description.
    Provide a score out of 100 and detailed feedback.
    
    Job Description:
    {job_description}
    
    Resume:
    {resume_text}
    
    Provide your analysis in the following format:
    Score: [number]
    Keyword Match: [list key matching terms]
    Missing Keywords: [list important missing terms]
    Strengths: [bullet points]
    Areas for Improvement: [bullet points]
    Format and Structure: [feedback]
    """
    
    try:
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error analyzing resume: {str(e)}"

# Streamlit UI
st.title("Resume ATS Score Calculator")
st.write("Upload your resume and paste the job description to get an ATS score and improvement suggestions.")

# File upload
uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")
job_description = st.text_area("Paste the job description here", height=200)

if st.button("Analyze Resume") and uploaded_file and job_description:
    with st.spinner("Analyzing your resume..."):
        # Extract text from PDF
        resume_text = extract_text_from_pdf(uploaded_file)
        
        # Get analysis
        analysis = analyze_resume(resume_text, job_description)
        
        # Display results
        st.markdown("### Analysis Results")
        st.write(analysis)
        
        # Additional tips
        st.markdown("### General Resume Tips")
        st.info("""
        - Use relevant keywords from the job description naturally throughout your resume
        - Quantify achievements with specific metrics when possible
        - Keep formatting clean and consistent
        - Proofread carefully for errors
        - Use action verbs to describe your experiences
        """)