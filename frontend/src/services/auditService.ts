import api from './api';

export interface AuditLogItem {
  id: number;
  usuario: string;
  tela: string;
  tabela: string;
  operacao: string;
  registro_id: string;
  dados_anteriores: string | null;
  dados_posteriores: string | null;
  data_hora: string;
  revertido: boolean;
  revertido_por?: string | null;
  revertido_em?: string | null;
}

export interface PaginatedAuditLogs {
  items: AuditLogItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface AuditFilterParams {
  tela?: string;
  usuario?: string;
  operacao?: string;
  data_inicio?: string;
  data_fim?: string;
  limit?: number;
  offset?: number;
}

export const auditService = {
  async getLogs(params: AuditFilterParams = {}): Promise<PaginatedAuditLogs> {
    const query = new URLSearchParams();
    if (params.tela) query.append('tela', params.tela);
    if (params.usuario) query.append('usuario', params.usuario);
    if (params.operacao && params.operacao !== 'TODAS') query.append('operacao', params.operacao);
    if (params.data_inicio) query.append('data_inicio', params.data_inicio);
    if (params.data_fim) query.append('data_fim', params.data_fim);
    if (params.limit) query.append('limit', String(params.limit));
    if (params.offset !== undefined) query.append('offset', String(params.offset));

    const response = await api.get<PaginatedAuditLogs>(`/api/audit-logs?${query.toString()}`);
    return response.data;
  },

  async getTelas(): Promise<string[]> {
    const response = await api.get<string[]>('/api/audit-logs/telas');
    return response.data;
  },

  async revertLog(id: number): Promise<{ sucesso: boolean; mensagem: string }> {
    const response = await api.post<{ sucesso: boolean; mensagem: string }>(`/api/audit-logs/${id}/revert`);
    return response.data;
  }
};
