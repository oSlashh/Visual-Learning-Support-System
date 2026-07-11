export interface Concept {
  text: string;
  frequency: number;
  importance: number;
}

export interface StudySummary {
  overview: string;
  keyPoints: string[];
}

export interface DocumentData {
  originalFilename: string;
  storedFilename: string;
  pages: number | null;
  wordCount: number | null;
  preview: string;
  
  // NLP Preprocessing metrics (calculated in Phase 4)
  totalWords?: number | null;
  meaningfulWords?: number | null;
  removedStopwords?: number | null;
  
  // Concept Discovery metrics (calculated in Phase 5)
  concepts?: Concept[];
  
  // Study Summary (calculated in Phase 6)
  summary?: StudySummary;
}


