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
}
