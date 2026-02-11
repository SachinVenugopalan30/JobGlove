import json
from unittest.mock import MagicMock, patch

import pytest

from services.ai_service import AIProvider, ClaudeProvider, GeminiProvider, OpenAIProvider


class TestSystemPromptConstant:
    """Test that the shared system prompt constant exists and is used"""

    def test_system_prompt_constant_exists(self):
        assert hasattr(AIProvider, "SCORE_TAILOR_SYSTEM_PROMPT")
        assert "valid JSON" in AIProvider.SCORE_TAILOR_SYSTEM_PROMPT
        assert "resume writer" in AIProvider.SCORE_TAILOR_SYSTEM_PROMPT

    @patch("services.ai_service.anthropic.Anthropic")
    def test_claude_score_tailor_uses_system_prompt(self, mock_anthropic_class):
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                text='{"original_score":{"total_score":70,"keyword_match_score":70,"relevance_score":70,"ats_score":70,"quality_score":70,"recommendations":[]},"tailored_resume":"text","tailored_score":{"total_score":80,"keyword_match_score":80,"relevance_score":80,"ats_score":80,"quality_score":80}}'
            )
        ]
        mock_client.messages.create.return_value = mock_response

        provider = ClaudeProvider("test-key")
        provider.score_and_tailor_resume("resume", "job desc")

        call_kwargs = mock_client.messages.create.call_args
        assert "system" in call_kwargs.kwargs, "Claude must pass system= parameter"


class TestLowTemperature:
    """Test that score_and_tailor uses low temperature for structured output"""

    @patch("services.ai_service.openai.OpenAI")
    def test_openai_score_tailor_uses_low_temperature(self, mock_openai_class):
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='{"original_score":{"total_score":70,"keyword_match_score":70,"relevance_score":70,"ats_score":70,"quality_score":70,"recommendations":[]},"tailored_resume":"text","tailored_score":{"total_score":80,"keyword_match_score":80,"relevance_score":80,"ats_score":80,"quality_score":80}}'
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAIProvider("test-key")
        provider.score_and_tailor_resume("resume", "job desc")

        call_kwargs = mock_client.chat.completions.create.call_args
        assert call_kwargs.kwargs.get("temperature", 1.0) <= 0.3, (
            f"Expected temperature <= 0.3, got {call_kwargs.kwargs.get('temperature')}"
        )


class TestAIProviderJSONParsing:
    """Test JSON response parsing for all providers"""

    def test_parse_clean_json(self):
        provider = OpenAIProvider("test_key")
        json_str = '{"original_score": {"total_score": 75}, "tailored_resume": "test", "tailored_score": {"total_score": 90}}'
        result = provider._parse_json_response(json_str)

        assert result["original_score"]["total_score"] == 75
        assert result["tailored_score"]["total_score"] == 90
        assert result["tailored_resume"] == "test"

    def test_parse_json_with_markdown_code_blocks(self):
        provider = OpenAIProvider("test_key")
        json_str = '```json\n{"original_score": {"total_score": 75}, "tailored_resume": "test", "tailored_score": {"total_score": 90}}\n```'
        result = provider._parse_json_response(json_str)

        assert result["original_score"]["total_score"] == 75
        assert result["tailored_score"]["total_score"] == 90

    def test_parse_json_with_plain_code_blocks(self):
        provider = OpenAIProvider("test_key")
        json_str = '```\n{"original_score": {"total_score": 75}, "tailored_resume": "test", "tailored_score": {"total_score": 90}}\n```'
        result = provider._parse_json_response(json_str)

        assert result["original_score"]["total_score"] == 75

    def test_parse_invalid_json_raises_error(self):
        provider = OpenAIProvider("test_key")
        json_str = "not valid json at all"

        with pytest.raises(ValueError, match="AI returned invalid JSON"):
            provider._parse_json_response(json_str)

    def test_parse_json_joins_tailored_resume_lines(self):
        """tailored_resume_lines array gets normalized to tailored_resume string"""
        provider = OpenAIProvider("test_key")
        response = json.dumps(
            {
                "original_score": {"total_score": 70},
                "tailored_resume_lines": ["[EDUCATION]", "MIT | Cambridge, MA", "BS CS | 2024"],
                "tailored_score": {"total_score": 80},
            }
        )
        result = provider._parse_json_response(response)
        assert result["tailored_resume"] == "[EDUCATION]\nMIT | Cambridge, MA\nBS CS | 2024"
        assert "tailored_resume_lines" not in result

    def test_parse_json_leaves_tailored_resume_string_untouched(self):
        """If model returns tailored_resume as string, it stays as-is"""
        provider = OpenAIProvider("test_key")
        response = json.dumps(
            {
                "original_score": {"total_score": 70},
                "tailored_resume": "already a string",
                "tailored_score": {"total_score": 80},
            }
        )
        result = provider._parse_json_response(response)
        assert result["tailored_resume"] == "already a string"


