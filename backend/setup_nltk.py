import nltk
import sys
import ssl

def setup_nltk_data():
    """Download required NLTK data packages."""
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    packages = [
        'punkt',
        'punkt_tab',
        'stopwords',
        'wordnet',
        'averaged_perceptron_tagger',
        'averaged_perceptron_tagger_eng',
        'maxent_ne_chunker',
        'maxent_ne_chunker_tab',
        'words'
    ]

    print("Downloading NLTK data packages...")
    for package in packages:
        try:
            print(f"Downloading {package}...", end=" ")
            nltk.download(package, quiet=True)
            print("✓")
        except Exception as e:
            print(f"⚠ (may already exist or optional)")

    print("\nNLTK data setup complete!")

if __name__ == '__main__':
    setup_nltk_data()
