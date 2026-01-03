# 🚀 HandsOn.AI - Job Search & Project Recommendations

An AI-powered Streamlit application with two powerful modes:
1. **Job Search** - Browse jobs from multiple job boards and get AI-generated project recommendations for any role
2. **Resume Analyzer** - Upload your resume and job description to get personalized hands-on projects

## 📸 Screenshots

### Main Interface

![URL Fetching Feature](screenshots/url-fetch-demo.png)
![HandsOn.AI Interface](screenshots/app-demo.png)

*Split-screen interface: Upload resume and job description on the left, get AI-generated project recommendations on the right*


*Fetch job details directly from LinkedIn URLs - no more copy-pasting job descriptions!*

## ✨ Features

### 🔍 Job Search Mode (NEW!)
- **Multi-Platform Job Search** - Search jobs from Indeed, LinkedIn, Google, and ZipRecruiter simultaneously
- **10 Popular Job Categories** - Quick access to Software Engineer, Data Scientist, ML Engineer, DevOps, and more
- **20 Real-Time Results** - Get 20 job listings per search with 1-hour caching
- **3 Project Recommendations** - Click any job to get AI-generated project ideas tailored to that role
- **Optional Resume Integration** - Upload your resume for personalized gap analysis

### 📄 Resume Analyzer Mode
- **PDF Resume Upload** - Upload your resume in PDF format
- **URL Job Fetching** - Automatically fetch job details from LinkedIn URLs
- **Manual Job Description** - Or paste any job description manually
- **AI-Powered Gap Analysis** - Identifies skill gaps between your profile and job requirements
- **5 Custom Project Recommendations** - Get tailored hands-on projects with:
  - Clear project descriptions
  - Step-by-step implementation guides (3-5 steps per project)
  - Skills you'll learn mapped to job requirements
- **Export Projects** - Download all recommendations as a markdown file

