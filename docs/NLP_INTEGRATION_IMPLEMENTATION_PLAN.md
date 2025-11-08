# JobGlove NLP Integration Implementation Plan

## Overview
This document outlines the detailed implementation plan for integrating local NLP-based resume analysis into JobGlove. The integration will add pre-tailoring resume scoring, dynamic keyword extraction from job descriptions, and post-tailoring score comparison.

## Key Features
- Local NLP-based resume analysis (no API dependency for scoring)
- Dynamic skill/keyword extraction from job descriptions
- Pre-tailoring resume score against job description
- Post-tailoring score comparison (before/after)
- Support for both PDF and DOCX resume uploads
- Multi-page frontend with landing page and tailoring workflow

## Technology Stack
- spaCy (NLP and Named Entity Recognition)
- NLTK (Text processing)
- PyMuPDF (PDF text extraction)
- scikit-learn (Text similarity calculations)
- AlpineJS + HTMX (Frontend)

---

## PHASE 1: Environment Setup & Dependencies

### Objective
Install and configure all required NLP libraries and language models.

### Tasks

#### 1.1 Update Requirements File
**File:** `backend/requirements.txt`

Add the following dependencies:
```
spacy==3.7.2
nltk==3.8.1
PyMuPDF==1.23.7
pdfplumber==0.10.3
scikit-learn==1.3.2
```

#### 1.2 Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### 1.3 Download Language Models
```bash
python -m spacy download en_core_web_sm
```

#### 1.4 Download NLTK Data
Create script: `backend/setup_nltk.py`
```python
import nltk

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
```

Run:
```bash
python backend/setup_nltk.py
```

### Testing
- Verify all packages install without errors
- Test spaCy model loading in Python REPL:
  ```python
  import spacy
  nlp = spacy.load('en_core_web_sm')
  doc = nlp("Test sentence")
  print(doc)
  ```
- Test NLTK data availability:
  ```python
  import nltk
  from nltk.corpus import stopwords
  print(stopwords.words('english')[:10])
  ```

### Acceptance Criteria
- All dependencies installed successfully
- spaCy model loads without errors
- NLTK data accessible
- No import errors when importing new packages

### Estimated Time
1-2 hours

---

## PHASE 2: NLP Module Development

### Objective
Build core NLP modules for resume parsing, keyword extraction, text analysis, and scoring.

### 2.1 Resume Parser Module

#### File Structure
Create: `backend/services/nlp/__init__.py`
Create: `backend/services/nlp/resume_parser.py`

#### Implementation
```python
# backend/services/nlp/resume_parser.py

import docx
import fitz  # PyMuPDF
import pdfplumber
from pathlib import Path

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file."""
    pass

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file using PyMuPDF."""
    pass

def extract_text(file_path: str) -> str:
    """Auto-detect file type and extract text."""
    pass

def clean_text(text: str) -> str:
    """Clean and normalize extracted text."""
    pass
```

#### Testing
Create: `backend/tests/test_nlp/__init__.py`
Create: `backend/tests/test_nlp/test_resume_parser.py`

Test cases:
- Extract text from sample DOCX resume
- Extract text from sample PDF resume
- Handle corrupt/invalid files
- Clean text properly (remove extra whitespace, special chars)

### 2.2 Entity Extractor Module

#### File
Create: `backend/services/nlp/entity_extractor.py`

#### Implementation
```python
# backend/services/nlp/entity_extractor.py

import spacy
import re
from typing import Optional, Dict

nlp = spacy.load('en_core_web_sm')

def extract_name(text: str) -> Optional[str]:
    """Extract candidate name using NER."""
    pass

def extract_email(text: str) -> Optional[str]:
    """Extract email using regex."""
    pass

def extract_phone(text: str) -> Optional[str]:
    """Extract phone number using regex."""
    pass

def extract_sections(text: str) -> Dict[str, str]:
    """
    Identify and extract resume sections.
    Returns dict with keys: 'experience', 'education', 'skills', 'summary'
    """
    pass

def extract_all_entities(text: str) -> Dict:
    """Extract all entities from resume."""
    pass
```

#### Testing
Create: `backend/tests/test_nlp/test_entity_extractor.py`

Test cases:
- Extract name from various resume formats
- Extract email (various formats)
- Extract phone (US, international formats)
- Identify resume sections correctly
- Handle missing information gracefully

### 2.3 Skill Extractor Module

#### File
Create: `backend/services/nlp/skill_extractor.py`

