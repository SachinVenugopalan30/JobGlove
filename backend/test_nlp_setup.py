"""Test script to verify NLP setup is working correctly."""

import sys

def test_spacy():
    """Test spaCy installation."""
    print("Testing spaCy...", end=" ")
    try:
        import spacy
        nlp = spacy.load('en_core_web_sm')
        doc = nlp("Apple is looking for a software engineer in California.")
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        assert len(entities) > 0, "No entities found"
        print(f"✓ (Found {len(entities)} entities)")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def test_nltk():
    """Test NLTK installation."""
    print("Testing NLTK...", end=" ")
    try:
        import nltk
        from nltk.corpus import stopwords
        from nltk.tokenize import word_tokenize

        text = "This is a test sentence for NLTK."
        tokens = word_tokenize(text)
        stop_words = set(stopwords.words('english'))
        filtered = [w for w in tokens if w.lower() not in stop_words]

        assert len(tokens) > 0, "No tokens found"
        assert len(filtered) < len(tokens), "Stopwords not filtered"
        print(f"✓ (Tokenized {len(tokens)} words, filtered to {len(filtered)})")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def test_pymupdf():
    """Test PyMuPDF installation."""
    print("Testing PyMuPDF...", end=" ")
    try:
        import fitz
        print("✓")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def test_pdfplumber():
    """Test pdfplumber installation."""
    print("Testing pdfplumber...", end=" ")
    try:
        import pdfplumber
        print("✓")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def test_sklearn():
    """Test scikit-learn installation."""
    print("Testing scikit-learn...", end=" ")
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        vectorizer = TfidfVectorizer()
        texts = ["Python developer", "Java programmer"]
        tfidf = vectorizer.fit_transform(texts)
        similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]

        assert 0 <= similarity <= 1, "Invalid similarity score"
        print(f"✓ (Similarity: {similarity:.2f})")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("NLP Setup Verification")
    print("=" * 60)

    tests = [
        test_spacy,
        test_nltk,
        test_pymupdf,
        test_pdfplumber,
        test_sklearn
    ]

    results = [test() for test in tests]

    print("=" * 60)
    if all(results):
        print("✓ All tests passed! NLP setup is complete.")
        print("=" * 60)
        return 0
    else:
        print("✗ Some tests failed. Please check the errors above.")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(main())
