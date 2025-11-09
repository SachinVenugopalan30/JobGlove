from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import json
import openai
import google.generativeai as genai
import anthropic
from utils.logger import app_logger
from config import Config


class IncompleteClaudeResponseError(Exception):
    """Raised when Claude API returns a response missing required fields"""
    pass


class AIProvider(ABC):
    """Abstract base class for AI providers"""

    @abstractmethod
    def tailor_resume(self, resume_text: str, job_description: str, custom_prompt: Optional[str] = None) -> str:
        """Tailor resume to job description"""
        pass

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate content using the AI provider with a custom prompt"""
        pass

    @abstractmethod
    def score_and_tailor_resume(self, resume_text: str, job_description: str, custom_prompt: Optional[str] = None, similarity_score: Optional[float] = None) -> Dict[str, Any]:
        """Score original resume, tailor it, and score the tailored version in a single request"""
        pass

    @staticmethod
    def create(provider_name: str):
        """Factory method to create an AI provider instance"""
        from config import Config

        api_key = None
        provider_name_lower = provider_name.lower()

        if provider_name_lower == 'openai':
            api_key = Config.OPENAI_API_KEY
            if not api_key:
                raise ValueError("OpenAI API key not configured")
            return OpenAIProvider(api_key)
        elif provider_name_lower == 'gemini':
            api_key = Config.GEMINI_API_KEY
            if not api_key:
                raise ValueError("Gemini API key not configured")
            return GeminiProvider(api_key)
        elif provider_name_lower == 'claude':
            api_key = Config.ANTHROPIC_API_KEY
            if not api_key:
                raise ValueError("Claude API key not configured")
            return ClaudeProvider(api_key)
        else:
            raise ValueError(f"Unknown provider: {provider_name}")



    def _create_score_and_tailor_prompt(self, resume_text: str, job_description: str, custom_prompt: Optional[str] = None, similarity_score: Optional[float] = None) -> str:
        """Create prompt for scoring and tailoring in single request"""
        base_instructions = custom_prompt if custom_prompt else ""
        
        # Add similarity score context if provided
        similarity_context = ""
        if similarity_score is not None:
            similarity_context = f"""
[INITIAL MATCH ANALYSIS]
TF-IDF Cosine Similarity Score: {similarity_score}%

This score represents the keyword overlap between the resume and job description.
- Below 30%: Significant mismatch - major tailoring needed
- 30-50%: Moderate match - substantial improvements possible
- 50-70%: Good match - focus on optimizing key sections
- Above 70%: Strong match - minor refinements suggested

Use this as context when scoring and tailoring the resume.
"""

        return f"""You are an expert resume writer and analyst.

CRITICAL: Section headers MUST use square brackets and ALL CAPS.
Examples: [EDUCATION], [TECHNICAL SKILLS], [EXPERIENCE], [PROJECTS]
{similarity_context}
Your task is to:
1. Score the original resume against the job description
2. Tailor the resume to match the job description
3. Score the tailored resume

Respond with ONLY a valid JSON object in this exact format (no markdown code fences, no explanations):

{{
  "original_score": {{
    "total_score": <number 0-100>,
    "keyword_match_score": <number 0-100>,
    "relevance_score": <number 0-100>,
    "ats_score": <number 0-100>,
    "quality_score": <number 0-100>,
    "recommendations": ["<recommendation 1>", "<recommendation 2>", "..."]
  }},
  "tailored_resume": "<full tailored resume text>",
  "tailored_score": {{
    "total_score": <number 0-100>,
    "keyword_match_score": <number 0-100>,
    "relevance_score": <number 0-100>,
    "ats_score": <number 0-100>,
    "quality_score": <number 0-100>
  }}
}}

SCORING CRITERIA:
- keyword_match_score: How well the resume matches keywords from the job description (0-100)
- relevance_score: How relevant the experience is to the job (0-100)
- ats_score: ATS compatibility - clear formatting, proper structure (0-100)
- quality_score: Overall quality - quantified achievements, action verbs, clarity (0-100)
- total_score: Weighted average of the above scores

