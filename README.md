# Resume-AI--Smart-Screener

An intelligent Resume Screening Web App built using Streamlit and Generative AI, designed to automate candidate evaluation by matching resumes with job descriptions.

# 🚀 Features

📂 Upload resumes (PDF/DOCX)

🧠 AI-powered resume analysis
📊 Match score with job description
🔍 Keyword extraction & skill matching
📈 Candidate ranking system
💡 Insights for better hiring decisions

# 🛠️ Tech Stack
Python
Streamlit – Web interface
OpenAI / LLM APIs – Resume analysis
PyPDF2 / pdfplumber – Resume parsing
Pandas & NumPy – Data processing
Scikit-learn – Similarity scoring (optional)

# 📁 Project Structure
resume-screener/
│── app.py                # Main Streamlit app
│── requirements.txt     # Dependencies
│── utils.py             # Helper functions
│── data/                # Sample resumes / job descriptions
│── README.md            # Project documentation

# ▶️ Run the App
streamlit run app.py

👉 If you get error like:

Error: File does not exist: app.py

Make sure you are inside the correct project folder.

# 📊 How It Works
Upload a resume
Enter job description
AI processes both inputs
System calculates similarity score
Displays:
Match %
Key skills found
Missing skills
Recommendation
# 📌 Use Cases
HR Resume Screening
Automated Hiring Systems
Internship/Job Shortlisting
Personal Resume Improvement
# 🧠 Future Improvements
Multi-resume batch processing
ATS score optimization
Dashboard for recruiters
Integration with job portals
Advanced NLP ranking models
