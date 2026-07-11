import { Component, OnInit, signal } from '@angular/core';
import { PdfService } from './services/pdf.service';
import { HomeComponent } from './components/home/home.component';

@Component({
  selector: 'app-root',
  imports: [HomeComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class App implements OnInit {

  status = signal<'connecting' | 'connected' | 'error'>('connecting');
  serviceName = signal<string>('');
  version = signal<string>('');

  constructor(private pdfService: PdfService) {}

  ngOnInit(): void {
    this.checkBackendHealth();
  }

  checkBackendHealth(): void {
    this.status.set('connecting');
    this.pdfService.getHealth().subscribe({
      next: (data) => {
        this.status.set('connected');
        this.serviceName.set(data.service || 'SmartNotes AI Backend');
        this.version.set(data.version || '1.0.0');
      },
      error: (err) => {
        console.error('Backend health-check connection failed:', err);
        this.status.set('error');
        this.serviceName.set('Disconnected');
        this.version.set('');
      }
    });
  }
}


