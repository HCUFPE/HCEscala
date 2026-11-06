<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 tracking-tight flex items-center gap-2">
          <CircleStackIcon class="h-7 w-7 text-paper-primary" />
          <span>Backup do Banco de Dados</span>
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-100 text-red-800 border border-red-200">
            Exclusivo Administrador
          </span>
        </h1>
        <p class="text-xs sm:text-sm text-gray-500 mt-1">
          Gere cópias de segurança íntegras do banco de dados na máquina com nome do arquivo + data, hora, minuto e segundo.
        </p>
      </div>

      <div class="flex items-center gap-2">
        <button
          @click="carregarBackups"
          type="button"
          class="btn btn-secondary flex items-center gap-1.5 shadow-sm text-xs sm:text-sm cursor-pointer"
          :disabled="loading || gerando"
        >
          <ArrowPathIcon class="h-4 w-4" :class="{ 'animate-spin': loading }" />
          <span>Atualizar Lista</span>
        </button>
      </div>
    </div>

    <!-- Mensagem de Sucesso / Erro -->
    <div
      v-if="mensagemSucesso"
      class="p-4 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 flex items-start justify-between gap-3 shadow-sm"
    >
      <div class="flex items-start gap-2.5 text-sm">
        <CheckCircleIcon class="h-5 w-5 text-emerald-600 shrink-0 mt-0.5" />
        <div>
          <p class="font-semibold">{{ mensagemSucesso }}</p>
          <p v-if="ultimoBackupGerado" class="text-xs text-emerald-700 mt-1 font-mono break-all">
            Salvo na máquina em: {{ ultimoBackupGerado.caminho_completo }} ({{ ultimoBackupGerado.tamanho_formatado }})
          </p>
        </div>
      </div>
      <button @click="mensagemSucesso = ''" class="text-emerald-600 hover:text-emerald-800 text-xs font-bold">✕</button>
    </div>

    <div
      v-if="mensagemErro"
      class="p-4 rounded-lg bg-red-50 border border-red-200 text-red-800 flex items-center justify-between gap-3 shadow-sm text-sm"
    >
      <span>{{ mensagemErro }}</span>
      <button @click="mensagemErro = ''" class="text-red-600 hover:text-red-800 text-xs font-bold">✕</button>
    </div>

    <!-- Painel de Geração de Backup -->
    <Card class="bg-white border-gray-200 shadow-sm">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 items-end">
        <div>
          <label class="form-label text-xs font-semibold text-gray-700">
            Nome Base do Arquivo de Backup
          </label>
          <input
            v-model="nomeBase"
            type="text"
            placeholder="Ex: app_backup"
            class="form-control text-sm font-mono"
          />
          <p class="text-[11px] text-gray-500 mt-1">
            Formato gerado: <span class="font-mono font-semibold text-gray-700">{{ previewNomeArquivo }}</span>
          </p>
        </div>

        <div class="bg-gray-50 p-3 rounded-lg border border-gray-200 text-xs space-y-1">
          <div class="flex justify-between">
            <span class="text-gray-500 font-medium">Banco de Origem:</span>
            <span class="font-mono font-semibold text-gray-800">{{ bancoOrigem || 'app.db' }}</span>
          </div>
          <div class="flex justify-between gap-2">
            <span class="text-gray-500 font-medium shrink-0">Pasta na Máquina:</span>
            <span class="font-mono text-gray-700 truncate" :title="diretorioBackups">{{ diretorioBackups || './backups' }}</span>
          </div>
          <label class="flex items-center gap-2 pt-1.5 cursor-pointer select-none text-gray-700 font-medium">
            <input type="checkbox" v-model="baixarAutomaticamente" class="rounded text-paper-primary" />
            <span>Baixar arquivo na máquina após gerar</span>
          </label>
        </div>

        <div class="flex justify-end">
          <button
            @click="gerarNovoBackup"
            type="button"
            :disabled="gerando"
            class="w-full lg:w-auto px-5 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-semibold text-sm shadow flex items-center justify-center gap-2 cursor-pointer transition"
          >
            <ArrowDownTrayIcon class="h-5 w-5" :class="{ 'animate-bounce': gerando }" />
            <span>{{ gerando ? 'Gerando Backup...' : 'Gerar Backup do Banco Agora' }}</span>
          </button>
        </div>
      </div>
    </Card>

    <!-- Tabela de Backups Salvos na Máquina -->
    <Card class="bg-white border-gray-200 overflow-hidden shadow-sm">
      <div class="px-4 py-3 border-b border-gray-200 flex justify-between items-center bg-gray-50">
        <h2 class="text-sm font-bold text-gray-700 uppercase tracking-wider">
          Backups Gerados na Máquina ({{ backups.length }})
        </h2>
      </div>

      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 text-left text-sm">
          <thead class="bg-gray-50 text-gray-600 font-semibold text-xs uppercase tracking-wider">
            <tr>
              <th scope="col" class="px-4 py-3">Nome do Arquivo (Nome + Data/Hora/Min/Seg)</th>
              <th scope="col" class="px-4 py-3">Data e Hora de Geração</th>
              <th scope="col" class="px-4 py-3">Caminho na Máquina</th>
              <th scope="col" class="px-4 py-3 text-right">Tamanho</th>
              <th scope="col" class="px-4 py-3 text-right">Ação</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 bg-white">
            <tr v-if="loading && backups.length === 0">
              <td colspan="5" class="px-4 py-8 text-center text-gray-500">
                Carregando backups disponíveis...
              </td>
            </tr>
            <tr v-else-if="backups.length === 0">
              <td colspan="5" class="px-4 py-8 text-center text-gray-500">
                Nenhum backup gerado ainda. Clique em <strong>"Gerar Backup do Banco Agora"</strong> acima.
              </td>
            </tr>
            <tr v-for="item in backups" :key="item.filename" class="hover:bg-gray-50">
              <td class="px-4 py-3 font-mono font-semibold text-gray-900">
                {{ item.filename }}
              </td>
              <td class="px-4 py-3 text-gray-700 whitespace-nowrap">
                {{ item.data_hora }}
              </td>
              <td class="px-4 py-3 font-mono text-xs text-gray-500 max-w-md truncate" :title="item.caminho_completo">
                {{ item.caminho_completo }}
              </td>
              <td class="px-4 py-3 text-right font-mono text-xs text-gray-700 whitespace-nowrap">
                {{ item.tamanho_formatado }}
              </td>
              <td class="px-4 py-3 text-right whitespace-nowrap">
                <button
                  @click="baixarBackup(item.filename)"
                  type="button"
                  class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 text-xs font-semibold cursor-pointer transition"
                >
                  <ArrowDownTrayIcon class="h-4 w-4" />
                  <span>Baixar na Máquina</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import {
  CircleStackIcon,
  ArrowPathIcon,
  ArrowDownTrayIcon,
  CheckCircleIcon,
} from '@heroicons/vue/24/outline';
import Card from '../components/Card.vue';
import api from '../services/api';

