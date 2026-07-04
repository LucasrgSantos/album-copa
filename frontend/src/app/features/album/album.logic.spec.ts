import { agruparPorSelecao, aplicarFiltros, badgeRepetida, temFiltroAtivo } from './album.logic';
import { Figurinha } from './models/figurinha.model';
import { FiltrosAlbum, FILTROS_PADRAO } from './models/album-view.model';

function fig(partial: Partial<Figurinha> & { code: string }): Figurinha {
  return {
    name: partial.name ?? partial.code,
    team: partial.team ?? 'Brazil',
    especial: partial.especial ?? false,
    imagem: partial.imagem ?? null,
    quantidade: partial.quantidade ?? 0,
    possuo: (partial.quantidade ?? 0) > 0,
    ...partial,
  };
}

const CATALOGO: Figurinha[] = [
  fig({ code: 'BRA2', name: 'Alisson', team: 'Brazil', quantidade: 2 }),
  fig({ code: 'BRA1', name: 'Escudo Brasil', team: 'Brazil', quantidade: 0, especial: true }),
  fig({ code: 'ARG1', name: 'Messi', team: 'Argentina', quantidade: 1 }),
];

describe('agruparPorSelecao', () => {
  it('agrupa por seleção ordenando teams e códigos', () => {
    const grupos = agruparPorSelecao(CATALOGO);
    expect(grupos.map((g) => g.team)).toEqual(['Argentina', 'Brazil']);
    const brasil = grupos.find((g) => g.team === 'Brazil')!;
    expect(brasil.figurinhas.map((f) => f.code)).toEqual(['BRA1', 'BRA2']);
    expect(brasil.total).toBe(2);
    expect(brasil.possuidas).toBe(1);
  });

  it('ordena por numeração natural (BRA10 depois de BRA2)', () => {
    const catalogo = [fig({ code: 'BRA10' }), fig({ code: 'BRA2' }), fig({ code: 'BRA1' })];
    const brasil = agruparPorSelecao(catalogo)[0];
    expect(brasil.figurinhas.map((f) => f.code)).toEqual(['BRA1', 'BRA2', 'BRA10']);
  });
});

describe('aplicarFiltros', () => {
  it('status "tenho" retorna apenas quantidade > 0', () => {
    const r = aplicarFiltros(CATALOGO, { ...FILTROS_PADRAO, status: 'tenho' });
    expect(r.map((f) => f.code).sort()).toEqual(['ARG1', 'BRA2']);
  });

  it('status "falta" retorna apenas quantidade 0', () => {
    const r = aplicarFiltros(CATALOGO, { ...FILTROS_PADRAO, status: 'falta' });
    expect(r.map((f) => f.code)).toEqual(['BRA1']);
  });

  it('filtra por seleção', () => {
    const r = aplicarFiltros(CATALOGO, { ...FILTROS_PADRAO, team: 'Argentina' });
    expect(r.map((f) => f.code)).toEqual(['ARG1']);
  });

  it('busca por nome ou código (case-insensitive)', () => {
    expect(aplicarFiltros(CATALOGO, { ...FILTROS_PADRAO, busca: 'mess' }).map((f) => f.code)).toEqual(['ARG1']);
    expect(aplicarFiltros(CATALOGO, { ...FILTROS_PADRAO, busca: 'bra2' }).map((f) => f.code)).toEqual(['BRA2']);
  });

  it('combina filtros em AND', () => {
    const filtros: FiltrosAlbum = { team: 'Brazil', status: 'tenho', busca: 'ali' };
    expect(aplicarFiltros(CATALOGO, filtros).map((f) => f.code)).toEqual(['BRA2']);
  });

  it('sem correspondência retorna vazio', () => {
    expect(aplicarFiltros(CATALOGO, { ...FILTROS_PADRAO, busca: 'zzz' })).toEqual([]);
  });
});

describe('badgeRepetida', () => {
  it('mostra xN só quando quantidade > 1', () => {
    expect(badgeRepetida(fig({ code: 'A', quantidade: 2 }))).toBe('x2');
    expect(badgeRepetida(fig({ code: 'A', quantidade: 1 }))).toBeNull();
    expect(badgeRepetida(fig({ code: 'A', quantidade: 0 }))).toBeNull();
  });
});

describe('temFiltroAtivo', () => {
  it('detecta filtros ativos', () => {
    expect(temFiltroAtivo(FILTROS_PADRAO)).toBe(false);
    expect(temFiltroAtivo({ ...FILTROS_PADRAO, status: 'tenho' })).toBe(true);
    expect(temFiltroAtivo({ ...FILTROS_PADRAO, team: 'Brazil' })).toBe(true);
    expect(temFiltroAtivo({ ...FILTROS_PADRAO, busca: ' x ' })).toBe(true);
  });
});