#### Implementation
```python
# backend/services/nlp/skill_extractor.py

import spacy
from typing import List, Dict, Set
from sklearn.feature_extraction.text import TfidfVectorizer

nlp = spacy.load('en_core_web_sm')

def extract_keywords_from_job_description(job_desc: str) -> List[str]:
    """
    Extract keywords/skills from job description using:
    - Named entities (PERSON, ORG, PRODUCT)
    - Noun phrases
    - Technical terms (proper nouns, acronyms)
    - Tools, frameworks, languages
    """
    pass

def extract_keywords_from_resume(resume_text: str) -> List[str]:
    """Extract keywords from resume using same approach."""
    pass

def extract_technical_terms(text: str) -> List[str]:
    """Extract technical terms using POS tagging."""
    pass

def extract_noun_phrases(text: str) -> List[str]:
    """Extract noun phrases that might be skills."""
    pass

def normalize_keywords(keywords: List[str]) -> List[str]:
    """Normalize keywords (lowercase, remove duplicates, etc.)."""
    pass

def calculate_keyword_match(resume_keywords: List[str],
                           job_keywords: List[str]) -> Dict:
    """
    Calculate keyword match between resume and job.
    Returns:
    {
        "matched": [...],
        "missing": [...],
        "match_percentage": float
    }
    """
    pass
```

#### Testing
Create: `backend/tests/test_nlp/test_skill_extractor.py`

Test cases:
- Extract keywords from software engineering job description
- Extract keywords from data science job description
- Extract keywords from product manager job description
- Match resume keywords against job keywords
- Calculate match percentage accurately
- Handle empty or minimal text

### 2.4 Text Analyzer Module

#### File
Create: `backend/services/nlp/text_analyzer.py`

#### Implementation
```python
# backend/services/nlp/text_analyzer.py

import re
from typing import Dict, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords

def calculate_keyword_density(resume_text: str, job_keywords: List[str]) -> float:
    """Calculate how frequently job keywords appear in resume."""
    pass

def check_ats_compatibility(resume_text: str) -> Dict:
    """
    Check ATS compatibility.
    Returns:
    {
        "score": 0-100,
        "issues": [...],
        "recommendations": [...]
    }
    """
    pass

def calculate_text_similarity(resume_text: str, job_desc: str) -> float:
    """Calculate cosine similarity using TF-IDF."""
    pass

def count_quantified_achievements(resume_text: str) -> int:
    """Count numbers/percentages in text (indicators of achievements)."""
    pass

def extract_action_verbs(resume_text: str) -> List[str]:
    """Extract action verbs from resume."""
    pass

def analyze_text_quality(resume_text: str) -> Dict:
    """
    Analyze overall text quality.
    Returns:
    {
        "avg_sentence_length": float,
        "action_verb_count": int,
        "quantified_achievements": int,
        "readability_score": float
    }
    """
    pass
```

#### Testing
Create: `backend/tests/test_nlp/test_text_analyzer.py`

Test cases:
- Calculate keyword density accurately
- Detect ATS compatibility issues (tables, images, etc.)
- Calculate text similarity between resume and job
- Count quantified achievements
- Extract action verbs
- Analyze text quality metrics

### 2.5 Local Scorer Module

#### File
Create: `backend/services/nlp/local_scorer.py`

#### Implementation
```python
# backend/services/nlp/local_scorer.py

from typing import Dict
from .skill_extractor import extract_keywords_from_job_description, \
                              extract_keywords_from_resume, \
                              calculate_keyword_match
from .text_analyzer import calculate_keyword_density, \
                           check_ats_compatibility, \
                           calculate_text_similarity, \
                           analyze_text_quality

def score_resume_against_job(resume_text: str, job_description: str) -> Dict:
    """
    Score resume against job description using local NLP.

    Returns:
    {
        "total_score": 0-100,

        "keyword_match_score": 0-100,
        "keyword_match_details": {
            "matched": [...],
            "missing": [...],
            "match_percentage": float
        },

        "relevance_score": 0-100,
        "relevance_details": {
            "similarity_score": float,
            "keyword_density": float
        },

        "ats_score": 0-100,
        "ats_details": {
            "issues": [...],
            "recommendations": [...]
        },

        "quality_score": 0-100,
        "quality_details": {
            "quantified_achievements": int,
            "action_verbs_count": int,
            "recommendations": [...]
        },

        "recommendations": [...]
    }
    """
    pass

def _calculate_total_score(keyword_score: float,
                          relevance_score: float,
                          ats_score: float,
                          quality_score: float) -> float:
    """
    Calculate weighted total score.

    Weights:
    - Keyword match: 40%
    - Relevance: 25%
    - ATS compatibility: 20%
    - Quality: 15%
    """
    pass

def generate_recommendations(score_data: Dict) -> List[str]:
    """Generate actionable recommendations based on scores."""
    pass
```

