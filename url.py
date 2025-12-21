"""
Job URL content fetcher and summarizer.
Uses LinkedIn Guest API to fetch job content and OpenRouter API to summarize it.
"""

import requests
import re
from bs4 import BeautifulSoup
import markdownify
from dotenv import load_dotenv
from utils import get_openrouter_client

load_dotenv()


def extract_linkedin_job_id(url: str) -> str:
    """
    Extract job ID from LinkedIn job URL.
    
    Args:
        url: LinkedIn job URL (e.g., https://www.linkedin.com/jobs/view/4333147858)
        
    Returns:
        str: The job ID extracted from the URL
        
    Raises:
        ValueError: If the URL is not a valid LinkedIn job URL or job ID cannot be extracted
    """
    # Pattern to match LinkedIn job URLs and extract the ID
    # Matches: /jobs/view/4333147858 or /jobs/view/4333147858/ or /jobs/view/4333147858?params
    pattern = r'/jobs/view/(\d+)'
    match = re.search(pattern, url)
    
    if not match:
        raise ValueError(f"Could not extract job ID from LinkedIn URL: {url}")
    
    return match.group(1)


def fetch_job_content(job_url: str) -> str:
    """
    Fetch job content from a LinkedIn URL using LinkedIn Guest API.
    
    Args:
        job_url: The URL of the LinkedIn job posting
        
    Returns:
        str: Markdown content of the job posting with title and description
        
    Raises:
        ValueError: If job ID cannot be extracted from URL
        requests.RequestException: If the request fails
        Exception: If HTML parsing fails or required elements are missing
    """
    # Extract job ID from URL
    job_id = extract_linkedin_job_id(job_url)
    print(f"[DEBUG] Extracted job ID: {job_id}")
    
    # Build Guest API URL
    guest_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
    print(f"[DEBUG] Fetching from: {guest_url}")
    
    # Make request with User-Agent header to avoid blocking
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        # Add timeout to prevent hanging (10 seconds for connect, 30 for read)
        print("[DEBUG] Sending request to LinkedIn...")
        response = requests.get(guest_url, headers=headers, timeout=(10, 30))
        print(f"[DEBUG] Response status code: {response.status_code}")
        response.raise_for_status()
    except requests.Timeout:
        raise Exception("Request timed out. LinkedIn may be slow to respond. Please try again.")
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch job content: {str(e)}")
    
    # Parse HTML with BeautifulSoup
    print("[DEBUG] Parsing HTML...")
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extract title
    title_tag = soup.find("h2")
    title = title_tag.text.strip() if title_tag else "N/A"
    print(f"[DEBUG] Found title: {title}")
    
    # Extract description and convert to Markdown
    description_div = soup.find("div", {"class": "description__text"})
    if not description_div:
        raise Exception("Could not find job description in the HTML response")
    
    print("[DEBUG] Converting to markdown...")
    markdown_text = markdownify.markdownify(str(description_div))
    print(f"[DEBUG] Markdown length: {len(markdown_text)} characters")
    
    # Return formatted content
    return f"# {title}\n\n{markdown_text}"


# def summarize_job_content(job_content: str) -> dict:
#     """
#     Summarize job content focusing on title, description, and requirements.
    
#     Args:
#         job_content: The raw job content in markdown format
        
#     Returns:
#         dict: Contains 'summary' with structured job information
#     """
#     client = get_openrouter_client()
    
#     prompt = f"""Analyze the following job posting and extract key information. Focus specifically on:

# 1. Job Title
# 2. Job Description (main responsibilities and what the role entails)
# 3. Job Requirements (required skills, qualifications, experience)

# Job Content:
# {job_content}

# Please provide a clean, structured summary that highlights:
# - The exact job title
# - A concise description of the role and responsibilities (2-3 sentences)
# - Key requirements and qualifications (as bullet points)

# Format your response in a clear, readable way."""
    
#     response = client.chat.completions.create(
#         model="nvidia/nemotron-3-nano-30b-a3b:free",
#         messages=[
#             {
#                 "role": "user",
#                 "content": prompt
#             }
#         ],
#         temperature=0.5
#     )
    
#     return {
#         "summary": response.choices[0].message.content,
#         "raw_content_length": len(job_content)
#     }


# def summarize_job_url(job_url: str) -> dict:
#     """
#     Fetch and summarize a LinkedIn job posting from a URL.
    
#     Args:
#         job_url: The URL of the LinkedIn job posting
        
#     Returns:
#         dict: Contains 'summary' and 'raw_content_length'
        
#     Example:
#         >>> result = summarize_job_url("https://www.linkedin.com/jobs/view/4333147858")
#         >>> print(result['summary'])
#     """
#     print("step 1: fetching job content using LinkedIn Guest API")
#     job_content = fetch_job_content(job_url)
#     print(f"step 1: job content fetched: {len(job_content)} characters")

#     return job_content

    # print("step 2: summarizing job content using openrouter")
    # result = summarize_job_content(job_content)
    
    # print("step 3: returning result")
    # print(f"step 3: result: {result['summary']}")
    # return result


if __name__ == "__main__":
    # Example usage
    url = "https://www.linkedin.com/jobs/view/4333147858"
    result = fetch_job_content(url)
    print(result)