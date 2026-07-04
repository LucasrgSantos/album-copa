/** Envelope de paginação padrão do DRF. */
export interface PaginaDRF<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
