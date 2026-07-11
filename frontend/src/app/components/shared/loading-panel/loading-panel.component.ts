import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-loading-panel',
  standalone: true,
  templateUrl: './loading-panel.component.html',
  styleUrl: './loading-panel.component.scss'
})
export class LoadingPanelComponent {
  @Input() message: string = '';
  @Input() subtext: string = '';
}
