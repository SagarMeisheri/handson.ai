import streamlit as st
import pymupdf4llm
import tempfile
import pathlib
from llm_analysis import generate_job_projects, generate_projects_from_job
from url import fetch_job_content
from job_scraper import search_jobs, JOB_KEYWORDS, format_salary

# Set page configuration
st.set_page_config(
    page_title="HandsOn.AI - Job Search & Project Recommendations",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Keyword button grid styling */
    .keyword-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
        padding: 10px 0;
    }
    
    /* Job card styling */
    .job-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border-left: 4px solid #e94560;
        transition: transform 0.2s ease;
    }
    
    .job-card:hover {
        transform: translateX(4px);
    }
    
    .job-card h4 {
        color: #ffffff;
        margin: 0 0 8px 0;
        font-size: 1.1rem;
    }
    
    .job-card .company {
        color: #e94560;
        font-weight: 600;
        margin-bottom: 4px;
    }
    
    .job-card .location {
        color: #a0a0a0;
        font-size: 0.9rem;
    }
    
    .job-card .source {
        color: #0f3460;
        background: #e94560;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        display: inline-block;
        margin-top: 8px;
    }
    
    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    /* Keyword button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    /* Project card styling */
    .project-header {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# SIDEBAR - Mode Selection & Resume Upload
# ============================================================================

with st.sidebar:
    st.markdown("## 🚀 HandsOn.AI")
    st.markdown("---")
    
    # Mode selection
    mode = st.radio(
        "Choose Mode",
        options=["🔍 Job Search", "📄 Resume Analyzer"],
        index=0,
        help="Job Search: Browse jobs and get project ideas. Resume Analyzer: Upload resume + job description for personalized projects."
    )
    
    st.markdown("---")
    
    # Resume upload (available in both modes)
    st.markdown("### 📎 Resume (Optional)")
    uploaded_file = st.file_uploader(
        "Upload PDF for personalized recommendations",
        type=['pdf'],
        help="Your resume helps tailor project recommendations to your skill gaps"
    )
    
    resume_text = None
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        try:
            resume_text = pymupdf4llm.to_markdown(tmp_path)
            st.session_state.resume_text = resume_text
            st.success(f"✅ {uploaded_file.name}")
        except Exception as e:
            st.error(f"Error: {str(e)}")
        finally:
            try:
                pathlib.Path(tmp_path).unlink()
            except:
                pass
    
    # Show resume preview if available
    if 'resume_text' in st.session_state and st.session_state.resume_text:
        with st.expander("Preview Resume"):
            st.markdown(st.session_state.resume_text[:500] + "..." if len(st.session_state.resume_text) > 500 else st.session_state.resume_text)
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #888; font-size: 0.8rem;'>
        Powered by AI<br/>
        <a href='https://github.com/speedyapply/JobSpy' target='_blank' style='color: #e94560;'>JobSpy</a> + OpenRouter
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# JOB SEARCH MODE
# ============================================================================

if mode == "🔍 Job Search":
    
    # Header
    st.markdown("<h1 class='main-header'>🔍 Job Search & Project Ideas</h1>", unsafe_allow_html=True)
    st.markdown("Click a job category to find opportunities, then get AI-powered project recommendations for any role")
    st.divider()
    
    # Initialize session state
    if 'selected_keyword' not in st.session_state:
        st.session_state.selected_keyword = None
    if 'jobs_df' not in st.session_state:
        st.session_state.jobs_df = None
    if 'selected_job_index' not in st.session_state:
        st.session_state.selected_job_index = None
    if 'job_projects' not in st.session_state:
        st.session_state.job_projects = None
    
    # ----- STEP 1: Keyword Selection Grid -----
    if st.session_state.selected_keyword is None:
        st.markdown("### 🎯 Select a Job Category")
        
        # Create 2x5 grid of keyword buttons
        cols = st.columns(2)
        for idx, keyword in enumerate(JOB_KEYWORDS):
            col_idx = idx % 2
            with cols[col_idx]:
                # Create unique gradient colors for each button
                colors = [
                    ("🧑‍💻", "#667eea", "#764ba2"),  # Purple
                    ("📊", "#f093fb", "#f5576c"),  # Pink
                    ("🤖", "#4facfe", "#00f2fe"),  # Cyan
                    ("⚙️", "#43e97b", "#38f9d7"),  # Green
                    ("🔧", "#fa709a", "#fee140"),  # Orange-pink
                    ("🎨", "#a18cd1", "#fbc2eb"),  # Lavender
                    ("💻", "#ff9a9e", "#fecfef"),  # Soft pink
                    ("📋", "#667eea", "#764ba2"),  # Purple
                    ("☁️", "#4facfe", "#00f2fe"),  # Cyan
                    ("📈", "#43e97b", "#38f9d7"),  # Green
                ]
                icon = colors[idx % len(colors)][0]
                
                if st.button(
                    f"{icon} {keyword}",
                    key=f"keyword_{idx}",
                    use_container_width=True,
                    type="secondary"
                ):
                    st.session_state.selected_keyword = keyword
                    st.session_state.jobs_df = None
                    st.session_state.selected_job_index = None
                    st.session_state.job_projects = None
                    st.rerun()
    
    # ----- STEP 2: Job Results List -----
    elif st.session_state.selected_keyword and st.session_state.selected_job_index is None:
        
        # Back button and header
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state.selected_keyword = None
                st.session_state.jobs_df = None
                st.rerun()
        with col2:
            st.markdown(f"### 📋 Jobs for: **{st.session_state.selected_keyword}**")
        
        # Fetch jobs if not already cached
        if st.session_state.jobs_df is None:
            with st.spinner(f"🔍 Searching for {st.session_state.selected_keyword} jobs across Indeed, LinkedIn, Google & ZipRecruiter..."):
                st.session_state.jobs_df = search_jobs(st.session_state.selected_keyword)
        
        jobs_df = st.session_state.jobs_df
        
        if jobs_df is None or len(jobs_df) == 0:
            st.warning("No jobs found. Try a different category or check your internet connection.")
            if st.button("🔄 Try Again"):
                st.session_state.jobs_df = None
                st.rerun()
        else:
            st.success(f"Found {len(jobs_df)} jobs!")
            
            # Display job cards
            for idx, row in jobs_df.iterrows():
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.markdown(f"""
                        <div class='job-card'>
                            <h4>{row.get('title', 'N/A')}</h4>
                            <div class='company'>🏢 {row.get('company', 'Unknown Company')}</div>
                            <div class='location'>📍 {row.get('location', 'Location not specified')}</div>
                            <span class='source'>{str(row.get('site', '')).upper()}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        if st.button("View & Get Projects →", key=f"job_{idx}", use_container_width=True):
                            st.session_state.selected_job_index = idx
                            st.session_state.job_projects = None
                            st.rerun()
    
    # ----- STEP 3: Job Details & Project Recommendations -----
    elif st.session_state.selected_job_index is not None:
        jobs_df = st.session_state.jobs_df
        job_idx = st.session_state.selected_job_index
        
        if jobs_df is None or job_idx >= len(jobs_df):
            st.error("Job not found. Please go back and try again.")
            if st.button("← Back to Jobs"):
                st.session_state.selected_job_index = None
                st.rerun()
        else:
            job = jobs_df.iloc[job_idx]
            
            # Back button
            if st.button("← Back to Job List"):
                st.session_state.selected_job_index = None
                st.session_state.job_projects = None
                st.rerun()
            
            st.divider()
            
            # Two-column layout: Job details | Project recommendations
            left_col, right_col = st.columns([1, 1])
            
            with left_col:
                st.markdown("### 📋 Job Details")
                
                # Job header card
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 20px; border-radius: 12px; margin-bottom: 16px;'>
                    <h2 style='color: #fff; margin: 0 0 10px 0;'>{job.get('title', 'N/A')}</h2>
                    <p style='color: #e94560; font-size: 1.2rem; margin: 0 0 8px 0;'>🏢 {job.get('company', 'Unknown Company')}</p>
                    <p style='color: #a0a0a0; margin: 0;'>📍 {job.get('location', 'Location not specified')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Job metadata
                meta_cols = st.columns(3)
                with meta_cols[0]:
                    job_type = job.get('job_type', '')
                    if job_type:
                        st.metric("Job Type", str(job_type).title())
                with meta_cols[1]:
                    is_remote = job.get('is_remote', '')
                    if is_remote:
                        st.metric("Remote", "Yes" if is_remote else "No")
                with meta_cols[2]:
                    salary = format_salary(job)
                    if salary:
                        st.metric("Salary", salary)
                
                # Job URL
                job_url = job.get('job_url', '')
                if job_url:
                    st.markdown(f"[🔗 View Original Posting]({job_url})")
                
                # Job description
                st.markdown("#### Description")
                description = job.get('description', 'No description available.')
                if description and len(str(description)) > 50:
                    with st.expander("View Full Description", expanded=True):
                        st.markdown(str(description)[:3000])
                else:
                    st.info("No detailed description available for this job.")
            
            with right_col:
                st.markdown("### 🚀 Project Recommendations")
                
                # Check for resume
                resume_for_analysis = st.session_state.get('resume_text', None)
                if resume_for_analysis:
                    st.info("📎 Using your resume for personalized recommendations")
                else:
                    st.info("💡 Upload a resume in the sidebar for personalized gap analysis")
                
                # Generate projects button or show cached results
                if st.session_state.job_projects is None:
                    if st.button("🎯 Generate 3 Project Ideas", type="primary", use_container_width=True):
                        description = str(job.get('description', ''))
                        if not description or len(description) < 50:
                            description = f"Role: {job.get('title', 'Software Engineer')} at {job.get('company', 'Tech Company')}. Looking for candidates with relevant skills and experience."
                        
                        with st.spinner("🤖 Generating project recommendations... This may take 30-60 seconds"):
                            try:
                                result = generate_projects_from_job(
                                    job_description=description,
                                    job_title=str(job.get('title', '')),
                                    company=str(job.get('company', '')),
                                    resume_text=resume_for_analysis
                                )
                                st.session_state.job_projects = result
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error generating projects: {str(e)}")
                                st.info("Make sure you have set up your OPENROUTER_API_KEY in a .env file")
                else:
                    # Display cached projects
                    result = st.session_state.job_projects
                    
                    # Analysis summary
                    st.markdown("#### 📊 Analysis")
                    st.success(result.get("analysis_summary", "Analysis complete."))
                    
                    st.markdown("---")
                    
                    # Display 3 projects
                    for i, project in enumerate(result.get("projects", [])[:3]):
                        with st.expander(f"**Project {i+1}: {project.get('title', 'Project')}**", expanded=(i == 0)):
                            st.markdown(project.get('description', ''))
                            
                            st.markdown("**📋 Steps:**")
                            for step_idx, step in enumerate(project.get('steps', []), 1):
                                st.markdown(f"{step_idx}. {step}")
                            
                            st.markdown("")
                            st.markdown("**🎓 Skills You'll Learn:**")
                            skills = project.get('skills', [])
                            st.markdown(f"*{' • '.join(skills)}*")
                    
                    # Regenerate button
                    if st.button("🔄 Regenerate Projects", use_container_width=True):
                        st.session_state.job_projects = None
                        st.rerun()


# ============================================================================
# RESUME ANALYZER MODE (Existing Flow)
# ============================================================================

elif mode == "📄 Resume Analyzer":
    
    st.markdown("<h1 class='main-header'>📄 Resume Analyzer</h1>", unsafe_allow_html=True)
    st.markdown("Upload your resume and paste a job description to get 5 personalized hands-on projects")
    st.divider()
    
    # Get resume from session state (uploaded in sidebar)
    resume_text = st.session_state.get('resume_text', None)
    
    # Create split-screen layout
    left_col, right_col = st.columns([1, 1])
    
    # LEFT COLUMN - Inputs
    with left_col:
        st.header("📄 Input Section")
        
        # Resume status
        if resume_text:
            st.success("✅ Resume uploaded via sidebar")
            with st.expander("📄 View Resume Content"):
                st.markdown(resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text)
        else:
            st.warning("⚠️ Please upload a resume PDF in the sidebar")
        
        # URL Input Section
        st.markdown("### 🔗 Fetch Job from URL")
        job_url = st.text_input(
            "Enter job posting URL (LinkedIn, Indeed, etc.)",
            placeholder="https://www.linkedin.com/jobs/view/...",
            help="We'll fetch and summarize the job details for you"
        )
        
        fetch_button = st.button("🔍 Fetch Job Details", use_container_width=True)
        
        if fetch_button and job_url:
            try:
                with st.spinner("Fetching job details from URL... This may take 30-60 seconds"):
                    result = fetch_job_content(job_url)
                    st.session_state.fetched_job_content = result
                    st.session_state.fetched_job_url = job_url
                    st.success("✅ Job details fetched successfully!")
            except Exception as e:
                st.error(f"❌ Error fetching job details: {str(e)}")
                st.info("💡 Please check the URL and try again, or paste the job description manually below")
                if 'fetched_job_content' in st.session_state:
                    del st.session_state.fetched_job_content
                if 'fetched_job_url' in st.session_state:
                    del st.session_state.fetched_job_url
        
        # Show fetched content if available
        if 'fetched_job_content' in st.session_state and st.session_state.fetched_job_content:
            st.info(f"📌 Using job details from: {st.session_state.fetched_job_url}")
            with st.expander("👁️ View Fetched Job Summary"):
                st.markdown(st.session_state.fetched_job_content)
        
        st.divider()
        
        # Job Description Input (Manual)
        st.markdown("### 📋 Or Paste Job Description Manually")
        job_description = st.text_area(
            "Paste the job description here",
            height=300,
            placeholder="Paste the complete job description including requirements, responsibilities, and qualifications...",
            help="Alternative to URL: Provide as much detail as possible for better project recommendations"
        )
        
        # Validation and Analysis Button
        has_job_info = (len(job_description.strip()) >= 50) or ('fetched_job_content' in st.session_state and st.session_state.fetched_job_content)
        can_analyze = resume_text is not None and has_job_info
        
        if not can_analyze and (resume_text is not None or job_description or 'fetched_job_content' in st.session_state):
            if not resume_text:
                st.warning("⚠️ Please upload a resume PDF in the sidebar")
            elif not has_job_info:
                st.info("💡 Please either fetch job details from URL or paste job description manually (at least 50 characters)")
        
        analyze_button = st.button(
            "🎯 Generate Project Recommendations",
            type="primary",
            disabled=not can_analyze,
            use_container_width=True
        )
    
    # RIGHT COLUMN - Results
    with right_col:
        st.header("🎯 AI Analysis & Project Recommendations")
        
        if not analyze_button:
            st.info("👈 Upload your resume and paste a job description, then click the button to generate personalized project recommendations")
            
            with st.expander("ℹ️ How it works"):
                st.markdown("""
                **Our AI analyzes:**
                - Your current skills and experience from your resume
                - The requirements and responsibilities in the job description
                - Skill gaps and growth opportunities
                
                **You get:**
                - 5 hands-on project recommendations tailored to the role
                - Step-by-step implementation guides
                - Clear mapping of skills you'll learn
                - Projects designed to bridge the gap between your current profile and the target role
                
                **Note:** Make sure you have an OpenRouter API key set in your `.env` file.
                """)
        else:
            try:
                # Determine which job description to use
                if 'fetched_job_content' in st.session_state and st.session_state.fetched_job_content:
                    final_job_description = st.session_state.fetched_job_content
                    job_source = "URL"
                else:
                    final_job_description = job_description
                    job_source = "Manual Input"
                
                with st.spinner("🤖 Analyzing resume and job description... This may take 30-60 seconds"):
                    result = generate_job_projects(resume_text, final_job_description)
                
                st.success(f"✅ Analysis complete! Here are your personalized projects (Job source: {job_source})")
                
                # Display analysis summary
                st.markdown("### 📊 Gap Analysis")
                st.info(result["analysis_summary"])
                
                st.divider()
                
                # Display projects
                st.markdown("### 🎯 Recommended Projects")
                st.markdown("*Complete these projects to strengthen your candidacy for this role*")
                
                for i, project in enumerate(result["projects"][:5]):
                    with st.expander(f"**Project {i+1}: {project['title']}**", expanded=(i==0)):
                        st.markdown(project['description'])
                        st.markdown("---")
                        st.markdown("**📋 Main Steps:**")
                        for step_idx, step in enumerate(project['steps'], 1):
                            st.markdown(f"{step_idx}. {step}")
                        st.markdown("")
                        st.markdown("**🎓 Skills You'll Learn:**")
                        skills_text = " • ".join(project['skills'])
                        st.markdown(f"*{skills_text}*")
                
                st.divider()
                
                # Download option
                download_content = f"# Job Match Analysis - Project Recommendations\n\n"
                download_content += f"## Gap Analysis\n{result['analysis_summary']}\n\n"
                download_content += f"## Recommended Projects\n\n"
                
                for i, project in enumerate(result["projects"][:5], 1):
                    download_content += f"### Project {i}: {project['title']}\n\n"
                    download_content += f"{project['description']}\n\n"
                    download_content += f"**Main Steps:**\n"
                    for step_idx, step in enumerate(project['steps'], 1):
                        download_content += f"{step_idx}. {step}\n"
                    download_content += f"\n**Skills You'll Learn:** {', '.join(project['skills'])}\n\n"
                    download_content += "---\n\n"
                
                st.download_button(
                    label="📥 Download All Projects as Markdown",
                    data=download_content,
                    file_name="job_match_projects.md",
                    mime="text/markdown",
                    use_container_width=True
                )
                
            except ValueError as ve:
                st.error(f"❌ Configuration Error: {str(ve)}")
                st.info("💡 Make sure you have set up your OPENROUTER_API_KEY in a .env file")
            except Exception as e:
                st.error(f"❌ Error generating recommendations: {str(e)}")
                st.info("💡 Please try again or check your inputs")


# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.8em;'>
    <p>HandsOn.AI • Find jobs, build projects, land your dream role</p>
</div>
""", unsafe_allow_html=True)
