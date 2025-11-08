import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import TailorForm from '@/components/tailor/TailorForm';
import ResultsView from '@/components/tailor/ResultsView';
import { fadeIn } from '@/lib/animations';

interface Score {
  total_score: number;
  keyword_match_score: number;
  relevance_score: number;
  ats_score: number;
  quality_score: number;
  recommendations?: string[];
}

interface TailorResults {
  original_score: Score;
  tailored_score: Score;
  pdf_file: string;
  tex_file: string;
}

export default function Tailor() {
  const navigate = useNavigate();
  const [results, setResults] = useState<TailorResults | null>(null);

  useEffect(() => {
    document.title = 'JobGlove - Tailor Resume';
  }, []);

  const handleTailorComplete = (data: TailorResults) => {
    setResults(data);
  };

  const handleReset = () => {
    setResults(null);
  };

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-background to-muted/20">
      {/* Header */}
      <motion.header
        className="border-b bg-background/95 backdrop-blur"
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
      >
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/')}
            className="gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Back
          </Button>
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            <span className="font-semibold">JobGlove</span>
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <main className="flex-1 container mx-auto px-4 py-8">
        <motion.div
          className="max-w-4xl mx-auto"
          variants={fadeIn}
          initial="hidden"
          animate="visible"
        >
          <AnimatePresence mode="wait">
            {!results ? (
              <TailorForm key="form" onComplete={handleTailorComplete} />
            ) : (
              <ResultsView key="results" results={results} onReset={handleReset} />
            )}
          </AnimatePresence>
        </motion.div>
      </main>
    </div>
  );
}
