import streamlit as st
from groq import Groq
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def initialize_groq_client():
    # Get API key from hardcoded value
    api_key = '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'
    return Groq(api_key=api_key)

def generate_questions(client, job_description, num_questions=5):
    prompt = f"""
    Based on this job description, generate {num_questions} technical multiple-choice questions that would be relevant 
    for interviewing candidates. Make the questions challenging but fair.
    
    Job Description:
    {job_description}
    
    Format your response as JSON with this structure:
    {{
        "questions": [
            {{
                "question": "The question text",
                "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
                "correct_answer": "A",
                "explanation": "Why this is the correct answer and what it tests for"
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
        
        # Parse JSON response
        response_text = response.choices[0].message.content
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        return json.loads(response_text[json_start:json_end])
    except Exception as e:
        st.error(f"Error generating questions: {str(e)}")
        return None

def initialize_session_state():
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'total_questions' not in st.session_state:
        st.session_state.total_questions = 0
    if 'questions_data' not in st.session_state:
        st.session_state.questions_data = None
    if 'show_explanation' not in st.session_state:
        st.session_state.show_explanation = False

def display_score():
    score_percentage = (st.session_state.score / st.session_state.total_questions * 100) if st.session_state.total_questions > 0 else 0
    st.sidebar.markdown("### Score")
    st.sidebar.write(f"Current Score: {st.session_state.score}/{st.session_state.total_questions}")
    st.sidebar.write(f"Percentage: {score_percentage:.1f}%")

def main():
    st.title("Infinite Job Interview Quiz Generator")
    
    initialize_session_state()
    
    # Sidebar for score display only
    with st.sidebar:
        st.header("Score Tracking")
        display_score()
    
    # Main area
    if 'job_description' not in st.session_state:
        st.markdown("### Enter Job Description")
        job_description = st.text_area(
            "Paste the job description here:",
            height=200,
            help="Paste the full job description to generate relevant questions"
        )
        
        if st.button("Start Quiz"):
            if job_description:
                st.session_state.job_description = job_description
                st.rerun()
            else:
                st.error("Please enter a job description first!")
    
    else:
        # Generate new questions if needed
        client = initialize_groq_client()
        if not st.session_state.questions_data:
            with st.spinner("Generating new questions..."):
                st.session_state.questions_data = generate_questions(client, st.session_state.job_description)
        
        # Display current question
        if st.session_state.questions_data and 'questions' in st.session_state.questions_data:
            current_q = st.session_state.questions_data['questions'][st.session_state.current_question]
            
            st.markdown(f"### Question {st.session_state.total_questions + 1}")
            st.write(current_q['question'])
            
            answer = st.radio("Select your answer:", current_q['options'], key=f"q_{st.session_state.total_questions}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Submit Answer"):
                    st.session_state.show_explanation = True
                    if answer and answer.startswith(current_q['correct_answer']):
                        st.success("✅ Correct!")
                        st.session_state.score += 1
                    else:
                        st.error("❌ Incorrect")
                    st.info(f"Explanation: {current_q['explanation']}")
            
            with col2:
                if st.button("Next Question"):
                    st.session_state.show_explanation = False
                    st.session_state.total_questions += 1
                    st.session_state.current_question = (st.session_state.current_question + 1) % len(st.session_state.questions_data['questions'])
                    
                    # Generate new questions if we've used all current ones
                    if st.session_state.current_question == 0:
                        st.session_state.questions_data = generate_questions(client, st.session_state.job_description)
                    
                    st.rerun()
            
            # Reset button
            if st.button("Reset Quiz"):
                for key in ['current_question', 'score', 'total_questions', 'questions_data', 'job_description', 'show_explanation']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

if __name__ == "__main__":
    main()