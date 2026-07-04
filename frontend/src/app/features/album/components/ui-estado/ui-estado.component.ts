import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';

type TipoEstado = 'loading' | 'erro' | 'vazio';

/** Estados de tela reutilizáveis: carregando (skeleton), erro (retry) e vazio. */
@Component({
  selector: 'app-ui-estado',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (tipo === 'loading') {
      <div class="grid grid-cols-2 gap-3 sm:grid-cols-[repeat(auto-fill,minmax(9rem,1fr))] sm:gap-4" aria-hidden="true">
        @for (s of skeletons; track s) {
          <div class="rounded-card border border-border bg-surface p-2 shadow-sm">
            <div class="aspect-[3/4] animate-pulse rounded-xl bg-surface-2"></div>
            <div class="mt-2 h-3 w-2/3 animate-pulse rounded bg-surface-2"></div>
          </div>
        }
      </div>
      <p class="sr-only">Carregando figurinhas…</p>
    } @else if (tipo === 'erro') {
      <div class="mx-auto max-w-md py-16 text-center">
        <p class="text-lg font-semibold text-ink">{{ mensagem || 'Algo deu errado.' }}</p>
        <p class="mt-1 text-sm text-muted">Verifique sua conexão e tente novamente.</p>
        <button
          type="button"
          class="mt-5 inline-flex min-h-[44px] items-center rounded-lg bg-brand-600 px-5 font-semibold text-white transition-colors hover:bg-brand-700"
          (click)="retry.emit()"
        >
          Tentar novamente
        </button>
      </div>
    } @else {
      <div class="mx-auto max-w-md py-16 text-center">
        <p class="text-lg font-semibold text-ink">Nenhuma figurinha encontrada</p>
        <p class="mt-1 text-sm text-muted">{{ mensagem || 'Ajuste ou limpe os filtros para ver o catálogo completo.' }}</p>
        <button
          type="button"
          class="mt-5 inline-flex min-h-[44px] items-center rounded-lg border border-border bg-surface px-5 font-semibold text-brand-600 transition-colors hover:border-brand-500"
          (click)="limparFiltros.emit()"
        >
          Limpar filtros
        </button>
      </div>
    }
  `,
})
export class UiEstadoComponent {
  @Input() tipo: TipoEstado = 'loading';
  @Input() mensagem?: string;
  @Output() retry = new EventEmitter<void>();
  @Output() limparFiltros = new EventEmitter<void>();

  protected readonly skeletons = Array.from({ length: 12 }, (_, i) => i);
}
