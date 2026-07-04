/** Progresso consolidado do álbum — GET /colecao/progresso/. */
export interface ProgressoTime {
  team: string;
  total: number;
  possuidas: number;
  percentual: number;
}

export interface Progresso {
  total: number;
  total_possuidas: number; // distintas com quantidade > 0 (repetidas contam 1)
  total_faltantes: number;
  percentual: number; // 0.0 quando total == 0
  por_team: ProgressoTime[];
}
