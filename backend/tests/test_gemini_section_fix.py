"""
Test for fixing Gemini's missing square bracket issue in section headers.
"""

import pytest
from services.latex_generator import LaTeXGenerator


class TestGeminiSectionHeaderFix:
    """Test that section headers without square brackets are normalized."""

    def test_normalize_section_headers_adds_brackets(self):
        """Test that missing brackets are added to section headers."""
        resume_text = """Education
Arizona State University | Tempe, AZ
Master of Science in Computer Science | May 2027

[EXPERIENCE]
Senior Data Scientist | October 2023 - April 2025
Firstsource Solutions Ltd. | Bengaluru, India
- Did something great

Technical Skills
Languages: Python, Java
"""
        normalized = LaTeXGenerator._normalize_section_headers(resume_text)

        assert '[EDUCATION]' in normalized
        assert '[TECHNICAL SKILLS]' in normalized
        assert '[EXPERIENCE]' in normalized
        assert 'Education\n' not in normalized or '[EDUCATION]' in normalized

    def test_gemini_style_response_full_parse(self):
        """Test complete parsing of Gemini-style response with missing brackets."""
        resume_text = """[HEADER]
John Doe | john@example.com | 555-1234

Education
Arizona State University | Tempe, AZ
Master of Science in Computer Science | May 2027
PES University | Bengaluru, India
Bachelor of Technology in Computer Science | May 2020

[EXPERIENCE]
Senior Data Scientist | October 2023 - April 2025
Firstsource Solutions Ltd. | Bengaluru, India
- Enhanced efficiency by 14%

Technical Skills
Languages: Python, Java, SQL
Frameworks: Django, React

[PROJECTS]
Project A | Python, React
Jan 2024 - Present
- Built something
"""
        result = LaTeXGenerator.parse_structured_resume(resume_text)

        # Verify all sections are present in output
        assert r'\textbf{\Huge' in result, "Header missing"
        assert r'\section{Education}' in result, "Education section missing"
        assert r'\section{Experience}' in result, "Experience section missing"
        assert r'\section{Technical Skills}' in result, "Technical Skills section missing"
        assert r'\section{Projects}' in result, "Projects section missing"

        # Verify Education content is present
        assert 'Arizona State University' in result
        assert 'Master of Science in Computer Science' in result

    def test_mixed_bracket_styles(self):
        """Test handling of mixed bracket styles (some with, some without)."""
        resume_text = """[HEADER]
Jane Smith | jane@example.com

Education
Stanford University | Palo Alto, CA
MS Computer Science | 2024

[EXPERIENCE]
Engineer | Google | 2024
- Built features

Skills
Python: Advanced
"""
        result = LaTeXGenerator.parse_structured_resume(resume_text)

        # All sections should be present
        assert r'\section{Education}' in result
        assert r'\section{Experience}' in result
        assert r'\section{Technical Skills}' in result
        assert 'Stanford University' in result

    def test_case_insensitive_section_matching(self):
        """Test that section headers are matched case-insensitively."""
        resume_text = """[HEADER]
Test User | test@example.com

education
University A | Location A
Degree | 2024

Experience
Company | Location
Role | 2024
- Task

technical skills
Languages: Python
"""
        normalized = LaTeXGenerator._normalize_section_headers(resume_text)

        # Should normalize to uppercase with brackets
        assert '[EDUCATION]' in normalized
        assert '[EXPERIENCE]' in normalized
        assert '[TECHNICAL SKILLS]' in normalized

    def test_does_not_break_correctly_formatted_sections(self):
        """Test that correctly formatted sections remain unchanged."""
        resume_text = """[HEADER]
User | email@example.com

[EDUCATION]
University | Location
Degree | 2024

[EXPERIENCE]
Company | Location
Role | 2024
- Task

[TECHNICAL SKILLS]
Languages: Python
"""
        normalized = LaTeXGenerator._normalize_section_headers(resume_text)

        # Should remain the same
        assert normalized.count('[EDUCATION]') == 1
        assert normalized.count('[EXPERIENCE]') == 1
        assert normalized.count('[TECHNICAL SKILLS]') == 1

        # Parse should work correctly
        result = LaTeXGenerator.parse_structured_resume(resume_text)
        assert r'\section{Education}' in result
        assert r'\section{Experience}' in result
        assert r'\section{Technical Skills}' in result
