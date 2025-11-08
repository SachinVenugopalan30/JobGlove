import os
import subprocess
import uuid
import re
from typing import Dict, List, Tuple
from utils.logger import app_logger

class LaTeXGenerator:
    @staticmethod
    def escape_latex(text: str) -> str:
        """Escape special LaTeX characters using regex for proper ordering"""
        # Escape backslash first, then others
        # Use a placeholder to avoid double-escaping
        text = text.replace('\\', '<<<BACKSLASH>>>')

        # Escape other special characters
        replacements = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\^{}',
        }

        for char, escape in replacements.items():
            text = text.replace(char, escape)

        # Replace backslash placeholder last
        text = text.replace('<<<BACKSLASH>>>', r'\textbackslash{}')

        return text

    @staticmethod
    def bold_metrics(text: str) -> str:
        """Bold numbers and metrics in text using \\textbf{}, then escape LaTeX"""
        # Pattern to match various numeric formats
        # Order matters: more specific patterns first
        # Use negative lookbehind to avoid re-matching already bolded content
        patterns = [
            (r'(\d+(?:\.\d+)?%)', r'<<<BOLD_START>>>\1<<<BOLD_END>>>'),  # Percentages: 50%, 12.5%
            (r'(\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', r'<<<BOLD_START>>>\1<<<BOLD_END>>>'),  # Currency: $1,000, $50.00
            (r'(?<!\$)(\d{1,3}(?:,\d{3})+)(?![\d.])', r'<<<BOLD_START>>>\1<<<BOLD_END>>>'),  # Large numbers: 1,000 (not after $)
            (r'(\d+-\d+)', r'<<<BOLD_START>>>\1<<<BOLD_END>>>'),  # Ranges: 10-20, 2021-2023
            (r'\b(\d+(?:\.\d+)?[KMB])\b', r'<<<BOLD_START>>>\1<<<BOLD_END>>>'),  # Abbreviated: 5K, 2.5M
            (r'\b(\d+(?:\.\d+)?)\s*(million|billion|thousand)', r'<<<BOLD_START>>>\1<<<BOLD_END>>> \2'),
            (r'(\d+x)', r'<<<BOLD_START>>>\1<<<BOLD_END>>>'),  # Multipliers: 2x, 10x
            (r'(?<!-)(\d{4})(?!-)', r'<<<BOLD_START>>>\1<<<BOLD_END>>>'),  # Years: 2023 (not in ranges)
        ]

        result = text
        for pattern, replacement in patterns:
            # Skip if already inside bold markers
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

        return result

    @staticmethod
    def finalize_bold_and_escape(text: str) -> str:
        """Escape LaTeX special characters while preserving bold placeholders, then convert to textbf"""
        # Extract bolded content temporarily
        bold_contents = []
        def save_bold(match):
            bold_contents.append(match.group(1))
            return f'<<<BOLDPLACEHOLDER{len(bold_contents)-1}>>>'

        text = re.sub(r'<<<BOLD_START>>>(.*?)<<<BOLD_END>>>', save_bold, text)

        # Escape the rest of the text
        text = LaTeXGenerator.escape_latex(text)

        # Restore bolded content with textbf
        for i, content in enumerate(bold_contents):
            escaped_content = LaTeXGenerator.escape_latex(content)
            text = text.replace(f'<<<BOLDPLACEHOLDER{i}>>>', f'\\textbf{{{escaped_content}}}')

        return text

    @staticmethod
    def parse_structured_resume(resume_text: str) -> str:
        """
        Parse structured resume text and convert to LaTeX format.

        Args:
            resume_text: Structured resume text from AI

        Returns:
            LaTeX formatted resume content
        """
        latex_parts = []

        # Split into sections (handle sections at start of string or after newline)
        sections = re.split(r'(?:^|\n)\[([A-Z]+)\]\n', resume_text, flags=re.MULTILINE)

        current_section = None
        for i, part in enumerate(sections):
            if i == 0:
                continue

            if i % 2 == 1:
                current_section = part
            else:
                content = part.strip()
                section_latex = ""

                if current_section == 'HEADER':
                    section_latex = LaTeXGenerator._format_header(content)
                elif current_section == 'EDUCATION':
                    section_latex = LaTeXGenerator._format_education(content)
                elif current_section == 'TECHNICAL SKILLS':
                    section_latex = LaTeXGenerator._format_skills(content)
                elif current_section == 'EXPERIENCE':
                    section_latex = LaTeXGenerator._format_experience(content)
                elif current_section == 'PROJECTS':
                    section_latex = LaTeXGenerator._format_projects(content)
                
                # Only add non-empty sections
                if section_latex:
                    latex_parts.append(section_latex)

        return '\n\n'.join(latex_parts)

    @staticmethod
    def _format_header(content: str) -> str:
        """Format header section"""
        lines = [line.strip() for line in content.split('\n') if line.strip()]

        # Handle edge cases: missing or incomplete header
        if len(lines) == 0:
            # No header content at all - skip it
            return ''

        if len(lines) == 1:
            # Only name provided
            name = LaTeXGenerator.escape_latex(lines[0])
            return f"\\begin{{center}}\n    \\textbf{{\\Huge \\scshape {name}}}\n\\end{{center}}"

        # Full header with name and contact info
        name = LaTeXGenerator.escape_latex(lines[0])
        contact_info = lines[1]

        # Don't escape contact info yet - process it first
        # Split contact info by |
        contact_parts = [part.strip() for part in contact_info.split('|')]

        # Format with href for email and links
        formatted_parts = []
        for part in contact_parts:
            # Escape the part first
            part_escaped = LaTeXGenerator.escape_latex(part)

            # Check original (unescaped) for special handling
            if '@' in part and 'redacted' not in part.lower():
                # Real email - make it a hyperlink
                formatted_parts.append(f"\\href{{mailto:{part}}}{{\\underline{{{part_escaped}}}}}")
            elif ('linkedin.com' in part.lower() or 'github.com' in part.lower()) and 'redacted' not in part.lower():
                # Real link - make it a hyperlink
                formatted_parts.append(f"\\href{{{part}}}{{\\underline{{{part_escaped}}}}}")
            else:
                # Plain text (including REDACTED values)
                formatted_parts.append(part_escaped)

        contact_line = ' $|$ '.join(formatted_parts)

        return f"\\begin{{center}}\n    \\textbf{{\\Huge \\scshape {name}}} \\\\ \\vspace{{1pt}}\n    \\small {contact_line}\n\\end{{center}}"

    @staticmethod
    def _format_education(content: str) -> str:
        """Format education section - skip if empty"""
        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('(')]

        # Check if there's any actual content (look for school entries with |)
        has_content = False
        for line in lines:
            if '|' in line:
                has_content = True
                break
        
        # Skip the entire section if empty
        if not has_content:
            return ""
        
        latex = "\\section{Education}\n  \\resumeSubHeadingListStart\n"

        i = 0
        while i < len(lines):
            if '|' in lines[i]:
                parts = [p.strip() for p in lines[i].split('|')]
                if len(parts) == 2:
                    school, location = parts
                    if i + 1 < len(lines) and '|' in lines[i + 1]:
                        degree_parts = [p.strip() for p in lines[i + 1].split('|')]
                        if len(degree_parts) == 2:
                            degree, date = degree_parts
                            school_esc = LaTeXGenerator.escape_latex(school)
                            location_esc = LaTeXGenerator.escape_latex(location)
                            degree_esc = LaTeXGenerator.escape_latex(degree)
                            date_esc = LaTeXGenerator.escape_latex(date)
                            latex += f"    \\resumeSubheading\n      {{{school_esc}}}{{{location_esc}}}\n      {{{degree_esc}}}{{{date_esc}}}\n"
                            i += 2
                            continue
            i += 1

        latex += "  \\resumeSubHeadingListEnd"
        return latex

    @staticmethod
    def _format_experience(content: str) -> str:
        """Format experience section - skip if empty
        
        Handles two formats:
        Format 1 (preferred - from prompt):
            Company Name | Location
            Job Title | Start Date - End Date
            - Bullet points
        
        Format 2 (AI sometimes returns):
            Job Title | Company Name | Location | Date
            - Bullet points
        """
        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('(')]
        
        # Check if there's any actual content (look for company entries with |)
        has_content = False
        for line in lines:
            if '|' in line and not line.startswith('-'):
                has_content = True
                break
        
        # Skip the entire section if empty
        if not has_content:
            app_logger.info("Experience section is empty, skipping")
            return ""
        
        latex = "\\section{Experience}\n  \\resumeSubHeadingListStart\n\n"

        i = 0
        while i < len(lines):
            if '|' in lines[i] and not lines[i].startswith('-'):
                parts = [p.strip() for p in lines[i].split('|')]
                
                # Format 2: Single line with 4 parts (Title | Company | Location | Date)
                if len(parts) == 4:
                    title, company, location, date = parts
                    
                    company_esc = LaTeXGenerator.escape_latex(company)
                    location_esc = LaTeXGenerator.escape_latex(location)
                    title_esc = LaTeXGenerator.escape_latex(title)
                    date_esc = LaTeXGenerator.escape_latex(date)
                    
                    latex += f"    \\resumeSubheading\n      {{{company_esc}}}{{{location_esc}}}\n      {{{title_esc}}}{{{date_esc}}}\n"
                    latex += "      \\resumeItemListStart\n"
                    
                    i += 1
                    while i < len(lines) and lines[i].startswith('-'):
                        bullet = lines[i][1:].strip()
                        bullet_bold = LaTeXGenerator.bold_metrics(bullet)
                        bullet_esc = LaTeXGenerator.finalize_bold_and_escape(bullet_bold)
                        latex += f"        \\resumeItem{{{bullet_esc}}}\n"
                        i += 1
                    
                    latex += "      \\resumeItemListEnd\n\n"
                    continue
                    
                # Format 1: Two lines (Company | Location, then Title | Date)
                elif len(parts) == 2:
                    company, location = parts

                    if i + 1 < len(lines) and '|' in lines[i + 1] and not lines[i + 1].startswith('-'):
                        title_parts = [p.strip() for p in lines[i + 1].split('|')]
                        if len(title_parts) == 2:
                            title, date = title_parts

                            company_esc = LaTeXGenerator.escape_latex(company)
                            location_esc = LaTeXGenerator.escape_latex(location)
                            title_esc = LaTeXGenerator.escape_latex(title)
                            date_esc = LaTeXGenerator.escape_latex(date)

                            latex += f"    \\resumeSubheading\n      {{{company_esc}}}{{{location_esc}}}\n      {{{title_esc}}}{{{date_esc}}}\n"
                            latex += "      \\resumeItemListStart\n"

                            i += 2
                            while i < len(lines) and lines[i].startswith('-'):
                                bullet = lines[i][1:].strip()
                                bullet_bold = LaTeXGenerator.bold_metrics(bullet)
                                bullet_esc = LaTeXGenerator.finalize_bold_and_escape(bullet_bold)
                                latex += f"        \\resumeItem{{{bullet_esc}}}\n"
                                i += 1

                            latex += "      \\resumeItemListEnd\n\n"
                            continue
            i += 1

        latex += "  \\resumeSubHeadingListEnd"
        return latex

    @staticmethod
    def _format_skills(content: str) -> str:
        """Format skills section - skip if empty"""
        lines = [line.strip() for line in content.split('\n') if line.strip() and ':' in line]

        # Skip the entire section if empty
        if not lines:
            return ""
        
        latex = "\\section{Technical Skills}\n \\begin{itemize}[leftmargin=0.15in, label={}]\n"

        for line in lines:
            if ':' in line:
                parts = line.split(':', 1)
                category = parts[0].strip()
                skills = parts[1].strip()

                category_esc = LaTeXGenerator.escape_latex(category)
                skills_esc = LaTeXGenerator.escape_latex(skills)

                latex += f"    \\small{{\\item{{\n     \\textbf{{{category_esc}}}{{: {skills_esc}}} \\\\\n    }}}}"

        latex += " \\end{itemize}"
        return latex

    @staticmethod
    def _format_projects(content: str) -> str:
        """Format projects section - skip if empty"""
        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('(')]

        # Check if there's any actual content (look for project entries with |)
        has_content = False
        for line in lines:
            if '|' in line and not line.startswith('-'):
                has_content = True
                break
        
        # Skip the entire section if empty
        if not has_content:
            return ""
        
        latex = "\\section{Projects}\n    \\resumeSubHeadingListStart\n"

        i = 0
        while i < len(lines):
            if '|' in lines[i] and not lines[i].startswith('-'):
                parts = [p.strip() for p in lines[i].split('|')]
                if len(parts) == 2:
                    project_name, tech_stack = parts

                    if i + 1 < len(lines) and not lines[i + 1].startswith('-'):
                        date_range = lines[i + 1].strip()

                        project_esc = LaTeXGenerator.escape_latex(project_name)
                        tech_esc = LaTeXGenerator.escape_latex(tech_stack)
                        date_esc = LaTeXGenerator.escape_latex(date_range)

                        latex += f"      \\resumeProjectHeading\n          {{\\textbf{{{project_esc}}} $|$ \\emph{{{tech_esc}}}}}{{{date_esc}}}\n"
                        latex += "          \\resumeItemListStart\n"

                        i += 2
                        while i < len(lines) and lines[i].startswith('-'):
                            bullet = lines[i][1:].strip()
                            bullet_bold = LaTeXGenerator.bold_metrics(bullet)
                            bullet_esc = LaTeXGenerator.finalize_bold_and_escape(bullet_bold)
                            latex += f"            \\resumeItem{{{bullet_esc}}}\n"
                            i += 1

                        latex += "          \\resumeItemListEnd\n"
                        continue
            i += 1

        latex += "    \\resumeSubHeadingListEnd"
        return latex

    @staticmethod
    def parse_resume_sections(resume_text: str) -> dict:
        """Parse resume text into sections"""
        lines = resume_text.split('\n')
        sections = {}
        current_section = 'header'
        current_content = []

        common_headers = ['experience', 'education', 'skills', 'summary', 'projects', 'certifications']

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
    def generate_latex(resume_text: str, template_path: str, output_dir: str,
                      user_name: str = None, company: str = None, job_title: str = None) -> Tuple[str, str]:
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
                safe_name = re.sub(r'[^\w\s-]', '', user_name).strip()
                safe_company = re.sub(r'[^\w\s-]', '', company).strip()
                safe_title = re.sub(r'[^\w\s-]', '', job_title).strip()
                
                # Replace multiple spaces with single space, then replace spaces with underscores
                safe_name = re.sub(r'\s+', ' ', safe_name).replace(' ', '_')
                safe_company = re.sub(r'\s+', ' ', safe_company).replace(' ', '_')
                safe_title = re.sub(r'\s+', ' ', safe_title).replace(' ', '_')
                
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
            with open(template_path, 'r') as f:
                template = f.read()

            # Convert structured text to LaTeX
            latex_resume_content = LaTeXGenerator.parse_structured_resume(resume_text)

            # Replace placeholder in template with LaTeX content
            latex_content = template.replace('{{RESUME_CONTENT}}', latex_resume_content)

            # Write LaTeX file
            with open(tex_file, 'w') as f:
                f.write(latex_content)

            # Compile LaTeX to PDF (run twice for proper cross-references)
            app_logger.info(f"Compiling LaTeX file: {filename}.tex")
            for _ in range(2):
                result = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', '-output-directory', output_dir, tex_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

            if result.returncode != 0:
                app_logger.error(f"LaTeX compilation failed for {filename}.tex")
                # pdflatex logs to stdout, so we include it in the exception
                error_log = result.stdout or result.stderr
                raise Exception(f"LaTeX compilation failed: {error_log}")

            # Clean up auxiliary files (keep .tex for debugging)
            for ext in ['.aux', '.log', '.out']:
                aux_file = os.path.join(output_dir, f"{filename}{ext}")
                if os.path.exists(aux_file):
                    os.remove(aux_file)

            if not os.path.exists(pdf_file):
                app_logger.error(f"PDF file was not generated for {filename}")
                raise Exception("PDF file was not generated")

            app_logger.info(f"LaTeX compilation successful: {filename}.pdf")
            return pdf_file, tex_file

        except subprocess.TimeoutExpired:
            app_logger.error(f"LaTeX compilation timed out for {filename}.tex")
            raise Exception("LaTeX compilation timed out")
        except Exception as e:
            app_logger.error(f"Error generating PDF: {str(e)}")
            raise Exception(f"Error generating PDF: {str(e)}")
