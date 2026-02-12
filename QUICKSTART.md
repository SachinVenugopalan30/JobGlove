# Quick Start Guide

Get JobGlove up and running in **less than 5 minutes**!

## Option 1: Docker (Recommended - Easiest)

### Prerequisites
- Docker Desktop installed ([Download here](https://www.docker.com/products/docker-desktop))
- At least one AI API key ([Get OpenAI key](https://platform.openai.com/api-keys))

# Steps

### 1. Clone the repository
```bash
git clone https://github.com/SachinVenugopalan30/JobGlove.git && cd JobGlove
```

### 2. Create .env file
`cp .env.example .env`

### 3. Edit .env and add your API key
Open .env in your text editor and add:
`OPENAI_API_KEY=sk-your-actual-key-here`

### 4. Start the application
`docker compose up -d`

### 5. View logs (optional)
`docker compose logs -f`


**That's it!** Open your browser to: **http://localhost:5000**

### Stop the application
`docker compose down`

---

## Option 2: Manual Installation

### Prerequisites
- Python 3.11+
- Node.js 20+
- LaTeX (TeXLive or MiKTeX)

### Backend Setup
```bash
cd backend

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .

# Configure .env
cp ../.env.example ../.env
# Edit .env with your API keys

python app.py
```

### Frontend Setup (New Terminal)
```bash
cd frontend
npm install
npm run dev
```

Open: **http://localhost:5173**

---

## Option 3: Using Local Models with Ollama

Run AI models locally on your machine for free and complete privacy.

### Docker Setup (Recommended)

The Docker setup already includes Ollama service. After running `docker compose up -d`:

```bash
# Pull a model into the Ollama container
docker exec -it jobglove-ollama ollama pull llama3.2

# Or pull other models
docker exec -it jobglove-ollama ollama pull mistral
docker exec -it jobglove-ollama ollama pull phi3
```

**Enable in .env:**
```bash
OLLAMA_ENABLED=true
OLLAMA_MODEL=llama3.2
```

Restart the containers:
```bash
docker compose restart jobglove
```

### Manual Setup

1. **Install Ollama:**
   - Visit [ollama.ai](https://ollama.ai)
   - Download and install for your OS

2. **Start Ollama:**
   ```bash
   ollama serve
   ```

3. **Pull a model (new terminal):**
   ```bash
   ollama pull llama3.2
   ```

4. **Enable in .env:**
   ```bash
   OLLAMA_ENABLED=true
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2
   ```

5. **Restart backend:**
   ```bash
   cd backend
   python app.py
   ```

**Popular models:**
- `llama3.2` - Fast, good quality (default)
- `llama3.1` - More capable, slower
- `mistral` - Balanced performance
- `phi3` - Lightweight, fast

**Ollama will now appear as an available AI provider in the UI.**

---

## Using JobGlove

1. **Upload Resume** - Drag/drop your PDF or DOCX resume
2. **Fill Details**:
   - Your Name
   - Job Title (e.g., "Software Engineer")
   - Company (e.g., "Google")
   - Job Description (paste the full job posting)
3. **Select AI Provider** - Choose OpenAI, Gemini, Claude, Groq, or Ollama
4. **Click "Tailor Resume with AI"** - Wait 10-30 seconds
5. **Download** - Get your tailored PDF and LaTeX files!

---

## Troubleshooting

### Docker Issues

**Port 5000 already in use:**
```bash
# Edit docker-compose.yml, change:
ports:
  - "8080:5000"  # Use port 8080 instead
```

**Container won't start:**
```bash
# Check logs
docker-compose logs jobglove

# Rebuild
docker-compose up -d --build
```

**Permission denied:**
```bash
sudo chown -R $USER:$USER uploads outputs backend/logs
```

### API Issues

**"No API keys configured":**
- Check your .env file has a valid API key
- Make sure it's not the placeholder text
- Restart the application after editing .env

**"Failed to tailor resume":**
- Verify your API key is valid
- Check you have credits/quota remaining
- View logs: `docker-compose logs -f jobglove`

### File Upload Issues

**"File too large":**
```text
- Max size is 10MB by default
- Compress your PDF or convert to DOCX
```

**"Failed to extract text":**
- Ensure your PDF is not scanned/image-based
- Try converting to DOCX format

### Ollama Issues

**Ollama not appearing as available:**
```bash
# Check OLLAMA_ENABLED=true in .env
# Restart the application
docker compose restart jobglove
```

**"Connection refused" when using Ollama:**
```bash
# Check Ollama is running
docker ps | grep ollama

# View Ollama logs
docker logs jobglove-ollama

# Restart Ollama
docker restart jobglove-ollama
```

**Ollama is slow:**
- First run downloads the model (may take time)
- Smaller models are faster: try phi3 instead of llama3.1
- Check available memory: `docker stats jobglove-ollama`

**No models available:**
```bash
# Pull a model first
docker exec -it jobglove-ollama ollama pull llama3.2

# List available models
docker exec -it jobglove-ollama ollama list
```

---

## More Information

- **Full Documentation**: See [README.md](./README.md)

---

## Success Indicators

You know it's working when you see:

```text
✅ Container is healthy: docker-compose ps
✅ Logs show "Starting Flask server"
✅ Browser shows JobGlove homepage
✅ API providers show as available (not locked)
```
