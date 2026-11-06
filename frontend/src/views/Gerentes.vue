<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 tracking-tight flex items-center gap-2">
          <span>Gestão de Gerentes & Chefias</span>
        </h1>
        <p class="text-xs sm:text-sm text-gray-500 mt-1">
          Atribuição de responsabilidades e controle de acesso por Unidade Organizacional (UORG) ou Posto de Serviço
        </p>
      </div>

      <div class="flex items-center gap-2">
        <button 
          @click="openCreateModal" 
          type="button" 
          class="btn btn-primary flex items-center gap-1.5 shadow-sm text-xs sm:text-sm cursor-pointer"
        >
          <PlusIcon class="h-4 w-4" />
          <span>Atribuir Novo Gerente</span>
        </button>
      </div>
    </div>

    <!-- Filter Bar -->
    <Card class="bg-white border-gray-200">
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 items-end">
        <div class="form-group mb-0">
          <label class="form-label">Buscar Gestor</label>
          <div class="relative">
            <input 
              v-model="searchTerm" 
              type="text" 
              placeholder="Nome ou login de rede..."
              class="form-control pl-9 text-sm"
            />
            <MagnifyingGlassIcon class="h-4 w-4 text-gray-400 absolute left-3 top-3" />
          </div>
        </div>

        <div class="form-group mb-0">
          <label class="form-label">Filtrar por Nível</label>
          <select v-model="filterNivel" class="form-control text-sm">
            <option value="TODOS">Todos os Níveis</option>
            <option value="DIVGP_ADMIN">DIVGP / Administrador Geral</option>
            <option value="UORG">Gerente de UORG</option>
            <option value="POSTO">Responsável por Posto</option>
          </select>
        </div>

        <div class="form-group mb-0">
          <label class="form-label">Filtrar por UORG</label>
          <select v-model="filterUorgId" class="form-control text-sm">
            <option :value="undefined">Todas as UORGs</option>
            <option v-for="u in sortedUorgs" :key="u.id" :value="u.id">
              {{ u.nome }}
            </option>
          </select>
        </div>

        <div class="flex items-center gap-2">
          <button 
            @click="clearFilters" 
            type="button" 
            class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-xs font-semibold transition-colors h-[38px] cursor-pointer"
          >
            Limpar Filtros
          </button>
        </div>
      </div>
    </Card>

    <!-- Table of Managers -->
    <div class="bg-white rounded-xl shadow-xs border border-gray-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-xs text-left">
          <thead class="bg-gray-50 text-paper-sidebar uppercase font-bold text-[11px] border-b border-gray-200 select-none">
            <tr>
              <th @click="sortBy('usuario')" class="px-4 py-3.5 cursor-pointer hover:bg-gray-100 transition-colors" title="Ordenar por Gestor / Usuário">
                <div class="flex items-center gap-1">
                  <span>Gestor / Usuário</span>
                  <span class="text-xs text-gray-500 font-mono">{{ getSortIcon('usuario') }}</span>
                </div>
              </th>
              <th @click="sortBy('nivel')" class="px-4 py-3.5 cursor-pointer hover:bg-gray-100 transition-colors" title="Ordenar por Nível">
                <div class="flex items-center gap-1">
                  <span>Nível de Gestão</span>
                  <span class="text-xs text-gray-500 font-mono">{{ getSortIcon('nivel') }}</span>
                </div>
              </th>
              <th @click="sortBy('escopo')" class="px-4 py-3.5 cursor-pointer hover:bg-gray-100 transition-colors" title="Ordenar por Escopo">
                <div class="flex items-center gap-1">
                  <span>Escopo Atribuído (Hierarquia)</span>
                  <span class="text-xs text-gray-500 font-mono">{{ getSortIcon('escopo') }}</span>
                </div>
              </th>
              <th @click="sortBy('ativo')" class="px-4 py-3.5 text-center cursor-pointer hover:bg-gray-100 transition-colors" title="Ordenar por Status">
                <div class="flex items-center justify-center gap-1">
                  <span>Status</span>
                  <span class="text-xs text-gray-500 font-mono">{{ getSortIcon('ativo') }}</span>
                </div>
              </th>
              <th @click="sortBy('data_alteracao')" class="px-4 py-3.5 cursor-pointer hover:bg-gray-100 transition-colors" title="Ordenar por Auditoria">
                <div class="flex items-center gap-1">
                  <span>Auditoria</span>
                  <span class="text-xs text-gray-500 font-mono">{{ getSortIcon('data_alteracao') }}</span>
                </div>
              </th>
              <th class="px-4 py-3.5 text-center">Ações</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-if="loading">
              <td colspan="6" class="px-4 py-12 text-center text-gray-500">
                <div class="flex flex-col items-center justify-center gap-2">
                  <div class="w-7 h-7 border-4 border-paper-primary border-t-transparent rounded-full animate-spin"></div>
                  <span>Carregando gerentes cadastrados...</span>
                </div>
              </td>
            </tr>

            <tr v-else-if="filteredGerencias.length === 0">
              <td colspan="6" class="px-4 py-12 text-center text-gray-500">
                <p class="font-medium text-gray-700">Nenhum gerente encontrado com os filtros selecionados.</p>
                <p class="text-xs text-gray-400 mt-1">Clique em "Atribuir Novo Gerente" para cadastrar um gestor de UORG ou posto.</p>
              </td>
            </tr>

            <tr 
              v-else 
              v-for="item in filteredGerencias" 
              :key="item.id" 
              class="hover:bg-slate-50 transition-colors"
            >
              <td class="px-4 py-3 font-medium text-gray-900">
                <div class="font-bold text-gray-900">{{ item.nome }}</div>
                <div class="text-[11px] text-gray-500 font-mono flex items-center gap-1">
                  <span>Login: {{ item.usuario }}</span>
                </div>
              </td>

              <td class="px-4 py-3">
                <span 
                  class="px-2.5 py-1 rounded-full text-[10px] font-bold inline-flex items-center gap-1"
                  :class="getNivelBadgeClass(item.nivel)"
                >
                  <span>{{ getNivelLabel(item.nivel) }}</span>
                </span>
              </td>

              <td class="px-4 py-3 text-gray-700">
                <div v-if="item.nivel === 'DIVGP_ADMIN' || item.nivel === 'DIGP_ADMIN'" class="text-xs font-semibold text-purple-900 flex items-center gap-1">
                  <span>🏛️ Todo o Hospital (Acesso Irrestrito)</span>
                </div>
                <div v-else-if="item.nivel === 'UORG' || item.nivel === 'SETOR' || item.nivel === 'UNIDADE'" class="text-xs">
                  <span class="font-bold text-blue-950">UORG: {{ item.uorg?.nome || item.unidade?.nome || item.setor?.nome || '-' }}</span>
                  <p v-if="item.uorg?.uorg_pai" class="text-[10px] text-gray-500 mt-0.5">↳ Subordinada a: {{ item.uorg.uorg_pai.nome }}</p>
                  <p v-else class="text-[10px] text-gray-500 mt-0.5">↳ UORG Raiz (Acesso a todas as subordinadas em cascata)</p>
                </div>
                <div v-else-if="item.nivel === 'POSTO'" class="text-xs">
                  <span class="font-bold text-amber-950">Posto: {{ item.posto?.nome || '-' }}</span>
                  <p class="text-[10px] text-gray-500 mt-0.5">↳ UORG: {{ item.posto?.uorg?.nome || '-' }}</p>
                </div>
              </td>

              <td class="px-4 py-3 text-center">
                <button 
                  @click="toggleAtivo(item)"
                  class="px-2 py-0.5 rounded text-[10px] font-bold cursor-pointer transition-colors"
                  :class="item.ativo ? 'bg-emerald-100 text-emerald-800 hover:bg-emerald-200' : 'bg-rose-100 text-rose-800 hover:bg-rose-200'"
                  :title="item.ativo ? 'Clique para desativar' : 'Clique para ativar'"
                >
                  {{ item.ativo ? 'Ativo' : 'Inativo' }}
                </button>
              </td>

              <td class="px-4 py-3 text-[11px] text-gray-500">
                <div>Por: {{ item.login }}</div>
                <div>{{ formatDate(item.data_alteracao) }}</div>
              </td>

              <td class="px-4 py-3 text-center space-x-2 whitespace-nowrap">
                <button 
                  @click="openEditModal(item)"
                  class="p-1 text-paper-primary hover:bg-paper-primary/10 rounded transition-colors inline-flex cursor-pointer"
                  title="Editar Atribuição"
                >
                  <PencilSquareIcon class="h-4 w-4" />
                </button>
                <button 
                  @click="deleteGerencia(item.id)"
                  class="p-1 text-paper-danger hover:bg-paper-danger/10 rounded transition-colors inline-flex cursor-pointer"
                  title="Excluir Atribuição"
                >
                  <TrashIcon class="h-4 w-4" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal: Atribuir / Editar Gerente -->
    <div v-if="showModal" class="fixed inset-0 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-fade-in">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg overflow-hidden flex flex-col max-h-[90vh]">
        <!-- Header -->
        <div class="px-6 py-4 bg-paper-sidebar text-white flex justify-between items-center shrink-0">
          <div>
            <h3 class="text-lg font-bold">
              {{ editingId ? 'Editar Atribuição de Gerência' : 'Nova Atribuição de Gerência' }}
            </h3>
            <p class="text-xs text-blue-200">
              Vincule um usuário ao seu escopo hierárquico de atuação
            </p>
          </div>
          <button @click="closeModal" class="text-white hover:text-gray-300 text-xl font-bold p-1">&times;</button>
        </div>

        <!-- Body -->
        <div class="p-6 overflow-y-auto space-y-4 flex-1">
          <div v-if="modalError" class="p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-800">
            {{ modalError }}
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="form-group mb-0">
              <label class="form-label">Login de Rede / Usuário AD <span class="text-red-500">*</span></label>
              <input 
                v-model="form.usuario" 
                type="text" 
                placeholder="Ex: joao.silva"
                class="form-control text-sm"
                required
              />
            </div>

            <div class="form-group mb-0">
              <label class="form-label">Nome Completo do Gestor <span class="text-red-500">*</span></label>
              <input 
                v-model="form.nome" 
                type="text" 
                placeholder="Ex: Dr. João da Silva"
                class="form-control text-sm"
                required
              />
            </div>
          </div>

          <!-- Nível de Gestão -->
          <div class="form-group mb-0">
            <label class="form-label">Nível Hierárquico de Gestão <span class="text-red-500">*</span></label>
            <select v-model="form.nivel" class="form-control text-sm font-semibold" @change="onNivelChange">
              <option value="UORG">Gerente de UORG (Acesso à UORG e suas subordinadas em cascata)</option>
              <option value="POSTO">Responsável por Posto de Serviço (Visão exclusiva do Posto)</option>
              <option value="DIVGP_ADMIN">DIVGP / Administrador Geral (Acesso irrestrito a todo o hospital)</option>
            </select>
          </div>

          <!-- Cascading Selection: UORG -->
          <div v-if="form.nivel === 'UORG' || form.nivel === 'SETOR' || form.nivel === 'UNIDADE'" class="form-group mb-0 p-3 bg-blue-50/60 rounded-xl border border-blue-200">
            <label class="form-label text-blue-950 font-bold">Unidade Organizacional (UORG) <span class="text-red-500">*</span></label>
            <select v-model="form.uorg_id" class="form-control text-sm" required>
              <option :value="null" disabled>Selecione a UORG...</option>
              <option v-for="u in sortedUorgs" :key="u.id" :value="u.id">
                {{ u.nome }} {{ u.sigla ? `(${u.sigla})` : '' }} {{ u.uorg_pai ? `— Subordinada a: ${u.uorg_pai.nome}` : '— (Nível Raiz)' }}
              </option>
            </select>
            <p class="text-[11px] text-blue-800 mt-1.5">
              * O gestor terá acesso automático a todas as UORGs e postos subordinados na árvore hierárquica.
            </p>
          </div>

          <!-- Cascading Selection: Posto -->
          <div v-if="form.nivel === 'POSTO'" class="form-group mb-0 p-3 bg-amber-50/60 rounded-xl border border-amber-200 space-y-3">
            <div>
              <label class="form-label text-amber-950 font-bold">Posto de Serviço <span class="text-red-500">*</span></label>
              <select v-model="form.posto_id" class="form-control text-sm" required>
                <option :value="null" disabled>Selecione o Posto...</option>
                <option v-for="p in sortedPostos" :key="p.id" :value="p.id">
                  {{ p.nome }} (UORG: {{ p.uorg?.nome || '-' }})
                </option>
              </select>
            </div>
            <p class="text-[11px] text-amber-800">
              * O responsável gerenciará apenas as escalas do seu posto de serviço específico.
            </p>
          </div>

          <!-- Status Ativo -->
          <div class="flex items-center gap-2 pt-2">
            <input 
              v-model="form.ativo" 
              type="checkbox" 
              id="ativoCheckbox" 
              class="w-4 h-4 text-paper-primary rounded border-gray-300 focus:ring-paper-primary"
            />
            <label for="ativoCheckbox" class="text-xs font-semibold text-gray-700 cursor-pointer">
              Atribuição Ativa (Permite acesso imediato ao painel)
            </label>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-6 py-3 bg-gray-50 border-t border-gray-100 flex justify-end gap-2 shrink-0">
          <button 
            @click="closeModal" 
            type="button" 
            class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg text-xs font-semibold transition-colors cursor-pointer"
          >
            Cancelar
          </button>
          <button 
            @click="saveGerencia" 
            type="button" 
            :disabled="saving" 
            class="btn btn-primary text-xs sm:text-sm flex items-center gap-1.5 shadow-sm cursor-pointer disabled:opacity-50"
          >
            <span v-if="saving" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            <span>{{ editingId ? 'Salvar Alterações' : 'Conceder Acesso' }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { 
  PlusIcon, PencilSquareIcon, TrashIcon, MagnifyingGlassIcon 
} from '@heroicons/vue/24/outline';
import Card from '../components/Card.vue';
import gerenciaService, { type UsuarioGerenciaItem } from '../services/gerenciaService';
import api from '../services/api';
import { useSearchFilterState } from '../composables/useSearchFilterState';

const gerencias = ref<UsuarioGerenciaItem[]>([]);
const uorgs = ref<any[]>([]);
const postos = ref<any[]>([]);

const sortedUorgs = computed(() => {
  return [...uorgs.value].sort((a, b) => 
    (a.nome || '').localeCompare(b.nome || '', 'pt-BR', { sensitivity: 'base' })
  );
});

const sortedPostos = computed(() => {
  return [...postos.value].sort((a, b) => 
    (a.nome || '').localeCompare(b.nome || '', 'pt-BR', { sensitivity: 'base' })
  );
});
const loading = ref(false);
const saving = ref(false);
const showModal = ref(false);
const editingId = ref<number | null>(null);
const modalError = ref('');

const searchTerm = ref('');
const filterNivel = ref('TODOS');
const filterUorgId = ref<number | undefined>(undefined);

// Persistência automática do status da última pesquisa/filtro
const { clearSavedState: clearSavedFilters } = useSearchFilterState('gerentes', {
  searchTerm,
  filterNivel,
  filterUorgId
});

const form = reactive({
  usuario: '',
  nome: '',
  nivel: 'UORG',
  uorg_id: null as number | null,
  setor_id: null as number | null,
  unidade_id: null as number | null,
  posto_id: null as number | null,
  ativo: true
});

const onNivelChange = () => {
  if (form.nivel === 'DIVGP_ADMIN') {
    form.uorg_id = null;
    form.setor_id = null;
    form.unidade_id = null;
    form.posto_id = null;
  } else if (form.nivel === 'UORG') {
    form.posto_id = null;
    if (!form.uorg_id && uorgs.value.length > 0) {
      form.uorg_id = uorgs.value[0].id;
    }
  } else if (form.nivel === 'POSTO') {
    form.uorg_id = null;
    if (!form.posto_id && postos.value.length > 0) {
      form.posto_id = postos.value[0].id;
    }
  }
};

const filteredGerencias = computed(() => {
  const filtered = gerencias.value.filter(g => {
    // Search
    if (searchTerm.value.trim()) {
      const q = searchTerm.value.toLowerCase();
      const matchNome = g.nome.toLowerCase().includes(q);
      const matchUser = g.usuario.toLowerCase().includes(q);
      const matchUorg = (g.uorg?.nome || g.unidade?.nome || g.setor?.nome || '').toLowerCase().includes(q);
      const matchPosto = (g.posto?.nome || '').toLowerCase().includes(q);
      if (!matchNome && !matchUser && !matchUorg && !matchPosto) return false;
    }

    // Filter Nivel
    if (filterNivel.value !== 'TODOS') {
      if (filterNivel.value === 'UORG') {
        if (!['UORG', 'SETOR', 'UNIDADE'].includes(g.nivel)) return false;
      } else if (g.nivel !== filterNivel.value) {
        return false;
      }
    }

    // Filter UORG
    if (filterUorgId.value) {
      const gUorgId = g.uorg_id || g.unidade_id || g.setor_id;
      if (gUorgId !== filterUorgId.value) return false;
    }

    return true;
  });

  const list = [...filtered];
  list.sort((a, b) => {
    let valA = '';
    let valB = '';

    if (sortColumn.value === 'usuario') {
      valA = `${a.nome || ''} ${a.usuario || ''}`;
      valB = `${b.nome || ''} ${b.usuario || ''}`;
    } else if (sortColumn.value === 'nivel') {
      valA = a.nivel || '';
      valB = b.nivel || '';
    } else if (sortColumn.value === 'escopo') {
      const getEscopo = (item: any) => {
        if (item.nivel === 'DIVGP_ADMIN' || item.nivel === 'DIGP_ADMIN') return 'Todo o Hospital';
        if (item.nivel === 'POSTO') return item.posto?.nome || '';
        return item.uorg?.nome || item.unidade?.nome || item.setor?.nome || '';
      };
      valA = getEscopo(a);
      valB = getEscopo(b);
    } else if (sortColumn.value === 'ativo') {
      const numA = a.ativo ? 1 : 0;
      const numB = b.ativo ? 1 : 0;
      return sortDirection.value === 'asc' ? numA - numB : numB - numA;
    } else if (sortColumn.value === 'data_alteracao') {
      valA = a.data_alteracao || '';
      valB = b.data_alteracao || '';
    }

    const comparison = valA.localeCompare(valB, 'pt-BR', { numeric: true, sensitivity: 'base' });
    return sortDirection.value === 'asc' ? comparison : -comparison;
  });

  return list;
});

type SortableGerenteColumn = 'usuario' | 'nivel' | 'escopo' | 'ativo' | 'data_alteracao';
const sortColumn = ref<SortableGerenteColumn>('usuario');
const sortDirection = ref<'asc' | 'desc'>('asc');

const sortBy = (column: SortableGerenteColumn) => {
  if (sortColumn.value === column) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortColumn.value = column;
    sortDirection.value = 'asc';
  }
};

