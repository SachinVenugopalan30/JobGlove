"""
Test that TECHNICAL SKILLS sections (with space) are properly parsed and rendered in LaTeX
"""
import pytest
from services.latex_generator import LaTeXGenerator


class TestTechnicalSkillsRendering:
    """Test that multi-word section names like 'TECHNICAL SKILLS' work correctly"""
    
    def test_parse_technical_skills_section(self):
        """Verify that [TECHNICAL SKILLS] section is properly parsed"""
        resume = """
[EDUCATION]
Arizona State University | Tempe, AZ
Master of Science in Computer Science | August 2025 - May 2027

[TECHNICAL SKILLS]
Languages & Libraries: Python, Java, C, SQL (PostgreSQL), Pandas, NumPy, Scikit-learn, TensorFlow, PyTorch
Machine Learning & AI: Predictive Modeling, Clustering, NLP, Time Series Forecasting, Anomaly Detection, Deep Learning
Visualization & Analytics: Tableau, Power BI, Matplotlib, Seaborn, SciPy, Excel
Cloud & Deployment: AWS, GCP, Azure, Docker, Git
Other Tools & Skills: Exploratory Data Analysis (EDA), Statistical Modeling, Model Deployment, Agile Methods

[EXPERIENCE]
Company | Location
Software Engineer | Jan 2020 - Present
- Built machine learning models
"""
        
        latex_output = LaTeXGenerator.parse_structured_resume(resume)
        
        # Should contain the Technical Skills section
        assert '\\section{Technical Skills}' in latex_output
        
        # Should contain all the skill categories
        assert 'Languages \\& Libraries' in latex_output
        assert 'Machine Learning \\& AI' in latex_output
        assert 'Visualization \\& Analytics' in latex_output
        assert 'Cloud \\& Deployment' in latex_output
        assert 'Other Tools \\& Skills' in latex_output
        
        # Should contain some of the actual skills (with proper escaping)
        assert 'Python' in latex_output
        assert 'TensorFlow' in latex_output
        assert 'AWS' in latex_output
        
    def test_parse_skills_section_without_technical(self):
        """Verify that [SKILLS] section (without TECHNICAL) also works"""
        resume = """
[EDUCATION]
University | Location
Degree | 2020

[SKILLS]
Programming: Python, Java
Tools: Docker, Git

[EXPERIENCE]
Company | Location
Engineer | 2020-2023
- Built apps
"""
        
        latex_output = LaTeXGenerator.parse_structured_resume(resume)
        
        # Should contain the Technical Skills section (note: _format_skills adds "Technical" to the heading)
        assert '\\section{Technical Skills}' in latex_output
        assert 'Programming' in latex_output
        assert 'Tools' in latex_output
        
    def test_both_skills_sections_in_same_resume(self):
        """Test edge case: resume has both [SKILLS] and [TECHNICAL SKILLS]"""
        resume = """
[TECHNICAL SKILLS]
Languages: Python, Java

[SKILLS]
Soft Skills: Communication, Leadership

[EXPERIENCE]
Company | Location
Role | 2020-2023
- Did stuff
"""
        
        latex_output = LaTeXGenerator.parse_structured_resume(resume)
        
        # Both should be rendered (though having both is unusual)
        assert 'Languages' in latex_output
        assert 'Soft Skills' in latex_output or 'Leadership' in latex_output
        
    def test_technical_skills_preserves_special_characters(self):
        """Verify that special characters in skills are properly escaped"""
        resume = """
[TECHNICAL SKILLS]
Languages & Libraries: C++, C#, .NET
Tools: Docker & Kubernetes
Frameworks: Node.js, Vue.js

[EXPERIENCE]
Company | Location
Role | 2020-2023
- Built things
"""
        
        latex_output = LaTeXGenerator.parse_structured_resume(resume)
        
        # Special characters should be escaped
        assert 'C++' in latex_output or 'C\\texttt{++}' in latex_output  # C++ might be handled specially
        assert '.NET' in latex_output  # Periods don't need escaping in text mode
        assert 'Node.js' in latex_output
        
        # Ampersands should be escaped
        assert '\\&' in latex_output
        
    def test_empty_technical_skills_section(self):
        """Verify that empty TECHNICAL SKILLS section is skipped"""
        resume = """
[EDUCATION]
University | Location
Degree | 2020

[TECHNICAL SKILLS]

[EXPERIENCE]
Company | Location
Role | 2020-2023
- Did work
"""
        
        latex_output = LaTeXGenerator.parse_structured_resume(resume)
        
        # Empty skills section should not appear
        # (The section might be present but should be minimal/empty)
        # Since _format_skills returns "" for empty content, section shouldn't be added
        assert latex_output.count('\\section{Technical Skills}') == 0
