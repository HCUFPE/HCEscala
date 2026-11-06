<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">Funcionários</h1>
        <p class="text-sm text-gray-500 mt-1">Gerenciamento de colaboradores, vínculos, escalas, lotações e férias</p>
      </div>
      <div class="flex items-center gap-2">
        <button 
          @click="openModal()" 
          class="inline-flex items-center justify-center gap-2 bg-paper-primary hover:bg-paper-primary-hover text-white px-4 py-2.5 rounded-lg text-sm font-medium transition-colors shadow-sm focus:outline-none focus:ring-2 focus:ring-paper-primary focus:ring-offset-2 shrink-0 cursor-pointer"
        >
          <PlusIcon class="h-5 w-5" />
          <span>Novo Funcionário</span>
        </button>
      </div>
    </div>

    <!-- Feedback Banners -->
    <div v-if="successBanner" class="p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-sm text-emerald-800 flex items-center justify-between shadow-sm animate-fade-in">
      <div class="flex items-center gap-2">
        <CheckCircleIcon class="h-5 w-5 text-emerald-600 shrink-0" />
        <span class="font-medium">{{ successBanner }}</span>
      </div>
      <button @click="successBanner = ''" class="text-emerald-500 hover:text-emerald-700 text-lg leading-none cursor-pointer">&times;</button>
    </div>

    <div v-if="errorBanner" class="p-4 bg-paper-danger/10 border border-paper-danger/20 rounded-xl text-sm text-paper-danger flex items-center justify-between shadow-sm animate-fade-in">
      <div class="flex items-center gap-2">
        <ExclamationCircleIcon class="h-5 w-5 shrink-0" />
        <span class="font-medium">{{ errorBanner }}</span>
      </div>
      <div class="flex items-center gap-2">
        <button @click="fetchData" class="px-3 py-1 bg-paper-danger text-white rounded text-xs font-semibold hover:bg-red-700 transition-colors cursor-pointer">
          Recarregar
        </button>
        <button @click="errorBanner = ''" class="text-paper-danger hover:text-red-800 text-lg leading-none cursor-pointer">&times;</button>
      </div>
    </div>

    <!-- Search and Filters Box -->
    <div class="bg-white p-4 sm:p-5 rounded-xl shadow-paper border border-gray-100 space-y-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 items-end">
        <!-- Text Search -->
        <div class="relative">
          <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Buscar Colaborador</label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon class="h-4 w-4 text-gray-400" />
            </div>
            <input
              v-model="searchQuery"
              type="text"
              class="block w-full pl-9 pr-8 py-2 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-paper-primary focus:border-paper-primary text-xs sm:text-sm font-medium"
              placeholder="Nome, SIAPE, Cargo ou Lotação..."
            />
            <button 
              v-if="searchQuery" 
              @click="searchQuery = ''" 
              class="absolute inset-y-0 right-0 pr-2.5 flex items-center text-gray-400 hover:text-gray-600 cursor-pointer"
            >
              &times;
            </button>
          </div>
        </div>

        <!-- Filter UORG -->
        <div>
          <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Lotação (UORG)</label>
          <select
            v-model="selectedLotacaoUorg"
            @change="onFilterUorgChange"
            class="block w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-1 focus:ring-paper-primary focus:border-paper-primary text-xs sm:text-sm font-medium"
          >
            <option value="TODOS">Todas as Lotações</option>
            <option value="SEM_LOTACAO">⚠️ Sem Lotação Cadastrada</option>
            <option v-for="u in sortedUnidades" :key="u.id" :value="u.id">
              {{ u.nome }} {{ u.sigla ? `(${u.sigla})` : '' }}
            </option>
          </select>
        </div>

        <!-- Filter Posto -->
        <div>
          <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Posto de Serviço</label>
          <select
            v-model="selectedPosto"
            @change="onFilterPostoChange"
            class="block w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-1 focus:ring-paper-primary focus:border-paper-primary text-xs sm:text-sm font-medium"
          >
            <option value="TODOS">Todos os Postos</option>
            <option v-for="p in postosFiltradosPorUorg" :key="p.id" :value="p.id">
              {{ p.nome }}
            </option>
          </select>
        </div>

        <!-- Filter Cargo -->
        <div>
          <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Cargo / Categoria</label>
          <select
            v-model="selectedCargo"
            class="block w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-1 focus:ring-paper-primary focus:border-paper-primary text-xs sm:text-sm font-medium"
          >
            <option value="TODOS">Todos os Cargos</option>
            <option v-for="c in filteredCargos" :key="c.id" :value="c.id">
              {{ c.nome }}
            </option>
          </select>
        </div>
      </div>

      <!-- Filter Stats & Clear Button (Igual à tela de Grades) -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-gray-500 pt-3 border-t border-gray-100">
        <div>
          Exibindo <b class="text-gray-900">{{ filteredFuncionarios.length }}</b> de <b class="text-gray-900">{{ funcionarios.length }}</b> funcionários
        </div>
        <button 
          v-if="hasActiveFilters" 
          @click="clearFilters" 
          type="button"
          class="bg-white border border-gray-300 text-paper-text px-4 py-2 rounded-lg text-sm hover:bg-gray-50 transition-colors shadow-xs cursor-pointer font-medium"
        >
          Limpar Filtros
        </button>
      </div>
    </div>

    <!-- Data Table -->
    <div class="bg-white rounded-xl shadow-paper overflow-hidden border border-gray-100">
      <div class="overflow-x-auto">
        <table class="w-full text-sm text-left">
          <thead class="bg-gray-100 text-paper-text text-xs uppercase font-semibold border-b border-gray-200 select-none">
            <tr>
              <th @click="sortBy('matricula')" class="px-4 py-3 cursor-pointer hover:bg-gray-200/80 transition-colors" title="Ordenar por Matrícula">
                <div class="flex items-center gap-1">
                  <span>Matrícula</span>
                  <span class="text-xs text-gray-500 font-mono">{{ getSortIcon('matricula') }}</span>
                </div>
              </th>
              <th @click="sortBy('nome')" class="px-4 py-3 cursor-pointer hover:bg-gray-200/80 transition-colors" title="Ordenar por Nome">
                <div class="flex items-center gap-1">
                  <span>Nome</span>
                  <span class="text-xs text-gray-500 font-mono">{{ getSortIcon('nome') }}</span>
                </div>
              </th>
              <th @click="sortBy('cargo')" class="px-4 py-3 cursor-pointer hover:bg-gray-200/80 transition-colors" title="Ordenar por Cargo">
                <div class="flex items-center gap-1">
                  <span>Cargo</span>
                  <span class="text-xs text-gray-500 font-mono">{{ getSortIcon('cargo') }}</span>
                </div>
              </th>
              <th @click="sortBy('carga_horaria')" class="px-4 py-3 text-center cursor-pointer hover:bg-gray-200/80 transition-colors" title="Ordenar por Carga Horária">
                <div class="flex items-center justify-center gap-1">
                  <span>Carga Horária</span>
                  <span class="text-xs text-gray-500 font-mono">{{ getSortIcon('carga_horaria') }}</span>
                </div>
              </th>
              <th @click="sortBy('vinculo')" class="px-4 py-3 cursor-pointer hover:bg-gray-200/80 transition-colors" title="Ordenar por Vínculo">
                <div class="flex items-center gap-1">
                  <span>Vínculo</span>
                  <span class="text-xs text-gray-500 font-mono">{{ getSortIcon('vinculo') }}</span>
                </div>
              </th>
              <th @click="sortBy('escala')" class="px-4 py-3 cursor-pointer hover:bg-gray-200/80 transition-colors" title="Ordenar por Escala">
                <div class="flex items-center gap-1">
                  <span>Escala</span>
                  <span class="text-xs text-gray-500 font-mono">{{ getSortIcon('escala') }}</span>
                </div>
              </th>
              <th @click="sortBy('lotacao')" class="px-4 py-3 cursor-pointer hover:bg-gray-200/80 transition-colors" title="Ordenar por Lotação">
                <div class="flex items-center gap-1">
                  <span>Lotação Atual</span>
                  <span class="text-xs text-gray-500 font-mono">{{ getSortIcon('lotacao') }}</span>
                </div>
              </th>
              <th class="px-4 py-3 text-center w-28">Ações</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-if="loading" class="animate-pulse">
              <td colspan="8" class="px-4 py-10 text-center text-gray-500">
                <div class="inline-flex items-center gap-2">
                  <ArrowPathIcon class="h-5 w-5 animate-spin text-paper-primary" />
                  <span>Carregando funcionários...</span>
                </div>
              </td>
            </tr>
            <tr v-else-if="filteredFuncionarios.length === 0">
              <td colspan="8" class="px-4 py-10 text-center text-gray-500">
                Nenhum funcionário encontrado com os filtros selecionados.
              </td>
            </tr>
            <tr v-else v-for="item in filteredFuncionarios" :key="item.id" class="hover:bg-gray-50/80 transition-colors">
              <td class="px-4 py-3 font-mono font-medium text-gray-800 text-xs sm:text-sm">{{ item.matricula }}</td>
              <td class="px-4 py-3 font-medium text-gray-900">{{ item.nome }}</td>
              <td class="px-4 py-3 text-paper-text font-medium">
                {{ item.cargo?.nome || '-' }}
              </td>
              <td class="px-4 py-3 text-center font-bold text-gray-700">
                <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-gray-100 text-gray-800">
                  {{ item.carga_horaria || 40 }}h
                </span>
              </td>
              <td class="px-4 py-3 text-paper-text text-xs">
                <span v-if="item.vinculo?.nome" class="px-2 py-0.5 rounded-full font-medium bg-purple-50 text-purple-700 border border-purple-200">
                  {{ item.vinculo.nome }}
                </span>
                <span v-else class="text-gray-400 italic text-xs">-</span>
              </td>
              <td class="px-4 py-3 text-paper-text text-xs">
                <span v-if="item.escala?.sigla" class="font-mono bg-gray-100 px-2 py-0.5 rounded text-gray-700 font-semibold">
                  {{ item.escala.sigla }}
                </span>
                <span v-else class="text-gray-400 italic">-</span>
              </td>
              <td class="px-4 py-3 text-gray-700">
                <div v-if="getActiveLotacoes(item).length > 0" class="flex flex-col gap-1 items-start">
                  <span 
                    v-for="(lotText, idx) in getActiveLotacoes(item)" 
                    :key="idx"
                    class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-800 border border-blue-200"
                  >
                    {{ lotText }}
                  </span>
                </div>
                <span v-else class="text-gray-400 text-xs italic">Sem lotação</span>
              </td>
              <td class="px-4 py-3 text-center space-x-1 whitespace-nowrap">
                <button 
                  @click="openModal(item)" 
                  class="text-paper-primary hover:text-paper-primary-hover p-1.5 rounded-full hover:bg-paper-primary/10 transition-colors inline-flex cursor-pointer" 
                  title="Editar funcionário, lotações ou férias"
                >
                  <PencilSquareIcon class="h-5 w-5" />
                </button>
                <button 
                  @click="deleteFuncionario(item.id)" 
                  class="text-paper-danger hover:text-paper-danger-hover p-1.5 rounded-full hover:bg-paper-danger/10 transition-colors inline-flex cursor-pointer" 
                  title="Excluir funcionário"
                >
                  <TrashIcon class="h-5 w-5" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal Funcionario -->
    <div v-if="isModalOpen" class="fixed inset-0 bg-gray-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in" @click.self="closeModal">
      <div class="bg-white rounded-xl shadow-paper-lg w-full max-w-3xl max-h-[92vh] overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/70 shrink-0">
          <div>
            <h3 class="text-lg font-semibold text-gray-800">
              {{ isEditing ? `Editar: ${form.nome || 'Funcionário'}` : 'Novo Funcionário' }}
            </h3>
            <p class="text-xs text-gray-500 mt-0.5">
              {{ isEditing ? 'Atualize os dados cadastrais, lotações e períodos de férias' : 'Preencha os dados cadastrais iniciais' }}
            </p>
          </div>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-600 transition-colors p-1.5 rounded-lg hover:bg-gray-200/60 cursor-pointer">
            <XMarkIcon class="h-5 w-5" />
          </button>
        </div>

        <!-- Modal Tabs -->
        <div class="border-b border-gray-200 px-6 pt-3 bg-white shrink-0">
          <nav class="-mb-px flex space-x-6">
            <button
              v-for="tab in modalTabs"
              :key="tab.id"
              @click="switchTab(tab.id)"
              :disabled="!isEditing && tab.id !== 'geral'"
              :class="[
                currentModalTab === tab.id
                  ? 'border-paper-primary text-paper-primary font-bold'
                  : (!isEditing && tab.id !== 'geral')
                    ? 'border-transparent text-gray-300 cursor-not-allowed'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 font-medium',
                'whitespace-nowrap pb-3 px-1 border-b-2 text-sm transition-colors cursor-pointer flex items-center gap-1.5'
              ]"
            >
              <span>{{ tab.name }}</span>
              <span v-if="tab.id === 'lotacoes' && isEditing && form.lotacoes?.length" class="text-[10px] px-1.5 py-0.2 bg-blue-100 text-blue-800 rounded-full font-semibold">
                {{ form.lotacoes.length }}
              </span>
              <span v-if="tab.id === 'ferias' && isEditing && form.ferias?.length" class="text-[10px] px-1.5 py-0.2 bg-purple-100 text-purple-800 rounded-full font-semibold">
                {{ form.ferias.length }}
              </span>
            </button>
          </nav>
        </div>

        <!-- Modal Body Scrollable -->
        <div class="flex-1 overflow-y-auto p-6">
          <!-- Modal Error Banner -->
          <div v-if="modalError" class="p-3 mb-4 bg-paper-danger/10 border border-paper-danger/20 rounded-lg text-sm text-paper-danger flex items-start justify-between gap-2">
            <div class="flex items-start gap-2">
              <ExclamationCircleIcon class="h-5 w-5 shrink-0 mt-0.5" />
              <span>{{ modalError }}</span>
            </div>
            <button @click="modalError = ''" class="text-paper-danger hover:text-red-800 text-base leading-none">&times;</button>
          </div>

          <!-- Modal Success Banner -->
          <div v-if="modalSuccess" class="p-3 mb-4 bg-emerald-50 border border-emerald-200 rounded-lg text-sm text-emerald-800 flex items-center justify-between">
            <div class="flex items-center gap-2">
              <CheckCircleIcon class="h-5 w-5 text-emerald-600 shrink-0" />
              <span>{{ modalSuccess }}</span>
            </div>
            <button @click="modalSuccess = ''" class="text-emerald-600 hover:text-emerald-800 text-base leading-none">&times;</button>
          </div>

          <!-- TAB 1: DADOS GERAIS -->
          <div v-show="currentModalTab === 'geral'">
            <form id="funcionarioForm" @submit.prevent="saveFuncionario" class="space-y-4">
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Matrícula (SIAPE / EBSERH) *</label>
                  <input 
                    v-model="form.matricula" 
                    type="text" 
                    required 
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-paper-primary focus:border-transparent text-sm"
                    placeholder="Ex: 1234567"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Nome Completo *</label>
                  <input 
                    v-model="form.nome" 
                    type="text" 
                    required 
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-paper-primary focus:border-transparent text-sm"
                    placeholder="Nome do colaborador"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Cargo *</label>
                  <select 
                    v-model="form.cargo_id" 
                    required 
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-paper-primary focus:border-transparent text-sm bg-white"
                  >
                    <option value="" disabled>Selecione um Cargo...</option>
                    <option v-for="c in sortedCargos" :key="c.id" :value="c.id">
                      {{ c.nome }}
                    </option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Carga Horária Semanal (horas) *</label>
                  <select 
                    v-model.number="form.carga_horaria" 
                    required 
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-paper-primary focus:border-transparent text-sm bg-white"
                  >
                    <option :value="20">20 horas semanais</option>
                    <option :value="24">24 horas semanais</option>
                    <option :value="30">30 horas semanais</option>
                    <option :value="36">36 horas semanais</option>
                    <option :value="40">40 horas semanais</option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Vínculo Empregatício</label>
                  <select 
                    v-model="form.vinculo_id" 
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-paper-primary focus:border-transparent text-sm bg-white"
                  >
                    <option :value="null">Nenhum / Selecione...</option>
                    <option v-for="v in sortedVinculos" :key="v.id" :value="v.id">
                      {{ v.nome }}
                    </option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Escala de Trabalho *</label>
                  <select 
                    v-model="form.escala_id" 
                    required 
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-paper-primary focus:border-transparent text-sm bg-white"
                  >
                    <option value="" disabled>Selecione uma Escala...</option>
                    <option v-for="e in sortedEscalas" :key="e.id" :value="e.id">
                      {{ e.sigla }} <span v-if="e.descricao">- {{ e.descricao }}</span>
                    </option>
                  </select>
                </div>
              </div>
            </form>
          </div>

          <!-- TAB 2: LOTAÇÕES -->
          <div v-show="currentModalTab === 'lotacoes'" class="space-y-5">
            <div v-if="!isEditing" class="p-6 text-center text-gray-500 bg-gray-50 rounded-xl border border-gray-200">
              <ExclamationCircleIcon class="h-8 w-8 mx-auto text-gray-400 mb-2" />
              <p class="font-medium text-gray-700">Salve os dados gerais primeiro</p>
              <p class="text-xs text-gray-500 mt-1">Após cadastrar o funcionário, você poderá vincular lotações e postos.</p>
            </div>

            <div v-else class="space-y-4">
              <!-- Banner de Sugestão para Fechar Lotação Anterior em Aberto -->
              <div v-if="currentOpenLotacao" class="bg-amber-50/90 border border-amber-200 rounded-xl p-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-amber-900">
                <div class="flex items-start sm:items-center gap-2">
                  <LockClosedIcon class="h-4 w-4 text-amber-600 shrink-0 mt-0.5 sm:mt-0" />
                  <div>
                    <span>Lotação ativa em: <b>{{ currentOpenLotacao.uorg?.nome || currentOpenLotacao.unidade?.nome }}</b> (desde {{ formatDateString(currentOpenLotacao.data_inicio) }}).</span>
                    <span class="block sm:inline sm:ml-1 text-amber-700">Deseja encerrar para transferir?</span>
                  </div>
                </div>
                <button 
                  type="button" 
                  @click="openCloseLotacaoModal(currentOpenLotacao)" 
                  class="bg-amber-600 hover:bg-amber-700 text-white font-semibold px-3 py-1.5 rounded-lg transition-colors inline-flex items-center justify-center gap-1.5 cursor-pointer shrink-0 shadow-xs"
                >
                  <LockClosedIcon class="h-3.5 w-3.5" />
                  <span>Fechar Esta Lotação</span>
                </button>
              </div>

              <!-- Form Nova Lotação -->
              <div class="bg-gray-50/80 p-4 rounded-xl border border-gray-200 shadow-sm space-y-3">
                <h5 class="text-xs font-bold text-gray-600 uppercase flex items-center gap-1.5">
                  <PlusIcon class="h-4 w-4 text-paper-primary" />
                  <span>Adicionar Nova Lotação</span>
                </h5>
                <form @submit.prevent="saveLotacao" class="space-y-3">
                  <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 items-end">
                    <div>
                      <label class="block text-xs font-semibold text-gray-600 mb-1">Unidade (UORG) *</label>
                      <select 
                        v-model="lotacaoForm.unidade_id" 
                        required
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg text-xs sm:text-sm focus:ring-2 focus:ring-paper-primary bg-white"
                      >
                        <option value="">Selecione a UORG...</option>
                        <option v-for="u in sortedUnidades" :key="u.id" :value="u.id">
                          {{ u.nome }} {{ u.sigla ? `(${u.sigla})` : '' }}
                        </option>
                      </select>
                    </div>
                    <div>
                      <label class="block text-xs font-semibold text-gray-600 mb-1">Posto de Serviço</label>
                      <select 
                        v-model="lotacaoForm.posto_id" 
                        @change="onPostoSelectChange"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg text-xs sm:text-sm focus:ring-2 focus:ring-paper-primary bg-white"
                      >
                        <option value="">(Opcional) Selecione...</option>
                        <option v-for="p in modalFilteredPostos" :key="p.id" :value="p.id">
                          {{ p.nome }} {{ !lotacaoForm.unidade_id && p.uorg ? `(${p.uorg.nome})` : '' }}
                        </option>
                      </select>
                    </div>
                    <div>
                      <label class="block text-xs font-semibold text-gray-600 mb-1">Início *</label>
                      <input 
                        v-model="lotacaoForm.data_inicio" 
                        type="date" 
                        required 
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg text-xs sm:text-sm focus:ring-2 focus:ring-paper-primary bg-white" 
                      />
                    </div>
                    <div>
                      <label class="block text-xs font-semibold text-gray-600 mb-1">Fim</label>
                      <input 
                        v-model="lotacaoForm.data_fim" 
                        type="date" 
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg text-xs sm:text-sm focus:ring-2 focus:ring-paper-primary bg-white" 
                      />
                    </div>
                  </div>

                  <!-- Checkbox para encerrar lotação anterior no mesmo envio se houver uma aberta -->
                  <div v-if="currentOpenLotacao" class="pt-2 border-t border-gray-200/60 flex items-center gap-2 text-xs text-gray-700">
                    <input 
                      id="autoClosePrevious" 
                      type="checkbox" 
                      v-model="lotacaoForm.autoClosePrevious" 
                      class="rounded text-paper-primary focus:ring-paper-primary h-4 w-4" 
                    />
                    <label for="autoClosePrevious" class="cursor-pointer">
                      Encerrar automaticamente a lotação anterior (<b class="font-medium text-gray-900">{{ currentOpenLotacao.uorg?.nome || currentOpenLotacao.unidade?.nome }}</b>) no dia anterior ao início desta nova lotação
                    </label>
                  </div>

                  <!-- Linha abaixo com o botão Salvar -->
                  <div class="flex justify-end pt-2 border-t border-gray-200/60">
                    <button 
                      type="submit" 
                      :disabled="savingLotacao"
                      class="bg-paper-primary hover:bg-paper-primary-hover text-white px-5 py-2 rounded-lg text-xs sm:text-sm font-semibold transition-colors disabled:opacity-50 inline-flex items-center gap-2 cursor-pointer shadow-xs" 
                      title="Salvar Lotação"
                    >
                      <ArrowPathIcon v-if="savingLotacao" class="h-4 w-4 animate-spin" />
                      <PlusIcon v-else class="h-4 w-4" />
                      <span>Salvar Lotação</span>
                    </button>
                  </div>
                </form>
              </div>

              <!-- Tabela de Lotações Cadastradas -->
              <div class="border border-gray-200 rounded-xl overflow-hidden shadow-sm">
                <table class="w-full text-xs sm:text-sm text-left">
                  <thead class="bg-gray-100 text-gray-700 uppercase font-semibold text-[11px] border-b border-gray-200">
                    <tr>
                      <th class="px-4 py-2.5">Unidade / Posto</th>
                      <th class="px-4 py-2.5">Início</th>
                      <th class="px-4 py-2.5">Fim / Situação</th>
                      <th class="px-4 py-2.5 text-center w-28">Ações</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-100">
                    <tr v-if="!form.lotacoes?.length">
                      <td colspan="4" class="px-4 py-6 text-center text-gray-400">Nenhuma lotação vinculada a este colaborador.</td>
                    </tr>
                    <tr v-else v-for="lot in sortedLotacoes" :key="lot.id" class="hover:bg-gray-50/60 transition-colors">
                      <td class="px-4 py-2.5">
                        <div class="font-medium text-gray-900">{{ lot.uorg?.nome || lot.unidade?.nome || 'UORG não identificada' }}</div>
                        <div v-if="lot.posto?.nome" class="text-xs text-gray-500 font-medium">Posto: {{ lot.posto.nome }}</div>
                      </td>
                      <td class="px-4 py-2.5 text-gray-700 font-mono text-xs">{{ formatDateString(lot.data_inicio) }}</td>
                      <td class="px-4 py-2.5">
                        <span v-if="lot.data_fim" class="font-mono text-xs text-gray-600">{{ formatDateString(lot.data_fim) }}</span>
                        <span v-else class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-100 text-emerald-800">
                          Atual (Em Aberto)
                        </span>
                      </td>
                      <td class="px-4 py-2.5 text-center space-x-1 whitespace-nowrap">
                        <!-- Botão Fechar / Encerrar Lotação -->
                        <button 
                          v-if="!lot.data_fim"
                          type="button"
                          @click="openCloseLotacaoModal(lot)" 
                          class="inline-flex items-center gap-1 text-amber-600 hover:text-amber-800 hover:bg-amber-50 px-2 py-1 rounded text-xs font-medium transition-colors cursor-pointer"
                          title="Fechar / Informar data de encerramento desta lotação"
                        >
                          <LockClosedIcon class="h-3.5 w-3.5" />
                          <span>Fechar</span>
                        </button>
                        <button 
                          v-else
                          type="button"
                          @click="openCloseLotacaoModal(lot)" 
                          class="inline-flex items-center text-gray-500 hover:text-gray-700 hover:bg-gray-100 p-1 rounded transition-colors cursor-pointer"
                          title="Alterar data fim desta lotação"
                        >
                          <PencilSquareIcon class="h-3.5 w-3.5" />
                        </button>

                        <button 
                          type="button"
                          @click="removeLotacao(lot.id)" 
                          class="text-red-500 hover:text-red-700 p-1 rounded hover:bg-red-50 transition-colors cursor-pointer"
                          title="Remover Lotação"
                        >
                          <TrashIcon class="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- TAB 3: FÉRIAS -->
          <div v-show="currentModalTab === 'ferias'" class="space-y-5">
            <div v-if="!isEditing" class="p-6 text-center text-gray-500 bg-gray-50 rounded-xl border border-gray-200">
              <ExclamationCircleIcon class="h-8 w-8 mx-auto text-gray-400 mb-2" />
              <p class="font-medium text-gray-700">Salve os dados gerais primeiro</p>
              <p class="text-xs text-gray-500 mt-1">Após cadastrar o funcionário, você poderá registrar períodos de férias.</p>
            </div>

            <div v-else class="space-y-4">
              <!-- Form Novas Férias -->
              <div class="bg-gray-50/80 p-4 rounded-xl border border-gray-200 shadow-sm">
                <h5 class="text-xs font-bold text-gray-600 uppercase mb-3 flex items-center gap-1.5">
                  <PlusIcon class="h-4 w-4 text-paper-primary" />
                  <span>Registrar Período de Férias</span>
                </h5>
                <form @submit.prevent="saveFerias" class="grid grid-cols-1 sm:grid-cols-3 gap-3 items-end">
                  <div>
                    <label class="block text-xs font-semibold text-gray-600 mb-1">Data Início *</label>
                    <input 
                      v-model="feriasForm.data_inicio" 
                      type="date" 
                      required 
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg text-xs sm:text-sm focus:ring-2 focus:ring-paper-primary bg-white" 
                    />
                  </div>
                  <div>
                    <label class="block text-xs font-semibold text-gray-600 mb-1">Data Fim *</label>
                    <input 
                      v-model="feriasForm.data_fim" 
                      type="date" 
                      required 
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg text-xs sm:text-sm focus:ring-2 focus:ring-paper-primary bg-white" 
                    />
                  </div>
                  <div>
                    <button 
                      type="submit" 
                      :disabled="savingFerias"
                      class="w-full bg-paper-primary hover:bg-paper-primary-hover text-white px-4 py-2 rounded-lg text-xs sm:text-sm font-semibold transition-colors disabled:opacity-50 inline-flex items-center justify-center gap-1.5 cursor-pointer"
                    >
                      <ArrowPathIcon v-if="savingFerias" class="h-4 w-4 animate-spin" />
                      <PlusIcon v-else class="h-4 w-4" />
                      <span>Registrar Férias</span>
                    </button>
                  </div>
                </form>
              </div>

              <!-- Tabela de Férias Registradas -->
              <div class="border border-gray-200 rounded-xl overflow-hidden shadow-sm">
                <table class="w-full text-xs sm:text-sm text-left">
                  <thead class="bg-gray-100 text-gray-700 uppercase font-semibold text-[11px] border-b border-gray-200">
                    <tr>
                      <th class="px-4 py-2.5">Data Início</th>
                      <th class="px-4 py-2.5">Data Fim</th>
                      <th class="px-4 py-2.5">Duração (Dias)</th>
                      <th class="px-4 py-2.5 text-center w-16">Ação</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-100">
                    <tr v-if="!form.ferias?.length">
                      <td colspan="4" class="px-4 py-6 text-center text-gray-400">Nenhum período de férias cadastrado.</td>
                    </tr>
                    <tr v-else v-for="fer in sortedFerias" :key="fer.id" class="hover:bg-gray-50/60 transition-colors">
                      <td class="px-4 py-2.5 font-mono text-xs text-gray-800">{{ formatDateString(fer.data_inicio) }}</td>
                      <td class="px-4 py-2.5 font-mono text-xs text-gray-800">{{ formatDateString(fer.data_fim) }}</td>
                      <td class="px-4 py-2.5 text-xs text-gray-600 font-medium">{{ calculateDays(fer.data_inicio, fer.data_fim) }} dias</td>
                      <td class="px-4 py-2.5 text-center">
                        <button 
                          @click="removeFerias(fer.id)" 
                          class="text-red-500 hover:text-red-700 p-1 rounded hover:bg-red-50 transition-colors cursor-pointer"
                          title="Remover Férias"
                        >
                          <TrashIcon class="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-6 py-4 border-t border-gray-100 bg-gray-50/70 flex justify-between items-center shrink-0">
          <div class="text-xs text-gray-500">
            <span v-if="currentModalTab !== 'geral'">Alterne entre as abas para editar dados gerais ou ocorrências.</span>
          </div>
          <div class="flex gap-3">
            <button 
              type="button" 
              @click="closeModal" 
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
            >
              {{ isEditing && currentModalTab !== 'geral' ? 'Fechar' : 'Cancelar' }}
            </button>
            <button 
              v-if="currentModalTab === 'geral'"
              type="submit" 
              form="funcionarioForm" 
              :disabled="saving" 
              class="px-4 py-2 text-sm font-medium text-white bg-paper-primary hover:bg-paper-primary-hover rounded-lg disabled:opacity-50 flex items-center gap-2 transition-colors cursor-pointer shadow-sm"
            >
              <ArrowPathIcon v-if="saving" class="h-4 w-4 animate-spin" />
              <span>{{ isEditing ? 'Salvar Alterações' : 'Cadastrar Funcionário' }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Sub-Modal: Fechar Lotação Anterior / Informar Data Fim -->
    <div v-if="isCloseLotacaoModalOpen" class="fixed inset-0 bg-gray-900/60 backdrop-blur-xs flex items-center justify-center p-4 z-60 animate-fade-in" @click.self="closeCloseLotacaoModal">
      <div class="bg-white rounded-xl shadow-paper-lg w-full max-w-md overflow-hidden flex flex-col border border-gray-100">
        <div class="px-5 py-3.5 border-b border-gray-100 flex justify-between items-center bg-amber-50/70">
          <div class="flex items-center gap-2">
            <LockClosedIcon class="h-5 w-5 text-amber-600" />
            <h4 class="text-sm font-bold text-gray-800">Encerrar / Fechar Lotação</h4>
          </div>
          <button @click="closeCloseLotacaoModal" class="text-gray-400 hover:text-gray-600 p-1 rounded-lg hover:bg-gray-100 cursor-pointer">
            <XMarkIcon class="h-4 w-4" />
          </button>
        </div>

        <div class="p-5 space-y-4">
          <div v-if="closingLotacaoItem" class="bg-gray-50 p-3 rounded-lg border border-gray-200 text-xs space-y-1">
            <div class="text-gray-500 font-semibold uppercase">Lotação Selecionada:</div>
            <div class="font-bold text-gray-900 text-sm">
              {{ closingLotacaoItem.uorg?.nome || closingLotacaoItem.unidade?.nome }}
            </div>
            <div v-if="closingLotacaoItem.posto?.nome" class="text-gray-600">
              Posto: {{ closingLotacaoItem.posto.nome }}
            </div>
            <div class="text-gray-500">
              Início: <b>{{ formatDateString(closingLotacaoItem.data_inicio) }}</b>
            </div>
          </div>

          <div v-if="closeLotacaoError" class="p-2.5 bg-paper-danger/10 border border-paper-danger/20 rounded-lg text-xs text-paper-danger">
            {{ closeLotacaoError }}
          </div>

          <div>
            <label class="block text-xs font-semibold text-gray-700 mb-1">
              Data de Encerramento (Fim) *
            </label>
            <div class="relative">
              <input 
                v-model="closeLotacaoDataFim" 
                type="date" 
                :min="closingLotacaoItem?.data_inicio"
                required 
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-paper-primary bg-white"
              />
            </div>
            <p class="text-[11px] text-gray-500 mt-1">
              Informe a data em que o colaborador encerrou as atividades nesta lotação.
            </p>
          </div>
        </div>

        <div class="px-5 py-3 border-t border-gray-100 bg-gray-50 flex justify-end gap-2">
          <button 
            type="button" 
            @click="closeCloseLotacaoModal" 
            class="px-3.5 py-1.5 text-xs font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 cursor-pointer"
          >
            Cancelar
          </button>
          <button 
            type="button" 
            @click="submitCloseLotacao" 
            :disabled="savingCloseLotacao"
            class="px-3.5 py-1.5 text-xs font-semibold text-white bg-amber-600 hover:bg-amber-700 rounded-lg disabled:opacity-50 flex items-center gap-1.5 cursor-pointer shadow-xs"
          >
            <ArrowPathIcon v-if="savingCloseLotacao" class="h-3.5 w-3.5 animate-spin" />
            <LockClosedIcon v-else class="h-3.5 w-3.5" />
            <span>Confirmar Encerramento</span>
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

// Reference lists
const funcionarios = ref<any[]>([]);
const cargos = ref<any[]>([]);
const vinculos = ref<any[]>([]);
const escalas = ref<any[]>([]);
const unidades = ref<any[]>([]);
const postos = ref<any[]>([]);

// State flags
const loading = ref(false);
const saving = ref(false);
const savingLotacao = ref(false);
const savingFerias = ref(false);

// Notification banners
const successBanner = ref('');
const errorBanner = ref('');
const modalError = ref('');
const modalSuccess = ref('');

// Filter state
const searchQuery = ref('');
const selectedLotacaoUorg = ref<number | 'TODOS' | 'SEM_LOTACAO'>('TODOS');
const selectedPosto = ref<number | 'TODOS'>('TODOS');
const selectedCargo = ref<number | 'TODOS'>('TODOS');

// Persistência automática do status da última pesquisa/filtro
const { clearSavedState: clearSavedFilters } = useSearchFilterState('funcionarios', {
  searchQuery,
  selectedLotacaoUorg,
  selectedPosto,
  selectedCargo
});

// Modal state
const isModalOpen = ref(false);
const isEditing = ref(false);
const currentModalTab = ref<'geral' | 'lotacoes' | 'ferias'>('geral');

const modalTabs: Array<{ id: 'geral' | 'lotacoes' | 'ferias'; name: string }> = [
  { id: 'geral', name: 'Dados Gerais' },
  { id: 'lotacoes', name: 'Histórico de Lotações' },
  { id: 'ferias', name: 'Férias' }
];

// Main Form
const form = reactive({
  id: null as number | null,
  matricula: '',
  nome: '',
  cargo_id: '' as number | string,
  carga_horaria: 40 as number,
  vinculo_id: null as number | null,
  escala_id: '' as number | string,
  lotacoes: [] as any[],
  ferias: [] as any[]
});

// Sub-forms
const lotacaoForm = reactive({
  unidade_id: '' as number | string,
  posto_id: '' as number | string,
  data_inicio: '2025-01-01',
  data_fim: '',
  autoClosePrevious: true
});

// Fechar Lotação Sub-Modal State
const isCloseLotacaoModalOpen = ref(false);
const closingLotacaoItem = ref<any>(null);
const closeLotacaoDataFim = ref('');
const savingCloseLotacao = ref(false);
const closeLotacaoError = ref('');

const feriasForm = reactive({
  data_inicio: '',
  data_fim: ''
});

// Sorting state
type SortableFuncionarioColumn = 'matricula' | 'nome' | 'cargo' | 'carga_horaria' | 'vinculo' | 'escala' | 'lotacao';
const sortColumn = ref<SortableFuncionarioColumn>('nome');
const sortDirection = ref<'asc' | 'desc'>('asc');

const sortBy = (column: SortableFuncionarioColumn) => {
  if (sortColumn.value === column) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortColumn.value = column;
    sortDirection.value = 'asc';
  }
};

