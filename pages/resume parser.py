import streamlit as st
from groq import Groq
import PyPDF2
import docx
import io
import json

# Initialize Groq client
GROQ_API_KEY = "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"

def extract_text_from_pdf(file):
    """Extract text from PDF file"""
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(file):
    """Extract text from DOCX file"""
    doc = docx.Document(file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def parse_resume_with_groq(resume_text):
    """Parse resume using Groq API"""
    client = Groq(api_key=GROQ_API_KEY)
    
    prompt = f"""
    Analyze the following resume and extract key information in JSON format:
    
    Resume:
    {resume_text}
    
    Please provide:
    1. Contact Information (name, email, phone, location)
    2. Professional Summary
    3. Skills (technical and soft skills)
    4. Work Experience (company, role, duration, responsibilities)
    5. Education (degree, institution, year)
    6. Certifications (if any)
    7. Projects (if any)
    
    Format the response as structured JSON.
    """
    
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2000
    )
    
    return response.choices[0].message.content

def get_improvement_suggestions(resume_text):
    """Get resume improvement suggestions using Groq API"""
    client = Groq(api_key=GROQ_API_KEY)
    
    prompt = f"""
    Analyze this resume and provide detailed improvement suggestions:
    
    Resume:
    {resume_text}
    
    Please provide:
    1. Overall Assessment (strengths and weaknesses)
    2. Content Improvements (what to add, remove, or modify)
    3. Formatting Suggestions
    4. Keyword Optimization (for ATS systems)
    5. Action Verbs to Use
    6. Quantifiable Achievements (how to add metrics)
    7. Section-by-Section Recommendations
    8. Industry-Specific Tips
    
    Be specific and actionable in your suggestions.
    """
    
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=3000
    )
    
    return response.choices[0].message.content

def main():
    st.set_page_config(page_title="Resume Parser & Analyzer", page_icon="📄", layout="wide")
    
    st.title("📄 AI-Powered Resume Parser & Analyzer")
    st.markdown("Upload your resume to get detailed analysis and improvement suggestions powered by Groq AI")
    
    # Sidebar
    st.sidebar.header("About")
    st.sidebar.info(
        "This tool uses Groq's LLaMA model to:\n"
        "- Parse resume content\n"
        "- Extract key information\n"
        "- Provide improvement suggestions\n"
        "- Optimize for ATS systems"
    )
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload your resume (PDF or DOCX)", 
        type=['pdf', 'docx'],
        help="Upload your resume in PDF or DOCX format"
    )
    
    if uploaded_file is not None:
        # Extract text based on file type
        try:
            if uploaded_file.type == "application/pdf":
                resume_text = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                resume_text = extract_text_from_docx(uploaded_file)
            else:
                st.error("Unsupported file format")
                return
            
            st.success("✅ Resume uploaded successfully!")
            
            # Display extracted text
            with st.expander("📝 View Extracted Text"):
                st.text_area("Resume Content", resume_text, height=300)
            
            # Create tabs for different analyses
            tab1, tab2 = st.tabs(["📊 Parsed Information", "💡 Improvement Suggestions"])
            
            with tab1:
                st.header("Parsed Resume Information")
                with st.spinner("Analyzing resume..."):
                    parsed_data = parse_resume_with_groq(resume_text)
                    st.markdown(parsed_data)
            
            with tab2:
                st.header("Resume Improvement Suggestions")
                with st.spinner("Generating improvement suggestions..."):
                    suggestions = get_improvement_suggestions(resume_text)
                    st.markdown(suggestions)
                
                # Additional features
                st.subheader("🎯 Quick Tips")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info(
                        "**ATS Optimization:**\n"
                        "- Use standard section headers\n"
                        "- Include relevant keywords\n"
                        "- Avoid tables and graphics\n"
                        "- Use common fonts"
                    )
                
                with col2:
                    st.info(
                        "**Content Tips:**\n"
                        "- Start bullets with action verbs\n"
                        "- Quantify achievements\n"
                        "- Tailor to job description\n"
                        "- Keep it concise (1-2 pages)"
                    )
        
        except Exception as e:
            st.error(f"Error processing resume: {str(e)}")
    
    else:
        # Display instructions
        st.info("👆 Please upload your resume to get started")
        
        st.markdown("---")
        st.subheader("What This Tool Analyzes:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**📋 Content Analysis**")
            st.write("- Contact information")
            st.write("- Professional summary")
            st.write("- Work experience")
            st.write("- Education & skills")
        
        with col2:
            st.markdown("**🎨 Format Review**")
            st.write("- Structure & layout")
            st.write("- Section organization")
            st.write("- Readability")
            st.write("- ATS compatibility")
        
        with col3:
            st.markdown("**💡 Suggestions**")
            st.write("- Content improvements")
            st.write("- Keyword optimization")
            st.write("- Achievement metrics")
            st.write("- Industry best practices")

if __name__ == "__main__":
    main()
