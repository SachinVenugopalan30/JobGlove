import { motion } from 'framer-motion';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { getScoreColor } from '@/lib/utils';
import { fadeIn, slideUp } from '@/lib/animations';

interface ScoreItem {
  label: string;
  score: number;
  description: string;
}

interface ScoreBreakdownProps {
  scores: {
    keyword_match: number;
    relevance: number;
    ats_score: number;
    quality: number;
  };
}

export default function ScoreBreakdown({ scores }: ScoreBreakdownProps) {
  const scoreItems: ScoreItem[] = [
    {
      label: 'Keyword Match',
      score: scores.keyword_match,
      description: 'How well your resume matches job keywords',
    },
    {
      label: 'Relevance',
      score: scores.relevance,
      description: 'How relevant your experience is to the role',
    },
    {
      label: 'ATS Compatibility',
      score: scores.ats_score,
      description: 'How well your resume passes ATS systems',
    },
    {
      label: 'Overall Quality',
      score: scores.quality,
      description: 'General quality and formatting of your resume',
    },
  ];

  return (
    <motion.div variants={slideUp}>
      <Card>
        <CardHeader>
          <CardTitle>Score Breakdown</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {scoreItems.map((item, index) => (
            <motion.div
              key={item.label}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1, duration: 0.5 }}
              className="space-y-2"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h4 className="font-medium">{item.label}</h4>
                  <p className="text-sm text-muted-foreground">{item.description}</p>
                </div>
                <span className={`text-2xl font-bold ml-4 ${getScoreColor(item.score)}`}>
                  {Math.round(item.score)}%
                </span>
              </div>
              <Progress value={item.score} className="h-2" />
            </motion.div>
          ))}
        </CardContent>
      </Card>
    </motion.div>
  );
}
