import { HttpClient } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { Observable, firstValueFrom } from 'rxjs';

import { environment } from '../../../environments/environment';
import { Figurinha } from '../../features/album/models/figurinha.model';
import { PaginaDRF } from '../../features/album/models/paginacao.model';
import { Progresso } from '../../features/album/models/progresso.model';
import { Time } from '../../features/album/models/time.model';

/**
 * Fonte única dos dados do álbum. Carrega o catálogo uma vez (cache em signal) e
 * expõe as operações de posse/progresso da API (At.05). Filtros são client-side
 * (ver album.logic.ts) — este serviço não refaz busca por filtro.
 */
@Injectable({ providedIn: 'root' })
export class FigurinhasService {
  private readonly http = inject(HttpClient);
  private readonly base = environment.apiBaseUrl;

  private readonly _catalogo = signal<Figurinha[]>([]);
  private readonly _progresso = signal<Progresso | null>(null);

  /** Catálogo completo em cache (somente leitura para a UI). */
  readonly catalogo = this._catalogo.asReadonly();
  readonly progresso = this._progresso.asReadonly();
  readonly carregado = computed(() => this._catalogo().length > 0);

  /** Carrega todo o catálogo em uma única requisição (a API entrega tudo em uma página). */
  async carregarCatalogo(): Promise<void> {
    const pagina = await firstValueFrom(
      this.http.get<PaginaDRF<Figurinha>>(`${this.base}/figurinhas/`),
    );
    this._catalogo.set(pagina.results);
  }

  async obterProgresso(): Promise<void> {
    const p = await firstValueFrom(this.http.get<Progresso>(`${this.base}/colecao/progresso/`));
    this._progresso.set(p);
  }

  obterTimes(): Promise<Time[]> {
    return firstValueFrom(this.http.get<Time[]>(`${this.base}/times/`));
  }

  definirQuantidade(code: string, quantidade: number): Promise<Figurinha> {
    return this.mutar(code, Math.max(0, quantidade), () =>
      this.http.patch<Figurinha>(`${this.base}/figurinhas/${encodeURIComponent(code)}/quantidade/`, {
        quantidade,
      }),
    );
  }

  incrementar(code: string): Promise<Figurinha> {
    const atual = this.buscar(code);
    const alvo = atual ? atual.quantidade + 1 : 1;
    return this.mutar(code, alvo, () =>
      this.http.post<Figurinha>(`${this.base}/figurinhas/${encodeURIComponent(code)}/incrementar/`, {}),
    );
  }

  decrementar(code: string): Promise<Figurinha> {
    const atual = this.buscar(code);
    const alvo = atual ? Math.max(0, atual.quantidade - 1) : 0;
    return this.mutar(code, alvo, () =>
      this.http.post<Figurinha>(`${this.base}/figurinhas/${encodeURIComponent(code)}/decrementar/`, {}),
    );
  }

  /**
   * Atualização otimista + reversão: aplica `novaQtd` no cache na hora, chama a API,
   * reconcilia com a resposta e, em erro, reverte ao estado anterior (RF-007/RF-020).
   */
  private async mutar(
    code: string,
    novaQtd: number,
    chamada: () => Observable<Figurinha>,
  ): Promise<Figurinha> {
    const anterior = this.buscar(code);
    if (anterior) {
      this.aplicarAtualizacao({ ...anterior, quantidade: novaQtd, possuo: novaQtd > 0 });
    }
    try {
      const atualizada = await firstValueFrom(chamada());
      this.aplicarAtualizacao(atualizada);
      return atualizada;
    } catch (e) {
      if (anterior) this.aplicarAtualizacao(anterior);
      throw e;
    }
  }

  private buscar(code: string): Figurinha | undefined {
    return this._catalogo().find((f) => f.code === code);
  }

  /** Substitui o item no cache pela versão informada (reconciliação/reversão). */
  private aplicarAtualizacao(fig: Figurinha): void {
    this._catalogo.update((lista) => lista.map((f) => (f.code === fig.code ? fig : f)));
  }
}
