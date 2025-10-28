# 🤖 Recruitment AI Agent

A comprehensive AI-powered recruitment system that automates candidate evaluation, job description processing, and email generation. Built with FastAPI backend and Streamlit frontend, featuring MongoDB integration for data persistence.

## Features

### 📝 Job Description Management
- **File Upload**: Support for PDF, DOC, and DOCX files
- **Manual Input**: Direct text input for job descriptions
- **AI Generation**: Generate job descriptions using AI based on job requirements
- **MongoDB Storage**: All job descriptions are automatically saved to database

### 📄 Resume Matching & Analysis
- **Multi-format Support**: Process PDF, DOC, and DOCX resumes
- **AI-Powered Analysis**: Intelligent matching using multiple AI providers
- **Skill Extraction**: Identify matching and missing skills
- **Scoring System**: Percentage-based matching scores
- **Batch Processing**: Handle up to 10 resumes simultaneously

### 📧 Enhanced Email Generation
- **🎯 Personalized Interview Emails**: Generate highly personalized interview invitations with specific skill mentions
- **📝 Intelligent Rejection Emails**: Create respectful rejection emails with constructive feedback
- **🔍 Resume Matching Integration**: Emails include detailed resume analysis and matching insights
- **📊 Candidate-Specific Content**: Mentions specific skills, experience, education, and strengths
- **🎨 Professional Templates**: AI-generated content with proper formatting and tone
- **📈 Matching Score Integration**: Emails reference candidate scores and analysis breakdown

### 🗄️ Database Management
- **MongoDB Integration**: Complete data persistence
- **Candidate Profiles**: Store detailed candidate information
- **Session Tracking**: Record matching sessions and results
- **Data Visualization**: View stored data through intuitive UI

### 🔧 AI Provider Support
- **OpenAI**: GPT models for analysis and generation
- **Google Gemini**: Alternative AI provider
- **Groq**: High-performance AI inference
- **Ollama**: Local AI model support

## 🏗️ Architecture

```
recruitment-app/
├── app/
│   ├── frontend/           # Streamlit UI
│   ├── models/             # Pydantic data models
│   ├── routers/            # FastAPI endpoints
│   ├── services/           # Business logic
│   └── utilities/          # Helper functions
├── logs/                   # Application logs
├── assets/
└── requirements.txt        # Dependencies
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB (local or cloud)
- AI Provider API keys (optional)

**📋 For detailed setup instructions, see [setup.md](setup.md)**

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/jagdish31502/recruitment-app.git
   cd recruitment-app
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Create .env file
   MONGODB_URL=your_mongodb_connection_string
   MONGODB_DATABASE=recruitment_app
   API_BASE_URL=http://localhost:8000/api/v1
   ```

5. **Run the application**
   ```bash
   # Start FastAPI backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   
   # Start Streamlit frontend (in another terminal)
   streamlit run app/frontend/streamlit_app.py
   ```

6. **Access the application**
   - **Frontend**: http://localhost:8501
   - **API Docs**: http://localhost:8000/docs
   - **API**: http://localhost:8000/api/v1

## 📖 Usage Guide

### 1. Job Description Input
- **Upload File**: Drag and drop PDF/DOC/DOCX files
- **Manual Input**: Paste job description text
- **AI Generate**: Fill form fields to generate with AI

### 2. Resume Matching
- Upload multiple resumes (up to 10)
- Select AI provider and configure settings
- Click "Match Resumes" to analyze candidates
- View detailed matching results with scores

### 3. Email Generation
- Select best match for interview email
- Choose other candidates for rejection emails
- Customize candidate and company information
- Generate personalized emails

### 4. Database View
- View all stored job descriptions
- Browse candidate profiles and scores
- Track matching sessions
- Export data for reporting

## 🔧 Configuration

### AI Provider Setup

#### OpenAI
```bash
export OPENAI_API_KEY=your_openai_api_key
```

#### Google Gemini
```bash
export GEMINI_API_KEY=your_gemini_api_key
```

#### Groq
```bash
export GROQ_API_KEY=your_groq_api_key
```

#### Ollama (Local)
```bash
# Install Ollama
https://ollama.com/download

# run models locally
ollama run llama3.1
```
Note: It may take some time to get a response when using local models


### MongoDB Configuration

#### Local MongoDB
```bash
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=recruitment_app
```

#### MongoDB Atlas (Cloud)
```bash
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=recruitment_app
```

## 📊 API Endpoints

### Job Description
- `POST /api/v1/job-description/upload` - Upload job description file
- `POST /api/v1/job-description/input` - Submit manual job description
- `POST /api/v1/job-description/generate` - Generate with AI

### Resume Matching
- `POST /api/v1/resume-matching/match` - Match resumes against job description

