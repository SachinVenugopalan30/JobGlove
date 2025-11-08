import { useEffect } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { FileQuestion } from 'lucide-react';
import { fadeIn, scaleIn } from '@/lib/animations';

export default function NotFound() {
  useEffect(() => {
    document.title = 'JobGlove - Page Not Found';
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <motion.div
        className="text-center"
        variants={fadeIn}
        initial="hidden"
        animate="visible"
      >
        <motion.div
          className="mb-6 flex justify-center"
          variants={scaleIn}
          initial="hidden"
          animate="visible"
        >
          <FileQuestion className="h-24 w-24 text-muted-foreground" />
        </motion.div>
        <h1 className="text-4xl font-bold mb-4">404 - Page Not Found</h1>
        <p className="text-muted-foreground mb-8">
          The page you're looking for doesn't exist.
        </p>
        <Link to="/">
          <Button size="lg">Go Home</Button>
        </Link>
      </motion.div>
    </div>
  );
}