const getSortIcon = (column: SortableFuncionarioColumn) => {
  if (sortColumn.value !== column) return '↕';
  return sortDirection.value === 'asc' ? '▲' : '▼';
};

// Safe alphabetical sorting for UORGs
const sortedUnidades = computed(() => {
  if (!Array.isArray(unidades.value)) return [];
  return [...unidades.value].sort((a, b) => {
    const nomeA = a?.nome || '';
    const nomeB = b?.nome || '';
    return nomeA.localeCompare(nomeB, 'pt-BR', { sensitivity: 'base' });
  });
});

// Safe alphabetical sorting for Cargos
const sortedCargos = computed(() => {
  if (!Array.isArray(cargos.value)) return [];
  return [...cargos.value].sort((a, b) => {
    const nomeA = a?.nome || '';
    const nomeB = b?.nome || '';
    return nomeA.localeCompare(nomeB, 'pt-BR', { sensitivity: 'base' });
  });
});

// Safe alphabetical sorting for Vínculos
const sortedVinculos = computed(() => {
  if (!Array.isArray(vinculos.value)) return [];
  return [...vinculos.value].sort((a, b) => {
    const nomeA = a?.nome || '';
    const nomeB = b?.nome || '';
    return nomeA.localeCompare(nomeB, 'pt-BR', { sensitivity: 'base' });
  });
});

