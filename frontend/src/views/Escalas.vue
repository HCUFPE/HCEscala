<template>
  <div class="escalas-container space-y-6">
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-2xl font-bold text-paper-sidebar">Cadastro de Escalas</h2>
        <p class="text-xs text-gray-500 mt-1">Gerencie as siglas de escalas, jornadas de trabalho e descrições dos turnos.</p>
      </div>
      <button @click="openModal()" class="bg-paper-primary hover:bg-paper-primary-hover text-white px-4 py-2 rounded-md text-sm transition-colors shadow-sm cursor-pointer">
        Nova Escala
      </button>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <table class="w-full text-sm text-left">
        <thead class="bg-gray-100 text-paper-text text-xs uppercase font-semibold border-b border-gray-200 select-none">
          <tr>
            <th 
              @click="sortBy('id')" 
              class="px-4 py-3 w-20 cursor-pointer hover:bg-gray-200/80 transition-colors"
              title="Clique para ordenar por ID"
            >
              <div class="flex items-center gap-1">
                <span>ID</span>
                <span class="text-xs text-gray-500 font-mono">{{ getSortIcon('id') }}</span>
              </div>
            </th>
            <th 
              @click="sortBy('sigla')" 
              class="px-4 py-3 w-32 cursor-pointer hover:bg-gray-200/80 transition-colors"
              title="Clique para ordenar por Sigla"
            >
              <div class="flex items-center gap-1">
                <span>Sigla</span>
                <span class="text-xs text-gray-500 font-mono">{{ getSortIcon('sigla') }}</span>
              </div>
            </th>
            <th 
              @click="sortBy('descricao')" 
              class="px-4 py-3 cursor-pointer hover:bg-gray-200/80 transition-colors"
              title="Clique para ordenar por Descrição"
            >
              <div class="flex items-center gap-1">
                <span>Descrição</span>
                <span class="text-xs text-gray-500 font-mono">{{ getSortIcon('descricao') }}</span>
              </div>
            </th>
            <th 
              @click="sortBy('inicio_jornada')" 
              class="px-4 py-3 w-40 cursor-pointer hover:bg-gray-200/80 transition-colors"
              title="Clique para ordenar por Horário de Jornada"
            >
              <div class="flex items-center gap-1">
                <span>Jornada</span>
                <span class="text-xs text-gray-500 font-mono">{{ getSortIcon('inicio_jornada') }}</span>
              </div>
            </th>
            <th 
              @click="sortBy('apenas_assistenciais')" 
              class="px-4 py-3 text-center w-36 cursor-pointer hover:bg-gray-200/80 transition-colors"
              title="Clique para ordenar por Categoria Assistencial"
            >
              <div class="flex items-center justify-center gap-1">
                <span>Apenas Assistenciais</span>
                <span class="text-xs text-gray-500 font-mono">{{ getSortIcon('apenas_assistenciais') }}</span>
              </div>
            </th>
            <th 
              @click="sortBy('login')" 
              class="px-4 py-3 w-32 cursor-pointer hover:bg-gray-200/80 transition-colors"
              title="Clique para ordenar por Usuário"
            >
              <div class="flex items-center gap-1">
                <span>Usuário</span>
                <span class="text-xs text-gray-500 font-mono">{{ getSortIcon('login') }}</span>
              </div>
            </th>
            <th 
              @click="sortBy('data_alteracao')" 
              class="px-4 py-3 w-36 cursor-pointer hover:bg-gray-200/80 transition-colors"
              title="Clique para ordenar por Data de Alteração"
            >
              <div class="flex items-center gap-1">
                <span>Data Alt.</span>
                <span class="text-xs text-gray-500 font-mono">{{ getSortIcon('data_alteracao') }}</span>
              </div>
            </th>
            <th class="px-4 py-3 text-center w-24">Ações</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-if="loading">
            <td colspan="8" class="px-4 py-8 text-center text-gray-500">Carregando...</td>
          </tr>
          <tr v-else-if="escalasOrdenadas.length === 0">
            <td colspan="8" class="px-4 py-8 text-center text-gray-500">Nenhuma escala cadastrada.</td>
          </tr>
          <tr v-else v-for="escala in escalasOrdenadas" :key="escala.id" class="hover:bg-gray-50 transition-colors">
            <td class="px-4 py-3 text-gray-500 font-mono text-xs">#{{ escala.id }}</td>
            <td class="px-4 py-3 font-bold text-paper-sidebar">
              <span class="bg-gray-200 px-2 py-1 rounded font-mono">{{ escala.sigla }}</span>
            </td>
            <td class="px-4 py-3 font-medium text-gray-800">{{ escala.descricao || '-' }}</td>
            <td class="px-4 py-3 text-paper-text font-mono text-xs">{{ formatTime(escala.inicio_jornada) }} - {{ formatTime(escala.fim_jornada) }}</td>
            <td class="px-4 py-3 text-center">
              <button @click="toggleAssistencial(escala)" class="focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-paper-primary rounded-full transition-transform hover:scale-105 active:scale-95">
                <span v-if="escala.apenas_assistenciais" class="px-2 py-1 bg-paper-warning/20 text-paper-warning hover:bg-paper-warning/30 transition-colors text-xs font-semibold rounded-full block">Sim</span>
                <span v-else class="px-2 py-1 bg-paper-success/20 text-paper-success hover:bg-paper-success/30 transition-colors text-xs font-semibold rounded-full block">Não</span>
              </button>
            </td>
            <td class="px-4 py-3 text-gray-500 text-xs truncate max-w-[120px]" :title="escala.login">{{ escala.login || '-' }}</td>
            <td class="px-4 py-3 text-gray-500 text-xs whitespace-nowrap">{{ formatDate(escala.data_alteracao) }}</td>
            <td class="px-4 py-3 text-center space-x-1">
              <button @click="openModal(escala)" class="text-paper-primary hover:text-paper-primary-hover p-1.5 rounded-full hover:bg-paper-primary/10 transition-colors inline-flex cursor-pointer" title="Editar">
                <PencilSquareIcon class="h-5 w-5" />
              </button>
              <button @click="deleteEscala(escala.id)" class="text-paper-danger hover:text-paper-danger-hover p-1.5 rounded-full hover:bg-paper-danger/10 transition-colors inline-flex cursor-pointer" title="Excluir">
                <TrashIcon class="h-5 w-5" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 transition-opacity">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-lg overflow-hidden transform transition-all">
        <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center bg-paper-sidebar text-white">
          <h3 class="text-lg font-bold">{{ isEditing ? 'Editar Escala' : 'Nova Escala' }}</h3>
          <button @click="closeModal" class="text-white hover:text-gray-300 font-bold text-xl cursor-pointer">&times;</button>
        </div>
        
        <form @submit.prevent="saveEscala" class="p-6 space-y-4">
          <div v-if="error" class="bg-paper-danger/10 text-paper-danger p-3 rounded text-sm mb-4">
            {{ error }}
          </div>
          
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div class="form-group mb-0">
              <label class="form-label flex items-center justify-between">
                <span>Sigla</span>
                <span class="text-[10px] text-paper-primary font-bold">ÚNICA</span>
              </label>
              <input v-model="form.sigla" type="text" class="form-control uppercase font-mono" required placeholder="Ex: M6" maxlength="20" />
            </div>
            
            <div class="form-group mb-0 sm:col-span-2">
              <label class="form-label">Descrição</label>
              <input v-model="form.descricao" type="text" class="form-control" placeholder="Ex: Manhã 6 horas" maxlength="255" />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="form-group mb-0">
              <label class="form-label">Início da Jornada</label>
              <input v-model="form.inicio_jornada" type="time" class="form-control" required />
            </div>
            
            <div class="form-group mb-0">
              <label class="form-label">Fim da Jornada</label>
              <input v-model="form.fim_jornada" type="time" class="form-control" required />
            </div>
          </div>

          <div class="form-group flex items-center mt-4">
            <input v-model="form.apenas_assistenciais" type="checkbox" id="apenas_assistenciais" class="h-4 w-4 text-paper-primary focus:ring-paper-primary border-gray-300 rounded cursor-pointer" />
            <label for="apenas_assistenciais" class="ml-2 block text-sm text-gray-900 cursor-pointer">
              Restrito para categorias assistenciais
            </label>
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