class TestOpenAIProviderScoreAndTailor:
    """Test OpenAI provider score_and_tailor_resume method"""

    @patch("services.ai_service.openai.OpenAI")
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
                "recommendations": ["Add more metrics", "Use action verbs"],
            },
            "tailored_resume": "[EDUCATION]\nUniversity | Location\nDegree | 2020",
            "tailored_score": {
                "total_score": 89,
                "keyword_match_score": 92,
                "relevance_score": 88,
                "ats_score": 85,
                "quality_score": 90,
            },
        }

        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = json.dumps(mock_response)
        mock_client.chat.completions.create.return_value = mock_completion

        provider = OpenAIProvider("test_key")
        result = provider.score_and_tailor_resume("resume text", "job description")

        assert result["original_score"]["total_score"] == 72
        assert result["tailored_score"]["total_score"] == 89
        assert len(result["original_score"]["recommendations"]) == 2
        assert "EDUCATION" in result["tailored_resume"]

        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs["model"] == "gpt-4o-mini"
        assert call_args.kwargs["max_tokens"] == 4000
        assert call_args.kwargs["response_format"] == {"type": "json_object"}

    @patch("services.ai_service.openai.OpenAI")
    def test_score_and_tailor_with_custom_prompt(self, mock_openai_class):
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = {
            "original_score": {
                "total_score": 70,
                "keyword_match_score": 65,
                "relevance_score": 75,
                "ats_score": 70,
                "quality_score": 70,
            },
            "tailored_resume": "custom tailored",
            "tailored_score": {
                "total_score": 85,
                "keyword_match_score": 80,
                "relevance_score": 90,
                "ats_score": 85,
                "quality_score": 85,
            },
        }

        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = json.dumps(mock_response)
        mock_client.chat.completions.create.return_value = mock_completion

        provider = OpenAIProvider("test_key")
        result = provider.score_and_tailor_resume("resume", "job", "Focus on leadership")

        assert result["tailored_resume"] == "custom tailored"

    @patch("services.ai_service.openai.OpenAI")
    def test_score_and_tailor_api_error(self, mock_openai_class):
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        provider = OpenAIProvider("test_key")

        with pytest.raises(Exception, match="OpenAI API error"):
            provider.score_and_tailor_resume("resume", "job")


class TestGeminiProviderScoreAndTailor:
    """Test Gemini provider score_and_tailor_resume method"""

    @patch("services.ai_service.genai.Client")
    def test_score_and_tailor_success(self, mock_client_class):
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_response = {
            "original_score": {
                "total_score": 70,
                "keyword_match_score": 65,
                "relevance_score": 72,
                "ats_score": 75,
                "quality_score": 68,
                "recommendations": ["Quantify achievements"],
            },
            "tailored_resume": "[EXPERIENCE]\nCompany | Location\nRole | 2020-2023",
            "tailored_score": {
                "total_score": 88,
                "keyword_match_score": 90,
                "relevance_score": 87,
                "ats_score": 86,
                "quality_score": 89,
            },
        }

        mock_result = MagicMock()
        mock_result.text = json.dumps(mock_response)
        mock_client.models.generate_content.return_value = mock_result

        provider = GeminiProvider("test_key")
        result = provider.score_and_tailor_resume("resume text", "job description")

        assert result["original_score"]["total_score"] == 70
        assert result["tailored_score"]["total_score"] == 88
        assert "EXPERIENCE" in result["tailored_resume"]

        mock_client.models.generate_content.assert_called_once()

    @patch("services.ai_service.genai.Client")
    def test_score_and_tailor_api_error(self, mock_client_class):
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception("Gemini API Error")

        provider = GeminiProvider("test_key")

        with pytest.raises(Exception, match="Gemini API error"):
            provider.score_and_tailor_resume("resume", "job")


class TestClaudeProviderScoreAndTailor:
    """Test Claude provider score_and_tailor_resume method"""

    @patch("services.ai_service.anthropic.Anthropic")
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
                "recommendations": ["Add certifications", "Include metrics"],
            },
            "tailored_resume": "[SKILLS]\nProgramming: Python, Java\nFrameworks: React, Django",
            "tailored_score": {
                "total_score": 91,
                "keyword_match_score": 95,
                "relevance_score": 90,
                "ats_score": 88,
                "quality_score": 92,
            },
        }

        mock_message = MagicMock()
        mock_content = MagicMock()
        mock_content.text = json.dumps(mock_response)
        mock_message.content = [mock_content]
        mock_client.messages.create.return_value = mock_message

        provider = ClaudeProvider("test_key")
        result = provider.score_and_tailor_resume("resume text", "job description")

        assert result["original_score"]["total_score"] == 75
        assert result["tailored_score"]["total_score"] == 91
        assert "SKILLS" in result["tailored_resume"]
        assert len(result["original_score"]["recommendations"]) == 2

        mock_client.messages.create.assert_called_once()
        call_args = mock_client.messages.create.call_args
        assert call_args.kwargs["model"] == "claude-haiku-4-5-20251001"
        assert call_args.kwargs["max_tokens"] == 4000

    @patch("services.ai_service.anthropic.Anthropic")
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
        assert "tailored_resume" in prompt or "tailored_resume_lines" in prompt
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
        assert "Return ONLY raw JSON" in prompt
