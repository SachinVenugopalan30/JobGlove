# JobGlove - Resume Tailoring Application

## Project Overview
JobGlove is an open-source application that allows users to upload their resume (DOC/DOCX) and paste a job description. The app uses AI APIs (OpenAI, Gemini, or Claude) to tailor the resume to the job description and generates a downloadable LaTeX PDF.

## Tech Stack
- **Frontend**: AlpineJS + HTMX
- **Backend**: Python (Flask/FastAPI)
- **AI APIs**: OpenAI, Google Gemini, Claude (Anthropic)
- **Document Processing**: python-docx (for DOCX), pypandoc (for DOC conversion)
- **LaTeX Generation**: pylatex or direct LaTeX templating
- **PDF Compilation**: pdflatex or xelatex

---

## Phase 1: Project Setup & Structure

### 1.1 Initialize Project
```bash
mkdir jobglove
cd jobglove
git init
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 1.2 Create Project Structure
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

### 1.3 Initialize Backend Dependencies
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

## Phase 2: Backend Development

### 2.1 Configuration Setup
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

### 2.2 Document Parser Service
Create `backend/services/document_parser.py`:
- Function to extract text from DOCX files using `python-docx`
- Function to handle DOC files (convert to DOCX first using `pypandoc` or similar)
- Error handling for corrupt/invalid files
- Text cleaning and formatting

### 2.3 AI Service Integration
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

### 2.4 LaTeX Generator Service
Create `backend/services/latex_generator.py`:
- Parse AI response into structured data
- Generate LaTeX using a clean resume template
- Compile LaTeX to PDF using subprocess (pdflatex)
- Return path to generated PDF
- Clean up temporary .tex, .aux, .log files

### 2.5 API Routes
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

### 2.6 Main Application
Create `backend/app.py`:
- Initialize Flask/FastAPI
- Configure CORS
- Register routes
- Set up error handlers
- Configure file upload settings

---

## Phase 3: Frontend Development

### 3.1 HTML Structure
Create `frontend/index.html`:
- Header with app name and description
- API selector (radio buttons or dropdown)
- File upload zone
- Textarea for job description
- Submit button
- Progress indicator
- Download button (hidden until ready)

### 3.2 AlpineJS Components
Create `frontend/js/app.js`:
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

### 3.3 HTMX Integration
- Use `hx-post` for form submission
- `hx-indicator` for loading states
- `hx-target` for response rendering
- `hx-swap` for dynamic content updates

### 3.4 Styling
Create `frontend/css/styles.css`:
- Clean, modern UI
- Responsive design
- Clear visual hierarchy
- Loading animations
- Error/success states

---

## Phase 4: Core Features Implementation

### 4.1 Resume Parsing
- [ ] Implement DOCX text extraction
- [ ] Handle DOC file conversion
- [ ] Preserve basic structure (sections, bullets)
- [ ] Clean extracted text

### 4.2 AI Integration
- [ ] Implement OpenAI API call with tailored prompt
- [ ] Implement Gemini API call
- [ ] Implement Claude API call
- [ ] Add error handling and retries
- [ ] Implement API key validation on startup

### 4.3 LaTeX Generation
- [ ] Create professional LaTeX resume template
- [ ] Map AI response to LaTeX structure
- [ ] Handle special characters (escape LaTeX symbols)
- [ ] Compile to PDF
- [ ] Error handling for LaTeX compilation issues

### 4.4 File Management
- [ ] Implement secure file upload
- [ ] Temporary file storage with cleanup
- [ ] Generated file cleanup (after 1 hour or on download)
- [ ] File size and type validation

---

## Phase 5: Testing & Refinement

### 5.1 Testing Checklist
- [ ] Test with various DOCX formats
- [ ] Test with DOC files
- [ ] Test with all three AI APIs
- [ ] Test with missing API keys
- [ ] Test with corrupt files
- [ ] Test with extremely long resumes/job descriptions
- [ ] Test LaTeX compilation edge cases
- [ ] Test file cleanup

### 5.2 Error Handling
- [ ] Invalid file format errors
- [ ] API key missing/invalid errors
- [ ] API rate limit errors
- [ ] LaTeX compilation errors
- [ ] File too large errors
- [ ] Network timeout errors

### 5.3 UX Improvements
- [ ] Add loading progress indicators
- [ ] Implement file drag-and-drop
- [ ] Add character count for job description
- [ ] Preview uploaded resume name
- [ ] Clear error messages
- [ ] Success feedback

---

## Phase 6: Polish & Documentation

### 6.1 Documentation
- [ ] Write comprehensive README
  - Project description
  - Installation instructions
  - API key setup
  - Usage guide
  - Screenshots
- [ ] Add code comments
- [ ] Create CONTRIBUTING.md
- [ ] Add LICENSE file (suggest MIT or Apache 2.0)

### 6.2 Configuration
- [ ] Environment variable documentation
- [ ] Docker support (optional)
- [ ] Setup script for easy installation

### 6.3 Security
- [ ] Sanitize file uploads
- [ ] Validate and sanitize all inputs
- [ ] Secure API key storage (never commit .env)
- [ ] Rate limiting (optional)
- [ ] CORS configuration

---

## Phase 7: Deployment Preparation

### 7.1 Local Development
```bash
# Terminal 1 - Backend
cd backend
python app.py

# Terminal 2 - Frontend (use simple HTTP server)
cd frontend
python -m http.server 8080
```

### 7.2 Future Enhancements (Post-MVP)
- [ ] Support for PDF resume uploads
- [ ] Multiple resume templates to choose from
- [ ] Resume preview before download
- [ ] Save previous tailored resumes (requires database)
- [ ] Batch processing for multiple jobs
- [ ] **Browser extension for auto-grabbing job descriptions** ⭐
  - Chrome extension
  - Firefox extension
  - Auto-detect job description text on job posting pages
  - One-click send to JobGlove web app
  - Support for major job sites (LinkedIn, Indeed, Glassdoor, etc.)
- [ ] A/B testing different AI providers
- [ ] Token usage tracking and costs

---

## Important instructions
- Do not create any additional markdown file unless specified to
- If specified to create a markdown file, drop it in a folder called docs in the project root
- Do not use emojis anywhere, and make sure comments are concise and straight to the point
- Do not add any additional feature without prompting the user
- Think of yourself as a junior-mid level software engineer learning HTMX and AlpingJS and using it in this project, ensure that the code is easy to read when it will be peer-reviewed. Ensure proper software development practices are followed.
- Once again, you are not allowed to create markdown files detailing whatever changes you have made unless the user has specified you to do so.


## Quick Start Commands

```bash
# 1. Clone/Create project
mkdir jobglove && cd jobglove

# 2. Create structure
mkdir -p backend/{routes,services,utils,templates} frontend/{css,js} uploads outputs

# 3. Set up Python environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 4. Install dependencies
pip install flask flask-cors python-docx python-dotenv openai google-generativeai anthropic pylatex requests werkzeug

# 5. Create .env file
cp .env.example .env
# Edit .env with your API keys

# 6. Run backend
cd backend
python app.py

# 7. Run frontend (separate terminal)
cd frontend
python -m http.server 8080
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

## Success Metrics

- ✅ User can upload a resume
- ✅ User can paste job description
- ✅ User can select available AI API
- ✅ System generates tailored resume
- ✅ User can download PDF
- ✅ All three AI APIs are supported
- ✅ Clean, intuitive UI
- ✅ Comprehensive error handling

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