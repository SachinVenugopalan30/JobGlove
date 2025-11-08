const API_BASE_URL = 'http://localhost:5000/api';

function resumeApp() {
    return {
        availableApis: {},
        selectedApi: null,
        resumeFile: null,
        resumeFileName: null,
        userName: '',
        company: '',
        jobTitle: '',
        jobDescription: '',
        customPrompt: '',
        showCustomPrompt: false,
        isProcessing: false,
        processingStatus: '',
        downloadUrl: null,
        texDownloadUrl: null,
        errorMessage: null,
        uploadedFilePath: null,
        originalResumeText: null,
        tailoredResumeText: null,
        isScoring: false,
        scoresLoaded: false,
        isReviewing: false,
        reviewLoaded: false,
        reviewBullets: [],
        originalScores: {
            ats_score: 0,
            content_score: 0,
            style_score: 0,
            match_score: 0,
            readiness_score: 0,
            total_score: 0
        },
        tailoredScores: {
            ats_score: 0,
            content_score: 0,
            style_score: 0,
            match_score: 0,
            readiness_score: 0,
            total_score: 0
        },

        init() {
            this.checkAvailableApis();
        },

        async checkAvailableApis() {
            try {
                const response = await fetch(`${API_BASE_URL}/check-apis`);
                if (!response.ok) {
                    throw new Error('Failed to check API availability');
                }
                this.availableApis = await response.json();

                // Auto-select first available API
                for (const [api, available] of Object.entries(this.availableApis)) {
                    if (available) {
                        this.selectedApi = api;
                        break;
                    }
                }
            } catch (error) {
                this.errorMessage = 'Failed to connect to server. Please ensure the backend is running.';
            }
        },

        handleFileChange(event) {
            const file = event.target.files[0];
            if (file) {
                this.resumeFile = file;
                this.resumeFileName = file.name;
                this.downloadUrl = null;
            }
        },

        canSubmit() {
            return this.resumeFile &&
                   this.userName.trim().length > 0 &&
                   this.company.trim().length > 0 &&
                   this.jobTitle.trim().length > 0 &&
                   this.jobDescription.trim().length > 0 &&
                   this.selectedApi &&
                   !this.isProcessing;
        },

        async uploadResume() {
            const formData = new FormData();
            formData.append('file', this.resumeFile);

            const response = await fetch(`${API_BASE_URL}/upload-resume`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Upload failed');
            }

            return await response.json();
        },

        async tailorResume() {
            this.isProcessing = true;
            this.errorMessage = null;
            this.downloadUrl = null;
            this.texDownloadUrl = null;
            this.scoresLoaded = false;

            try {
                // Upload resume
                this.processingStatus = 'Uploading resume...';
                const uploadResponse = await this.uploadResume();
                this.uploadedFilePath = uploadResponse.file_path;

                // Tailor resume
                this.processingStatus = 'Analyzing job description...';
                await new Promise(resolve => setTimeout(resolve, 500));

                this.processingStatus = `Tailoring resume with ${this.selectedApi.toUpperCase()} AI...`;
                const tailorResponse = await fetch(`${API_BASE_URL}/tailor-resume`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        file_path: this.uploadedFilePath,
                        job_description: this.jobDescription,
                        api: this.selectedApi,
                        user_name: this.userName,
                        company: this.company,
                        job_title: this.jobTitle,
                        custom_prompt: this.customPrompt.trim() || null
                    })
                });

                if (!tailorResponse.ok) {
                    const error = await tailorResponse.json();
                    throw new Error(error.error || 'Failed to tailor resume');
                }

                this.processingStatus = 'Generating PDF...';
                const result = await tailorResponse.json();
                this.originalResumeText = result.original_text || '';
                this.tailoredResumeText = result.tailored_text || '';
                this.downloadUrl = `${API_BASE_URL}/download/${result.pdf_file}`;
                this.texDownloadUrl = `${API_BASE_URL}/download/${result.tex_file}`;

            } catch (error) {
                this.errorMessage = error.message || 'An error occurred while processing your resume';
            } finally {
                this.isProcessing = false;
                this.processingStatus = '';
            }
        },

        async scoreResumes() {
            this.isScoring = true;
            this.errorMessage = null;

            try {
                // Score original resume
                const originalScoreResponse = await fetch(`${API_BASE_URL}/score`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        resume_text: this.originalResumeText || '',
                        job_description: this.jobDescription,
                        api: this.selectedApi
                    })
                });

                if (originalScoreResponse.ok) {
                    this.originalScores = await originalScoreResponse.json();
                }

                // Score tailored resume
                const tailoredScoreResponse = await fetch(`${API_BASE_URL}/score`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        resume_text: this.tailoredResumeText || '',
                        job_description: this.jobDescription,
                        api: this.selectedApi
                    })
                });

                if (tailoredScoreResponse.ok) {
                    this.tailoredScores = await tailoredScoreResponse.json();
                }

                this.scoresLoaded = true;

            } catch (error) {
                this.errorMessage = error.message || 'Failed to score resumes';
            } finally {
                this.isScoring = false;
            }
        },

        getScoreClass(score) {
            if (score >= 80) return 'score-excellent';
            if (score >= 60) return 'score-good';
            if (score >= 40) return 'score-fair';
            return 'score-poor';
        },

        async reviewResume() {
            this.isReviewing = true;
            this.errorMessage = null;

            try {
                const reviewResponse = await fetch(`${API_BASE_URL}/review`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        resume_text: this.tailoredResumeText || '',
                        job_description: this.jobDescription,
                        api: this.selectedApi
                    })
                });

                if (reviewResponse.ok) {
                    const reviewData = await reviewResponse.json();
                    this.reviewBullets = reviewData.bullets || [];
                    this.reviewLoaded = true;
                }

            } catch (error) {
                this.errorMessage = error.message || 'Failed to review resume';
            } finally {
                this.isReviewing = false;
            }
        },

        get groupedBullets() {
            const grouped = {};
            this.reviewBullets.forEach(bullet => {
                const section = bullet.section || 'Other';
                if (!grouped[section]) {
                    grouped[section] = [];
                }
                grouped[section].push(bullet);
            });
            return grouped;
        },

        getRelevanceClass(score) {
            if (score >= 4) return 'relevance-high';
            if (score >= 3) return 'relevance-medium';
            return 'relevance-low';
        }
    };
}
