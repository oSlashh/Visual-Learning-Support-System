import { Component } from '@angular/core';
import { UploadComponent } from '../upload/upload.component';

@Component({
  selector: 'app-home',
  imports: [UploadComponent],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent {}
