import { motion } from 'framer-motion';
import { Lightbulb, TrendingUp, AlertTriangle } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { slideUp } from '@/lib/animations';

interface RecommendationsProps {
  recommendations: string[];
}

const getRecommendationIcon = (index: number) => {
  const icons = [Lightbulb, TrendingUp, AlertTriangle];
  const Icon = icons[index % icons.length];
  return <Icon className="h-5 w-5 text-primary" />;
};

export default function Recommendations({ recommendations }: RecommendationsProps) {
  if (!recommendations || recommendations.length === 0) {
    return null;
  }

  return (
    <motion.div variants={slideUp}>
      <Card>
        <CardHeader>
          <CardTitle>Recommendations</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-4">
            {recommendations.map((recommendation, index) => (
              <motion.li
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1, duration: 0.5 }}
                className="flex gap-3"
              >
                <div className="flex-shrink-0 mt-1">
                  {getRecommendationIcon(index)}
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {recommendation}
                </p>
              </motion.li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </motion.div>
  );
}
