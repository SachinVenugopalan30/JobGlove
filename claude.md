# JobGlove - Resume Tailoring Application

## Project Overview
JobGlove is an open-source AI-powered resume tailoring application that allows users to upload their resume (PDF/DOCX) and paste a job description. The app uses AI APIs (OpenAI, Gemini, or Claude) to tailor the resume to the job description, provides detailed scoring and ATS analysis, and generates both PDF and LaTeX source files. The application includes advanced features like keyword analysis, missing keyword identification, and actionable recommendations for resume improvement.

## Tech Stack (As Implemented)
- **Frontend**: React 19 + TypeScript + Tailwind CSS v4 + Vite
- **Backend**: Python (Flask) with SQLAlchemy
- **AI APIs**: OpenAI GPT-4, Google Gemini, Claude (Anthropic)
- **Document Processing**: PyPDF2, python-docx, PyMuPDF, pdfplumber
- **LaTeX Generation**: PyLaTeX with custom templates
- **PDF Compilation**: pdflatex
- **Testing**: pytest (backend), Vitest + Testing Library (frontend)
- **Deployment**: Docker + Docker Compose

---

## Phase 1: Project Setup & Structure - COMPLETED

### 1.1 Initialize Project - COMPLETED
```bash
mkdir jobglove
cd jobglove
git init
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 1.2 Create Project Structure - COMPLETED
```
jobglove/
├── backend/
│   ├── app.py                 # Main Flask/FastAPI application
│   ├── requirements.txt       # Python dependencies
│   ├── config.py             # Configuration & API keys
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── resume.py         # Resume processing routes
│   │   └── health.py         # Health check endpoint
│   ├── services/
│   │   ├── __init__.py
│   │   ├── document_parser.py    # Parse DOCX/DOC files
│   │   ├── ai_service.py         # AI API integration
│   │   └── latex_generator.py    # Generate LaTeX from AI response
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py
│   └── templates/
│       └── resume_template.tex   # LaTeX resume template
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── app.js            # AlpineJS components
├── uploads/                   # Temporary file storage
├── outputs/                   # Generated resumes
├── .env.example              # Example environment variables
├── .gitignore
├── README.md
└── LICENSE
```

### 1.3 Initialize Backend Dependencies - COMPLETED
Create `backend/requirements.txt`:
```
flask
flask-cors
python-docx
python-dotenv
openai
google-generativeai
anthropic
pylatex
requests
werkzeug
```

Install:
```bash
pip install -r backend/requirements.txt
```

---

## Phase 2: Backend Development - COMPLETED

### 2.1 Configuration Setup - COMPLETED
Create `backend/config.py`:
- Load API keys from environment variables
- Define which APIs are available
- Set upload/output directories
- Configure file size limits

Create `.env.example`:
```
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here
ANTHROPIC_API_KEY=your_claude_key_here
MAX_FILE_SIZE=10485760  # 10MB
```

### 2.2 Document Parser Service - COMPLETED
Create `backend/services/document_parser.py`:
- Function to extract text from DOCX files using `python-docx`
- Function to handle DOC files (convert to DOCX first using `pypandoc` or similar)
- Error handling for corrupt/invalid files
- Text cleaning and formatting

### 2.3 AI Service Integration - COMPLETED
Create `backend/services/ai_service.py`:
- Abstract base class for AI providers
- OpenAI integration class
- Gemini integration class
- Claude integration class
- Each class should:
  - Accept resume text and job description
  - Send prompt to respective API
  - Return tailored resume content
  - Handle API errors gracefully

**Prompt Engineering Notes:**
- Instruct AI to maintain original formatting structure
- Ask for clear section headers (Experience, Education, Skills, etc.)
- Request bullet points for experience items
- Emphasize relevant skills from job description
- Keep original achievements but reframe for target role

### 2.4 LaTeX Generator Service - COMPLETED
Create `backend/services/latex_generator.py`:
- Parse AI response into structured data
- Generate LaTeX using a clean resume template
- Compile LaTeX to PDF using subprocess (pdflatex)
- Return path to generated PDF
- Clean up temporary .tex, .aux, .log files

### 2.5 API Routes - COMPLETED
Create `backend/routes/resume.py`:

**POST /api/check-apis**
- Returns which API keys are available
- Response: `{"openai": true, "gemini": false, "claude": true}`

**POST /api/upload-resume**
- Accept file upload (DOCX/DOC)
- Validate file type and size
- Save temporarily
- Return file ID or path

**POST /api/tailor-resume**
- Accept: resume file, job description, selected API
- Validate API key exists
- Parse resume → Send to AI → Generate LaTeX → Compile PDF
- Return download link or file

**GET /api/download/:filename**
- Serve generated PDF
- Clean up file after download (optional)

### 2.6 Main Application - COMPLETED
Create `backend/app.py`:
- Initialize Flask/FastAPI
- Configure CORS
- Register routes
- Set up error handlers
- Configure file upload settings

---

## Phase 3: Frontend Development - COMPLETED (Using React + TypeScript)
Note: Frontend was built with React + TypeScript + Tailwind instead of AlpineJS + HTMX

### 3.1 HTML Structure - COMPLETED
Create `frontend/index.html`:
- Header with app name and description
- API selector (radio buttons or dropdown)
- File upload zone
- Textarea for job description
- Submit button
- Progress indicator
- Download button (hidden until ready)

### 3.2 React Components - COMPLETED
Create `frontend/src/` directory with React components:
```javascript
// Main Alpine component
{
  availableApis: {},
  selectedApi: null,
  resumeFile: null,
  jobDescription: '',
  isProcessing: false,
  downloadUrl: null,
  errorMessage: null
}
```

Key functions:
- `checkAvailableApis()` - On page load, fetch available APIs
- `handleFileUpload()` - Handle file selection
- `submitResume()` - Send data to backend via HTMX or fetch
- `downloadResume()` - Trigger PDF download

### 3.3 API Integration - COMPLETED
- Using fetch API for backend communication
- State management with React hooks
- Error handling and loading states
- Response rendering with dynamic components

### 3.4 Styling - COMPLETED
Using Tailwind CSS v4:
- Clean, modern UI
- Responsive design
- Clear visual hierarchy
- Loading animations
- Error/success states

---

## Phase 4: Core Features Implementation - COMPLETED

### 4.1 Resume Parsing - COMPLETED
- [x] Implement DOCX text extraction
- [x] Handle PDF file parsing (added feature)
- [x] Preserve basic structure (sections, bullets)
- [x] Clean extracted text
- [x] Header extraction and privacy protection

### 4.2 AI Integration - COMPLETED
- [x] Implement OpenAI API call with tailored prompt
- [x] Implement Gemini API call
- [x] Implement Claude API call
- [x] Add error handling and retries
- [x] Implement API key validation on startup
- [x] Configurable AI models via environment variables

### 4.3 LaTeX Generation - COMPLETED
- [x] Create professional LaTeX resume template
- [x] Map AI response to LaTeX structure
- [x] Handle special characters (escape LaTeX symbols)
- [x] Compile to PDF
- [x] Error handling for LaTeX compilation issues
- [x] Dual output (PDF and LaTeX source files)

### 4.4 File Management - COMPLETED
- [x] Implement secure file upload
- [x] Temporary file storage with cleanup
- [x] Generated file cleanup (after 1 hour or on download)
- [x] File size and type validation

---

## Phase 5: Testing & Refinement - COMPLETED

### 5.1 Testing Checklist - COMPLETED
- [x] Test with various DOCX formats
- [x] Test with PDF files
- [x] Test with all three AI APIs
- [x] Test with missing API keys
- [x] Test with corrupt files
- [x] Test with extremely long resumes/job descriptions
- [x] Test LaTeX compilation edge cases
- [x] Test file cleanup
- [x] Backend tests with pytest
- [x] Frontend tests with Vitest

### 5.2 Error Handling - COMPLETED
- [x] Invalid file format errors
- [x] API key missing/invalid errors
- [x] API rate limit errors
- [x] LaTeX compilation errors
- [x] File too large errors
- [x] Network timeout errors

### 5.3 UX Improvements - COMPLETED
- [x] Add loading progress indicators
- [x] Implement file drag-and-drop
- [x] Add character count for job description
- [x] Preview uploaded resume name
- [x] Clear error messages
- [x] Success feedback
- [x] Resume scoring display
- [x] Keyword analysis visualization
- [x] ATS recommendations display

---

## Phase 6: Polish & Documentation - COMPLETED

### 6.1 Documentation - COMPLETED
- [x] Write comprehensive README
  - Project description
  - Installation instructions
  - API key setup
  - Usage guide
  - Architecture overview
- [x] Add code comments
- [x] Add LICENSE file (MIT)
- [x] Create QUICKSTART.md
- [ ] Create CONTRIBUTING.md (pending)

### 6.2 Configuration - COMPLETED
- [x] Environment variable documentation
- [x] Docker support with docker-compose.yml
- [x] Dockerfile for containerization
- [x] .env.example template

### 6.3 Security - COMPLETED
- [x] Sanitize file uploads
- [x] Validate and sanitize all inputs
- [x] Secure API key storage (never commit .env)
- [x] CORS configuration
- [x] Header privacy protection (removed before AI processing)

---

## Phase 7: Deployment Preparation - COMPLETED

### 7.1 Local Development - COMPLETED
```bash
# Using Docker (recommended)
docker compose up -d

