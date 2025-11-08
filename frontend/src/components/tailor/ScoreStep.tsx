import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, ArrowRight, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import CircularScore from '@/components/score/CircularScore';
import ScoreBreakdown from '@/components/score/ScoreBreakdown';
import KeywordBadges from '@/components/score/KeywordBadges';
import Recommendations from '@/components/score/Recommendations';
import { ApiClient } from '@/lib/api';
import { fadeIn, staggerContainer } from '@/lib/animations';
import type { AnalyzeResponse } from '@/types/api';

interface ScoreStepProps {
  filePath: string;
  jobDescription: string;
  onBack: () => void;
  onNext: () => void;
}

export default function ScoreStep({ filePath, jobDescription, onBack, onNext }: ScoreStepProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null);

  useEffect(() => {
    let cancelled = false;

    const analyzeResume = async () => {
      if (!filePath || !jobDescription) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        setAnalysis(null); // Clear previous analysis
        
        const result = await ApiClient.analyzeResume(filePath, jobDescription);
        
        // Only update state if component is still mounted
        if (!cancelled) {
          setAnalysis(result);
          setLoading(false);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to analyze resume');
          setLoading(false);
        }
      }
    };

    analyzeResume();

    // Cleanup function to prevent state updates after unmount
    return () => {
      cancelled = true;
    };
  }, [filePath, jobDescription]);

  if (loading) {
    return (
      <motion.div
        variants={fadeIn}
        initial="hidden"
        animate="visible"
        exit="hidden"
        className="flex items-center justify-center min-h-[400px]"
      >
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary mx-auto" />
          <p className="text-lg text-muted-foreground">Analyzing your resume...</p>
        </div>
      </motion.div>
    );
  }

  if (error) {
    return (
      <motion.div
        variants={fadeIn}
        initial="hidden"
        animate="visible"
        exit="hidden"
        className="space-y-6"
      >
        <div className="text-center space-y-4 py-12">
          <p className="text-red-600 font-medium">{error}</p>
          <div className="flex gap-4 justify-center">
            <Button variant="outline" onClick={onBack}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Go Back
            </Button>
          </div>
        </div>
      </motion.div>
    );
  }

  if (!analysis) {
    // Show loading state if we're still loading
    if (loading) {
      return (
        <motion.div
          variants={fadeIn}
          initial="hidden"
          animate="visible"
          exit="hidden"
          className="flex items-center justify-center min-h-[400px]"
        >
          <div className="text-center space-y-4">
            <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary mx-auto" />
            <p className="text-lg text-muted-foreground">Analyzing your resume...</p>
          </div>
        </motion.div>
      );
    }
    return null;
  }

  const totalScore = analysis.score.total_score;
  const scores = analysis.score;

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      exit="hidden"
      className="space-y-8"
    >
      {/* Header */}
      <div className="text-center">
        <motion.h2 variants={fadeIn} className="text-3xl font-bold mb-2">
          Resume Analysis Complete
        </motion.h2>
        <motion.p variants={fadeIn} className="text-muted-foreground">
          Here's how your resume scores against the job description
        </motion.p>
      </div>

      {/* Warning Banner */}
      <motion.div 
        variants={fadeIn}
        className="bg-yellow-50 dark:bg-yellow-950/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4"
      >
        <div className="flex gap-3">
          <AlertTriangle className="h-5 w-5 text-yellow-600 dark:text-yellow-500 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="font-semibold text-yellow-900 dark:text-yellow-200 mb-1">
              Note About Scoring Accuracy
            </h3>
            <p className="text-sm text-yellow-800 dark:text-yellow-300">
              These scores may not be entirely accurate due to keyword extraction inconsistencies. 
              However, our AI-powered resume tailoring in the next step will intelligently analyze 
              and optimize your resume to ensure the best possible match with the job description.
            </p>
          </div>
        </div>
      </motion.div>

      {/* Main Score Display */}
      <motion.div variants={fadeIn} className="flex justify-center py-8">
        <CircularScore score={totalScore} label="Overall Score" size="lg" />
      </motion.div>

      {/* Score Details Grid */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Individual Scores */}
        <motion.div variants={fadeIn} className="grid grid-cols-2 gap-4">
          <CircularScore
            score={scores.keyword_match_score}
            label="Keyword Match"
            size="sm"
            delay={0.2}
          />
          <CircularScore
            score={scores.relevance_score}
            label="Relevance"
            size="sm"
            delay={0.3}
          />
          <CircularScore
            score={scores.ats_score}
            label="ATS Score"
            size="sm"
            delay={0.4}
          />
          <CircularScore
            score={scores.quality_score}
            label="Quality"
            size="sm"
            delay={0.5}
          />
        </motion.div>

        {/* Score Breakdown */}
        <ScoreBreakdown scores={{
          keyword_match: scores.keyword_match_score,
          relevance: scores.relevance_score,
          ats_score: scores.ats_score,
          quality: scores.quality_score,
        }} />
      </div>

      {/* Keywords Analysis */}
      <KeywordBadges
        matched={scores.keyword_match_details?.matched || []}
        missing={scores.keyword_match_details?.missing || []}
      />

      {/* Recommendations */}
      {scores.recommendations && scores.recommendations.length > 0 && (
        <Recommendations recommendations={scores.recommendations} />
      )}

      {/* Navigation Buttons */}
      <motion.div variants={fadeIn} className="flex justify-between pt-6">
        <Button variant="outline" onClick={onBack}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>
        <Button onClick={onNext} className="min-w-[200px]">
          Continue to Tailoring
          <ArrowRight className="ml-2 h-4 w-4" />
        </Button>
      </motion.div>
    </motion.div>
  );
}
