import os
import re
import uuid

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from utils.logger import app_logger


class LaTeXGenerator:
    @staticmethod
    def escape_latex(text: str) -> str:
        """Escape special LaTeX characters using regex for proper ordering"""
        # Escape backslash first, then others
        # Use a placeholder to avoid double-escaping
        text = text.replace("\\", "<<<BACKSLASH>>>")

        # Escape other special characters
        replacements = {
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
            "~": r"\textasciitilde{}",
            "^": r"\^{}",
        }

        for char, escape in replacements.items():
            text = text.replace(char, escape)

        # Replace backslash placeholder last
        text = text.replace("<<<BACKSLASH>>>", r"\textbackslash{}")

        return text

    @staticmethod
    def bold_metrics(text: str) -> str:
        """Bold numbers and metrics in text using \\textbf{}, then escape LaTeX"""
        # Pattern to match various numeric formats
        # Order matters: more specific patterns first to avoid conflicts

        result = text

        # Apply patterns one by one to avoid overlapping matches
        patterns = [
            # Percentages: 50%, 12.5%
            (r"(\d+(?:\.\d+)?%)", r"<<<BOLD_START>>>\1<<<BOLD_END>>>"),
            # Currency with abbreviations: $2.5M, $1.2B, $500K (MUST come before plain currency)
            (r"(\$\d+(?:\.\d+)?[KMB])\b", r"<<<BOLD_START>>>\1<<<BOLD_END>>>"),
            # Currency with commas or decimals: $1,000, $50.00, $1,234,567, $2.50
            # But NOT if already inside bold markers or followed by K/M/B
            (
                r"(?<!START>>>)(\$\d{1,3}(?:,\d{3})*(?:\.\d+)?)(?![KMB])(?!<<<BOLD_END>>>)",
                r"<<<BOLD_START>>>\1<<<BOLD_END>>>",
            ),
            # Large numbers with commas (not currency, not already bolded): 1,000, 10,000
            (
                r"(?<!\$)(?<!START>>>)(\d{1,3}(?:,\d{3})+)(?![\d.])(?!<<<BOLD_END>>>)",
                r"<<<BOLD_START>>>\1<<<BOLD_END>>>",
            ),
            # Abbreviated numbers: 5K, 2.5M, 1.2B (but not if part of currency or already bolded)
            (
                r"(?<!\$)(?<!START>>>)\b(\d+(?:\.\d+)?[KMB])\b(?!<<<BOLD_END>>>)",
                r"<<<BOLD_START>>>\1<<<BOLD_END>>>",
            ),
            # Number + word: "5 million", "2.5 billion"
            (
                r"(?<!START>>>)\b(\d+(?:\.\d+)?)\s*(million|billion|thousand)(?!<<<BOLD_END>>>)",
                r"<<<BOLD_START>>>\1<<<BOLD_END>>> \2",
            ),
            # Multipliers: 2x, 10x
            (r"(?<!START>>>)(\d+x)(?!<<<BOLD_END>>>)", r"<<<BOLD_START>>>\1<<<BOLD_END>>>"),
            # Ranges (but NOT dates like 2021-2023, so only for small numbers)
            # Only match ranges like 10-20, 5-8, not 2021-2023
            (
                r"(?<!START>>>)\b([1-9]\d{0,2}-[1-9]\d{0,2})\b(?!<<<BOLD_END>>>)",
                r"<<<BOLD_START>>>\1<<<BOLD_END>>>",
            ),
            # Note: Years in dates (like "Oct 2025", "in 2023") should NOT be bolded
            # Removed standalone year pattern to avoid bolding years in dates
        ]

        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

        return result

    @staticmethod
    def finalize_bold_and_escape(text: str) -> str:
        """Escape LaTeX special characters while preserving bold placeholders, then convert to textbf"""
        # Extract bolded content temporarily
        bold_contents = []

        def save_bold(match):
            bold_contents.append(match.group(1))
            return f"<<<BOLDPLACEHOLDER{len(bold_contents) - 1}>>>"

        text = re.sub(r"<<<BOLD_START>>>(.*?)<<<BOLD_END>>>", save_bold, text)

        # Escape the rest of the text
        text = LaTeXGenerator.escape_latex(text)

        # Restore bolded content with textbf
        for i, content in enumerate(bold_contents):
            escaped_content = LaTeXGenerator.escape_latex(content)
            text = text.replace(f"<<<BOLDPLACEHOLDER{i}>>>", f"\\textbf{{{escaped_content}}}")

        return text

    @staticmethod
    def _sanitize_date(date_str: str) -> str:
        """Return empty string for placeholder dates like N/A, None, etc."""
        if date_str.strip().lower() in ("n/a", "na", "none", "null", "tbd", "-", "—"):
            return ""
        return date_str

    @staticmethod
    def _normalize_section_headers(resume_text: str) -> str:
        """
        Normalize section headers by adding square brackets if missing.
        Some AI providers (especially Gemini) sometimes return headers without brackets.

        Args:
            resume_text: Resume text that may have malformed section headers

        Returns:
            Resume text with normalized section headers
        """
        common_sections = [
            "HEADER",
            "EDUCATION",
            "EXPERIENCE",
            "TECHNICAL SKILLS",
            "SKILLS",
            "PROJECTS",
            "CERTIFICATIONS",
            "PUBLICATIONS",
            "AWARDS",
        ]

        lines = resume_text.split("\n")
        normalized_lines = []
        max_blank_lines_to_skip = 3

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Check if line matches a common section name (case-insensitive, no brackets)
            # and is likely a header (short line, all caps or title case, followed by content)
            for section in common_sections:
                # Match exact section name without brackets
                if stripped.upper() == section and not stripped.startswith("["):
                    # Verify this looks like a header by checking for non-empty content
                    # within the next few lines (skip over blank lines)
                    has_content_following = False
                    for j in range(1, min(max_blank_lines_to_skip + 1, len(lines) - i)):
                        if lines[i + j].strip():
                            has_content_following = True
                            break

                    if has_content_following:
                        app_logger.info(
                            f"Normalizing section header: '{stripped}' -> '[{section}]'"
                        )
                        normalized_lines.append(f"[{section}]")
                        break
            else:
                # No section match, keep original line
                normalized_lines.append(line)

        return "\n".join(normalized_lines)

    @staticmethod
    def parse_structured_resume(resume_text: str) -> str:
        """
        Parse structured resume text and convert to LaTeX format.

        Args:
            resume_text: Structured resume text from AI

        Returns:
            LaTeX formatted resume content
        """
        app_logger.debug(f"Raw resume text to parse (first 500 chars): {resume_text[:500]}")

        # Normalize section headers (add brackets if missing)
        resume_text = LaTeXGenerator._normalize_section_headers(resume_text)

        # Split into sections (handle sections at start of string or after newline)
        # Updated regex to handle multi-word sections like "TECHNICAL SKILLS"
        sections = re.split(r"(?:^|\n)\[([A-Z\s]+)\]\n", resume_text, flags=re.MULTILINE)

        # Parse all sections into a dictionary
        section_dict = {}
        current_section = None
        for i, part in enumerate(sections):
            if i == 0:
                continue

            if i % 2 == 1:
                current_section = part.strip()  # Strip whitespace from section name
            else:
                content = part.strip()
                section_dict[current_section] = content

        # Enforce fixed section order: HEADER -> EDUCATION -> TECHNICAL SKILLS -> EXPERIENCE -> PROJECTS
        # This ensures consistent ordering regardless of AI output
        ordered_sections = [
            ("HEADER", LaTeXGenerator._format_header),
            ("EDUCATION", LaTeXGenerator._format_education),
            ("TECHNICAL SKILLS", LaTeXGenerator._format_skills),
            ("SKILLS", LaTeXGenerator._format_skills),  # Fallback for SKILLS
            ("EXPERIENCE", LaTeXGenerator._format_experience),
            ("PROJECTS", LaTeXGenerator._format_projects),
        ]

        # Log what sections we received for debugging
        app_logger.info(f"Received sections from AI: {list(section_dict.keys())}")

        latex_parts = []
        skills_added = False  # Track if we've already added skills section
        for section_name, format_func in ordered_sections:
            if section_name in section_dict:
                content = section_dict[section_name]
                section_latex = format_func(content)

                # Only add non-empty sections
                if section_latex:
                    # Skip SKILLS if we already added TECHNICAL SKILLS (or vice versa)
                    if section_name in ["SKILLS", "TECHNICAL SKILLS"]:
                        if skills_added:
                            app_logger.info(f"Skipping duplicate skills section: {section_name}")
                            continue
                        skills_added = True

                    latex_parts.append(section_latex)
                    app_logger.info(f"Added section: {section_name}")

        return "\n\n".join(latex_parts)

    @staticmethod
    def _format_header(content: str) -> str:
        """Format header section"""
        lines = [line.strip() for line in content.split("\n") if line.strip()]

        # Handle edge cases: missing or incomplete header
        if len(lines) == 0:
            # No header content at all - skip it
            return ""

        if len(lines) == 1:
            # Only name provided
            name = LaTeXGenerator.escape_latex(lines[0])
            return f"\\begin{{center}}\n    \\textbf{{\\Huge \\scshape {name}}}\n\\end{{center}}"

        # Full header with name and contact info
        name = LaTeXGenerator.escape_latex(lines[0])
        contact_info = lines[1]

        # Don't escape contact info yet - process it first
        # Split contact info by |
        contact_parts = [part.strip() for part in contact_info.split("|")]

        # Format with href for email and links
        formatted_parts = []
        for part in contact_parts:
            # Escape the part first
            part_escaped = LaTeXGenerator.escape_latex(part)

            # Check original (unescaped) for special handling
            if "@" in part and "redacted" not in part.lower():
                # Real email - make it a hyperlink
                formatted_parts.append(f"\\href{{mailto:{part}}}{{\\textcolor{{customblue}}{{{part_escaped}}}}}")
            elif (
                "linkedin.com" in part.lower() or "github.com" in part.lower()
            ) and "redacted" not in part.lower():
                # Real link - make it a hyperlink
                formatted_parts.append(f"\\href{{{part}}}{{\\textcolor{{customblue}}{{{part_escaped}}}}}")
            else:
                # Plain text (including REDACTED values)
                formatted_parts.append(part_escaped)

        contact_line = " $|$ ".join(formatted_parts)

        return f"\\begin{{center}}\n    \\textbf{{\\Huge \\scshape {name}}} \\\\ \\vspace{{1pt}}\n    \\small {contact_line}\n\\end{{center}}"

    @staticmethod
    def _format_education(content: str) -> str:
        """Format education section - skip if empty"""
        lines = [
            line.strip()
            for line in content.split("\n")
            if line.strip() and not line.startswith("(")
        ]

        # Check if there's any actual content (look for school entries with |)
        has_content = False
        for line in lines:
            if "|" in line:
                has_content = True
                break

        # Skip the entire section if empty
        if not has_content:
            return ""

        header = "\\section{Education}\n  \\resumeSubHeadingListStart\n"
        entries = ""

        i = 0
        while i < len(lines):
            if "|" in lines[i]:
                parts = [p.strip() for p in lines[i].split("|")]
                if len(parts) == 2:
                    school, location = parts
                    if i + 1 < len(lines) and "|" in lines[i + 1]:
                        degree_parts = [p.strip() for p in lines[i + 1].split("|")]
                        if len(degree_parts) == 2:
                            degree, date = degree_parts
                            school_esc = LaTeXGenerator.escape_latex(school)
                            location_esc = LaTeXGenerator.escape_latex(location)
                            degree_esc = LaTeXGenerator.escape_latex(degree)
                            date_esc = LaTeXGenerator.escape_latex(date)
                            entries += f" \\resumeSubheading\n      {{{school_esc}}}{{{location_esc}}}\n      {{{degree_esc}}} {{{date_esc}}}\n"
                            i += 2
                            continue
                    elif i + 1 < len(lines) and not lines[i + 1].startswith("-"):
                        # Second line has no pipe - treat as combined degree/date
                        degree_line = lines[i + 1].strip()
                        school_esc = LaTeXGenerator.escape_latex(school)
                        location_esc = LaTeXGenerator.escape_latex(location)
                        degree_esc = LaTeXGenerator.escape_latex(degree_line)
                        entries += f" \\resumeSubheading\n      {{{school_esc}}}{{{location_esc}}}\n      {{{degree_esc}}} {{}}\n"
                        i += 2
                        continue
            i += 1

        if not entries:
            return ""

        return header + entries + "  \\resumeSubHeadingListEnd"

    @staticmethod
    def _format_experience(content: str) -> str:
        """Format experience section - skip if empty

        Handles three formats:
        Format 1 (NEW - correct order from prompt):
            Job Title | Start Date - End Date
            Company Name | Location
            - Bullet points

        Format 2 (OLD - backwards compatibility):
            Company Name | Location
            Job Title | Start Date - End Date
            - Bullet points

        Format 3 (AI sometimes returns single line):
            Job Title | Company Name | Location | Date
            - Bullet points
        """
        lines = [
            line.strip()
            for line in content.split("\n")
            if line.strip() and not line.startswith("(")
        ]

        # Check if there's any actual content (look for company entries with |)
        has_content = False
        for line in lines:
            if "|" in line and not line.startswith("-"):
                has_content = True
                break

        # Skip the entire section if empty
        if not has_content:
            app_logger.info("Experience section is empty, skipping")
            return ""

        header = "\\section{Experience}\n  \\resumeSubHeadingListStart\n"
        entries = ""

        i = 0
        while i < len(lines):
            if "|" in lines[i] and not lines[i].startswith("-"):
                parts = [p.strip() for p in lines[i].split("|")]

                # Format 3: Single line with 4 parts (Title | Company | Location | Date)
                if len(parts) == 4:
                    title, company, location, date = parts

                    title_esc = LaTeXGenerator.escape_latex(title)
                    date_esc = LaTeXGenerator.escape_latex(date)
                    company_esc = LaTeXGenerator.escape_latex(company)
                    location_esc = LaTeXGenerator.escape_latex(location)

                    # Correct order: Title, Date, Company, Location
                    entries += f"\n    \\resumeSubheading\n      {{{title_esc}}}{{{date_esc}}}\n      {{{company_esc}}}{{{location_esc}}}\n"
                    entries += "      \\resumeItemListStart\n"

                    i += 1
                    while i < len(lines) and lines[i].startswith("-"):
                        bullet = lines[i][1:].strip()
                        bullet_bold = LaTeXGenerator.bold_metrics(bullet)
                        bullet_esc = LaTeXGenerator.finalize_bold_and_escape(bullet_bold)
                        entries += f"        \\resumeItem{{{bullet_esc}}}\n"
                        i += 1

                    entries += "      \\resumeItemListEnd\n"
                    continue

                # Format 3b: Single line with 3 parts (Title | Company | Date)
                elif len(parts) == 3:
                    date_pattern = (
                        r"\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Present|Current)"
                    )
                    if re.search(date_pattern, parts[2], re.IGNORECASE):
                        title, company, date = parts
                        location = ""
                    else:
                        title, company, location = parts
                        date = ""

                    title_esc = LaTeXGenerator.escape_latex(title)
                    date_esc = LaTeXGenerator.escape_latex(date)
                    company_esc = LaTeXGenerator.escape_latex(company)
                    location_esc = LaTeXGenerator.escape_latex(location)

                    entries += f"\n    \\resumeSubheading\n      {{{title_esc}}}{{{date_esc}}}\n      {{{company_esc}}}{{{location_esc}}}\n"
                    entries += "      \\resumeItemListStart\n"

                    i += 1
                    while i < len(lines) and lines[i].startswith("-"):
                        bullet = lines[i][1:].strip()
                        bullet_bold = LaTeXGenerator.bold_metrics(bullet)
                        bullet_esc = LaTeXGenerator.finalize_bold_and_escape(bullet_bold)
                        entries += f"        \\resumeItem{{{bullet_esc}}}\n"
                        i += 1

                    entries += "      \\resumeItemListEnd\n"
                    continue

                # Format 1 or 2: Two lines, need to detect which order
                elif len(parts) == 2:
                    first_part1, first_part2 = parts

                    if (
                        i + 1 < len(lines)
                        and "|" in lines[i + 1]
                        and not lines[i + 1].startswith("-")
                    ):
                        second_parts = [p.strip() for p in lines[i + 1].split("|")]
                        if len(second_parts) == 2:
                            second_part1, second_part2 = second_parts

                            # Detect format: check if first line looks like a date (contains year or month-year pattern)
                            # If first line second part contains digits suggesting a year/date, it's Title | Date (Format 1)
                            # Otherwise it's Company | Location (Format 2)
                            date_pattern = r"\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Present|Current)"

                            if re.search(date_pattern, first_part2, re.IGNORECASE):
                                # Format 1: Title | Date, then Company | Location
                                title = first_part1
                                date = first_part2
                                company = second_part1
                                location = second_part2
                            else:
                                # Format 2: Company | Location, then Title | Date
                                company = first_part1
                                location = first_part2
                                title = second_part1
                                date = second_part2

                            title_esc = LaTeXGenerator.escape_latex(title)
                            date_esc = LaTeXGenerator.escape_latex(date)
                            company_esc = LaTeXGenerator.escape_latex(company)
                            location_esc = LaTeXGenerator.escape_latex(location)

                            # Correct order: Title, Date, Company, Location
                            entries += f"\n    \\resumeSubheading\n      {{{title_esc}}}{{{date_esc}}}\n      {{{company_esc}}}{{{location_esc}}}\n"
                            entries += "      \\resumeItemListStart\n"

                            i += 2
                            while i < len(lines) and lines[i].startswith("-"):
                                bullet = lines[i][1:].strip()
                                bullet_bold = LaTeXGenerator.bold_metrics(bullet)
                                bullet_esc = LaTeXGenerator.finalize_bold_and_escape(bullet_bold)
                                entries += f"        \\resumeItem{{{bullet_esc}}}\n"
                                i += 1

                            entries += "      \\resumeItemListEnd\n"
                            continue
                    else:
                        # Single 2-part line: no second | line follows
                        date_pattern = r"\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Present|Current)"
                        if re.search(date_pattern, first_part2, re.IGNORECASE):
                            title, date = first_part1, first_part2
                            company, location = "", ""
                        else:
                            title, date = first_part1, ""
                            company, location = "", first_part2

                        title_esc = LaTeXGenerator.escape_latex(title)
                        date_esc = LaTeXGenerator.escape_latex(date)
                        company_esc = LaTeXGenerator.escape_latex(company)
                        location_esc = LaTeXGenerator.escape_latex(location)

                        entries += f"\n    \\resumeSubheading\n      {{{title_esc}}}{{{date_esc}}}\n      {{{company_esc}}}{{{location_esc}}}\n"
                        entries += "      \\resumeItemListStart\n"

                        i += 1
                        while i < len(lines) and lines[i].startswith("-"):
                            bullet = lines[i][1:].strip()
                            bullet_bold = LaTeXGenerator.bold_metrics(bullet)
                            bullet_esc = LaTeXGenerator.finalize_bold_and_escape(bullet_bold)
                            entries += f"        \\resumeItem{{{bullet_esc}}}\n"
                            i += 1

                        entries += "      \\resumeItemListEnd\n"
                        continue
            i += 1

        if not entries:
            app_logger.warning(
                "Experience section had content lines but no entries matched expected formats"
            )
            return ""

        return header + entries + "  \\resumeSubHeadingListEnd"

    @staticmethod
    def _format_skills(content: str) -> str:
        """Format skills section - skip if empty"""
        lines = [line.strip() for line in content.split("\n") if line.strip() and ":" in line]

        # Skip the entire section if empty
        if not lines:
            return ""

        # Use regular string concatenation to avoid f-string brace issues
        latex = "\\section{Technical Skills}\n \\begin{itemize}[leftmargin=0.15in, label={}]\n    \\small{\\item{\n"

        for line in lines:
            if ":" in line:
                parts = line.split(":", 1)
                category = parts[0].strip()
                skills = parts[1].strip()

                category_esc = LaTeXGenerator.escape_latex(category)
                skills_esc = LaTeXGenerator.escape_latex(skills)

                latex += f"    \\textbf{{{category_esc}}}{{: {skills_esc}}} \\\\\n"

        latex += "    }}\n \\end{itemize}"
        return latex

    @staticmethod
    def _format_projects(content: str) -> str:
        """Format projects section - skip if empty"""
        lines = [
            line.strip()
            for line in content.split("\n")
            if line.strip() and not line.startswith("(")
        ]

        # Check if there's any actual content
        has_content = False
        for idx, line in enumerate(lines):
            if "|" in line and not line.startswith("-"):
                has_content = True
                break
            if (
                not line.startswith("-")
                and idx + 1 < len(lines)
                and any(ln.startswith("-") for ln in lines[idx + 1 : idx + 5])
            ):
                has_content = True
                break

        # Skip the entire section if empty
        if not has_content:
            return ""

        header = "\\section{Projects}\n    \\resumeSubHeadingListStart\n"
        entries = ""

        i = 0
        while i < len(lines):
            if "|" in lines[i] and not lines[i].startswith("-"):
                parts = [p.strip() for p in lines[i].split("|")]
                if len(parts) >= 2:
                    project_name = parts[0]

                    # 3-part: Name | Tech | Date (detect date-like or placeholder last part)
                    date_from_line = ""
                    if len(parts) == 3 and re.search(
                        r"\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Present|Current)|^(?:N/?A|NA|None|TBD)$",
                        parts[2].strip(),
                        re.IGNORECASE,
                    ):
                        tech_stack = parts[1]
                        date_from_line = LaTeXGenerator._sanitize_date(parts[2])
                    else:
                        tech_stack = " | ".join(parts[1:])

                    project_esc = LaTeXGenerator.escape_latex(project_name)
                    tech_esc = LaTeXGenerator.escape_latex(tech_stack)

                    # Determine date: from 3-part split, next line, or empty
                    if date_from_line:
                        date_esc = LaTeXGenerator.escape_latex(date_from_line)
                        entries += f"    \\resumeProjectHeading\n          {{\\textbf{{{project_esc}}} $|$ \\emph{{{tech_esc}}}}}{{{date_esc}}}\n"
                        i += 1
                    elif (
                        i + 1 < len(lines)
                        and not lines[i + 1].startswith("-")
                        and "|" not in lines[i + 1]
                    ):
                        date_range = LaTeXGenerator._sanitize_date(lines[i + 1].strip())
                        date_esc = LaTeXGenerator.escape_latex(date_range)
                        entries += f"    \\resumeProjectHeading\n          {{\\textbf{{{project_esc}}} $|$ \\emph{{{tech_esc}}}}}{{{date_esc}}}\n"
                        i += 2
                    else:
                        entries += f"    \\resumeProjectHeading\n          {{\\textbf{{{project_esc}}} $|$ \\emph{{{tech_esc}}}}}{{}}\n"
                        i += 1

                    entries += "          \\resumeItemListStart\n"
                    while i < len(lines) and lines[i].startswith("-"):
                        bullet = lines[i][1:].strip()
                        bullet_bold = LaTeXGenerator.bold_metrics(bullet)
                        bullet_esc = LaTeXGenerator.finalize_bold_and_escape(bullet_bold)
                        entries += f"            \\resumeItem{{{bullet_esc}}}\n"
                        i += 1
                    entries += "          \\resumeItemListEnd\n"
                    continue
            i += 1

        if not entries:
            # Fallback: treat non-bullet lines followed by bullets as project entries
            i = 0
            while i < len(lines):
                if not lines[i].startswith("-"):
                    project_name = lines[i]
                    date_range = ""
                    i += 1

                    if i < len(lines) and not lines[i].startswith("-") and "|" not in lines[i]:
                        date_range = LaTeXGenerator._sanitize_date(lines[i])
                        i += 1

                    bullets = []
                    while i < len(lines) and lines[i].startswith("-"):
                        bullets.append(lines[i][1:].strip())
                        i += 1

                    if bullets:
                        project_esc = LaTeXGenerator.escape_latex(project_name)
                        date_esc = LaTeXGenerator.escape_latex(date_range)
                        entries += f"    \\resumeProjectHeading\n          {{\\textbf{{{project_esc}}} $|$ \\emph{{}}}}{{{date_esc}}}\n"
                        entries += "          \\resumeItemListStart\n"
                        for bullet in bullets:
                            bullet_bold = LaTeXGenerator.bold_metrics(bullet)
                            bullet_esc = LaTeXGenerator.finalize_bold_and_escape(bullet_bold)
                            entries += f"            \\resumeItem{{{bullet_esc}}}\n"
                        entries += "          \\resumeItemListEnd\n"
                    continue
                i += 1

        if not entries:
            app_logger.warning(
                "Projects section had content lines but no entries matched expected formats"
            )
            return ""

        return header + entries + "    \\resumeSubHeadingListEnd"

    @staticmethod
    def parse_resume_sections(resume_text: str) -> dict:
        """Parse resume text into sections"""
        lines = resume_text.split("\n")
        sections = {}
        current_section = "header"
        current_content = []

        common_headers = [
            "experience",
            "education",
            "skills",
            "summary",
            "projects",
            "certifications",
        ]

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if line is a section header
            is_header = False
            for header in common_headers:
                if header in line.lower() and len(line) < 50:
                    if current_content:
                        sections[current_section] = current_content
                    current_section = header.lower()
                    current_content = []
                    is_header = True
                    break

            if not is_header:
                current_content.append(line)

        # Add last section
        if current_content:
            sections[current_section] = current_content

        return sections

    @staticmethod
    def _xml_escape(text: str) -> str:
        """Escape XML special characters for reportlab Paragraph markup."""
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        return text

    @staticmethod
    def _finalize_bold_for_pdf(text: str) -> str:
        """
        Convert bold placeholders to reportlab XML markup.
        Applies XML escaping to surrounding text while wrapping metrics in <b> tags.
        """
        parts = re.split(r"<<<BOLD_START>>>(.*?)<<<BOLD_END>>>", text)
        result = []
        for i, part in enumerate(parts):
            if i % 2 == 0:
                # Regular text — XML-escape it
                result.append(LaTeXGenerator._xml_escape(part))
            else:
                # Bold content — XML-escape the content inside <b>
                result.append(f"<b>{LaTeXGenerator._xml_escape(part)}</b>")
        return "".join(result)

    @staticmethod
    def _generate_pdf_with_reportlab(resume_text: str, pdf_path: str) -> None:
        """
        Generate a PDF resume from structured resume text using reportlab.
        Parses sections in fixed order: HEADER, EDUCATION, TECHNICAL SKILLS/SKILLS,
        EXPERIENCE, PROJECTS.
        """
        margin = 0.5 * inch
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            leftMargin=margin,
            rightMargin=margin,
            topMargin=margin,
            bottomMargin=margin,
        )
        content_width = letter[0] - 2 * margin

        # Define paragraph styles
        name_style = ParagraphStyle(
            "Name",
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            spaceAfter=4,
        )
        contact_style = ParagraphStyle(
            "Contact",
            fontName="Helvetica",
            fontSize=7.5,
            leading=10,
            alignment=TA_CENTER,
            spaceAfter=8,
            wordWrap="LTR",
        )
        section_header_style = ParagraphStyle(
            "SectionHeader",
            fontName="Helvetica-Bold",
            fontSize=11,
            alignment=TA_LEFT,
            spaceBefore=8,
            spaceAfter=2,
            textTransform="uppercase",
        )
        subheading_left_style = ParagraphStyle(
            "SubheadingLeft",
            fontName="Helvetica-Bold",
            fontSize=10,
            alignment=TA_LEFT,
        )
        subheading_right_style = ParagraphStyle(
            "SubheadingRight",
            fontName="Helvetica",
            fontSize=10,
            alignment=TA_RIGHT,
        )
        subheading_left_plain_style = ParagraphStyle(
            "SubheadingLeftPlain",
            fontName="Helvetica-Oblique",
            fontSize=9,
            alignment=TA_LEFT,
        )
        bullet_style = ParagraphStyle(
            "Bullet",
            fontName="Helvetica",
            fontSize=9,
            leftIndent=16,
            firstLineIndent=0,
            spaceAfter=1,
            bulletText="\u2022",
            bulletIndent=6,
            bulletFontName="Helvetica",
            bulletFontSize=9,
        )
        skills_style = ParagraphStyle(
            "Skills",
            fontName="Helvetica",
            fontSize=9,
            alignment=TA_LEFT,
            spaceAfter=2,
        )

        # Parse sections from structured text
        normalized = LaTeXGenerator._normalize_section_headers(resume_text)
        raw_sections = re.split(r"(?:^|\n)\[([A-Z\s]+)\]\n", normalized, flags=re.MULTILINE)

        section_dict = {}
        current_section = None
        for i, part in enumerate(raw_sections):
            if i == 0:
                continue
            if i % 2 == 1:
                current_section = part.strip()
            else:
                section_dict[current_section] = part.strip()

        ordered_sections = [
            "HEADER",
            "EDUCATION",
            "TECHNICAL SKILLS",
            "SKILLS",
            "EXPERIENCE",
            "PROJECTS",
        ]

        story = []
        skills_added = False

        for section_name in ordered_sections:
            if section_name not in section_dict:
                continue

            content = section_dict[section_name]
            lines = [ln.strip() for ln in content.split("\n") if ln.strip()]

            if section_name == "HEADER":
                if not lines:
                    continue
                # Name
                name = LaTeXGenerator._xml_escape(lines[0])
                story.append(Paragraph(f"<b>{name}</b>", name_style))

                if len(lines) >= 2:
                    # Contact line — pipe-separated
                    contact_parts = [p.strip() for p in lines[1].split("|")]
                    formatted_parts = []
                    for part in contact_parts:
                        part_esc = LaTeXGenerator._xml_escape(part)
                        if "@" in part and "redacted" not in part.lower():
                            formatted_parts.append(
                                f'<a href="mailto:{part_esc}">'
                                f'<font color="#004f90">{part_esc}</font></a>'
                            )
                        elif (
                            "linkedin.com" in part.lower() or "github.com" in part.lower()
                        ) and "redacted" not in part.lower():
                            formatted_parts.append(
                                f'<a href="{part_esc}">'
                                f'<font color="#004f90">{part_esc}</font></a>'
                            )
                        else:
                            formatted_parts.append(part_esc)
                    contact_line = " | ".join(formatted_parts)
                    story.append(Paragraph(contact_line, contact_style))

            elif section_name == "EDUCATION":
                edu_lines = [
                    ln.strip()
                    for ln in content.split("\n")
                    if ln.strip() and not ln.strip().startswith("(")
                ]
                has_content = any("|" in ln for ln in edu_lines)
                if not has_content:
                    continue

                story.append(Paragraph("Education", section_header_style))
                story.append(
                    HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceAfter=4)
                )

                i = 0
                while i < len(edu_lines):
                    if "|" in edu_lines[i]:
                        parts = [p.strip() for p in edu_lines[i].split("|")]
                        if len(parts) == 2:
                            school, location = parts
                            if i + 1 < len(edu_lines) and "|" in edu_lines[i + 1]:
                                degree_parts = [p.strip() for p in edu_lines[i + 1].split("|")]
                                if len(degree_parts) == 2:
                                    degree, date = degree_parts
                                    row1 = Table(
                                        [[
                                            Paragraph(
                                                LaTeXGenerator._xml_escape(school),
                                                subheading_left_style,
                                            ),
                                            Paragraph(
                                                LaTeXGenerator._xml_escape(location),
                                                subheading_right_style,
                                            ),
                                        ]],
                                        colWidths=[content_width * 0.70, content_width * 0.30],
                                    )
                                    row1.setStyle(
                                        TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0),
                                                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                                                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                                                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1)])
                                    )
                                    row2 = Table(
                                        [[
                                            Paragraph(
                                                f"<i>{LaTeXGenerator._xml_escape(degree)}</i>",
                                                subheading_left_plain_style,
                                            ),
                                            Paragraph(
                                                LaTeXGenerator._xml_escape(date),
                                                subheading_right_style,
                                            ),
                                        ]],
                                        colWidths=[content_width * 0.70, content_width * 0.30],
                                    )
                                    row2.setStyle(
                                        TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0),
                                                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                                                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                                                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4)])
                                    )
                                    story.append(row1)
                                    story.append(row2)
                                    i += 2
                                    continue
                    i += 1

            elif section_name in ("TECHNICAL SKILLS", "SKILLS"):
                if skills_added:
                    continue
                skill_lines = [
                    ln.strip() for ln in content.split("\n") if ln.strip() and ":" in ln
                ]
                if not skill_lines:
                    continue

                story.append(Paragraph("Technical Skills", section_header_style))
                story.append(
                    HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceAfter=4)
                )

                for ln in skill_lines:
                    if ":" in ln:
                        cat, rest = ln.split(":", 1)
                        cat_esc = LaTeXGenerator._xml_escape(cat.strip())
                        rest_esc = LaTeXGenerator._xml_escape(rest.strip())
                        story.append(
                            Paragraph(f"<b>{cat_esc}:</b> {rest_esc}", skills_style)
                        )

                skills_added = True

            elif section_name == "EXPERIENCE":
                exp_lines = [
                    ln.strip()
                    for ln in content.split("\n")
                    if ln.strip() and not ln.strip().startswith("(")
                ]
                has_content = any("|" in ln for ln in exp_lines if not ln.startswith("-"))
                if not has_content:
                    continue

                story.append(Paragraph("Experience", section_header_style))
                story.append(
                    HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceAfter=4)
                )

                date_pattern = (
                    r"\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Present|Current)"
                )
                i = 0
                while i < len(exp_lines):
                    if "|" in exp_lines[i] and not exp_lines[i].startswith("-"):
                        parts = [p.strip() for p in exp_lines[i].split("|")]

                        if len(parts) == 4:
                            title, company, location, date = parts
                        elif len(parts) == 3:
                            if re.search(date_pattern, parts[2], re.IGNORECASE):
                                title, company, date = parts
                                location = ""
                            else:
                                title, company, location = parts
                                date = ""
                        elif len(parts) == 2:
                            first_p1, first_p2 = parts
                            if (
                                i + 1 < len(exp_lines)
                                and "|" in exp_lines[i + 1]
                                and not exp_lines[i + 1].startswith("-")
                            ):
                                second_parts = [p.strip() for p in exp_lines[i + 1].split("|")]
                                if len(second_parts) == 2:
                                    second_p1, second_p2 = second_parts
                                    if re.search(date_pattern, first_p2, re.IGNORECASE):
                                        title, date, company, location = (
                                            first_p1, first_p2, second_p1, second_p2
                                        )
                                    else:
                                        company, location, title, date = (
                                            first_p1, first_p2, second_p1, second_p2
                                        )
                                    i += 1
                                else:
                                    title, date = first_p1, first_p2
                                    company, location = "", ""
                            else:
                                if re.search(date_pattern, first_p2, re.IGNORECASE):
                                    title, date = first_p1, first_p2
                                    company, location = "", ""
                                else:
                                    title, date = first_p1, ""
                                    company, location = "", first_p2
                        else:
                            i += 1
                            continue

                        row1 = Table(
                            [[
                                Paragraph(
                                    f"<b>{LaTeXGenerator._xml_escape(title)}</b>",
                                    subheading_left_style,
                                ),
                                Paragraph(
                                    LaTeXGenerator._xml_escape(date),
                                    subheading_right_style,
                                ),
                            ]],
                            colWidths=[content_width * 0.70, content_width * 0.30],
                        )
                        row1.setStyle(
                            TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0),
                                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                                        ("TOPPADDING", (0, 0), (-1, -1), 0),
                                        ("BOTTOMPADDING", (0, 0), (-1, -1), 1)])
                        )
                        row2 = Table(
                            [[
                                Paragraph(
                                    f"<i>{LaTeXGenerator._xml_escape(company)}</i>",
                                    subheading_left_plain_style,
                                ),
                                Paragraph(
                                    LaTeXGenerator._xml_escape(location),
                                    subheading_right_style,
                                ),
                            ]],
                            colWidths=[content_width * 0.70, content_width * 0.30],
                        )
                        row2.setStyle(
                            TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0),
                                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                                        ("TOPPADDING", (0, 0), (-1, -1), 0),
                                        ("BOTTOMPADDING", (0, 0), (-1, -1), 2)])
                        )
                        story.append(row1)
                        story.append(row2)

                        i += 1
                        while i < len(exp_lines) and exp_lines[i].startswith("-"):
                            bullet = exp_lines[i][1:].strip()
                            bullet_bold = LaTeXGenerator.bold_metrics(bullet)
                            bullet_text = LaTeXGenerator._finalize_bold_for_pdf(bullet_bold)
                            story.append(Paragraph(bullet_text, bullet_style))
                            i += 1
                        story.append(Spacer(1, 4))
                        continue
                    i += 1

            elif section_name == "PROJECTS":
                proj_lines = [
                    ln.strip()
                    for ln in content.split("\n")
                    if ln.strip() and not ln.strip().startswith("(")
                ]
                has_content = any(
                    not ln.startswith("-") for ln in proj_lines
                )
                if not has_content:
                    continue

                story.append(Paragraph("Projects", section_header_style))
                story.append(
                    HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceAfter=4)
                )

                i = 0
                while i < len(proj_lines):
                    if not proj_lines[i].startswith("-"):
                        parts = [p.strip() for p in proj_lines[i].split("|")]
                        project_name = parts[0]
                        date_str = ""
                        tech_stack = ""

                        if len(parts) >= 2:
                            # Pipe-delimited header: "Name | Stack" or "Name | Stack | Date"
                            if len(parts) == 3 and re.search(
                                r"\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
                                r"|Present|Current)|^(?:N/?A|NA|None|TBD)$",
                                parts[2].strip(),
                                re.IGNORECASE,
                            ):
                                tech_stack = parts[1]
                                raw_date = LaTeXGenerator._sanitize_date(parts[2])
                                date_str = raw_date
                            else:
                                tech_stack = " | ".join(parts[1:])
                                # Check if the next non-bullet line is a date
                                i += 1
                                if (
                                    i < len(proj_lines)
                                    and not proj_lines[i].startswith("-")
                                    and "|" not in proj_lines[i]
                                ):
                                    raw_date = LaTeXGenerator._sanitize_date(proj_lines[i])
                                    date_str = raw_date
                                else:
                                    # Next line is a bullet or another header; don't consume it
                                    i -= 1
                        else:
                            # Plain header with no pipe: next non-bullet line may be a date
                            i += 1
                            if (
                                i < len(proj_lines)
                                and not proj_lines[i].startswith("-")
                                and "|" not in proj_lines[i]
                            ):
                                raw_date = LaTeXGenerator._sanitize_date(proj_lines[i])
                                date_str = raw_date
                            else:
                                i -= 1

                        i += 1

                        proj_esc = LaTeXGenerator._xml_escape(project_name)
                        tech_esc = LaTeXGenerator._xml_escape(tech_stack)
                        date_esc = LaTeXGenerator._xml_escape(date_str)

                        header_text = f"<b>{proj_esc}</b>"
                        if tech_esc:
                            header_text += f" | <i>{tech_esc}</i>"
                        proj_row = Table(
                            [[
                                Paragraph(header_text, subheading_left_style),
                                Paragraph(date_esc, subheading_right_style),
                            ]],
                            colWidths=[content_width * 0.70, content_width * 0.30],
                        )
                        proj_row.setStyle(
                            TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0),
                                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                                        ("TOPPADDING", (0, 0), (-1, -1), 0),
                                        ("BOTTOMPADDING", (0, 0), (-1, -1), 2)])
                        )
                        story.append(proj_row)

                        while i < len(proj_lines) and proj_lines[i].startswith("-"):
                            bullet = proj_lines[i][1:].strip()
                            bullet_bold = LaTeXGenerator.bold_metrics(bullet)
                            bullet_text = LaTeXGenerator._finalize_bold_for_pdf(bullet_bold)
                            story.append(Paragraph(bullet_text, bullet_style))
                            i += 1
                        story.append(Spacer(1, 4))
                        continue
                    i += 1

        doc.build(story)

    @staticmethod
    def generate_latex(
        resume_text: str,
        template_path: str,
        output_dir: str,
        user_name: str = None,
        company: str = None,
        job_title: str = None,
    ) -> tuple[str, str]:
        """
        Generate LaTeX file from structured resume text.

        Args:
            resume_text: Tailored resume text in structured format (with header prepended)
            template_path: Path to LaTeX template
            output_dir: Directory to save output files
            user_name: User's name for filename
            company: Company name for filename
            job_title: Job title for filename

        Returns:
            Tuple of (pdf_path, tex_path)
        """
        try:
            # Generate filename
            if user_name and company and job_title:
                # Sanitize filename components - remove special chars but keep spaces for proper word separation
                safe_name = re.sub(r"[^\w\s-]", "", user_name).strip()
                safe_company = re.sub(r"[^\w\s-]", "", company).strip()
                safe_title = re.sub(r"[^\w\s-]", "", job_title).strip()

                # Replace multiple spaces with single space, then replace spaces with underscores
                safe_name = re.sub(r"\s+", " ", safe_name).replace(" ", "_")
                safe_company = re.sub(r"\s+", " ", safe_company).replace(" ", "_")
                safe_title = re.sub(r"\s+", " ", safe_title).replace(" ", "_")

                filename = f"{safe_name}_{safe_company}_{safe_title}_resume"
            else:
                filename = str(uuid.uuid4())

            tex_file = os.path.join(output_dir, f"{filename}.tex")
            pdf_file = os.path.join(output_dir, f"{filename}.pdf")

            # Handle filename collisions
            counter = 1
            while os.path.exists(tex_file) or os.path.exists(pdf_file):
                if user_name and company and job_title:
                    filename = f"{safe_name}_{safe_company}_{safe_title}_resume_{counter}"
                else:
                    filename = str(uuid.uuid4())
                tex_file = os.path.join(output_dir, f"{filename}.tex")
                pdf_file = os.path.join(output_dir, f"{filename}.pdf")
                counter += 1

            # Read template
            with open(template_path) as f:
                template = f.read()

            # Convert structured text to LaTeX
            latex_resume_content = LaTeXGenerator.parse_structured_resume(resume_text)

            # Replace placeholder in template with LaTeX content
            latex_content = template.replace("{{RESUME_CONTENT}}", latex_resume_content)

            # Write LaTeX file
            with open(tex_file, "w") as f:
                f.write(latex_content)

            # Generate PDF using pure-Python reportlab (works on any OS)
            app_logger.info(f"Generating PDF: {filename}.pdf")
            LaTeXGenerator._generate_pdf_with_reportlab(resume_text, pdf_file)

            if not os.path.exists(pdf_file):
                app_logger.error(f"PDF file was not generated for {filename}")
                raise Exception("PDF file was not generated")

            app_logger.info(f"PDF generated successfully: {filename}.pdf")
            return pdf_file, tex_file

        except Exception as e:
            app_logger.error(f"Error generating PDF: {str(e)}")
            raise Exception(f"Error generating PDF: {str(e)}")
