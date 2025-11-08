import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from services.ai_service import OpenAIProvider, GeminiProvider, ClaudeProvider, AIProvider


class TestAIProviderJSONParsing:
    """Test JSON response parsing for all providers"""

    def test_parse_clean_json(self):
        provider = OpenAIProvider("test_key")
        json_str = '{"original_score": {"total_score": 75}, "tailored_resume": "test", "tailored_score": {"total_score": 90}}'
        result = provider._parse_json_response(json_str)

        assert result['original_score']['total_score'] == 75
        assert result['tailored_score']['total_score'] == 90
        assert result['tailored_resume'] == 'test'

    def test_parse_json_with_markdown_code_blocks(self):
        provider = OpenAIProvider("test_key")
        json_str = '```json\n{"original_score": {"total_score": 75}, "tailored_resume": "test", "tailored_score": {"total_score": 90}}\n```'
        result = provider._parse_json_response(json_str)

        assert result['original_score']['total_score'] == 75
        assert result['tailored_score']['total_score'] == 90

    def test_parse_json_with_plain_code_blocks(self):
        provider = OpenAIProvider("test_key")
        json_str = '```\n{"original_score": {"total_score": 75}, "tailored_resume": "test", "tailored_score": {"total_score": 90}}\n```'
        result = provider._parse_json_response(json_str)

        assert result['original_score']['total_score'] == 75

    def test_parse_invalid_json_raises_error(self):
        provider = OpenAIProvider("test_key")
        json_str = 'not valid json at all'

        with pytest.raises(ValueError, match="AI returned invalid JSON"):
            provider._parse_json_response(json_str)


class TestOpenAIProviderScoreAndTailor:
    """Test OpenAI provider score_and_tailor_resume method"""

    @patch('services.ai_service.openai.OpenAI')
    def test_score_and_tailor_success(self, mock_openai_class):
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = {
            "original_score": {
                "total_score": 72,
                "keyword_match_score": 68,
                "relevance_score": 75,
                "ats_score": 80,
                "quality_score": 65,
                "recommendations": ["Add more metrics", "Use action verbs"]
            },
            "tailored_resume": "[EDUCATION]\nUniversity | Location\nDegree | 2020",
            "tailored_score": {
                "total_score": 89,
                "keyword_match_score": 92,
                "relevance_score": 88,
                "ats_score": 85,
                "quality_score": 90
            }
        }

        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = json.dumps(mock_response)
        mock_client.chat.completions.create.return_value = mock_completion

        provider = OpenAIProvider("test_key")
        result = provider.score_and_tailor_resume("resume text", "job description")

        assert result['original_score']['total_score'] == 72
        assert result['tailored_score']['total_score'] == 89
        assert len(result['original_score']['recommendations']) == 2
        assert 'EDUCATION' in result['tailored_resume']

        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs['model'] == 'gpt-4o-mini'
        assert call_args.kwargs['max_tokens'] == 4000
        assert call_args.kwargs['response_format'] == {"type": "json_object"}

    @patch('services.ai_service.openai.OpenAI')
    def test_score_and_tailor_with_custom_prompt(self, mock_openai_class):
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = {
            "original_score": {"total_score": 70, "keyword_match_score": 65, "relevance_score": 75, "ats_score": 70, "quality_score": 70},
            "tailored_resume": "custom tailored",
            "tailored_score": {"total_score": 85, "keyword_match_score": 80, "relevance_score": 90, "ats_score": 85, "quality_score": 85}
        }

        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = json.dumps(mock_response)
        mock_client.chat.completions.create.return_value = mock_completion

        provider = OpenAIProvider("test_key")
        result = provider.score_and_tailor_resume("resume", "job", "Focus on leadership")

        assert result['tailored_resume'] == "custom tailored"

    @patch('services.ai_service.openai.OpenAI')
    def test_score_and_tailor_api_error(self, mock_openai_class):
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        provider = OpenAIProvider("test_key")

        with pytest.raises(Exception, match="OpenAI API error"):
            provider.score_and_tailor_resume("resume", "job")


