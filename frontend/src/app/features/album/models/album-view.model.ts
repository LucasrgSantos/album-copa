import { Figurinha } from './figurinha.model';

/** Grupo exibido na grade (derivado do catálogo, agrupado por seleção). */
export interface GrupoSelecao {
  team: string;
  figurinhas: Figurinha[];
  total: number;
  possuidas: number;
}

export type StatusPosse = 'todas' | 'tenho' | 'falta';

/** Estado dos filtros da tela (aplicados no cliente). */
export interface FiltrosAlbum {
  team: string | null; // null = todas as seleções
  status: StatusPosse;
  busca: string;
}

export type EstadoTela = 'loading' | 'ok' | 'erro' | 'vazio';

export const FILTROS_PADRAO: FiltrosAlbum = { team: null, status: 'todas', busca: '' };
