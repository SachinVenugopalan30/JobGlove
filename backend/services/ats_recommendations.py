"""
ATS Recommendation Engine

Analyzes resume content against job description and generates actionable
recommendations to improve ATS compatibility, following Resume Matcher patterns.
"""

import re

from sklearn.feature_extraction.text import TfidfVectorizer

from utils.logger import app_logger


class ATSRecommendationEngine:
    """
    Generates ATS-focused recommendations by analyzing keyword gaps,
    section presence, and content optimization opportunities.
    """

    def __init__(self):
        """Initialize the ATS recommendation engine"""
        self.stopwords = self._load_stopwords()
        app_logger.info("ATSRecommendationEngine initialized")

    def generate_recommendations(
        self,
        resume_text: str,
        job_description: str,
        embedding_similarity: float = None,
        tfidf_similarity: float = None
    ) -> dict[str, any]:
        """
        Generate comprehensive ATS recommendations.

        Args:
            resume_text: The resume content
            job_description: The job description
            embedding_similarity: Optional embedding-based similarity score
            tfidf_similarity: Optional TF-IDF similarity score

        Returns:
            Dictionary containing recommendations and analysis
        """
        try:
            app_logger.info("Generating ATS recommendations")

            # Extract keywords from job description with resume as context for better TF-IDF
            jd_keywords = self.extract_keywords_with_context(job_description, resume_text, top_n=30)
            resume_keywords = self.extract_keywords(resume_text, top_n=50)

            # Find missing and present keywords
            missing_keywords = self._find_missing_keywords(jd_keywords, resume_keywords, resume_text)
            present_keywords = self._find_present_keywords(jd_keywords, resume_text)

            # Analyze resume structure
            has_summary = self._check_for_summary(resume_text)
            section_analysis = self._analyze_sections(resume_text)

            # Calculate keyword coverage
            keyword_coverage = self._calculate_keyword_coverage(jd_keywords, resume_keywords)

            # Generate specific recommendations
            recommendations = self._generate_specific_recommendations(
                missing_keywords=missing_keywords,
                present_keywords=present_keywords,
                has_summary=has_summary,
                section_analysis=section_analysis,
                keyword_coverage=keyword_coverage,
                embedding_similarity=embedding_similarity,
                tfidf_similarity=tfidf_similarity
            )

            result = {
                'ats_score': self._calculate_ats_score(
                    keyword_coverage,
                    has_summary,
                    section_analysis,
                    embedding_similarity
                ),
                'keyword_coverage': keyword_coverage,
                'missing_keywords': missing_keywords[:10],  # Top 10 most important
                'present_keywords': present_keywords[:10],
                'has_summary_section': has_summary,
                'section_analysis': section_analysis,
                'recommendations': recommendations,
                'keyword_analysis': {
                    'total_jd_keywords': len(jd_keywords),
                    'matched_keywords': len(present_keywords),
                    'missing_count': len(missing_keywords)
                }
            }

            app_logger.info(f"ATS recommendations generated. Score: {result['ats_score']:.2f}")
            return result

        except Exception as e:
            app_logger.error(f"Error generating ATS recommendations: {e}")
            return self._get_fallback_recommendations()

    def extract_keywords(self, text: str, top_n: int = 20) -> list[tuple[str, float]]:
        """
        Extract important keywords using TF-IDF scoring.

        Args:
            text: Input text
            top_n: Number of top keywords to return

        Returns:
            List of (keyword, score) tuples sorted by importance
        """
        try:
            if not text or len(text.strip()) < 10:
                return []

            # Clean text
            cleaned_text = self._preprocess_text(text)

            # Custom stopwords that exclude programming terms and technical skills
            from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
            custom_stop_words = set(ENGLISH_STOP_WORDS) - {
                'python', 'java', 'javascript', 'react', 'node', 'sql', 'system', 'computer', 'data'
            }

            # Use TF-IDF for keyword extraction
            vectorizer = TfidfVectorizer(
                max_features=top_n * 3,
                stop_words=list(custom_stop_words),
                ngram_range=(1, 3),  # Include phrases up to 3 words
                min_df=1,
                token_pattern=r'(?u)\b[a-zA-Z][a-zA-Z+#\.]*[a-zA-Z+#]*\b'  # Keep technical terms like C++, C#
            )

            # Fit and get feature names
            tfidf_matrix = vectorizer.fit_transform([cleaned_text])
            feature_names = vectorizer.get_feature_names_out()

            # Get scores for each keyword
            scores = tfidf_matrix.toarray()[0]

            # Create keyword-score pairs
            keyword_scores = list(zip(feature_names, scores, strict=False))

            # Sort by score and filter technical terms
            keyword_scores = sorted(keyword_scores, key=lambda x: x[1], reverse=True)

            # Filter out single letters and very short words (except known abbreviations)
            known_abbreviations = {'ai', 'ml', 'ci', 'cd', 'ui', 'ux', 'qa', 'api', 'sql', 'aws', 'gcp', 'nlp'}
            keyword_scores = [
                (kw, score) for kw, score in keyword_scores
                if len(kw) > 2 or kw.lower() in known_abbreviations
            ]

            return keyword_scores[:top_n]

        except Exception as e:
            app_logger.error(f"Error extracting keywords: {e}")
            return []

    def extract_keywords_with_context(
        self,
        primary_text: str,
        context_text: str,
        top_n: int = 20
    ) -> list[tuple[str, float]]:
        """
        Extract keywords from primary text using context text for better TF-IDF scoring.
        This makes TF-IDF meaningful by providing a corpus of 2 documents.

        Args:
            primary_text: Text to extract keywords from (e.g., job description)
            context_text: Context text for comparison (e.g., resume)
            top_n: Number of top keywords to return

        Returns:
            List of (keyword, score) tuples from primary_text, sorted by importance
        """
        try:
            if not primary_text or len(primary_text.strip()) < 10:
                return []

            # Clean both texts
            cleaned_primary = self._preprocess_text(primary_text)
            cleaned_context = self._preprocess_text(context_text) if context_text else ""

            # Custom stopwords that exclude programming terms and technical skills
            from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
            custom_stop_words = set(ENGLISH_STOP_WORDS) - {
                'python', 'java', 'javascript', 'react', 'node', 'sql', 'system', 'computer', 'data'
            }

            # Use TF-IDF with both documents for meaningful IDF scores
            vectorizer = TfidfVectorizer(
                max_features=top_n * 3,
                stop_words=list(custom_stop_words),
                ngram_range=(1, 3),  # Include phrases up to 3 words
                min_df=1,
                token_pattern=r'(?u)\b[a-zA-Z][a-zA-Z+#\.]*[a-zA-Z+#]*\b'  # Keep technical terms like C++, C#
            )

            # Fit on both documents (corpus), but we only want keywords from primary
            corpus = [cleaned_primary, cleaned_context] if cleaned_context else [cleaned_primary]
            tfidf_matrix = vectorizer.fit_transform(corpus)
            feature_names = vectorizer.get_feature_names_out()

            # Get scores for primary document (first document, index 0)
            scores = tfidf_matrix.toarray()[0]

            # Create keyword-score pairs
            keyword_scores = list(zip(feature_names, scores, strict=False))

            # Sort by score - higher scores mean more important in primary vs context
            keyword_scores = sorted(keyword_scores, key=lambda x: x[1], reverse=True)

            # Filter out single letters and very short words (except known abbreviations)
            known_abbreviations = {'ai', 'ml', 'ci', 'cd', 'ui', 'ux', 'qa', 'api', 'sql', 'aws', 'gcp', 'nlp'}
            keyword_scores = [
                (kw, score) for kw, score in keyword_scores
                if (len(kw) > 2 or kw.lower() in known_abbreviations) and score > 0
            ]

            return keyword_scores[:top_n]

        except Exception as e:
            app_logger.error(f"Error extracting keywords with context: {e}")
            return []

    def _find_missing_keywords(
        self,
        jd_keywords: list[tuple[str, float]],
        resume_keywords: list[tuple[str, float]],
        resume_text: str
    ) -> list[tuple[str, float]]:
        """Find important keywords from JD that are missing or underrepresented in resume"""
        resume_keyword_set = {kw.lower() for kw, _ in resume_keywords}

        missing = []
        for keyword, score in jd_keywords:
            # Create boundary-aware regex pattern
            escaped_keyword = re.escape(keyword)
            pattern = re.compile(r'\b' + escaped_keyword + r'\b', re.IGNORECASE)

            # Check if keyword appears in resume
            if not pattern.search(resume_text):
                missing.append((keyword, score))
            # Check if it's underrepresented (mentioned but not emphasized)
            elif keyword.lower() not in resume_keyword_set:
                # Count occurrences with boundary-aware matching
                matches = pattern.findall(resume_text)
                count = len(matches)
                if count < 2:  # Appears less than twice
                    missing.append((keyword, score * 0.7))  # Lower priority

        # Sort by score (importance)
        missing = sorted(missing, key=lambda x: x[1], reverse=True)
        return missing

    def _find_present_keywords(
        self,
        jd_keywords: list[tuple[str, float]],
        resume_text: str
    ) -> list[tuple[str, int]]:
        """Find JD keywords that are present in resume with their frequency"""
        present = []

        for keyword, _score in jd_keywords:
            # Create boundary-aware regex pattern
            escaped_keyword = re.escape(keyword)
            pattern = re.compile(r'\b' + escaped_keyword + r'\b', re.IGNORECASE)

            # Count occurrences with boundary-aware matching
            matches = pattern.findall(resume_text)
            count = len(matches)

            if count > 0:
                present.append((keyword, count))

        # Sort by frequency
        present = sorted(present, key=lambda x: x[1], reverse=True)
        return present

    def _check_for_summary(self, resume_text: str) -> bool:
        """
        Check if resume has a summary/profile/overview section at the top.
        ATS systems favor resumes with clear summaries.
        """
        # Get first 500 characters (typical summary location)
        top_section = resume_text[:500].lower()

        # Look for summary indicators
        summary_patterns = [
            r'\bsummary\b',
            r'\bprofile\b',
            r'\boverview\b',
            r'\babout\s+me\b',
            r'\bprofessional\s+summary\b',
            r'\bcareer\s+summary\b',
            r'\bexecutive\s+summary\b',
            r'\bqualifications\b'
        ]

        return any(re.search(pattern, top_section) for pattern in summary_patterns)

    def _analyze_sections(self, resume_text: str) -> dict[str, any]:
        """Analyze the presence and quality of key resume sections"""
        sections = {
            'has_experience': False,
            'has_education': False,
            'has_skills': False,
            'has_projects': False,
            'experience_bullet_count': 0,
            'quantified_bullets': 0
        }

        text_lower = resume_text.lower()

        # Check for section headers (look for these words as headers, not just mentions)
        # Pattern: start of line, optional whitespace, keyword, optional colon/dashes, mostly alone on the line
        sections['has_experience'] = bool(re.search(r'^[\s#]*(?:experience|work history|employment)[\s:_-]*$', text_lower, re.MULTILINE))
        sections['has_education'] = bool(re.search(r'^[\s#]*(?:education|academic)[\s:_-]*$', text_lower, re.MULTILINE))
        sections['has_skills'] = bool(re.search(r'^[\s#]*(?:skills|competencies|technologies|technical skills)[\s:_-]*$', text_lower, re.MULTILINE))
        sections['has_projects'] = bool(re.search(r'^[\s#]*(?:projects|portfolio)[\s:_-]*$', text_lower, re.MULTILINE))

        # Count bullet points (likely achievements)
        bullet_patterns = [r'^\s*[-•]\s', r'^\s*\*\s']
        for pattern in bullet_patterns:
            sections['experience_bullet_count'] += len(re.findall(pattern, resume_text, re.MULTILINE))

        # Count quantified achievements (numbers, percentages, $)
        quantified_pattern = r'(?:\d+%|\$\d+|[\d,]+\s*(?:million|billion|thousand|k|m|b)|\d+x|[\d,]+\+)'
        sections['quantified_bullets'] = len(re.findall(quantified_pattern, text_lower))

        return sections

    def _calculate_keyword_coverage(
        self,
        jd_keywords: list[tuple[str, float]],
        resume_keywords: list[tuple[str, float]]
    ) -> float:
        """Calculate what percentage of JD keywords appear in resume"""
        if not jd_keywords:
            return 0.0

        jd_keyword_set = {kw.lower() for kw, _ in jd_keywords}
        resume_keyword_set = {kw.lower() for kw, _ in resume_keywords}

        matched = len(jd_keyword_set.intersection(resume_keyword_set))
        coverage = (matched / len(jd_keyword_set)) * 100

        return round(coverage, 2)

    def _calculate_ats_score(
        self,
        keyword_coverage: float,
        has_summary: bool,
        section_analysis: dict,
        embedding_similarity: float = None
    ) -> float:
        """
        Calculate overall ATS compatibility score (0-1).

        Factors:
        - Keyword coverage (40%)
        - Section presence (30%)
        - Summary presence (15%)
        - Embedding similarity (15%) if available
        """
        score = 0.0

        # Keyword coverage (40%)
        score += (keyword_coverage / 100) * 0.40

        # Section presence (30%)
        section_score = 0
        section_score += 0.4 if section_analysis.get('has_experience') else 0
        section_score += 0.25 if section_analysis.get('has_education') else 0
        section_score += 0.25 if section_analysis.get('has_skills') else 0
        section_score += 0.1 if section_analysis.get('has_projects') else 0
        score += section_score * 0.30

        # Summary presence (15%)
        score += 0.15 if has_summary else 0

        # Embedding similarity (15%) if available
        if embedding_similarity is not None:
            score += (embedding_similarity / 100) * 0.15
        else:
            # Redistribute to keyword coverage if embedding not available
            score += (keyword_coverage / 100) * 0.15

        return round(score, 3)

    def _generate_specific_recommendations(
        self,
        missing_keywords: list[tuple[str, float]],
        present_keywords: list[tuple[str, int]],
        has_summary: bool,
        section_analysis: dict,
        keyword_coverage: float,
        embedding_similarity: float = None,
        tfidf_similarity: float = None
    ) -> list[dict[str, str]]:
        """Generate prioritized, actionable recommendations"""
        recommendations = []
        priority_map = {'critical': 1, 'high': 2, 'medium': 3, 'low': 4}

        # Summary recommendation
        if not has_summary:
            recommendations.append({
                'priority': 'high',
                'category': 'structure',
                'title': 'Add a Professional Summary',
                'description': 'ATS systems favor resumes with a clear summary at the top. Add a 2-3 sentence professional summary highlighting your key qualifications.',
                'action': 'Add a "Professional Summary" section at the top of your resume.'
            })

        # Missing keywords recommendations
        if missing_keywords and len(missing_keywords) > 0:
            top_missing = missing_keywords[:5]
            keywords_str = ', '.join([f'"{kw}"' for kw, _ in top_missing])

            if keyword_coverage < 30:
                priority = 'critical'
            elif keyword_coverage < 50:
                priority = 'high'
            else:
                priority = 'medium'

            recommendations.append({
                'priority': priority,
                'category': 'keywords',
                'title': 'Incorporate Missing Keywords',
                'description': f'Your resume is missing key terms from the job description: {keywords_str}. These keywords are important for ATS matching.',
                'action': 'Review your experience bullets and naturally incorporate these terms where truthful and relevant. Do not fabricate experience.'
            })

        # Section recommendations
        if not section_analysis.get('has_experience'):
            recommendations.append({
                'priority': 'critical',
                'category': 'structure',
                'title': 'Add Experience Section',
                'description': 'Your resume appears to be missing a clear "Experience" or "Work History" section.',
                'action': 'Add a dedicated "Experience" section with your work history, including company names, dates, and achievement bullets.'
            })

        if not section_analysis.get('has_skills'):
            recommendations.append({
                'priority': 'high',
                'category': 'structure',
                'title': 'Add Skills Section',
                'description': 'A dedicated "Skills" section helps ATS systems quickly identify your technical competencies.',
                'action': 'Create a "Technical Skills" section listing relevant technologies, tools, and methodologies.'
            })

        # Quantification recommendation
        if section_analysis.get('quantified_bullets', 0) < 3:
            recommendations.append({
                'priority': 'medium',
                'category': 'content',
                'title': 'Quantify Your Achievements',
                'description': 'ATS systems and recruiters favor quantified results. Your resume has few measurable achievements.',
                'action': 'Add numbers, percentages, or metrics to your bullets (e.g., "Improved efficiency by 25%", "Managed team of 5").'
            })

        # Bullet point recommendation
        if section_analysis.get('experience_bullet_count', 0) < 5:
            recommendations.append({
                'priority': 'medium',
                'category': 'content',
                'title': 'Expand Experience Details',
                'description': 'Your experience section appears brief. More detail helps ATS systems understand your qualifications.',
                'action': 'Add 3-5 bullet points per job describing your responsibilities and achievements using action verbs.'
            })

        # Keyword density recommendation
        if present_keywords and any(count > 10 for _, count in present_keywords[:3]):
            recommendations.append({
                'priority': 'low',
                'category': 'keywords',
                'title': 'Avoid Keyword Stuffing',
                'description': 'Some keywords appear excessively. While keyword matching is important, over-repetition can trigger ATS penalties.',
                'action': 'Use synonyms and varied phrasing to naturally incorporate key terms without excessive repetition.'
            })

        # Similarity score recommendations
        if embedding_similarity is not None and embedding_similarity < 40:
            recommendations.append({
                'priority': 'high',
                'category': 'alignment',
                'title': 'Improve Content Alignment',
                'description': f'Your resume has low semantic similarity ({embedding_similarity:.1f}%) to the job description.',
                'action': 'Restructure your bullets to emphasize experiences and skills that directly relate to this job\'s requirements.'
            })

        # Sort by priority
        recommendations.sort(key=lambda x: priority_map.get(x['priority'], 5))

        return recommendations

    @staticmethod
    def _preprocess_text(text: str) -> str:
        """Clean and preprocess text for analysis"""
        # Convert to lowercase
        text = text.lower()

        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)

        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    @staticmethod
    def _load_stopwords() -> set[str]:
        """Load common English stopwords"""
        # Basic stopwords - in production, use nltk or spacy stopwords
        stopwords = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'this', 'but', 'they', 'have',
            'had', 'what', 'when', 'where', 'who', 'which', 'why', 'how'
        }
        return stopwords

    @staticmethod
    def _get_fallback_recommendations() -> dict:
        """Return fallback recommendations if analysis fails"""
        return {
            'ats_score': 0.0,
            'keyword_coverage': 0.0,
            'missing_keywords': [],
            'present_keywords': [],
            'has_summary_section': False,
            'section_analysis': {},
            'recommendations': [{
                'priority': 'high',
                'category': 'error',
                'title': 'Analysis Unavailable',
                'description': 'Unable to complete ATS analysis. Please ensure resume and job description are provided.',
                'action': 'Contact support if this issue persists.'
            }],
            'keyword_analysis': {
                'total_jd_keywords': 0,
                'matched_keywords': 0,
                'missing_count': 0
            }
        }
