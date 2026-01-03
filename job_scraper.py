"""
Job scraper module using JobSpy library.
Provides job search functionality across multiple job boards.
"""

import pandas as pd
from jobspy import scrape_jobs
import streamlit as st


# Job keywords for the intro page
JOB_KEYWORDS = [
    "Software Engineer",
    "Data Scientist",
    "Machine Learning Engineer",
    "DevOps Engineer",
    "Backend Developer",
    "Frontend Developer",
    "Full Stack Developer",
    "Product Manager",
    "Cloud Engineer",
    "Data Analyst",
]


@st.cache_data(ttl=3600, show_spinner=False)
def search_jobs(keyword: str, location: str = "San Francisco, CA", results_wanted: int = 20) -> pd.DataFrame:
    """
    Search for jobs using JobSpy across multiple job boards.
    Results are cached for 1 hour to avoid rate limiting.
    
    Args:
        keyword: Job search term (e.g., "Software Engineer")
        location: Location to search in (default: "San Francisco, CA")
        results_wanted: Number of results to return (default: 20)
        
    Returns:
        pd.DataFrame: DataFrame containing job listings with columns like
                      title, company, location, job_url, description, etc.
    """
    try:
        jobs = scrape_jobs(
            site_name=["indeed", "linkedin", "zip_recruiter", "google"],
            search_term=keyword,
            google_search_term=f"{keyword} jobs near {location}",
            location=location,
            results_wanted=results_wanted,
            hours_old=72,
            country_indeed='USA',
            verbose=0,  # Suppress logs
        )
        
        # Clean up the dataframe - keep only essential columns
        columns_to_keep = [
            'site', 'title', 'company', 'location', 'job_url', 
            'description', 'job_type', 'date_posted', 
            'min_amount', 'max_amount', 'currency', 'is_remote'
        ]
        
        # Keep only columns that exist in the result
        available_columns = [col for col in columns_to_keep if col in jobs.columns]
        jobs = jobs[available_columns]
        
        # Fill NaN values for display
        jobs = jobs.fillna('')
        
        return jobs
        
    except Exception as e:
        # Return empty dataframe on error
        print(f"Error scraping jobs: {e}")
        return pd.DataFrame()


def format_salary(row: pd.Series) -> str:
    """
    Format salary information from a job row.
    
    Args:
        row: A row from the jobs DataFrame
        
    Returns:
        str: Formatted salary string or empty string if not available
    """
    min_amt = row.get('min_amount', '')
    max_amt = row.get('max_amount', '')
    currency = row.get('currency', 'USD')
    
    if min_amt and max_amt:
        return f"{currency} {min_amt:,.0f} - {max_amt:,.0f}"
    elif min_amt:
        return f"{currency} {min_amt:,.0f}+"
    elif max_amt:
        return f"Up to {currency} {max_amt:,.0f}"
    return ""


def get_job_by_index(jobs_df: pd.DataFrame, index: int) -> dict:
    """
    Get a job from the dataframe by index as a dictionary.
    
    Args:
        jobs_df: DataFrame of jobs
        index: Index of the job to retrieve
        
    Returns:
        dict: Job details as a dictionary
    """
    if index < 0 or index >= len(jobs_df):
        return {}
    return jobs_df.iloc[index].to_dict()