TAILORING REQUIREMENTS:
Use this EXACT format for the tailored_resume text:

[EDUCATION]
School Name | Location
Degree Title | Graduation Date

[TECHNICAL SKILLS]
Category: Skill1, Skill2, Skill3
CRITICAL: Copy the EXACT skills from the original resume - do NOT modify.

[EXPERIENCE]
CRITICAL: Each job entry MUST follow this 2-line format:
Job Title | Start Date - End Date
Company Name | Location
- Bullet points starting with "-"

BULLET POINT REQUIREMENTS:
- Each job entry MUST have 3-5 bullet points (minimum 3, maximum 5)
- If original resume has more than 5 points, condense the most impactful achievements into 5 points
- If original resume has fewer than 3 points, expand with relevant details

CORRECT Example:
Senior Data Scientist | October 2023 - April 2025
Comapny Name | City, Country
- Enhanced operational efficiency by 14% through predictive model deployment
- Reduced costs by 10% using Random Forest algorithms
- Led team of 3 data scientists

WRONG: Company first, or single line with 4 parts.

[PROJECTS]
Project Name | Tech Stack
Date Range
- Bullet points (2-4 points per project)

REQUIREMENTS:
1. PRESERVE SKILLS section exactly as in original resume
2. For EXPERIENCE/PROJECTS: Reframe to align with job description
3. Each EXPERIENCE entry MUST have 3-5 bullet points (condense if original has more)
4. Each PROJECT entry should have 2-4 bullet points
5. Use "Accomplished X through Y using Z" template for bullets
6. Use action verbs and quantify achievements (avoid repeating verbs)
7. Use plain text - DO NOT escape special characters (%, &, $, #)
8. Maintain professional tone and consistent tense
{f"9. {base_instructions}" if base_instructions else ""}

Original Resume:
{resume_text}

Job Description:
{job_description}

RESPONSE FORMAT:
- Return ONLY raw JSON starting with {{ and ending with }}
- DO NOT wrap in markdown code blocks (no ```json or ```)
- DO NOT add any explanatory text before or after the JSON
- Start your response directly with the opening brace {{
- End your response directly with the closing brace }}"""

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from AI response, handling markdown code blocks if present"""
        cleaned = response_text.strip()

        # Remove markdown code fences at the start
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]

        # Remove markdown code fences at the end
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        cleaned = cleaned.strip()

        # Try to find the JSON object boundaries
        # Look for the first '{' and last '}'
        start_idx = cleaned.find('{')
        end_idx = cleaned.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            cleaned = cleaned[start_idx:end_idx + 1]

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            app_logger.error(f"Failed to parse JSON response: {e}")
            app_logger.error(f"Response text (first 1000 chars): {response_text[:1000]}")
            app_logger.error(f"Response text (last 500 chars): {response_text[-500:]}")
            raise ValueError(f"AI returned invalid JSON: {str(e)}")

    def _create_prompt(self, resume_text: str, job_description: str, custom_prompt: Optional[str] = None) -> str:
        """Create standardized prompt for tailoring"""
        if custom_prompt:
            return custom_prompt.format(
                resume_text=resume_text,
                job_description=job_description
            )

        return f"""You are an expert resume writer. Tailor the resume to match the job description.

FORMAT YOUR RESPONSE EXACTLY AS FOLLOWS:

[EDUCATION]
School Name | Location
Degree Title | Graduation Date

[EXPERIENCE]
Job Title | Start Date - End Date
Company Name | Location
- Bullet points (3-5 points per job entry)

[TECHNICAL SKILLS]
Category: Skill1, Skill2, Skill3
CRITICAL: Copy EXACT skills from original resume - do NOT modify.

[PROJECTS]
Project Name | Tech Stack
Date Range
- Bullet points (2-4 points per project)

REQUIREMENTS:
1. PRESERVE SKILLS section exactly as in original
2. For EXPERIENCE/PROJECTS: Reframe to align with job description
3. Each EXPERIENCE entry MUST have 3-5 bullet points (condense if original has more than 5)
4. Each PROJECT entry should have 2-4 bullet points
5. Use "Accomplished X through Y using Z" template
6. Use action verbs and quantify achievements
7. Maintain consistency in tense
8. Use plain text - DO NOT escape special characters (%, &, $, #)

Original Resume:
{resume_text}

Job Description:
{job_description}

Output ONLY structured resume content in the format above."""


