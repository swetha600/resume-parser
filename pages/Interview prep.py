import streamlit as st
import PyPDF2
from groq import Groq
import json

# Initialize Groq client - Use environment variable in production!
client = Groq(api_key="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")

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def generate_questions(resume_text, question_type="general"):
    type_prompts = {
        "general": "Generate general interview questions based on the resume content.",
        "technical": "Generate technical interview questions based on the skills and technologies mentioned in the resume.",
        "behavioral": "Generate behavioral interview questions based on the experiences and achievements in the resume.",
        "situational": "Generate situational interview questions based on the role and responsibilities mentioned in the resume."
    }
    
    prompt = f"""
    Analyze the following resume and generate 5 relevant {question_type} interview questions.
    For each question, also provide:
    1. The reasoning behind asking this question
    2. What to look for in a good answer
    3. Follow-up questions if needed
    
    Resume:
    {resume_text}
    
    Format your response as JSON with the following structure:
    {{
        "questions": [
            {{
                "question": "The main question",
                "reasoning": "Why this question is relevant",
                "good_answer_criteria": "What makes a good answer",
                "follow_ups": ["Follow up question 1", "Follow up question 2"]
            }}
        ]
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}

# Streamlit UI
st.title("Resume-Based Interview Question Generator")
st.write("Upload a resume to generate customized interview questions")

# File upload
uploaded_file = st.file_uploader("Upload resume (PDF)", type="pdf")

if uploaded_file:
    # Extract text
    resume_text = extract_text_from_pdf(uploaded_file)
    
    # Question type selection
    question_type = st.selectbox(
        "Select the type of questions to generate",
        ["general", "technical", "behavioral", "situational"]
    )
    
    if st.button("Generate New Questions"):
        with st.spinner("Generating questions..."):
            questions_data = generate_questions(resume_text, question_type)
            
            if "error" in questions_data:
                st.error(f"Error generating questions: {questions_data['error']}")
            else:
                for i, q in enumerate(questions_data["questions"], 1):
                    with st.expander(f"Question {i}: {q['question']}"):
                        st.markdown("### Reasoning")
                        st.write(q["reasoning"])
                        
                        st.markdown("### What Makes a Good Answer")
                        st.write(q["good_answer_criteria"])
                        
                        if q["follow_ups"]:
                            st.markdown("### Follow-up Questions")
                            for follow_up in q["follow_ups"]:
                                st.write(f"- {follow_up}")
                                
                st.success("Questions generated successfully! Click 'Generate New Questions' to get more questions.")

else:
    st.info("Please upload a resume to generate questions.")

# Sidebar with tips
with st.sidebar:
    st.markdown("### Question Types")
    st.markdown("""
    - **General**: Basic questions about experience and background
    - **Technical**: Skills and technology-specific questions
    - **Behavioral**: Past experiences and handling situations
    - **Situational**: Hypothetical scenario-based questions
    """)
    
    st.markdown("### Tips for Good Answers")
    st.markdown("""
    - Use the STAR method for behavioral questions
    - Provide specific examples
    - Keep answers concise but detailed
    - Focus on measurable impacts
    - Be honest and authentic
    """)