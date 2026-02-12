import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    # Ollama Configuration
    OLLAMA_ENABLED = os.getenv("OLLAMA_ENABLED", "false").lower() == "true"
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # AI Model Configuration
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

    # Debug
    DEBUG_AI_RESPONSES = os.getenv("DEBUG_AI_RESPONSES", "false").lower() == "true"

    # User settings
    DEFAULT_USER_NAME = os.getenv("DEFAULT_USER_NAME", "User")

    # File upload settings
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10485760))
    ALLOWED_EXTENSIONS = {"docx", "doc", "pdf"}

    # Directory paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")
    TEMPLATES_FOLDER = os.path.join(BASE_DIR, "backend", "templates")

    # NLP Configuration
    SPACY_MODEL = "en_core_web_sm"
    MIN_KEYWORD_LENGTH = 2
    MAX_KEYWORDS = 50

    # Scoring weights
    KEYWORD_MATCH_WEIGHT = 0.40
    RELEVANCE_WEIGHT = 0.25
    ATS_WEIGHT = 0.20
    QUALITY_WEIGHT = 0.15

    @staticmethod
    def check_api_availability():
        """Check which API keys are available"""
        return {
            "openai": bool(Config.OPENAI_API_KEY),
            "gemini": bool(Config.GEMINI_API_KEY),
            "claude": bool(Config.ANTHROPIC_API_KEY),
            "groq": bool(Config.GROQ_API_KEY),
            "ollama": Config.OLLAMA_ENABLED,
        }
