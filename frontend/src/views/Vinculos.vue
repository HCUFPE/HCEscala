<template>
  <div class="vinculos-container space-y-6">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-paper-sidebar">Cadastro de Vínculos</h2>
      <button @click="openModal()" class="bg-paper-primary hover:bg-paper-primary-hover text-white px-4 py-2 rounded-md text-sm transition-colors shadow-sm">
        Novo Vínculo
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
            <th @click="sortBy('nome')" class="px-4 py-3 cursor-pointer hover:bg-gray-200/80 transition-colors" title="Ordenar por Nome do Vínculo">
              <div class="flex items-center gap-1">
                <span>Nome do Vínculo</span>
                <span class="text-xs text-gray-500 font-mono">{{ getSortIcon('nome') }}</span>
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
            <td colspan="5" class="px-4 py-8 text-center text-gray-500">Carregando...</td>
          </tr>
          <tr v-else-if="vinculosOrdenados.length === 0">
            <td colspan="5" class="px-4 py-8 text-center text-gray-500">Nenhum vínculo cadastrado.</td>
          </tr>
          <tr v-else v-for="vinculo in vinculosOrdenados" :key="vinculo.id" class="hover:bg-gray-50 transition-colors">
            <td class="px-4 py-3 text-gray-500 font-mono text-xs">#{{ vinculo.id }}</td>
            <td class="px-4 py-3 font-medium text-gray-800">{{ vinculo.nome }}</td>
            <td class="px-4 py-3 text-gray-500 text-xs truncate max-w-[120px]" :title="vinculo.login">{{ vinculo.login || '-' }}</td>
            <td class="px-4 py-3 text-gray-500 text-xs whitespace-nowrap">{{ formatDate(vinculo.data_alteracao) }}</td>
            <td class="px-4 py-3 text-center space-x-1">
              <button @click="openModal(vinculo)" class="text-paper-primary hover:text-paper-primary-hover p-1.5 rounded-full hover:bg-paper-primary/10 transition-colors inline-flex cursor-pointer" title="Editar">
                <PencilSquareIcon class="h-5 w-5" />
              </button>
              <button @click="deleteVinculo(vinculo.id)" class="text-paper-danger hover:text-paper-danger-hover p-1.5 rounded-full hover:bg-paper-danger/10 transition-colors inline-flex cursor-pointer" title="Excluir">
                <TrashIcon class="h-5 w-5" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 transition-opacity">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-md overflow-hidden transform transition-all">
        <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center bg-paper-sidebar text-white">
          <h3 class="text-lg font-bold">{{ isEditing ? 'Editar Vínculo' : 'Novo Vínculo' }}</h3>
          <button @click="closeModal" class="text-white hover:text-gray-300 font-bold text-xl">&times;</button>
        </div>
        
        <form @submit.prevent="saveVinculo" class="p-6 space-y-4">
          <div v-if="error" class="bg-paper-danger/10 text-paper-danger p-3 rounded text-sm mb-4">
            {{ error }}
          </div>
          
          <div class="form-group mb-0">
            <label class="form-label">Nome do Vínculo</label>
            <input v-model="form.nome" type="text" class="form-control" required placeholder="Ex: CLT" maxlength="100" />
          </div>
          
          <div class="flex justify-end space-x-3 pt-6 border-t border-gray-200 mt-6">
            <button type="button" @click="closeModal" class="px-4 py-2 text-sm text-paper-text hover:bg-gray-100 rounded-md transition-colors">
              Cancelar
            </button>
            <button type="submit" class="bg-paper-primary hover:bg-paper-primary-hover text-white px-4 py-2 rounded-md text-sm transition-colors shadow" :disabled="saving">
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

interface Vinculo {
  id: number;
  nome: string;
  login: string;
  data_alteracao: string;
}

const vinculos = ref<Vinculo[]>([]);
const loading = ref(true);
const saving = ref(false);
const error = ref('');
const showModal = ref(false);
const isEditing = ref(false);

// ==========================================
// Ordenação Dinâmica por Coluna
// ==========================================
type SortableVinculoColumn = 'id' | 'nome' | 'login' | 'data_alteracao';
const sortColumn = ref<SortableVinculoColumn>('nome');
const sortDirection = ref<'asc' | 'desc'>('asc');

// Persistência automática do status de ordenação
useSearchFilterState('vinculos', {
  sortColumn,
  sortDirection
});

const sortBy = (column: SortableVinculoColumn) => {
  if (sortColumn.value === column) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortColumn.value = column;
    sortDirection.value = 'asc';
  }
};

const getSortIcon = (column: SortableVinculoColumn) => {
  if (sortColumn.value !== column) return '↕';
  return sortDirection.value === 'asc' ? '▲' : '▼';
};

const vinculosOrdenados = computed(() => {
  const list = [...vinculos.value];
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
  nome: ''
});

const formatDate = (dateString: string) => {
  if (!dateString) return '-';
  const d = new Date(dateString);
  return d.toLocaleString('pt-BR');
};

const fetchVinculos = async () => {
  loading.value = true;
  try {
    const { data } = await api.get('/api/vinculos');
    vinculos.value = data;
  } catch (err: any) {
    console.error('Erro ao buscar vínculos', err);
    if(err.response?.status !== 401) {
        alert('Erro ao carregar os dados dos vínculos.');
    }
  } finally {
    loading.value = false;
  }
};

const openModal = (vinculo?: Vinculo) => {
  error.value = '';
  if (vinculo) {
    isEditing.value = true;
    form.id = vinculo.id;
    form.nome = vinculo.nome;
  } else {
    isEditing.value = false;
    form.id = 0;
    form.nome = '';
  }
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
};

const saveVinculo = async () => {
  saving.value = true;
  error.value = '';
  
  const payload = {
    nome: form.nome
  };
  
  try {
    if (isEditing.value) {
      await api.put(`/api/vinculos/${form.id}`, payload);
    } else {
      await api.post('/api/vinculos', payload);
    }
    closeModal();
    fetchVinculos();
  } catch (err: any) {
    if (err.response?.data?.detail) {
      error.value = err.response.data.detail;
    } else {
      error.value = 'Erro ao salvar vínculo.';
    }
  } finally {
    saving.value = false;
  }
};

const deleteVinculo = async (id: number) => {
  if (!confirm('Deseja realmente excluir este vínculo?')) return;
  
  try {
    await api.delete(`/api/vinculos/${id}`);
    fetchVinculos();
  } catch (err) {
    alert('Erro ao excluir vínculo.');
  }
};

onMounted(() => {
  fetchVinculos();
});
</script>