# OR Manual setup:
# Terminal 1 - Backend
cd backend
python app.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 7.2 Production Deployment - COMPLETED
- [x] Docker Compose configuration
- [x] Production-ready Dockerfile
- [x] Frontend build process
- [x] Static file serving via Flask

### 7.3 Additional Features Implemented (Beyond Original Plan)
- [x] Resume scoring system with multiple metrics
- [x] ATS (Applicant Tracking System) compatibility analysis
- [x] Keyword extraction and analysis
- [x] Missing keyword identification
- [x] Actionable recommendations for resume improvement
- [x] Database integration with SQLAlchemy
- [x] Dual file format output (PDF + LaTeX source)
- [x] PDF resume upload support (in addition to DOCX)
- [x] Header extraction and privacy protection
- [x] Comprehensive test suite (backend with pytest, frontend with Vitest)
- [x] Modern React-based UI with TypeScript
- [x] Tailwind CSS v4 styling
- [x] Docker containerization with docker-compose

### 7.4 Future Enhancements (Post-MVP)
- [ ] Multiple resume templates to choose from
- [ ] Resume preview before download
- [ ] Resume version history and management
- [ ] Batch processing for multiple jobs
- [ ] **Browser extension for auto-grabbing job descriptions**
  - Chrome extension
  - Firefox extension
  - Auto-detect job description text on job posting pages
  - One-click send to JobGlove web app
  - Support for major job sites (LinkedIn, Indeed, Glassdoor, etc.)