#### Testing
Create: `backend/tests/test_nlp/test_local_scorer.py`

Test cases:
- Score resume with high match (should get high score)
- Score resume with low match (should get low score)
- Verify score components add up correctly
- Verify recommendations are generated
- Test with various resume/job combinations
- Ensure score is always 0-100

### Acceptance Criteria for Phase 2
- All NLP modules implemented and documented
- All unit tests passing
- Text extraction works for both PDF and DOCX
- Keyword extraction works for various job descriptions
- Scoring algorithm produces reasonable scores (0-100)
- Recommendations are actionable and relevant

### Estimated Time
3-4 days

---

## PHASE 3: Backend API Routes

### Objective
Create API endpoints for resume analysis and update existing endpoints for PDF support and post-tailoring scoring.

### 3.1 New Route: Analyze Resume

#### File
Modify: `backend/routes/resume.py`

#### Implementation
```python
@resume_bp.route('/analyze-resume', methods=['POST'])
def analyze_resume():
    """
    Analyze uploaded resume against job description using local NLP.

    Request:
    {
        "file_path": "uploads/resume_xyz.pdf",
        "job_description": "..."
    }

    Response:
    {
        "extracted_data": {
            "name": "...",
            "email": "...",
            "phone": "..."
        },
        "score": {
            "total_score": 72,
            "keyword_match_score": 68,
            "keyword_match_details": {...},
            "relevance_score": 75,
            "ats_score": 80,
            "quality_score": 65,
            "recommendations": [...]
        }
    }
    """
    pass
```

### 3.2 Update Route: Upload Resume

#### File
Modify: `backend/routes/resume.py`

#### Changes
- Accept `.pdf` files in addition to `.doc`, `.docx`
- Update file validation logic
- Update allowed extensions in config

```python
ALLOWED_EXTENSIONS = {'doc', 'docx', 'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
```

### 3.3 Update Route: Tailor Resume

#### File
Modify: `backend/routes/resume.py`

#### Changes
- After AI tailoring, score the tailored resume using local NLP
- Include `tailored_score` in response

```python
@resume_bp.route('/tailor-resume', methods=['POST'])
def tailor_resume():
    """
    Tailor resume using AI, then score with local NLP.

    Response includes:
    {
        "pdf_file": "...",
        "tex_file": "...",
        "original_text": "...",
        "tailored_text": "...",
        "tailored_score": {  # NEW
            "total_score": 89,
            "keyword_match_score": 92,
            ...
        }
    }
    """
    pass
```

### 3.4 Update Configuration

#### File
Modify: `backend/config.py`

Add configuration for NLP:
```python
class Config:
    # Existing config...

    # NLP Configuration
    SPACY_MODEL = 'en_core_web_sm'
    MIN_KEYWORD_LENGTH = 2
    MAX_KEYWORDS = 50

    # Scoring weights
    KEYWORD_MATCH_WEIGHT = 0.40
    RELEVANCE_WEIGHT = 0.25
    ATS_WEIGHT = 0.20
    QUALITY_WEIGHT = 0.15
```

### Testing
Create: `backend/tests/test_nlp_routes.py`

Test cases:
- POST /api/analyze-resume with DOCX file
- POST /api/analyze-resume with PDF file
- POST /api/upload-resume with PDF file
- POST /api/tailor-resume includes tailored_score
- Error handling (missing file_path, invalid job description)
- Validate response structure matches specification

### Acceptance Criteria
- /api/analyze-resume endpoint works correctly
- PDF uploads are supported
- /api/tailor-resume includes post-tailoring local NLP score
- All API tests passing
- Error responses are clear and helpful

### Estimated Time
2-3 days

---

## PHASE 4: Frontend Restructuring

### Objective
Create a multi-page frontend with landing page and tailoring workflow page.

### 4.1 Landing Page

#### File
Create: `frontend/landing.html`
Create: `frontend/css/landing.css`
Create: `frontend/js/landing.js`

