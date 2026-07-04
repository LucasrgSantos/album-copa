/** Item do catálogo — espelha o FigurinhaSerializer da API (At.05). */
export interface Figurinha {
  code: string; // único (ex.: "BRA1") — usado como track/lookup
  name: string;
  team: string; // = Selecao.nome
  especial: boolean;
  imagem: string | null; // URL absoluta; null quando sem imagem → placeholder
  quantidade: number; // inteiro >= 0
  possuo: boolean; // = quantidade > 0
}
