import { HttpInterceptorFn } from '@angular/common/http';

/**
 * ngrok (plano free) intercepta requisições de navegador e devolve uma página HTML
 * de aviso em vez da resposta real — o que quebraria o parse de JSON da API.
 * Enviar o header `ngrok-skip-browser-warning` (qualquer valor) pula essa página.
 * Aplicado só quando a URL aponta para um domínio ngrok, para não vazar o header
 * em outros backends.
 */
export const ngrokInterceptor: HttpInterceptorFn = (req, next) => {
  if (!req.url.includes('.ngrok-free.dev') && !req.url.includes('.ngrok.io')) {
    return next(req);
  }
  return next(req.clone({ setHeaders: { 'ngrok-skip-browser-warning': 'true' } }));
};
