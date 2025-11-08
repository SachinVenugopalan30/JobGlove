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
