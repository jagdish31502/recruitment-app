# 🛠️ Setup Guide - Recruitment AI Agent

This guide will walk you through setting up the Recruitment AI Agent application from scratch.

## 📋 Prerequisites

Before starting, ensure you have:

- **Python 3.8 or higher** installed
- **MongoDB** (local installation or cloud account)
- **Git** for version control
- **Text editor** or IDE (VS Code, PyCharm, etc.)

### System Requirements

- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: At least 2GB free space
- **Internet**: Required for AI API calls and package installation

## 🔧 Step-by-Step Setup

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/jagdish31502/recruitment-app.git
cd recruitment-app

```

Expected structure:
```
recruitment-app/
├── app/
├── assets/
├── requirements.txt
├── README.md
└── setup.md
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

```

### Step 3: Install Dependencies

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

```

**Expected packages:**
- fastapi==0.115.12
- streamlit==1.39.1
- motor==3.6.0
- pymongo>=4.9,<4.10
- openai==1.67.0
- google-generativeai==0.8.3
- groq==0.11.0
- ollama==0.4.1

### Step 4: MongoDB Setup

1. **Create Account**: Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. **Create Cluster**: Choose free tier
3. **Get Connection String**: Copy connection string
4. **Whitelist IP**: Add your IP address

### Step 5: Environment Configuration

Create a `.env` file in the project root:

```bash
# Create .env file
touch .env  # On Windows: type nul > .env
```

Add the following content to `.env`:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=recruitment_app

# API Configuration
API_BASE_URL=http://localhost:8000/api/v1

# AI Provider API Keys (Optional - can be set in UI)
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# Application Settings
LOG_LEVEL=INFO
DEBUG=False
```

**For MongoDB Atlas, use:**
```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=recruitment_app
```

### Step 6: AI Provider Setup (Optional)

#### OpenAI Setup
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create account and get API key
3. Add to `.env` file or set in Streamlit UI

#### Google Gemini Setup
1. Go to [Google AI Studio](https://makersuite.google.com/)
2. Create API key
3. Add to `.env` file or set in Streamlit UI

#### Groq Setup
1. Go to [Groq Console](https://console.groq.com/)
2. Create account and get API key
3. Add to `.env` file or set in Streamlit UI

#### Ollama Setup (Local)
```bash
# Install Ollama
https://ollama.com/download

# Pull a model (optional)
ollama run llama3.1
```
Note: It may take some time to get a response when using local models

## 🎯 Enhanced Email Generation Setup

### **New Features Available**

The application now includes advanced email generation capabilities:

#### **Personalized Email Generation**
- **Resume Matching Integration**: Emails automatically include detailed resume analysis
- **Skill-Specific Content**: Mentions specific skills, experience, and qualifications
- **Professional Templates**: AI-generated content with proper formatting
- **Multi-Provider Support**: Works with all supported AI providers

#### **Email Types**
1. **Interview Emails**: Personalized invitations with specific skill mentions
2. **Rejection Emails**: Respectful rejections with constructive feedback

#### **Setup Requirements**
- **Resume Matching**: Complete resume matching first to enable personalized emails
- **AI Provider**: Any supported AI provider (OpenAI, Gemini, Groq, Ollama)

#### **Usage Workflow**
1. Upload job description
2. Upload and match resumes
3. Generate personalized emails with matching insights
4. View detailed analysis used for personalization

### Running Commands

```bash
# Backend with auto-reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend with auto-reload
streamlit run app/frontend/streamlit_app.py 
```
**Access the application**
   - **Frontend**: http://localhost:8501
   - **API Docs**: http://localhost:8000/docs
   - **API**: http://localhost:8000/api/v1