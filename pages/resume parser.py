import streamlit as st
import PyPDF2
import docx2txt
import re
import spacy
from pathlib import Path
import io

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    st.error("Please install spaCy and the English model first with:")
    st.code("pip install spacy\npython -m spacy download en_core_web_sm")
    st.stop()

class ResumeParser:
    def __init__(self):
        self.text = ""
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_pattern = r'(\+\d{1,3}[-.]?)?\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        self.skills_pattern = self._get_skills_pattern()

    def _get_skills_pattern(self):
        """Define common skills to look for"""
        skills = [
            # Programming Languages
            "Python", "Java", "JavaScript", "C++", "C#", "Ruby", "PHP", "Swift",
            # Web Technologies
            "HTML", "CSS", "React", "Angular", "Vue.js", "Node.js", "Django", "Flask",
            # Databases
            "SQL", "MySQL", "PostgreSQL", "MongoDB", "Oracle",
            # Tools & Platforms
            "Git", "Docker", "AWS", "Azure", "Linux", "Jenkins", "Kubernetes",
            # Data Science
            "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Pandas", "NumPy",
            # Microsoft Office
            "Excel", "Word", "PowerPoint", "Outlook"
        ]
        return r'\b(?:' + '|'.join(skills) + r')\b'

    def extract_text_from_pdf(self, pdf_file):
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
            return ""

    def extract_text_from_docx(self, docx_file):
        """Extract text from DOCX file"""
        try:
            text = docx2txt.process(docx_file)
            return text
        except Exception as e:
            st.error(f"Error reading DOCX: {str(e)}")
            return ""

    def parse_resume(self, file):
        """Parse resume file and extract information"""
        # Extract text based on file type
        file_ext = Path(file.name).suffix.lower()
        
        if file_ext == '.pdf':
            self.text = self.extract_text_from_pdf(file)
        elif file_ext in ['.docx', '.doc']:
            self.text = self.extract_text_from_docx(file)
        else:
            st.error("Unsupported file format. Please upload a PDF or DOCX file.")
            return None

        if not self.text:
            return None

        # Process text with spaCy
        doc = nlp(self.text)

        # Extract information
        return {
            'name': self.extract_name(doc),
            'email': self.extract_email(),
            'phone': self.extract_phone(),
            'skills': self.extract_skills(),
            'education': self.extract_education(doc),
            'experience': self.extract_experience(doc)
        }

    def extract_name(self, doc):
        """Extract name using spaCy NER"""
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text
        return "Not found"

    def extract_email(self):
        """Extract email using regex"""
        emails = re.findall(self.email_pattern, self.text)
        return emails[0] if emails else "Not found"

    def extract_phone(self):
        """Extract phone number using regex"""
        phones = re.findall(self.phone_pattern, self.text)
        return phones[0] if phones else "Not found"

    def extract_skills(self):
        """Extract skills using regex pattern matching"""
        skills = re.findall(self.skills_pattern, self.text, re.IGNORECASE)
        return list(set(skills))

    def extract_education(self, doc):
        """Extract education information"""
        education = []
        edu_keywords = ["degree", "university", "college", "school", "bachelor", "master", "phd"]
        
        for sent in doc.sents:
            if any(keyword in sent.text.lower() for keyword in edu_keywords):
                education.append(sent.text.strip())
        
        return education

    def extract_experience(self, doc):
        """Extract work experience information"""
        experience = []
        exp_keywords = ["experience", "work", "employment", "job", "position"]
        
        for sent in doc.sents:
            if any(keyword in sent.text.lower() for keyword in exp_keywords):
                experience.append(sent.text.strip())
        
        return experience

def main():
    st.set_page_config(page_title="Resume Parser", page_icon="📄")
    st.title("📄 Resume Parser")
    st.write("Upload a resume (PDF or DOCX) to extract information")

    # Initialize parser
    parser = ResumeParser()

    # File upload
    uploaded_file = st.file_uploader("Choose a resume file", type=["pdf", "docx"])

    if uploaded_file:
        with st.spinner("Parsing resume..."):
            # Parse resume
            results = parser.parse_resume(uploaded_file)

            if results:
                # Display results
                st.header("Extracted Information")

                # Basic Information
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Basic Information")
                    st.write(f"**Name:** {results['name']}")
                    st.write(f"**Email:** {results['email']}")
                    st.write(f"**Phone:** {results['phone']}")

                # Skills
                with col2:
                    st.subheader("Skills")
                    if results['skills']:
                        st.write(", ".join(results['skills']))
                    else:
                        st.write("No skills found")

                # Education
                st.subheader("Education")
                if results['education']:
                    for edu in results['education']:
                        st.write(f"- {edu}")
                else:
                    st.write("No education information found")

                # Experience
                st.subheader("Experience")
                if results['experience']:
                    for exp in results['experience']:
                        st.write(f"- {exp}")
                else:
                    st.write("No experience information found")

if __name__ == "__main__":
    main()