interface BackupItem {
  filename: string;
  caminho_completo: string;
  data_hora: string;
  timestamp_iso: string;
  tamanho_bytes: number;
  tamanho_formatado: string;
}

const backups = ref<BackupItem[]>([]);
const bancoOrigem = ref<string>('app.db');
const diretorioBackups = ref<string>('');
const nomeBase = ref<string>('app_backup');
const baixarAutomaticamente = ref<boolean>(true);
const loading = ref<boolean>(false);
const gerando = ref<boolean>(false);
const mensagemSucesso = ref<string>('');
const mensagemErro = ref<string>('');
const ultimoBackupGerado = ref<BackupItem | null>(null);
const agoraTick = ref<Date>(new Date());

let timer: ReturnType<typeof setInterval> | null = null;

const pad2 = (n: number) => String(n).padStart(2, '0');

const previewNomeArquivo = computed(() => {
  const dt = agoraTick.value;
  const limpo = (nomeBase.value || 'app').replace(/[^a-zA-Z0-9_-]/g, '') || 'app';
  const dataStr = `${dt.getFullYear()}-${pad2(dt.getMonth() + 1)}-${pad2(dt.getDate())}`;
  const horaStr = `${pad2(dt.getHours())}-${pad2(dt.getMinutes())}-${pad2(dt.getSeconds())}`;
  return `${limpo}_${dataStr}_${horaStr}.db`;
});

const carregarBackups = async () => {
  loading.value = true;
  mensagemErro.value = '';
  try {
    const { data } = await api.get('/api/admin/backups');
    backups.value = data.items || [];
    bancoOrigem.value = data.banco_origem || 'app.db';
    diretorioBackups.value = data.diretorio_backups || '';
  } catch (err: any) {
    mensagemErro.value = err.response?.data?.detail || 'Erro ao carregar a lista de backups.';
  } finally {
    loading.value = false;
  }
};

const baixarBackup = async (filename: string) => {
  try {
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
  } catch (err: any) {
    mensagemErro.value = 'Falha ao transferir o arquivo de backup para a máquina.';
  }
};

const gerarNovoBackup = async () => {
  gerando.value = true;
  mensagemErro.value = '';
  mensagemSucesso.value = '';
  try {
    const { data } = await api.post('/api/admin/backups/gerar', {
      nome_base: nomeBase.value || 'app_backup',
    });
    ultimoBackupGerado.value = data.backup;
    mensagemSucesso.value = data.mensagem;
    await carregarBackups();
    if (baixarAutomaticamente.value && data.backup?.filename) {
      await baixarBackup(data.backup.filename);
    }
  } catch (err: any) {
    mensagemErro.value = err.response?.data?.detail || 'Erro ao gerar backup do banco de dados.';
  } finally {
    gerando.value = false;
  }
};

onMounted(() => {
  carregarBackups();
  timer = setInterval(() => {
    agoraTick.value = new Date();
  }, 1000);
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
});
</script>
