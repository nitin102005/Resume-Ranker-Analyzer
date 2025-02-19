import os
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai
from pdf2image import convert_from_path
import pytesseract
import pdfplumber
import re
import base64
import streamlit.components.v1 as com

# Load environment variables
load_dotenv()

# Configure Google Gemini AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    # Add timeout for large PDFs
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                except Exception as e:
                    print(f"Error extracting page: {e}")
                    continue

        if text.strip():
            return text.strip()
    except Exception as e:
        print(f"Direct text extraction failed: {e}")

    # Improved OCR settings
    try:
        images = convert_from_path(pdf_path, dpi=300)  # Higher DPI for better quality
        for image in images:
            try:
                page_text = pytesseract.image_to_string(
                    image, 
                    config='--psm 1 --oem 3'  # Improved OCR settings
                )
                text += page_text + "\n"
            except Exception as e:
                print(f"OCR error on page: {e}")
                continue
    except Exception as e:
        print(f"OCR failed: {e}")

    return text.strip() or "Error: Could not extract text from PDF"

# Function to get response from Gemini AI
def analyze_resume(resume_text, job_description=None):
    if not resume_text:
        return {"error": "Resume text is required for analysis."}
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    base_prompt = f"""
    As an experienced HR professional with technical expertise, analyze this resume using the following structure:

    1. Candidate name
      Key Strengths:
    - [List key strengths as bullet points]

    2. Areas for Improvement:
    - [List areas for improvement as bullet points]

    3. Skills Assessment:
    - Technical Skills: [List and rate proficiency]
    - Soft Skills: [List observed soft skills]
    - Experience Level: [Entry/Mid/Senior]

    4. Overall Recommendation:
    [Provide a clear recommendation]

    Resume Text:
    {resume_text}
    """

    if job_description:
        base_prompt += f"""
        Job Fit Analysis:
        1. Job Fit Score: [Score out of 100]
        2. Matching Skills:
        - [List matching skills]
        3. Missing Skills:
        - [List missing skills]
        
        Job Description:
        {job_description}
        """

    try:
        response = model.generate_content(base_prompt, safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ])
        return response.text.strip()
    except Exception as e:
        return f"Error generating analysis: {str(e)}"

def extract_job_fit_score(analysis_text):
    """
    Extracts the job fit score from the AI-generated analysis text.
    Returns a score between 0 and 100.
    """
    if not analysis_text:
        return 0
        
    # More comprehensive patterns to catch different score formats
    patterns = [
        r'(?i)job\s*fit\s*score\s*[:=-]*\s*(\d{1,3})',  # Job Fit Score: 85
        r'(?i)fit\s*score\s*[:=-]*\s*(\d{1,3})',        # Fit Score: 85
        r'(?i)match\s*score\s*[:=-]*\s*(\d{1,3})',      # Match Score: 85
        r'(?i)(\d{1,3})\s*[/]\s*100',                   # 85/100
        r'(?i)(\d{1,3})\s*percent match',               # 85 percent match
        r'(?i)(\d{1,3})%\s*match',                      # 85% match
    ]
    
    for pattern in patterns:
        match = re.search(pattern, analysis_text)
        if match:
            try:
                score = int(match.group(1))
                # Validate score is within reasonable range
                if 0 <= score <= 100:
                    return score
                elif score > 100:
                    return 100
                else:
                    return 0
            except (ValueError, IndexError):
                continue
    
    # If no score found, try to estimate based on sentiment analysis
    positive_indicators = ['excellent', 'perfect', 'ideal', 'strong', 'outstanding']
    negative_indicators = ['poor', 'weak', 'lacking', 'insufficient', 'inadequate']
    
    analysis_lower = analysis_text.lower()
    
    # Count positive and negative indicators
    positive_count = sum(1 for word in positive_indicators if word in analysis_lower)
    negative_count = sum(1 for word in negative_indicators if word in analysis_lower)
    
    if positive_count > negative_count:
        return 75  # Default good score
    elif negative_count > positive_count:
        return 35  # Default poor score
    
    return 50  # Default neutral score

