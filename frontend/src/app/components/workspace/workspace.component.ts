import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DocumentData } from '../../models/document-data.interface';

@Component({
  selector: 'app-workspace',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './workspace.component.html',
  styleUrl: './workspace.component.scss'
})
export class WorkspaceComponent {
  @Input() data: DocumentData | null = null;
  @Input() file: File | null = null;
}