// Safe alphabetical sorting for Escalas (ordenado por sigla)
const sortedEscalas = computed(() => {
  if (!Array.isArray(escalas.value)) return [];
  return [...escalas.value].sort((a, b) => {
    const siglaA = a?.sigla?.trim() || '';
    const siglaB = b?.sigla?.trim() || '';
    return siglaA.localeCompare(siglaB, 'pt-BR', { sensitivity: 'base' });
  });
});

// Postos dropdown for main screen filter (ordenado alfabeticamente)
const postosFiltradosPorUorg = computed(() => {
  if (!Array.isArray(postos.value)) return [];
  let list = postos.value;
  if (selectedLotacaoUorg.value !== 'TODOS' && selectedLotacaoUorg.value !== 'SEM_LOTACAO') {
    const targetUorg = Number(selectedLotacaoUorg.value);
    list = postos.value.filter(p => p.uorg_id === targetUorg || p.unidade_id === targetUorg);
  }
  return [...list].sort((a, b) => {
    const nomeA = a?.nome || '';
    const nomeB = b?.nome || '';
    return nomeA.localeCompare(nomeB, 'pt-BR', { sensitivity: 'base' });
  });
});

// Postos dropdown inside modal lotacao form (ordenado alfabeticamente)
const modalFilteredPostos = computed(() => {
  if (!Array.isArray(postos.value)) return [];
  let list = postos.value;
  if (lotacaoForm.unidade_id) {
    const targetUorg = Number(lotacaoForm.unidade_id);
    list = postos.value.filter(p => p.uorg_id === targetUorg || p.unidade_id === targetUorg);
  }
  return [...list].sort((a, b) => {
    const nomeA = a?.nome || '';
    const nomeB = b?.nome || '';
    return nomeA.localeCompare(nomeB, 'pt-BR', { sensitivity: 'base' });
  });
});

