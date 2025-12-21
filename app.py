import streamlit as st
import pymupdf4llm
import tempfile
import pathlib
from llm_analysis import generate_job_projects
from url import fetch_job_content

# Set page configuration
st.set_page_config(
    page_title="Job Match Analyzer - Get Project Recommendations",
    page_icon="🎯",
    layout="wide"
)

# App title and description
st.title("🎯 Job Match Analyzer - Get Project Recommendations")
st.markdown("Upload your resume and paste a job description to get 5 personalized hands-on projects that will help you prepare for the role")
st.divider()

# Create split-screen layout
left_col, right_col = st.columns([1, 1])

# LEFT COLUMN - Inputs
with left_col:
    st.header("📄 Input Section")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=['pdf'])
    
    resume_text = None
    
    if uploaded_file is not None:
        # Display file details
        st.success(f"✅ Uploaded: {uploaded_file.name}")
        
        # Create a temporary file to save the uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        try:
            # Process the PDF using pymupdf4llm
            with st.spinner("Converting PDF to Markdown..."):
                resume_text = pymupdf4llm.to_markdown(tmp_path)
            
            st.success("✅ Resume processed successfully!")
            
            # Optional: Show resume preview in an expander
            with st.expander("📄 View Resume Content"):
                st.markdown(resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text)
            
        except Exception as e:
            st.error(f"❌ Error processing PDF: {str(e)}")
            resume_text = None
        
        finally:
            # Clean up temporary file
            try:
                pathlib.Path(tmp_path).unlink()
            except:
                pass
    
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
            # Clear any stale data
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
    can_analyze = uploaded_file is not None and resume_text is not None and has_job_info
    
    if not can_analyze and (uploaded_file is not None or job_description or 'fetched_job_content' in st.session_state):
        if not uploaded_file:
            st.warning("⚠️ Please upload a resume PDF")
        elif not resume_text:
            st.warning("⚠️ Resume processing failed")
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
        # Show instructions when no analysis has been run
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
        # Generate and display analysis
        try:
            # Determine which job description to use (either/or, not both)
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
            
            for i, project in enumerate(result["projects"][:5]):  # Ensure max 5 projects
                with st.expander(f"**Project {i+1}: {project['title']}**", expanded=(i==0)):
                    # Description
                    st.markdown(project['description'])
                    
                    st.markdown("---")
                    
                    # Main Steps
                    st.markdown("**📋 Main Steps:**")
                    for step_idx, step in enumerate(project['steps'], 1):
                        st.markdown(f"{step_idx}. {step}")
                    
                    st.markdown("")
                    
                    # Skills Learned
                    st.markdown("**🎓 Skills You'll Learn:**")
                    skills_text = " • ".join(project['skills'])
                    st.markdown(f"*{skills_text}*")
            
            st.divider()
            
            # Download option
            # Create a formatted markdown document of all projects
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
    <p>Powered by AI • Upload your resume and job description to get started</p>
</div>
""", unsafe_allow_html=True)