class TestGeminiProviderScoreAndTailor:
    """Test Gemini provider score_and_tailor_resume method"""

    @patch('services.ai_service.genai.configure')
    @patch('services.ai_service.genai.GenerativeModel')
    def test_score_and_tailor_success(self, mock_model_class, mock_configure):
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model

        mock_response = {
            "original_score": {
                "total_score": 70,
                "keyword_match_score": 65,
                "relevance_score": 72,
                "ats_score": 75,
                "quality_score": 68,
                "recommendations": ["Quantify achievements"]
            },
            "tailored_resume": "[EXPERIENCE]\nCompany | Location\nRole | 2020-2023",
            "tailored_score": {
                "total_score": 88,
                "keyword_match_score": 90,
                "relevance_score": 87,
                "ats_score": 86,
                "quality_score": 89
            }
        }

        mock_result = MagicMock()
        mock_result.text = json.dumps(mock_response)
        mock_model.generate_content.return_value = mock_result

        provider = GeminiProvider("test_key")
        result = provider.score_and_tailor_resume("resume text", "job description")

        assert result['original_score']['total_score'] == 70
        assert result['tailored_score']['total_score'] == 88
        assert 'EXPERIENCE' in result['tailored_resume']

        mock_model.generate_content.assert_called_once()

    @patch('services.ai_service.genai.configure')
    @patch('services.ai_service.genai.GenerativeModel')
    def test_score_and_tailor_api_error(self, mock_model_class, mock_configure):
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        mock_model.generate_content.side_effect = Exception("Gemini API Error")

        provider = GeminiProvider("test_key")

        with pytest.raises(Exception, match="Gemini API error"):
            provider.score_and_tailor_resume("resume", "job")


class TestClaudeProviderScoreAndTailor:
    """Test Claude provider score_and_tailor_resume method"""

    @patch('services.ai_service.anthropic.Anthropic')
    def test_score_and_tailor_success(self, mock_anthropic_class):
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_response = {
            "original_score": {
                "total_score": 75,
                "keyword_match_score": 70,
                "relevance_score": 78,
                "ats_score": 80,
                "quality_score": 72,
                "recommendations": ["Add certifications", "Include metrics"]
            },
            "tailored_resume": "[SKILLS]\nProgramming: Python, Java\nFrameworks: React, Django",
            "tailored_score": {
                "total_score": 91,
                "keyword_match_score": 95,
                "relevance_score": 90,
                "ats_score": 88,
                "quality_score": 92
            }
        }

        mock_message = MagicMock()
        mock_content = MagicMock()
        mock_content.text = json.dumps(mock_response)
        mock_message.content = [mock_content]
        mock_client.messages.create.return_value = mock_message

        provider = ClaudeProvider("test_key")
        result = provider.score_and_tailor_resume("resume text", "job description")

        assert result['original_score']['total_score'] == 75
        assert result['tailored_score']['total_score'] == 91
        assert 'SKILLS' in result['tailored_resume']
        assert len(result['original_score']['recommendations']) == 2

        mock_client.messages.create.assert_called_once()
        call_args = mock_client.messages.create.call_args
        assert call_args.kwargs['model'] == 'claude-3-5-haiku-20241022'
        assert call_args.kwargs['max_tokens'] == 4000

    @patch('services.ai_service.anthropic.Anthropic')
    def test_score_and_tailor_api_error(self, mock_anthropic_class):
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("Claude API Error")

        provider = ClaudeProvider("test_key")

        with pytest.raises(Exception, match="Claude API error"):
            provider.score_and_tailor_resume("resume", "job")


class TestPromptGeneration:
    """Test prompt creation for score_and_tailor"""

    def test_prompt_includes_all_sections(self):
        provider = OpenAIProvider("test_key")
        prompt = provider._create_score_and_tailor_prompt("my resume", "job desc")

        assert "Score the original resume" in prompt
        assert "Tailor the resume" in prompt
        assert "Score the tailored resume" in prompt
        assert "original_score" in prompt
        assert "tailored_resume" in prompt
        assert "tailored_score" in prompt
        assert "keyword_match_score" in prompt
        assert "relevance_score" in prompt
        assert "ats_score" in prompt
        assert "quality_score" in prompt
        assert "my resume" in prompt
        assert "job desc" in prompt

    def test_prompt_includes_custom_instructions(self):
        provider = OpenAIProvider("test_key")
        prompt = provider._create_score_and_tailor_prompt("resume", "job", "Focus on Python skills")

        assert "Focus on Python skills" in prompt

    def test_prompt_includes_json_format(self):
        provider = OpenAIProvider("test_key")
        prompt = provider._create_score_and_tailor_prompt("resume", "job")

        assert "JSON" in prompt or "json" in prompt
        assert "CRITICAL: Return ONLY the JSON object" in prompt
