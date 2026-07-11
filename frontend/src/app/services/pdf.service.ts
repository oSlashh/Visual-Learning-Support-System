import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class PdfService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  /**
   * Fetches backend API health status.
   */
  getHealth(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/health`);
  }

  /**
   * Uploads a PDF file to the backend for note generation.
   * Placeholder for Phase 2 implementation.
   */
  uploadPdf(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('pdf', file);
    return this.http.post<any>(`${this.apiUrl}/upload`, formData);
  }
}
