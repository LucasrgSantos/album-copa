import { Figurinha } from './models/figurinha.model';
import { FiltrosAlbum, GrupoSelecao } from './models/album-view.model';

/**
 * Compara códigos por numeração natural: BRA1 < BRA2 < BRA10 (e não BRA1 < BRA10 < BRA2,
 * como faria a ordenação textual). `numeric: true` trata os dígitos como números.
 */
export function compararCodigo(a: string, b: string): number {
  return a.localeCompare(b, undefined, { numeric: true, sensitivity: 'base' });
}

/** Agrupa o catálogo por seleção, ordenando por `team` e, dentro do grupo, por numeração. */
export function agruparPorSelecao(catalogo: readonly Figurinha[]): GrupoSelecao[] {
  const mapa = new Map<string, Figurinha[]>();
  for (const f of catalogo) {
    const lista = mapa.get(f.team) ?? [];
    lista.push(f);
    mapa.set(f.team, lista);
  }
  return [...mapa.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([team, figurinhas]) => {
      const ordenadas = [...figurinhas].sort((a, b) => compararCodigo(a.code, b.code));
      return {
        team,
        figurinhas: ordenadas,
        total: ordenadas.length,
        possuidas: ordenadas.filter((f) => f.possuo).length,
      };
    });
}

/** Aplica os filtros de tela (team + status + busca) em AND, sobre o catálogo em cache. */
export function aplicarFiltros(
  catalogo: readonly Figurinha[],
  filtros: FiltrosAlbum,
): Figurinha[] {
  const termo = filtros.busca.trim().toLowerCase();
  return catalogo.filter((f) => {
    if (filtros.team && f.team !== filtros.team) return false;
    if (filtros.status === 'tenho' && f.quantidade <= 0) return false;
    if (filtros.status === 'falta' && f.quantidade > 0) return false;
    if (termo) {
      const alvo = `${f.name} ${f.code}`.toLowerCase();
      if (!alvo.includes(termo)) return false;
    }
    return true;
  });
}

/** Rótulo de repetidas ("x2", "x3"…) quando a quantidade é maior que 1; senão null. */
export function badgeRepetida(f: Figurinha): string | null {
  return f.quantidade > 1 ? `x${f.quantidade}` : null;
}

/** Há algum filtro ativo? (para exibir "limpar filtros"). */
export function temFiltroAtivo(filtros: FiltrosAlbum): boolean {
  return filtros.team !== null || filtros.status !== 'todas' || filtros.busca.trim() !== '';
}
