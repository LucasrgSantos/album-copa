/** Seleção disponível para filtro — GET /times/. */
export interface Time {
  team: string;
  /** URL da bandeira do país; string vazia quando a seção não tem bandeira. */
  bandeira: string;
}
