# Deployment Guide for Recruitment AI Agent

This guide covers deploying the Recruitment AI Agent with separate FastAPI backend and Streamlit frontend services on Render.

## 🏗️ Architecture

- **FastAPI Backend**: Handles API endpoints, business logic, and data processing
- **Streamlit Frontend**: Provides the user interface for interacting with the application
- **MongoDB**: Database for storing job descriptions, candidate data, and session information

## 📋 Prerequisites

- GitHub repository with your code
- MongoDB Atlas account or MongoDB instance
- Render account
- AI provider API keys (optional)

## 🚀 Deployment Steps

### Step 1: Deploy FastAPI Backend

1. **Create New Web Service** in Render Dashboard
2. **Connect GitHub Repository**
3. **Configure Service Settings:**

   **Service Name:** `recruitment-app-api`
   
   **Build Command:**
   ```bash
   pip install -r requirements.txt
   ```
   
   **Start Command:**
   ```bash
   python3 -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

4. **Set Environment Variables:**
   - `MONGODB_URL`: Your MongoDB connection string
   - `MONGODB_DATABASE`: `recruitment_app`
   - `OPENAI_API_KEY`: (optional) Your OpenAI API key
   - `GEMINI_API_KEY`: (optional) Your Google Gemini API key
   - `GROQ_API_KEY`: (optional) Your Groq API key

5. **Deploy** the service

### Step 2: Deploy Streamlit Frontend

1. **Create New Web Service** in Render Dashboard
2. **Connect Same GitHub Repository**
3. **Configure Service Settings:**

   **Service Name:** `recruitment-app-ui`
   
   **Build Command:**
   ```bash
   pip install -r requirements.txt
   ```
   
   **Start Command:**
   ```bash
   python -m streamlit run app/frontend/streamlit_app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
   ```

4. **Set Environment Variables:**
   - `API_BASE_URL`: `https://your-fastapi-service-name.onrender.com/api/v1`
   - `MONGODB_URL`: Same MongoDB connection string as FastAPI
   - `MONGODB_DATABASE`: `recruitment_app`
   - `OPENAI_API_KEY`: (optional) Your OpenAI API key
   - `GEMINI_API_KEY`: (optional) Your Google Gemini API key
   - `GROQ_API_KEY`: (optional) Your Groq API key

5. **Deploy** the service

## 🌐 Access Your Deployed Application

### FastAPI Backend
- **Service URL**: `https://your-fastapi-service-name.onrender.com`
- **API Documentation**: `https://your-fastapi-service-name.onrender.com/docs`
- **Health Check**: `https://your-fastapi-service-name.onrender.com/health`
- **API Endpoints**: `https://your-fastapi-service-name.onrender.com/api/v1`

### Streamlit Frontend
- **Service URL**: `https://your-streamlit-service-name.onrender.com`
- **Full UI Experience**: Complete Streamlit interface

## 🔧 Environment Variables Reference

### FastAPI Service Required Variables:
```bash
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=recruitment_app
```

### Streamlit Service Required Variables:
```bash
API_BASE_URL=https://your-fastapi-service-name.onrender.com/api/v1
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=recruitment_app
```

### Optional AI Provider Variables (both services):
```bash
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

## 📝 Important Notes

1. **Service Names**: Replace `your-fastapi-service-name` and `your-streamlit-service-name` with your actual Render service names
2. **MongoDB**: Both services must use the same MongoDB instance for data consistency
3. **API Communication**: Streamlit service communicates with FastAPI service via HTTP requests
4. **Environment Variables**: Ensure all required environment variables are set in both services
5. **Deployment Order**: Deploy FastAPI first, then Streamlit to ensure API availability

## 🔍 Troubleshooting

### Common Issues:
- **API Connection Failed**: Verify `API_BASE_URL` in Streamlit service matches FastAPI service URL
- **MongoDB Connection Error**: Check `MONGODB_URL` format and credentials
- **Build Failures**: Ensure all dependencies are in `requirements.txt`
- **Service Not Starting**: Check logs for specific error messages

### Health Checks:
- FastAPI: `https://your-fastapi-service-name.onrender.com/health`
- Streamlit: Check service status in Render dashboard

## 🎯 Testing Your Deployment

1. **Test FastAPI**: Visit the API documentation at `/docs`
2. **Test Streamlit**: Access the frontend URL
3. **Test Integration**: Use Streamlit UI to interact with FastAPI endpoints
4. **Test Database**: Create job descriptions and candidates through the UI

## 📊 Service Monitoring

- Monitor both services in Render dashboard
- Check logs for any errors or issues
- Monitor MongoDB Atlas for database performance
- Set up alerts for service downtime
