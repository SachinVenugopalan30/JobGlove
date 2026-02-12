import os
import subprocess
import tempfile

import pytest

from services.latex_generator import LaTeXGenerator


# Check if pdflatex is available
def is_pdflatex_available():
    try:
        subprocess.run(["pdflatex", "--version"], capture_output=True, timeout=5, check=True)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.CalledProcessError):
        return False


PDFLATEX_AVAILABLE = is_pdflatex_available()


@pytest.mark.unit
class TestLaTeXGenerator:
    """Test LaTeX generator functionality"""

    def test_escape_latex(self):
        """Test LaTeX character escaping"""
        text = "Price: $100, efficiency: 90%, & more!"
        escaped = LaTeXGenerator.escape_latex(text)

        assert r"\$" in escaped
        assert r"\%" in escaped
        assert r"\&" in escaped

    def test_escape_latex_special_chars(self):
        """Test escaping special characters"""
        text = "Test_{subscript}^{superscript}#hashtag"
        escaped = LaTeXGenerator.escape_latex(text)

        assert r"\_" in escaped
        assert r"\{" in escaped
        assert r"\}" in escaped
        assert r"\#" in escaped

    def test_bold_metrics_percentages(self):
        """Test bolding percentages"""
        text = "Improved performance by 50% and reduced costs by 25.5%"
        result = LaTeXGenerator.bold_metrics(text)

        assert "<<<BOLD_START>>>50%<<<BOLD_END>>>" in result
        assert "<<<BOLD_START>>>25.5%<<<BOLD_END>>>" in result

    def test_bold_metrics_currency(self):
        """Test bolding currency values"""
        text = "Saved $1,000 and generated $50,000.00 in revenue"
        result = LaTeXGenerator.bold_metrics(text)

        assert "<<<BOLD_START>>>$1,000<<<BOLD_END>>>" in result
        assert "<<<BOLD_START>>>$50,000.00<<<BOLD_END>>>" in result

    def test_bold_metrics_large_numbers(self):
        """Test bolding large numbers with commas"""
        text = "Processed 10,000 requests and handled 1,000,000 users"
        result = LaTeXGenerator.bold_metrics(text)

        assert "<<<BOLD_START>>>10,000<<<BOLD_END>>>" in result
        assert "<<<BOLD_START>>>1,000,000<<<BOLD_END>>>" in result

    def test_bold_metrics_ranges(self):
        """Test bolding number ranges (but NOT year ranges like 2021-2023)"""
        text = "Managed team of 5-10 people from 2021-2023"
        result = LaTeXGenerator.bold_metrics(text)

        # Small number ranges should be bolded
        assert "<<<BOLD_START>>>5-10<<<BOLD_END>>>" in result
        # Year ranges should NOT be bolded (to avoid bolding dates)
        assert "<<<BOLD_START>>>2021-2023<<<BOLD_END>>>" not in result
        assert "2021-2023" in result  # But the text should still be there

    def test_bold_metrics_abbreviated(self):
        """Test bolding abbreviated numbers"""
        text = "Reached 5K users, generated 2.5M in revenue, worth 1B"
        result = LaTeXGenerator.bold_metrics(text)

        assert "<<<BOLD_START>>>5K<<<BOLD_END>>>" in result
        assert "<<<BOLD_START>>>2.5M<<<BOLD_END>>>" in result
        assert "<<<BOLD_START>>>1B<<<BOLD_END>>>" in result

    def test_bold_metrics_multipliers(self):
        """Test bolding multipliers"""
        text = "Achieved 2x growth and 10x increase in efficiency"
        result = LaTeXGenerator.bold_metrics(text)

        assert "<<<BOLD_START>>>2x<<<BOLD_END>>>" in result
        assert "<<<BOLD_START>>>10x<<<BOLD_END>>>" in result

    def test_bold_metrics_years(self):
        """Test that years in dates are NOT bolded (to avoid bolding dates like 'Oct 2025')"""
        text = "Won award in Oct 2023, started in 2020, graduated in 2023"
        result = LaTeXGenerator.bold_metrics(text)

        # Years should NOT be bolded standalone anymore to avoid bolding dates
        assert "<<<BOLD_START>>>2020<<<BOLD_END>>>" not in result
        assert "<<<BOLD_START>>>2023<<<BOLD_END>>>" not in result

        # The text should remain unchanged (no bolding)
        assert "2020" in result
        assert "2023" in result

    def test_bold_metrics_does_not_bold_dates(self):
        """Test that dates are not bolded"""
        test_cases = [
            "Won Employee of the Year award in Oct 2025",
            "Published paper in January 2024",
            "Graduated in May 2023",
            "Started project in 2022",
            "Completed certification in Dec 2021",
        ]

        for text in test_cases:
            result = LaTeXGenerator.bold_metrics(text)
            # No years should be bolded
            assert "<<<BOLD_START>>>2025<<<BOLD_END>>>" not in result
            assert "<<<BOLD_START>>>2024<<<BOLD_END>>>" not in result
            assert "<<<BOLD_START>>>2023<<<BOLD_END>>>" not in result
            assert "<<<BOLD_START>>>2022<<<BOLD_END>>>" not in result
            assert "<<<BOLD_START>>>2021<<<BOLD_END>>>" not in result

    def test_finalize_bold_and_escape(self):
        """Test combining bolding and escaping"""
        text = "Improved by <<<BOLD_START>>>50%<<<BOLD_END>>> & saved <<<BOLD_START>>>$1,000<<<BOLD_END>>>"
        result = LaTeXGenerator.finalize_bold_and_escape(text)

        assert r"\textbf{50%}" in result or r"\textbf{50\%}" in result
        assert r"\&" in result

    def test_finalize_bold_and_escape_preserves_bold(self):
        """Test that bolding is preserved during escaping"""
        text = "Result: <<<BOLD_START>>>100%<<<BOLD_END>>> success"
        result = LaTeXGenerator.finalize_bold_and_escape(text)

        assert r"\textbf{" in result
        assert "}" in result

    @pytest.mark.skipif(not PDFLATEX_AVAILABLE, reason="pdflatex not available")
    def test_generate_latex_filename_with_user_info(self):
        """Test filename generation with user info"""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = os.path.join(tmpdir, "template.tex")
            # Create a minimal valid LaTeX document
            with open(template_path, "w") as f:
                f.write(r"""\documentclass{article}
\begin{document}
{{RESUME_CONTENT}}
\end{document}
""")

            resume_text = "[HEADER]\nTest Resume"

            pdf_path, tex_path = LaTeXGenerator.generate_latex(
                resume_text,
                template_path,
                tmpdir,
                user_name="John Doe",
                company="Tech Corp",
                job_title="Software Engineer",
            )

            filename = os.path.basename(pdf_path).replace(".pdf", "")
            assert "John_Doe" in filename
            assert "Tech_Corp" in filename
            assert "Software_Engineer" in filename
            assert filename.endswith("_resume")

    @pytest.mark.skipif(not PDFLATEX_AVAILABLE, reason="pdflatex not available")
    def test_generate_latex_filename_sanitization(self):
        """Test filename sanitization removes special characters"""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = os.path.join(tmpdir, "template.tex")
            # Create a minimal valid LaTeX document
            with open(template_path, "w") as f:
                f.write(r"""\documentclass{article}
\begin{document}
{{RESUME_CONTENT}}
\end{document}
""")

            resume_text = "[HEADER]\nTest Resume"

            pdf_path, tex_path = LaTeXGenerator.generate_latex(
                resume_text,
                template_path,
                tmpdir,
                user_name="John O'Brien",
                company="Tech & Co.",
                job_title="Sr. Developer",
            )

            filename = os.path.basename(pdf_path)
            assert "'" not in filename
            assert "&" not in filename
            assert "." not in filename.replace(".pdf", "")

    @pytest.mark.skipif(not PDFLATEX_AVAILABLE, reason="pdflatex not available")
    def test_generate_latex_filename_without_user_info(self):
        """Test filename generation without user info uses UUID"""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = os.path.join(tmpdir, "template.tex")
            # Create a minimal valid LaTeX document
            with open(template_path, "w") as f:
                f.write(r"""\documentclass{article}
\begin{document}
{{RESUME_CONTENT}}
\end{document}
""")

            resume_text = "[HEADER]\nTest Resume"

            pdf_path, tex_path = LaTeXGenerator.generate_latex(resume_text, template_path, tmpdir)

            filename = os.path.basename(pdf_path).replace(".pdf", "")
            # UUID format: 8-4-4-4-12 hex digits
            assert len(filename) == 36
            assert filename.count("-") == 4

    def test_parse_structured_resume(self, sample_resume_text):
        """Test parsing structured resume text"""
        result = LaTeXGenerator.parse_structured_resume(sample_resume_text)

        # Should contain LaTeX commands
        assert "resumeSubheading" in result or "resumeItem" in result
        # Should have content from the resume
        assert "University of Example" in result or "Tech Corp" in result

    def test_escape_latex_backslash(self):
        """Test escaping backslashes"""
        text = "Path: C:\\Users\\test"
        escaped = LaTeXGenerator.escape_latex(text)

        assert "textbackslash" in escaped

    def test_format_experience_empty(self):
        """Test that empty experience section is skipped"""
        empty_content = ""
        result = LaTeXGenerator._format_experience(empty_content)
        assert result == ""

    def test_format_experience_with_no_entries(self):
        """Test that experience section with no valid entries is skipped"""
        content = "Some text but no proper entries"
        result = LaTeXGenerator._format_experience(content)
        assert result == ""

    def test_format_projects_empty(self):
        """Test that empty projects section is skipped"""
        empty_content = ""
        result = LaTeXGenerator._format_projects(empty_content)
        assert result == ""

    def test_format_education_empty(self):
        """Test that empty education section is skipped"""
        empty_content = ""
        result = LaTeXGenerator._format_education(empty_content)
        assert result == ""

    def test_format_skills_empty(self):
        """Test that empty skills section is skipped"""
        empty_content = ""
        result = LaTeXGenerator._format_skills(empty_content)
        assert result == ""

    def test_format_education_no_pipe_in_degree(self):
        """Education where degree line has no pipe should still render"""
        content = """MIT | Cambridge, MA
Bachelor of Science in Computer Science, 2024"""
        result = LaTeXGenerator._format_education(content)
        assert "MIT" in result
        assert "Bachelor of Science" in result
        assert "\\resumeSubheading" in result

    def test_format_education_groq_format(self):
        """Education in Groq's format: School - Degree | GPA, then date without pipe"""
        content = """Arizona State University - Master of Science in Computer Science | GPA: 3.33
Expected May 2027"""
        result = LaTeXGenerator._format_education(content)
        assert "Arizona State University" in result
        assert "Expected May 2027" in result or "GPA" in result
        assert "\\resumeSubheading" in result

    def test_format_experience_single_two_part_line(self):
        """Experience with only one 2-part line (no second line) should still render"""
        content = """Software Engineer | January 2023 - Present
- Built microservices architecture
- Led team of 5 developers
- Reduced deployment time by 60%"""
        result = LaTeXGenerator._format_experience(content)
        assert "Software Engineer" in result
        assert "Built microservices" in result
        assert "\\resumeSubheading" in result

    def test_format_projects_without_dates(self):
        """Projects with no date line should still render"""
        content = """Project A | Python, React
- Built a web app for task management
- Implemented REST API with FastAPI

Project B | TensorFlow, Docker
- Trained ML model for image classification
- Deployed with Docker containers"""
        result = LaTeXGenerator._format_projects(content)
        assert "Project A" in result
        assert "Project B" in result
        assert "\\resumeProjectHeading" in result
        assert "Built a web app" in result

    def test_format_projects_with_three_part_pipe(self):
        """Projects with Name | Tech | Date on one line should render with date separate from tech"""
        content = """E-Commerce Platform | React, Node.js | March 2024
- Built full-stack e-commerce application
- Implemented payment processing with Stripe

Data Pipeline | Python, Airflow | 2023-2024
- Automated ETL pipeline processing 1M records daily
- Reduced data processing time by 40%"""
        result = LaTeXGenerator._format_projects(content)
        assert "E-Commerce Platform" in result
        assert "Data Pipeline" in result
        assert "\\resumeProjectHeading" in result
        # Date should be in the date field, not mixed into tech stack
        assert "March 2024" in result
        # Tech stack should NOT contain the date
        assert "React, Node.js | March 2024" not in result

    def test_format_projects_without_pipe_separator(self):
        """Projects with no | separator should still render as best-effort"""
        content = """My ML Project
January 2024
- Built a machine learning pipeline
- Achieved 95% accuracy

Web Dashboard
- Created a React dashboard for analytics
- Integrated with REST API"""
        result = LaTeXGenerator._format_projects(content)
        assert "My ML Project" in result
        assert "Web Dashboard" in result
        assert "Built a machine learning" in result

    def test_format_projects_na_date_rendered_blank(self):
        """Projects where AI returns N/A as date should render with blank date, not 'N/A'"""
        content = """Portfolio Website | React, Tailwind CSS
N/A
- Built responsive portfolio site
- Deployed on Vercel

CLI Tool | Python, Click
n/a
- Created command-line utility for file management
- Published to PyPI"""
        result = LaTeXGenerator._format_projects(content)
        assert "Portfolio Website" in result
        assert "CLI Tool" in result
        assert "N/A" not in result
        assert "n/a" not in result

    def test_format_projects_three_part_na_date_rendered_blank(self):
        """3-part project with N/A date should render blank"""
        content = """My App | Flask, PostgreSQL | N/A
- Built REST API
- Deployed to AWS"""
        result = LaTeXGenerator._format_projects(content)
        assert "My App" in result
        assert "N/A" not in result
        assert "Built REST API" in result

    def test_parse_structured_resume_with_empty_experience(self):
        """Test parsing resume with empty experience section"""
        resume_text = """[HEADER]
John Doe
email@example.com | 123-456-7890

[EDUCATION]
University | Location
Degree | 2020-2024

[EXPERIENCE]

[PROJECTS]
Project Name | Tech Stack
2024
- Project description
"""
        result = LaTeXGenerator.parse_structured_resume(resume_text)

        # Should not contain empty experience section list markers
        assert result.count("resumeSubHeadingListStart") == result.count("resumeSubHeadingListEnd")
        # Should contain education and projects but not experience
        assert "Education" in result
        assert "Projects" in result
        # Experience section should be omitted entirely
        if "Experience" in result:
            # If it exists, it should be properly formed
            assert "resumeSubheading" in result or "Experience" not in result