const getSortIcon = (column: SortableGerenteColumn) => {
  if (sortColumn.value !== column) return '↕';
  return sortDirection.value === 'asc' ? '▲' : '▼';
};

const getNivelLabel = (nivel: string) => {
  switch (nivel) {
    case 'DIVGP_ADMIN':
    case 'DIGP_ADMIN':
      return 'DIVGP / ADMIN GERAL';
    case 'UORG':
    case 'SETOR':
      return 'GERENTE DE UORG';
    case 'UNIDADE':
      return 'GERENTE DE UNIDADE';
    case 'POSTO':
      return 'RESPONSÁVEL POR POSTO';
    default:
      return nivel;
  }
};

const getNivelBadgeClass = (nivel: string) => {
  switch (nivel) {
    case 'DIVGP_ADMIN':
    case 'DIGP_ADMIN':
      return 'bg-purple-100 text-purple-900 border border-purple-300';
    case 'UORG':
    case 'SETOR':
      return 'bg-blue-100 text-blue-900 border border-blue-300';
    case 'UNIDADE':
      return 'bg-emerald-100 text-emerald-900 border border-emerald-300';
    case 'POSTO':
      return 'bg-amber-100 text-amber-900 border border-amber-300';
    default:
      return 'bg-gray-100 text-gray-700';
  }
};

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-';
  const d = new Date(dateStr);
  return d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' });
};