#### Structure
```html
<!DOCTYPE html>
<html>
<head>
    <title>JobGlove - AI Resume Tailoring</title>
    <link rel="stylesheet" href="css/styles.css">
    <link rel="stylesheet" href="css/landing.css">
</head>
<body>
    <div class="landing-container">
        <header>
            <h1>JobGlove</h1>
            <p>AI-Powered Resume Tailoring</p>
        </header>

        <main>
            <div class="options-container">
                <!-- Option 1: Tailor Existing Resume -->
                <div class="option-card">
                    <h2>Tailor Existing Resume</h2>
                    <p>Upload your resume and job description to get an AI-tailored version</p>
                    <a href="tailor.html" class="btn-primary">Get Started</a>
                </div>

                <!-- Option 2: Create New Resume (Coming Soon) -->
                <div class="option-card disabled">
                    <h2>Create New Resume</h2>
                    <p>Build a professional resume from scratch</p>
                    <button class="btn-disabled" disabled>Coming Soon</button>
                </div>
            </div>
        </main>

        <footer>
            <p>Open source resume tailoring tool</p>
        </footer>
    </div>
</body>
</html>
```

### 4.2 Tailoring Page

#### File
Rename: `frontend/index.html` → `frontend/tailor.html`
Create: `frontend/css/tailor.css`
Modify: `frontend/js/app.js` (rename to tailor.js if needed)

#### Structure (Multi-Step Flow)
```html
<div class="tailor-container" x-data="tailorApp()">
    <!-- Progress Steps Indicator -->
    <div class="steps-indicator">
        <div class="step" :class="{ active: currentStep === 1 }">1. Upload & Analyze</div>
        <div class="step" :class="{ active: currentStep === 2 }">2. Review Score</div>
        <div class="step" :class="{ active: currentStep === 3 }">3. Tailor with AI</div>
        <div class="step" :class="{ active: currentStep === 4 }">4. Download</div>
    </div>

    <!-- Step 1: Upload & Analyze -->
    <section x-show="currentStep === 1" class="step-content">
        <h2>Upload Resume & Job Description</h2>

        <div class="file-upload">
            <input type="file" accept=".doc,.docx,.pdf" @change="handleFileChange">
            <label>Choose Resume (PDF or DOCX)</label>
        </div>

        <textarea placeholder="Paste job description here..."
                  x-model="jobDescription"></textarea>

        <button @click="analyzeResume()" :disabled="!canAnalyze()">
            Analyze Resume
        </button>
    </section>

    <!-- Step 2: Score Display -->
    <section x-show="currentStep === 2" class="step-content">
        <h2>Resume Analysis</h2>

        <!-- Circular Score Gauge -->
        <div class="score-gauge">
            <div class="score-circle">
                <span x-text="originalScore.total_score"></span>
                <span class="score-label">/100</span>
            </div>
        </div>

        <!-- Score Breakdown -->
        <div class="score-breakdown">
            <div class="score-item">
                <label>Keyword Match</label>
                <div class="score-bar">
                    <div :style="`width: ${originalScore.keyword_match_score}%`"></div>
                </div>
                <span x-text="originalScore.keyword_match_score"></span>
            </div>
            <!-- More score items... -->
        </div>

        <!-- Matched/Missing Keywords -->
        <div class="keywords-section">
            <div class="matched-keywords">
                <h3>Matched Keywords</h3>
                <template x-for="keyword in originalScore.keyword_match_details.matched">
                    <span class="keyword-badge matched" x-text="keyword"></span>
                </template>
            </div>

            <div class="missing-keywords">
                <h3>Missing Keywords</h3>
                <template x-for="keyword in originalScore.keyword_match_details.missing">
                    <span class="keyword-badge missing" x-text="keyword"></span>
                </template>
            </div>
        </div>

        <!-- Recommendations -->
        <div class="recommendations">
            <h3>Recommendations</h3>
            <ul>
                <template x-for="rec in originalScore.recommendations">
                    <li x-text="rec"></li>
                </template>
            </ul>
        </div>

        <button @click="currentStep = 3">Continue to Tailoring</button>
    </section>

    <!-- Step 3: Tailor with AI -->
    <section x-show="currentStep === 3" class="step-content">
        <h2>Tailor Resume with AI</h2>

        <!-- User Info -->
        <div class="form-group">
            <input type="text" placeholder="Your Name" x-model="userName">
            <input type="text" placeholder="Company Name" x-model="company">
            <input type="text" placeholder="Job Title" x-model="jobTitle">
        </div>

        <!-- AI Selection -->
        <div class="api-selector">
            <template x-for="(available, api) in availableApis">
                <label>
                    <input type="radio" :value="api" x-model="selectedApi" :disabled="!available">
                    <span x-text="api"></span>
                </label>
            </template>
        </div>

        <!-- Custom Prompt (Optional) -->
        <div class="custom-prompt-section">
            <button @click="showCustomPrompt = !showCustomPrompt">
                Custom Instructions (Optional)
            </button>
            <div x-show="showCustomPrompt">
                <textarea x-model="customPrompt"
                          placeholder="Add specific instructions..."></textarea>
            </div>
        </div>

        <button @click="tailorResume()" :disabled="!canTailor()">
            Tailor Resume with AI
        </button>
    </section>

    <!-- Step 4: Download & Comparison -->
    <section x-show="currentStep === 4" class="step-content">
        <h2>Resume Tailored Successfully!</h2>

        <!-- Download Buttons -->
        <div class="download-buttons">
            <a :href="downloadUrl" download class="btn-download">Download PDF</a>
            <a :href="texDownloadUrl" download class="btn-download-secondary">Download LaTeX</a>
        </div>

        <!-- Before/After Score Comparison -->
        <div class="score-comparison">
            <h3>Score Improvement</h3>

            <div class="comparison-cards">
                <!-- Original Score Card -->
                <div class="score-card">
                    <h4>Original Resume</h4>
                    <div class="score-number" x-text="originalScore.total_score"></div>
                    <!-- Score breakdown... -->
                </div>

                <!-- Tailored Score Card -->
                <div class="score-card improved">
                    <h4>Tailored Resume</h4>
                    <div class="score-number" x-text="tailoredScore.total_score"></div>
                    <div class="improvement-badge"
                         x-text="`+${tailoredScore.total_score - originalScore.total_score}`">
                    </div>
                    <!-- Score breakdown... -->
                </div>
            </div>
        </div>

        <button @click="resetApp()">Tailor Another Resume</button>
    </section>
</div>
```