### 🆓 Completely Free
- Uses NVIDIA's free Nemotron model via OpenRouter
- No credit card required
- No usage limits

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher (required for JobSpy)
- OpenRouter API key (free - see setup below)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/handson.ai.git
cd handson.ai
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OpenRouter API key (see [API Key Setup](#-openrouter-api-key-setup) below)

4. Run the app:
```bash
streamlit run app.py
```

5. Open your browser at `http://localhost:8501`

## 🔑 OpenRouter API Key Setup

This app uses [OpenRouter](https://openrouter.ai) to access AI models. The best part? **It's completely free!** We use NVIDIA's Nemotron-3-Nano model which has no cost.

### Step 1: Get Your Free API Key

1. Go to [OpenRouter.ai](https://openrouter.ai)
2. Click **"Sign In"** in the top right
3. Sign up using Google, GitHub, or email
4. Once logged in, go to [Keys](https://openrouter.ai/keys) or click your profile → "Keys"
5. Click **"Create Key"**
6. Give it a name (e.g., "HandsOn.AI") and click **"Create"**
7. Copy your API key (starts with `sk-or-v1-...`)

### Step 2: Configure the App

Create a `.env` file in the project root directory:

```bash
# Create .env file
touch .env
```

Add your API key to the `.env` file:

```env
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
```

**Important:** Never commit your `.env` file to Git! It's already in `.gitignore`.

### Cost Information

✅ **This app is FREE to use!**

- Model used: `nvidia/nemotron-3-nano-30b-a3b:free`
- Cost per request: **$0.00**
- No credit card required
- No usage limits

## 📖 How to Use

### Job Search Mode

1. **Select Job Search** in the sidebar (default mode)

2. **Optional: Upload Resume**
   - In the sidebar, upload your PDF resume for personalized recommendations
   - The resume helps identify skill gaps specific to your profile

3. **Choose a Job Category**
   - Click any of the 10 job category buttons (Software Engineer, Data Scientist, etc.)
   - The app will search across Indeed, LinkedIn, Google, and ZipRecruiter

4. **Browse Job Results**
   - View 20 job listings with title, company, and location
   - Each card shows which job board the listing came from

5. **Get Project Recommendations**
   - Click "View & Get Projects" on any job
   - View job details and click "Generate 3 Project Ideas"
   - AI generates tailored project recommendations based on the job description
   - If you uploaded a resume, recommendations are personalized to your skill gaps

### Resume Analyzer Mode

1. **Upload Your Resume**
   - Upload your PDF resume in the sidebar
   - Wait for it to process (usually 2-3 seconds)

2. **Add Job Description** (Choose one method):

   **Option A: Fetch from URL** ⭐ Recommended
   - Paste a LinkedIn job URL into the "Enter job posting URL" field
   - Click **"🔍 Fetch Job Details"**
   - Wait 30-60 seconds for the app to fetch and parse the job posting
   
   **Option B: Manual Paste**
   - Copy the full job description from any job posting
   - Paste it into the "Paste the job description here" text area

3. **Generate Projects**
   - Click **"🎯 Generate Project Recommendations"**
   - Wait 30-60 seconds for AI analysis
   - Review your 5 personalized projects

4. **Download & Practice**
   - Click **"📥 Download All Projects as Markdown"**
   - Start building the projects!

## 🏗️ How It Works

```mermaid
flowchart LR
    subgraph JobSearch[Job Search Mode]
        Keywords[Job Keywords] --> JobSpy[JobSpy Scraper]
        JobSpy --> Jobs[20 Job Results]
        Jobs --> Select[Select Job]
        Select --> Projects3[3 Project Ideas]
    end
    
    subgraph ResumeMode[Resume Analyzer Mode]
        Resume[Resume PDF] --> Extract[PDF to Markdown]
        URL[LinkedIn URL] --> Fetch[Fetch Job Content]
        JobDesc[Job Description] --> LLM[AI Analysis]
        Fetch --> LLM
        Extract --> LLM
        LLM --> Gap[Gap Analysis]
        Gap --> Projects5[5 Custom Projects]
    end
    
    OptResume[Optional Resume] -.-> Projects3
```

### Job Search Mode Flow
1. **Category Selection**: User clicks a job category (e.g., "Software Engineer")
2. **Multi-Platform Search**: JobSpy queries Indeed, LinkedIn, Google, and ZipRecruiter
3. **Results Display**: 20 aggregated job listings shown with details
4. **Project Generation**: AI creates 3 project recommendations based on job description
5. **Resume Enhancement**: If resume uploaded, projects target specific skill gaps

### Resume Analyzer Mode Flow
1. **PDF Processing**: Converts your resume to structured markdown using `pymupdf4llm`
2. **Job Fetching** (Optional): Fetches job details from LinkedIn using their Guest API
3. **AI Analysis**: Sends both resume and job description to NVIDIA's Nemotron model
4. **Gap Identification**: AI identifies skills you need to develop
5. **Project Generation**: Creates 5 hands-on projects tailored to bridge those gaps

## 🛠️ Tech Stack

- **[Streamlit](https://streamlit.io/)** - Web app framework
- **[JobSpy](https://github.com/speedyapply/JobSpy)** - Multi-platform job scraping (NEW!)
- **[pymupdf4llm](https://pypi.org/project/pymupdf4llm/)** - PDF to markdown conversion
- **[OpenRouter](https://openrouter.ai)** - AI model access
- **[NVIDIA Nemotron-3-Nano](https://openrouter.ai/models/nvidia/nemotron-3-nano-30b-a3b)** - Free AI model
- **[Requests](https://requests.readthedocs.io/)** - HTTP library for fetching job URLs
- **[BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)** - HTML parsing
- **[Markdownify](https://github.com/matthewwithanm/python-markdownify)** - HTML to Markdown conversion
- **[python-dotenv](https://pypi.org/project/python-dotenv/)** - Environment variable management

## 📁 Project Structure

```
handson.ai/
├── app.py                    # Main Streamlit application (both modes)
├── job_scraper.py            # JobSpy wrapper and job search logic (NEW!)
├── llm_analysis.py           # AI analysis and project generation logic
├── url.py                    # Job URL fetching and parsing
├── utils.py                  # Utility functions (OpenRouter client)
├── requirements.txt          # Python dependencies
├── screenshots/              # App screenshots for README
│   ├── app-demo.png         # Main interface screenshot
│   └── url-fetch-demo.png   # URL fetching feature screenshot
├── .env                      # API keys (create this - not in repo)
├── .gitignore               # Git ignore rules
├── LICENSE                  # MIT License
└── README.md                # This file
```

## 🔍 Job Search Feature

The Job Search mode uses [JobSpy](https://github.com/speedyapply/JobSpy) to aggregate job listings from multiple platforms:

### Supported Job Boards
- ✅ **Indeed** - Most reliable, no rate limiting
- ✅ **LinkedIn** - May rate limit after many requests
- ✅ **Google Jobs** - Good coverage
- ✅ **ZipRecruiter** - US/Canada jobs

### Job Categories
- Software Engineer
- Data Scientist
- Machine Learning Engineer
- DevOps Engineer
- Backend Developer
- Frontend Developer
- Full Stack Developer
- Product Manager
- Cloud Engineer
- Data Analyst

### Caching
Results are cached for 1 hour to:
- Improve response times on repeat searches
- Reduce API calls to job boards
- Avoid rate limiting

## 🔗 URL Fetching Feature

The Resume Analyzer mode can automatically fetch job details from LinkedIn URLs using LinkedIn's Guest API. This feature:

- ✅ Works with LinkedIn job posting URLs (e.g., `https://www.linkedin.com/jobs/view/123456789`)
- ✅ Extracts job title and full description
- ✅ Converts to clean markdown format
- ✅ Has built-in timeout protection (won't hang indefinitely)

### Troubleshooting URL Fetching

If URL fetching fails or times out:

1. **Check the terminal output** - Debug messages show exactly where the process is
2. **Verify the URL format** - Must be a LinkedIn job posting URL with `/jobs/view/` in it
3. **Network issues** - VPN or firewall might block requests to LinkedIn
4. **Rate limiting** - LinkedIn may temporarily block requests; wait a few minutes
5. **Fallback option** - You can always paste the job description manually

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:

```env
OPENROUTER_API_KEY=your_api_key_here
```

### Customization

You can customize the AI model in `llm_analysis.py`:

```python
# Current model (free)
model="nvidia/nemotron-3-nano-30b-a3b:free"

# Other free options:
# - "meta-llama/llama-3-8b-instruct:free"
# - "google/gemma-7b-it:free"
```

### Customizing Job Keywords

Edit the `JOB_KEYWORDS` list in `job_scraper.py` to change available job categories:

```python
JOB_KEYWORDS = [
    "Software Engineer",
    "Data Scientist",
    # Add your own categories...
]
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Job search powered by [JobSpy](https://github.com/speedyapply/JobSpy)
- AI powered by [OpenRouter](https://openrouter.ai)
- Uses NVIDIA's Nemotron-3-Nano model
- PDF processing by [pymupdf4llm](https://github.com/pymupdf/pymupdf4llm)

## 📧 Support

If you have questions or run into issues:

1. Check that your `.env` file is set up correctly
2. Verify your OpenRouter API key is valid
3. Ensure Python 3.10+ is installed (required for JobSpy)
4. Ensure all dependencies are installed: `pip install -r requirements.txt`
5. Open an issue on GitHub

## 🌟 Star This Repo

If you find this project helpful, please give it a star! ⭐

---

**Made with ❤️ for job seekers who believe in learning by doing**