const onPostoSelectChange = () => {
  if (lotacaoForm.posto_id && !lotacaoForm.unidade_id) {
    const foundPosto = postos.value.find(p => p.id === Number(lotacaoForm.posto_id));
    if (foundPosto) {
      const parentUnitId = foundPosto.uorg_id || foundPosto.unidade_id;
      if (parentUnitId) {
        lotacaoForm.unidade_id = parentUnitId;
      }
    }
  }
};

// Cargos filtrados de acordo com o Posto e/ou UORG selecionados
const filteredCargos = computed(() => {
  if (!Array.isArray(cargos.value)) return [];

  // Se um posto específico foi selecionado, listar apenas as categorias/cargos que têm colaboradores nesse posto
  if (selectedPosto.value !== 'TODOS') {
    const targetPostoId = Number(selectedPosto.value);
    const cargoIdsNoPosto = new Set<number>();

    if (Array.isArray(funcionarios.value)) {
      funcionarios.value.forEach(f => {
        if (!f) return;
        const lotacoesAbertas = (f.lotacoes || []).filter(isLotacaoAberta);
        const hasPosto = lotacoesAbertas.some((l: any) => Number(l.posto_id) === targetPostoId);
        if (hasPosto && f.cargo_id) {
          cargoIdsNoPosto.add(Number(f.cargo_id));
        }
      });
    }

    const list = cargos.value.filter(c => cargoIdsNoPosto.has(Number(c.id)));
    return [...list].sort((a, b) => {
      const nomeA = a?.nome || '';
      const nomeB = b?.nome || '';
      return nomeA.localeCompare(nomeB, 'pt-BR', { sensitivity: 'base' });
    });
  }

  // Caso contrário, retorna todos os cargos ordenados alfabeticamente
  return sortedCargos.value;
});