const clearFilters = () => {
  searchTerm.value = '';
  filterNivel.value = 'TODOS';
  filterUorgId.value = undefined;
  clearSavedFilters();
};

const fetchData = async () => {
  loading.value = true;
  try {
    const [gerRes, uorgRes, posRes] = await Promise.all([
      gerenciaService.getAll(),
      api.get('/api/uorgs'),
      api.get('/api/postos')
    ]);
    gerencias.value = gerRes;
    uorgs.value = uorgRes.data;
    postos.value = posRes.data;
  } catch (error) {
    console.error('Erro ao carregar dados de gerências:', error);
  } finally {
    loading.value = false;
  }
};

const openCreateModal = () => {
  editingId.value = null;
  modalError.value = '';
  form.usuario = '';
  form.nome = '';
  form.nivel = 'UORG';
  form.uorg_id = uorgs.value[0]?.id || null;
  form.setor_id = null;
  form.unidade_id = null;
  form.posto_id = null;
  form.ativo = true;
  showModal.value = true;
};

const openEditModal = (item: UsuarioGerenciaItem) => {
  editingId.value = item.id;
  modalError.value = '';
  form.usuario = item.usuario;
  form.nome = item.nome;
  form.nivel = item.nivel === 'SETOR' || item.nivel === 'UNIDADE' ? 'UORG' : item.nivel;
  form.uorg_id = item.uorg_id || item.unidade_id || item.setor_id || null;
  form.setor_id = null;
  form.unidade_id = null;
  form.posto_id = item.posto_id || null;
  form.ativo = item.ativo;
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
};

