import api from './api';

export interface UorgSimple {
  id: number;
  codigo?: string;
  sigla?: string;
  nome: string;
  uorg_pai_id?: number | null;
  uorg_pai?: UorgSimple;
}

export interface SetorSimple {
  id: number;
  nome: string;
}

export interface UnidadeSimple {
  id: number;
  nome: string;
  setor_id?: number;
  setor?: SetorSimple;
}

export interface PostoSimple {
  id: number;
  nome: string;
  uorg_id?: number;
  uorg?: UorgSimple;
  unidade?: UnidadeSimple;
}

export interface UsuarioGerenciaItem {
  id: number;
  usuario: string;
  nome: string;
  nivel: 'DIVGP_ADMIN' | 'DIGP_ADMIN' | 'UORG' | 'SETOR' | 'UNIDADE' | 'POSTO';
  uorg_id?: number | null;
  setor_id?: number | null;
  unidade_id?: number | null;
  posto_id?: number | null;
  ativo: boolean;
  login: string;
  data_alteracao?: string;
  uorg?: UorgSimple;
  setor?: SetorSimple;
  unidade?: UnidadeSimple;
  posto?: PostoSimple;
}

export interface UserScopeResponse {
  usuario: string;
  is_admin: boolean;
  nivel: string;
  descricao_escopo: string;
  uorg_ids: number[] | null;
  unidade_ids: number[] | null;
  setor_ids: number[] | null;
  posto_ids: number[] | null;
}

export interface GerenciaCreatePayload {
  usuario: string;
  nome: string;
  nivel: string;
  uorg_id?: number | null;
  setor_id?: number | null;
  unidade_id?: number | null;
  posto_id?: number | null;
  ativo?: boolean;
}

export const gerenciaService = {
  async getMyScope(): Promise<UserScopeResponse> {
    const res = await api.get<UserScopeResponse>('/api/gerencias/me');
    return res.data;
  },

  async getAll(nivel?: string, uorgId?: number, apenasAtivos: boolean = false): Promise<UsuarioGerenciaItem[]> {
    const params: any = {};
    if (nivel && nivel !== 'TODOS') params.nivel = nivel;
    if (uorgId) params.uorg_id = uorgId;
    if (apenasAtivos) params.apenas_ativos = true;

    const res = await api.get<UsuarioGerenciaItem[]>('/api/gerencias', { params });
    return res.data;
  },

  async getById(id: number): Promise<UsuarioGerenciaItem> {
    const res = await api.get<UsuarioGerenciaItem>(`/api/gerencias/${id}`);
    return res.data;
  },

  async create(payload: GerenciaCreatePayload): Promise<UsuarioGerenciaItem> {
    const res = await api.post<UsuarioGerenciaItem>('/api/gerencias', payload);
    return res.data;
  },

  async update(id: number, payload: Partial<GerenciaCreatePayload>): Promise<UsuarioGerenciaItem> {
    const res = await api.put<UsuarioGerenciaItem>(`/api/gerencias/${id}`, payload);
    return res.data;
  },

  async delete(id: number): Promise<{ message: string }> {
    const res = await api.delete<{ message: string }>(`/api/gerencias/${id}`);
    return res.data;
  }
};

export default gerenciaService;
