# Resume-Ranker-Analyzer
ResumeRanker - AI-Powered Resume Screening and Ranking System
ResumeRanker is an AI-powered system for automating the resume screening process. By leveraging Google Gemini AI and machine learning, the system analyzes and ranks resumes based on job descriptions and candidate fit. It extracts key information from resumes in PDF format, assesses the match, and provides actionable insights for recruitment teams.
Table of Contents
•	Project Description
•	Features
•	Tech Stack
•	Setup Instructions
•	Usage
Project Description
ResumeRanker is designed to help HR professionals and recruitment teams streamline the resume screening process. The tool extracts key strengths, weaknesses, skills, and experience from resumes and compares them with job descriptions to provide a job fit score and recommendations.
Key Features:
•	Extract text from resumes in PDF format using OCR and PDF text extraction techniques.
•	Use Google Gemini AI to analyze resumes and generate insights.
•	Rank candidates based on job fit score.
•	Provide detailed analysis of key strengths, improvement areas, and skills.
•	Clean and responsive web interface built with Streamlit.
Features
•	PDF Resume Parsing: Extracts data from resumes in PDF format using pdfplumber and OCR (pytesseract).
•	AI-Powered Resume Analysis: Leverages Google Gemini AI to provide a detailed analysis of resumes.
•	Job Fit Score: Calculates the job fit score based on the resume content and job description.
•	Skills Assessment: Identifies technical and soft skills present in the resume.
•	Candidate Ranking: Ranks multiple candidates based on their job fit score.
•	Responsive Web Interface: The app is built using Streamlit and adapts to different screen sizes.
Tech Stack
•	Backend:
o	Python
o	Google Gemini AI API
o	Streamlit
o	PDF Handling (pdfplumber, pdf2image, pytesseract)
o	Environment Variables (dotenv)
•	Frontend:
o	Streamlit (UI/UX)
o	HTML, CSS (for responsive web design)
Setup Instructions
Follow these steps to set up the project locally:
Prerequisites
Ensure you have the following installed:
•	Python 3.7+
•	pip (Python package manager)
1.	Clone the repository
2.	Install dependencies 
o	pip install -r requirements.txt
3.	Set up environment variables
o	Create a .env file in the root directory and add your 
o	Google Gemini API key: =your-API-key-here
4.	Run the application
o	streamlit run streamlit_app.py
Usage
Upload Resumes
1.	Open the web application.
2.	Upload one or more resumes in PDF format.
3.	Optionally, provide a job description to compare the resumes against.
4.	The application will analyze the resumes, provide insights, and rank them based on job fit.
Analysis Features:
•	Key Strengths: Highlights the candidate's strengths based on the resume.
•	Areas for Improvement: Identifies gaps or areas where the candidate can improve.
•	Skills Assessment: Lists the technical and soft skills found in the resume.
•	Job Fit Score: Displays a score representing the candidate's suitability for the job.
