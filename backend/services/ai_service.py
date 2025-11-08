from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import json
import openai
import google.generativeai as genai
import anthropic
from utils.logger import app_logger
from config import Config

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
    def score_and_tailor_resume(self, resume_text: str, job_description: str, custom_prompt: Optional[str] = None) -> Dict[str, Any]:
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



    def _create_score_and_tailor_prompt(self, resume_text: str, job_description: str, custom_prompt: Optional[str] = None) -> str:
        """Create prompt for scoring and tailoring in single request"""
        base_instructions = custom_prompt if custom_prompt else ""

        return f"""You are an expert resume writer and analyst. 

CRITICAL INSTRUCTION: You MUST follow the exact formatting rules specified below. Pay special attention to the EXPERIENCE section format.

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
Use this EXACT format for the tailored_resume text. Follow these formatting rules STRICTLY:

[EDUCATION]
School Name | Location
Degree Title | Graduation Date
(Repeat for each education entry)

[EXPERIENCE]
CRITICAL: Each job entry MUST follow this EXACT 2-line format:
Line 1: Company Name | Location
Line 2: Job Title | Start Date - End Date
Then bullet points starting with "-"

CORRECT Example:
Company Name | Location, Country
Role | Month 2023 - Month 2025
- Enhanced operational efficiency by 14% through predictive model deployment
- Reduced costs by 10% using Random Forest and Clustering algorithms

WRONG Example (DO NOT DO THIS):
Role | Company | Location, Country | Month 2023 - Month 2025

WRONG Example (DO NOT DO THIS):
Role | Company | Location, Country
Month 2023 - Month 2025

DO NOT put all information on one line with 4 pipe separators.
DO NOT put the date on a separate third line.
ALWAYS use exactly 2 lines: "Company | Location" then "Title | Date".

(Repeat for each job)

[SKILLS]
Category Name: skill1, skill2, skill3, skill4
Category Name: skill1, skill2, skill3, skill4
(Use categories like: Programming Languages, Frameworks, Tools, etc.)

[PROJECTS] (if applicable)
Project Name | Tech Stack
Date Range
- Bullet point describing the project
- Bullet point describing the project
(Repeat for each project)

REQUIREMENTS:
1. Emphasize skills and experiences most relevant to the job description
2. All bullet points should follow the "Accomplished X through Y using Z" template
3. Keep original achievements but reframe them to align with the target role
4. Use action verbs and quantify achievements where possible. Try and not repeat the same action verbs as much as possible.
5. Use plain text only - DO NOT escape special characters (%, &, $, #, etc.)
6. Maintain professional tone and consistency in tense
{f"7. {base_instructions}" if base_instructions else ""}

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

        return f"""You are an expert resume writer. Tailor the following resume to match the job description provided.

Analyze the job description and rewrite the resume to emphasize relevant skills and experiences. Use the following structured format:

FORMAT YOUR RESPONSE EXACTLY AS FOLLOWS:

[EDUCATION]
School Name | Location
Degree Title | Graduation Date
(Repeat for each education entry)

[EXPERIENCE]
Company Name | Location
Job Title | Start Date - End Date
- Bullet point describing achievement/responsibility
- Bullet point describing achievement/responsibility
- Bullet point describing achievement/responsibility
(Repeat for each job)

[SKILLS]
Category Name: skill1, skill2, skill3, skill4
Category Name: skill1, skill2, skill3, skill4
(Use categories like: Programming Languages, Frameworks, Tools, etc.)

[PROJECTS] (if applicable)
Project Name | Tech Stack
Date Range
- Bullet point describing the project
- Bullet point describing the project
(Repeat for each project)

REQUIREMENTS:
1. Emphasize skills and experiences most relevant to the job description
2. Ensure that all bullet points follow the Accomplished X through Y using Z template
3. Keep original achievements but reframe them to align with the target role
4. Maintain professional tone and quantify achievements where possible, but do not create your own metrics and achievements
5. Use action verbs and specific metrics
6. Ensure consistency in tense (past tense for previous roles, present for current)
7. Use plain text only - DO NOT escape special characters like %, &, $, #, etc. The system will handle escaping automatically

Original Resume:
{resume_text}

Job Description:
{job_description}

CRITICAL: Output ONLY the structured resume content following the exact format above.
- Do NOT include explanations, comments, or markdown formatting
- Do NOT escape special characters (no backslashes, no LaTeX commands)
- Use plain text with normal symbols: %, &, $, #, etc."""


class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = Config.OPENAI_MODEL
        app_logger.info(f"OpenAI provider initialized with model: {self.model}")

    def score_and_tailor_resume(self, resume_text: str, job_description: str, custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        try:
            app_logger.info(f"Calling OpenAI API for score and tailor ({self.model})")
            prompt = self._create_score_and_tailor_prompt(resume_text, job_description, custom_prompt)
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

    def score_and_tailor_resume(self, resume_text: str, job_description: str, custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        try:
            app_logger.info(f"Calling Gemini API for score and tailor ({self.model_name})")
            prompt = self._create_score_and_tailor_prompt(resume_text, job_description, custom_prompt)
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

    def score_and_tailor_resume(self, resume_text: str, job_description: str, custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        try:
            app_logger.info(f"Calling Claude API for score and tailor ({self.model})")
            prompt = self._create_score_and_tailor_prompt(resume_text, job_description, custom_prompt)
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
            parsed_response = self._parse_json_response(content)
            app_logger.debug(f"Parsed response keys: {parsed_response.keys()}")
            
            # Validate required keys
            required_keys = ['original_score', 'tailored_resume', 'tailored_score']
            missing_keys = [key for key in required_keys if key not in parsed_response]
            if missing_keys:
                app_logger.error(f"Missing required keys in Claude response: {missing_keys}")
                app_logger.error(f"Available keys: {list(parsed_response.keys())}")
                raise ValueError(f"Claude API returned incomplete response. Missing: {missing_keys}")
            
            return parsed_response
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