// Ação executada quando o usuário seleciona um Posto de Serviço nos filtros principais
const onFilterPostoChange = () => {
  if (selectedPosto.value !== 'TODOS') {
    const targetPostoId = Number(selectedPosto.value);
    const foundPosto = postos.value.find(p => p.id === targetPostoId);
    if (foundPosto) {
      const parentUorgId = foundPosto.uorg_id || foundPosto.unidade_id;
      if (parentUorgId) {
        selectedLotacaoUorg.value = parentUorgId;
      }
    }
  }

  // Se o cargo atualmente selecionado não existir no novo posto selecionado, resetar para TODOS
  if (selectedCargo.value !== 'TODOS') {
    const exists = filteredCargos.value.some(c => c.id === selectedCargo.value);
    if (!exists) {
      selectedCargo.value = 'TODOS';
    }
  }
};

const onFilterUorgChange = () => {
  // Ao alterar a UORG diretamente, se o posto atual não pertencer a ela, resetar o posto
  if (selectedPosto.value !== 'TODOS') {
    const targetPostoId = Number(selectedPosto.value);
    const foundPosto = postos.value.find(p => p.id === targetPostoId);
    if (foundPosto) {
      const parentUorgId = foundPosto.uorg_id || foundPosto.unidade_id;
      if (selectedLotacaoUorg.value !== 'TODOS' && parentUorgId !== Number(selectedLotacaoUorg.value)) {
        selectedPosto.value = 'TODOS';
      }
    }
  }
  // Se o cargo selecionado não fizer mais parte dos cargos filtrados, resetar
  if (selectedCargo.value !== 'TODOS') {
    const exists = filteredCargos.value.some(c => c.id === selectedCargo.value);
    if (!exists) {
      selectedCargo.value = 'TODOS';
    }
  }
};

