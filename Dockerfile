# Multi-stage Dockerfile for JobGlove Application

# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY frontend/ ./

# Build frontend for production
RUN npm run build

# Stage 2: Backend with Python
FROM python:3.11-slim

# Install system dependencies for LaTeX, PDF processing, and curl for health checks
RUN apt-get update && apt-get install -y \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-xetex \
    latexmk \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy backend dependency files
COPY backend/requirements.txt ./backend/

# Install Python dependencies using uv
RUN cd backend && uv pip install --system -r requirements.txt

# Copy backend source
COPY backend/ ./backend/

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/dist ./backend/static

# Create necessary directories
RUN mkdir -p /app/uploads /app/outputs /app/backend/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Expose port
EXPOSE 5000

# Change to backend directory
WORKDIR /app/backend

# Create a startup script to serve both frontend and backend
RUN echo '#!/bin/bash\n\
echo "======================================"\n\
echo "  Starting JobGlove Application"\n\
echo "======================================"\n\
echo ""\n\
echo "Initializing database..."\n\
python -c "from database.db import init_db; init_db()"\n\
echo "✅ Database initialized"\n\
echo ""\n\
echo "Starting production server with Gunicorn..."\n\
echo "📡 API Server: http://0.0.0.0:5000/api/"\n\
echo "🌐 Frontend: http://0.0.0.0:5000/"\n\
echo ""\n\
echo "======================================"\n\
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 --access-logfile - --error-logfile - wsgi:application\n\
' > /app/start.sh && chmod +x /app/start.sh

# Start the application
CMD ["/app/start.sh"]
