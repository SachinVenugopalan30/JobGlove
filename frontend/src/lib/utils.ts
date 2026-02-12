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

export function getScoreGradient(score: number): { from: string; to: string; className: string } {
  if (score >= 80) return { from: "#22c55e", to: "#10b981", className: "from-green-500 to-emerald-600" }
  if (score >= 60) return { from: "#3b82f6", to: "#4f46e5", className: "from-blue-500 to-indigo-600" }
  if (score >= 40) return { from: "#eab308", to: "#f97316", className: "from-yellow-500 to-orange-600" }
  return { from: "#ef4444", to: "#f43f5e", className: "from-red-500 to-rose-600" }
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}