def analyze_multiple_resumes(resumes, job_description=None):
    results = []
    for resume in resumes:
        try:
            file_name = resume.name
            temp_file_path = f"temp_{file_name}"
            
            # Save uploaded file
            with open(temp_file_path, "wb") as f:
                f.write(resume.getbuffer())
            
            # Extract and analyze text
            resume_text = extract_text_from_pdf(temp_file_path)
            if not resume_text or "Error:" in resume_text:
                raise ValueError("Failed to extract text from PDF")
                
            analysis = analyze_resume(resume_text, job_description)
            
            # Extract and validate score
            score = extract_job_fit_score(analysis)
            
            results.append({
                'file_name': file_name,
                'analysis': analysis,
                'score': score
            })
            
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            
        except Exception as e:
            results.append({
                'file_name': getattr(resume, 'name', 'Unknown'),
                'analysis': f"Error analyzing resume: {str(e)}",
                'score': 0
            })
    
    # Sort results by score in descending order
    results.sort(key=lambda x: (x['score'], x['file_name']), reverse=True)
    return results

# Streamlit app
st.set_page_config(page_title="ResumeRanker", layout="wide")

# Convert image to Base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Image file path
image_path = "logo.png"  # Make sure "logo.png" is in the same folder

# Get Base64 encoded string
image_base64 = get_base64_image(image_path)

# Apply CSS and display the image
st.markdown(
    f"""
    <style>
        .custom-image {{
            display: block;
            margin: auto;
            width: 21%;
            position: relative;
            top: -10vh;
            left: -65vh;
        }}

        @media (max-width: 1024px) {{
            .custom-image {{
                width: 30%;
                left: -30vh;
                top: -5vh;
            }}
        }}

        @media (max-width: 768px) {{
            .custom-image {{
                width: 40%;
                left: -2px;
                top: -5vh;
            }}
        }}

        @media (max-width: 480px) {{
            .custom-image {{
                width: 50%;
                left: 0;
                top: -3vh;
            }}
        }}
    </style>
    <img src="data:image/png;base64,{image_base64}" class="custom-image">
    """,
    unsafe_allow_html=True
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
        
    }
    .title {
        text-align: center;
        margin-bottom: 2rem !important;
        color:#1e1e1e !important;
        font-family: 'Switzer', sans-serif !important;
        font-weight: 400 !important; 
        font-size: 45px !important;
        position: relative;
        top: -114px;
    }
    @import url('https://fonts.googleapis.com/css2?family=Switzer:wght@300;400;500;600&family=Inter:wght@300;400;500&family=Archivo:wght@200;300;400;600&display=swap');
    .sub-heading{
        font-family: 'Inter', 'Inter Placeholder', sans-serif;
        font-size: 20px !important;
        font-weight: 300;
        text-align: center;
        position: relative;
        top: -147px;
    }
    .text-heading{
        font-weight: 600;
        font-family: 'Archivo', sans-serif;
        font-size: 12px;
        position: relative;
        bottom: 15px;
    }
    .text{
        font-weight: 200;
        font-family: 'Archivo', sans-serif;
        color: #424242;
        font-size: 10px;
        position: relative;
        bottom: 26px;
    }   
    .file-uploader {
        border: 2px dashed #2e7d32;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .st-emotion-cache-w3nhqi{
        display: none;
    }
    .analysis-card {
        background-color: #f5f5f5;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .score {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2e7d32;
    }
    .footer {
        text-align: center;
        padding: 1rem;
        background-color: #f5f5f5;
        margin-top: 2rem;
    
    
    }
    .container{
        width: 75%;
        height: 30vh;
        padding: 21px;
        display: flex;
        flex-direction: row;
        position: relative;
        top: -155px;
        left: 163px;
    }
    .box{
        width: 40%;
        height: 17vh;
        padding: 20px;
        border-left: 1px solid rgba(0, 0, 0, 0.258);
        align-items: center;
        justify-content: center;
    }
   
