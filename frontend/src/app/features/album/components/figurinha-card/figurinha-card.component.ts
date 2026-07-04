import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import { Figurinha } from '../../models/figurinha.model';
import { badgeRepetida } from '../../album.logic';

const PLACEHOLDER = 'assets/placeholder-figurinha.svg';

/** Card estilo sticker: imagem, código/nome, estados tenho/falta/especial/repetida e controles +/-. */
@Component({
  selector: 'app-figurinha-card',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: { class: 'block' },
  template: `
    <article
      class="relative flex flex-col gap-2 rounded-card border bg-surface p-2 shadow-sm transition-transform duration-150"
      [class.border-border]="!figurinha.especial"
      [class.border-accent-400]="figurinha.especial"
      [class.hover:-translate-y-1]="figurinha.possuo"
      [class.ring-2]="figurinha.especial"
      [class.ring-accent-400]="figurinha.especial"
      [class.ring-1]="figurinha.possuo && !figurinha.especial"
      [class.ring-success-500]="figurinha.possuo && !figurinha.especial"
    >
      <!-- Painel da imagem -->
      <div
        class="relative grid aspect-[3/4] place-items-center overflow-hidden rounded-xl bg-surface-2"
        [class.grayscale]="!figurinha.possuo"
        [class.opacity-60]="!figurinha.possuo"
      >
        <img
          [src]="src"
          [alt]="figurinha.name"
          loading="lazy"
          class="h-full w-full object-cover"
          (error)="aoFalharImagem()"
        />

        @if (figurinha.especial) {
          <span
            class="absolute left-2 top-2 flex items-center gap-1 rounded-full bg-accent-500 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-white shadow-sm"
            >★ Especial</span
          >
        }
        @if (badge) {
          <span
            class="absolute right-2 top-2 grid h-6 min-w-[24px] place-items-center rounded-full bg-brand-600 px-1.5 font-display text-xs font-bold text-white shadow-sm tabular-nums"
            [attr.aria-label]="figurinha.quantidade + ' unidades'"
            >{{ badge }}</span
          >
        }
      </div>

      <!-- Código + nome -->
      <div class="flex items-baseline justify-between gap-2 px-0.5">
        <span class="font-display text-sm font-bold tracking-wide text-brand-600">{{ figurinha.code }}</span>
        <span class="truncate text-xs font-semibold text-ink" [title]="figurinha.name">{{ figurinha.name }}</span>
      </div>

      <!-- Controles de posse -->
      <div class="flex items-center gap-1.5">
        <button
          type="button"
          class="grid min-h-[44px] flex-1 place-items-center rounded-lg border border-border bg-surface-2 text-lg font-semibold text-ink transition-colors hover:border-danger hover:text-danger disabled:opacity-40 disabled:hover:border-border disabled:hover:text-ink"
          [disabled]="figurinha.quantidade === 0 || ocupado"
          [attr.aria-label]="'Remover uma de ' + figurinha.name"
          (click)="decrementar.emit(figurinha.code)"
        >
          −
        </button>
        <span class="min-w-[2rem] text-center font-display text-base font-bold tabular-nums" aria-live="polite">{{
          figurinha.quantidade
        }}</span>
        <button
          type="button"
          class="grid min-h-[44px] flex-1 place-items-center rounded-lg border border-brand-600 bg-brand-600 text-lg font-semibold text-white transition-colors hover:bg-brand-700 disabled:opacity-40"
          [disabled]="ocupado"
          [attr.aria-label]="'Adicionar uma de ' + figurinha.name"
          (click)="incrementar.emit(figurinha.code)"
        >
          +
        </button>
      </div>
    </article>
  `,
})
export class FigurinhaCardComponent {
  @Input({ required: true }) figurinha!: Figurinha;
  /** Bloqueia os botões enquanto uma mutação está em voo (evita cliques duplos). */
  @Input() ocupado = false;

  @Output() incrementar = new EventEmitter<string>();
  @Output() decrementar = new EventEmitter<string>();

  private falhou = false;

  get src(): string {
    return this.falhou || !this.figurinha.imagem ? PLACEHOLDER : this.figurinha.imagem;
  }

  get badge(): string | null {
    return badgeRepetida(this.figurinha);
  }

  aoFalharImagem(): void {
    this.falhou = true;
  }
}