### Email Generation
- `POST /api/v1/email/generate` - Generate personalized emails with resume matching data
- `POST /api/v1/email/generate-with-matching` - Enhanced endpoint with detailed matching analysis

### Database
- `GET /api/v1/database/summary` - Get all data summary
- `GET /api/v1/database/job-descriptions` - List all job descriptions
- `GET /api/v1/database/candidates` - List all candidates

## 🎯 Enhanced Email Generation Features

### **Personalized Email Generation**
The system now generates highly personalized emails by integrating resume matching analysis:

#### **Interview Emails Include:**
- ✅ **Specific Skill Mentions**: "Your expertise in Python, Django, and AWS..."
- 📈 **Experience Highlights**: "With your 5 years of backend development experience..."
- 🎓 **Education References**: "Your Computer Science background from..."
- 🌟 **Strength Recognition**: "Your problem-solving and leadership skills..."
- 📝 **Detailed Analysis**: References to the matching score breakdown

#### **Rejection Emails Include:**
- ✅ **Acknowledgment of Strengths**: "Your strong Python skills and cloud experience..."
- ⚠️ **Constructive Feedback**: "Areas for growth include Kubernetes and ML frameworks..."
- 📊 **Professional Tone**: Respectful and encouraging language
- 🚀 **Future Opportunities**: Encourages future applications

#### **Technical Implementation:**
- **Single LLM Call**: Optimized to generate both content and structured output in one call
- **Resume Data Integration**: Automatically includes extracted resume information
- **Multi-Provider Support**: Works with OpenAI, Gemini, Groq, and Ollama

## 🧠 AI Model Choice & Logic

### **Primary AI Model: GPT-4o-mini**

**Why GPT-4o-mini?**
- **Cost-Effective**: Significantly cheaper than GPT-4 while maintaining high quality
- **Performance**: Excellent response quality for text analysis and generation tasks
- **Speed**: Fast response times for real-time applications
- **Reliability**: Consistent results across different use cases
- **API Stability**: Well-established OpenAI API with excellent documentation

### **AI Usage Across the Application**

#### 1. **Job Description Generation**
- **Model**: GPT-4o-mini
- **Purpose**: Generate comprehensive job descriptions from structured inputs
- **Input**: Job title, experience, skills, company details
- **Output**: Professional, well-formatted job description
- **Prompt Engineering**: Uses structured prompts to ensure consistent format and quality

#### 2. **Resume Matching & Analysis**
- **Model**: GPT-4o-mini
- **Purpose**: Analyze resume content against job requirements
- **Process**:
  - Extract key skills and experience from resume
  - Compare against job description requirements
  - Calculate matching percentage
  - Identify missing skills
  - Generate contextual remarks
- **Scoring Logic**: 
  - Skills match (40%)
  - Experience level (30%)
  - Education relevance (20%)
  - Overall fit (10%)

#### 3. **Email Generation**
- **Model**: GPT-4o-mini
- **Purpose**: Create personalized interview and rejection emails
- **Features**:
  - Context-aware content generation
  - Professional tone adaptation
  - Candidate-specific personalization
  - Company branding integration

### **Alternative AI Providers**
- **Google Gemini**: Backup option for cost optimization
- **Groq**: High-speed inference for real-time processing
- **Ollama**: Local deployment for privacy-sensitive environments

## 🔍 AI Logic Deep Dive

### **Resume Matching Algorithm**

1. **Text Extraction**: Extract clean text from PDF/DOC files
2. **Skill Identification**: Use NLP to identify technical and soft skills
3. **Experience Analysis**: Parse work history and calculate relevant experience
4. **Education Matching**: Evaluate educational background relevance
5. **Scoring Calculation**: Weighted algorithm considering multiple factors
6. **Gap Analysis**: Identify missing skills and experience gaps
7. **Contextual Remarks**: Generate human-readable explanations

### **Prompt Engineering Strategy**

- **Structured Prompts**: Consistent format for reliable outputs
- **Context Injection**: Include job requirements in all AI calls
- **Output Formatting**: JSON-structured responses for easy parsing
- **Error Handling**: Fallback prompts for edge cases

## 📁 Example Files

### **sample Job Descriptions**
Located in `assets/job-descriptions/`

### **Sample Resumes**
Located in `assets/resumes/`

### **Testing the System**
1. Upload a job description from `assets/job-descriptions/`
2. Upload 2-3 resumes from `assets/resumes/`
3. Run matching analysis
4. Generate emails for different scenarios

## 🔒 Security Considerations

- API keys are handled securely through environment variables
- File uploads are validated for type and size
- MongoDB connections use proper authentication
- Input validation prevents injection attacks
- AI prompts are sanitized to prevent injection
