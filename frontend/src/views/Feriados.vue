<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-800">Feriados</h1>
      <button @click="openModal()" class="inline-flex items-center gap-2 bg-paper-primary hover:bg-paper-primary-hover text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors shadow-sm focus:outline-none focus:ring-2 focus:ring-paper-primary focus:ring-offset-2">
        <PlusIcon class="h-5 w-5" />
        Novo Feriado
      </button>
    </div>

    <!-- Search/Filter -->
    <div class="bg-white p-4 rounded-xl shadow-paper border border-gray-100 flex gap-4 items-center">
      <div class="relative flex-1">
        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <MagnifyingGlassIcon class="h-5 w-5 text-gray-400" />
        </div>
        <input
          v-model="searchQuery"
          type="text"
          class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-paper-primary focus:border-paper-primary sm:text-sm transition-shadow"
          placeholder="Buscar feriado..."
        />
      </div>
      <div class="w-48">
        <select v-model="selectedAno" @change="fetchData" class="block w-full pl-3 pr-10 py-2 text-base border border-gray-300 focus:outline-none focus:ring-paper-primary focus:border-paper-primary sm:text-sm rounded-lg">
          <option value="">Todos os Anos</option>
          <option v-for="ano in anosDisponiveis" :key="ano" :value="ano">{{ ano }}</option>
        </select>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-xl shadow-paper overflow-hidden border border-gray-100">
      <div class="overflow-x-auto">
        <table class="w-full text-sm text-left">
          <thead class="bg-gray-100 text-paper-text text-xs uppercase font-semibold border-b border-gray-200 select-none">
            <tr>
              <th @click="sortBy('data')" class="px-4 py-3 cursor-pointer hover:bg-gray-200/80 transition-colors" title="Ordenar por Data">
                <div class="flex items-center gap-1">
                  <span>Data</span>
                  <span class="text-xs text-gray-500 font-mono">{{ getSortIcon('data') }}</span>
                </div>
              </th>
              <th @click="sortBy('nome')" class="px-4 py-3 cursor-pointer hover:bg-gray-200/80 transition-colors" title="Ordenar por Nome">
                <div class="flex items-center gap-1">
                  <span>Nome</span>
                  <span class="text-xs text-gray-500 font-mono">{{ getSortIcon('nome') }}</span>
                </div>
              </th>
              <th @click="sortBy('tipo')" class="px-4 py-3 cursor-pointer hover:bg-gray-200/80 transition-colors" title="Ordenar por Tipo">
                <div class="flex items-center gap-1">
                  <span>Tipo</span>
                  <span class="text-xs text-gray-500 font-mono">{{ getSortIcon('tipo') }}</span>
                </div>
              </th>
              <th class="px-4 py-3 text-center w-28">Ações</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-if="loading" class="animate-pulse">
              <td colspan="4" class="px-4 py-8 text-center text-gray-500">Carregando...</td>
            </tr>
            <tr v-else-if="filteredFeriados.length === 0">
              <td colspan="4" class="px-4 py-8 text-center text-gray-500">Nenhum feriado encontrado.</td>
            </tr>
            <tr v-else v-for="item in filteredFeriados" :key="item.id" class="hover:bg-gray-50 transition-colors">
              <td class="px-4 py-3 font-medium text-gray-800">{{ formatDateString(item.data) }}</td>
              <td class="px-4 py-3 text-gray-700">{{ item.nome }}</td>
              <td class="px-4 py-3 text-gray-600">
                <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800 border border-gray-200">
                  {{ item.tipo }}
                </span>
              </td>
              <td class="px-4 py-3 text-center space-x-1">
                <button @click="openModal(item)" class="text-paper-primary hover:text-paper-primary-hover p-1.5 rounded-full hover:bg-paper-primary/10 transition-colors inline-flex" title="Editar">
                  <PencilSquareIcon class="h-5 w-5" />
                </button>
                <button @click="deleteItem(item.id)" class="text-paper-danger hover:text-paper-danger-hover p-1.5 rounded-full hover:bg-paper-danger/10 transition-colors inline-flex" title="Excluir">
                  <TrashIcon class="h-5 w-5" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal Form -->
    <div v-if="isModalOpen" class="fixed inset-0 bg-gray-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-xl shadow-paper-lg w-full max-w-md overflow-hidden flex flex-col" @click.stop>
        <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50 shrink-0">
          <h3 class="text-lg font-semibold text-gray-800">
            {{ isEditing ? 'Editar Feriado' : 'Novo Feriado' }}
          </h3>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-600 transition-colors p-1 rounded-full hover:bg-gray-100">
            <XMarkIcon class="h-5 w-5" />
          </button>
        </div>

        <div class="p-6 overflow-y-auto">
          <form id="feriadoForm" @submit.prevent="saveItem" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Nome do Feriado *</label>
              <input v-model="form.nome" type="text" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-paper-primary focus:border-transparent text-sm" placeholder="Ex: Natal" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Data *</label>
              <input v-model="form.data" type="date" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-paper-primary focus:border-transparent text-sm" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Tipo *</label>
              <select v-model="form.tipo" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-paper-primary focus:border-transparent text-sm">
                <option value="" disabled>Selecione um Tipo</option>
                <option value="Estadual">Estadual</option>
                <option value="Institucional">Institucional</option>
                <option value="Municipal">Municipal</option>
                <option value="Nacional">Nacional</option>
              </select>
            </div>
            
            <div v-if="errorMsg" class="p-3 bg-paper-danger/10 border border-paper-danger/20 rounded-lg text-sm text-paper-danger flex items-start gap-2">
              <ExclamationCircleIcon class="h-5 w-5 shrink-0" />
              <span>{{ errorMsg }}</span>
            </div>
          </form>
        </div>

        <div class="px-6 py-4 border-t border-gray-100 bg-gray-50 flex justify-end gap-3 shrink-0">
          <button type="button" @click="closeModal" class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">
            Cancelar
          </button>
          <button type="submit" form="feriadoForm" :disabled="saving" class="px-4 py-2 text-sm font-medium text-white bg-paper-primary hover:bg-paper-primary-hover rounded-lg disabled:opacity-50 flex items-center gap-2">
            <ArrowPathIcon v-if="saving" class="h-4 w-4 animate-spin" />
            {{ isEditing ? 'Salvar Alterações' : 'Cadastrar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { 
  PlusIcon, PencilSquareIcon, TrashIcon, XMarkIcon, 
  ExclamationCircleIcon, ArrowPathIcon, MagnifyingGlassIcon
} from '@heroicons/vue/24/outline';
import api from '../services/api';
import { useSearchFilterState } from '../composables/useSearchFilterState';

const items = ref<any[]>([]);
const loading = ref(false);
const saving = ref(false);
const searchQuery = ref('');

const currentYear = new Date().getFullYear();
const selectedAno = ref<number | string>(currentYear);

// Persistência automática do status da última pesquisa/filtro
useSearchFilterState('feriados', {
  searchQuery,
  selectedAno
});

// Gera anos: atual, +2 para frente, -5 para trás
const anosDisponiveis = computed(() => {
  const anos = [];
  for (let i = currentYear - 5; i <= currentYear + 2; i++) {
    anos.push(i);
  }
  return anos.sort((a, b) => b - a);
});

const isModalOpen = ref(false);
const isEditing = ref(false);
const errorMsg = ref('');

const form = reactive({
  id: null as number | null,
  nome: '',
  data: '',
  tipo: ''
});

// ==========================================
// Ordenação Dinâmica por Coluna
// ==========================================
type SortableFeriadoColumn = 'data' | 'nome' | 'tipo';
const sortColumn = ref<SortableFeriadoColumn>('data');
const sortDirection = ref<'asc' | 'desc'>('asc');

const sortBy = (column: SortableFeriadoColumn) => {
  if (sortColumn.value === column) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortColumn.value = column;
    sortDirection.value = 'asc';
  }
};

