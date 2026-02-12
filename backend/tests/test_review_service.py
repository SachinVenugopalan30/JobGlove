import json
from unittest.mock import Mock, patch

import pytest

from services.review_service import ReviewService, create_review_service


@pytest.mark.unit
class TestReviewService:
    """Test resume review service"""

    def test_review_resume_success(self, sample_resume_text, sample_job_description):
        """Test successful resume review"""
        mock_provider = Mock()
        mock_provider.generate.return_value = json.dumps({
            'bullets': [
                {
                    'section': 'Experience',
                    'original_text': 'Developed scalable microservices',
                    'strengths': 'Uses strong action verb',
                    'refinement_suggestions': 'Add specific metrics',
                    'relevance_score': 4
                },
                {
                    'section': 'Skills',
                    'original_text': 'Python, JavaScript, React',
                    'strengths': 'Relevant technologies',
                    'refinement_suggestions': 'Organize by category',
                    'relevance_score': 5
                }
            ]
        })

        service = ReviewService(mock_provider)
        result = service.review_resume(sample_resume_text, sample_job_description)

        assert len(result) == 2
        assert result[0]['section'] == 'Experience'
        assert result[0]['relevance_score'] == 4
        assert result[1]['section'] == 'Skills'
        assert result[1]['relevance_score'] == 5

    def test_review_resume_handles_markdown(self, sample_resume_text, sample_job_description):
        """Test review handles markdown code fences"""
        mock_provider = Mock()
        mock_provider.generate.return_value = """```json
{
    "bullets": [
        {
            "section": "Test",
            "original_text": "Test bullet",
            "strengths": "Test strength",
            "refinement_suggestions": "Test suggestion",
            "relevance_score": 3
        }
    ]
}
```"""

        service = ReviewService(mock_provider)
        result = service.review_resume(sample_resume_text, sample_job_description)

        assert len(result) == 1
        assert result[0]['section'] == 'Test'

    def test_review_resume_invalid_json_uses_fallback(self, sample_resume_text, sample_job_description):
        """Test fallback extraction when AI returns invalid JSON"""
        mock_provider = Mock()
        mock_provider.generate.return_value = "Invalid JSON response"

        service = ReviewService(mock_provider)
        result = service.review_resume(sample_resume_text, sample_job_description)

        # Should extract bullets from the resume text using fallback
        assert len(result) > 0
        assert all('section' in bullet for bullet in result)
        assert all('original_text' in bullet for bullet in result)

    def test_review_resume_exception_uses_fallback(self, sample_resume_text, sample_job_description):
        """Test fallback when exception occurs"""
        mock_provider = Mock()
        mock_provider.generate.side_effect = Exception("API Error")

        service = ReviewService(mock_provider)
        result = service.review_resume(sample_resume_text, sample_job_description)

        # Should still return something using fallback
        assert isinstance(result, list)
        assert len(result) > 0

    def test_review_fallback_extracts_bullets(self):
        """Test fallback bullet extraction"""
        resume_text = """
[EXPERIENCE]
Tech Corp | San Francisco
Software Engineer | 2023-Present
- Developed scalable applications
- Improved performance by 50%

[SKILLS]
- Python
- JavaScript
"""
        service = ReviewService(Mock())
        result = service._extract_bullets_fallback(resume_text)

        # Should find the bullets
        assert len(result) >= 4
        assert any('Developed scalable applications' in b['original_text'] for b in result)
        assert any('Python' in b['original_text'] for b in result)

    def test_review_fallback_identifies_sections(self):
        """Test fallback correctly identifies sections"""
        resume_text = """
[EDUCATION]
University Name

[EXPERIENCE]
- First bullet
- Second bullet

[PROJECTS]
- Project bullet
"""
        service = ReviewService(Mock())
        result = service._extract_bullets_fallback(resume_text)

        [b for b in result if b['section'] == 'Education']
        experience_bullets = [b for b in result if b['section'] == 'Experience']
        project_bullets = [b for b in result if b['section'] == 'Projects']

        assert len(experience_bullets) == 2
        assert len(project_bullets) == 1

    def test_review_fallback_handles_empty_resume(self):
        """Test fallback handles empty or invalid resume"""
        service = ReviewService(Mock())
        result = service._extract_bullets_fallback("")

        # Should return at least one placeholder bullet
        assert len(result) >= 1
        assert 'Unable to parse' in result[0]['original_text']

    @patch('services.review_service.AIProvider.create')
    def test_create_review_service(self, mock_create):
        """Test creating review service"""
        mock_provider = Mock()
        mock_create.return_value = mock_provider

        service = create_review_service('claude')

        mock_create.assert_called_once_with('claude')
        assert isinstance(service, ReviewService)

    def test_review_prompt_includes_resume_and_job(self, sample_resume_text, sample_job_description):
        """Test that review prompt includes both resume and job description"""
        mock_provider = Mock()
        mock_provider.generate.return_value = json.dumps({'bullets': []})

        service = ReviewService(mock_provider)
        service.review_resume(sample_resume_text, sample_job_description)

        call_args = mock_provider.generate.call_args[0][0]
        assert sample_job_description in call_args
        assert 'Tech Corp' in call_args

    def test_review_all_bullets_have_required_fields(self, sample_resume_text, sample_job_description):
        """Test that all bullets have required fields"""
        mock_provider = Mock()
        mock_provider.generate.return_value = json.dumps({
            'bullets': [
                {
                    'section': 'Test',
                    'original_text': 'Test text',
                    'strengths': 'Test strength',
                    'refinement_suggestions': 'Test suggestion',
                    'relevance_score': 4
                }
            ]
        })

        service = ReviewService(mock_provider)
        result = service.review_resume(sample_resume_text, sample_job_description)

        for bullet in result:
            assert 'section' in bullet
            assert 'original_text' in bullet
            assert 'strengths' in bullet
            assert 'refinement_suggestions' in bullet
            assert 'relevance_score' in bullet
