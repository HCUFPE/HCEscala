<template>
  <div class="legendas-container space-y-6">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-paper-sidebar">Cadastro de Legendas</h2>
      <button @click="openModal()" class="bg-paper-primary hover:bg-paper-primary-hover text-white px-4 py-2 rounded-md text-sm transition-colors">
        Nova Legenda
      </button>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <table class="w-full text-sm text-left">
        <thead class="bg-gray-100 text-paper-text text-xs uppercase font-semibold border-b border-gray-200 select-none">
          <tr>
            <th @click="sortBy('id')" class="px-4 py-3 w-20 cursor-pointer hover:bg-gray-200/80 transition-colors" title="Ordenar por ID">
              <div class="flex items-center gap-1">
                <span>ID</span>
                <span class="text-xs text-gray-500 font-mono">{{ getSortIcon('id') }}</span>
              </div>
            </th>
            <th @click="sortBy('sigla')" class="px-4 py-3 w-28 cursor-pointer hover:bg-gray-200/80 transition-colors" title="Ordenar por Sigla">
              <div class="flex items-center gap-1">
                <span>Sigla</span>
                <span class="text-xs text-gray-500 font-mono">{{ getSortIcon('sigla') }}</span>
              </div>
            </th>
            <th @click="sortBy('descricao')" class="px-4 py-3 cursor-pointer hover:bg-gray-200/80 transition-colors" title="Ordenar por Descrição">
              <div class="flex items-center gap-1">
                <span>Descrição</span>
                <span class="text-xs text-gray-500 font-mono">{{ getSortIcon('descricao') }}</span>
              </div>
            </th>
            <th @click="sortBy('login')" class="px-4 py-3 w-32 cursor-pointer hover:bg-gray-200/80 transition-colors" title="Ordenar por Usuário">
              <div class="flex items-center gap-1">
                <span>Usuário</span>
                <span class="text-xs text-gray-500 font-mono">{{ getSortIcon('login') }}</span>
              </div>
            </th>
            <th @click="sortBy('data_alteracao')" class="px-4 py-3 w-36 cursor-pointer hover:bg-gray-200/80 transition-colors" title="Ordenar por Data de Alteração">
              <div class="flex items-center gap-1">
                <span>Data Alt.</span>
                <span class="text-xs text-gray-500 font-mono">{{ getSortIcon('data_alteracao') }}</span>
              </div>
            </th>
            <th class="px-4 py-3 w-24 text-center">Ações</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-if="loading">
            <td colspan="6" class="px-4 py-8 text-center text-gray-500">Carregando...</td>
          </tr>
          <tr v-else-if="legendasOrdenadas.length === 0">
            <td colspan="6" class="px-4 py-8 text-center text-gray-500">Nenhuma legenda cadastrada.</td>
          </tr>
          <tr v-else v-for="legenda in legendasOrdenadas" :key="legenda.id" class="hover:bg-gray-50 transition-colors">
            <td class="px-4 py-3 text-gray-500 font-mono text-xs">#{{ legenda.id }}</td>
            <td class="px-4 py-3 font-bold text-paper-sidebar">
              <span class="bg-gray-200 px-2 py-1 rounded font-mono">{{ legenda.sigla }}</span>
            </td>
            <td class="px-4 py-3 text-paper-text font-medium">{{ legenda.descricao }}</td>
            <td class="px-4 py-3 text-gray-500 text-xs truncate max-w-[120px]" :title="legenda.login">{{ legenda.login || '-' }}</td>
            <td class="px-4 py-3 text-gray-500 text-xs whitespace-nowrap">{{ formatDate(legenda.data_alteracao) }}</td>
            <td class="px-4 py-3 text-center space-x-1">
              <button @click="openModal(legenda)" class="text-paper-primary hover:text-paper-primary-hover p-1.5 rounded-full hover:bg-paper-primary/10 transition-colors inline-flex cursor-pointer" title="Editar">
                <PencilSquareIcon class="h-5 w-5" />
              </button>
              <button @click="deleteLegenda(legenda.id)" class="text-paper-danger hover:text-paper-danger-hover p-1.5 rounded-full hover:bg-paper-danger/10 transition-colors inline-flex cursor-pointer" title="Excluir">
                <TrashIcon class="h-5 w-5" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-md overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center bg-paper-sidebar text-white">
          <h3 class="text-lg font-bold">{{ isEditing ? 'Editar Legenda' : 'Nova Legenda' }}</h3>
          <button @click="closeModal" class="text-white hover:text-gray-300 font-bold">&times;</button>
        </div>
        
        <form @submit.prevent="saveLegenda" class="p-6 space-y-4">
          <div v-if="error" class="bg-paper-danger/10 text-paper-danger p-3 rounded text-sm mb-4">
            {{ error }}
          </div>
          
          <div class="form-group">
            <label class="form-label">Sigla</label>
            <input v-model="form.sigla" type="text" class="form-control" required placeholder="Ex: M" maxlength="10" />
          </div>
          
          <div class="form-group">
            <label class="form-label">Descrição</label>
            <input v-model="form.descricao" type="text" class="form-control" required placeholder="Ex: Plantão Manhã" maxlength="100" />
          </div>
          
          <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <button type="button" @click="closeModal" class="px-4 py-2 text-sm text-paper-text hover:bg-gray-100 rounded-md transition-colors">
              Cancelar
            </button>
            <button type="submit" class="bg-paper-primary hover:bg-paper-primary-hover text-white px-4 py-2 rounded-md text-sm transition-colors" :disabled="saving">
              {{ saving ? 'Salvando...' : 'Salvar' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue';
import { PencilSquareIcon, TrashIcon } from '@heroicons/vue/24/outline';
import api from '../services/api';
import { useSearchFilterState } from '../composables/useSearchFilterState';

interface Legenda {
  id: number;
  sigla: string;
  descricao: string;
  login?: string;
  data_alteracao?: string;
}

const legendas = ref<Legenda[]>([]);
const loading = ref(true);
const saving = ref(false);
const error = ref('');
const showModal = ref(false);
const isEditing = ref(false);

// ==========================================
// Ordenação Dinâmica por Coluna
// ==========================================
type SortableLegendaColumn = 'id' | 'sigla' | 'descricao' | 'login' | 'data_alteracao';
const sortColumn = ref<SortableLegendaColumn>('sigla');
const sortDirection = ref<'asc' | 'desc'>('asc');

// Persistência automática do status de ordenação
useSearchFilterState('legendas', {
  sortColumn,
  sortDirection
});

const sortBy = (column: SortableLegendaColumn) => {
  if (sortColumn.value === column) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortColumn.value = column;
    sortDirection.value = 'asc';
  }
};

const getSortIcon = (column: SortableLegendaColumn) => {
  if (sortColumn.value !== column) return '↕';
  return sortDirection.value === 'asc' ? '▲' : '▼';
};

const legendasOrdenadas = computed(() => {
  const list = [...legendas.value];
  const col = sortColumn.value;
  const mult = sortDirection.value === 'asc' ? 1 : -1;

  return list.sort((a, b) => {
    let valA = a[col];
    let valB = b[col];

    if (valA === undefined || valA === null) valA = '';
    if (valB === undefined || valB === null) valB = '';

    if (typeof valA === 'number' && typeof valB === 'number') {
      return (valA - valB) * mult;
    }

    const strA = String(valA).toLowerCase();
    const strB = String(valB).toLowerCase();
    return strA.localeCompare(strB, 'pt-BR', { numeric: true }) * mult;
  });
});

const form = reactive({
  id: 0,
  sigla: '',
  descricao: ''
});

const formatDate = (dateString?: string) => {
  if (!dateString) return '-';
  const d = new Date(dateString);
  return d.toLocaleString('pt-BR');
};

const fetchLegendas = async () => {
  loading.value = true;
  try {
    const { data } = await api.get('/api/legendas');
    legendas.value = data;
  } catch (err) {
    console.error('Erro ao buscar legendas', err);
    alert('Erro ao carregar os dados.');
  } finally {
    loading.value = false;
  }
};

const openModal = (legenda?: Legenda) => {
  error.value = '';
  if (legenda) {
    isEditing.value = true;
    form.id = legenda.id;
    form.sigla = legenda.sigla;
    form.descricao = legenda.descricao;
  } else {
    isEditing.value = false;
    form.id = 0;
    form.sigla = '';
    form.descricao = '';
  }
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
};

const saveLegenda = async () => {
  saving.value = true;
  error.value = '';
  
  try {
    if (isEditing.value) {
      await api.put(`/api/legendas/${form.id}`, {
        sigla: form.sigla,
        descricao: form.descricao
      });
    } else {
      await api.post('/api/legendas', {
        sigla: form.sigla,
        descricao: form.descricao
      });
    }
    closeModal();
    fetchLegendas();
  } catch (err: any) {
    if (err.response?.data?.detail) {
      error.value = err.response.data.detail;
    } else {
      error.value = 'Erro ao salvar legenda.';
    }
  } finally {
    saving.value = false;
  }
};

const deleteLegenda = async (id: number) => {
  if (!confirm('Deseja realmente excluir esta legenda?')) return;
  
  try {
    await api.delete(`/api/legendas/${id}`);
    fetchLegendas();
  } catch (err) {
    alert('Erro ao excluir legenda.');
  }
};

onMounted(() => {
  fetchLegendas();
});
</script>