const getSortIcon = (column: SortableFeriadoColumn) => {
  if (sortColumn.value !== column) return '↕';
  return sortDirection.value === 'asc' ? '▲' : '▼';
};

const filteredFeriados = computed(() => {
  let list = [...items.value];
  if (searchQuery.value) {
    const lower = searchQuery.value.toLowerCase();
    list = list.filter(item => 
      (item.nome && item.nome.toLowerCase().includes(lower)) ||
      (item.tipo && item.tipo.toLowerCase().includes(lower)) ||
      (item.data && item.data.includes(lower))
    );
  }

  const col = sortColumn.value;
  const mult = sortDirection.value === 'asc' ? 1 : -1;

  return list.sort((a, b) => {
    let valA = a[col];
    let valB = b[col];

    if (valA === undefined || valA === null) valA = '';
    if (valB === undefined || valB === null) valB = '';

    const strA = String(valA).toLowerCase();
    const strB = String(valB).toLowerCase();
    return strA.localeCompare(strB, 'pt-BR', { numeric: true }) * mult;
  });
});

const formatDateString = (dateStr: string) => {
  if (!dateStr) return '';
  const [y, m, d] = dateStr.split('-');
  return `${d}/${m}/${y}`;
};

const fetchData = async () => {
  loading.value = true;
  try {
    let url = '/api/feriados';
    if (selectedAno.value) {
      url += `?ano=${selectedAno.value}`;
    }
    const response = await api.get(url);
    items.value = response.data;
  } catch (err: any) {
    console.error('Erro ao carregar dados:', err);
  } finally {
    loading.value = false;
  }
};

const openModal = (item: any = null) => {
  isEditing.value = !!item;
  errorMsg.value = '';
  
  if (item) {
    form.id = item.id;
    form.nome = item.nome;
    form.data = item.data;
    form.tipo = item.tipo;
  } else {
    form.id = null;
    form.nome = '';
    form.data = '';
    form.tipo = '';
  }
  
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
};

const saveItem = async () => {
  saving.value = true;
  errorMsg.value = '';
  
  try {
    const payload = {
      nome: form.nome,
      data: form.data,
      tipo: form.tipo
    };
    
    if (isEditing.value) {
      await api.put(`/api/feriados/${form.id}`, payload);
    } else {
      await api.post('/api/feriados', payload);
    }
    
    await fetchData();
    closeModal();
  } catch (err: any) {
    errorMsg.value = err.response?.data?.detail || 'Erro ao salvar feriado.';
  } finally {
    saving.value = false;
  }
};

const deleteItem = async (id: number) => {
  if (!confirm('Tem certeza que deseja excluir este feriado?')) return;
  
  try {
    await api.delete(`/api/feriados/${id}`);
    await fetchData();
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Erro ao excluir.');
  }
};

onMounted(() => {
  fetchData();
});
</script>