const hasActiveFilters = computed(() => {
  return searchQuery.value.trim() !== '' || 
         selectedLotacaoUorg.value !== 'TODOS' || 
         selectedPosto.value !== 'TODOS' || 
         selectedCargo.value !== 'TODOS';
});

const clearFilters = () => {
  searchQuery.value = '';
  selectedLotacaoUorg.value = 'TODOS';
  selectedPosto.value = 'TODOS';
  selectedCargo.value = 'TODOS';
  clearSavedFilters();
};

// Helper para verificar se a lotação está com a data final em aberto
const isLotacaoAberta = (l: any) => {
  return !l.data_fim || String(l.data_fim).trim() === '';
};

const formatLotacaoText = (lot: any) => {
  const uorgObj = lot.uorg || lot.unidade;
  if (!uorgObj) return '';
  let text = uorgObj.nome || '';
  if (lot.posto?.nome) {
    text += ` - ${lot.posto.nome}`;
  }
  return text;
};

const getActiveLotacoes = (funcionario: any): string[] => {
  if (!funcionario?.lotacoes || funcionario.lotacoes.length === 0) return [];
  const abertas = funcionario.lotacoes.filter(isLotacaoAberta);
  if (abertas.length === 0) return [];

  const sorted = [...abertas].sort((a, b) => {
    const timeA = a.data_inicio ? new Date(a.data_inicio).getTime() : 0;
    const timeB = b.data_inicio ? new Date(b.data_inicio).getTime() : 0;
    return timeB - timeA;
  });

  return sorted.map(formatLotacaoText).filter(Boolean);
};

const getCurrentLotacao = (funcionario: any) => {
  const active = getActiveLotacoes(funcionario);
  return active.join(' / ');
};

// Filtered and Sorted Funcionários list
const filteredFuncionarios = computed(() => {
  if (!Array.isArray(funcionarios.value)) return [];

  const filtered = funcionarios.value.filter(f => {
    if (!f) return false;

    // Lotações do colaborador com data final em aberto
    const lotacoesAbertas = (f.lotacoes || []).filter(isLotacaoAberta);

    // 1. Filtro por Lotação (UORG)
    if (selectedLotacaoUorg.value !== 'TODOS') {
      if (selectedLotacaoUorg.value === 'SEM_LOTACAO') {
        if (lotacoesAbertas.length > 0) return false;
      } else {
        const targetUorg = Number(selectedLotacaoUorg.value);
        const hasUorg = lotacoesAbertas.some((l: any) => 
          (l.uorg_id === targetUorg || l.unidade_id === targetUorg)
        );
        if (!hasUorg) return false;
      }
    }

    // 2. Filtro por Posto de Serviço
    if (selectedPosto.value !== 'TODOS') {
      const targetPosto = Number(selectedPosto.value);
      const hasPosto = lotacoesAbertas.some((l: any) => l.posto_id === targetPosto);
      if (!hasPosto) return false;
    }

    // 3. Filtro por Cargo
    if (selectedCargo.value !== 'TODOS' && f.cargo_id !== selectedCargo.value) {
      return false;
    }

    // 4. Busca textual
    if (searchQuery.value.trim()) {
      const lower = searchQuery.value.toLowerCase().trim();
      const matchNome = (f.nome || '').toLowerCase().includes(lower);
      const matchMatr = (f.matricula || '').toLowerCase().includes(lower);
      const matchCargo = (f.cargo?.nome || '').toLowerCase().includes(lower);
      const matchVinculo = (f.vinculo?.nome || '').toLowerCase().includes(lower);
      // Na busca por lotação, considera apenas a lotação em aberto
      const matchLotacao = lotacoesAbertas.some((l: any) => {
        const uNome = (l.uorg?.nome || l.unidade?.nome || '').toLowerCase();
        const uSigla = (l.uorg?.sigla || l.unidade?.sigla || '').toLowerCase();
        const p = (l.posto?.nome || '').toLowerCase();
        return uNome.includes(lower) || uSigla.includes(lower) || p.includes(lower);
      });

      if (!matchNome && !matchMatr && !matchCargo && !matchVinculo && !matchLotacao) {
        return false;
      }
    }

    return true;
  });

  return filtered.sort((a, b) => {
    let valA = '';
    let valB = '';

    if (sortColumn.value === 'matricula') {
      valA = a.matricula || '';
      valB = b.matricula || '';
    } else if (sortColumn.value === 'nome') {
      valA = a.nome || '';
      valB = b.nome || '';
    } else if (sortColumn.value === 'cargo') {
      valA = a.cargo?.nome || '';
      valB = b.cargo?.nome || '';
    } else if (sortColumn.value === 'carga_horaria') {
      const numA = Number(a.carga_horaria || 40);
      const numB = Number(b.carga_horaria || 40);
      return sortDirection.value === 'asc' ? numA - numB : numB - numA;
    } else if (sortColumn.value === 'vinculo') {
      valA = a.vinculo?.nome || '';
      valB = b.vinculo?.nome || '';
    } else if (sortColumn.value === 'escala') {
      valA = a.escala?.sigla?.trim() || '';
      valB = b.escala?.sigla?.trim() || '';
    } else if (sortColumn.value === 'lotacao') {
      valA = getCurrentLotacao(a);
      valB = getCurrentLotacao(b);
    }

    const comparison = valA.localeCompare(valB, 'pt-BR', { numeric: true, sensitivity: 'base' });
    return sortDirection.value === 'asc' ? comparison : -comparison;
  });
});

