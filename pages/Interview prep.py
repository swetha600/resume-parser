import streamlit as st
import PyPDF2
from groq import Groq
import json
import re

# Initialize Groq client - Use environment variable in production!
client = Groq(api_key="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")

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_json_from_response(response_text):
    """Extract JSON from response that might contain markdown or extra text"""
    # Try to find JSON within markdown code blocks
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
    if json_match:
        return json_match.group(1)
    
    # Try to find JSON object directly
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if json_match:
        return json_match.group(0)
    
    return response_text

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
    
    IMPORTANT: Respond ONLY with valid JSON. Do not include any explanatory text, markdown formatting, or code blocks.
    Use exactly this structure:
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
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        
        # Get the response content
        response_content = response.choices[0].message.content
        
        # Debug: Show what we received
        print("Raw response:", response_content[:200])
        
        # Try to extract JSON from the response
        json_content = extract_json_from_response(response_content)
        
        # Parse the JSON
        parsed_data = json.loads(json_content)
        
        # Validate structure
        if "questions" not in parsed_data:
            return {"error": "Invalid response structure: missing 'questions' key"}
        
        return parsed_data
        
    except json.JSONDecodeError as e:
        return {
            "error": f"JSON parsing error: {str(e)}",
            "raw_response": response_content[:500] if 'response_content' in locals() else "No response"
        }
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

# Streamlit UI
st.title("Resume-Based Interview Question Generator")
st.write("Upload a resume to generate customized interview questions")

# File upload
uploaded_file = st.file_uploader("Upload resume (PDF)", type="pdf")

if uploaded_file:
    # Extract text
    resume_text = extract_text_from_pdf(uploaded_file)
    
    # Show preview of extracted text
    with st.expander("Preview extracted resume text"):
        st.text(resume_text[:500] + "..." if len(resume_text) > 500 else resume_text)
    
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
                if "raw_response" in questions_data:
                    with st.expander("Show raw response for debugging"):
                        st.code(questions_data['raw_response'])
            else:
                for i, q in enumerate(questions_data["questions"], 1):
                    with st.expander(f"Question {i}: {q['question']}"):
                        st.markdown("### Reasoning")
                        st.write(q["reasoning"])
                        
                        st.markdown("### What Makes a Good Answer")
                        st.write(q["good_answer_criteria"])
                        
                        if q.get("follow_ups"):
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