</style>
""", unsafe_allow_html=True)        

# Title


st.markdown("""
    <style>

    .custom-box {

        width: 80vw;
        max-width: 1010px;
        margin: 50px auto;
        padding: 20px;
        background-color: #1e1e1e;
        color: #ffffff;
        border-radius: 12px;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.3), 0 10px 30px rgba(0, 0, 0, 0.15);
        text-align: center;
        position: relative;
        top: -100px;
        min-height: 38vh;
        display: flex;
        align-items: center;
        justify-content: center;
        box-sizing: border-box;
        }



    .custom-title {
        font-family: ui-serif !important;
        font-size: 54px !important;
        color: #ffffff !important;
        margin: 0 !important;
        padding: 10px !important;
        display: flex;
        align-items: center;
        justify-content: center;
        }

    .custom-box:hover,
    .custom-title:hover {
        background-color: #292929;
        transform: scale(1.03);
        transition: all 0.3s ease-in-out;
        cursor: pointer;
        }



    @media (max-width: 768px) {
      .custom-box {
        width: 83vw;
        margin: 20px auto;
        padding: 9px;
        top: -40px;
        min-height: auto;
        height: auto;
        right: 14px;

      }
      .title{
          font-size: 19px;
          top: -56px;
          right: 6px;
          white-space: nowrap;
          display: inline-block;
          font-weight: 540;
      }
      .sub-heading{
          font-size: 13px;
          top: -87px;
          right: -2px;
      }
      .container {
        width: 146%;
        height: auto;
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        top: -95px;
        left: -69px;
        padding: 10px;
    }
    .box {
        width: 31%;
        height: 134px;
        padding: 0px;
        margin-bottom: 10px;
    }
    .box:nth-child(4), .box:nth-child(5) {
        width: 37%; 
        height: 120px;
    }
    .box:nth-child(4){
        border-left: none;
    }
    .text-heading {
        font-size: 11px;
        bottom: -2px;
        left: 9px;
    }
    .text {
        font-size: 11px;
        bottom: 10px;
        padding-left: 13px;
    }
    

      .custom-title {
        font-size: 36px;
      }
      

    }

    @media (max-width: 480px) {
      .custom-title {
        font-size: 24px;
      }
    }
    </style>

    <div class="custom-box">
        <h1 class="custom-title">Smart screening for smarter hiring <br> Let AI do the heavy lifting!</h1>
    </div>
