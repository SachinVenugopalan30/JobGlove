import pytest
from datetime import datetime
from database.db import Resume, ResumeVersion, Score, ReviewBullet

@pytest.mark.unit
class TestDatabaseModels:
    """Test database models and operations"""

    def test_create_resume(self, db_session):
        """Test creating a resume record"""
        resume = Resume(
            user_name='John Doe',
            company='Tech Corp',
            job_title='Software Engineer',
            original_file_path='/path/to/file.docx',
            job_description='Sample job description',
            selected_api='openai',
            custom_prompt=None
        )
        db_session.add(resume)
        db_session.commit()

        assert resume.id is not None
        assert resume.user_name == 'John Doe'
        assert resume.company == 'Tech Corp'
        assert resume.job_title == 'Software Engineer'
        assert resume.created_at is not None

    def test_resume_to_dict(self, db_session):
        """Test resume serialization"""
        resume = Resume(
            user_name='Jane Smith',
            company='StartupXYZ',
            job_title='Senior Developer',
            job_description='Job description',
            selected_api='claude'
        )
        db_session.add(resume)
        db_session.commit()

        resume_dict = resume.to_dict()
        assert resume_dict['user_name'] == 'Jane Smith'
        assert resume_dict['company'] == 'StartupXYZ'
        assert resume_dict['job_title'] == 'Senior Developer'
        assert 'id' in resume_dict
        assert 'created_at' in resume_dict

    def test_resume_versions_relationship(self, db_session):
        """Test resume-versions relationship"""
        resume = Resume(
            user_name='Test User',
            company='Test Co',
            job_title='Test Role',
            job_description='Test description',
            selected_api='gemini'
        )
        db_session.add(resume)
        db_session.flush()

        version1 = ResumeVersion(
            resume_id=resume.id,
            pdf_path='/path/to/file.pdf',
            tex_path='/path/to/file.tex',
            version_type='original'
        )
        version2 = ResumeVersion(
            resume_id=resume.id,
            pdf_path='/path/to/tailored.pdf',
            tex_path='/path/to/tailored.tex',
            version_type='tailored'
        )
        db_session.add_all([version1, version2])
        db_session.commit()

        assert len(resume.versions) == 2
        assert resume.versions[0].version_type == 'original'
        assert resume.versions[1].version_type == 'tailored'

    def test_create_score(self, db_session):
        """Test creating a score record"""
        resume = Resume(
            user_name='Test User',
            company='Test Co',
            job_title='Test Role',
            job_description='Test description',
            selected_api='openai'
        )
        db_session.add(resume)
        db_session.flush()

        score = Score(
            resume_id=resume.id,
            version_type='tailored',
            ats_score=18.5,
            content_score=19.0,
            style_score=23.5,
            match_score=24.0,
            readiness_score=9.0,
            total_score=94.0,
            ats_feedback='Excellent formatting',
            content_feedback='Strong achievements',
            style_feedback='Professional writing',
            match_feedback='Perfect fit',
            readiness_feedback='Ready to submit'
        )
        db_session.add(score)
        db_session.commit()

        assert score.id is not None
        assert score.total_score == 94.0
        assert score.ats_score == 18.5
        assert score.created_at is not None

    def test_score_to_dict(self, db_session):
        """Test score serialization"""
        resume = Resume(
            user_name='Test',
            company='Test',
            job_title='Test',
            job_description='Test',
            selected_api='openai'
        )
        db_session.add(resume)
        db_session.flush()

        score = Score(
            resume_id=resume.id,
            version_type='original',
            ats_score=15.0,
            content_score=16.0,
            style_score=20.0,
            match_score=18.0,
            readiness_score=7.0,
            total_score=76.0
        )
        db_session.add(score)
        db_session.commit()

        score_dict = score.to_dict()
        assert score_dict['total_score'] == 76.0
        assert score_dict['version_type'] == 'original'
        assert 'created_at' in score_dict

    def test_create_review_bullet(self, db_session):
        """Test creating a review bullet"""
        resume = Resume(
            user_name='Test',
            company='Test',
            job_title='Test',
            job_description='Test',
            selected_api='claude'
        )
        db_session.add(resume)
        db_session.flush()

        bullet = ReviewBullet(
            resume_id=resume.id,
            section='Experience',
            original_text='Improved performance by 50%',
            strengths='Quantifies achievement',
            refinement_suggestions='Add specific metrics',
            relevance_score=4
        )
        db_session.add(bullet)
        db_session.commit()

        assert bullet.id is not None
        assert bullet.section == 'Experience'
        assert bullet.relevance_score == 4

    def test_resume_cascade_delete(self, db_session):
        """Test cascade delete of related records"""
        resume = Resume(
            user_name='Test',
            company='Test',
            job_title='Test',
            job_description='Test',
            selected_api='openai'
        )
        db_session.add(resume)
        db_session.flush()

        version = ResumeVersion(
            resume_id=resume.id,
            pdf_path='/test.pdf',
            tex_path='/test.tex',
            version_type='tailored'
        )
        score = Score(
            resume_id=resume.id,
            version_type='tailored',
            ats_score=15, content_score=15, style_score=20,
            match_score=20, readiness_score=8, total_score=78
        )
        bullet = ReviewBullet(
            resume_id=resume.id,
            section='Test',
            original_text='Test',
            strengths='Test',
            refinement_suggestions='Test',
            relevance_score=3
        )
        db_session.add_all([version, score, bullet])
        db_session.commit()

        resume_id = resume.id

        db_session.delete(resume)
        db_session.commit()

        assert db_session.query(ResumeVersion).filter_by(resume_id=resume_id).count() == 0
        assert db_session.query(Score).filter_by(resume_id=resume_id).count() == 0
        assert db_session.query(ReviewBullet).filter_by(resume_id=resume_id).count() == 0