interface Escala {
  id: number;
  codigo?: string;
  sigla: string;
  descricao?: string;
  inicio_jornada: string;
  fim_jornada: string;
  apenas_assistenciais: boolean;
  login: string;
  data_alteracao: string;
}

const escalas = ref<Escala[]>([]);
const loading = ref(true);
const saving = ref(false);
const error = ref('');
const showModal = ref(false);
const isEditing = ref(false);

// ==========================================
// Ordenação Dinâmica por Coluna
// ==========================================
type SortableColumn = 'id' | 'sigla' | 'descricao' | 'inicio_jornada' | 'apenas_assistenciais' | 'login' | 'data_alteracao';
const sortColumn = ref<SortableColumn>('sigla');
const sortDirection = ref<'asc' | 'desc'>('asc');

// Persistência automática do status de ordenação
useSearchFilterState('escalas', {
  sortColumn,
  sortDirection
});

const sortBy = (column: SortableColumn) => {
  if (sortColumn.value === column) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortColumn.value = column;
    sortDirection.value = 'asc';
  }
};

const getSortIcon = (column: SortableColumn) => {
  if (sortColumn.value !== column) return '↕';
  return sortDirection.value === 'asc' ? '▲' : '▼';
};

const escalasOrdenadas = computed(() => {
  const list = [...escalas.value];
  const col = sortColumn.value;
  const mult = sortDirection.value === 'asc' ? 1 : -1;

  return list.sort((a, b) => {
    let valA = a[col];
    let valB = b[col];

    if (valA === undefined || valA === null) valA = '';
    if (valB === undefined || valB === null) valB = '';

    // Ordenação booleana
    if (typeof valA === 'boolean' && typeof valB === 'boolean') {
      return (valA === valB ? 0 : valA ? 1 : -1) * mult;
    }

    // Ordenação numérica
    if (typeof valA === 'number' && typeof valB === 'number') {
      return (valA - valB) * mult;
    }

    // Ordenação de string / texto
    const strA = String(valA).toLowerCase();
    const strB = String(valB).toLowerCase();
    return strA.localeCompare(strB, 'pt-BR', { numeric: true }) * mult;
  });
});

