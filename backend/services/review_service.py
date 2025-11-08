import json
import re
from services.ai_service import AIProvider
from utils.logger import app_logger

REVIEW_PROMPT_TEMPLATE = """
You are an expert resume analyst. Analyze the following resume against the job description and provide detailed feedback for each bullet point.

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

For each bullet point in the resume, provide:
1. The section it belongs to (Education, Experience, Skills, Projects, etc.)
2. Strengths of the bullet point
3. Specific refinement suggestions to better match the job description
4. Relevance score from 1-5 (1=not relevant, 5=highly relevant)

Return your analysis in the following JSON format:
{{
  "bullets": [
    {{
      "section": "<section name>",
      "original_text": "<full bullet text>",
      "strengths": "<what works well about this bullet>",
      "refinement_suggestions": "<specific ways to improve it for this job>",
      "relevance_score": <1-5>
    }}
  ]
}}

Guidelines:
- Focus on actionable feedback
- Be specific about what makes each bullet strong or weak
- Suggest concrete improvements related to the job description
- Identify missing keywords or skills that could be added
- Note if metrics/numbers could strengthen the bullet
- Consider the "Accomplished X through Y using Z" framework

Return ONLY the JSON object, no additional text.
"""

class ReviewService:
    def __init__(self, ai_provider: AIProvider):
        self.ai_provider = ai_provider
        app_logger.info(f"ReviewService initialized with {ai_provider.__class__.__name__}")

    def review_resume(self, resume_text: str, job_description: str) -> list:
        try:
            prompt = REVIEW_PROMPT_TEMPLATE.format(
                job_description=job_description,
                resume_text=resume_text
            )

            app_logger.info("Requesting resume review from AI")
            response = self.ai_provider.generate(prompt)

            response_text = response.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            review_data = json.loads(response_text)
            bullets = review_data.get('bullets', [])

            app_logger.info(f"Resume reviewed successfully. {len(bullets)} bullet points analyzed")
            return bullets

        except json.JSONDecodeError as e:
            app_logger.error(f"Failed to parse AI review response as JSON: {e}")
            app_logger.error(f"Response was: {response[:500] if len(response) > 500 else response}")
            return self._extract_bullets_fallback(resume_text)
        except Exception as e:
            app_logger.error(f"Error during resume review: {e}")
            return self._extract_bullets_fallback(resume_text)

    def _extract_bullets_fallback(self, resume_text: str) -> list:
        bullets = []
        current_section = "Unknown"

        section_headers = ['EDUCATION', 'EXPERIENCE', 'SKILLS', 'PROJECTS', 'SUMMARY', 'ACHIEVEMENTS']

        lines = resume_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            upper_line = line.upper()
            for header in section_headers:
                if header in upper_line:
                    current_section = header.title()
                    break

            if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                bullet_text = line.lstrip('-•* ')
                if bullet_text:
                    bullets.append({
                        'section': current_section,
                        'original_text': bullet_text,
                        'strengths': 'Analysis unavailable',
                        'refinement_suggestions': 'Manual review recommended',
                        'relevance_score': 3
                    })

        if not bullets:
            bullets.append({
                'section': 'General',
                'original_text': 'Unable to parse resume structure',
                'strengths': 'N/A',
                'refinement_suggestions': 'Please ensure resume is properly formatted',
                'relevance_score': 1
            })

        app_logger.warning(f"Using fallback bullet extraction. Found {len(bullets)} bullets")
        return bullets

def create_review_service(api_name: str) -> ReviewService:
    provider = AIProvider.create(api_name)
    return ReviewService(provider)