### 4.3 AlpineJS Application

#### File
Modify: `frontend/js/app.js`

#### Implementation
```javascript
function tailorApp() {
    return {
        currentStep: 1,

        // Step 1 data
        resumeFile: null,
        resumeFileName: '',
        jobDescription: '',
        isAnalyzing: false,
        uploadedFilePath: null,

        // Step 2 data (original score from local NLP)
        originalScore: null,
        extractedData: null,

        // Step 3 data
        userName: '',
        company: '',
        jobTitle: '',
        availableApis: {},
        selectedApi: null,
        customPrompt: '',
        showCustomPrompt: false,
        isTailoring: false,

        // Step 4 data
        tailoredScore: null,  // Local NLP score of tailored resume
        downloadUrl: null,
        texDownloadUrl: null,

        // Lifecycle
        init() {
            this.checkAvailableApis();
        },

        // Methods
        async checkAvailableApis() { /* ... */ },

        handleFileChange(event) { /* ... */ },

        canAnalyze() {
            return this.resumeFile &&
                   this.jobDescription.trim().length > 0 &&
                   !this.isAnalyzing;
        },

        async analyzeResume() {
            this.isAnalyzing = true;
            try {
                // Upload file
                const formData = new FormData();
                formData.append('file', this.resumeFile);

                const uploadResponse = await fetch(`${API_BASE_URL}/upload-resume`, {
                    method: 'POST',
                    body: formData
                });

                const uploadResult = await uploadResponse.json();
                this.uploadedFilePath = uploadResult.file_path;

                // Analyze with local NLP
                const analyzeResponse = await fetch(`${API_BASE_URL}/analyze-resume`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        file_path: this.uploadedFilePath,
                        job_description: this.jobDescription
                    })
                });

                const analyzeResult = await analyzeResponse.json();
                this.originalScore = analyzeResult.score;
                this.extractedData = analyzeResult.extracted_data;

                // Move to step 2
                this.currentStep = 2;

            } catch (error) {
                console.error('Analysis failed:', error);
                alert('Failed to analyze resume');
            } finally {
                this.isAnalyzing = false;
            }
        },

        canTailor() {
            return this.userName.trim().length > 0 &&
                   this.company.trim().length > 0 &&
                   this.jobTitle.trim().length > 0 &&
                   this.selectedApi &&
                   !this.isTailoring;
        },

        async tailorResume() {
            this.isTailoring = true;
            try {
                const response = await fetch(`${API_BASE_URL}/tailor-resume`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        file_path: this.uploadedFilePath,
                        job_description: this.jobDescription,
                        api: this.selectedApi,
                        user_name: this.userName,
                        company: this.company,
                        job_title: this.jobTitle,
                        custom_prompt: this.customPrompt.trim() || null
                    })
                });

                const result = await response.json();
                this.tailoredScore = result.tailored_score;
                this.downloadUrl = `${API_BASE_URL}/download/${result.pdf_file}`;
                this.texDownloadUrl = `${API_BASE_URL}/download/${result.tex_file}`;

                // Move to step 4
                this.currentStep = 4;

            } catch (error) {
                console.error('Tailoring failed:', error);
                alert('Failed to tailor resume');
            } finally {
                this.isTailoring = false;
            }
        },

        resetApp() {
            this.currentStep = 1;
            this.resumeFile = null;
            this.jobDescription = '';
            this.originalScore = null;
            this.tailoredScore = null;
            this.userName = '';
            this.company = '';
            this.jobTitle = '';
            this.customPrompt = '';
        }
    };
}
```

