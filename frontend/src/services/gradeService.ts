import api from './api';

export interface LotacaoItemInfo {
  unidade_id?: number | null;
  unidade_nome: string;
  posto_nome: string;
  is_atual: boolean;
}

export interface DiaMatrixItem {
  dia: number;
  sigla: string | null;
  escala_id: number | null;
  descricao: string | null;
  horas?: number;
  is_ferias: boolean;
  is_feriado?: boolean;
  feriado_nome?: string | null;
  outra_unidade_sigla?: string | null;
  outra_unidade_nome?: string | null;
  is_outra_unidade?: boolean;
}

export interface ColaboradorGradeRow {
  funcionario_id: number;
  matricula: string;
  nome: string;
  cargo: string;
  cargo_id: number;
  unidade_id?: number | null;
  posto_id?: number | null;
  escala_padrao: string;
  escala_codigo?: string;
  escala_nome?: string;
  posto_nome: string;
  carga_horaria_total?: number | null;
  carga_horaria_semanal?: number;
  carga_horaria_mensal_teto?: number;
  total_horas_escaladas?: number;
  total_horas_unidade?: number;
  horas_excedentes?: number;
  saldo_horas?: number;
  ultrapassou_carga_horaria?: boolean;
  has_multiple_lotacoes: boolean;
  total_lotacoes: number;
  lotacoes_info?: LotacaoItemInfo[];
  is_ferias_mes: boolean;
  is_diarista?: boolean;
  grade_id: number | null;
  grade_status: string;
  is_bloqueada?: boolean;
  observacao?: string | null;
  dias: DiaMatrixItem[];
}

export interface GradeIndicators {
  total_colaboradores: number;
  total_ferias: number;
  total_multiplas_lotacoes: number;
}

export interface GradeDiaPayload {
  dia: number;
  escala_id?: number | null;
  legenda_sigla?: string | null;
  descricao?: string | null;
}

export interface CreateGradePayload {
  funcionario_id: number;
  unidade_id: number;
  posto_id?: number | null;
  mes: number;
  ano: number;
  status?: string;
  observacao?: string;
  permitir_excedente?: boolean;
  dias: GradeDiaPayload[];
}

export interface CopyGradePayload {
  source_func_id?: number;
  source_func_ids?: number[];
  source_unidade_id: number;
  source_mes: number;
  source_ano: number;
  target_func_ids: number[];
  target_unidade_id?: number;
  target_posto_id?: number | null;
  target_mes?: number;
  target_ano?: number;
}

export const gradeService = {
  async getMatrix(params: {
    mes: number;
    ano: number;
    unidade_id?: number;
    cargo_id?: number;
    posto_id?: number;
    search?: string;
    status?: string;
    apenas_publicadas?: boolean;
    incluir_subordinadas?: boolean;
  }): Promise<ColaboradorGradeRow[]> {
    const { data } = await api.get('/api/grades', { params });
    return data;
  },

  async getIndicators(params: {
    mes: number;
    ano: number;
    unidade_id?: number;
    cargo_id?: number;
    posto_id?: number;
    search?: string;
    incluir_subordinadas?: boolean;
  }): Promise<GradeIndicators> {
    const { data } = await api.get('/api/grades/indicadores', { params });
    return data;
  },

  async getGradeById(id: number) {
    const { data } = await api.get(`/api/grades/${id}`);
    return data;
  },

  async createGrade(payload: CreateGradePayload) {
    const { data } = await api.post('/api/grades', payload);
    return data;
  },

  async updateGrade(id: number, payload: Partial<CreateGradePayload>) {
    const { data } = await api.put(`/api/grades/${id}`, payload);
    return data;
  },

  async enviarSuperior(id: number, observacao?: string) {
    const { data } = await api.post(`/api/grades/${id}/enviar-superior`, { observacao });
    return data;
  },

  async enviarLoteSuperior(unidade_id: number, mes: number, ano: number) {
    const { data } = await api.post('/api/grades/enviar-lote-superior', null, {
      params: { unidade_id, mes, ano }
    });
    return data;
  },

  async devolverGrade(id: number, motivo?: string) {
    const { data } = await api.post(`/api/grades/${id}/devolver`, { motivo });
    return data;
  },

  async publishGrade(id: number) {
    const { data } = await api.post(`/api/grades/${id}/publicar`);
    return data;
  },

  async publishAllInUnit(unidade_id: number, mes: number, ano: number) {
    const { data } = await api.post('/api/grades/publicar-lote', null, {
      params: { unidade_id, mes, ano }
    });
    return data;
  },

  async reabrirGrade(id: number) {
    const { data } = await api.post(`/api/grades/${id}/reabrir`);
    return data;
  },

  async copyGrade(payload: CopyGradePayload) {
    const { data } = await api.post('/api/grades/copiar', payload);
    return data;
  },

  async deleteGrade(id: number) {
    const { data } = await api.delete(`/api/grades/${id}`);
    return data;
  }
};

export default gradeService;