const sortedLotacoes = computed(() => {
  if (!Array.isArray(form.lotacoes)) return [];
  return [...form.lotacoes].sort((a, b) => {
    const timeA = a.data_inicio ? new Date(a.data_inicio).getTime() : 0;
    const timeB = b.data_inicio ? new Date(b.data_inicio).getTime() : 0;
    return timeB - timeA;
  });
});

// Detecta a lotação ativa mais recente que ainda está em aberto (sem data_fim)
const currentOpenLotacao = computed(() => {
  return sortedLotacoes.value.find(l => !l.data_fim) || null;
});

const sortedFerias = computed(() => {
  if (!Array.isArray(form.ferias)) return [];
  return [...form.ferias].sort((a, b) => {
    const timeA = a.data_inicio ? new Date(a.data_inicio).getTime() : 0;
    const timeB = b.data_inicio ? new Date(b.data_inicio).getTime() : 0;
    return timeB - timeA;
  });
});

const formatDateString = (dateStr: string) => {
  if (!dateStr) return '';
  const parts = dateStr.split('-');
  if (parts.length === 3) {
    return `${parts[2]}/${parts[1]}/${parts[0]}`;
  }
  return dateStr;
};

const calculateDays = (startStr: string, endStr: string) => {
  if (!startStr || !endStr) return 0;
  const start = new Date(startStr);
  const end = new Date(endStr);
  const diffTime = end.getTime() - start.getTime();
  const days = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
  return days > 0 ? days : 0;
};

// Data loading
const fetchData = async () => {
  loading.value = true;
  errorBanner.value = '';
  try {
    const results = await Promise.allSettled([
      api.get('/api/funcionarios'),
      api.get('/api/cargos'),
      api.get('/api/vinculos'),
      api.get('/api/escalas'),
      api.get('/api/uorgs'),
      api.get('/api/postos')
    ]);

    const [resFunc, resCar, resVin, resEsc, resUni, resPos] = results;

    if (resFunc.status === 'fulfilled') {
      funcionarios.value = Array.isArray(resFunc.value.data) ? resFunc.value.data : [];
    } else {
      console.error('Erro ao carregar funcionários:', resFunc.reason);
      errorBanner.value = resFunc.reason?.response?.data?.detail || 'Erro ao carregar lista de funcionários.';
    }

    if (resCar.status === 'fulfilled') cargos.value = Array.isArray(resCar.value.data) ? resCar.value.data : [];
    if (resVin.status === 'fulfilled') vinculos.value = Array.isArray(resVin.value.data) ? resVin.value.data : [];
    if (resEsc.status === 'fulfilled') escalas.value = Array.isArray(resEsc.value.data) ? resEsc.value.data : [];
    if (resUni.status === 'fulfilled') unidades.value = Array.isArray(resUni.value.data) ? resUni.value.data : [];
    if (resPos.status === 'fulfilled') postos.value = Array.isArray(resPos.value.data) ? resPos.value.data : [];
  } catch (err: any) {
    console.error('Erro de conexão ao carregar dados:', err);
    errorBanner.value = 'Falha de comunicação com o servidor backend.';
  } finally {
    loading.value = false;
  }
};

// Modal handlers
const switchTab = (tabId: 'geral' | 'lotacoes' | 'ferias') => {
  if (!isEditing.value && tabId !== 'geral') return;
  currentModalTab.value = tabId;
  modalError.value = '';
  modalSuccess.value = '';
};

const openModal = (item: any = null) => {
  isEditing.value = !!item;
  currentModalTab.value = 'geral';
  modalError.value = '';
  modalSuccess.value = '';

  if (item) {
    form.id = item.id;
    form.matricula = item.matricula || '';
    form.nome = item.nome || '';
    form.cargo_id = item.cargo_id || (item.cargo?.id ?? '');
    form.carga_horaria = Number(item.carga_horaria || item.cargo?.carga_horaria || 40);
    form.vinculo_id = item.vinculo_id || (item.vinculo?.id ?? null);
    form.escala_id = item.escala_id || (item.escala?.id ?? '');
    form.lotacoes = Array.isArray(item.lotacoes) ? [...item.lotacoes] : [];
    form.ferias = Array.isArray(item.ferias) ? [...item.ferias] : [];
  } else {
    form.id = null;
    form.matricula = '';
    form.nome = '';
    form.cargo_id = '';
    form.carga_horaria = 40;
    form.vinculo_id = null;
    form.escala_id = '';
    form.lotacoes = [];
    form.ferias = [];
  }

  lotacaoForm.unidade_id = '';
  lotacaoForm.posto_id = '';
  lotacaoForm.data_inicio = '2025-01-01';
  lotacaoForm.data_fim = '';

  feriasForm.data_inicio = '';
  feriasForm.data_fim = '';

  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
  modalError.value = '';
  modalSuccess.value = '';
};

// Save Funcionario (Create / Update)
const saveFuncionario = async () => {
  saving.value = true;
  modalError.value = '';
  modalSuccess.value = '';

  try {
    let trimmedMatricula = form.matricula?.trim() || '';
    if (trimmedMatricula.startsWith('99') && trimmedMatricula.endsWith('26') && trimmedMatricula.length > 4) {
      trimmedMatricula = trimmedMatricula.slice(2, -2);
      form.matricula = trimmedMatricula;
    }
    const trimmedNome = form.nome?.trim();

    if (!trimmedMatricula) {
      modalError.value = 'A matrícula é obrigatória.';
      saving.value = false;
      return;
    }

    if (!trimmedNome) {
      modalError.value = 'O nome completo é obrigatório.';
      saving.value = false;
      return;
    }

    if (!form.cargo_id) {
      modalError.value = 'Selecione um cargo.';
      saving.value = false;
      return;
    }

    if (!form.escala_id) {
      modalError.value = 'Selecione um código de escala.';
      saving.value = false;
      return;
    }

    const payload = {
      matricula: trimmedMatricula,
      nome: trimmedNome,
      cargo_id: Number(form.cargo_id),
      carga_horaria: Number(form.carga_horaria) || 40,
      vinculo_id: form.vinculo_id ? Number(form.vinculo_id) : null,
      escala_id: Number(form.escala_id)
    };

    if (isEditing.value && form.id) {
      const res = await api.put(`/api/funcionarios/${form.id}`, payload);
      successBanner.value = `Funcionário "${trimmedNome}" atualizado com sucesso!`;
      errorBanner.value = '';
      
      // Update form data from server
      if (res.data) {
        form.nome = res.data.nome;
        form.matricula = res.data.matricula;
      }
    } else {
      await api.post('/api/funcionarios', payload);
      successBanner.value = `Funcionário "${trimmedNome}" cadastrado com sucesso!`;
      errorBanner.value = '';
    }

    closeModal();
    await fetchData();
  } catch (err: any) {
    console.error('Erro ao salvar funcionário:', err);
    const msg = err.response?.data?.detail || 'Erro ao salvar funcionário no servidor.';
    modalError.value = msg;
    errorBanner.value = msg;
  } finally {
    saving.value = false;
  }
};

