import { motion } from 'framer-motion';
import { Download, FileText, RotateCcw, TrendingUp, CheckCircle2 } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import CircularScore from '@/components/score/CircularScore';
import { slideUp, staggerContainer } from '@/lib/animations';
import { getScoreColor } from '@/lib/utils';

interface Score {
  total_score: number;
  keyword_match_score: number;
  relevance_score: number;
  ats_score: number;
  quality_score: number;
  recommendations?: string[];
}

interface ResultsViewProps {
  results: {
    original_score: Score;
    tailored_score: Score;
    pdf_file: string;
    tex_file: string;
  };
  onReset: () => void;
}

export default function ResultsView({ results, onReset }: ResultsViewProps) {
  const improvement = results.tailored_score.total_score - results.original_score.total_score;

  const downloadPdf = () => {
    window.open(`/api/download/${results.pdf_file}`, '_blank');
  };

  const downloadTex = () => {
    window.open(`/api/download/${results.tex_file}`, '_blank');
  };

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      exit="hidden"
      className="space-y-6"
    >
      {/* Success Header */}
      <motion.div variants={slideUp}>
        <Card className="border-green-500/50 bg-green-500/5">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="h-12 w-12 rounded-full bg-green-500/10 flex items-center justify-center">
                <CheckCircle2 className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <CardTitle>Resume Successfully Tailored!</CardTitle>
                <CardDescription>
                  Your resume has been optimized and is ready for download
                </CardDescription>
              </div>
            </div>
          </CardHeader>
        </Card>
      </motion.div>

      {/* Score Comparison */}
      <motion.div variants={slideUp}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-primary" />
              Score Improvement
            </CardTitle>
            <CardDescription>
              See how much your resume improved after AI tailoring
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-center">
              {/* Original Score */}
              <div className="flex flex-col items-center">
                <CircularScore
                  score={results.original_score.total_score}
                  size="md"
                  label="Original Resume"
                  delay={0.2}
                />
              </div>

              {/* Improvement Badge */}
              <div className="flex flex-col items-center gap-2">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.6, type: 'spring' }}
                >
                  <Badge
                    variant="outline"
                    className={`text-2xl px-6 py-2 ${improvement > 0 ? 'border-green-500 text-green-600' : 'border-muted'}`}
                  >
                    {improvement > 0 ? '+' : ''}{improvement}
                  </Badge>
                </motion.div>
                <p className="text-sm text-muted-foreground">points improved</p>
              </div>

              {/* Tailored Score */}
              <div className="flex flex-col items-center">
                <CircularScore
                  score={results.tailored_score.total_score}
                  size="md"
                  label="Tailored Resume"
                  delay={0.4}
                />
              </div>
            </div>

            <Separator className="my-6" />

            {/* Score Breakdown */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: 'Keyword Match', original: results.original_score.keyword_match_score, tailored: results.tailored_score.keyword_match_score },
                { label: 'Relevance', original: results.original_score.relevance_score, tailored: results.tailored_score.relevance_score },
                { label: 'ATS Score', original: results.original_score.ats_score, tailored: results.tailored_score.ats_score },
                { label: 'Quality', original: results.original_score.quality_score, tailored: results.tailored_score.quality_score },
              ].map((item, index) => (
                <motion.div
                  key={item.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.8 + index * 0.1 }}
                  className="text-center p-4 rounded-lg border bg-muted/30"
                >
                  <p className="text-sm text-muted-foreground mb-2">{item.label}</p>
                  <div className="flex items-center justify-center gap-2">
                    <span className="text-lg font-semibold text-muted-foreground/60">
                      {item.original}
                    </span>
                    <span className="text-muted-foreground">→</span>
                    <span className={`text-xl font-bold ${getScoreColor(item.tailored)}`}>
                      {item.tailored}
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Recommendations */}
      {results.original_score.recommendations && results.original_score.recommendations.length > 0 && (
        <motion.div variants={slideUp}>
          <Card>
            <CardHeader>
              <CardTitle>Original Resume Insights</CardTitle>
              <CardDescription>
                Key improvements that were made to your resume
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {results.original_score.recommendations.map((rec, index) => (
                  <motion.li
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 1.0 + index * 0.1 }}
                    className="flex items-start gap-2 text-sm"
                  >
                    <CheckCircle2 className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <span>{rec}</span>
                  </motion.li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Download Buttons */}
      <motion.div variants={slideUp} className="flex flex-col sm:flex-row gap-4">
        <Button onClick={downloadPdf} size="lg" className="flex-1 gap-2">
          <Download className="h-4 w-4" />
          Download PDF
        </Button>
        <Button onClick={downloadTex} variant="outline" size="lg" className="flex-1 gap-2">
          <FileText className="h-4 w-4" />
          Download LaTeX
        </Button>
      </motion.div>

      {/* Reset Button */}
      <motion.div variants={slideUp} className="flex justify-center">
        <Button onClick={onReset} variant="ghost" className="gap-2">
          <RotateCcw className="h-4 w-4" />
          Tailor Another Resume
        </Button>
      </motion.div>
    </motion.div>
  );
}
