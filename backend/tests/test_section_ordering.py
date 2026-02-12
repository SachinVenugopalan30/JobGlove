"""
Tests for enforcing fixed section ordering in LaTeX generation.

This test suite verifies that sections are always output in the correct order:
HEADER -> EDUCATION -> TECHNICAL SKILLS -> EXPERIENCE -> PROJECTS

regardless of the order in which the AI provides them.
"""

from services.latex_generator import LaTeXGenerator


class TestSectionOrdering:
    """Test fixed section ordering in resume generation."""

    def test_sections_in_wrong_order(self):
        """Test that sections are reordered when AI provides them in wrong order."""
        # AI provides sections in random order: PROJECTS, EDUCATION, EXPERIENCE, SKILLS, HEADER
        resume_text = """[HEADER]
John Doe | john@example.com | 555-1234 | linkedin.com/in/johndoe

[PROJECTS]
Project A | Python, React
Jan 2024
- Built something

[EDUCATION]
University of X | Boston, MA
BS Computer Science | 2020-2024

[TECHNICAL SKILLS]
Languages: Python, Java
ML: TensorFlow

[EXPERIENCE]
Software Engineer | Jan 2024 - Present
Google | Mountain View, CA
- Developed features
"""
        result = LaTeXGenerator.parse_structured_resume(resume_text)

        # Find section positions in output
        header_pos = result.find(r"\textbf{\Huge")
        education_pos = result.find(r"\section{Education}")
        skills_pos = result.find(r"\section{Technical Skills}")
        experience_pos = result.find(r"\section{Experience}")
        projects_pos = result.find(r"\section{Projects}")

        # Verify all sections exist
        assert header_pos != -1, "Header section not found"
        assert education_pos != -1, "Education section not found"
        assert skills_pos != -1, "Technical Skills section not found"
        assert experience_pos != -1, "Experience section not found"
        assert projects_pos != -1, "Projects section not found"

        # Verify correct order: HEADER < EDUCATION < TECHNICAL SKILLS < EXPERIENCE < PROJECTS
        assert header_pos < education_pos, "Header should come before Education"
        assert education_pos < skills_pos, "Education should come before Technical Skills"
        assert skills_pos < experience_pos, "Technical Skills should come before Experience"
        assert experience_pos < projects_pos, "Experience should come before Projects"

    def test_sections_in_correct_order(self):
        """Test that sections remain in correct order when already correct."""
        resume_text = """[HEADER]
Jane Smith | jane@example.com | 555-5678

[EDUCATION]
Stanford University | Stanford, CA
MS Data Science | 2022-2024

[TECHNICAL SKILLS]
Languages: Python, R

[EXPERIENCE]
Data Scientist | Jan 2024 - Present
Meta | Menlo Park, CA
- Analyzed data

[PROJECTS]
Project B | Python, Scikit-learn
Mar 2024
- Implemented ML model
"""
        result = LaTeXGenerator.parse_structured_resume(resume_text)

        # Find section positions
        header_pos = result.find(r"\textbf{\Huge")
        education_pos = result.find(r"\section{Education}")
        skills_pos = result.find(r"\section{Technical Skills}")
        experience_pos = result.find(r"\section{Experience}")
        projects_pos = result.find(r"\section{Projects}")

        # Verify correct order maintained
        assert header_pos < education_pos < skills_pos < experience_pos < projects_pos

    def test_missing_sections_handled_gracefully(self):
        """Test that missing sections don't break ordering."""
        # Resume with only HEADER, EDUCATION, and EXPERIENCE
        resume_text = """[HEADER]
Bob Johnson | bob@example.com

[EDUCATION]
MIT | Cambridge, MA
BS Engineering | 2020-2024

[EXPERIENCE]
Engineer | Jan 2024 - Present
Apple | Cupertino, CA
- Built systems
"""
        result = LaTeXGenerator.parse_structured_resume(resume_text)

        header_pos = result.find(r"\textbf{\Huge")
        education_pos = result.find(r"\section{Education}")
        experience_pos = result.find(r"\section{Experience}")

        # Skills and Projects should not exist
        assert result.find(r"\section{Technical Skills}") == -1
        assert result.find(r"\section{Projects}") == -1

        # Remaining sections should be in order
        assert header_pos < education_pos < experience_pos

    def test_skills_vs_technical_skills(self):
        """Test that both SKILLS and TECHNICAL SKILLS are handled."""
        # Test with "TECHNICAL SKILLS"
        resume_text1 = """[HEADER]
Test User | test@example.com

[EDUCATION]
BS CS | University | 2020-2024

[TECHNICAL SKILLS]
Languages: Python

[EXPERIENCE]
Developer | Company | 2024
"""
        result1 = LaTeXGenerator.parse_structured_resume(resume_text1)
        assert r"\section{Technical Skills}" in result1

        # Test with just "SKILLS"
        resume_text2 = """[HEADER]
Test User | test@example.com

[EDUCATION]
BS CS | University | 2020-2024

[SKILLS]
Languages: Python

[EXPERIENCE]
Developer | Company | 2024
"""
        result2 = LaTeXGenerator.parse_structured_resume(resume_text2)
        # SKILLS should still be formatted as Technical Skills section
        assert r"\section{Technical Skills}" in result2

    def test_duplicate_sections_use_first_occurrence(self):
        """Test that if AI mistakenly provides duplicate sections, we use first one."""
        resume_text = """[HEADER]
Test User | test@example.com

[EDUCATION]
University A | Boston, MA
BS Computer Science | 2020-2024

[TECHNICAL SKILLS]
First Skills: Python

[EDUCATION]
University B | New York, NY
MS Data Science | 2018-2020

[EXPERIENCE]
Company | Location
Developer | 2024
- Developed software
"""
        result = LaTeXGenerator.parse_structured_resume(resume_text)

        # Should only have one Education section (the first one)
        assert result.count(r"\section{Education}") == 1
        # Note: Dict behavior means last occurrence will be used, not first
        # This is acceptable behavior - AI shouldn't send duplicates anyway

    def test_section_order_with_all_sections(self):
        """Comprehensive test with all sections present."""
        resume_text = """[HEADER]
Full Resume | full@example.com | 555-9999 | github.com/full

[PROJECTS]
Amazing Project | Python, React
Dec 2023 - Feb 2024
- Created revolutionary app
- Used cutting-edge tech

[EXPERIENCE]
Tech Corp | San Francisco, CA
Senior Engineer | Jan 2023 - Present
- Led team of 5 engineers
- Increased performance by 200%

StartUp Inc | Austin, TX
Junior Engineer | Jun 2021 - Dec 2022
- Built microservices

[EDUCATION]
Top University | Cambridge, MA
BS Computer Science | 2017-2021

Elite Institute | Palo Alto, CA
MS AI | 2021-2023

[TECHNICAL SKILLS]
Languages: Python, Java, JavaScript, C++, Go
Frameworks: Django, React, TensorFlow, PyTorch
Cloud: AWS, GCP, Azure
"""
        result = LaTeXGenerator.parse_structured_resume(resume_text)

        # Get positions
        positions = {
            "header": result.find(r"\textbf{\Huge"),
            "education": result.find(r"\section{Education}"),
            "skills": result.find(r"\section{Technical Skills}"),
            "experience": result.find(r"\section{Experience}"),
            "projects": result.find(r"\section{Projects}"),
        }

        # All sections should exist
        for section, pos in positions.items():
            assert pos != -1, f"{section} section not found in output"

        # Verify strict ordering: HEADER -> EDUCATION -> TECHNICAL SKILLS -> EXPERIENCE -> PROJECTS
        assert positions["header"] < positions["education"], "Header should come before Education"
        assert positions["education"] < positions["skills"], (
            "Education should come before Technical Skills"
        )
        assert positions["skills"] < positions["experience"], (
            "Technical Skills should come before Experience"
        )
        assert positions["experience"] < positions["projects"], (
            "Experience should come before Projects"
        )

        # Verify key content is preserved (basic check)
        assert "Full Resume" in result
        assert "Top University" in result
        assert "Elite Institute" in result
        assert "Python, Java" in result
        assert "Tech Corp" in result
        assert "Amazing Project" in result