class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = Config.OPENAI_MODEL
        app_logger.info(f"OpenAI provider initialized with model: {self.model}")

    def score_and_tailor_resume(self, resume_text: str, job_description: str, custom_prompt: Optional[str] = None, similarity_score: Optional[float] = None) -> Dict[str, Any]:
        try:
            app_logger.info(f"Calling OpenAI API for score and tailor ({self.model})")
            prompt = self._create_score_and_tailor_prompt(resume_text, job_description, custom_prompt, similarity_score)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert resume writer and analyst. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content or ""
            app_logger.info("OpenAI API call successful")
            return self._parse_json_response(content)
        except Exception as e:
            app_logger.error(f"OpenAI API error: {str(e)}")
            raise Exception(f"OpenAI API error: {str(e)}")

    def tailor_resume(self, resume_text: str, job_description: str, custom_prompt: Optional[str] = None) -> str:
        try:
            app_logger.info(f"Calling OpenAI API ({self.model})")
            prompt = self._create_prompt(resume_text, job_description, custom_prompt)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert resume writer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            content = response.choices[0].message.content or ""
            app_logger.info("OpenAI API call successful")
            return content
        except Exception as e:
            app_logger.error(f"OpenAI API error: {str(e)}")
            raise Exception(f"OpenAI API error: {str(e)}")

    def generate(self, prompt: str) -> str:
        try:
            app_logger.info(f"Calling OpenAI API with custom prompt ({self.model})")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )
            content = response.choices[0].message.content or ""
            app_logger.info("OpenAI API call successful")
            return content
        except Exception as e:
            app_logger.error(f"OpenAI API error: {str(e)}")
            raise Exception(f"OpenAI API error: {str(e)}")


class GeminiProvider(AIProvider):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model_name = Config.GEMINI_MODEL
        self.model = genai.GenerativeModel(self.model_name,
            generation_config={"response_mime_type": "application/json"})
        app_logger.info(f"Gemini provider initialized with model: {self.model_name}")

    def score_and_tailor_resume(self, resume_text: str, job_description: str, custom_prompt: Optional[str] = None, similarity_score: Optional[float] = None) -> Dict[str, Any]:
        try:
            app_logger.info(f"Calling Gemini API for score and tailor ({self.model_name})")
            prompt = self._create_score_and_tailor_prompt(resume_text, job_description, custom_prompt, similarity_score)
            response = self.model.generate_content(prompt)
            content = response.text
            app_logger.info("Gemini API call successful")
            return self._parse_json_response(content)
        except Exception as e:
            app_logger.error(f"Gemini API error: {str(e)}")
            raise Exception(f"Gemini API error: {str(e)}")

    def tailor_resume(self, resume_text: str, job_description: str, custom_prompt: Optional[str] = None) -> str:
        try:
            app_logger.info(f"Calling Gemini API ({self.model_name})")
            prompt = self._create_prompt(resume_text, job_description, custom_prompt)
            response = self.model.generate_content(prompt)
            content = response.text
            app_logger.info("Gemini API call successful")
            return content
        except Exception as e:
            app_logger.error(f"Gemini API error: {str(e)}")
            raise Exception(f"Gemini API error: {str(e)}")

    def generate(self, prompt: str) -> str:
        try:
            app_logger.info(f"Calling Gemini API with custom prompt ({self.model_name})")
            response = self.model.generate_content(prompt)
            content = response.text
            app_logger.info("Gemini API call successful")
            return content
        except Exception as e:
            app_logger.error(f"Gemini API error: {str(e)}")
            raise Exception(f"Gemini API error: {str(e)}")


