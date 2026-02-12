"""Entity extraction module for extracting structured information from resumes."""

import re

import spacy

from utils.logger import app_logger

nlp = spacy.load('en_core_web_sm')


def extract_name(text: str) -> str | None:
    """
    Extract candidate name from resume using NER.

    Args:
        text: Resume text

    Returns:
        Candidate name or None if not found

    Strategy:
    - Look for PERSON entities in first 500 characters
    - Prefer first occurrence (likely in header)
    """
    try:
        doc = nlp(text[:500])

        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                name = ent.text.strip()
                if len(name.split()) >= 2:
                    app_logger.debug(f"Extracted name: {name}")
                    return name

        app_logger.warning("No name found in resume")
        return None

    except Exception as e:
        app_logger.error(f"Error extracting name: {e}")
        return None


def extract_email(text: str) -> str | None:
    """
    Extract email address from resume using regex.

    Args:
        text: Resume text

    Returns:
        Email address or None if not found
    """
    try:
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)

        if matches:
            email = matches[0]
            app_logger.debug(f"Extracted email: {email}")
            return email

        app_logger.warning("No email found in resume")
        return None

    except Exception as e:
        app_logger.error(f"Error extracting email: {e}")
        return None


def extract_phone(text: str) -> str | None:
    """
    Extract phone number from resume using regex.

    Args:
        text: Resume text

    Returns:
        Phone number or None if not found

    Supports formats:
    - (123) 456-7890
    - 123-456-7890
    - 123.456.7890
    - +1 123 456 7890
    - 1234567890
    """
    try:
        phone_patterns = [
            r'\+?1?\s*\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}',
            r'\+?\d{1,3}[\s.-]?\d{3,4}[\s.-]?\d{3,4}[\s.-]?\d{3,4}'
        ]

        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                phone = matches[0].strip()
                app_logger.debug(f"Extracted phone: {phone}")
                return phone

        app_logger.warning("No phone number found in resume")
        return None

    except Exception as e:
        app_logger.error(f"Error extracting phone: {e}")
        return None


def extract_sections(text: str) -> dict[str, str]:
    """
    Identify and extract resume sections.

    Args:
        text: Resume text

    Returns:
        Dictionary with section names as keys and section content as values

    Common sections:
    - experience / work experience / employment
    - education
    - skills / technical skills
    - summary / objective / profile
    - projects
    - certifications
    """
    sections = {}

    section_patterns = {
        'experience': r'(?i)(work experience|experience|employment|professional experience)',
        'education': r'(?i)(education|academic background)',
        'skills': r'(?i)(skills|technical skills|core competencies|technologies)',
        'summary': r'(?i)(summary|objective|profile|about me)',
        'projects': r'(?i)(projects|portfolio)',
        'certifications': r'(?i)(certifications|certificates|licenses)'
    }

    lines = text.split('\n')

    current_section = None
    section_content = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        matched_section = None
        for section_name, pattern in section_patterns.items():
            if re.match(pattern, line) and len(line) < 50:
                matched_section = section_name
                break

        if matched_section:
            if current_section and section_content:
                sections[current_section] = '\n'.join(section_content)

            current_section = matched_section
            section_content = []
        elif current_section:
            section_content.append(line)

    if current_section and section_content:
        sections[current_section] = '\n'.join(section_content)

    app_logger.debug(f"Extracted sections: {list(sections.keys())}")
    return sections


def extract_all_entities(text: str) -> dict:
    """
    Extract all entities from resume.

    Args:
        text: Resume text

    Returns:
        Dictionary containing all extracted entities:
        {
            'name': str or None,
            'email': str or None,
            'phone': str or None,
            'sections': dict
        }
    """
    try:
        entities = {
            'name': extract_name(text),
            'email': extract_email(text),
            'phone': extract_phone(text),
            'sections': extract_sections(text)
        }

        app_logger.info(f"Extracted entities: name={bool(entities['name'])}, "
                       f"email={bool(entities['email'])}, phone={bool(entities['phone'])}, "
                       f"sections={list(entities['sections'].keys())}")

        return entities

    except Exception as e:
        app_logger.error(f"Error extracting entities: {e}")
        return {
            'name': None,
            'email': None,
            'phone': None,
            'sections': {}
        }
