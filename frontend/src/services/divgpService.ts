import api from './api';

export interface DivgpSumario {
  total_unidades: number;
  unidades_100: number;
  unidades_pendentes: number;
  total_colaboradores: number;
  total_publicadas: number;
  percentual_geral: number;
}

export interface DivgpUnidadeStatusItem {
  uorg_id?: number;
  uorg_nome?: string;
  uorg_pai_id?: number | null;
  uorg_pai_nome?: string;
  unidade_id: number;
  unidade_nome: string;
  setor_id?: number | null;
  setor_nome: string;
  total_colaboradores: number;
  total_publicadas: number;
  total_pendentes: number;
  total_sem_grade: number;
  percentual_conclusao: number;
  status_homologacao: 'HOMOLOGADA_100' | 'PARCIAL' | 'SEM_ENVIO';
}

export interface DivgpStatusUnidadesResponse {
  mes: number;
  ano: number;
  sumario: DivgpSumario;
  unidades: DivgpUnidadeStatusItem[];
}

export interface DivgpFaltanteItem {
  funcionario_id: number;
  matricula: string;
  nome: string;
  cargo: string;
  escala_padrao: string;
  unidade_nome: string;
  posto_nome: string;
  grade_id?: number | null;
  grade_status: string;
}

export interface DivgpEscalaDetalheItem {
  funcionario_id: number;
  matricula: string;
  nome: string;
  cargo: string;
  cargo_id?: number | null;
  codigo_escala: string;
  escala_padrao: string;
  uorg_id?: number | null;
  uorg_nome: string;
  uorg_pai_id?: number | null;
  uorg_pai_nome: string;
  posto_id?: number | null;
  posto_nome: string;
  grade_id?: number | null;
  grade_status: string;
  observacao?: string | null;
  login_responsavel?: string | null;
  data_alteracao?: string | null;
  carga_horaria_semanal: number;
  carga_horaria_mensal_teto: number;
  total_horas_escaladas: number;
  saldo_horas: number;
  is_diarista: boolean;
}

export const divgpService = {
  async getStatusUnidades(mes?: number, ano?: number): Promise<DivgpStatusUnidadesResponse> {
    const res = await api.get<DivgpStatusUnidadesResponse>('/api/divgp/status-unidades', {
      params: { mes, ano }
    });
    return res.data;
  },

  async getFaltantes(unidade_id: number, mes?: number, ano?: number): Promise<DivgpFaltanteItem[]> {
    const res = await api.get<DivgpFaltanteItem[]>('/api/divgp/faltantes', {
      params: { unidade_id, mes, ano }
    });
    return res.data;
  },

  async getTodasEscalas(params: {
    mes?: number;
    ano?: number;
    uorg_id?: number;
    uorg_pai_id?: number;
    status?: string;
    cargo_id?: number;
    search?: string;
  }): Promise<DivgpEscalaDetalheItem[]> {
    const res = await api.get<DivgpEscalaDetalheItem[]>('/api/divgp/todas-escalas', { params });
    return res.data;
  }
};

// Aliases para compatibilidade
export const digpService = divgpService;
export type DigpSumario = DivgpSumario;
export type DigpUnidadeStatusItem = DivgpUnidadeStatusItem;
export type DigpFaltanteItem = DivgpFaltanteItem;

export default divgpService;
