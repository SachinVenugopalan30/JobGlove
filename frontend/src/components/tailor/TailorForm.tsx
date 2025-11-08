import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Upload, Loader2, FileText } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { fadeIn, slideUp } from '@/lib/animations';
import { cn } from '@/lib/utils';

interface TailorFormProps {
  onComplete: (results: any) => void;
}

export default function TailorForm({ onComplete }: TailorFormProps) {
  const [file, setFile] = useState<File | null>(null);
  const [jobTitle, setJobTitle] = useState('');
  const [company, setCompany] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [selectedApi, setSelectedApi] = useState<string>('');
  const [availableApis, setAvailableApis] = useState<Record<string, boolean>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isDragging, setIsDragging] = useState(false);

  useEffect(() => {
    checkAvailableApis();
  }, []);

  const checkAvailableApis = async () => {
    try {
      const response = await fetch('/api/check-apis');
      const data = await response.json();
      setAvailableApis(data);
      const firstAvailable = Object.keys(data).find(api => data[api]);
      if (firstAvailable) {
        setSelectedApi(firstAvailable);
      }
    } catch (err) {
      setError('Failed to check available AI providers');
    }
  };

  const handleFileChange = (selectedFile: File | null) => {
    if (!selectedFile) return;

    const allowedTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/msword'
    ];

    if (!allowedTypes.includes(selectedFile.type)) {
      setError('Please upload a PDF or DOCX file');
      return;
    }

    setFile(selectedFile);
    setError('');
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    handleFileChange(droppedFile);
  };

  const handleSubmit = async () => {
    if (!file || !jobTitle || !company || !jobDescription || !selectedApi) {
      setError('Please fill in all fields');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const uploadResponse = await fetch('/api/upload-resume', {
        method: 'POST',
        body: formData,
      });

      if (!uploadResponse.ok) {
        throw new Error('Failed to upload resume');
      }

      const uploadData = await uploadResponse.json();

      const tailorResponse = await fetch('/api/tailor-resume', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_path: uploadData.file_path,
          job_description: jobDescription,
          api: selectedApi,
          user_name: 'User',
          company: company,
          job_title: jobTitle,
        }),
      });

      if (!tailorResponse.ok) {
        throw new Error('Failed to tailor resume');
      }

      const tailorData = await tailorResponse.json();
      onComplete(tailorData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const canSubmit = file && jobTitle && company && jobDescription && selectedApi && !isLoading;

  return (
    <motion.div
      variants={fadeIn}
      initial="hidden"
      animate="visible"
      exit="hidden"
    >
      <Card>
        <CardHeader>
          <CardTitle>Tailor Your Resume</CardTitle>
          <CardDescription>
            Upload your resume and provide job details. AI will analyze and tailor it for you.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* File Upload */}
          <div>
            <label className="block text-sm font-medium mb-2">Resume Upload</label>
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={cn(
                'border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer',
                isDragging ? 'border-primary bg-primary/5' : 'border-muted',
                file && 'border-green-500 bg-green-500/5'
              )}
              onClick={() => document.getElementById('file-input')?.click()}
            >
              <input
                id="file-input"
                type="file"
                accept=".pdf,.docx,.doc"
                onChange={(e) => handleFileChange(e.target.files?.[0] || null)}
                className="hidden"
              />
              {file ? (
                <div className="flex items-center justify-center gap-2 text-green-600">
                  <FileText className="h-5 w-5" />
                  <span className="font-medium">{file.name}</span>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-2">
                  <Upload className="h-8 w-8 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">
                    Click or drag to upload PDF or DOCX
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Job Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Job Title</label>
              <Input
                placeholder="Software Engineer"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Company</label>
              <Input
                placeholder="Google"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
              />
            </div>
          </div>

          {/* Job Description */}
          <div>
            <label className="block text-sm font-medium mb-2">Job Description</label>
            <Textarea
              placeholder="Paste the full job description here..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              rows={8}
              className="resize-none"
            />
          </div>

          {/* AI Provider Selection */}
          <div>
            <label className="block text-sm font-medium mb-2">AI Provider</label>
            <div className="flex gap-3">
              {Object.keys(availableApis).map((api) => (
                <button
                  key={api}
                  onClick={() => setSelectedApi(api)}
                  disabled={!availableApis[api]}
                  className={cn(
                    'flex-1 py-2 px-4 rounded-lg border-2 transition-all capitalize',
                    selectedApi === api
                      ? 'border-primary bg-primary text-primary-foreground'
                      : 'border-muted hover:border-primary/50',
                    !availableApis[api] && 'opacity-50 cursor-not-allowed'
                  )}
                >
                  {api}
                </button>
              ))}
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-3 rounded-lg bg-destructive/10 text-destructive text-sm">
              {error}
            </div>
          )}

          {/* Submit Button */}
          <Button
            onClick={handleSubmit}
            disabled={!canSubmit}
            className="w-full"
            size="lg"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Tailoring Resume...
              </>
            ) : (
              'Tailor Resume with AI'
            )}
          </Button>
        </CardContent>
      </Card>
    </motion.div>
  );
}