### Testing
- Navigate to landing page, click "Tailor Existing Resume"
- Upload DOCX file, paste job description, click analyze
- Verify score displays with animation
- Verify matched/missing keywords display
- Fill user info, select AI, optionally add custom prompt
- Click tailor, verify success
- Verify before/after comparison shows improvement
- Verify download buttons work
- Test on mobile/tablet devices

### Acceptance Criteria
- Landing page displays with two options
- Tailoring page shows 4-step flow
- Step 1: File upload and job description work
- Step 2: Score displays with all details
- Step 3: User can configure tailoring options
- Step 4: Download and comparison work correctly
- Mobile responsive design
- Smooth transitions between steps

### Estimated Time
3-4 days

---

## PHASE 5: Score Visualization

### Objective
Create visually appealing, animated score displays and comparisons.

### 5.1 Circular Score Gauge

#### File
Create: `frontend/css/components/score-gauge.css`

#### Implementation
Use CSS animations or SVG to create animated circular progress:
```css
.score-circle {
    width: 200px;
    height: 200px;
    border-radius: 50%;
    background: conic-gradient(
        #4ade80 0deg,
        #4ade80 calc(var(--score) * 3.6deg),
        #e5e7eb calc(var(--score) * 3.6deg),
        #e5e7eb 360deg
    );
    animation: fillScore 2s ease-out;
}

@keyframes fillScore {
    from { --score: 0; }
    to { --score: var(--final-score); }
}
```

### 5.2 Score Breakdown Bars

#### Implementation
Horizontal bars that animate from 0 to score value:
```css
.score-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    width: 0;
    animation: fillBar 1s ease-out forwards;
    animation-delay: var(--delay);
}

@keyframes fillBar {
    to { width: var(--target-width); }
}
```

### 5.3 Keyword Badges

#### Implementation
```css
.keyword-badge {
    display: inline-block;
    padding: 0.5rem 1rem;
    border-radius: 1rem;
    margin: 0.25rem;
    transition: all 0.3s;
}

.keyword-badge.matched {
    background: #10b981;
    color: white;
}

.keyword-badge.missing {
    background: #ef4444;
    color: white;
}
```

### 5.4 Before/After Comparison

#### Implementation
Side-by-side cards with improvement indicators:
```html
<div class="comparison-cards">
    <div class="score-card original">
        <div class="score-value">72</div>
        <div class="score-breakdown">...</div>
    </div>

    <div class="improvement-arrow">→</div>

    <div class="score-card improved">
        <div class="score-value">89</div>
        <div class="improvement-badge">+17</div>
        <div class="score-breakdown">...</div>
    </div>
</div>
```

### Testing
- Verify circular gauge animates smoothly
- Verify score bars animate with stagger effect
- Verify colors change based on score ranges
- Verify keyword badges display correctly
- Verify before/after comparison is clear
- Test on different screen sizes
- Test with various score values (low, medium, high)

### Acceptance Criteria
- All animations run smoothly (60fps)
- Score visualizations are clear and intuitive
- Color coding matches score ranges
- Mobile responsive
- Accessible (screen reader friendly)

### Estimated Time
2-3 days

---

## PHASE 6: Integration & End-to-End Testing

### Objective
Test the complete user journey and ensure all components work together seamlessly.

### 6.1 Complete User Journey Tests

#### Test Scenarios

**Scenario 1: Happy Path - DOCX Resume**
1. Navigate to landing page
2. Click "Tailor Existing Resume"
3. Upload DOCX resume
4. Paste job description
5. Click "Analyze Resume"
6. Verify score displays (should be reasonable, e.g., 60-80)
7. Verify matched/missing keywords
8. Fill user info
9. Select AI provider
10. Click "Tailor Resume"
11. Verify tailored score is higher
12. Download PDF and LaTeX
13. Verify files are valid

