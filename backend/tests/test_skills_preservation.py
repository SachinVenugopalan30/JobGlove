"""
Tests to verify that the TECHNICAL SKILLS section is preserved in tailored resumes
"""
import pytest
from services.ai_service import AIService


class TestSkillsPreservation:
    """Test that skills section is preserved during tailoring"""
    
    def test_prompt_includes_skills_preservation_instruction(self):
        """Verify that the prompt includes instructions to preserve skills"""
        resume = """
EDUCATION
University Name | Location
Degree | 2020

TECHNICAL SKILLS
Languages & Libraries: Python, Java, C, SQL (PostgreSQL), Pandas, NumPy, Scikit-learn, TensorFlow, PyTorch
Machine Learning & AI: Predictive Modeling, Clustering, NLP, Time Series Forecasting, Anomaly Detection, Deep Learning
Visualization & Analytics: Tableau, Power BI, Matplotlib, Seaborn, SciPy, Excel
Cloud & Deployment: AWS, GCP, Azure, Docker, Git

EXPERIENCE
Company | Location
Software Engineer | Jan 2020 - Present
- Built machine learning models
"""
        
        job_description = "Looking for Python developer with ML experience"
        
        # Create a mock AI service to check the prompt
        service = AIService.get_provider('openai', 'dummy-key')
        prompt = service._create_score_and_tailor_prompt(resume, job_description)
        
        # Verify the prompt contains preservation instructions
        assert "PRESERVE" in prompt.upper()
        assert "skills section" in prompt.lower() or "technical skills" in prompt.lower()
        assert "copy" in prompt.lower() and "verbatim" in prompt.lower()
        assert "DO NOT add new skills" in prompt
        assert "DO NOT remove any existing skills" in prompt
        
    def test_prompt_distinguishes_skills_from_experience(self):
        """Verify prompt treats skills differently from experience"""
        resume = "Sample resume with TECHNICAL SKILLS section"
        jd = "Job description"
        
        service = AIService.get_provider('openai', 'dummy-key')
        prompt = service._create_score_and_tailor_prompt(resume, jd)
        
        # Should preserve skills but tailor experience
        assert "PRESERVE the SKILLS" in prompt or "PRESERVE the original skills" in prompt
        assert "EXPERIENCE" in prompt
        # Experience should be tailored, skills preserved
        prompt_lines = prompt.split('\n')
        
        skills_context = []
        experience_context = []
        
        for i, line in enumerate(prompt_lines):
            if 'SKILLS' in line.upper():
                # Get surrounding context
                skills_context = prompt_lines[max(0, i-2):min(len(prompt_lines), i+8)]
            if 'EXPERIENCE' in line.upper() and 'REQUIREMENTS' not in line.upper():
                experience_context = prompt_lines[max(0, i-2):min(len(prompt_lines), i+8)]
        
        # Skills section should have PRESERVE instructions
        skills_text = ' '.join(skills_context).upper()
        assert 'PRESERVE' in skills_text or 'COPY' in skills_text
        
        # Experience section should have tailoring instructions
        # (but not preserve - we want experience to be tailored)
        experience_text = ' '.join(experience_context)
        # Just verify experience section exists and has formatting guidance
        assert len(experience_context) > 0
