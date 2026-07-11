import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PipelineStep } from '../../../models/pipeline-step.interface';

@Component({
  selector: 'app-pipeline-status',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './pipeline-status.component.html',
  styleUrl: './pipeline-status.component.scss'
})
export class PipelineStatusComponent {
  @Input() steps: PipelineStep[] = [];
}
