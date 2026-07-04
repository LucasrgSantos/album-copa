import { ChangeDetectionStrategy, Component, OnInit, computed, inject, signal } from '@angular/core';

import { FigurinhasService } from '../../../../core/services/figurinhas.service';
import { ErroAmigavel } from '../../../../core/http/erro.interceptor';
import { agruparPorSelecao, aplicarFiltros } from '../../album.logic';
import { EstadoTela, FiltrosAlbum, FILTROS_PADRAO } from '../../models/album-view.model';
import { Time } from '../../models/time.model';

import { FigurinhaCardComponent } from '../../components/figurinha-card/figurinha-card.component';
import { FiltrosAlbumComponent } from '../../components/filtros-album/filtros-album.component';
import { ProgressoResumoComponent } from '../../components/progresso-resumo/progresso-resumo.component';
import { UiEstadoComponent } from '../../components/ui-estado/ui-estado.component';

@Component({
  selector: 'app-album-page',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [FigurinhaCardComponent, FiltrosAlbumComponent, ProgressoResumoComponent, UiEstadoComponent],
  template: `
    <!-- App bar (azul Hermes — identidade estrutural, faixa tricolor da marca) -->
    <header class="sticky top-0 z-40 bg-brand-600 text-white shadow-lg">
      <div class="mx-auto flex h-16 max-w-[1240px] items-center gap-4 px-4 sm:px-7">
        <div class="flex items-center gap-3">
          <span class="grid h-9 w-9 place-items-center rounded-lg border border-white/40 bg-white/10 font-display text-base font-extrabold" aria-hidden="true">C26</span>
          <span class="font-display text-xl font-bold uppercase tracking-wide">Álbum <span class="text-white/70">2026</span></span>
        </div>
        <span class="flex-1"></span>
        @if (progresso()) {
          <div class="hidden items-center gap-2 rounded-full border border-white/25 bg-white/10 px-3 py-1.5 sm:flex" aria-hidden="true">
            <span class="font-display text-lg font-bold tabular-nums">{{ progresso()!.percentual }}%</span>
            <div class="h-2 w-24 overflow-hidden rounded-full bg-white/25">
              <div class="h-full rounded-full bg-success-500 transition-[width] duration-500" [style.width.%]="progresso()!.percentual"></div>
            </div>
          </div>
        }
        <button
          type="button"
          class="grid h-10 w-10 place-items-center rounded-lg border border-white/40 bg-white/10 text-white transition-colors hover:bg-white/20"
          aria-label="Alternar tema claro/escuro"
          (click)="alternarTema()"
        >
          ◐
        </button>
      </div>
      <span
        class="pointer-events-none absolute inset-x-0 bottom-0 h-[4px] bg-[linear-gradient(90deg,var(--success-500)_0_34%,#ffffff_34%_66%,var(--accent-500)_66%_100%)]"
        aria-hidden="true"
      ></span>
    </header>

    <main class="mx-auto max-w-[1240px] px-4 pb-20 pt-6 sm:px-7">
      <app-progresso-resumo [progresso]="progresso()" [repetidas]="repetidas()" />

      <div class="sticky top-16 z-30 -mx-4 bg-canvas px-4 py-3 sm:mx-0 sm:px-0">
        <app-filtros-album [times]="times()" [filtros]="filtros()" (filtrosChange)="filtros.set($event)" (limpar)="limparFiltros()" />
      </div>

      @if (estado() === 'loading') {
        <app-ui-estado tipo="loading" />
      } @else if (estado() === 'erro') {
        <app-ui-estado tipo="erro" [mensagem]="erroMsg()" (retry)="carregar()" />
      } @else if (semResultado()) {
        <app-ui-estado tipo="vazio" (limparFiltros)="limparFiltros()" />
      } @else {
        @for (grupo of grupos(); track grupo.team) {
          <section class="mt-6">
            <div class="mb-3 flex items-center gap-3">
              @if (bandeiras().get(grupo.team); as bandeira) {
                <img
                  [src]="bandeira"
                  alt=""
                  class="h-5 w-auto rounded-sm border border-border object-contain"
                  loading="lazy"
                />
              }
              <h2 class="font-display text-xl font-bold uppercase tracking-wide">{{ grupo.team }}</h2>
              <span class="ml-auto text-sm font-semibold text-muted tabular-nums">
                <b class="text-brand-600">{{ grupo.possuidas }}</b> / {{ grupo.total }}
              </span>
            </div>
            <div class="grid grid-cols-2 gap-3 sm:grid-cols-[repeat(auto-fill,minmax(9rem,1fr))] sm:gap-4">
              @for (f of grupo.figurinhas; track f.code) {
                <app-figurinha-card
                  [figurinha]="f"
                  [ocupado]="ocupado().has(f.code)"
                  (incrementar)="onIncrementar($event)"
                  (decrementar)="onDecrementar($event)"
                />
              }
            </div>
          </section>
        }
      }
    </main>

    @if (toast()) {
      <div class="fixed bottom-6 left-1/2 z-50 -translate-x-1/2 rounded-full bg-danger px-4 py-2 text-sm font-semibold text-white shadow-lg" role="alert">
        {{ toast() }}
      </div>
    }
  `,
})
export class AlbumPageComponent implements OnInit {
  private readonly service = inject(FigurinhasService);