**Scenario 2: Happy Path - PDF Resume**
Same as above but with PDF upload.

**Scenario 3: Low Initial Score**
Test with resume that poorly matches job description:
- Initial score should be low (30-50)
- Should show many missing keywords
- After tailoring, score should improve significantly

**Scenario 4: High Initial Score**
Test with resume that already matches well:
- Initial score should be high (75-90)
- Few missing keywords
- After tailoring, slight improvement

**Scenario 5: Custom Prompt**
- Add custom prompt (e.g., "Focus on leadership skills")
- Verify tailored resume reflects custom instructions
- Score should still improve

**Scenario 6: Different AI Providers**
Test tailoring with:
- OpenAI
- Gemini
- Claude
- Verify all work correctly

#### File
Create: `backend/tests/test_integration.py`
Create: `frontend/tests/e2e/test_user_journey.js` (if using Playwright/Cypress)

### 6.2 Error Handling Tests

#### Test Scenarios
- Upload invalid file type
- Upload corrupt PDF/DOCX
- Submit without job description
- Submit with very short job description
- Network timeout during analysis
- Network timeout during tailoring
- API key missing/invalid
- Backend server down

#### Expected Behavior
- Clear error messages
- User can retry without losing data
- Graceful degradation

### 6.3 Performance Tests

#### Metrics to Measure
- Resume analysis time (target: < 5 seconds)
- Resume tailoring time (target: < 30 seconds total)
- File upload time
- Page load time
- Animation smoothness

#### Tools
- Browser DevTools Performance tab
- Lighthouse audit
- Manual testing with large files (10+ page resumes)

### Testing Checklist
- [ ] DOCX upload and analysis works
- [ ] PDF upload and analysis works
- [ ] Score displays correctly
- [ ] Keywords extracted accurately
- [ ] Tailoring improves score
- [ ] Download links work
- [ ] All AI providers work
- [ ] Custom prompts work
- [ ] Error handling works
- [ ] Mobile responsive
- [ ] Performance acceptable
- [ ] All unit tests pass
- [ ] All integration tests pass

### Acceptance Criteria
- All test scenarios pass
- No critical bugs
- Performance metrics met
- Error handling is user-friendly
- Mobile and desktop work correctly

### Estimated Time
3-4 days

---

## PHASE 7: NLP Accuracy Tuning

### Objective
Fine-tune NLP algorithms to maximize accuracy and usefulness.

### 7.1 Keyword Extraction Accuracy

#### Test Data
Collect 30+ real job descriptions across industries:
- 10 Software Engineering roles
- 10 Data Science roles
- 10 Product/Project Management roles

#### Evaluation
For each job description:
1. Extract keywords using NLP
2. Manually review extracted keywords
3. Calculate precision (% of extracted keywords that are relevant)
4. Calculate recall (% of important keywords that were extracted)
5. Identify patterns in missed keywords
6. Adjust extraction logic

#### Tuning Parameters
- spaCy NER confidence threshold
- Noun phrase filtering rules
- Technical term patterns
- Keyword normalization rules

### 7.2 Scoring Algorithm Weights

#### Initial Weights
```python
total_score = (
    keyword_match_score * 0.40 +
    relevance_score * 0.25 +
    ats_score * 0.20 +
    quality_score * 0.15
)
```

#### Validation
Test with 20+ real resumes:
1. Score each resume against its target job
2. Manually evaluate if score is reasonable
3. Compare original vs tailored scores
4. Ensure tailored always scores higher
5. Adjust weights if needed

#### Metrics
- Average score improvement after tailoring (target: 10-25 points)
- Score variance (should be reasonable spread, not all 70-75)
- Correlation with manual evaluation

### 7.3 Recommendation Quality

#### Evaluation
For each test case:
1. Review generated recommendations
2. Check if they are actionable
3. Check if they are accurate
4. Check for false positives (recommending something already present)

#### Improvements
- Filter out redundant recommendations
- Prioritize recommendations by impact
- Make language more user-friendly

### Documentation
Create: `docs/NLP_TUNING_RESULTS.md`

Document:
- Test data used
- Accuracy metrics achieved
- Final tuned parameters
- Known limitations

### Acceptance Criteria
- Keyword extraction precision > 80%
- Keyword extraction recall > 70%
- Tailored resume always scores 10+ points higher
- Recommendations are accurate and actionable
- Documentation complete

### Estimated Time
2-3 days

---

## PHASE 8: Documentation & Polish

