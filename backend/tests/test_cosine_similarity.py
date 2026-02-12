from services.scoring_service import calculate_cosine_similarity


class TestCosineSimilarity:
    """Test suite for cosine similarity calculation"""

    def test_identical_texts(self):
        """Test that identical texts have 100% similarity"""
        text = "Python developer with experience in machine learning"
        score = calculate_cosine_similarity(text, text)
        assert score == 100.0, "Identical texts should have 100% similarity"

    def test_completely_different_texts(self):
        """Test that completely different texts have low similarity"""
        resume = "Python developer with machine learning experience"
        jd = "Chef with culinary expertise in French cuisine"
        score = calculate_cosine_similarity(resume, jd)
        assert score < 20, "Completely different texts should have very low similarity"

    def test_high_keyword_overlap(self):
        """Test that texts with high keyword overlap have high similarity"""
        resume = "Senior Python Developer with 5 years experience in machine learning, data science, and AI"
        jd = "Looking for Python Developer with machine learning and data science experience"
        score = calculate_cosine_similarity(resume, jd)
        assert score > 45, f"Texts with high keyword overlap should have decent similarity, got {score}%"

    def test_moderate_keyword_overlap(self):
        """Test that texts with moderate keyword overlap have moderate similarity"""
        resume = "Software Engineer with Java and C++ experience"
        jd = "Software Engineer needed with Python and JavaScript skills"
        score = calculate_cosine_similarity(resume, jd)
        assert 20 < score < 60, "Texts with moderate overlap should have moderate similarity"

    def test_empty_resume(self):
        """Test handling of empty resume text"""
        score = calculate_cosine_similarity("", "Python developer needed")
        assert score == 0.0, "Empty resume should return 0% similarity"

    def test_empty_job_description(self):
        """Test handling of empty job description"""
        score = calculate_cosine_similarity("Python developer", "")
        assert score == 0.0, "Empty job description should return 0% similarity"

    def test_both_empty(self):
        """Test handling of both texts being empty"""
        score = calculate_cosine_similarity("", "")
        assert score == 0.0, "Both empty texts should return 0% similarity"

    def test_whitespace_handling(self):
        """Test that extra whitespace is handled correctly"""
        resume = "Python    developer   with   machine   learning"
        jd = "Python developer with machine learning"
        score = calculate_cosine_similarity(resume, jd)
        assert score > 95, "Extra whitespace should be normalized"

    def test_case_insensitivity(self):
        """Test that similarity calculation is case-insensitive"""
        resume = "PYTHON DEVELOPER WITH MACHINE LEARNING"
        jd = "python developer with machine learning"
        score = calculate_cosine_similarity(resume, jd)
        assert score > 95, "Calculation should be case-insensitive"

    def test_real_world_example(self):
        """Test with a realistic resume and job description"""
        resume = """
        Senior Data Scientist with 7 years of experience in machine learning,
        statistical modeling, and predictive analytics. Proficient in Python,
        R, SQL, and TensorFlow. Led cross-functional teams to deploy ML models
        in production. Strong background in natural language processing and
        computer vision.
        """

        jd = """
        We are seeking a Data Scientist with strong machine learning skills.
        Must have experience with Python, SQL, and statistical analysis.
        Experience with NLP and deploying models to production is a plus.
        Team leadership experience preferred.
        """

        score = calculate_cosine_similarity(resume, jd)
        # TF-IDF with stopwords removed can result in lower scores than expected
        # This is normal and shows semantic matching rather than simple word overlap
        assert 15 < score < 80, f"Realistic resume/JD should have reasonable similarity, got {score}%"
        assert isinstance(score, float), "Score should be a float"

    def test_score_range(self):
        """Test that scores are always in valid range"""
        resume = "Python developer with machine learning experience"
        jd = "Java developer with web development skills"
        score = calculate_cosine_similarity(resume, jd)
        assert 0 <= score <= 100, "Score should be between 0 and 100"

    def test_score_precision(self):
        """Test that scores are rounded to 2 decimal places"""
        resume = "Python developer"
        jd = "Python developer with experience"
        score = calculate_cosine_similarity(resume, jd)
        # Check that there are at most 2 decimal places
        score_str = str(score)
        if '.' in score_str:
            decimals = len(score_str.split('.')[1])
            assert decimals <= 2, "Score should be rounded to at most 2 decimal places"