const toggleAtivo = async (item: UsuarioGerenciaItem) => {
  try {
    await gerenciaService.update(item.id, { ativo: !item.ativo });
    item.ativo = !item.ativo;
  } catch (err: any) {
    alert('Erro ao alterar status: ' + (err.response?.data?.detail || err.message));
  }
};

const deleteGerencia = async (id: number) => {
  if (!confirm('Deseja realmente revogar esta atribuição de gerência?')) return;
  try {
    await gerenciaService.delete(id);
    await fetchData();
  } catch (err: any) {
    alert('Erro ao excluir gerência: ' + (err.response?.data?.detail || err.message));
  }
};

const saveGerencia = async () => {
  if (!form.usuario.trim()) {
    modalError.value = 'O login de rede do usuário é obrigatório.';
    return;
  }
  if (!form.nome.trim()) {
    modalError.value = 'O nome completo do gestor é obrigatório.';
    return;
  }
  if (form.nivel === 'UORG' && !form.uorg_id) {
    modalError.value = 'Selecione a Unidade Organizacional (UORG).';
    return;
  }
  if (form.nivel === 'POSTO' && !form.posto_id) {
    modalError.value = 'Selecione o posto de serviço de atuação.';
    return;
  }

  saving.value = true;
  modalError.value = '';

  try {
    const payload: any = {
      usuario: form.usuario.trim(),
      nome: form.nome.trim(),
      nivel: form.nivel,
      uorg_id: form.nivel === 'UORG' ? form.uorg_id : null,
      posto_id: form.nivel === 'POSTO' ? form.posto_id : null,
      ativo: form.ativo
    };

    if (editingId.value) {
      await gerenciaService.update(editingId.value, payload);
    } else {
      await gerenciaService.create(payload);
    }

    await fetchData();
    closeModal();
  } catch (err: any) {
    const detail = err.response?.data?.detail;
    if (typeof detail === 'string') {
      modalError.value = detail;
    } else if (Array.isArray(detail)) {
      modalError.value = detail.map((d: any) => d.msg || JSON.stringify(d)).join('; ');
    } else if (err.response?.data?.message) {
      modalError.value = err.response.data.message;
    } else {
      modalError.value = err.message || 'Erro ao salvar atribuição.';
    }
  } finally {
    saving.value = false;
  }
};

onMounted(() => {
  fetchData();
});
</script>
