"""
Tests for Experience section format detection and handling.

The LaTeX generator now handles THREE different experience formats:
1. NEW (correct from updated prompt): Title | Date, then Company | Location
2. OLD (backwards compatibility): Company | Location, then Title | Date
3. SINGLE LINE (AI sometimes outputs): Title | Company | Location | Date
"""

from services.latex_generator import LaTeXGenerator


class TestExperienceFormatDetection:
    """Test experience section handles multiple input formats correctly."""

    def test_format_1_new_title_first(self):
        """Test Format 1: Title | Date, then Company | Location (NEW correct format)."""
        content = """Senior Data Scientist | October 2023 - April 2025
Firstsource Solutions Ltd. | Bengaluru, India
- Developed predictive models improving accuracy by 25%
- Led team of 5 data scientists
- Reduced processing time by 40%"""

        result = LaTeXGenerator._format_experience(content)

        # Verify correct LaTeX output
        assert '\\section{Experience}' in result
        assert '\\resumeSubheading' in result

        # Verify CORRECT ORDER: Title, Date, Company, Location
        assert '{Senior Data Scientist}{October 2023 - April 2025}' in result
        assert '{Firstsource Solutions Ltd.}{Bengaluru, India}' in result

        # Verify bullets preserved
        assert '\\resumeItem{Developed predictive models improving accuracy by \\textbf{25\\%}}' in result
        assert '\\resumeItem{Led team of 5 data scientists}' in result  # 5 is too small to bold
        assert '\\resumeItem{Reduced processing time by \\textbf{40\\%}}' in result

    def test_format_2_old_company_first(self):
        """Test Format 2: Company | Location, then Title | Date (OLD backwards format)."""
        content = """Firstsource Solutions Ltd. | Bengaluru, India
Senior Data Scientist | October 2023 - April 2025
- Developed predictive models improving accuracy by 25%
- Led team of 5 data scientists
- Reduced processing time by 40%"""

        result = LaTeXGenerator._format_experience(content)

        # Verify correct LaTeX output
        assert '\\section{Experience}' in result
        assert '\\resumeSubheading' in result

        # Verify STILL produces CORRECT ORDER: Title, Date, Company, Location
        # Even though input was backwards, output should be correct
        assert '{Senior Data Scientist}{October 2023 - April 2025}' in result
        assert '{Firstsource Solutions Ltd.}{Bengaluru, India}' in result

        # Verify bullets preserved
        assert '\\resumeItem{Developed predictive models improving accuracy by \\textbf{25\\%}}' in result

    def test_format_3_single_line(self):
        """Test Format 3: Title | Company | Location | Date (single line)."""
        content = """Senior Data Scientist | Firstsource Solutions Ltd. | Bengaluru, India | October 2023 - April 2025
- Developed predictive models improving accuracy by 25%
- Led team of 5 data scientists
- Reduced processing time by 40%"""

        result = LaTeXGenerator._format_experience(content)

        # Verify correct LaTeX output
        assert '\\section{Experience}' in result
        assert '\\resumeSubheading' in result

        # Verify CORRECT ORDER: Title, Date, Company, Location
        assert '{Senior Data Scientist}{October 2023 - April 2025}' in result
        assert '{Firstsource Solutions Ltd.}{Bengaluru, India}' in result

        # Verify bullets preserved
        assert '\\resumeItem{Developed predictive models improving accuracy by \\textbf{25\\%}}' in result

    def test_multiple_jobs_format_1(self):
        """Test multiple jobs with Format 1 (new correct format)."""
        content = """Senior Data Scientist | October 2023 - April 2025
Firstsource Solutions Ltd. | Bengaluru, India
- Developed predictive models improving accuracy by 25%
- Led team of 5 data scientists

Data Scientist | January 2021 - September 2023
Tech Company Inc. | San Francisco, CA
- Built ML pipelines processing 1M records/day
- Improved model performance by 30%"""

        result = LaTeXGenerator._format_experience(content)

        # Verify both jobs present
        assert '{Senior Data Scientist}{October 2023 - April 2025}' in result
        assert '{Firstsource Solutions Ltd.}{Bengaluru, India}' in result
        assert '{Data Scientist}{January 2021 - September 2023}' in result
        assert '{Tech Company Inc.}{San Francisco, CA}' in result

        # Verify both sets of bullets
        assert 'improving accuracy by \\textbf{25\\%}' in result
        assert 'processing \\textbf{1M} records/day' in result

    def test_multiple_jobs_format_2(self):
        """Test multiple jobs with Format 2 (old backwards format)."""
        content = """Firstsource Solutions Ltd. | Bengaluru, India
Senior Data Scientist | October 2023 - April 2025
- Developed predictive models improving accuracy by 25%
- Led team of 5 data scientists

Tech Company Inc. | San Francisco, CA
Data Scientist | January 2021 - September 2023
- Built ML pipelines processing 1M records/day
- Improved model performance by 30%"""

        result = LaTeXGenerator._format_experience(content)

        # Verify both jobs present in CORRECT order
        assert '{Senior Data Scientist}{October 2023 - April 2025}' in result
        assert '{Firstsource Solutions Ltd.}{Bengaluru, India}' in result
        assert '{Data Scientist}{January 2021 - September 2023}' in result
        assert '{Tech Company Inc.}{San Francisco, CA}' in result

    def test_mixed_formats(self):
        """Test handling of mixed format types (shouldn't happen but be resilient)."""
        content = """Senior Data Scientist | October 2023 - April 2025
Firstsource Solutions Ltd. | Bengaluru, India
- Led ML initiatives

Data Scientist | Tech Company Inc. | San Francisco, CA | January 2021 - September 2023
- Built pipelines"""

        result = LaTeXGenerator._format_experience(content)

        # Verify both jobs processed correctly
        assert '{Senior Data Scientist}{October 2023 - April 2025}' in result
        assert '{Data Scientist}{January 2021 - September 2023}' in result
        assert '{Firstsource Solutions Ltd.}{Bengaluru, India}' in result
        assert '{Tech Company Inc.}{San Francisco, CA}' in result

    def test_format_detection_with_month_names(self):
        """Test format detection correctly identifies dates with month names."""
        content = """Senior Data Scientist | Jan 2023 - Present
Firstsource Solutions Ltd. | Bengaluru, India
- Developed models"""

        result = LaTeXGenerator._format_experience(content)

        # Verify detected as Format 1 (title first) because "Jan 2023" looks like a date
        assert '{Senior Data Scientist}{Jan 2023 - Present}' in result
        assert '{Firstsource Solutions Ltd.}{Bengaluru, India}' in result

    def test_format_detection_with_year_only(self):
        """Test format detection with year-only dates."""
        content = """Senior Data Scientist | 2023 - 2025
Firstsource Solutions Ltd. | Bengaluru, India
- Developed models"""

        result = LaTeXGenerator._format_experience(content)

        # Verify detected as Format 1 because "2023 - 2025" contains years
        assert '{Senior Data Scientist}{2023 - 2025}' in result
        assert '{Firstsource Solutions Ltd.}{Bengaluru, India}' in result

    def test_format_detection_with_current(self):
        """Test format detection with 'Current' keyword."""
        content = """Senior Data Scientist | October 2023 - Current
Firstsource Solutions Ltd. | Bengaluru, India
- Leading ML team"""

        result = LaTeXGenerator._format_experience(content)

        # Verify detected as Format 1 because "Current" is a date indicator
        assert '{Senior Data Scientist}{October 2023 - Current}' in result
        assert '{Firstsource Solutions Ltd.}{Bengaluru, India}' in result

    def test_backwards_compatibility_no_date_indicators(self):
        """Test that Format 2 (old) still works when line has no obvious date indicators."""
        # This might be rare, but if first line has no year/month and is Company | Location
        # it should still work as Format 2
        content = """ABC Corp | New York
Engineer | 2020 - 2023
- Built systems"""

        result = LaTeXGenerator._format_experience(content)

        # Should detect as Format 2 (company first) and still output correctly
        assert '{Engineer}{2020 - 2023}' in result
        assert '{ABC Corp}{New York}' in result
