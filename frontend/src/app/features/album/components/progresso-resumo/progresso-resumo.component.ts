import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { Progresso } from '../../models/progresso.model';

/** Resumo de progresso: percentual, totais e avanço por seleção. */
@Component({
  selector: 'app-progresso-resumo',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <section
      class="rounded-2xl bg-gradient-to-br from-success-700 via-success-600 to-success-500 p-4 text-white shadow-md sm:p-6"
      aria-label="Progresso da coleção"
    >
      @if (progresso) {
        <div class="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-white/80">Sua coleção</p>
            <p class="mt-1 font-display text-3xl font-bold leading-none tabular-nums sm:text-4xl">
              {{ progresso.total_possuidas }}<span class="text-white/60"> / {{ progresso.total }}</span>
            </p>
            <p class="mt-1 text-sm text-white/80 tabular-nums">
              <b class="text-white">{{ progresso.total_faltantes }}</b> faltando ·
              <b class="text-white">{{ repetidas }}</b> repetidas
            </p>
          </div>
          <div class="font-display text-5xl font-bold leading-none tabular-nums sm:text-6xl">
            {{ progresso.percentual }}<span class="text-2xl text-white/70">%</span>
          </div>
        </div>

        <div class="mt-4 h-3 overflow-hidden rounded-full bg-white/20">
          <div
            class="h-full rounded-full bg-white transition-[width] duration-500"
            [style.width.%]="progresso.percentual"
          ></div>
        </div>

        @if (progresso.por_team.length) {
          <details class="mt-4 group">
            <summary class="cursor-pointer select-none text-sm font-semibold text-white/90">
              Progresso por seleção
            </summary>
            <ul class="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
              @for (t of progresso.por_team; track t.team) {
                <li class="flex items-center gap-2 text-sm">
                  <span class="w-28 shrink-0 truncate text-white">{{ t.team }}</span>
                  <span class="h-2 flex-1 overflow-hidden rounded-full bg-white/20">
                    <span class="block h-full rounded-full bg-white" [style.width.%]="t.percentual"></span>
                  </span>
                  <span class="w-14 shrink-0 text-right text-white/70 tabular-nums">{{ t.possuidas }}/{{ t.total }}</span>
                </li>
              }
            </ul>
          </details>
        }
      } @else {
        <div class="h-20 animate-pulse rounded-xl bg-white/20" aria-hidden="true"></div>
      }
    </section>
  `,
})
export class ProgressoResumoComponent {
  @Input() progresso: Progresso | null = null;
  /** Total de repetidas (soma de quantidade-1); calculado na página a partir do catálogo. */
  @Input() repetidas = 0;
}
