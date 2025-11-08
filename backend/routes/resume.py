import os
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from datetime import datetime

from config import Config
from services.document_parser import DocumentParser
from services.ai_service import AIService
from services.latex_generator import LaTeXGenerator
from services.scoring_service import create_scoring_service
from services.review_service import create_review_service
from database.db import get_session, Resume, ResumeVersion, Score, ReviewBullet
from utils.logger import app_logger

resume_bp = Blueprint('resume', __name__)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


@resume_bp.route('/check-apis', methods=['GET'])
def check_apis():
    """Check which API keys are available"""
    try:
        available_apis = Config.check_api_availability()
        return jsonify({
            **available_apis,
            'default_user_name': Config.DEFAULT_USER_NAME
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@resume_bp.route('/upload-resume', methods=['POST'])
def upload_resume():
    """Handle resume file upload"""
    try:
        if 'file' not in request.files:
            app_logger.warning("Upload attempt with no file provided")
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            app_logger.warning("Upload attempt with empty filename")
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            app_logger.warning(f"Invalid file type uploaded: {file.filename}")
            return jsonify({'error': 'Invalid file type. Only DOCX, DOC, and PDF files are allowed'}), 400

        filename = secure_filename(file.filename)
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(file_path)
        app_logger.info(f"File uploaded successfully: {filename}")

        # Validate file size
        if not DocumentParser.validate_file(file_path, Config.MAX_FILE_SIZE):
            os.remove(file_path)
            app_logger.warning(f"File too large and removed: {filename}")
            return jsonify({'error': 'File is too large'}), 400

        return jsonify({'file_path': file_path, 'filename': filename}), 200

    except Exception as e:
        app_logger.error(f"Error uploading resume: {str(e)}")
        return jsonify({'error': str(e)}), 500


@resume_bp.route('/tailor-resume', methods=['POST'])
def tailor_resume():
    """Tailor resume using selected AI API"""
    try:
        data = request.json

        file_path = data.get('file_path')
        job_description = data.get('job_description')
        selected_api = data.get('api')
        user_name = data.get('user_name', Config.DEFAULT_USER_NAME)
        company = data.get('company', 'Unknown')
        job_title = data.get('job_title', 'Unknown')
        custom_prompt = data.get('custom_prompt')

        if not file_path or not job_description or not selected_api:
            app_logger.warning("Tailor request missing required fields")
            return jsonify({'error': 'Missing required fields'}), 400

        app_logger.info(f"Starting resume tailoring for {user_name} - {company} - {job_title} with {selected_api} API")

        # Parse resume using DocumentParser (supports PDF and DOCX)
        resume_text = DocumentParser.extract_text(file_path)

        if not resume_text or len(resume_text.strip()) < 50:
            app_logger.error(f"Failed to extract text from resume: {file_path}")
            return jsonify({'error': 'Failed to extract text from resume'}), 400

        # Store original resume text for scoring
        original_resume_text = resume_text
        app_logger.info(f"Extracted {len(resume_text)} characters from resume")

        # Extract header from original resume (keep it private)
        header = DocumentParser.extract_header(resume_text)
        app_logger.info(f"Extracted header from resume (length: {len(header)} chars)")

        # Remove header from resume before sending to AI (privacy protection)
        resume_without_header = DocumentParser.remove_header(resume_text)
        app_logger.info(f"Removed header for privacy. Resume length: {len(resume_without_header)} chars")

        # Get appropriate API key
        api_keys = {
            'openai': Config.OPENAI_API_KEY,
            'gemini': Config.GEMINI_API_KEY,
            'claude': Config.ANTHROPIC_API_KEY
        }

        api_key = api_keys.get(selected_api)
        if not api_key:
            app_logger.error(f"API key not configured for {selected_api}")
            return jsonify({'error': f'API key not configured for {selected_api}'}), 400

        # Score and tailor resume using AI in single request
        app_logger.info(f"Sending resume to {selected_api} API for scoring and tailoring")
        ai_provider = AIService.get_provider(selected_api, api_key)
        ai_response = ai_provider.score_and_tailor_resume(resume_without_header, job_description, custom_prompt)

        original_score = ai_response['original_score']
        tailored_resume = ai_response['tailored_resume']
        tailored_score = ai_response['tailored_score']

        app_logger.info(f"AI scoring complete - Original: {original_score['total_score']}/100, Tailored: {tailored_score['total_score']}/100")
        app_logger.info(f"Received tailored resume from AI (length: {len(tailored_resume)} chars)")

        # Prepend original header back to AI response
        complete_resume = header + "\n" + tailored_resume
        app_logger.info(f"Combined header with tailored resume (total length: {len(complete_resume)} chars)")

        # Generate PDF
        template_path = os.path.join(Config.TEMPLATES_FOLDER, 'resume_template.tex')
        app_logger.info("Starting LaTeX PDF generation")
        pdf_path, tex_path = LaTeXGenerator.generate_latex(complete_resume, template_path, Config.OUTPUT_FOLDER, user_name, company, job_title)
        app_logger.info(f"PDF generated successfully: {os.path.basename(pdf_path)}")

        # Save to database
        session = get_session()
        try:
            resume_record = Resume(
                user_name=user_name,
                company=company,
                job_title=job_title,
                original_file_path=file_path,
                job_description=job_description,
                selected_api=selected_api,
                custom_prompt=custom_prompt
            )
            session.add(resume_record)
            session.flush()

            version = ResumeVersion(
                resume_id=resume_record.id,
                pdf_path=pdf_path,
                tex_path=tex_path,
                version_type='tailored'
            )
            session.add(version)
            session.commit()
            app_logger.info(f"Resume saved to database with ID: {resume_record.id}")

        except Exception as e:
            session.rollback()
            app_logger.error(f"Failed to save to database: {str(e)}")
        finally:
            session.close()

        # Clean up uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)
            app_logger.info("Cleaned up uploaded resume file")

        return jsonify({
            'pdf_file': os.path.basename(pdf_path),
            'tex_file': os.path.basename(tex_path),
            'original_text': original_resume_text,
            'tailored_text': complete_resume,
            'original_score': original_score,
            'tailored_score': tailored_score,
            'message': 'Resume tailored successfully'
        }), 200

    except Exception as e:
        app_logger.error(f"Error tailoring resume: {str(e)}")
        return jsonify({'error': str(e)}), 500


@resume_bp.route('/download/<filename>', methods=['GET'])
def download_resume(filename):
    """Download generated PDF or TEX file"""
    try:
        file_path = os.path.join(Config.OUTPUT_FOLDER, filename)

        if not os.path.exists(file_path):
            app_logger.warning(f"Download requested for non-existent file: {filename}")
            return jsonify({'error': 'File not found'}), 404

        # Use the actual filename for download (already contains user/company/job info)
        download_name = filename

        app_logger.info(f"Serving file for download: {filename}")
        return send_file(file_path, as_attachment=True, download_name=download_name)

    except Exception as e:
        app_logger.error(f"Error downloading file: {str(e)}")
        return jsonify({'error': str(e)}), 500


@resume_bp.route('/score', methods=['POST'])
def score_resume():
    """Score a resume against a job description"""
    try:
        data = request.json

        resume_text = data.get('resume_text')
        job_description = data.get('job_description')
        selected_api = data.get('api')

        if not resume_text or not job_description or not selected_api:
            app_logger.warning("Score request missing required fields")
            return jsonify({'error': 'Missing required fields'}), 400

        app_logger.info(f"Starting resume scoring with {selected_api} API")

        scoring_service = create_scoring_service(selected_api)
        scores = scoring_service.score_resume(resume_text, job_description)

        app_logger.info(f"Resume scored: {scores['total_score']}/100")
        return jsonify(scores), 200

    except Exception as e:
        app_logger.error(f"Error scoring resume: {str(e)}")
        return jsonify({'error': str(e)}), 500


@resume_bp.route('/review', methods=['POST'])
def review_resume():
    """Get bullet-by-bullet review of resume"""
    try:
        data = request.json

        resume_text = data.get('resume_text')
        job_description = data.get('job_description')
        selected_api = data.get('api')

        if not resume_text or not job_description or not selected_api:
            app_logger.warning("Review request missing required fields")
            return jsonify({'error': 'Missing required fields'}), 400

        app_logger.info(f"Starting resume review with {selected_api} API")

        review_service = create_review_service(selected_api)
        bullets = review_service.review_resume(resume_text, job_description)

        app_logger.info(f"Resume reviewed: {len(bullets)} bullet points analyzed")
        return jsonify({'bullets': bullets}), 200

    except Exception as e:
        app_logger.error(f"Error reviewing resume: {str(e)}")
        return jsonify({'error': str(e)}), 500


@resume_bp.route('/resumes/history', methods=['GET'])
def get_resume_history():
    """Get all resumes from history"""
    try:
        session = get_session()
        resumes = session.query(Resume).order_by(Resume.created_at.desc()).all()

        history = []
        for resume in resumes:
            latest_score = session.query(Score).filter_by(
                resume_id=resume.id,
                version_type='tailored'
            ).order_by(Score.created_at.desc()).first()

            latest_version = session.query(ResumeVersion).filter_by(
                resume_id=resume.id,
                version_type='tailored'
            ).order_by(ResumeVersion.created_at.desc()).first()

            history.append({
                **resume.to_dict(),
                'latest_score': latest_score.total_score if latest_score else None,
                'pdf_file': os.path.basename(latest_version.pdf_path) if latest_version else None,
                'tex_file': os.path.basename(latest_version.tex_path) if latest_version else None
            })

        app_logger.info(f"Retrieved {len(history)} resumes from history")
        return jsonify({'resumes': history}), 200

    except Exception as e:
        app_logger.error(f"Error retrieving resume history: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@resume_bp.route('/resumes/search', methods=['GET'])
def search_resumes():
    """Search resumes by query"""
    session = None
    try:
        query = request.args.get('q', '').strip()

        if not query:
            return get_resume_history()

        session = get_session()
        resumes = session.query(Resume).filter(
            (Resume.user_name.ilike(f'%{query}%')) |
            (Resume.company.ilike(f'%{query}%')) |
            (Resume.job_title.ilike(f'%{query}%'))
        ).order_by(Resume.created_at.desc()).all()

        results = []
        for resume in resumes:
            latest_score = session.query(Score).filter_by(
                resume_id=resume.id,
                version_type='tailored'
            ).order_by(Score.created_at.desc()).first()

            latest_version = session.query(ResumeVersion).filter_by(
                resume_id=resume.id,
                version_type='tailored'
            ).order_by(ResumeVersion.created_at.desc()).first()

            results.append({
                **resume.to_dict(),
                'latest_score': latest_score.total_score if latest_score else None,
                'pdf_file': os.path.basename(latest_version.pdf_path) if latest_version else None,
                'tex_file': os.path.basename(latest_version.tex_path) if latest_version else None
            })

        app_logger.info(f"Search for '{query}' returned {len(results)} results")
        return jsonify({'resumes': results}), 200

    except Exception as e:
        app_logger.error(f"Error searching resumes: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if session:
            session.close()
