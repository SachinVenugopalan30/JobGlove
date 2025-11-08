import { motion } from 'framer-motion';
import { CheckCircle, XCircle } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { slideUp } from '@/lib/animations';

interface KeywordBadgesProps {
  matched: string[];
  missing: string[];
}

export default function KeywordBadges({ matched, missing }: KeywordBadgesProps) {
  return (
    <motion.div variants={slideUp}>
      <Card>
        <CardHeader>
          <CardTitle>Keyword Analysis</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Matched Keywords */}
          {matched.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <h4 className="font-medium">Matched Keywords ({matched.length})</h4>
              </div>
              <div className="flex flex-wrap gap-2">
                {matched.map((keyword, index) => (
                  <motion.div
                    key={keyword}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.05, duration: 0.3 }}
                  >
                    <Badge variant="default" className="bg-green-100 text-green-800 hover:bg-green-200">
                      {keyword}
                    </Badge>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {/* Missing Keywords */}
          {missing.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <XCircle className="h-5 w-5 text-red-600" />
                <h4 className="font-medium">Missing Keywords ({missing.length})</h4>
              </div>
              <div className="flex flex-wrap gap-2">
                {missing.map((keyword, index) => (
                  <motion.div
                    key={keyword}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.05, duration: 0.3 }}
                  >
                    <Badge variant="destructive" className="bg-red-100 text-red-800 hover:bg-red-200">
                      {keyword}
                    </Badge>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {matched.length === 0 && missing.length === 0 && (
            <p className="text-sm text-muted-foreground text-center py-4">
              No keyword analysis available
            </p>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