- [ ] A/B testing different AI providers
- [ ] Token usage tracking and costs
- [ ] Cover letter generation
- [ ] Groq API integration
- [ ] Ollama local model support
- [ ] In-app LaTeX editor

---

## Project Status Summary

**Overall Progress: PRODUCTION READY**

All 7 phases have been completed successfully. The application is fully functional with:
- Complete backend API with Flask
- Modern React + TypeScript frontend
- Integration with OpenAI, Gemini, and Claude APIs
- Resume scoring and ATS analysis
- Docker deployment ready
- Comprehensive testing suite
- Full documentation

The project has exceeded the original MVP requirements with additional features like resume scoring, keyword analysis, ATS recommendations, and privacy protection.

---

## Important instructions
- Do not create any additional markdown file unless specified to
- If specified to create a markdown file, drop it in a folder called docs in the project root
- Do not use emojis anywhere, and make sure comments are concise and straight to the point
- Do not add any additional feature without prompting the user
- Once again, you are not allowed to create markdown files detailing whatever changes you have made unless the user has specified you to do so.
- This project currently uses pip for dependency management, switch to uv and use only uv going forward.
- Along with uv, you will use ruff for linting the Python code.
- Whenever changes are made and if changes to how the docker containers are run, ensure that the relevant files are also updated there.
- Testing will be done through uv and pytest, frontend testing will be done same as before.

