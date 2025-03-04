
# ResumeRanker

ResumeRanker is an AI-powered resume screening and ranking system that extracts text from resumes, analyzes them using Google Gemini AI, and provides structured feedback along with a job fit score.

## Features

 - Extracts text from resumes using pdfplumber and OCR via        pytesseract

 - Analyzes resumes with Google Gemini AI

 - Provides structured feedback on strengths, weaknesses, and skills

 - Calculates job fit score based on job descriptions

 - Supports multiple resume uploads and ranks them

 - Responsive UI built with Streamlit


## Tech Stack

Backend: Python, Streamlit, Flask (for API)

AI/ML: Google Gemini AI, spaCy, NLTK

File Processing: PyMuPDF, pdfplumber, pytesseract, pdf2image

Frontend: HTML, JavaScript, Streamlit UI components


## Installation

**Prerequisites**

Ensure you have the following installed:

Python 3.8+

pip


    
## Clone the Repository

```
  https://github.com/nitin102005/Resume-Ranker-Analyzer.git
```
## Install Dependencies

```
  pip install -r requirements.txt
```
## Set Up Environment Variables

Create a .env file and add your Google API key:
```
GOOGLE_API_KEY=your_api_key_here

```
## Run the Application
```
streamlit run streamlit_app.py
```
## Usage


1.Upload one or multiple resumes in PDF format.

2.Enter a job description for job fit analysis.

3.Click Analyze to generate insights.

4.View structured feedback and job fit scores.

5.Resumes are ranked based on the job fit score.


## Troubleshooting

 - OCR not working? Ensure Tesseract OCR is installed and properly configured.

 - Google API errors? Double-check your API key in .env.

 - Slow processing? Large PDFs may take time. Try reducing file size.

## Video
``` Drive Link : https://drive.google.com/file/d/1OB7u1sJWOZkLneycuqNgM0uH5ILMLwLL/view?usp=sharing

