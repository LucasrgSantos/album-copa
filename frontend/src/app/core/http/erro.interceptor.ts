import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';

/** Erro já tratado para exibição amigável na UI. */
export interface ErroAmigavel {
  code: string;
  mensagem: string;
  status: number;
}

const MENSAGENS: Record<string, string> = {
  not_found: 'Figurinha não encontrada.',
  invalid: 'Quantidade inválida.',
  parse_error: 'Não foi possível processar a solicitação.',
  method_not_allowed: 'Ação não permitida.',
};

/**
 * Lê o formato de erro padrão da API ({ detail, code }) e produz uma mensagem
 * amigável — nunca vaza stacktrace/erro técnico cru. Ver contracts/api-consumo.md.
 */
export const erroInterceptor: HttpInterceptorFn = (req, next) =>
  next(req).pipe(
    catchError((err: HttpErrorResponse) => {
      const apiCode: string | undefined = err?.error?.code;
      const apiDetail: string | undefined = err?.error?.detail;
      const code = apiCode ?? (err.status === 0 ? 'network' : `http_${err.status}`);
      const mensagem =
        (apiCode && MENSAGENS[apiCode]) ||
        apiDetail ||
        (err.status === 0
          ? 'Falha de conexão. Tente novamente.'
          : 'Algo deu errado. Tente novamente.');
      const amigavel: ErroAmigavel = { code, mensagem, status: err.status };
      return throwError(() => amigavel);
    }),
  );
