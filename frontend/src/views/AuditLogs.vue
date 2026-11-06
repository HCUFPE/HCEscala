<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 tracking-tight flex items-center gap-2">
          <span>Logs & Auditoria de Alterações</span>
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-100 text-red-800 border border-red-200">
            Exclusivo Administrador
          </span>
        </h1>
        <p class="text-xs sm:text-sm text-gray-500 mt-1">
          Rastreamento histórico de todas as alterações realizadas no banco de dados com antes/depois e capacidade de reversão.
        </p>
      </div>

      <div class="flex items-center gap-2">
        <button 
          @click="gerarBackupRapido" 
          type="button" 
          class="px-3 py-1.5 rounded-md bg-emerald-600 hover:bg-emerald-700 text-white font-semibold flex items-center gap-1.5 shadow-sm text-xs sm:text-sm cursor-pointer transition"
          :disabled="gerandoBackup"
        >
          <CircleStackIcon class="h-4 w-4" :class="{ 'animate-bounce': gerandoBackup }" />
          <span>{{ gerandoBackup ? 'Gerando Backup...' : 'Gerar Backup do Banco' }}</span>
        </button>
        <button 
          @click="fetchLogs" 
          type="button" 
          class="btn btn-secondary flex items-center gap-1.5 shadow-sm text-xs sm:text-sm cursor-pointer"
          :disabled="loading"
        >
          <ArrowPathIcon class="h-4 w-4" :class="{ 'animate-spin': loading }" />
          <span>Atualizar</span>
        </button>
      </div>
    </div>

    <!-- Filter Bar -->
    <Card class="bg-white border-gray-200 shadow-sm">
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-4 items-end">
        <!-- Tela/Módulo -->
        <div class="form-group mb-0">
          <label class="form-label text-xs font-semibold text-gray-700">Tela / Módulo</label>
          <select v-model="filters.tela" @change="applyFilters" class="form-control text-sm">
            <option value="">Todas as Telas</option>
            <option v-for="t in telasDisponiveis" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>

        <!-- Usuário -->
        <div class="form-group mb-0">
          <label class="form-label text-xs font-semibold text-gray-700">Usuário (Login)</label>
          <div class="relative">
            <input 
              v-model="filters.usuario" 
              @keyup.enter="applyFilters"
              type="text" 
              placeholder="Ex: admin, m.silva..."
              class="form-control pl-8 text-sm"
            />
            <UserIcon class="h-4 w-4 text-gray-400 absolute left-2.5 top-2.5" />
          </div>
        </div>

        <!-- Tipo de Operação -->
        <div class="form-group mb-0">
          <label class="form-label text-xs font-semibold text-gray-700">Operação</label>
          <select v-model="filters.operacao" @change="applyFilters" class="form-control text-sm">
            <option value="TODAS">Todas</option>
            <option value="DELETE">DELETE (Exclusão)</option>
            <option value="INSERT">INSERT (Criação)</option>
            <option value="REVERT">REVERT (Reversão)</option>
            <option value="UPDATE">UPDATE (Edição)</option>
          </select>
        </div>

        <!-- Período: De -->
        <div class="form-group mb-0">
          <label class="form-label text-xs font-semibold text-gray-700">Data Inicial</label>
          <input 
            v-model="filters.data_inicio" 
            @change="applyFilters"
            type="date" 
            class="form-control text-sm"
          />
        </div>

        <!-- Período: Até -->
        <div class="form-group mb-0">
          <label class="form-label text-xs font-semibold text-gray-700">Data Final</label>
          <input 
            v-model="filters.data_fim" 
            @change="applyFilters"
            type="date" 
            class="form-control text-sm"
          />
        </div>
      </div>

      <div class="mt-3 flex justify-between items-center pt-3 border-t border-gray-100">
        <span class="text-xs text-gray-500 font-medium">
          Exibindo <strong>{{ logs.length }}</strong> de <strong>{{ totalLogs }}</strong> registros
        </span>
        <button 
          v-if="hasActiveFilters" 
          @click="resetFilters" 
          class="text-xs text-paper-primary hover:underline flex items-center gap-1 cursor-pointer font-medium"
        >
          <XMarkIcon class="h-3.5 w-3.5" />
          <span>Limpar Filtros</span>
        </button>
      </div>
    </Card>

    <!-- Table Card -->
    <Card class="bg-white border-gray-200 overflow-hidden shadow-sm">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 text-left text-sm">
          <thead class="bg-gray-50 text-gray-600 font-semibold text-xs uppercase tracking-wider">
            <tr>
              <th scope="col" class="px-4 py-3">Data / Hora</th>
              <th scope="col" class="px-4 py-3">Usuário</th>
              <th scope="col" class="px-4 py-3">Tela / Módulo</th>
              <th scope="col" class="px-4 py-3">Tabela & ID</th>
              <th scope="col" class="px-4 py-3 text-center">Operação</th>
              <th scope="col" class="px-4 py-3 text-center">Status</th>
              <th scope="col" class="px-4 py-3 text-right">Ações</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 bg-white">
            <tr v-if="loading" class="text-center">
              <td colspan="7" class="py-12 text-gray-500">
                <div class="flex flex-col items-center justify-center gap-2">
                  <div class="w-8 h-8 border-4 border-paper-primary border-t-transparent rounded-full animate-spin"></div>
                  <span>Carregando logs de auditoria...</span>
                </div>
              </td>
            </tr>

            <tr v-else-if="logs.length === 0" class="text-center">
              <td colspan="7" class="py-12 text-gray-500">
                <ShieldCheckIcon class="h-10 w-10 text-gray-300 mx-auto mb-2" />
                <p class="font-medium text-gray-700">Nenhum registro de log encontrado.</p>
                <p class="text-xs text-gray-400 mt-1">Tente ajustar os filtros de tela, usuário ou período.</p>
              </td>
            </tr>

            <tr 
              v-else 
              v-for="log in logs" 
              :key="log.id" 
              class="hover:bg-slate-50 transition-colors"
            >
              <!-- Data / Hora -->
              <td class="px-4 py-3 whitespace-nowrap text-xs font-mono text-gray-700">
                {{ formatDateTime(log.data_hora) }}
              </td>

              <!-- Usuário -->
              <td class="px-4 py-3 whitespace-nowrap">
                <div class="flex items-center gap-1.5 font-medium text-gray-900 text-xs">
                  <span class="w-5 h-5 rounded-full bg-slate-200 text-slate-700 flex items-center justify-center text-[10px] font-bold">
                    {{ log.usuario.charAt(0).toUpperCase() }}
                  </span>
                  <span>{{ log.usuario }}</span>
                </div>
              </td>

              <!-- Tela / Módulo -->
              <td class="px-4 py-3 whitespace-nowrap text-xs">
                <span class="px-2 py-0.5 rounded bg-blue-50 text-blue-800 font-medium border border-blue-100">
                  {{ log.tela }}
                </span>
              </td>

              <!-- Tabela & ID -->
              <td class="px-4 py-3 whitespace-nowrap text-xs font-mono text-gray-600">
                <span>{{ log.tabela }}</span>
                <span class="text-gray-400">#{{ log.registro_id }}</span>
              </td>

              <!-- Operação Badge -->
              <td class="px-4 py-3 whitespace-nowrap text-center">
                <span 
                  class="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase border"
                  :class="{
                    'bg-emerald-100 text-emerald-800 border-emerald-300': log.operacao === 'INSERT',
                    'bg-blue-100 text-blue-800 border-blue-300': log.operacao === 'UPDATE',
                    'bg-rose-100 text-rose-800 border-rose-300': log.operacao === 'DELETE',
                    'bg-purple-100 text-purple-800 border-purple-300': log.operacao === 'REVERT'
                  }"
                >
                  {{ log.operacao }}
                </span>
              </td>

              <!-- Status Revertido -->
              <td class="px-4 py-3 whitespace-nowrap text-center text-xs">
                <span 
                  v-if="log.revertido" 
                  class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-900 border border-amber-300"
                  :title="`Revertido por ${log.revertido_por || 'admin'} em ${formatDateTime(log.revertido_em)}`"
                >
                  ↩️ Revertido
                </span>
                <span v-else class="text-gray-400 text-xs">Ativo</span>
              </td>

              <!-- Ações -->
              <td class="px-4 py-3 whitespace-nowrap text-right space-x-2">
                <button 
                  @click="openDetails(log)" 
                  class="text-blue-600 hover:text-blue-900 text-xs font-semibold cursor-pointer"
                  title="Ver detalhes da alteração (Antes / Depois)"
                >
                  Detalhes
                </button>
                <button 
                  v-if="!log.revertido && log.operacao !== 'REVERT'"
                  @click="confirmRevert(log)" 
                  class="text-rose-600 hover:text-rose-900 text-xs font-semibold cursor-pointer"
                  title="Desfazer e reverter esta alteração no banco"
                >
                  Reverter
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>

    <!-- Modal Detalhes (Antes / Depois) -->
    <div v-if="selectedLog" class="fixed inset-0 z-50 overflow-y-auto bg-black/50 flex items-center justify-center p-4">
      <div class="bg-white rounded-xl shadow-2xl max-w-3xl w-full p-6 space-y-4">
        <div class="flex justify-between items-center border-b pb-3">
          <div>
            <h3 class="text-lg font-bold text-gray-900 flex items-center gap-2">
              <span>Detalhes da Alteração</span>
              <span 
                class="px-2 py-0.5 rounded text-xs font-bold uppercase"
                :class="{
                  'bg-emerald-100 text-emerald-800': selectedLog.operacao === 'INSERT',
                  'bg-blue-100 text-blue-800': selectedLog.operacao === 'UPDATE',
                  'bg-rose-100 text-rose-800': selectedLog.operacao === 'DELETE',
                  'bg-purple-100 text-purple-800': selectedLog.operacao === 'REVERT'
                }"
              >
                {{ selectedLog.operacao }}
              </span>
            </h3>
            <p class="text-xs text-gray-500 mt-0.5">
              Tela: <strong>{{ selectedLog.tela }}</strong> | Tabela: <strong>{{ selectedLog.tabela }}</strong> (#{{ selectedLog.registro_id }})
            </p>
          </div>
          <button @click="selectedLog = null" class="text-gray-400 hover:text-gray-600 p-1">
            <XMarkIcon class="h-6 w-6" />
          </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
          <!-- Antes -->
          <div class="space-y-1">
            <span class="font-sans font-bold text-gray-700 block">Estado Anterior:</span>
            <div class="p-3 bg-rose-50/60 rounded border border-rose-100 overflow-x-auto max-h-72">
              <pre v-if="selectedLog.dados_anteriores">{{ formatJson(selectedLog.dados_anteriores) }}</pre>
              <span v-else class="text-gray-400 italic">Nenhum (Novo Registro)</span>
            </div>
          </div>

          <!-- Depois -->
          <div class="space-y-1">
            <span class="font-sans font-bold text-gray-700 block">Estado Posterior:</span>
            <div class="p-3 bg-emerald-50/60 rounded border border-emerald-100 overflow-x-auto max-h-72">
              <pre v-if="selectedLog.dados_posteriores">{{ formatJson(selectedLog.dados_posteriores) }}</pre>
              <span v-else class="text-gray-400 italic">Registro Excluído</span>
            </div>
          </div>
        </div>

        <div class="flex justify-between items-center pt-3 border-t text-xs text-gray-500">
          <div>
            Alterado por <strong>{{ selectedLog.usuario }}</strong> em {{ formatDateTime(selectedLog.data_hora) }}
          </div>
          <div class="flex gap-2">
            <button 
              v-if="!selectedLog.revertido && selectedLog.operacao !== 'REVERT'"
              @click="confirmRevert(selectedLog)" 
              class="btn btn-danger text-xs cursor-pointer"
            >
              Reverter Alteração
            </button>
            <button @click="selectedLog = null" class="btn btn-secondary text-xs cursor-pointer">
              Fechar
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { 
  ArrowPathIcon, 
  UserIcon, 
  XMarkIcon, 
  ShieldCheckIcon,
  CircleStackIcon
} from '@heroicons/vue/24/outline';
import Card from '../components/Card.vue';
import { auditService, AuditLogItem } from '../services/auditService';
import api from '../services/api';

const logs = ref<AuditLogItem[]>([]);
const totalLogs = ref(0);
const loading = ref(false);
const gerandoBackup = ref(false);
const telasDisponiveis = ref<string[]>([]);
const selectedLog = ref<AuditLogItem | null>(null);

async function gerarBackupRapido() {
  gerandoBackup.value = true;
  try {
    const { data } = await api.post('/api/admin/backups/gerar', { nome_base: 'app_backup' });
    const filename = data.backup?.filename;
    if (filename) {
      const response = await api.get(`/api/admin/backups/download/${encodeURIComponent(filename)}`, {
        responseType: 'blob',
      });
      const blob = new Blob([response.data], { type: 'application/octet-stream' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    }
    alert(`${data.mensagem}\nCaminho na máquina: ${data.backup?.caminho_completo}`);
    await fetchLogs();
  } catch (err: any) {
    alert('Erro ao gerar backup: ' + (err.response?.data?.detail || err.message));
  } finally {
    gerandoBackup.value = false;
  }
}

const filters = reactive({
  tela: '',
  usuario: '',
  operacao: 'TODAS',
  data_inicio: '',
  data_fim: '',
  limit: 100,
  offset: 0
});

const hasActiveFilters = computed(() => {
  return !!filters.tela || !!filters.usuario || filters.operacao !== 'TODAS' || !!filters.data_inicio || !!filters.data_fim;
});

async function fetchLogs() {
  loading.value = true;
  try {
    const res = await auditService.getLogs({
      tela: filters.tela || undefined,
      usuario: filters.usuario || undefined,
      operacao: filters.operacao || undefined,
      data_inicio: filters.data_inicio ? `${filters.data_inicio}T00:00:00` : undefined,
      data_fim: filters.data_fim ? `${filters.data_fim}T23:59:59` : undefined,
      limit: filters.limit,
      offset: filters.offset
    });
    logs.value = res.items;
    totalLogs.value = res.total;
  } catch (err: any) {
    console.error('Erro ao carregar logs:', err);
    alert('Erro ao carregar logs de auditoria: ' + (err.response?.data?.detail || err.message));
  } finally {
    loading.value = false;
  }
}

async function loadTelas() {
  try {
    const list = await auditService.getTelas();
    telasDisponiveis.value = (list || []).sort((a, b) => a.localeCompare(b, 'pt-BR', { sensitivity: 'base' }));
  } catch (e) {
    console.error('Erro ao buscar lista de telas:', e);
  }
}

function applyFilters() {
  filters.offset = 0;
  fetchLogs();
}

function resetFilters() {
  filters.tela = '';
  filters.usuario = '';
  filters.operacao = 'TODAS';
  filters.data_inicio = '';
  filters.data_fim = '';
  filters.offset = 0;
  fetchLogs();
}

function openDetails(log: AuditLogItem) {
  selectedLog.value = log;
}

function formatJson(jsonStr: string | null) {
  if (!jsonStr) return '';
  try {
    return JSON.stringify(JSON.parse(jsonStr), null, 2);
  } catch {
    return jsonStr;
  }
}

function formatDateTime(dateStr?: string | null) {
  if (!dateStr) return '-';
  try {
    const d = new Date(dateStr);
    return d.toLocaleString('pt-BR');
  } catch {
    return dateStr;
  }
}

async function confirmRevert(log: AuditLogItem) {
  const confirmed = confirm(
    `Tem certeza que deseja REVERTER a alteração #${log.id} (${log.operacao} em ${log.tela})?\nIsso irá desfazer as alterações no banco de dados.`
  );
  if (!confirmed) return;

  try {
    const res = await auditService.revertLog(log.id);
    alert(res.mensagem || 'Reversão concluída com sucesso!');
    if (selectedLog.value?.id === log.id) {
      selectedLog.value = null;
    }
    await fetchLogs();
  } catch (err: any) {
    alert('Falha ao reverter: ' + (err.response?.data?.detail || err.message));
  }
}

onMounted(() => {
  fetchLogs();
  loadTelas();
});
</script>
