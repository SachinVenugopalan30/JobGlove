import { useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { FileEdit, PlusCircle, Sparkles } from 'lucide-react';
import { slideUp, staggerContainer } from '@/lib/animations';

export default function Landing() {
  const navigate = useNavigate();

  useEffect(() => {
    document.title = 'JobGlove';
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <motion.header
        className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60"
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-primary" />
            <h1 className="text-2xl font-bold">JobGlove</h1>
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center p-4">
        <motion.div
          className="max-w-5xl w-full"
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
        >
          {/* Hero Section */}
          <motion.div className="text-center mb-12" variants={slideUp}>
            <h2 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
              AI-Powered Resume Tailoring
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Transform your resume to perfectly match any job description using advanced AI technology
            </p>
          </motion.div>

          {/* Options Grid */}
          <motion.div
            className="grid md:grid-cols-2 gap-6"
            variants={staggerContainer}
          >
            {/* Tailor Existing Resume */}
            <motion.div variants={slideUp}>
              <Card className="h-full hover:shadow-lg transition-shadow cursor-pointer group">
                <CardHeader>
                  <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                    <FileEdit className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle>Tailor Existing Resume</CardTitle>
                  <CardDescription>
                    Upload your resume and job description to get an AI-optimized version with before/after scoring
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button
                    className="w-full"
                    size="lg"
                    onClick={() => navigate('/tailor')}
                  >
                    Get Started
                  </Button>
                  <div className="mt-4 space-y-2 text-sm text-muted-foreground">
                    <div className="flex items-center gap-2">
                      <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                      <span>AI scores before & after tailoring</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                      <span>One-click AI optimization</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                      <span>PDF & LaTeX download</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            {/* Create New Resume */}
            <motion.div variants={slideUp}>
              <Card className="h-full opacity-60 cursor-not-allowed">
                <CardHeader>
                  <div className="h-12 w-12 rounded-lg bg-muted flex items-center justify-center mb-4">
                    <PlusCircle className="h-6 w-6 text-muted-foreground" />
                  </div>
                  <CardTitle>Create New Resume</CardTitle>
                  <CardDescription>
                    Build a professional resume from scratch with AI assistance
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button
                    className="w-full"
                    size="lg"
                    disabled
                  >
                    Coming Soon
                  </Button>
                  <p className="mt-4 text-sm text-muted-foreground text-center">
                    This feature is under development
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          </motion.div>
        </motion.div>
      </main>

      {/* Footer */}
      <motion.footer
        className="border-t py-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
      >
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>Open source resume tailoring tool powered by AI</p>
        </div>
      </motion.footer>
    </div>
  );
}
