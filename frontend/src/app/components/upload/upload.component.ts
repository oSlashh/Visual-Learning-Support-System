import { Component, signal } from '@angular/core';
import { PdfService } from '../../services/pdf.service';

@Component({
  selector: 'app-upload',
  imports: [],
  templateUrl: './upload.component.html',
  styleUrl: './upload.component.scss'
})
export class UploadComponent {
  // Define upload lifecycle signals
  uploadStatus = signal<'idle' | 'selected' | 'uploading' | 'uploaded' | 'error'>('idle');
  selectedFile = signal<File | null>(null);
  originalFilename = signal<string>('');
  storedFilename = signal<string>('');
  errorMessage = signal<string>('');

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
      this.uploadStatus.set('error');
      this.selectedFile.set(null);
      return;
    }

    this.selectedFile.set(file);
    this.originalFilename.set(file.name);
    this.uploadStatus.set('selected');
    this.errorMessage.set('');
  }

  /**
   * Triggers the multipart upload request to the Flask server.
   */
  uploadFile(): void {
    const file = this.selectedFile();
    if (!file) return;

    this.uploadStatus.set('uploading');

    this.pdfService.uploadPdf(file).subscribe({
      next: (response) => {
        if (response.status === 'success') {
          this.originalFilename.set(response.original_filename);
          this.storedFilename.set(response.stored_filename);
          this.uploadStatus.set('uploaded');
        } else {
          this.errorMessage.set(response.message || 'An error occurred during file upload.');
          this.uploadStatus.set('error');
        }
      },
      error: (err) => {
        console.error('File upload failed:', err);
        const serverError = err.error?.message || 'Backend connection failed. Please ensure the Flask server is running.';
        this.errorMessage.set(serverError);
        this.uploadStatus.set('error');
      }
    });
  }

  /**
   * Resets the component state to allow uploading another file.
   */
  resetUpload(): void {
    this.uploadStatus.set('idle');
    this.selectedFile.set(null);
    this.originalFilename.set('');
    this.storedFilename.set('');
    this.errorMessage.set('');
  }
}