  protected readonly progresso = this.service.progresso;
  protected readonly filtros = signal<FiltrosAlbum>({ ...FILTROS_PADRAO });
  protected readonly times = signal<Time[]>([]);
  protected readonly estado = signal<EstadoTela>('loading');
  protected readonly erroMsg = signal<string>('');
  protected readonly ocupado = signal<ReadonlySet<string>>(new Set());
  protected readonly toast = signal<string>('');

  protected readonly grupos = computed(() =>
    agruparPorSelecao(aplicarFiltros(this.service.catalogo(), this.filtros())),
  );
  /** team → URL da bandeira (das seleções carregadas), para o cabeçalho de cada grupo. */
  protected readonly bandeiras = computed(
    () => new Map(this.times().map((t) => [t.team, t.bandeira])),
  );
  protected readonly semResultado = computed(
    () => this.service.carregado() && this.grupos().length === 0,
  );
  protected readonly repetidas = computed(() =>
    this.service.catalogo().reduce((soma, f) => soma + Math.max(0, f.quantidade - 1), 0),
  );

  ngOnInit(): void {
    void this.carregar();
  }

  async carregar(): Promise<void> {
    this.estado.set('loading');
    try {
      const [, , times] = await Promise.all([
        this.service.carregarCatalogo(),
        this.service.obterProgresso(),
        this.service.obterTimes(),
      ]);
      this.times.set(times);
      this.estado.set('ok');
    } catch (e) {
      this.erroMsg.set(this.msg(e));
      this.estado.set('erro');
    }
  }

  onIncrementar(code: string): void {
    void this.mutar(code, () => this.service.incrementar(code));
  }

  onDecrementar(code: string): void {
    void this.mutar(code, () => this.service.decrementar(code));
  }

  private async mutar(code: string, acao: () => Promise<unknown>): Promise<void> {
    this.marcarOcupado(code, true);
    try {
      await acao();
      await this.service.obterProgresso();
    } catch (e) {
      this.mostrarToast(this.msg(e));
    } finally {
      this.marcarOcupado(code, false);
    }
  }

  limparFiltros(): void {
    this.filtros.set({ ...FILTROS_PADRAO });
  }

  alternarTema(): void {
    const el = document.documentElement;
    const escuro = el.classList.contains('dark');
    el.classList.remove('dark', 'light');
    el.classList.add(escuro ? 'light' : 'dark');
  }

  private marcarOcupado(code: string, ocupado: boolean): void {
    this.ocupado.update((set) => {
      const proximo = new Set(set);
      if (ocupado) proximo.add(code);
      else proximo.delete(code);
      return proximo;
    });
  }

  private mostrarToast(mensagem: string): void {
    this.toast.set(mensagem);
    setTimeout(() => this.toast.set(''), 3000);
  }

  private msg(e: unknown): string {
    return (e as ErroAmigavel)?.mensagem ?? 'Algo deu errado. Tente novamente.';
  }
}