const form = reactive({
  id: 0,
  codigo: '',
  sigla: '',
  descricao: '',
  inicio_jornada: '',
  fim_jornada: '',
  apenas_assistenciais: false
});

const formatTime = (timeStr: string) => {
  if (!timeStr) return '';
  return timeStr.substring(0, 5);
};

const formatDate = (dateString: string) => {
  if (!dateString) return '-';
  const d = new Date(dateString);
  return d.toLocaleString('pt-BR');
};

const fetchEscalas = async () => {
  loading.value = true;
  try {
    const { data } = await api.get('/api/escalas');
    escalas.value = data;
  } catch (err: any) {
    console.error('Erro ao buscar escalas', err);
    if(err.response?.status !== 401) { // auth handles 401 usually
        alert('Erro ao carregar os dados das escalas.');
    }
  } finally {
    loading.value = false;
  }
};

const openModal = (escala?: Escala) => {
  error.value = '';
  if (escala) {
    isEditing.value = true;
    form.id = escala.id;
    form.codigo = escala.codigo || escala.sigla;
    form.sigla = escala.sigla;
    form.descricao = escala.descricao || '';
    form.inicio_jornada = formatTime(escala.inicio_jornada);
    form.fim_jornada = formatTime(escala.fim_jornada);
    form.apenas_assistenciais = escala.apenas_assistenciais;
  } else {
    isEditing.value = false;
    form.id = 0;
    form.codigo = '';
    form.sigla = '';
    form.descricao = '';
    form.inicio_jornada = '';
    form.fim_jornada = '';
    form.apenas_assistenciais = false;
  }
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
};

const saveEscala = async () => {
  saving.value = true;
  error.value = '';

  const siglaLimpa = form.sigla.trim().toUpperCase();
  if (!siglaLimpa) {
    error.value = 'A sigla é obrigatória.';
    saving.value = false;
    return;
  }
  
  // Format times properly for backend
  const payload = {
    codigo: form.codigo || siglaLimpa,
    sigla: siglaLimpa,
    descricao: form.descricao?.trim() || '',
    inicio_jornada: form.inicio_jornada.length === 5 ? form.inicio_jornada + ':00' : form.inicio_jornada,
    fim_jornada: form.fim_jornada.length === 5 ? form.fim_jornada + ':00' : form.fim_jornada,
    apenas_assistenciais: form.apenas_assistenciais
  };
  
  try {
    if (isEditing.value) {
      await api.put(`/api/escalas/${form.id}`, payload);
    } else {
      await api.post('/api/escalas', payload);
    }
    closeModal();
    fetchEscalas();
  } catch (err: any) {
    if (err.response?.data?.detail) {
      error.value = err.response.data.detail;
    } else {
      error.value = 'Erro ao salvar escala.';
    }
  } finally {
    saving.value = false;
  }
};

const toggleAssistencial = async (escala: Escala) => {
  const newValue = !escala.apenas_assistenciais;
  
  // Optimistic update for quick UI feedback
  escala.apenas_assistenciais = newValue;
  
  try {
    const payload = {
      codigo: escala.codigo || escala.sigla,
      sigla: escala.sigla,
      descricao: escala.descricao || '',
      inicio_jornada: formatTime(escala.inicio_jornada) + ':00',
      fim_jornada: formatTime(escala.fim_jornada) + ':00',
      apenas_assistenciais: newValue
    };
    await api.put(`/api/escalas/${escala.id}`, payload);
  } catch (err) {
    // Revert on error
    escala.apenas_assistenciais = !newValue;
    alert('Erro ao atualizar o status assistencial da escala.');
  }
};

const deleteEscala = async (id: number) => {
  if (!confirm('Deseja realmente excluir esta escala?')) return;
  
  try {
    await api.delete(`/api/escalas/${id}`);
    fetchEscalas();
  } catch (err) {
    alert('Erro ao excluir escala.');
  }
};

onMounted(() => {
  fetchEscalas();
});
</script>
