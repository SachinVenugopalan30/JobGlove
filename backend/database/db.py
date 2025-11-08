from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from datetime import datetime
import os

Base = declarative_base()

class Resume(Base):
    __tablename__ = 'resumes'

    id = Column(Integer, primary_key=True)
    user_name = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    job_title = Column(String(255), nullable=False)
    original_file_path = Column(String(512), nullable=True)
    job_description = Column(Text, nullable=False)
    selected_api = Column(String(50), nullable=False)
    custom_prompt = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    versions = relationship('ResumeVersion', back_populates='resume', cascade='all, delete-orphan')
    scores = relationship('Score', back_populates='resume', cascade='all, delete-orphan')
    review_bullets = relationship('ReviewBullet', back_populates='resume', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_name': self.user_name,
            'company': self.company,
            'job_title': self.job_title,
            'original_file_path': self.original_file_path,
            'job_description': self.job_description,
            'selected_api': self.selected_api,
            'custom_prompt': self.custom_prompt,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ResumeVersion(Base):
    __tablename__ = 'resume_versions'

    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer, ForeignKey('resumes.id'), nullable=False)
    pdf_path = Column(String(512), nullable=False)
    tex_path = Column(String(512), nullable=False)
    version_type = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    resume = relationship('Resume', back_populates='versions')

    def to_dict(self):
        return {
            'id': self.id,
            'resume_id': self.resume_id,
            'pdf_path': self.pdf_path,
            'tex_path': self.tex_path,
            'version_type': self.version_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Score(Base):
    __tablename__ = 'scores'

    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer, ForeignKey('resumes.id'), nullable=False)
    version_type = Column(String(50), nullable=False)
    ats_score = Column(Float, nullable=False)
    content_score = Column(Float, nullable=False)
    style_score = Column(Float, nullable=False)
    match_score = Column(Float, nullable=False)
    readiness_score = Column(Float, nullable=False)
    total_score = Column(Float, nullable=False)
    ats_feedback = Column(Text, nullable=True)
    content_feedback = Column(Text, nullable=True)
    style_feedback = Column(Text, nullable=True)
    match_feedback = Column(Text, nullable=True)
    readiness_feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    resume = relationship('Resume', back_populates='scores')

    def to_dict(self):
        return {
            'id': self.id,
            'resume_id': self.resume_id,
            'version_type': self.version_type,
            'ats_score': self.ats_score,
            'content_score': self.content_score,
            'style_score': self.style_score,
            'match_score': self.match_score,
            'readiness_score': self.readiness_score,
            'total_score': self.total_score,
            'ats_feedback': self.ats_feedback,
            'content_feedback': self.content_feedback,
            'style_feedback': self.style_feedback,
            'match_feedback': self.match_feedback,
            'readiness_feedback': self.readiness_feedback,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ReviewBullet(Base):
    __tablename__ = 'review_bullets'

    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer, ForeignKey('resumes.id'), nullable=False)
    section = Column(String(100), nullable=False)
    original_text = Column(Text, nullable=False)
    strengths = Column(Text, nullable=True)
    refinement_suggestions = Column(Text, nullable=True)
    relevance_score = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    resume = relationship('Resume', back_populates='review_bullets')

    def to_dict(self):
        return {
            'id': self.id,
            'resume_id': self.resume_id,
            'section': self.section,
            'original_text': self.original_text,
            'strengths': self.strengths,
            'refinement_suggestions': self.refinement_suggestions,
            'relevance_score': self.relevance_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'jobglove.db')
engine = create_engine(f'sqlite:///{db_path}', echo=False)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

db = Session()

def init_db():
    Base.metadata.create_all(engine)
    print(f"Database initialized at {db_path}")

def get_session():
    return Session()
