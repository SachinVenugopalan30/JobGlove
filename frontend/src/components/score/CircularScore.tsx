import { motion } from 'framer-motion';
import { getScoreColor, getScoreGradient } from '@/lib/utils';

interface CircularScoreProps {
  score: number;
  label: string;
  size?: 'sm' | 'md' | 'lg';
  showPercentage?: boolean;
  delay?: number;
}

const sizeConfig = {
  sm: { radius: 35, strokeWidth: 6, fontSize: 'text-xl' },
  md: { radius: 50, strokeWidth: 8, fontSize: 'text-3xl' },
  lg: { radius: 70, strokeWidth: 10, fontSize: 'text-5xl' },
};

export default function CircularScore({
  score,
  label,
  size = 'md',
  showPercentage = true,
  delay = 0,
}: CircularScoreProps) {
  const config = sizeConfig[size];
  const normalizedRadius = config.radius - config.strokeWidth / 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  const scoreColor = getScoreColor(score);
  const gradient = getScoreGradient(score);

  return (
    <div className="flex flex-col items-center gap-3">
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay, duration: 0.5, type: 'spring' }}
        className="relative"
      >
        <svg
          height={config.radius * 2}
          width={config.radius * 2}
          className="transform -rotate-90"
        >
          {/* Background circle */}
          <circle
            stroke="oklch(var(--color-muted) / 0.3)"
            fill="transparent"
            strokeWidth={config.strokeWidth}
            r={normalizedRadius}
            cx={config.radius}
            cy={config.radius}
          />
          
          {/* Animated progress circle */}
          <motion.circle
            stroke={`url(#gradient-${label})`}
            fill="transparent"
            strokeWidth={config.strokeWidth}
            strokeDasharray={`${circumference} ${circumference}`}
            strokeLinecap="round"
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ delay: delay + 0.3, duration: 1.5, ease: 'easeOut' }}
            r={normalizedRadius}
            cx={config.radius}
            cy={config.radius}
          />
          
          {/* Gradient definition */}
          <defs>
            <linearGradient id={`gradient-${label}`} x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor={gradient.from} />
              <stop offset="100%" stopColor={gradient.to} />
            </linearGradient>
          </defs>
        </svg>

        {/* Score text in center */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: delay + 0.5, duration: 0.5 }}
          className="absolute inset-0 flex items-center justify-center"
        >
          <span className={`font-bold ${config.fontSize} ${scoreColor}`}>
            {Math.round(score)}
            {showPercentage && <span className="text-sm">%</span>}
          </span>
        </motion.div>
      </motion.div>

      {/* Label */}
      <motion.p
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: delay + 0.7, duration: 0.5 }}
        className="text-sm font-medium text-center text-muted-foreground"
      >
        {label}
      </motion.p>
    </div>
  );
}
