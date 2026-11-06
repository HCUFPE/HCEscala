<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">Unidades Organizacionais</h1>
        <p class="text-sm text-gray-500 mt-1">Gestão da estrutura hierárquica hospitalar (UORGs) e postos de serviço</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="bg-white rounded-xl shadow-paper overflow-hidden border border-gray-100">
      <div class="border-b border-gray-200">
        <nav class="-mb-px flex" aria-label="Tabs">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="currentTab = tab.id"
            :class="[
              currentTab === tab.id
                ? 'border-paper-primary text-paper-primary'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
              'w-1/2 py-4 px-1 text-center border-b-2 font-medium text-sm transition-colors flex items-center justify-center gap-2 cursor-pointer'
            ]"
          >
            <BuildingOfficeIcon v-if="tab.id === 'uorgs'" class="h-5 w-5" />
            <MapPinIcon v-else class="h-5 w-5" />
            {{ tab.name }}
          </button>
        </nav>
      </div>

      <!-- Tab Content -->
      <div class="p-6">
        <!-- TAB 1: UORGs -->
        <div v-if="currentTab === 'uorgs'" class="space-y-4">
          <div class="flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-3">
            <div class="relative flex-1 max-w-md">
              <MagnifyingGlassIcon class="h-5 w-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input 
                v-model="searchUorg" 
                type="text" 
                placeholder="Buscar por nome, sigla, código ou UORG pai..." 
                class="w-full pl-10 pr-9 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-paper-primary/20 focus:border-paper-primary"
              />
              <button 
                v-if="searchUorg" 
                @click="searchUorg = ''" 
                class="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 p-1 rounded-full"
                title="Limpar busca"
              >
                <XMarkIcon class="h-4 w-4" />
              </button>
            </div>
            <div class="flex items-center gap-2">
              <button @click="openModal('uorg')" class="inline-flex items-center justify-center gap-2 bg-paper-primary hover:bg-paper-primary-hover text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors shadow-sm focus:outline-none focus:ring-2 focus:ring-paper-primary focus:ring-offset-2 cursor-pointer">
                <PlusIcon class="h-5 w-5" />
                Nova UORG
              </button>
            </div>
          </div>
          
          <div class="overflow-x-auto rounded-lg border border-gray-200">
            <table class="w-full text-sm text-left">
              <thead class="bg-gray-100 text-paper-text text-xs uppercase font-semibold border-b border-gray-200 select-none">
                <tr>
                  <th @click="sortByUorg('id')" class="px-4 py-3 w-16 cursor-pointer hover:bg-gray-200/80 transition-colors" title="Ordenar por ID">
                    <div class="flex items-center gap-1">
                      <span>ID</span>
                      <span class="text-xs text-gray-500 font-mono">{{ getSortIconUorg('id') }}</span>
                    </div>
                  </th>
                  <th @click="sortByUorg('codigo_sigla')" class="px-4 py-3 w-32 cursor-pointer hover:bg-gray-200/80 transition-colors" title="Ordenar por Código / Sigla">
                    <div class="flex items-center gap-1">
                      <span>Código / Sigla</span>
                      <span class="text-xs text-gray-500 font-mono">{{ getSortIconUorg('codigo_sigla') }}</span>
                    </div>
                  </th>
                  <th @click="sortByUorg('nome')" class="px-4 py-3 cursor-pointer hover:bg-gray-200/80 transition-colors" title="Ordenar por Nome da UORG">
                    <div class="flex items-center gap-1">
                      <span>Nome da UORG</span>
                      <span class="text-xs text-gray-500 font-mono">{{ getSortIconUorg('nome') }}</span>
                    </div>
                  </th>
                  <th @click="sortByUorg('uorg_pai')" class="px-4 py-3 cursor-pointer hover:bg-gray-200/80 transition-colors" title="Ordenar por UORG Pai">
                    <div class="flex items-center gap-1">
                      <span>UORG Pai (Hierarquia Superior)</span>
                      <span class="text-xs text-gray-500 font-mono">{{ getSortIconUorg('uorg_pai') }}</span>
                    </div>
                  </th>
                  <th @click="sortByUorg('login')" class="px-4 py-3 w-32 cursor-pointer hover:bg-gray-200/80 transition-colors" title="Ordenar por Usuário">
                    <div class="flex items-center gap-1">
                      <span>Usuário</span>
                      <span class="text-xs text-gray-500 font-mono">{{ getSortIconUorg('login') }}</span>
                    </div>
                  </th>
                  <th @click="sortByUorg('data_alteracao')" class="px-4 py-3 w-32 cursor-pointer hover:bg-gray-200/80 transition-colors" title="Ordenar por Data de Alteração">
                    <div class="flex items-center gap-1">
                      <span>Data Alt.</span>
                      <span class="text-xs text-gray-500 font-mono">{{ getSortIconUorg('data_alteracao') }}</span>
                    </div>
                  </th>
                  <th class="px-4 py-3 w-24 text-center">Ações</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr v-if="loading" class="animate-pulse">
                  <td colspan="7" class="px-4 py-8 text-center text-gray-500">Carregando...</td>
                </tr>
                <tr v-else-if="filteredUorgs.length === 0">
                  <td colspan="7" class="px-4 py-8 text-center text-gray-500">Nenhuma UORG encontrada.</td>
                </tr>
                <tr v-else v-for="item in filteredUorgs" :key="item.id" class="hover:bg-gray-50 transition-colors">
                  <td class="px-4 py-3 text-gray-500 font-mono text-xs">#{{ item.id }}</td>
                  <td class="px-4 py-3 text-xs">
                    <div class="flex items-center gap-1.5 flex-wrap">
                      <span v-if="item.codigo" class="px-1.5 py-0.5 rounded bg-gray-100 text-gray-700 font-mono font-medium">{{ item.codigo }}</span>
                      <span v-if="item.sigla" class="px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 font-semibold">{{ item.sigla }}</span>
                      <span v-if="!item.codigo && !item.sigla" class="text-gray-400 italic">-</span>
                    </div>
                  </td>
                  <td class="px-4 py-3 font-medium text-gray-800">
                    <div class="flex items-center gap-1.5 flex-wrap">
                      <span>{{ item.nome }}</span>
                      <span v-if="item.sigla" class="text-xs px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 font-semibold border border-blue-100">
                        {{ item.sigla }}
                      </span>
                    </div>
                    <div v-if="item.subordinadas?.length" class="text-[11px] text-gray-400 mt-0.5">
                      {{ item.subordinadas.length }} UORG(s) subordinada(s)
                    </div>
                  </td>
                  <td class="px-4 py-3 text-sm">
                    <span v-if="item.uorg_pai" class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-50 text-purple-700 border border-purple-200">
                      <span>{{ item.uorg_pai.nome }}</span>
                      <span v-if="item.uorg_pai.sigla" class="text-[10px] font-bold text-purple-800">({{ item.uorg_pai.sigla }})</span>
                    </span>
                    <span v-else class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                      Nível Raiz
                    </span>
                  </td>
                  <td class="px-4 py-3 text-gray-500 text-xs truncate max-w-[120px]" :title="item.login">{{ item.login || '-' }}</td>
                  <td class="px-4 py-3 text-gray-500 text-xs whitespace-nowrap">{{ formatDate(item.data_alteracao) }}</td>
                  <td class="px-4 py-3 text-center space-x-1">
                    <button @click="openModal('uorg', item)" class="text-paper-primary hover:text-paper-primary-hover p-1.5 rounded-full hover:bg-paper-primary/10 transition-colors inline-flex" title="Editar">
                      <PencilSquareIcon class="h-5 w-5" />
                    </button>
                    <button @click="deleteItem('uorg', item.id)" class="text-paper-danger hover:text-paper-danger-hover p-1.5 rounded-full hover:bg-paper-danger/10 transition-colors inline-flex" title="Excluir">
                      <TrashIcon class="h-5 w-5" />
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- TAB 2: Postos de Serviço -->
        <div v-if="currentTab === 'postos'" class="space-y-4">
          <div class="flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-3">
            <div class="relative flex-1 max-w-md">
              <MagnifyingGlassIcon class="h-5 w-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input 
                v-model="searchPosto" 
                type="text" 
                placeholder="Buscar por nome do posto ou UORG vinculada..." 
                class="w-full pl-10 pr-9 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-paper-primary/20 focus:border-paper-primary"
              />
              <button 
                v-if="searchPosto" 
                @click="searchPosto = ''" 
                class="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 p-1 rounded-full"
                title="Limpar busca"
              >
                <XMarkIcon class="h-4 w-4" />
              </button>
            </div>
            <div class="flex items-center gap-2">
              <button @click="openModal('posto')" class="inline-flex items-center justify-center gap-2 bg-paper-primary hover:bg-paper-primary-hover text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors shadow-sm focus:outline-none focus:ring-2 focus:ring-paper-primary focus:ring-offset-2">
                <PlusIcon class="h-5 w-5" />
                Novo Posto de Serviço
              </button>
            </div>
          </div>

          <div class="overflow-x-auto rounded-lg border border-gray-200">
            <table class="w-full text-sm text-left">
              <thead class="bg-gray-100 text-paper-text text-xs uppercase font-semibold border-b border-gray-200 select-none">
                <tr>
                  <th @click="sortByPosto('id')" class="px-4 py-3 w-16 cursor-pointer hover:bg-gray-200/80 transition-colors" title="Ordenar por ID">
                    <div class="flex items-center gap-1">
                      <span>ID</span>
                      <span class="text-xs text-gray-500 font-mono">{{ getSortIconPosto('id') }}</span>
                    </div>
                  </th>
                  <th @click="sortByPosto('nome')" class="px-4 py-3 cursor-pointer hover:bg-gray-200/80 transition-colors" title="Ordenar por Nome do Posto">
                    <div class="flex items-center gap-1">
                      <span>Nome do Posto</span>
                      <span class="text-xs text-gray-500 font-mono">{{ getSortIconPosto('nome') }}</span>
                    </div>
                  </th>
                  <th @click="sortByPosto('uorg')" class="px-4 py-3 cursor-pointer hover:bg-gray-200/80 transition-colors" title="Ordenar por UORG Vinculada">
                    <div class="flex items-center gap-1">
                      <span>UORG Vinculada (UORG Pai)</span>
                      <span class="text-xs text-gray-500 font-mono">{{ getSortIconPosto('uorg') }}</span>
                    </div>
                  </th>
                  <th @click="sortByPosto('login')" class="px-4 py-3 w-32 cursor-pointer hover:bg-gray-200/80 transition-colors" title="Ordenar por Usuário">
                    <div class="flex items-center gap-1">
                      <span>Usuário</span>
                      <span class="text-xs text-gray-500 font-mono">{{ getSortIconPosto('login') }}</span>
                    </div>
                  </th>
                  <th @click="sortByPosto('data_alteracao')" class="px-4 py-3 w-32 cursor-pointer hover:bg-gray-200/80 transition-colors" title="Ordenar por Data de Alteração">
                    <div class="flex items-center gap-1">
                      <span>Data Alt.</span>
                      <span class="text-xs text-gray-500 font-mono">{{ getSortIconPosto('data_alteracao') }}</span>
                    </div>
                  </th>
                  <th class="px-4 py-3 w-24 text-center">Ações</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr v-if="loading" class="animate-pulse">
                  <td colspan="6" class="px-4 py-8 text-center text-gray-500">Carregando...</td>
                </tr>
                <tr v-else-if="filteredPostos.length === 0">
                  <td colspan="6" class="px-4 py-8 text-center text-gray-500">Nenhum posto de serviço encontrado.</td>
                </tr>
                <tr v-else v-for="item in filteredPostos" :key="item.id" class="hover:bg-gray-50 transition-colors">
                  <td class="px-4 py-3 text-gray-500 font-mono text-xs">#{{ item.id }}</td>
                  <td class="px-4 py-3 font-medium text-gray-800">{{ item.nome }}</td>
                  <td class="px-4 py-3">
                    <div class="flex flex-col gap-0.5">
                      <span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200 w-fit">
                        <span>{{ item.uorg?.nome || 'Não vinculada' }}</span>
                        <span v-if="item.uorg?.sigla" class="text-[10px] font-bold text-blue-800">({{ item.uorg.sigla }})</span>
                      </span>
                      <span v-if="item.uorg?.uorg_pai?.nome" class="text-[11px] text-gray-500 pl-1">
                        ↳ Subordinada a: <span class="font-medium text-gray-700">{{ item.uorg.uorg_pai.nome }} {{ item.uorg.uorg_pai.sigla ? `(${item.uorg.uorg_pai.sigla})` : '' }}</span>
                      </span>
                    </div>
                  </td>
                  <td class="px-4 py-3 text-gray-500 text-xs truncate max-w-[120px]" :title="item.login">{{ item.login || '-' }}</td>
                  <td class="px-4 py-3 text-gray-500 text-xs whitespace-nowrap">{{ formatDate(item.data_alteracao) }}</td>
                  <td class="px-4 py-3 text-center space-x-1">
                    <button @click="openModal('posto', item)" class="text-paper-primary hover:text-paper-primary-hover p-1.5 rounded-full hover:bg-paper-primary/10 transition-colors inline-flex" title="Editar">
                      <PencilSquareIcon class="h-5 w-5" />
                    </button>
                    <button @click="deleteItem('posto', item.id)" class="text-paper-danger hover:text-paper-danger-hover p-1.5 rounded-full hover:bg-paper-danger/10 transition-colors inline-flex" title="Excluir">
                      <TrashIcon class="h-5 w-5" />
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Form -->
    <div v-if="isModalOpen" class="fixed inset-0 bg-gray-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-xl shadow-paper-lg w-full max-w-lg overflow-hidden flex flex-col" @click.stop>
        <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
          <h3 class="text-lg font-semibold text-gray-800">
            {{ isEditing ? 'Editar' : 'Nova' }} {{ modalType === 'uorg' ? 'Unidade Organizacional (UORG)' : 'Posto de Serviço' }}
          </h3>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-600 transition-colors p-1 rounded-full hover:bg-gray-100">
            <XMarkIcon class="h-5 w-5" />
          </button>
        </div>

        <form @submit.prevent="saveItem" class="p-6 space-y-4">
          <!-- Form UORG -->
          <template v-if="modalType === 'uorg'">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Nome da UORG *</label>
              <input 
                v-model="formData.nome" 
                type="text" 
                required 
                placeholder="Ex: UNIDADE DE TERAPIA INTENSIVA ADULTO"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-paper-primary focus:border-transparent text-sm"
              />
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Código (Opcional)</label>
                <input 
                  v-model="formData.codigo" 
                  type="text" 
                  placeholder="Ex: 10.01 ou UORG-01"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-paper-primary focus:border-transparent text-sm"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Sigla (Opcional)</label>
                <input 
                  v-model="formData.sigla" 
                  type="text" 
                  placeholder="Ex: UTI, GAS, DIVGP"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-paper-primary focus:border-transparent text-sm uppercase"
                />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">UORG Pai (Hierarquia Superior)</label>
              <select 
                v-model="formData.uorg_pai_id" 
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-paper-primary focus:border-transparent text-sm"
              >
                <option :value="null">Nenhuma (UORG de Nível Raiz / Superior)</option>
                <option 
                  v-for="u in availableParentUorgs" 
                  :key="u.id" 
                  :value="u.id"
                >
                  {{ u.nome }} {{ u.sigla ? `(${u.sigla})` : '' }}
                </option>
              </select>
              <p class="text-xs text-gray-500 mt-1">Selecione o setor, gerência ou divisão ao qual esta UORG se subordina.</p>
            </div>
          </template>

          <!-- Form Posto de Serviço -->
          <template v-if="modalType === 'posto'">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Nome do Posto *</label>
              <input 
                v-model="formData.nome" 
                type="text" 
                required 
                placeholder="Ex: POSTO 1 - ENFERMARIA"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-paper-primary focus:border-transparent text-sm"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Unidade / UORG Subordinada *</label>
              <select 
                v-model="formData.uorg_id" 
                required 
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-paper-primary focus:border-transparent text-sm"
              >
                <option value="" disabled>Selecione a Unidade (UORG) à qual o posto está subordinado</option>
                <option v-for="uorg in sortedUorgs" :key="uorg.id" :value="uorg.id">
                  {{ uorg.nome }} {{ uorg.sigla ? `(${uorg.sigla})` : '' }} {{ uorg.uorg_pai ? `— Subordinada a: ${uorg.uorg_pai.nome}` : '' }}
                </option>
              </select>
              <p class="text-xs text-gray-500 mt-1">Ao gravar o posto de serviço, ele será vinculado a esta Unidade Organizacional e à sua hierarquia.</p>
            </div>
          </template>

          <div v-if="errorMsg" class="p-3 bg-paper-danger/10 border border-paper-danger/20 rounded-lg text-sm text-paper-danger flex items-start gap-2">
            <ExclamationCircleIcon class="h-5 w-5 shrink-0" />
            <span>{{ errorMsg }}</span>
          </div>

          <div class="flex justify-end gap-3 pt-4 border-t border-gray-100">
            <button 
              type="button" 
              @click="closeModal" 
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-paper-primary"
            >
              Cancelar
            </button>
            <button 
              type="submit" 
              :disabled="saving" 
              class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-paper-primary hover:bg-paper-primary-hover rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-paper-primary disabled:opacity-50"
            >
              <ArrowPathIcon v-if="saving" class="h-4 w-4 animate-spin" />
              {{ isEditing ? 'Salvar Alterações' : 'Cadastrar' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { 
  PlusIcon, PencilSquareIcon, TrashIcon, XMarkIcon, 
  ExclamationCircleIcon, ArrowPathIcon, BuildingOfficeIcon,
  MapPinIcon, MagnifyingGlassIcon
} from '@heroicons/vue/24/outline';
import api from '../services/api';
import { useSearchFilterState } from '../composables/useSearchFilterState';

const tabs = [
  { id: 'uorgs', name: 'Unidades Organizacionais (UORGs)', icon: BuildingOfficeIcon },
  { id: 'postos', name: 'Postos de Serviço', icon: MapPinIcon }
];

const currentTab = ref('uorgs');

const uorgs = ref<any[]>([]);
const postos = ref<any[]>([]);
const loading = ref(false);
const saving = ref(false);
const errorMsg = ref('');

const searchUorg = ref('');
const searchPosto = ref('');

type SortableUorgColumn = 'id' | 'codigo_sigla' | 'nome' | 'uorg_pai' | 'login' | 'data_alteracao';
const sortColumnUorg = ref<SortableUorgColumn>('nome');
const sortDirectionUorg = ref<'asc' | 'desc'>('asc');

type SortablePostoColumn = 'id' | 'nome' | 'uorg' | 'login' | 'data_alteracao';
const sortColumnPosto = ref<SortablePostoColumn>('nome');
const sortDirectionPosto = ref<'asc' | 'desc'>('asc');

// Persistência automática do status da última pesquisa, aba e ordenação
useSearchFilterState('organizacao', {
  currentTab,
  searchUorg,
  searchPosto,
  sortColumnUorg,
  sortDirectionUorg,
  sortColumnPosto,
  sortDirectionPosto
});

const isModalOpen = ref(false);
const isEditing = ref(false);
const modalType = ref<'uorg' | 'posto'>('uorg');

const formData = reactive({
  id: null as number | null,
  nome: '',
  codigo: '',
  sigla: '',
  uorg_pai_id: null as number | null,
  uorg_id: '' as number | string
});

const filteredUorgs = computed(() => {
  let list = Array.isArray(uorgs.value) ? uorgs.value : [];
  if (searchUorg.value) {
    const q = String(searchUorg.value).toLowerCase();
    list = list.filter(u => 
      String(u.nome || '').toLowerCase().includes(q) ||
      String(u.codigo || '').toLowerCase().includes(q) ||
      String(u.sigla || '').toLowerCase().includes(q) ||
      String(u.uorg_pai?.nome || '').toLowerCase().includes(q) ||
      String(u.uorg_pai?.sigla || '').toLowerCase().includes(q)
    );
  }

  const sorted = [...list];
  sorted.sort((a, b) => {
    if (sortColumnUorg.value === 'id') {
      const numA = Number(a.id) || 0;
      const numB = Number(b.id) || 0;
      return sortDirectionUorg.value === 'asc' ? numA - numB : numB - numA;
    }

    let valA = '';
    let valB = '';

    if (sortColumnUorg.value === 'codigo_sigla') {
      valA = `${a.codigo || ''} ${a.sigla || ''}`.trim();
      valB = `${b.codigo || ''} ${b.sigla || ''}`.trim();
    } else if (sortColumnUorg.value === 'nome') {
      valA = `${a.nome || ''} ${a.sigla || ''}`.trim();
      valB = `${b.nome || ''} ${b.sigla || ''}`.trim();
    } else if (sortColumnUorg.value === 'uorg_pai') {
      valA = `${a.uorg_pai?.nome || ''} ${a.uorg_pai?.sigla || ''}`.trim();
      valB = `${b.uorg_pai?.nome || ''} ${b.uorg_pai?.sigla || ''}`.trim();
    } else if (sortColumnUorg.value === 'login') {
      valA = String(a.login || '');
      valB = String(b.login || '');
    } else if (sortColumnUorg.value === 'data_alteracao') {
      valA = String(a.data_alteracao || '');
      valB = String(b.data_alteracao || '');
    } else {
      valA = String(a.nome || '');
      valB = String(b.nome || '');
    }

    const comparison = valA.localeCompare(valB, 'pt-BR', { numeric: true, sensitivity: 'base' });
    return sortDirectionUorg.value === 'asc' ? comparison : -comparison;
  });

  return sorted;
});

const sortByUorg = (column: SortableUorgColumn) => {
  if (sortColumnUorg.value === column) {
    sortDirectionUorg.value = sortDirectionUorg.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortColumnUorg.value = column;
    sortDirectionUorg.value = 'asc';
  }
};

const getSortIconUorg = (column: SortableUorgColumn) => {
  if (sortColumnUorg.value !== column) return '↕';
  return sortDirectionUorg.value === 'asc' ? '▲' : '▼';
};

const filteredPostos = computed(() => {
  let list = Array.isArray(postos.value) ? postos.value : [];
  if (searchPosto.value) {
    const q = String(searchPosto.value).toLowerCase();
    list = list.filter(p => 
      String(p.nome || '').toLowerCase().includes(q) ||
      String(p.uorg?.nome || '').toLowerCase().includes(q) ||
      String(p.uorg?.sigla || '').toLowerCase().includes(q) ||
      String(p.uorg?.uorg_pai?.nome || '').toLowerCase().includes(q) ||
      String(p.uorg?.uorg_pai?.sigla || '').toLowerCase().includes(q)
    );
  }

  const sorted = [...list];
  sorted.sort((a, b) => {
    if (sortColumnPosto.value === 'id') {
      const numA = Number(a.id) || 0;
      const numB = Number(b.id) || 0;
      return sortDirectionPosto.value === 'asc' ? numA - numB : numB - numA;
    }

    let valA = '';
    let valB = '';

    if (sortColumnPosto.value === 'nome') {
      valA = String(a.nome || '');
      valB = String(b.nome || '');
    } else if (sortColumnPosto.value === 'uorg') {
      valA = String(a.uorg?.nome || '');
      valB = String(b.uorg?.nome || '');
    } else if (sortColumnPosto.value === 'login') {
      valA = String(a.login || '');
      valB = String(b.login || '');
    } else if (sortColumnPosto.value === 'data_alteracao') {
      valA = String(a.data_alteracao || '');
      valB = String(b.data_alteracao || '');
    } else {
      valA = String(a.nome || '');
      valB = String(b.nome || '');
    }

    const comparison = valA.localeCompare(valB, 'pt-BR', { numeric: true, sensitivity: 'base' });
    return sortDirectionPosto.value === 'asc' ? comparison : -comparison;
  });

  return sorted;
});

const sortByPosto = (column: SortablePostoColumn) => {
  if (sortColumnPosto.value === column) {
    sortDirectionPosto.value = sortDirectionPosto.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortColumnPosto.value = column;
    sortDirectionPosto.value = 'asc';
  }
};

const getSortIconPosto = (column: SortablePostoColumn) => {
  if (sortColumnPosto.value !== column) return '↕';
  return sortDirectionPosto.value === 'asc' ? '▲' : '▼';
};

const sortedUorgs = computed(() => {
  const list = Array.isArray(uorgs.value) ? uorgs.value : [];
  return [...list].sort((a, b) => (a.nome || '').localeCompare(b.nome || '', 'pt-BR', { sensitivity: 'base' }));
});

const availableParentUorgs = computed(() => {
  const list = sortedUorgs.value;
  if (!isEditing.value || !formData.id) return list;
  return list.filter(u => u.id !== formData.id);
});

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-';
  try {
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return String(dateStr);
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return String(dateStr);
  }
};

const fetchData = async () => {
  loading.value = true;
  try {
    const [resUorgs, resPostos] = await Promise.allSettled([
      api.get('/api/uorgs'),
      api.get('/api/postos')
    ]);

    if (resUorgs.status === 'fulfilled') {
      uorgs.value = Array.isArray(resUorgs.value.data) ? resUorgs.value.data : [];
    } else {
      console.error('Erro ao carregar UORGs:', resUorgs.reason);
      uorgs.value = [];
    }

    if (resPostos.status === 'fulfilled') {
      postos.value = Array.isArray(resPostos.value.data) ? resPostos.value.data : [];
    } else {
      console.error('Erro ao carregar Postos:', resPostos.reason);
      postos.value = [];
    }
  } catch (err: any) {
    console.error('Erro geral ao carregar dados:', err);
  } finally {
    loading.value = false;
  }
};

const openModal = (type: 'uorg' | 'posto', item: any = null) => {
  modalType.value = type;
  isEditing.value = !!item;
  errorMsg.value = '';
  
  if (item) {
    formData.id = item.id;
    formData.nome = item.nome;
    formData.codigo = item.codigo || '';
    formData.sigla = item.sigla || '';
    formData.uorg_pai_id = item.uorg_pai_id || null;
    formData.uorg_id = item.uorg_id || '';
  } else {
    formData.id = null;
    formData.nome = '';
    formData.codigo = '';
    formData.sigla = '';
    formData.uorg_pai_id = null;
    formData.uorg_id = '';
  }
  
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
};

const saveItem = async () => {
  errorMsg.value = '';
  
  const trimmedNome = formData.nome ? formData.nome.trim() : '';
  if (!trimmedNome) {
    errorMsg.value = modalType.value === 'uorg' 
      ? 'O nome da Unidade Organizacional (UORG) é obrigatório e não pode ser em branco.' 
      : 'O nome do Posto de Serviço é obrigatório e não pode ser em branco.';
    return;
  }

  // Validação preventiva no frontend de nomes duplicados
  if (modalType.value === 'uorg') {
    const duplicate = uorgs.value.find(u => 
      u.nome.trim().toUpperCase() === trimmedNome.toUpperCase() && 
      (!isEditing.value || u.id !== formData.id)
    );
    if (duplicate) {
      errorMsg.value = 'Já existe uma Unidade Organizacional cadastrada com este nome.';
      return;
    }
  } else {
    const targetUorgId = Number(formData.uorg_id);
    if (!targetUorgId) {
      errorMsg.value = 'A Unidade Organizacional vinculada (UORG Pai) é obrigatória.';
      return;
    }

    const duplicate = postos.value.find(p => 
      p.nome.trim().toUpperCase() === trimmedNome.toUpperCase() && 
      (p.uorg_id === targetUorgId || p.unidade_id === targetUorgId) &&
      (!isEditing.value || p.id !== formData.id)
    );
    if (duplicate) {
      errorMsg.value = 'Já existe um Posto de Serviço com este nome nesta mesma Unidade Organizacional.';
      return;
    }
  }

  saving.value = true;
  
  try {
    let payload: any = {};
    let endpoint = '';
    
    if (modalType.value === 'uorg') {
      endpoint = '/api/uorgs';
      payload = {
        nome: trimmedNome.toUpperCase(),
        codigo: formData.codigo?.trim() || null,
        sigla: formData.sigla?.trim().toUpperCase() || null,
        uorg_pai_id: formData.uorg_pai_id ? Number(formData.uorg_pai_id) : null
      };
    } else {
      endpoint = '/api/postos';
      const selectedUorgId = Number(formData.uorg_id);
      payload = {
        nome: trimmedNome.toUpperCase(),
        uorg_id: selectedUorgId,
        unidade_id: selectedUorgId
      };
    }
    
    if (isEditing.value) {
      await api.put(`${endpoint}/${formData.id}`, payload);
    } else {
      await api.post(endpoint, payload);
    }
    
    await fetchData();
    closeModal();
  } catch (err: any) {
    const detail = err.response?.data?.detail;
    if (typeof detail === 'string') {
      errorMsg.value = detail;
    } else if (Array.isArray(detail)) {
      errorMsg.value = detail.map((d: any) => d.msg || JSON.stringify(d)).join('; ');
    } else if (err.response?.data?.message) {
      errorMsg.value = err.response.data.message;
    } else {
      errorMsg.value = err.message || 'Erro ao salvar o registro.';
    }
  } finally {
    saving.value = false;
  }
};

const deleteItem = async (type: 'uorg' | 'posto', id: number) => {
  const typeName = type === 'uorg' ? 'esta Unidade Organizacional (UORG)' : 'este Posto de Serviço';
  if (!confirm(`Tem certeza que deseja excluir ${typeName}?`)) return;
  
  try {
    const endpoint = type === 'uorg' ? `/api/uorgs/${id}` : `/api/postos/${id}`;
    await api.delete(endpoint);
    await fetchData();
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Erro ao excluir o registro.');
  }
};


onMounted(() => {
  fetchData();
});
</script>
