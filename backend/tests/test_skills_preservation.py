"""
Tests to verify that the TECHNICAL SKILLS section is preserved in tailored resumes
"""

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
        service = AIService.get_provider("openai", "dummy-key")
        prompt = service._create_score_and_tailor_prompt(resume, job_description)

        # Verify the prompt contains preservation instructions
        prompt_upper = prompt.upper()

        assert "PRESERVE SKILLS SECTION EXACTLY AS IN ORIGINAL" in prompt_upper
        assert "COPY THE EXACT SKILLS FROM THE ORIGINAL RESUME - DO NOT MODIFY" in prompt_upper

    def test_prompt_distinguishes_skills_from_experience(self):
        """Verify prompt treats skills differently from experience"""
        resume = "Sample resume with TECHNICAL SKILLS section"
        jd = "Job description"

        service = AIService.get_provider("openai", "dummy-key")
        prompt = service._create_score_and_tailor_prompt(resume, jd)

        # Should preserve skills but tailor experience
        prompt_upper = prompt.upper()
        assert "PRESERVE SKILLS" in prompt_upper
        assert "COPY THE EXACT SKILLS" in prompt_upper or "DO NOT MODIFY" in prompt_upper
        # Experience should be tailored
        assert "EXPERIENCE" in prompt
        assert "REFRAME" in prompt_upper or "ALIGN WITH JOB" in prompt_upper
