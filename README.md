# 🧤 JobGlove - AI-Powered Resume Tailoring Application

**JobGlove** is a full-stack web application that uses AI to tailor your resume for specific job applications. It analyzes job descriptions, scores your resume, and generates optimized PDF and LaTeX files with improved keyword matching and relevance.

## ✨ Features

- **Multi-AI Provider Support**: Choose between OpenAI GPT-4, Google Gemini, or Anthropic Claude
- **Multiple Format Support**: Upload PDF or DOCX resumes
- **AI-Powered Tailoring**: Automatically optimizes your resume for job descriptions
- **Resume Scoring**: Get detailed scores on keyword matching, relevance, and ATS compatibility
- **Keyword Analysis**: See which keywords are missing and should be added
- **Smart Recommendations**: Receive actionable suggestions to improve your resume
- **Dual Output**: Download both PDF and LaTeX (.tex) source files
- **Modern UI**: Beautiful, responsive interface built with React and Tailwind CSS
- **Privacy-First**: Your personal information stays protected (header removed before AI processing)
- **Docker Ready**: One-command deployment with Docker Compose

## 🚀 Quick Start with Docker (Recommended)

The easiest way to run JobGlove is with Docker:

### Prerequisites
- Docker and Docker Compose installed on your system
- At least one AI API key (OpenAI, Gemini, or Anthropic)

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/SachinVenugopalan30/JobGlove.git
   cd JobGlove
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. **Start the application**
   ```bash
   docker compose up -d
   ```
   ⚠️ Note: First time setup of the container will take around 5-10 minutes depending on your network connection and device specifications, but this will not happen the next time you deploy it.

4. **Open in browser**
   ```
   http://localhost:5000
   ```

That's it!

## 💻 Manual Installation

If you prefer to run without Docker:

### Prerequisites

- Python 3.11+
- Node.js 20+
- LaTeX distribution (TeXLive or MiKTeX)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp ../.env.example ../.env
# Edit .env with your API keys

# Run the server
python app.py
```

Backend runs on `http://localhost:5000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend runs on `http://localhost:5173` (development) or served by Flask in production.

## 🎯 Usage

1. **Upload Your Resume**: Drag and drop or click to upload a PDF or DOCX file
2. **Enter Details**: Provide your name, job title, company, and paste the job description
3. **Select AI Provider**: Choose your preferred AI service (must have API key configured)
4. **Get Results**: View your score breakdown and download the tailored resume

## 🏗️ Architecture

### Backend (Flask/Python)
- **Framework**: Flask with Flask-CORS
- **AI Integration**: OpenAI, Google Gemini, Anthropic Claude APIs
- **Document Processing**: PyPDF2, python-docx, PyMuPDF, pdfplumber
- **LaTeX Generation**: PyLaTeX + system LaTeX distribution
- **Database**: SQLAlchemy with SQLite

### Frontend (React/TypeScript)
- **Framework**: React 19 with TypeScript
- **Build Tool**: Vite
- **UI Framework**: Tailwind CSS v4
- **Components**: shadcn/ui pattern components
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Testing**: Vitest + Testing Library

## 📁 Project Structure

```
JobGlove/
├── backend/
│   ├── app.py                 # Flask application
│   ├── config.py              # Configuration
│   ├── requirements.txt       # Python dependencies
│   ├── database/              # Database models and initialization
│   ├── routes/                # API endpoints
│   ├── services/              # Business logic (AI, parsing, scoring)
│   ├── templates/             # LaTeX templates
│   ├── tests/                 # Backend tests
│   └── utils/                 # Logging and utilities
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── lib/               # Utilities and animations
│   │   └── test/              # Frontend tests
│   ├── package.json
│   └── vite.config.ts
├── uploads/                   # Uploaded resume files
├── outputs/                   # Generated PDF/TEX files
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose configuration
├── .env.example               # Environment variables template
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# API Keys (at least one required)
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Application Settings
MAX_FILE_SIZE=10485760          # 10MB default
DEFAULT_USER_NAME=User          # Default name for resumes
```

### Getting API Keys

- **OpenAI**: [platform.openai.com](https://platform.openai.com/)
- **Google Gemini**: [ai.google.dev](https://ai.google.dev/)
- **Anthropic Claude**: [console.anthropic.com](https://console.anthropic.com/)

## 🧪 Testing

### Backend Tests

```bash
cd backend
source venv/bin/activate
pytest                          # Run all tests
pytest --cov                    # Run with coverage
pytest -v tests/test_routes.py  # Run specific test file
```

### Frontend Tests

```bash
cd frontend
npm test                        # Run tests
npm run test:ui                 # Run with UI
npm run test:coverage           # Run with coverage
```

## 📊 Features in Detail

### Resume Scoring System

Your resume is scored across four categories:

1. **Keyword Matching (40%)**: How well your resume matches job description keywords
2. **Relevance (25%)**: Overall relevance to the position
3. **ATS Compatibility (20%)**: Applicant Tracking System friendliness
4. **Quality (15%)**: Grammar, formatting, and professionalism

### AI Tailoring Process

1. **Header Extraction**: Personal info extracted and protected
2. **Privacy Protection**: Header removed before sending to AI
3. **AI Analysis**: AI analyzes job description and tailors content
4. **Smart Merging**: Original header merged back with tailored content
5. **LaTeX Generation**: Professional PDF generated with proper formatting
6. **Dual Output**: Both PDF and source TEX files provided

### Keyword Analysis

- Extracts key skills and technologies from job descriptions
- Identifies missing keywords in your resume
- Highlights matched keywords
- Suggests improvements

## 🔒 Security & Privacy

- **Header Privacy**: Personal information removed before AI processing
- **No Data Storage**: API keys never logged or stored
- **Local Processing**: Resume parsing happens locally
- **Secure File Handling**: Files sanitized and validated
- **CORS Protection**: Configured for secure API access

## 🛠️ Development

### Running in Development Mode

```bash
# Backend (with hot reload)
cd backend
source venv/bin/activate
python app.py

# Frontend (with hot reload)
cd frontend
npm run dev
```

### Building for Production

```bash
# Frontend build
cd frontend
npm run build

# Output goes to frontend/dist/
# Flask serves static files in production
```

## 📈 Roadmap

- Multiple resume versions management
- Resume comparison view
- In-app LaTeX editor for easy editing
- Cover letter generation
- Browser extension to immediately send job description, job title and company to the web page from various job sites

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

---

**Made with love by [Sachin Venugopalan Nair](https://github.com/SachinVenugopalan30)**

Star this repo if you find it helpful!