## Quick Start Commands

```bash
# 1. Clone/Create project
mkdir jobglove && cd jobglove

# 2. Create structure
mkdir -p backend/{routes,services,utils,templates} frontend/{css,js} uploads outputs

# 3. Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 4. Set up Python environment with uv
cd backend
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 5. Install dependencies with uv
uv pip install -e .

# 6. Install development dependencies (testing, linting)
uv pip install -e ".[dev]"

# 7. Create .env file
cp ../.env.example ../.env
# Edit .env with your API keys

# 8. Run backend
python app.py

# 9. Run frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Development Workflow with uv and ruff

```bash
# Install dependencies
uv pip install -e ".[dev]"

# Run tests
uv run pytest
uv run pytest --cov  # with coverage

# Lint code with ruff
uv run ruff check .
uv run ruff check --fix .  # auto-fix issues

# Format code with ruff
uv run ruff format .

# Add a new dependency
# Edit backend/pyproject.toml and add to dependencies array
uv pip install -e .
```

---

## Key Development Tips

1. **Start Simple**: Get basic file upload → text extraction working first
2. **Test One API First**: Implement OpenAI first, then add others
3. **Mock AI Responses**: While developing, use hardcoded responses to test LaTeX generation
4. **Version Control**: Commit frequently with clear messages
5. **LaTeX Template**: Find a good resume template online or use a minimal one initially
6. **Error Logging**: Log all errors to help with debugging

---

## Success Metrics - ALL COMPLETED

- ✅ User can upload a resume (PDF or DOCX)
- ✅ User can paste job description
- ✅ User can select available AI API
- ✅ System generates tailored resume
- ✅ User can download PDF and LaTeX source
- ✅ All three AI APIs are supported (OpenAI, Gemini, Claude)
- ✅ Clean, intuitive UI (React + Tailwind)
- ✅ Comprehensive error handling
- ✅ Resume scoring and analysis
- ✅ ATS compatibility check
- ✅ Keyword analysis
- ✅ Docker deployment ready
- ✅ Comprehensive testing suite

---

## Resources

- **AlpineJS**: https://alpinejs.dev/
- **HTMX**: https://htmx.org/
- **python-docx**: https://python-docx.readthedocs.io/
- **OpenAI API**: https://platform.openai.com/docs/
- **Gemini API**: https://ai.google.dev/docs
- **Claude API**: https://docs.anthropic.com/
- **LaTeX Resume Templates**: https://www.overleaf.com/gallery/tagged/cv

---

## Frontend Aesthetics
You tend to converge toward generic, "on distribution" outputs. In frontend design, this creates what users call the "AI slop" aesthetic. Avoid this: make creative, distinctive frontends that surprise and delight. Focus on:

Typography: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics.

Color & Theme: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes. Draw from IDE themes and cultural aesthetics for inspiration.

Motion: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available. Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions.

Backgrounds: Create atmosphere and depth rather than defaulting to solid colors. Layer CSS gradients, use geometric patterns, or add contextual effects that match the overall aesthetic.

Avoid generic AI-generated aesthetics:
- Overused font families (Inter, Roboto, Arial, system fonts)
- Clichéd color schemes (particularly purple gradients on white backgrounds)
- Predictable layouts and component patterns
- Cookie-cutter design that lacks context-specific character

Interpret creatively and make unexpected choices that feel genuinely designed for the context. Vary between light and dark themes, different fonts, different aesthetics. You still tend to converge on common choices (Space Grotesk, for example) across generations. Avoid this: it is critical that you think outside the box!
