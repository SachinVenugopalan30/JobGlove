import json
from services.ai_service import AIProvider
from utils.logger import app_logger

SCORING_PROMPT_TEMPLATE = """
You are an expert resume analyst and career coach. Analyze the following resume against the job description and provide a detailed scoring breakdown.

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

Provide a scoring analysis in the following JSON format:
{{
  "ats_score": <number 0-20>,
  "ats_feedback": "<detailed feedback on ATS readability, formatting, keyword usage, parseability>",
  "content_score": <number 0-20>,
  "content_feedback": "<detailed feedback on relevance, achievements, quantification, clarity>",
  "style_score": <number 0-25>,
  "style_feedback": "<detailed feedback on action verbs, conciseness, consistency, professionalism>",
  "match_score": <number 0-25>,
  "match_feedback": "<detailed feedback on alignment with job requirements, relevant skills, experience match>",
  "readiness_score": <number 0-10>,
  "readiness_feedback": "<detailed feedback on overall polish, completeness, competitive strength>"
}}

Scoring Guidelines:
1. ATS Readability (0-20): Assess formatting consistency, keyword presence, structure clarity, and parseability by ATS systems
2. Content Quality (0-20): Evaluate relevance of experience, achievement impact, use of metrics/numbers, and clarity
3. Writing Style (0-25): Analyze use of strong action verbs, conciseness, consistency, and professional tone
4. Job Match (0-25): Compare resume against specific job requirements, required skills, and relevant experience
5. Readiness Score (0-10): Overall assessment of whether the resume is competitive and ready for submission

Be objective and constructive in your feedback. Highlight both strengths and areas for improvement.
Return ONLY the JSON object, no additional text.
"""

class ScoringService:
    def __init__(self, ai_provider: AIProvider):
        self.ai_provider = ai_provider
        app_logger.info(f"ScoringService initialized with {ai_provider.__class__.__name__}")

    def score_resume(self, resume_text: str, job_description: str) -> dict:
        try:
            prompt = SCORING_PROMPT_TEMPLATE.format(
                job_description=job_description,
                resume_text=resume_text
            )

            app_logger.info("Requesting resume scoring from AI")
            response = self.ai_provider.generate(prompt)

            response_text = response.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            scores = json.loads(response_text)

            total_score = (
                scores.get('ats_score', 0) +
                scores.get('content_score', 0) +
                scores.get('style_score', 0) +
                scores.get('match_score', 0) +
                scores.get('readiness_score', 0)
            )
            scores['total_score'] = round(total_score, 1)

            app_logger.info(f"Resume scored successfully. Total: {scores['total_score']}/100")
            return scores

        except json.JSONDecodeError as e:
            app_logger.error(f"Failed to parse AI scoring response as JSON: {e}")
            app_logger.error(f"Response was: {response[:500] if len(response) > 500 else response}")
            return self._fallback_score(f"Failed to parse AI response: {str(e)}")
        except Exception as e:
            app_logger.error(f"Error during resume scoring: {e}")
            return self._fallback_score(str(e))

    def _fallback_score(self, error_message: str) -> dict:
        return {
            'ats_score': 0,
            'ats_feedback': f'Scoring unavailable: {error_message}',
            'content_score': 0,
            'content_feedback': f'Scoring unavailable: {error_message}',
            'style_score': 0,
            'style_feedback': f'Scoring unavailable: {error_message}',
            'match_score': 0,
            'match_feedback': f'Scoring unavailable: {error_message}',
            'readiness_score': 0,
            'readiness_feedback': f'Scoring unavailable: {error_message}',
            'total_score': 0
        }

def create_scoring_service(api_name: str) -> ScoringService:
    provider = AIProvider.create(api_name)
    return ScoringService(provider)
