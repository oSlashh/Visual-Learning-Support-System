import { Component, signal } from '@angular/core';
import { PdfService } from '../../services/pdf.service';
import { DocumentData } from '../../models/document-data.interface';

@Component({
  selector: 'app-upload',
  imports: [],
  templateUrl: './upload.component.html',
  styleUrl: './upload.component.scss'
})
export class UploadComponent {
  // Define processing lifecycle states
  processingState = signal<'idle' | 'selected' | 'uploading' | 'uploaded' | 'preprocessing' | 'preprocessed' | 'error'>('idle');
  selectedFile = signal<File | null>(null);
  errorMessage = signal<string>('');

  // Encapsulated document data model signal
  documentData = signal<DocumentData | null>(null);

  // Dynamic user-friendly progress loading message
  nlpLoadingMessage = signal<string>('Generating study material...');

  constructor(private pdfService: PdfService) {}


  /**
   * Triggered when a file is selected via the traditional file picker.
   */
  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.handleFile(input.files[0]);
    }
  }

  /**
   * Prevents browser default drag behavior to enable drop handling.
   */
  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
  }

  /**
   * Triggered when a file is dropped onto the drop zone.
   */
  onDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    if (event.dataTransfer && event.dataTransfer.files.length > 0) {
      this.handleFile(event.dataTransfer.files[0]);
    }
  }

  /**
   * Validates that the file is a PDF and updates signals accordingly.
   */
  private handleFile(file: File): void {
    // Check MIME type or file extension
    const isPdf = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
    
    if (!isPdf) {
      this.errorMessage.set('Invalid file format. Only PDF documents are allowed.');
      this.processingState.set('error');
      this.selectedFile.set(null);
      return;
    }

    this.selectedFile.set(file);
    this.documentData.set({
      originalFilename: file.name,
      storedFilename: '',
      pages: null,
      wordCount: null,
      preview: ''
    });
    this.processingState.set('selected');
    this.errorMessage.set('');
  }

  /**
   * Triggers the file upload and text extraction sequentially.
   */
  uploadFile(): void {
    const file = this.selectedFile();
    if (!file) return;

    this.processingState.set('uploading');

    // 1. Submit file to Flask Upload endpoint
    this.pdfService.uploadPdf(file).subscribe({
      next: (response) => {
        if (response.status === 'success') {
          this.documentData.set({
            originalFilename: response.original_filename,
            storedFilename: response.stored_filename,
            pages: null,
            wordCount: null,
            preview: ''
          });
          
          // 2. Trigger the local parsing endpoint immediately on success
          this.pdfService.processPdf(response.stored_filename).subscribe({
            next: (procResponse) => {
              if (procResponse.status === 'success') {
                const current = this.documentData();
                if (current) {
                  this.documentData.set({
                    ...current,
                    pages: procResponse.pages,
                    wordCount: procResponse.wordCount,
                    preview: procResponse.preview
                  });
                }
                this.processingState.set('uploaded');
              } else {
                this.errorMessage.set(procResponse.message || 'An error occurred during text extraction.');
                this.processingState.set('error');
              }
            },
            error: (procErr) => {
              console.error('File processing failed:', procErr);
              const procServerError = procErr.error?.message || 'Processing failed. Please check the backend console.';
              this.errorMessage.set(procServerError);
              this.processingState.set('error');
            }
          });
        } else {
          this.errorMessage.set(response.message || 'An error occurred during file upload.');
          this.processingState.set('error');
        }
      },
      error: (err) => {
        console.error('File upload failed:', err);
        const serverError = err.error?.message || 'Backend connection failed. Please ensure the Flask server is running.';
        this.errorMessage.set(serverError);
        this.processingState.set('error');
      }
    });
  }

  /**
   * Invokes the text cleaning/preprocessing NLP pipeline.
   */
  analyzeDocument(): void {
    const currentData = this.documentData();
    if (!currentData || !currentData.storedFilename) return;

    this.processingState.set('preprocessing');
    this.nlpLoadingMessage.set('Generating study material...');

    // Dynamic cycling of progress messages
    const loadingMessages = [
      'Generating study material...',
      'Finding meaningful words...',
      'Preparing your notes...'
    ];
    let msgIndex = 0;
    
    const messageInterval = setInterval(() => {
      msgIndex = (msgIndex + 1) % loadingMessages.length;
      this.nlpLoadingMessage.set(loadingMessages[msgIndex]);
    }, 1500);

    // Call the preprocessing API
    this.pdfService.preprocessText(currentData.storedFilename).subscribe({
      next: (response) => {
        clearInterval(messageInterval);
        if (response.status === 'success') {
          const current = this.documentData();
          if (current) {
            this.documentData.set({
              ...current,
              totalWords: response.totalWords,
              meaningfulWords: response.meaningfulWords,
              removedStopwords: response.removedStopwords
            });
          }
          this.processingState.set('preprocessed');
        } else {
          this.errorMessage.set(response.message || 'An error occurred during text cleaning.');
          this.processingState.set('error');
        }
      },
      error: (err) => {
        clearInterval(messageInterval);
        console.error('Document analysis failed:', err);
        const serverError = err.error?.message || 'NLP analysis failed. Please verify connection.';
        this.errorMessage.set(serverError);
        this.processingState.set('error');
      }
    });
  }

  /**
   * Resets all component state parameters to allow uploading another file.
   */
  resetUpload(): void {
    this.processingState.set('idle');
    this.selectedFile.set(null);
    this.errorMessage.set('');
    this.documentData.set(null);
    this.nlpLoadingMessage.set('Generating study material...');
  }

}