""", unsafe_allow_html=True)

st.markdown("<h1 class='title'>Candidate score that you can Trust</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-heading'>Taking resume screening to the next level with AI-driven insights!</p>", unsafe_allow_html=True)
st.markdown("""
    <div class="container">
        <div class="box" style="border: none;">
            <p class="text-heading">Key Strengths </p>
            <p class="text"> Instantly identify candidates strongest attributes, ensuring the best fit for the role.
            </p>
        </div>
        <div class="box">
            <p class="text-heading">Improvement Areas</p>
            <p class="text"> Recognize skill gaps and improvement areas to make informed hiring decisions.
            </p>
        </div>
        <div class="box">
            <p class="text-heading">Skills Assessment </p>
            <p class="text"> Identify technical strengths and soft skills to evaluate candidate suitability and potential for growth.
            </p>
        </div>
        <div class="box">
            <p class="text-heading">Job Fit Analysis </p>
            <p class="text"> Assess overall suitability with a precise score, highlight matching skills, and identify
                skill gaps for better hiring decisions.
            </p>
        </div>
        <div class="box">
            <p class="text-heading">Candidates Ranking</p>
            <p class="text"> Instantly identify candidates strongest attributes, ensuring the best fit for the role.
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)
st.markdown("""
    <style>
        .lottie-container {
            margin-bottom: -112px !important;
            position: relative;
            bottom: 149px;
            right: -115px;
            display: flex       ;
            justify-content: flex-end;
            align-items: center;
            height: 438px;
            background-color: #f4f4f4;
            border-radius: 15px;
            box-shadow: 5px 5px 15px rgba(0, 0, 0, 0.3);
            width: 70vw;
            margin-bottom: -112px;
        }

        .lottie {
            bottom: 10px !important;
            right: -39vw !important;
            position: relative;
            border: none !important;
        }
        .get-started{
            position: relative;
            bottom: 14vh;
            right: 20vw;
            font-size: 44px;
            font-weight: 300;
            font-family: ui-serif;
            white-space: nowrap;
            display: inline-block;
            
        }
        .Description-Resumes{
            font-size: 40px !important;
            font-weight: 400 !important;
            font-family: ui-serif !important;   
        }
        .sub-text{
            position: relative;
            bottom: 0.5vh;
            right: 41.5vw;
            white-space: nowrap;
            display: inline-block;
        }
        .lottie-container:hover,
        .lottie-container:hover .lottie,
        .lottie-container:hover ~ .get-started,
        .lottie-container:hover ~ .sub-text,
        .sub-text:hover ~ .get-started,
        .sub-text:hover ~ .lottie-container,
        .sub-text:hover ~ .lottie {
            transform: scale(1.1);
            transition: transform 0.3s ease-in-out;
        }
        @media (max-width: 768px){
            .lottie-container{ 
                width: 90vw;
                height: 30vh;
                left: -26px;
                top: -94px;     
            }
            .lottie,.lottie iframe{
                
                left: 282px;
                width: 199px;
                height: 168px;      
                
            }
            .get-started{
                font-size: 16px;
                left: -48px;
                top: -65px;         
            }
            .sub-text{
                left: -168px;
                font-size: 9px;
                top: -9px;         
            }
            .custom-box:hover,
            .custom-title:hover {
                background-color: #1e1e1e;
                transform: none;
                transition: none;
                cursor: default;
            }
            .lottie-container:hover,
        .lottie-container:hover .lottie,
        .lottie-container:hover ~ .get-started,
        .lottie-container:hover ~ .sub-text,
        .sub-text:hover ~ .get-started,
        .sub-text:hover ~ .lottie-container,
        .sub-text:hover ~ .lottie{
                transform: none;
                transition: none;
                cursor: default;
        }
            .Description-Resumes{
                font-size: 21px;
            }
            
        
    }
        

        
        
    </style>
    
    <div class="lottie-container">
        <div>
        <iframe src="https://lottie.host/embed/8b1682ce-4d9b-4182-99be-7b97cf5d5efc/iJmjlFmgHZ.lottie" class="lottie" width="450" height="450" ></iframe></div>
        
    <div class="get-started">Get Started Today!</div>
    <div class= "sub-text">Start your journey with our AI-powered <br>resume screening system. Upload your <br> resume, analyze key skills, and receive <br> instant rankings to enhance your hiring <br> process.</div>
    

""", unsafe_allow_html=True)

# Create a vertical layout
st.markdown("<h1 class='Description-Resumes'>Job Description</h1>", unsafe_allow_html=True)
job_description = st.text_area("Enter Job Description:", placeholder="Paste the job description here...")

st.markdown("<h1 class='Description-Resumes'>Upload Resumes</h1>", unsafe_allow_html=True)
uploaded_files = st.file_uploader("Upload resumes (PDF)", type=["pdf"], accept_multiple_files=True)


if uploaded_files:
    st.success(f"{len(uploaded_files)} resume(s) uploaded successfully!")
else:
    st.warning("Please upload resumes in PDF format.")

if uploaded_files and st.button("Analyze Resumes"):
    with st.spinner("Analyzing resumes..."):
        progress_bar = st.progress(0)
        try:
            results = analyze_multiple_resumes(uploaded_files, job_description)
            
            st.markdown("### Resume Rankings")
            for i, result in enumerate(results, 1):
                progress_bar.progress(i / len(results))
                
                # Create a container for each result
                result_container = st.container()
                with result_container:
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.markdown(f"**#{i} - {result['file_name']}**")
                    with col2:
                        score_color = "#2e7d32" if result['score'] >= 70 else "#FFA500" if result['score'] >= 50 else "#FF0000"
                        st.markdown(f"<span style='color: {score_color}'>**Score: {result['score']}%**</span>", unsafe_allow_html=True)
                    
                    # Show detailed analysis in expander
                    with st.expander("View Details"):
                        if "error" in result['analysis'].lower():
                            st.error(result['analysis'])
                        else:
                            st.markdown(result['analysis'])
                    
                    st.markdown("---")
            
            progress_bar.empty()
            
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")
            st.error("Please try again with different files or contact support if the issue persists.")

# Footer
st.markdown("---")
st.markdown("""

""", unsafe_allow_html=True)
