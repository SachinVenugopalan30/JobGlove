import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from services.scoring_service import ScoringService, create_scoring_service

@pytest.mark.unit
class TestScoringService:
    """Test resume scoring service"""

    def test_score_resume_success(self, sample_resume_text, sample_job_description):
        """Test successful resume scoring"""
        mock_provider = Mock()
        mock_provider.generate.return_value = json.dumps({
            'ats_score': 18.0,
            'ats_feedback': 'Good ATS compatibility',
            'content_score': 19.0,
            'content_feedback': 'Strong content',
            'style_score': 23.0,
            'style_feedback': 'Professional style',
            'match_score': 24.0,
            'match_feedback': 'Excellent match',
            'readiness_score': 9.0,
            'readiness_feedback': 'Ready to submit'
        })

        service = ScoringService(mock_provider)
        result = service.score_resume(sample_resume_text, sample_job_description)

        assert result['ats_score'] == 18.0
        assert result['content_score'] == 19.0
        assert result['style_score'] == 23.0
        assert result['match_score'] == 24.0
        assert result['readiness_score'] == 9.0
        assert result['total_score'] == 93.0
        assert 'ats_feedback' in result
        assert 'content_feedback' in result

    def test_score_resume_handles_markdown_fences(self, sample_resume_text, sample_job_description):
        """Test that scoring handles markdown code fences"""
        mock_provider = Mock()
        mock_provider.generate.return_value = """```json
{
    "ats_score": 15.0,
    "ats_feedback": "Test",
    "content_score": 16.0,
    "content_feedback": "Test",
    "style_score": 20.0,
    "style_feedback": "Test",
    "match_score": 21.0,
    "match_feedback": "Test",
    "readiness_score": 8.0,
    "readiness_feedback": "Test"
}
```"""

        service = ScoringService(mock_provider)
        result = service.score_resume(sample_resume_text, sample_job_description)

        assert result['total_score'] == 80.0
        assert result['ats_score'] == 15.0

    def test_score_resume_invalid_json_returns_fallback(self, sample_resume_text, sample_job_description):
        """Test fallback when AI returns invalid JSON"""
        mock_provider = Mock()
        mock_provider.generate.return_value = "This is not valid JSON"

        service = ScoringService(mock_provider)
        result = service.score_resume(sample_resume_text, sample_job_description)

        assert result['total_score'] == 0
        assert 'unavailable' in result['ats_feedback'].lower()

    def test_score_resume_calculates_total(self, sample_resume_text, sample_job_description):
        """Test that total score is calculated correctly"""
        mock_provider = Mock()
        mock_provider.generate.return_value = json.dumps({
            'ats_score': 10.0,
            'ats_feedback': 'Test',
            'content_score': 10.0,
            'content_feedback': 'Test',
            'style_score': 15.0,
            'style_feedback': 'Test',
            'match_score': 20.0,
            'match_feedback': 'Test',
            'readiness_score': 5.0,
            'readiness_feedback': 'Test'
        })

        service = ScoringService(mock_provider)
        result = service.score_resume(sample_resume_text, sample_job_description)

        expected_total = 10.0 + 10.0 + 15.0 + 20.0 + 5.0
        assert result['total_score'] == expected_total

    def test_score_resume_exception_handling(self, sample_resume_text, sample_job_description):
        """Test exception handling during scoring"""
        mock_provider = Mock()
        mock_provider.generate.side_effect = Exception("API Error")

        service = ScoringService(mock_provider)
        result = service.score_resume(sample_resume_text, sample_job_description)

        assert result['total_score'] == 0
        assert 'API Error' in result['ats_feedback']

    @patch('services.scoring_service.AIProvider.create')
    def test_create_scoring_service_openai(self, mock_create):
        """Test creating scoring service with OpenAI"""
        mock_provider = Mock()
        mock_create.return_value = mock_provider

        service = create_scoring_service('openai')

        mock_create.assert_called_once_with('openai')
        assert isinstance(service, ScoringService)

    @patch('services.scoring_service.AIProvider.create')
    def test_create_scoring_service_gemini(self, mock_create):
        """Test creating scoring service with Gemini"""
        mock_provider = Mock()
        mock_create.return_value = mock_provider

        service = create_scoring_service('gemini')

        mock_create.assert_called_once_with('gemini')
        assert isinstance(service, ScoringService)

    @patch('services.scoring_service.AIProvider.create')
    def test_create_scoring_service_claude(self, mock_create):
        """Test creating scoring service with Claude"""
        mock_provider = Mock()
        mock_create.return_value = mock_provider

        service = create_scoring_service('claude')

        mock_create.assert_called_once_with('claude')
        assert isinstance(service, ScoringService)

    def test_scoring_prompt_includes_resume_and_job(self, sample_resume_text, sample_job_description):
        """Test that scoring prompt includes both resume and job description"""
        mock_provider = Mock()
        mock_provider.generate.return_value = json.dumps({
            'ats_score': 15, 'ats_feedback': 'Test',
            'content_score': 15, 'content_feedback': 'Test',
            'style_score': 20, 'style_feedback': 'Test',
            'match_score': 20, 'match_feedback': 'Test',
            'readiness_score': 8, 'readiness_feedback': 'Test'
        })

        service = ScoringService(mock_provider)
        service.score_resume(sample_resume_text, sample_job_description)

        # Check that the prompt was called with content including both texts
        call_args = mock_provider.generate.call_args[0][0]
        assert sample_job_description in call_args
        assert 'Tech Corp' in call_args  # From resume text