class ClaudeProvider(AIProvider):
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = Config.CLAUDE_MODEL
        app_logger.info(f"Claude provider initialized with model: {self.model}")

    def _validate_score_response(self, parsed_response: Dict[str, Any]) -> None:
        """
        Validate that Claude's score_and_tailor_resume response contains all required fields.
        
        Args:
            parsed_response: The parsed JSON response from Claude API
            
        Raises:
            IncompleteClaudeResponseError: If any required keys are missing
        """
        required_keys = ['original_score', 'tailored_resume', 'tailored_score']
        missing_keys = [key for key in required_keys if key not in parsed_response]
        
        if missing_keys:
            available_keys = list(parsed_response.keys())
            app_logger.error(f"Missing required keys in Claude response: {missing_keys}")
            app_logger.error(f"Available keys: {available_keys}")
            raise IncompleteClaudeResponseError(
                f"Claude API returned incomplete response. Missing keys: {missing_keys}. "
                f"Available keys: {available_keys}"
            )

    def score_and_tailor_resume(self, resume_text: str, job_description: str, custom_prompt: Optional[str] = None, similarity_score: Optional[float] = None) -> Dict[str, Any]:
        try:
            app_logger.info(f"Calling Claude API for score and tailor ({self.model})")
            prompt = self._create_score_and_tailor_prompt(resume_text, job_description, custom_prompt, similarity_score)
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            content = response.content[0].text
            app_logger.info("Claude API call successful")
            app_logger.debug(f"Claude response content (first 500 chars): {content[:500]}")
            
            try:
                parsed_response = self._parse_json_response(content)
                app_logger.debug(f"Parsed response keys: {parsed_response.keys()}")
            except (json.JSONDecodeError, ValueError) as parse_error:
                app_logger.error(f"Failed to parse Claude response: {parse_error}")
                raise IncompleteClaudeResponseError(
                    f"Claude API returned invalid or unparseable response: {str(parse_error)}"
                ) from parse_error
            
            # Validate required keys using extracted method
            try:
                self._validate_score_response(parsed_response)
            except IncompleteClaudeResponseError as validation_error:
                # Re-raise with full context
                raise validation_error
            
            return parsed_response
        except IncompleteClaudeResponseError:
            # Re-raise our custom exceptions without wrapping
            raise
        except Exception as e:
            app_logger.error(f"Claude API error: {str(e)}")
            raise Exception(f"Claude API error: {str(e)}")

    def tailor_resume(self, resume_text: str, job_description: str, custom_prompt: Optional[str] = None) -> str:
        try:
            app_logger.info(f"Calling Claude API ({self.model})")
            prompt = self._create_prompt(resume_text, job_description, custom_prompt)
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            content = response.content[0].text
            app_logger.info("Claude API call successful")
            return content
        except Exception as e:
            app_logger.error(f"Claude API error: {str(e)}")
            raise Exception(f"Claude API error: {str(e)}")

    def generate(self, prompt: str) -> str:
        try:
            app_logger.info(f"Calling Claude API with custom prompt ({self.model})")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            content_block = response.content[0]
            content = content_block.text if hasattr(content_block, 'text') else str(content_block)
            app_logger.info("Claude API call successful")
            return content
        except Exception as e:
            app_logger.error(f"Claude API error: {str(e)}")
            raise Exception(f"Claude API error: {str(e)}")


class AIService:
    @staticmethod
    def get_provider(provider_name: str, api_key: str) -> Optional[AIProvider]:
        """Factory method to get appropriate AI provider"""
        providers = {
            'openai': OpenAIProvider,
            'gemini': GeminiProvider,
            'claude': ClaudeProvider
        }

        provider_class = providers.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"Unknown provider: {provider_name}")

        if not api_key:
            raise ValueError(f"API key not found for {provider_name}")

        return provider_class(api_key)