// Delete Funcionario
const deleteFuncionario = async (id: number) => {
  const func = funcionarios.value.find(f => f.id === id);
  const nomeFunc = func?.nome || 'este funcionário';
  if (!confirm(`Tem certeza de que deseja excluir ${nomeFunc}? Esta ação apagará também suas lotações e férias.`)) {
    return;
  }

  try {
    await api.delete(`/api/funcionarios/${id}`);
    successBanner.value = `Funcionário "${nomeFunc}" excluído com sucesso.`;
    await fetchData();
  } catch (err: any) {
    console.error('Erro ao excluir:', err);
    errorBanner.value = err.response?.data?.detail || 'Erro ao excluir o funcionário.';
  }
};

// Fechar / Encerrar Lotação Sub-Modal
const openCloseLotacaoModal = (lot: any) => {
  closingLotacaoItem.value = lot;
  // Sugere hoje ou dia anterior à data atual
  closeLotacaoDataFim.value = lot.data_fim || new Date().toISOString().split('T')[0];
  closeLotacaoError.value = '';
  isCloseLotacaoModalOpen.value = true;
};

const closeCloseLotacaoModal = () => {
  isCloseLotacaoModalOpen.value = false;
  closingLotacaoItem.value = null;
  closeLotacaoDataFim.value = '';
  closeLotacaoError.value = '';
};

const submitCloseLotacao = async () => {
  if (!closingLotacaoItem.value || !form.id) return;
  if (!closeLotacaoDataFim.value) {
    closeLotacaoError.value = 'Por favor, informe a data de encerramento.';
    return;
  }

  if (closeLotacaoDataFim.value < closingLotacaoItem.value.data_inicio) {
    closeLotacaoError.value = `A data de encerramento não pode ser anterior à data de início (${formatDateString(closingLotacaoItem.value.data_inicio)}).`;
    return;
  }

  savingCloseLotacao.value = true;
  closeLotacaoError.value = '';

  try {
    const lotId = closingLotacaoItem.value.id;
    await api.put(`/api/funcionarios/${form.id}/lotacoes/${lotId}`, {
      data_fim: closeLotacaoDataFim.value
    });

    // Atualiza funcionário
    const resFunc = await api.get(`/api/funcionarios/${form.id}`);
    form.lotacoes = resFunc.data.lotacoes || [];

    modalSuccess.value = 'Lotação encerrada com sucesso!';
    closeCloseLotacaoModal();
    await fetchData();
  } catch (err: any) {
    console.error('Erro ao fechar lotação:', err);
    let msg = 'Erro ao fechar lotação.';
    if (err.response?.data?.detail) {
      const d = err.response.data.detail;
      if (typeof d === 'string') {
        msg = d;
      } else if (Array.isArray(d)) {
        msg = d.map(item => item.msg || item.message || JSON.stringify(item)).join('; ');
      } else {
        msg = JSON.stringify(d);
      }
    }
    closeLotacaoError.value = msg;
  } finally {
    savingCloseLotacao.value = false;
  }
};

// Save Lotação (com opção de fechar a anterior)
const saveLotacao = async () => {
  if (!form.id) {
    modalError.value = 'Funcionário não identificado.';
    return;
  }
  if (!lotacaoForm.unidade_id) {
    modalError.value = 'A Unidade Organizacional (UORG) é obrigatória para a lotação.';
    return;
  }
  if (!lotacaoForm.data_inicio) {
    modalError.value = 'A data de início da lotação é obrigatória.';
    return;
  }

  savingLotacao.value = true;
  modalError.value = '';
  modalSuccess.value = '';

  try {
    // Se o usuário marcou para fechar a anterior automaticamente
    if (lotacaoForm.autoClosePrevious && currentOpenLotacao.value) {
      const openLot = currentOpenLotacao.value;
      // Calcula o dia anterior à nova data de início
      const newStartDate = new Date(lotacaoForm.data_inicio);
      const prevDate = new Date(newStartDate);
      prevDate.setDate(prevDate.getDate() - 1);
      const formattedPrevDate = prevDate.toISOString().split('T')[0];

      // Só encerra se a data de início da nova for posterior à de início da anterior
      if (formattedPrevDate >= openLot.data_inicio) {
        await api.put(`/api/funcionarios/${form.id}/lotacoes/${openLot.id}`, {
          data_fim: formattedPrevDate
        });
      }
    }

    const payload: any = {
      data_inicio: lotacaoForm.data_inicio,
      uorg_id: Number(lotacaoForm.unidade_id)
    };
    if (lotacaoForm.posto_id) {
      payload.posto_id = Number(lotacaoForm.posto_id);
    }
    if (lotacaoForm.data_fim) {
      payload.data_fim = lotacaoForm.data_fim;
    }

    await api.post(`/api/funcionarios/${form.id}/lotacoes`, payload);

    // Refresh single funcionario data to update lotacoes table
    const resFunc = await api.get(`/api/funcionarios/${form.id}`);
    form.lotacoes = resFunc.data.lotacoes || [];

    // Reset sub-form
    lotacaoForm.unidade_id = '';
    lotacaoForm.posto_id = '';
    lotacaoForm.data_inicio = '2025-01-01';
    lotacaoForm.data_fim = '';
    lotacaoForm.autoClosePrevious = true;

    modalSuccess.value = 'Lotação vinculada com sucesso!';
    await fetchData();
  } catch (err: any) {
    console.error('Erro ao adicionar lotação:', err);
    let msg = 'Erro ao vincular lotação.';
    if (err.response?.data?.detail) {
      const d = err.response.data.detail;
      if (typeof d === 'string') {
        msg = d;
      } else if (Array.isArray(d)) {
        msg = d.map(item => item.msg || item.message || JSON.stringify(item)).join('; ');
      } else {
        msg = JSON.stringify(d);
      }
    }
    modalError.value = msg;
  } finally {
    savingLotacao.value = false;
  }
};

// Remove Lotação
const removeLotacao = async (lotacaoId: number) => {
  if (!confirm('Deseja remover este registro de lotação?')) return;

  try {
    await api.delete(`/api/funcionarios/${form.id}/lotacoes/${lotacaoId}`);
    const resFunc = await api.get(`/api/funcionarios/${form.id}`);
    form.lotacoes = resFunc.data.lotacoes || [];
    modalSuccess.value = 'Lotação removida com sucesso.';
    await fetchData();
  } catch (err: any) {
    console.error('Erro ao remover lotação:', err);
    modalError.value = err.response?.data?.detail || 'Erro ao remover lotação.';
  }
};

// Save Férias
const saveFerias = async () => {
  if (!form.id) {
    modalError.value = 'Funcionário não identificado.';
    return;
  }
  if (!feriasForm.data_inicio || !feriasForm.data_fim) {
    modalError.value = 'As datas de início e fim das férias são obrigatórias.';
    return;
  }
  if (feriasForm.data_inicio > feriasForm.data_fim) {
    modalError.value = 'A data de início não pode ser posterior à data de término.';
    return;
  }

  savingFerias.value = true;
  modalError.value = '';
  modalSuccess.value = '';

  try {
    const payload = {
      data_inicio: feriasForm.data_inicio,
      data_fim: feriasForm.data_fim
    };

    await api.post(`/api/funcionarios/${form.id}/ferias`, payload);

    const resFunc = await api.get(`/api/funcionarios/${form.id}`);
    form.ferias = resFunc.data.ferias || [];

    feriasForm.data_inicio = '';
    feriasForm.data_fim = '';

    modalSuccess.value = 'Período de férias registrado com sucesso!';
    await fetchData();
  } catch (err: any) {
    console.error('Erro ao registrar férias:', err);
    modalError.value = err.response?.data?.detail || 'Erro ao registrar férias.';
  } finally {
    savingFerias.value = false;
  }
};

// Remove Férias
const removeFerias = async (feriasId: number) => {
  if (!confirm('Deseja remover este registro de férias?')) return;

  try {
    await api.delete(`/api/funcionarios/${form.id}/ferias/${feriasId}`);
    const resFunc = await api.get(`/api/funcionarios/${form.id}`);
    form.ferias = resFunc.data.ferias || [];
    modalSuccess.value = 'Registro de férias removido com sucesso.';
    await fetchData();
  } catch (err: any) {
    console.error('Erro ao remover férias:', err);
    modalError.value = err.response?.data?.detail || 'Erro ao remover férias.';
  }
};

onMounted(() => {
  fetchData();
});
</script>
