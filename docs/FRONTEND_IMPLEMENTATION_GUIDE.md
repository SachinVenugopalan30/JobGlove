# JobGlove Frontend Implementation Guide
## React + TypeScript + shadcn/ui + Tailwind CSS + Framer Motion

This guide will help you build a modern, beautiful, animated frontend for JobGlove.

---

## Table of Contents
1. [File Structure](#file-structure)
2. [shadcn/ui Component Setup](#shadcnui-component-setup)
3. [TypeScript Types](#typescript-types)
4. [Utility Functions](#utility-functions)
5. [Routing Setup](#routing-setup)
6. [API Integration](#api-integration)
7. [Components Implementation](#components-implementation)
8. [Pages Implementation](#pages-implementation)
9. [Animation Patterns](#animation-patterns)
10. [Implementation Order](#implementation-order)

---

## File Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/                      # shadcn components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   ├── progress.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── separator.tsx
│   │   │   ├── skeleton.tsx
│   │   │   └── textarea.tsx
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   └── Footer.tsx
│   │   ├── tailor/
│   │   │   ├── StepIndicator.tsx
│   │   │   ├── UploadStep.tsx
│   │   │   ├── ScoreStep.tsx
│   │   │   ├── TailorStep.tsx
│   │   │   └── DownloadStep.tsx
│   │   ├── score/
│   │   │   ├── CircularScore.tsx
│   │   │   ├── ScoreBreakdown.tsx
│   │   │   ├── KeywordBadges.tsx
│   │   │   └── Recommendations.tsx
│   │   └── animations/
│   │       └── PageTransition.tsx
│   ├── pages/
│   │   ├── Landing.tsx
│   │   ├── Tailor.tsx
│   │   └── NotFound.tsx
│   ├── lib/
│   │   ├── utils.ts                 # cn() utility
│   │   ├── api.ts                   # API client
│   │   └── animations.ts            # Animation variants
│   ├── types/
│   │   ├── resume.ts
│   │   ├── score.ts
│   │   └── api.ts
│   ├── hooks/
│   │   ├── useApi.ts
│   │   └── useFileUpload.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

---

## shadcn/ui Component Setup

### 1. Install shadcn CLI (if not already)
```bash
npm install -D @shadcn/ui
```

### 2. Initialize shadcn configuration

Create `components.json`:
```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": false,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.js",
    "css": "src/index.css",
    "baseColor": "blue",
    "cssVariables": true
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils"
  }
}
```

### 3. Update tsconfig.json for path aliases
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### 4. Update vite.config.ts for path aliases
```typescript
import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
})
```

### 5. Add shadcn components
```bash
# You would manually create these or use shadcn CLI
# For this guide, we'll create them manually
```

---

## TypeScript Types

### `src/types/resume.ts`
```typescript
export interface ResumeData {
  name?: string;
  email?: string;
  phone?: string;
}

export interface UploadResponse {
  file_path: string;
  filename: string;
}
```

### `src/types/score.ts`
```typescript
export interface KeywordMatchDetails {
  matched: string[];
  missing: string[];
  match_percentage: number;
}

export interface RelevanceDetails {
  similarity_score: number;
  keyword_density: number;
}

export interface ATSDetails {
  issues: string[];
  recommendations: string[];
}

export interface QualityDetails {
  quantified_achievements: number;
  action_verbs_count: number;
  readability_score: number;
  word_count: number;
}

export interface Score {
  total_score: number;
  keyword_match_score: number;
  keyword_match_details: KeywordMatchDetails;
  relevance_score: number;
  relevance_details?: RelevanceDetails;
  ats_score: number;
  ats_details?: ATSDetails;
  quality_score: number;
  quality_details?: QualityDetails;
  recommendations: string[];
}

export interface AnalyzeResponse {
  extracted_data: {
    name?: string;
    email?: string;
    phone?: string;
  };
  score: Score;
}
```

### `src/types/api.ts`
```typescript
export interface ApiError {
  error: string;
}

export interface TailorRequest {
  file_path: string;
  job_description: string;
  api: 'openai' | 'gemini' | 'claude';
  user_name: string;
  company: string;
  job_title: string;
  custom_prompt?: string;
}

export interface TailorResponse {
  pdf_file: string;
  tex_file: string;
  original_text: string;
  tailored_text: string;
  tailored_score: Score;
  message: string;
}
```

---

## Utility Functions

### `src/lib/utils.ts`
```typescript
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function getScoreColor(score: number): string {
  if (score >= 80) return "text-green-600"
  if (score >= 60) return "text-blue-600"
  if (score >= 40) return "text-yellow-600"
  return "text-red-600"
}

export function getScoreGradient(score: number): string {
  if (score >= 80) return "from-green-500 to-emerald-600"
  if (score >= 60) return "from-blue-500 to-indigo-600"
  if (score >= 40) return "from-yellow-500 to-orange-600"
  return "from-red-500 to-rose-600"
}
```

### `src/lib/animations.ts`
```typescript
import { Variants } from "framer-motion"

export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { duration: 0.5 }
  }
}

export const slideUp: Variants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: { duration: 0.5 }
  }
}

export const scaleIn: Variants = {
  hidden: { scale: 0.9, opacity: 0 },
  visible: {
    scale: 1,
    opacity: 1,
    transition: { duration: 0.3 }
  }
}

export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
}

export const scoreAnimation: Variants = {
  hidden: { scale: 0, rotate: -180 },
  visible: {
    scale: 1,
    rotate: 0,
    transition: {
      type: "spring",
      stiffness: 260,
      damping: 20
    }
  }
}
```

---

## API Integration

### `src/lib/api.ts`
```typescript
import {
  AnalyzeResponse,
  TailorRequest,
  TailorResponse,
  UploadResponse
} from '@/types/api';

const API_BASE = '/api';

export class ApiClient {
  static async checkApis(): Promise<Record<string, boolean>> {
    const response = await fetch(`${API_BASE}/check-apis`);
    if (!response.ok) throw new Error('Failed to check APIs');
    return response.json();
  }

  static async uploadResume(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE}/upload-resume`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Upload failed');
    }

    return response.json();
  }

  static async analyzeResume(
    filePath: string,
    jobDescription: string
  ): Promise<AnalyzeResponse> {
    const response = await fetch(`${API_BASE}/analyze-resume`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        file_path: filePath,
        job_description: jobDescription,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Analysis failed');
    }

    return response.json();
  }

  static async tailorResume(data: TailorRequest): Promise<TailorResponse> {
    const response = await fetch(`${API_BASE}/tailor-resume`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Tailoring failed');
    }

    return response.json();
  }

  static getDownloadUrl(filename: string): string {
    return `${API_BASE}/download/${filename}`;
  }
}
```

---

## Routing Setup

### `src/App.tsx`
```typescript
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import Landing from './pages/Landing';
import Tailor from './pages/Tailor';
import NotFound from './pages/NotFound';

function App() {
  return (
    <Router>
      <AnimatePresence mode="wait">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/tailor" element={<Tailor />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </AnimatePresence>
    </Router>
  );
}

export default App;
```

### `src/main.tsx`
```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

---

## Components Implementation

### shadcn Button Component: `src/components/ui/button.tsx`
```typescript
import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
```

### Card Component: `src/components/ui/card.tsx`
```typescript
import * as React from "react"
import { cn } from "@/lib/utils"

const Card = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "rounded-lg border bg-card text-card-foreground shadow-sm",
      className
    )}
    {...props}
  />
))
Card.displayName = "Card"

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-1.5 p-6", className)}
    {...props}
  />
))
CardHeader.displayName = "CardHeader"

const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      "text-2xl font-semibold leading-none tracking-tight",
      className
    )}
    {...props}
  />
))
CardTitle.displayName = "CardTitle"

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
))
CardDescription.displayName = "CardDescription"

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
))
CardContent.displayName = "CardContent"

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center p-6 pt-0", className)}
    {...props}
  />
))
CardFooter.displayName = "CardFooter"

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent }
```

### Circular Score Component: `src/components/score/CircularScore.tsx`
```typescript
import { motion } from 'framer-motion';
import { cn, getScoreColor, getScoreGradient } from '@/lib/utils';

interface CircularScoreProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  label?: string;
}

export function CircularScore({ score, size = 'lg', label }: CircularScoreProps) {
  const radius = size === 'sm' ? 40 : size === 'md' ? 60 : 80;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  const sizeClasses = {
    sm: 'w-32 h-32 text-2xl',
    md: 'w-40 h-40 text-3xl',
    lg: 'w-52 h-52 text-5xl',
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <motion.div
        className={cn("relative", sizeClasses[size])}
        initial={{ scale: 0, rotate: -180 }}
        animate={{ scale: 1, rotate: 0 }}
        transition={{
          type: "spring",
          stiffness: 260,
          damping: 20,
          delay: 0.2,
        }}
      >
        <svg className="w-full h-full -rotate-90">
          <circle
            cx="50%"
            cy="50%"
            r={radius}
            stroke="currentColor"
            strokeWidth="8"
            fill="none"
            className="text-muted"
          />
          <motion.circle
            cx="50%"
            cy="50%"
            r={radius}
            stroke="url(#gradient)"
            strokeWidth="8"
            fill="none"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.5, ease: "easeOut", delay: 0.5 }}
          />
          <defs>
            <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" className={cn("stop-color-1", getScoreGradient(score).split(' ')[0])} />
              <stop offset="100%" className={cn("stop-color-2", getScoreGradient(score).split(' ')[1])} />
            </linearGradient>
          </defs>
        </svg>

        <motion.div
          className="absolute inset-0 flex flex-col items-center justify-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
        >
          <span className={cn("font-bold", getScoreColor(score))}>
            {score}
          </span>
          <span className="text-sm text-muted-foreground">/100</span>
        </motion.div>
      </motion.div>

      {label && (
        <motion.p
          className="text-sm font-medium text-muted-foreground"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2 }}
        >
          {label}
        </motion.p>
      )}
    </div>
  );
}
```

---

## Pages Implementation

### Landing Page: `src/pages/Landing.tsx`
```typescript
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { FileEdit, PlusCircle, Sparkles } from 'lucide-react';
import { fadeIn, slideUp, staggerContainer } from '@/lib/animations';

export default function Landing() {
  const navigate = useNavigate();

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
              Transform your resume to perfectly match any job description using advanced AI and NLP technology
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
                    Upload your resume and job description to get an AI-optimized version with local NLP analysis
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
                      <span>Local NLP score analysis</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                      <span>AI-powered tailoring</span>
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
```

### Tailor Page Structure: `src/pages/Tailor.tsx`
```typescript
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import StepIndicator from '@/components/tailor/StepIndicator';
import UploadStep from '@/components/tailor/UploadStep';
import ScoreStep from '@/components/tailor/ScoreStep';
import TailorStep from '@/components/tailor/TailorStep';
import DownloadStep from '@/components/tailor/DownloadStep';
import { fadeIn } from '@/lib/animations';
import type { Score } from '@/types/score';

export default function Tailor() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [uploadedFilePath, setUploadedFilePath] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [originalScore, setOriginalScore] = useState<Score | null>(null);
  const [extractedData, setExtractedData] = useState<any>(null);
  const [tailoredScore, setTailoredScore] = useState<Score | null>(null);
  const [downloadUrls, setDownloadUrls] = useState<{
    pdf: string;
    tex: string;
  } | null>(null);

  const steps = [
    { number: 1, label: 'Upload' },
    { number: 2, label: 'Analyze' },
    { number: 3, label: 'Tailor' },
    { number: 4, label: 'Download' },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-background to-muted/20">
      {/* Header */}
      <motion.header
        className="border-b bg-background/95 backdrop-blur"
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
      >
        <div className="container mx-auto px-4 py-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/')}
            className="gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Back
          </Button>
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
          {/* Step Indicator */}
          <StepIndicator steps={steps} currentStep={currentStep} />

          {/* Step Content */}
          <AnimatePresence mode="wait">
            {currentStep === 1 && (
              <UploadStep
                key="upload"
                onComplete={(filePath, jobDesc) => {
                  setUploadedFilePath(filePath);
                  setJobDescription(jobDesc);
                  setCurrentStep(2);
                }}
              />
            )}

            {currentStep === 2 && (
              <ScoreStep
                key="score"
                filePath={uploadedFilePath}
                jobDescription={jobDescription}
                onComplete={(score, data) => {
                  setOriginalScore(score);
                  setExtractedData(data);
                  setCurrentStep(3);
                }}
                onBack={() => setCurrentStep(1)}
              />
            )}

            {currentStep === 3 && (
              <TailorStep
                key="tailor"
                filePath={uploadedFilePath}
                jobDescription={jobDescription}
                extractedData={extractedData}
                onComplete={(urls, score) => {
                  setDownloadUrls(urls);
                  setTailoredScore(score);
                  setCurrentStep(4);
                }}
                onBack={() => setCurrentStep(2)}
              />
            )}

            {currentStep === 4 && downloadUrls && (
              <DownloadStep
                key="download"
                downloadUrls={downloadUrls}
                originalScore={originalScore}
                tailoredScore={tailoredScore}
                onReset={() => {
                  setCurrentStep(1);
                  setUploadedFilePath('');
                  setJobDescription('');
                  setOriginalScore(null);
                  setTailoredScore(null);
                  setDownloadUrls(null);
                }}
              />
            )}
          </AnimatePresence>
        </motion.div>
      </main>
    </div>
  );
}
```

---

## Animation Patterns

### Score Animation with Framer Motion
```typescript
// Circular progress animation
<motion.circle
  initial={{ strokeDashoffset: circumference }}
  animate={{ strokeDashoffset: offset }}
  transition={{
    duration: 1.5,
    ease: "easeOut",
    delay: 0.5
  }}
/>

// Number count-up animation
<motion.span
  initial={{ opacity: 0, scale: 0.5 }}
  animate={{ opacity: 1, scale: 1 }}
  transition={{
    duration: 0.8,
    type: "spring",
    stiffness: 200
  }}
>
  {score}
</motion.span>

// Stagger children animation
<motion.div
  variants={{
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  }}
  initial="hidden"
  animate="visible"
>
  {items.map((item) => (
    <motion.div
      key={item.id}
      variants={{
        hidden: { y: 20, opacity: 0 },
        visible: { y: 0, opacity: 1 }
      }}
    >
      {item.content}
    </motion.div>
  ))}
</motion.div>
```

---

## Implementation Order

### Phase 1: Setup & Basic Structure (1-2 hours)
1. ✅ Create React + TypeScript project with Vite
2. ✅ Install Tailwind CSS and dependencies
3. ✅ Configure path aliases in tsconfig and vite.config
4. Create utility functions (`lib/utils.ts`, `lib/animations.ts`)
5. Create TypeScript types (`types/*.ts`)
6. Set up API client (`lib/api.ts`)

### Phase 2: shadcn Components (2-3 hours)
1. Create Button component
2. Create Card component
3. Create Input component
4. Create Textarea component
5. Create Badge component
6. Create Progress component
7. Create Separator component

### Phase 3: Layout & Routing (1 hour)
1. Set up React Router in `App.tsx`
2. Create Landing page
3. Create Tailor page shell
4. Create NotFound page

### Phase 4: Landing Page (1-2 hours)
1. Implement hero section
2. Add option cards with animations
3. Add footer
4. Test navigation

### Phase 5: Upload Step (2-3 hours)
1. Create file upload component
2. Add drag-and-drop functionality
3. Create job description textarea
4. Add validation
5. Integrate with API
6. Add loading states

### Phase 6: Score Step (3-4 hours)
1. Create CircularScore component
2. Create ScoreBreakdown component
3. Create KeywordBadges component
4. Create Recommendations component
5. Integrate with analyze API
6. Add animations

### Phase 7: Tailor Step (2-3 hours)
1. Create user info form
2. Create API selector
3. Create custom prompt textarea
4. Integrate with tailor API
5. Add loading states

### Phase 8: Download Step (2-3 hours)
1. Create download buttons
2. Create before/after score comparison
3. Add score improvement indicators
4. Add reset functionality

### Phase 9: Polish & Testing (2-3 hours)
1. Add error handling throughout
2. Improve loading states
3. Test all animations
4. Test on mobile
5. Fix responsive issues
6. Add final touches

**Total Estimated Time: 16-24 hours**

---

## Key Animation Tips

1. **Use Framer Motion variants** for reusable animations
2. **Stagger children** for list animations
3. **Spring animations** for score reveals
4. **Exit animations** with AnimatePresence for page transitions
5. **Loading skeletons** instead of spinners
6. **Micro-interactions** on buttons and cards (hover, active states)
7. **Progress indicators** for multi-step processes

---

## Next Steps

1. Start with Phase 1 (setup)
2. Implement components incrementally
3. Test each component before moving on
4. Use the API client for all backend interactions
5. Add error boundaries for production-ready code

---

## Additional Resources

- [shadcn/ui Documentation](https://ui.shadcn.com)
- [Framer Motion Documentation](https://www.framer.com/motion/)
- [Tailwind CSS Documentation](https://tailwindcss.com)
- [React Router Documentation](https://reactrouter.com)

---

Good luck with the implementation! The structure is set up, and you have all the code patterns you need. Follow the implementation order, and you'll have a beautiful, modern frontend in no time.
