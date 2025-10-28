"""
Streamlit Frontend for Recruitment AI Agent
"""
import streamlit as st
import requests
import os
from typing import List
import json

# Local document extraction for frontend
def extract_text_from_upload(uploaded_file):
    """Extract text from uploaded file"""
    try:
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        
        if file_ext == '.pdf':
            import PyPDF2
            import io
            uploaded_file.seek(0)  # Reset file pointer
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        elif file_ext in ['.doc', '.docx']:
            from docx import Document
            import io
            uploaded_file.seek(0)  # Reset file pointer
            doc = Document(io.BytesIO(uploaded_file.read()))
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        elif file_ext == '.txt':
            uploaded_file.seek(0)  # Reset file pointer
            return uploaded_file.read().decode('utf-8')
        else:
            return ""
    except Exception as e:
        st.error(f"Error extracting text: {str(e)}")
        return ""

# Page config
st.set_page_config(
    page_title="Recruitment AI Agent",
    page_icon="🤖",
    layout="wide"
)

# API Base URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")


def main():
    st.title("🤖 Recruitment AI Agent")
    st.markdown("AI-powered candidate evaluation and matching platform")
    
    # Sidebar for AI Provider Selection
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        ai_provider = st.selectbox(
            "Select AI Model",
            ["OpenAI", "Gemini", "Groq", "Ollama"],
            help="Choose the AI model for analysis"
        )
        
        if ai_provider == "OpenAI":
            api_key = st.text_input("OpenAI API Key", type="password")
            os.environ["OPENAI_API_KEY"] = api_key
            provider_code = "openai"
        elif ai_provider == "Gemini":
            api_key = st.text_input("Gemini API Key", type="password")
            os.environ["GEMINI_API_KEY"] = api_key
            provider_code = "gemini"
        elif ai_provider == "Groq":
            api_key = st.text_input("Groq API Key", type="password")
            os.environ["GROQ_API_KEY"] = api_key
            provider_code = "groq"
        else:  # Ollama
            api_key = None
            provider_code = "ollama"
        
        use_ai = st.checkbox("Use AI for Analysis", value=True)
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Job Description", "📄 Resume Matching", "📧 Email Generation", "🗄️ Database View"])
    
    # Tab 1: Job Description
    with tab1:
        st.header("Job Description Input")
        
        input_method = st.radio(
            "Select Input Method",
            ["Upload File", "Manual Input", "AI Generate"],
            horizontal=True
        )
        
        if input_method == "Upload File":
            uploaded_file = st.file_uploader(
                "Upload Job Description",
                type=["pdf", "doc", "docx"],
                help="Upload PDF or DOC/DOCX file"
            )
            
            if uploaded_file and st.button("Extract Job Description"):
                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                try:
                    response = requests.post(f"{API_BASE_URL}/job-description/upload", files=files)
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state['job_description'] = data['job_description']
                        st.session_state['job_description_id'] = data['metadata'].get('job_description_id')
                        st.success("Job description extracted successfully!")
                    else:
                        st.error(f"Error: {response.json()['detail']}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        elif input_method == "Manual Input":
            job_description_text = st.text_area(
                "Enter Job Description",
                height=300,
                placeholder="Paste or type the job description here..."
            )
            
            if st.button("Save Job Description"):
                if job_description_text:
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/job-description/input",
                            params={"job_description": job_description_text}
                        )
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state['job_description'] = data['job_description']
                            st.session_state['job_description_id'] = data['metadata'].get('job_description_id')
                            st.success("Job description saved!")
                        else:
                            st.error(f"Error: {response.json()['detail']}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                else:
                    st.warning("Please enter a job description")
        
        else:  # AI Generate
            st.subheader("Generate Job Description with AI")
            
            col1, col2 = st.columns(2)
            with col1:
                job_title = st.text_input("Job Title", placeholder="e.g., Senior Python Developer")
                years_of_exp = st.number_input("Years of Experience", min_value=0, max_value=20, value=5)
                must_have_skills = st.text_input("Must-Have Skills", placeholder="Python, FastAPI, Docker")
            
            with col2:
                company_name = st.text_input("Company Name")
                employment_type = st.selectbox(
                    "Employment Type",
                    ["Full-time", "Part-time", "Contract", "Internship", "Temporary"]
                )
                industry = st.text_input("Industry", placeholder="Technology")
            
            location = st.text_input("Location", placeholder="San Francisco, CA")
            
            if st.button("Generate Job Description", type="primary"):
                with st.spinner("Generating..."):
                    if job_title and must_have_skills:
                        try:
                            payload = {
                                "job_title": job_title,
                                "years_of_experience": years_of_exp,
                                "must_have_skills": must_have_skills,
                                "company_name": company_name,
                                "employment_type": employment_type,
                                "industry": industry,
                                "location": location
                            }
                            
                            params = {"provider": provider_code}
                            if api_key:
                                params["api_key"] = api_key
                            
                            response = requests.post(
                                f"{API_BASE_URL}/job-description/generate",
                                json=payload,
                                params=params
                            )
                            
                            if response.status_code == 200:
                                data = response.json()
                                st.session_state['job_description'] = data['job_description']
                                st.session_state['job_description_id'] = data['metadata'].get('job_description_id')
                                st.success("Job description generated!")
                                
                                # Show generated JD
                                with st.expander("Generated Job Description"):
                                    st.markdown(data['job_description'])
                            else:
                                st.error(f"Error: {response.json()['detail']}")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                    else:
                        st.warning("Please fill in all required fields")
        
        # Display current job description
        if 'job_description' in st.session_state:
            st.divider()
            st.subheader("Current Job Description")
            st.text_area("", st.session_state['job_description'], height=200, disabled=True)
    
    # Tab 2: Resume Matching
    with tab2:
        st.header("Resume Matching")
        
        if 'job_description' not in st.session_state:
            st.warning("Please input a job description first!")
        else:
            # Upload resumes
            uploaded_resumes = st.file_uploader(
                "Upload Resumes (PDF or DOCX)",
                type=["pdf", "doc", "docx"],
                accept_multiple_files=True,
                help="Upload up to 10 resumes"
            )
            
            if len(uploaded_resumes) > 10:
                st.error("Maximum 10 resumes allowed!")
                uploaded_resumes = uploaded_resumes[:10]
            
            if uploaded_resumes and st.button("Match Resumes", type="primary"):
                with st.spinner("Analyzing resumes..."):
                    resume_texts = []
                    resume_filenames = []
                    
                    # Extract text from resumes locally
                    for resume in uploaded_resumes:
                        text = extract_text_from_upload(resume)
                        resume_texts.append(text)
                        resume_filenames.append(resume.name)
                        
                        if not text:
                            st.warning(f"Could not extract text from {resume.name}")
                    
                    # Call matching API
                    try:
                        payload = {
                            "job_description": st.session_state['job_description'],
                            "job_description_id": st.session_state.get('job_description_id'),
                            "resume_texts": resume_texts,
                            "resume_filenames": resume_filenames
                        }
                        
                        params = {"provider": provider_code, "use_ai": use_ai}
                        if api_key:
                            params["api_key"] = api_key
                        
                        response = requests.post(
                            f"{API_BASE_URL}/resume-matching/match",
                            json=payload,
                            params=params
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state['matching_results'] = data
                            st.success("Matching completed! Scroll down to view results.")
                        else:
                            st.error(f"Error: {response.json()['detail']}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            # Display previous results if available
            if 'matching_results' in st.session_state:
                display_results(st.session_state['matching_results'])
    
    # Tab 3: Email Generation
    with tab3:
        st.header("Email Generation")
        
        if 'matching_results' not in st.session_state:
            st.info("Please match resumes first to generate emails")
        else:
            candidates = st.session_state['matching_results']['results']
            
            # Add info about personalization
            st.info("🎯 **New Feature:** Emails are now personalized with specific resume matching insights, including matching skills, experience, and detailed analysis!")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("🎯 Personalized Interview Email (Best Match)")
                if candidates:
                    best_candidate = candidates[0]  # Already sorted by score
                    
                    st.info(f"**Top Candidate:** {best_candidate['filename']} (Score: {best_candidate['score']}%)")
                    
                    candidate_name = st.text_input("Candidate Name", value="John Doe")
                    candidate_email = st.text_input("Candidate Email", value="john.doe@example.com")
                    company_name_email = st.text_input("Company Name", value="Tech Corp")
                    manager_name = st.text_input("Hiring Manager Name", value="Sarah Johnson")
                    
                    if st.button("🎉 Generate Personalized Interview Email", type="primary"):
                        generate_and_show_email(    
                            best_candidate,
                            candidate_name,
                            candidate_email,
                            company_name_email,
                            manager_name,
                            "interview",
                            provider_code,
                            api_key
                        )
            
            with col2:
                selected_candidate_idx = st.selectbox(
                    "Select Candidate",
                    range(len(candidates)),
                    format_func=lambda x: f"{candidates[x]['filename']} (Score: {candidates[x]['score']}%)"
                )
                
                if selected_candidate_idx > 0:  # Skip the best match
                    st.subheader("📝 Personalized Rejection Email (Other Candidates)")
                    candidate = candidates[selected_candidate_idx]
                    
                    st.info(f"**Selected Candidate:** {candidate['filename']} (Score: {candidate['score']}%)")
                    
                    candidate_name = st.text_input("Candidate Name", value="Jane Smith", key="rejection")
                    candidate_email = st.text_input("Candidate Email", value="jane.smith@example.com", key="rejection_email")
                    company_name_email = st.text_input("Company Name", value="Tech Corp", key="rejection_company")
                    manager_name = st.text_input("Hiring Manager Name", value="Sarah Johnson", key="rejection_manager")
                    
                    if st.button("📝 Generate Personalized Rejection Email", type="primary"):
                        generate_and_show_email(
                            candidate,
                            candidate_name,
                            candidate_email,
                            company_name_email,
                            manager_name,
                            "rejection",
                            provider_code,
                            api_key
                        )
    
    # Tab 4: Database View
    with tab4:
        st.header("🗄️ Database View")
        st.markdown("View stored job descriptions and candidate data from MongoDB")
        
        # Database summary
        if st.button("🔄 Refresh Database Data", type="primary"):
            try:
                response = requests.get(f"{API_BASE_URL}/database/summary")
                if response.status_code == 200:
                    st.session_state['db_summary'] = response.json()
                    st.success("Database data refreshed!")
                else:
                    st.error(f"Error: {response.json()['detail']}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        # Display database summary if available
        if 'db_summary' in st.session_state:
            summary = st.session_state['db_summary']
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Job Descriptions", summary.get('total_job_descriptions', 0))
            with col2:
                st.metric("Total Candidates", summary.get('total_candidates', 0))
            with col3:
                st.metric("Total Sessions", summary.get('total_sessions', 0))
            
            st.divider()
            
            # Job Descriptions section
            st.subheader("📝 Job Descriptions")
            job_descriptions = summary.get('job_descriptions', [])
            
            if job_descriptions:
                for i, jd in enumerate(job_descriptions):
                    # Use session state to control expander state
                    expander_state_key = f"jd_expanded_{i}"
                    is_expanded = st.session_state.get(expander_state_key, False)
                    
                    # Create expandable section using checkbox
                    col_header, col_toggle = st.columns([4, 1])
                    with col_header:
                        st.subheader(f"# {i+1} - {jd.get('source', 'Unknown')} ({jd.get('created_at', '')[:10]})")
                    with col_toggle:
                        is_expanded = st.checkbox("Expand", value=is_expanded, key=f"expand_{i}")
                        st.session_state[expander_state_key] = is_expanded
                    
                    if is_expanded:
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write("**Job Description:**")
                            st.text_area("", jd.get('job_description', ''), height=150, disabled=True, key=f"jd_text_{i}")
                        
                        with col2:
                            st.write("**Metadata:**")
                            st.json({
                                "ID": jd.get('_id', ''),
                                "Source": jd.get('source', ''),
                                "Filename": jd.get('filename', 'N/A'),
                                "Created": jd.get('created_at', '')[:19] if jd.get('created_at') else 'N/A'
                            })
                            
                            # Button to view candidates for this job description
                            candidates_loaded = f'candidates_{jd["_id"]}' in st.session_state
                            
                            if not candidates_loaded:
                                if st.button(f"View Candidates", key=f"view_candidates_{i}"):
                                    try:
                                        response = requests.get(f"{API_BASE_URL}/database/job-descriptions/{jd['_id']}/candidates")
                                        if response.status_code == 200:
                                            st.session_state[f'candidates_{jd["_id"]}'] = response.json()['candidates']
                                            st.success("Candidates loaded!")
                                        else:
                                            st.error(f"Error: {response.json()['detail']}")
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")
                            else:
                                if st.button(f"Close Candidates", key=f"close_candidates_{i}"):
                                    del st.session_state[f'candidates_{jd["_id"]}']
                                    st.success("Candidates list closed!")
                        
                        # Display candidates if loaded
                        if f'candidates_{jd["_id"]}' in st.session_state:
                            candidates = st.session_state[f'candidates_{jd["_id"]}']
                            st.write("**Candidates for this Job Description:**")
                            
                            for j, candidate in enumerate(candidates):
                                with st.container():
                                    col1, col2, col3 = st.columns([2, 1, 1])
                                    
                                    with col1:
                                        st.write(f"**{candidate.get('name', 'Unknown')}** ({candidate.get('filename', '')})")
                                        st.write(f"Email: {candidate.get('email', 'N/A')}")
                                        if candidate.get('phone'):
                                            st.write(f"Phone: {candidate.get('phone')}")
                                    
                                    with col2:
                                        st.metric("Score", f"{candidate.get('matching_score', 0):.1f}%")
                                    
                                    with col3:
                                        # Use a different approach for showing details
                                        show_details_key = f"show_details_{i}_{j}"
                                        if st.button("Details", key=f"candidate_details_{i}_{j}"):
                                            st.session_state[show_details_key] = True
                                    
                                    # Show candidate details if requested
                                    show_details = st.session_state.get(f"show_details_{i}_{j}", False)
                                    if show_details:
                                        candidate_data = candidate
                                        
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            st.write("**Matching Skills:**")
                                            for skill in candidate_data.get('matching_skills', [])[:5]:
                                                st.write(f"✅ {skill}")
                                        
                                        with col2:
                                            st.write("**Missing Skills:**")
                                            for skill in candidate_data.get('missing_skills', [])[:5]:
                                                st.write(f"❌ {skill}")
                                        
                                        st.write("**Remarks:**")
                                        st.write(candidate_data.get('remarks', 'No remarks available'))
                                        
                                        # Clear details button
                                        if st.button("Close Details", key=f"close_details_{i}_{j}"):
                                            st.session_state[f"show_details_{i}_{j}"] = False                        
                        st.divider()  # Add divider after each job description
            else:
                st.info("No job descriptions found in database")
        else:
            st.info("Click 'Refresh Database Data' to load information from MongoDB")


def display_results(data):
    """Display matching results"""
    st.subheader("Matching Results")
    
    results = data['results']
    best_match = data.get('best_match')
    
    # Summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Candidates", data['total_candidates'])
    with col2:
        if results:
            st.metric("Best Score", f"{results[0]['score']:.1f}%")
    with col3:
        if best_match:
            st.metric("Selected", best_match['filename'])
    
    # Results table
    if results:
        # Highlight best match
        for idx, result in enumerate(results):
            is_best = idx == 0 and result['score'] >= 70
            
            with st.container():
                if is_best:
                    st.success(f"🏆 **{result['filename']}** - Score: **{result['score']:.1f}%**")
                else:
                    st.write(f"**{result['filename']}** - Score: {result['score']:.1f}%")
                
                # Show details
                with st.expander("View Details"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Matching Skills:**")
                        if result.get('matching_skills'):
                            for skill in result['matching_skills'][:5]:  # Show first 5
                                st.write(f"✅ {skill}")
                        else:
                            st.info("No matching skills identified")
                    
                    with col2:
                        st.write("**Missing Skills:**")
                        if result.get('missing_skills'):
                            for skill in result['missing_skills'][:5]:  # Show first 5
                                st.write(f"❌ {skill}")
                        else:
                            st.success("All required skills present!")
                    
                    st.write("**Remarks:**")
                    st.write(result['remarks'])
                
                st.divider()


def generate_and_show_email(candidate, name, email, company, manager, email_type, provider, api_key=None):
    """Generate and display personalized email with resume matching insights"""
    try:
        # Use the new enhanced endpoint with resume matching data
        params = {
            "provider": provider
        }
        
        if api_key:
            params["api_key"] = api_key
        
        # Include resume matching data for personalization
        matching_result = {
            "score": candidate['score'],
            "matching_skills": candidate.get('matching_skills', []),
            "missing_skills": candidate.get('missing_skills', []),
            "remarks": candidate.get('remarks', ''),
            "resume_info": candidate.get('resume_info', {})  # Include extracted resume information
        }
        
        payload = {
            "candidate_name": name,
            "candidate_email": email,
            "job_description": st.session_state['job_description'],
            "email_type": email_type,
            "company_name": company,
            "hiring_manager_name": manager,
            "matching_result": matching_result
        }
        
        response = requests.post(
            f"{API_BASE_URL}/email/generate-with-matching",
            json=payload,
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            
            st.success("🎉 Personalized email generated!")
            
            # Display email subject and body
            st.text_input("📧 Subject", value=data['email_subject'], disabled=True)
            st.text_area("📝 Email Body", value=data['email_body'], height=300)
            
            # Display personalized insights used
            if data.get('personalized_insights'):
                with st.expander("🎯 Personalized Insights Used", expanded=False):
                    st.markdown("**Resume Matching Analysis:**")
                    st.text(data['personalized_insights'])
                    
                    # Show matching skills breakdown
                    if candidate.get('matching_skills'):
                        st.markdown("**✅ Matching Skills:**")
                        for skill in candidate['matching_skills'][:5]:
                            st.write(f"• {skill}")
                    
                    if candidate.get('missing_skills') and email_type == "rejection":
                        st.markdown("**⚠️ Areas for Growth:**")
                        for skill in candidate['missing_skills'][:3]:
                            st.write(f"• {skill}")
            
            # Show candidate score prominently
            score_color = "green" if candidate['score'] >= 70 else "orange" if candidate['score'] >= 50 else "red"
            st.markdown(f"**📊 Candidate Score: <span style='color: {score_color}'>{candidate['score']}%</span>**", unsafe_allow_html=True)
            
        else:
            st.error(f"❌ Error: {response.json()['detail']}")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()

