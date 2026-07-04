import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { FiltrosAlbum, StatusPosse } from '../../models/album-view.model';
import { Time } from '../../models/time.model';
import { temFiltroAtivo } from '../../album.logic';

/** Filtros da grade: status (chips), seleção (mat-select) e busca (nome/código) + limpar. */
@Component({
  selector: 'app-filtros-album',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [MatFormFieldModule, MatSelectModule],
  template: `
    <div class="flex flex-col gap-3 md:flex-row md:flex-wrap md:items-center">
      <!-- Status -->
      <div
        class="inline-flex justify-center rounded-full border border-border bg-surface-2 p-1"
        role="group"
        aria-label="Filtrar por status"
      >
        @for (op of statusOpcoes; track op.valor) {
          <button
            type="button"
            class="min-h-[40px] rounded-full px-4 text-sm font-semibold transition-colors"
            [class.bg-brand-600]="filtros.status === op.valor"
            [class.text-white]="filtros.status === op.valor"
            [class.text-muted]="filtros.status !== op.valor"
            [attr.aria-pressed]="filtros.status === op.valor"
            (click)="mudarStatus(op.valor)"
          >
            {{ op.rotulo }}
          </button>
        }
      </div>

      <!-- Seleção -->
      <mat-form-field
        class="filtro-selecao w-full md:w-56"
        appearance="fill"
        subscriptSizing="dynamic"
      >
        <mat-label>Seleção</mat-label>
        <mat-select
          [value]="filtros.team ?? ''"
          (selectionChange)="mudarTeam($event.value)"
          panelClass="filtro-selecao-panel"
        >
          <mat-option value="">Todas as seleções</mat-option>
          @for (t of times; track t.team) {
            <mat-option [value]="t.team">
              @if (t.bandeira) {
                <img [src]="t.bandeira" alt="" class="mr-2 inline-block h-3.5 w-auto rounded-[2px] align-[-2px]" />
              }
              {{ t.team }}
            </mat-option>
          }
        </mat-select>
      </mat-form-field>

      <!-- Busca -->
      <label class="flex min-h-[40px] w-full items-center gap-2 rounded-lg border border-border bg-surface px-3 md:flex-1">
        <span class="sr-only">Buscar por nome ou código</span>
        <input
          type="search"
          class="min-h-[40px] w-full bg-transparent text-sm text-ink outline-none"
          placeholder="Buscar nome ou código…"
          [value]="filtros.busca"
          (input)="mudarBusca($event)"
        />
      </label>

      @if (ativo) {
        <button type="button" class="min-h-[40px] px-2 text-sm font-semibold text-brand-600" (click)="limpar.emit()">
          Limpar filtros
        </button>
      }
    </div>
  `,
})
export class FiltrosAlbumComponent {
  @Input() times: Time[] = [];
  @Input({ required: true }) filtros!: FiltrosAlbum;

  @Output() filtrosChange = new EventEmitter<FiltrosAlbum>();
  @Output() limpar = new EventEmitter<void>();

  protected readonly statusOpcoes: { valor: StatusPosse; rotulo: string }[] = [
    { valor: 'todas', rotulo: 'Todas' },
    { valor: 'tenho', rotulo: 'Tenho' },
    { valor: 'falta', rotulo: 'Falta' },
  ];

  get ativo(): boolean {
    return temFiltroAtivo(this.filtros);
  }

  mudarStatus(status: StatusPosse): void {
    this.filtrosChange.emit({ ...this.filtros, status });
  }

  mudarTeam(valor: string): void {
    this.filtrosChange.emit({ ...this.filtros, team: valor || null });
  }

  mudarBusca(ev: Event): void {
    const busca = (ev.target as HTMLInputElement).value;
    this.filtrosChange.emit({ ...this.filtros, busca });
  }
}