### Objective
Finalize documentation, optimize performance, and polish user experience.

### 8.1 Code Documentation

#### Backend
- Add docstrings to all NLP functions
- Add inline comments for complex logic
- Document scoring algorithm
- Document configuration options

#### Frontend
- Add JSDoc comments to key functions
- Document AlpineJS component structure
- Document API endpoints used

### 8.2 User Documentation

#### File
Create: `docs/USER_GUIDE.md`

Contents:
- How to use JobGlove
- Understanding your scores
- Tips for improving scores
- What each score category means
- How to write effective custom prompts
- Troubleshooting common issues

### 8.3 Developer Documentation

#### File
Update: `README.md`

Contents:
- Updated project description (include NLP features)
- Updated installation instructions (spaCy, NLTK)
- Updated setup instructions
- API documentation
- Architecture overview

### 8.4 Performance Optimization

#### Backend
- Cache spaCy model (load once at startup)
- Optimize keyword matching algorithm
- Profile slow functions
- Add caching where appropriate

#### Frontend
- Minimize CSS/JS files
- Optimize images
- Lazy load non-critical resources
- Test with slow network connections

### 8.5 UX Polish

#### Improvements
- Add loading skeletons instead of spinners
- Add micro-interactions (hover effects, etc.)
- Improve error messages
- Add success animations
- Add tooltips for score explanations
- Improve mobile experience

### 8.6 Security Review

#### Checklist
- [ ] File upload validation
- [ ] Input sanitization
- [ ] File size limits enforced
- [ ] Temporary file cleanup
- [ ] API key security
- [ ] No sensitive data in logs

### Testing
- Run full test suite
- Manual QA on all features
- Cross-browser testing (Chrome, Firefox, Safari)
- Accessibility audit (WCAG compliance)
- Security scan

### Acceptance Criteria
- All code documented
- User guide complete
- README updated
- Performance optimized (analysis < 5s, tailoring < 30s)
- UX polished and professional
- Security review passed
- All tests passing

### Estimated Time
2-3 days

---

## FINAL CHECKLIST

### Functionality
- [ ] Resume upload (PDF and DOCX)
- [ ] Local NLP analysis
- [ ] Pre-tailoring scoring
- [ ] Keyword extraction and matching
- [ ] AI-based tailoring
- [ ] Post-tailoring scoring
- [ ] Before/after comparison
- [ ] PDF/LaTeX download

### Quality
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] E2E tests pass
- [ ] Code review complete
- [ ] Documentation complete
- [ ] Performance benchmarks met

### User Experience
- [ ] Intuitive UI/UX
- [ ] Clear error messages
- [ ] Smooth animations
- [ ] Mobile responsive
- [ ] Accessible (WCAG)

### Technical
- [ ] NLP accuracy validated
- [ ] API endpoints documented
- [ ] Security review passed
- [ ] Performance optimized

---

## TOTAL ESTIMATED TIME

- Phase 1: 1-2 hours
- Phase 2: 3-4 days
- Phase 3: 2-3 days
- Phase 4: 3-4 days
- Phase 5: 2-3 days
- Phase 6: 3-4 days
- Phase 7: 2-3 days
- Phase 8: 2-3 days

**Total: 17-23 days (3.5-4.5 weeks)**

---

## DEPENDENCIES & RISKS

### Dependencies
- spaCy model availability
- NLTK data availability
- AI API availability (OpenAI, Gemini, Claude)
- LaTeX compilation tools

### Risks
- NLP accuracy may vary across different resume formats
- Keyword extraction may miss domain-specific terms
- Scoring may need multiple tuning iterations
- PDF text extraction may fail for certain formats

### Mitigation
- Test with diverse resume formats early
- Collect feedback and iterate on accuracy
- Provide manual override options where possible
- Have fallback PDF parsers (PyMuPDF + pdfplumber)

---

## SUCCESS METRICS

### Technical Metrics
- NLP analysis completes in < 5 seconds
- Keyword extraction accuracy > 75%
- Tailored resume scores 10-25 points higher than original
- Zero critical bugs
- All tests passing

### User Metrics
- Users can complete full workflow without errors
- Score visualizations are clear and understandable
- Users can download tailored resume successfully
- Mobile users can complete workflow

---

## POST-LAUNCH IMPROVEMENTS

Future enhancements (not in current plan):
- Save resume history
- A/B test different AI providers
- Resume template selection
- Browser extension for job description extraction
- Batch processing for multiple jobs
- Resume preview before download
- Export to other formats (Word, HTML)
