import pytest
import os
import tempfile
import subprocess
from services.latex_generator import LaTeXGenerator

# Check if pdflatex is available
def is_pdflatex_available():
    try:
        subprocess.run(['pdflatex', '--version'], capture_output=True, timeout=5, check=True)
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

        assert r'\$' in escaped
        assert r'\%' in escaped
        assert r'\&' in escaped

    def test_escape_latex_special_chars(self):
        """Test escaping special characters"""
        text = "Test_{subscript}^{superscript}#hashtag"
        escaped = LaTeXGenerator.escape_latex(text)

        assert r'\_' in escaped
        assert r'\{' in escaped
        assert r'\}' in escaped
        assert r'\#' in escaped

    def test_bold_metrics_percentages(self):
        """Test bolding percentages"""
        text = "Improved performance by 50% and reduced costs by 25.5%"
        result = LaTeXGenerator.bold_metrics(text)

        assert '<<<BOLD_START>>>50%<<<BOLD_END>>>' in result
        assert '<<<BOLD_START>>>25.5%<<<BOLD_END>>>' in result

    def test_bold_metrics_currency(self):
        """Test bolding currency values"""
        text = "Saved $1,000 and generated $50,000.00 in revenue"
        result = LaTeXGenerator.bold_metrics(text)

        assert '<<<BOLD_START>>>$1,000<<<BOLD_END>>>' in result
        assert '<<<BOLD_START>>>$50,000.00<<<BOLD_END>>>' in result

    def test_bold_metrics_large_numbers(self):
        """Test bolding large numbers with commas"""
        text = "Processed 10,000 requests and handled 1,000,000 users"
        result = LaTeXGenerator.bold_metrics(text)

        assert '<<<BOLD_START>>>10,000<<<BOLD_END>>>' in result
        assert '<<<BOLD_START>>>1,000,000<<<BOLD_END>>>' in result

    def test_bold_metrics_ranges(self):
        """Test bolding number ranges"""
        text = "Managed team of 5-10 people from 2021-2023"
        result = LaTeXGenerator.bold_metrics(text)

        assert '<<<BOLD_START>>>5-10<<<BOLD_END>>>' in result
        assert '<<<BOLD_START>>>2021-2023<<<BOLD_END>>>' in result

    def test_bold_metrics_abbreviated(self):
        """Test bolding abbreviated numbers"""
        text = "Reached 5K users, generated 2.5M in revenue, worth 1B"
        result = LaTeXGenerator.bold_metrics(text)

        assert '<<<BOLD_START>>>5K<<<BOLD_END>>>' in result
        assert '<<<BOLD_START>>>2.5M<<<BOLD_END>>>' in result
        assert '<<<BOLD_START>>>1B<<<BOLD_END>>>' in result

    def test_bold_metrics_multipliers(self):
        """Test bolding multipliers"""
        text = "Achieved 2x growth and 10x increase in efficiency"
        result = LaTeXGenerator.bold_metrics(text)

        assert '<<<BOLD_START>>>2x<<<BOLD_END>>>' in result
        assert '<<<BOLD_START>>>10x<<<BOLD_END>>>' in result

    def test_bold_metrics_years(self):
        """Test bolding years"""
        text = "Started in 2020, graduated in 2023"
        result = LaTeXGenerator.bold_metrics(text)

        assert '<<<BOLD_START>>>2020<<<BOLD_END>>>' in result
        assert '<<<BOLD_START>>>2023<<<BOLD_END>>>' in result

    def test_finalize_bold_and_escape(self):
        """Test combining bolding and escaping"""
        text = "Improved by <<<BOLD_START>>>50%<<<BOLD_END>>> & saved <<<BOLD_START>>>$1,000<<<BOLD_END>>>"
        result = LaTeXGenerator.finalize_bold_and_escape(text)

        assert r'\textbf{50%}' in result or r'\textbf{50\%}' in result
        assert r'\&' in result

    def test_finalize_bold_and_escape_preserves_bold(self):
        """Test that bolding is preserved during escaping"""
        text = "Result: <<<BOLD_START>>>100%<<<BOLD_END>>> success"
        result = LaTeXGenerator.finalize_bold_and_escape(text)

        assert r'\textbf{' in result
        assert '}' in result

    @pytest.mark.skipif(not PDFLATEX_AVAILABLE, reason="pdflatex not available")
    def test_generate_latex_filename_with_user_info(self):
        """Test filename generation with user info"""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = os.path.join(tmpdir, 'template.tex')
            # Create a minimal valid LaTeX document
            with open(template_path, 'w') as f:
                f.write(r'''\documentclass{article}
\begin{document}
{{RESUME_CONTENT}}
\end{document}
''')

            resume_text = "[HEADER]\nTest Resume"

            pdf_path, tex_path = LaTeXGenerator.generate_latex(
                resume_text,
                template_path,
                tmpdir,
                user_name='John Doe',
                company='Tech Corp',
                job_title='Software Engineer'
            )

            filename = os.path.basename(pdf_path).replace('.pdf', '')
            assert 'John_Doe' in filename
            assert 'Tech_Corp' in filename
            assert 'Software_Engineer' in filename
            assert filename.endswith('_resume')

    @pytest.mark.skipif(not PDFLATEX_AVAILABLE, reason="pdflatex not available")
    def test_generate_latex_filename_sanitization(self):
        """Test filename sanitization removes special characters"""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = os.path.join(tmpdir, 'template.tex')
            # Create a minimal valid LaTeX document
            with open(template_path, 'w') as f:
                f.write(r'''\documentclass{article}
\begin{document}
{{RESUME_CONTENT}}
\end{document}
''')

            resume_text = "[HEADER]\nTest Resume"

            pdf_path, tex_path = LaTeXGenerator.generate_latex(
                resume_text,
                template_path,
                tmpdir,
                user_name='John O\'Brien',
                company='Tech & Co.',
                job_title='Sr. Developer'
            )

            filename = os.path.basename(pdf_path)
            assert "'" not in filename
            assert "&" not in filename
            assert "." not in filename.replace('.pdf', '')

    @pytest.mark.skipif(not PDFLATEX_AVAILABLE, reason="pdflatex not available")
    def test_generate_latex_filename_without_user_info(self):
        """Test filename generation without user info uses UUID"""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = os.path.join(tmpdir, 'template.tex')
            # Create a minimal valid LaTeX document
            with open(template_path, 'w') as f:
                f.write(r'''\documentclass{article}
\begin{document}
{{RESUME_CONTENT}}
\end{document}
''')

            resume_text = "[HEADER]\nTest Resume"

            pdf_path, tex_path = LaTeXGenerator.generate_latex(
                resume_text,
                template_path,
                tmpdir
            )

            filename = os.path.basename(pdf_path).replace('.pdf', '')
            # UUID format: 8-4-4-4-12 hex digits
            assert len(filename) == 36
            assert filename.count('-') == 4

    def test_parse_structured_resume(self, sample_resume_text):
        """Test parsing structured resume text"""
        result = LaTeXGenerator.parse_structured_resume(sample_resume_text)

        # Should contain LaTeX commands
        assert 'resumeSubheading' in result or 'resumeItem' in result
        # Should have content from the resume
        assert 'University of Example' in result or 'Tech Corp' in result

    def test_escape_latex_backslash(self):
        """Test escaping backslashes"""
        text = "Path: C:\\Users\\test"
        escaped = LaTeXGenerator.escape_latex(text)

        assert 'textbackslash' in escaped
