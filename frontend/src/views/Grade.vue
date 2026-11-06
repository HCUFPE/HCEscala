<template>
  <div class="grade-container space-y-6">
    <!-- Success Toast Notification -->
    <transition
      enter-active-class="transform ease-out duration-300 transition"
      enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
      enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
      leave-active-class="transition ease-in duration-100"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="toastMessage" 
        class="fixed top-5 right-5 z-50 flex items-center gap-3 bg-emerald-600 text-white px-4 py-3 rounded-xl shadow-xl font-medium text-sm border border-emerald-500"
      >
        <span class="text-base">✅</span>
        <span>{{ toastMessage }}</span>
        <button type="button" @click="toastMessage = ''" class="ml-2 hover:opacity-80 text-white font-bold p-1 cursor-pointer">
          &times;
        </button>
      </div>
    </transition>

    <!-- Top Header -->
    <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 bg-white p-5 rounded-xl shadow-sm border border-gray-200">
      <div>
        <div class="flex items-center gap-3">
          <div class="p-2.5 bg-paper-primary/10 text-paper-primary rounded-xl">
            <CalendarDaysIcon class="h-7 w-7" />
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-2xl font-bold text-paper-sidebar tracking-tight">Gerenciamento de Escala</h2>
              <span 
                v-if="userScope"
                class="px-2.5 py-0.5 rounded-full text-xs font-bold border inline-flex items-center gap-1 shadow-2xs"
                :class="{
                  'bg-purple-100 text-purple-900 border-purple-300': authStore.isAdmin,
                  'bg-emerald-100 text-emerald-900 border-emerald-300': !authStore.isAdmin && userScope.nivel === 'DIVGP_ADMIN',
                  'bg-blue-100 text-blue-900 border-blue-300': !authStore.isAdmin && (userScope.nivel === 'UORG' || userScope.nivel === 'UNIDADE' || userScope.nivel === 'SETOR'),
                  'bg-amber-100 text-amber-900 border-amber-300': !authStore.isAdmin && userScope.nivel === 'POSTO',
                  'bg-gray-100 text-gray-700 border-gray-300': !authStore.isAdmin && userScope.nivel === 'COLABORADOR'
                }"
                :title="userScope.descricao_escopo"
              >
                <span v-if="authStore.isAdmin">🛡️ Administrador do Sistema</span>
                <span v-else-if="userScope.nivel === 'DIVGP_ADMIN'">🏢 Gerente da DIVGP</span>
                <span v-else-if="userScope.nivel === 'UORG' || userScope.nivel === 'UNIDADE' || userScope.nivel === 'SETOR'">🏛️ Gerente da Unidade</span>
                <span v-else-if="userScope.nivel === 'POSTO'">📋 Supervisor de Posto</span>
                <span v-else>👤 Usuário Externo / Colaborador</span>
              </span>
            </div>
            <p class="text-xs sm:text-sm text-paper-text">Hospital das Clínicas / UFPE · Escala Mensal dos Colaboradores</p>
          </div>
        </div>
      </div>

      <!-- Action & Month/Year selector -->
      <div class="flex flex-wrap items-center gap-3">
        <!-- Month and Year Selection -->
        <div class="flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-lg p-1">
          <select 
            v-model="selectedMes" 
            @change="fetchData" 
            class="bg-white border-0 text-sm font-semibold text-paper-sidebar rounded px-2.5 py-1.5 focus:ring-1 focus:ring-paper-primary shadow-xs cursor-pointer"
          >
            <option v-for="(nome, idx) in mesesNomes" :key="idx + 1" :value="idx + 1">
              {{ nome }}
            </option>
          </select>

          <select 
            v-model="selectedAno" 
            @change="fetchData" 
            class="bg-white border-0 text-sm font-semibold text-paper-sidebar rounded px-2.5 py-1.5 focus:ring-1 focus:ring-paper-primary shadow-xs cursor-pointer"
          >
            <option v-for="ano in anosDisponiveis" :key="ano" :value="ano">
              {{ ano }}
            </option>
          </select>
        </div>

        <!-- Seletor de Modo de Visualização (Tabela / Calendário) -->
        <div class="inline-flex rounded-xl bg-gray-100 p-1 border border-gray-300 shadow-xs">
          <button 
            type="button" 
            @click="viewMode = 'tabela'"
            class="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-bold rounded-lg transition-all cursor-pointer"
            :class="viewMode === 'tabela' 
              ? 'bg-white text-paper-primary shadow-xs border border-gray-200' 
              : 'text-gray-600 hover:text-gray-950 hover:bg-gray-200/50'"
            title="Exibir no formato tradicional de grade matricial mensal"
          >
            <TableCellsIcon class="h-4 w-4 text-paper-primary" />
            <span>Visão Tabela</span>
          </button>

          <button 
            type="button" 
            @click="viewMode = 'calendario'"
            class="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-bold rounded-lg transition-all cursor-pointer"
            :class="viewMode === 'calendario' 
              ? 'bg-white text-paper-primary shadow-xs border border-gray-200' 
              : 'text-gray-600 hover:text-gray-950 hover:bg-gray-200/50'"
            title="Exibir no formato de calendário mensal com profissionais alocados por dia"
          >
            <CalendarIcon class="h-4 w-4 text-paper-primary" />
            <span>Visão Calendário</span>
          </button>
        </div>

        <!-- Action Buttons -->
        <button 
          @click="openCopiarModal" 
          class="inline-flex items-center gap-2 bg-white hover:bg-gray-50 text-paper-sidebar border border-gray-300 px-3.5 py-2 rounded-lg text-sm font-medium transition-all shadow-xs hover:border-gray-400 cursor-pointer"
        >
          <DocumentDuplicateIcon class="h-4 w-4 text-paper-primary" />
          <span>Copiar Escala</span>
        </button>

        <button 
          @click="openCriarModal" 
          class="inline-flex items-center gap-2 bg-paper-primary hover:bg-paper-primary-hover text-white px-4 py-2 rounded-lg text-sm font-medium transition-all shadow-sm active:scale-98 cursor-pointer"
        >
          <PlusIcon class="h-4 w-4" />
          <span>Nova Escala</span>
        </button>
      </div>
    </div>

    <!-- Summary KPI Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <!-- Total Colaboradores -->
      <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-200 hover:border-paper-primary/40 transition-all">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs font-semibold text-paper-text uppercase tracking-wider">Colaboradores no Setor</p>
            <p class="text-3xl font-extrabold text-paper-sidebar mt-1">{{ indicators.total_colaboradores }}</p>
            <p class="text-xs text-gray-500 mt-1">Lotação ativa nesta unidade</p>
          </div>
          <div class="p-3 bg-blue-50 text-paper-primary rounded-xl">
            <UserGroupIcon class="h-6 w-6" />
          </div>
        </div>
      </div>

      <!-- Férias/Afastados no Mês -->
      <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-200 hover:border-paper-warning/40 transition-all">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs font-semibold text-paper-text uppercase tracking-wider">Férias / Afastamentos</p>
            <p class="text-3xl font-extrabold text-amber-700 mt-1">{{ indicators.total_ferias }}</p>
            <p class="text-xs text-gray-500 mt-1">Colaboradores em gozo no mês</p>
          </div>
          <div class="p-3 bg-amber-50 text-amber-600 rounded-xl">
            <SunIcon class="h-6 w-6" />
          </div>
        </div>
      </div>

      <!-- Múltiplas Lotações -->
      <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-200 hover:border-purple-300 transition-all">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs font-semibold text-paper-text uppercase tracking-wider">Múltiplas Lotações</p>
            <p class="text-3xl font-extrabold text-purple-800 mt-1">{{ indicators.total_multiplas_lotacoes }}</p>
            <p class="text-xs text-gray-500 mt-1">Alocados em mais de um posto</p>
          </div>
          <div class="p-3 bg-purple-50 text-purple-600 rounded-xl">
            <ArrowsRightLeftIcon class="h-6 w-6" />
          </div>
        </div>
      </div>
    </div>

    <!-- Filters Section -->
    <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-200 flex flex-wrap gap-4 items-end">
      <!-- Unidade Filter (Filtered by permission & Hierarchy) -->
      <div class="space-y-1 w-full sm:w-80">
        <div class="flex items-center justify-between">
          <label class="block text-xs font-semibold text-paper-text uppercase flex items-center gap-1">
            <span>Órgão / Unidade</span>
            <span v-if="!authStore.isAdmin" class="text-[10px] text-gray-400 font-normal">(Permitidas)</span>
          </label>
          <label v-if="selectedUnidadeId" class="inline-flex items-center gap-1 text-[11px] font-semibold text-paper-primary cursor-pointer hover:underline select-none">
            <input 
              type="checkbox" 
              v-model="incluirSubordinadas" 
              @change="onUnidadeChange"
              class="rounded text-paper-primary focus:ring-paper-primary h-3.5 w-3.5 border-gray-300 cursor-pointer"
            />
            <span>Hierarquia (Subordinadas)</span>
          </label>
        </div>
        <select 
          v-model="selectedUnidadeId" 
          @change="onUnidadeChange" 
          class="form-control text-sm w-full font-medium"
        >
          <option :value="undefined">Todas as Unidades Autorizadas</option>
          <option v-for="u in unidadesFormatadasHierarquia" :key="u.id" :value="u.id">
            {{ u.display_nome }}
          </option>
        </select>
      </div>

      <!-- Categoria / Cargo Filter -->
      <div class="space-y-1 w-full sm:w-48">
        <label class="block text-xs font-semibold text-paper-text uppercase">Categoria</label>
        <select 
          v-model="selectedCargoId" 
          @change="fetchData" 
          class="form-control text-sm w-full font-medium"
        >
          <option :value="undefined">Todas as Categorias</option>
          <option v-for="c in sortedCargos" :key="c.id" :value="c.id">
            {{ c.nome }}
          </option>
        </select>
      </div>

      <!-- Posto de Serviço Filter -->
      <div class="space-y-1 w-full sm:w-48 notranslate" translate="no">
        <label class="block text-xs font-semibold text-paper-text uppercase notranslate" translate="no">Posto de Serviço</label>
        <select 
          v-model="selectedPostoId" 
          @change="onPostoChange" 
          class="form-control text-sm w-full font-medium notranslate"
          translate="no"
        >
          <option :value="undefined">Todos os Postos</option>
          <option v-for="p in postosFiltrados" :key="p.id" :value="p.id">
            {{ p.nome }}
          </option>
        </select>
      </div>

      <!-- Status Filter (DIVGP) -->
      <div class="space-y-1 w-full sm:w-64">
        <label class="block text-xs font-semibold text-paper-text uppercase flex items-center justify-between">
          <span>Status da Escala</span>
          <span class="text-[10px] text-emerald-700 font-bold">Fluxo</span>
        </label>
        <select 
          v-model="selectedStatus" 
          @change="fetchData" 
          class="form-control text-sm w-full font-medium"
        >
          <option value="Todos">Todos os Status</option>
          <option value="Rascunho">⚪ Em Elaboração (Chefe do Posto)</option>
          <option value="Enviada_Superior">🔵 Enviada para Unidade (Aguardando Chefe da Unidade)</option>
          <option value="Devolvida">🟠 Devolvida para Ajuste (Retornada ao Posto)</option>
          <option value="DIVGP_PUBLICADAS">🟢 Publicadas pela DIVGP (Oficial / Bloqueada)</option>
          <option value="Pendente">⚪ Sem Escala Cadastrada</option>
        </select>
      </div>

      <!-- Search Input -->
      <div class="space-y-1 flex-1 min-w-[200px]">
        <label class="block text-xs font-semibold text-paper-text uppercase">Buscar Colaborador</label>
        <div class="relative">
          <input 
            v-model="searchTerm" 
            @input="onSearchInput" 
            type="text" 
            placeholder="Nome ou SIAPE/Matrícula..." 
            class="form-control text-sm w-full pr-8"
          />
          <span v-if="searchTerm" @click="clearSearch" class="absolute right-2.5 top-2.5 text-gray-400 hover:text-gray-600 cursor-pointer text-xs">
            ✕
          </span>
        </div>
      </div>

      <!-- Clear Filters Button -->
      <button 
        @click="clearFilters" 
        class="bg-white border border-gray-300 text-paper-text px-4 py-2 rounded-lg text-sm hover:bg-gray-50 transition-colors shadow-xs cursor-pointer"
      >
        Limpar Filtros
      </button>
    </div>

    <!-- Monthly Grid Matrix Table -->
    <div v-if="viewMode === 'tabela'" class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div class="bg-paper-sidebar text-white px-5 py-3.5 flex flex-wrap justify-between items-center gap-3">
        <div class="flex items-center gap-2 flex-wrap">
          <h3 class="font-semibold text-sm">
            {{ getUnidadeNomeDisplay() }} · {{ mesesNomes[selectedMes - 1] }} / {{ selectedAno }}
          </h3>
          <span class="text-xs bg-blue-500/30 text-blue-100 px-2 py-0.5 rounded-full">
            {{ matrixData.length }} colaborador(es)
          </span>

          <!-- Chips com os Filtros Selecionados Atualmente -->
          <div v-if="activeFiltersList.length > 0" class="flex items-center gap-1.5 flex-wrap">
            <span 
              v-for="(f, fIdx) in activeFiltersList" 
              :key="fIdx"
              class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium bg-white/15 text-white border border-white/20 shadow-2xs"
            >
              <span class="text-blue-200 text-[10px] font-bold uppercase tracking-wider">{{ f.label }}:</span>
              <span class="font-semibold text-amber-300">{{ f.value }}</span>
            </span>
          </div>

          <!-- Botões de ordenação rápida -->
          <div class="flex items-center gap-1.5 flex-wrap">
            <button 
              @click="toggleSort('dias_alocados')" 
              class="text-xs px-2.5 py-1 rounded-md font-medium transition-all flex items-center gap-1 cursor-pointer border"
              :class="sortColumn === 'dias_alocados' ? 'bg-amber-400 text-gray-900 border-amber-300 shadow-xs font-semibold' : 'bg-white/10 hover:bg-white/20 text-white border-white/20'"
              title="Ordenar a grade colocando no topo os colaboradores que possuem escalas/plantões alocados"
            >
              <span>📅 Dias Alocados</span>
              <span class="font-mono text-[11px]">{{ sortColumn === 'dias_alocados' ? (sortDirection === 'desc' ? '▼' : '▲') : '↕' }}</span>
            </button>
            <button 
              @click="toggleSort('cargo')" 
              class="text-xs px-2.5 py-1 rounded-md font-medium transition-all flex items-center gap-1 cursor-pointer border"
              :class="sortColumn === 'cargo' ? 'bg-amber-400 text-gray-900 border-amber-300 shadow-xs font-semibold' : 'bg-white/10 hover:bg-white/20 text-white border-white/20'"
              title="Ordenar alfabeticamente por Cargo do colaborador"
            >
              <span>🏷️ Cargo</span>
              <span class="font-mono text-[11px]">{{ sortColumn === 'cargo' ? (sortDirection === 'asc' ? '▲' : '▼') : '↕' }}</span>
            </button>
            <button 
              @click="toggleSort('escala')" 
              class="text-xs px-2.5 py-1 rounded-md font-medium transition-all flex items-center gap-1 cursor-pointer border"
              :class="sortColumn === 'escala' ? 'bg-amber-400 text-gray-900 border-amber-300 shadow-xs font-semibold' : 'bg-white/10 hover:bg-white/20 text-white border-white/20'"
              title="Ordenar pela Escala de trabalho do cadastro do funcionário"
            >
              <span>⏱️ Escala</span>
              <span class="font-mono text-[11px]">{{ sortColumn === 'escala' ? (sortDirection === 'asc' ? '▲' : '▼') : '↕' }}</span>
            </button>
          </div>

          <!-- Indicador de Dia Selecionado / Destaque -->
          <div 
            v-if="selectedDiaHighlight" 
            class="flex items-center gap-1.5 bg-amber-400 text-gray-950 px-2.5 py-1 rounded-md text-xs font-bold shadow-xs animate-fade-in"
          >
            <span>Dia {{ selectedDiaHighlight }} selecionado</span>
            <button 
              @click="selectedDiaHighlight = null" 
              class="hover:bg-amber-500 rounded p-0.5 transition-colors cursor-pointer"
              title="Limpar destaque do dia"
            >
              <XMarkIcon class="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <!-- Ação em lote: Aprovar Todas para Unidade (Supervisor do Posto ou Admin) -->
          <button 
            v-if="selectedUnidadeId && (!isTopLevelForSelectedUnit || authStore.isAdmin)"
            @click="enviarLoteSuperior" 
            class="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-bold transition-all shadow-xs flex items-center gap-1.5 cursor-pointer"
            title="Finalizar e aprovar todas as escalas elaboradas do posto para a Chefia da Unidade."
          >
            <ArrowUpCircleIcon class="h-4 w-4" />
            <span>Aprovar para Unidade</span>
          </button>

          <!-- Ação em lote: Aprovar e Enviar Todas para DIVGP (Chefia da Unidade, DIVGP ou Admin) -->
          <button 
            v-if="selectedUnidadeId && (isTopLevelForSelectedUnit || authStore.isAdmin)"
            @click="publishAllUnidade" 
            class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold transition-all shadow-xs flex items-center gap-1.5 cursor-pointer"
            title="Aprovar e enviar todas as escalas desta unidade para a DIVGP."
          >
            <MegaphoneIcon class="h-4 w-4" />
            <span>Aprovar para DIVGP</span>
          </button>
          <div class="hidden md:flex items-center gap-2.5 text-xs text-blue-200 border-l border-blue-400/30 pl-3">
            <span class="inline-flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-xs bg-blue-100 border border-blue-300 inline-block"></span> M</span>
            <span class="inline-flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-xs bg-amber-100 border border-amber-300 inline-block"></span> T</span>
            <span class="inline-flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-xs bg-purple-100 border border-purple-300 inline-block"></span> N</span>
            <span class="inline-flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-xs bg-emerald-100 border border-emerald-300 inline-block"></span> D</span>
            <span class="inline-flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-xs bg-rose-100 border border-rose-300 inline-block"></span> FE</span>
          </div>
        </div>
      </div>

      <!-- Barra de Rolagem Horizontal Superior Sincronizada -->
      <div 
        ref="topScrollContainer" 
        @scroll="handleTopScroll"
        class="overflow-x-auto border-b border-gray-200 bg-gray-50/70 scrollbar-thin"
        style="height: 14px;"
      >
        <div :style="{ width: tableScrollWidth + 'px', height: '1px' }"></div>
      </div>

      <!-- Table Content -->
      <div 
        ref="bottomScrollContainer" 
        @scroll="handleBottomScroll" 
        class="overflow-x-auto scrollbar-thin"
      >
        <table ref="matrixTableRef" class="w-full text-xs text-left border-collapse">
          <thead class="bg-gray-100 text-paper-text uppercase font-semibold text-[11px] select-none">
            <tr>
              <th 
                class="px-2.5 py-2.5 sticky left-0 bg-gray-100 z-20 border-b border-r border-gray-200 w-[420px] min-w-[420px] max-w-[420px] transition-colors"
              >
                <div 
                  @click="toggleSort('nome')" 
                  class="cursor-pointer hover:text-paper-primary flex items-center gap-1 font-bold text-[10.5px]"
                  title="Clique para ordenar por Nome do Profissional"
                >
                  <span>Profissional (Siape - Nome - Cargo)</span>
                  <span class="text-xs font-mono text-gray-500">{{ sortColumn === 'nome' ? (sortDirection === 'asc' ? '▲' : '▼') : '↕' }}</span>
                </div>
              </th>
              <th 
                v-for="dia in totalDiasMes" 
                :key="dia" 
                @click="toggleDiaHighlight(dia)"
                class="px-1 py-2 text-center border-b border-r border-gray-200 min-w-[32px] max-w-[34px] relative select-none cursor-pointer hover:bg-amber-100/70 transition-colors"
                :class="[
                  selectedDiaHighlight === dia ? 'bg-amber-400 text-gray-900 font-black ring-2 ring-inset ring-amber-500 shadow-sm' :
                  (sortColumn === ('dia_' + dia) ? 'bg-amber-100 text-amber-900 font-black border-b-2 border-b-amber-500' :
                  (feriadosMesMap[dia] ? 'bg-rose-50/90 text-rose-900 font-bold border-b-2 border-b-rose-400' : 
                  (isWeekend(dia) ? 'bg-gray-200/60 font-bold text-gray-800' : '')))
                ]"
                :title="(feriadosMesMap[dia] ? ('Feriado: ' + feriadosMesMap[dia]) : (getDiaSemanaSigla(dia) + ' - Dia ' + dia)) + ' (Clique para destacar colaboradores em escala e ordenar)'"
              >
                <div class="flex items-center justify-center gap-0.5">
                  <span>{{ dia }}</span>
                  <span v-if="feriadosMesMap[dia]" class="w-1.5 h-1.5 rounded-full bg-rose-500 inline-block" title="Feriado Oficial"></span>
                </div>
                <div class="text-[9px] font-normal notranslate" translate="no" :class="[selectedDiaHighlight === dia ? 'text-gray-900 font-bold' : (feriadosMesMap[dia] ? 'text-rose-700 font-bold' : 'text-gray-500')]">
                  {{ feriadosMesMap[dia] ? 'FER' : getDiaSemanaSigla(dia) }}
                </div>
              </th>
              <th 
                @click="toggleSort('horas')"
                class="px-2.5 py-3 text-center border-b border-r border-gray-200 min-w-[105px] max-w-[115px] cursor-pointer hover:bg-gray-200/80 transition-colors"
                title="Clique para ordenar por Carga Horária Escalada"
              >
                <div class="flex items-center justify-center gap-1">
                  <span>Carga Horária</span>
                  <span class="text-xs font-mono text-gray-500">{{ sortColumn === 'horas' ? (sortDirection === 'asc' ? '▲' : '▼') : '↕' }}</span>
                </div>
              </th>
              <th class="px-2.5 py-3 text-center border-b border-r border-gray-200 min-w-[110px] max-w-[125px]">
                <span>Status</span>
              </th>
              <th class="px-3 py-3 text-center border-b border-gray-200 min-w-[70px]">Ações</th>
            </tr>
          </thead>

          <tbody class="divide-y divide-gray-100">
            <!-- Loading State -->
            <tr v-if="loading">
              <td :colspan="totalDiasMes + 4" class="px-4 py-12 text-center text-gray-500">
                <div class="flex flex-col items-center justify-center gap-2">
                  <div class="w-8 h-8 border-4 border-paper-primary border-t-transparent rounded-full animate-spin"></div>
                  <span>Carregando dados da escala...</span>
                </div>
              </td>
            </tr>

            <!-- Empty State -->
            <tr v-else-if="sortedMatrixData.length === 0">
              <td :colspan="totalDiasMes + 4" class="px-4 py-12 text-center text-gray-500">
                <p class="font-medium text-gray-700">Nenhum colaborador encontrado para os filtros selecionados.</p>
                <p class="text-xs text-gray-400 mt-1">Tente ajustar a unidade, a categoria ou o termo de busca.</p>
              </td>
            </tr>

            <!-- Data Rows -->
            <tr 
              v-else 
              v-for="row in sortedMatrixData" 
              :key="row.funcionario_id" 
              class="transition-colors group"
              :class="[
                selectedDiaHighlight && hasPlantaoNoDia(row, selectedDiaHighlight)
                  ? 'bg-amber-50/80 hover:bg-amber-100/70'
                  : (selectedDiaHighlight
                      ? 'opacity-60 hover:opacity-100 hover:bg-blue-50/30'
                      : 'hover:bg-blue-50/40')
              ]"
            >
              <!-- Sticky Colaborador Column -->
              <td 
                class="px-2.5 py-2 sticky left-0 font-medium text-paper-sidebar z-10 shadow-[2px_0_4px_rgba(0,0,0,0.04)] border-r border-gray-200 transition-colors w-[420px] min-w-[420px] max-w-[420px]"
                :class="[
                  selectedDiaHighlight && hasPlantaoNoDia(row, selectedDiaHighlight)
                    ? 'bg-amber-50/95 border-l-4 border-l-amber-500 font-semibold'
                    : 'bg-white group-hover:bg-slate-50'
                ]"
              >
                <div class="font-semibold text-gray-900 truncate text-[10px] sm:text-[10.5px] leading-tight" :title="(row.matricula ? row.matricula + ' - ' : '') + row.nome + ((row.cargo && row.cargo !== '-') ? ' (' + row.cargo + ')' : '')">
                  <span>{{ formatProfissional70(row) }}</span>
                </div>
                <!-- Badge exclusivo de Férias se estiver em gozo no mês -->
                <div v-if="row.is_ferias_mes" class="flex flex-wrap gap-1 mt-0.5">
                  <span class="px-1.5 py-0.2 rounded text-[8.5px] font-semibold bg-rose-100 text-rose-700 border border-rose-200">
                    Férias
                  </span>
                </div>
              </td>

              <!-- Days Columns -->
              <td 
                v-for="diaItem in row.dias" 
                :key="diaItem.dia" 
                class="px-0.5 py-1.5 text-center border-r border-gray-100"
                :class="[
                  selectedDiaHighlight === diaItem.dia && hasPlantaoNoDia(row, diaItem.dia)
                    ? 'bg-amber-100/90 ring-1 ring-inset ring-amber-400'
                    : (selectedDiaHighlight === diaItem.dia
                        ? 'bg-amber-50/40'
                        : (feriadosMesMap[diaItem.dia] ? 'bg-rose-50/40' : 
                           (isWeekend(diaItem.dia) ? 'bg-gray-50/70 group-hover:bg-blue-50/30' : '')))
                ]"
              >
                <!-- Badge of shift / legend in current unit -->
                <span 
                  v-if="diaItem.sigla" 
                  :class="getSiglaBadgeClass(diaItem.sigla)"
                  class="inline-block w-6 py-0.5 rounded text-[10px] font-bold shadow-xs cursor-default"
                  :title="getDiaTooltip(diaItem)"
                >
                  {{ diaItem.sigla }}
                </span>
                <!-- Badge of shift in OTHER linked unit (Workload division) -->
                <span 
                  v-else-if="diaItem.is_outra_unidade" 
                  class="inline-flex items-center justify-center w-6 py-0.5 rounded text-[9px] font-bold bg-teal-50 text-teal-700 border border-dashed border-teal-400 cursor-help"
                  :title="diaItem.descricao || ('Escala em outra unidade: ' + diaItem.outra_unidade_nome)"
                >
                  {{ diaItem.outra_unidade_sigla }}
                </span>
                <span v-else-if="diaItem.is_ferias" class="inline-block w-6 py-0.5 rounded text-[10px] font-bold bg-rose-100 text-rose-700">
                  FE
                </span>
                <!-- Feriado Oficial sem turno -->
                <span 
                  v-else-if="diaItem.is_feriado" 
                  class="inline-flex items-center justify-center w-6 py-0.5 rounded text-[9px] font-bold bg-rose-50 text-rose-700 border border-rose-200 cursor-help"
                  :title="'Feriado: ' + (diaItem.feriado_nome || 'Feriado Oficial')"
                >
                  FR
                </span>
                <span v-else class="text-gray-300 font-light select-none">-</span>
              </td>

              <!-- Carga Horária Column -->
              <td 
                class="px-2 py-2 text-center border-r border-gray-200 whitespace-nowrap select-none transition-colors"
                :class="selectedDiaHighlight && hasPlantaoNoDia(row, selectedDiaHighlight) ? 'bg-amber-100/50' : 'bg-gray-50/40'"
              >
                <div class="flex flex-col items-center justify-center gap-0.5">
                  <span 
                    class="text-[11px] font-extrabold font-mono tracking-tight"
                    :class="{
                      'text-rose-700 font-black': row.ultrapassou_carga_horaria,
                      'text-emerald-700': !row.ultrapassou_carga_horaria && row.total_horas_escaladas === row.carga_horaria_mensal_teto,
                      'text-paper-sidebar': !row.ultrapassou_carga_horaria && row.total_horas_escaladas !== row.carga_horaria_mensal_teto
                    }"
                  >
                    {{ row.total_horas_escaladas || 0 }}h / {{ row.carga_horaria_mensal_teto || 0 }}h
                  </span>

                  <!-- Status Tag -->
                  <span 
                    v-if="row.ultrapassou_carga_horaria" 
                    class="text-[9px] px-1.5 py-0.2 rounded-full font-black bg-rose-100 text-rose-700 border border-rose-300"
                    :title="'Excedeu ' + row.horas_excedentes + 'h do teto mensal!'"
                  >
                    ⚠️ +{{ row.horas_excedentes }}h
                  </span>
                  <span 
                    v-else-if="row.total_horas_escaladas !== undefined && row.total_horas_escaladas === row.carga_horaria_mensal_teto && row.total_horas_escaladas > 0" 
                    class="text-[9px] px-1.5 py-0.2 rounded-full font-bold bg-emerald-100 text-emerald-800 border border-emerald-300"
                  >
                    ✓ Completa
                  </span>
                  <span 
                    v-else 
                    class="text-[9px] text-gray-500 font-medium"
                  >
                    {{ (row.saldo_horas && row.saldo_horas > 0) ? ('Faltam ' + row.saldo_horas + 'h') : '0h' }}
                  </span>
                </div>
              </td>

              <!-- Status da Escala Column (Após Carga Horária) -->
              <td 
                class="px-2 py-2 text-center border-r border-gray-200 whitespace-nowrap select-none transition-colors"
                :class="selectedDiaHighlight && hasPlantaoNoDia(row, selectedDiaHighlight) ? 'bg-amber-100/50' : ''"
              >
                <div class="flex items-center justify-center">
                  <span 
                    v-if="row.grade_id && row.grade_status !== 'Pendente'"
                    class="px-2 py-0.5 rounded text-[9.5px] font-bold border inline-flex items-center gap-1 shadow-2xs"
                    :class="{
                      'bg-emerald-100 text-emerald-800 border-emerald-300': row.grade_status === 'Publicada',
                      'bg-blue-100 text-blue-800 border-blue-300': row.grade_status === 'Enviada_Superior' || row.grade_status === 'Enviada',
                      'bg-rose-100 text-rose-800 border-rose-300': row.grade_status === 'Devolvida',
                      'bg-amber-100 text-amber-800 border-amber-300': row.grade_status === 'Aprovada',
                      'bg-gray-100 text-gray-700 border-gray-300': row.grade_status === 'Rascunho'
                    }"
                    :title="row.observacao ? `Obs: ${row.observacao}` : (row.grade_status === 'Publicada' ? 'Escala Homologada e Publicada pela DIVGP (Definitiva).' : 'Fluxo de aprovação em andamento')"
                  >
                    <span v-if="row.grade_status === 'Publicada'">🟢 Publicada (DIVGP)</span>
                    <span v-else-if="row.grade_status === 'Enviada_Superior' || row.grade_status === 'Enviada'">🔵 Enviada para Unidade</span>
                    <span v-else-if="row.grade_status === 'Devolvida'">🟠 Devolvida para Posto</span>
                    <span v-else-if="row.grade_status === 'Aprovada'">🟡 Aprovada</span>
                    <span v-else-if="row.grade_status === 'Rascunho'">⚪ Em Elaboração</span>
                  </span>
                  <span v-else class="text-[9.5px] text-gray-400 italic">
                    Sem Escala
                  </span>
                </div>
              </td>

              <!-- Actions column -->
              <td class="px-2 py-2 text-center border-gray-200 space-x-1 whitespace-nowrap">
                <!-- Ação 1: Supervisor de Posto (ou Admin) aprova para a Unidade -->
                <button 
                  v-if="row.grade_id && (row.grade_status === 'Rascunho' || row.grade_status === 'Devolvida') && (!isTopLevelForSelectedUnit || authStore.isAdmin)" 
                  @click="enviarSuperiorSingleGrade(row.grade_id)" 
                  class="p-1 text-blue-600 hover:bg-blue-50 rounded transition-colors inline-flex cursor-pointer"
                  title="Aprovar para Unidade (Supervisor finaliza e encaminha escala ao Chefe da Unidade)"
                >
                  <ArrowUpCircleIcon class="h-4 w-4" />
                </button>

                <!-- Ação 2: Chefe da Unidade (ou Admin) - Aprovar para DIVGP quando a escala foi submetida pelo posto -->
                <button 
                  v-if="row.grade_id && (row.grade_status === 'Enviada_Superior' || row.grade_status === 'Enviada' || (isTopLevelForSelectedUnit && row.grade_status !== 'Publicada'))" 
                  @click="publishSingleGrade(row.grade_id)" 
                  class="p-1 text-emerald-600 hover:bg-emerald-50 rounded transition-colors inline-flex cursor-pointer"
                  title="Aprovar para DIVGP (Chefe da Unidade homologa e envia a escala)"
                >
                  <CheckCircleIcon class="h-4 w-4" />
                </button>

                <!-- Ação 3: Chefe da Unidade (ou Admin) - Devolver para o Chefe do Posto corrigir -->
                <button 
                  v-if="row.grade_id && (row.grade_status === 'Enviada_Superior' || row.grade_status === 'Enviada') && (isTopLevelForSelectedUnit || authStore.isAdmin)" 
                  @click="devolverSingleGrade(row.grade_id)" 
                  class="p-1 text-amber-600 hover:bg-amber-50 rounded transition-colors inline-flex cursor-pointer"
                  title="Devolver para Correção do Supervisor do Posto"
                >
                  <ArrowUturnLeftIcon class="h-4 w-4" />
                </button>

                <!-- Admin Unlock / Reabrir button -->
                <button 
                  v-if="row.grade_id && row.grade_status === 'Publicada' && authStore.isAdmin" 
                  @click="reabrirGrade(row.grade_id)" 
                  class="p-1 text-amber-600 hover:bg-amber-50 rounded transition-colors inline-flex cursor-pointer"
                  title="Reabrir Escala (Retornar para Rascunho / Desbloquear)"
                >
                  <LockOpenIcon class="h-4 w-4" />
                </button>

                <!-- Edit / View button -->
                <button 
                  v-if="row.grade_status === 'Publicada' && !authStore.isAdmin" 
                  @click="openEditarGrade(row)" 
                  class="p-1 text-slate-500 hover:bg-slate-100 rounded transition-colors inline-flex cursor-pointer"
                  title="Visualizar Escala (Bloqueada para Edição - Publicada para DIVGP.)"
                >
                  <EyeIcon class="h-4 w-4" />
                </button>
                <button 
                  v-else 
                  @click="openEditarGrade(row)" 
                  class="p-1 text-paper-primary hover:bg-paper-primary/10 rounded transition-colors inline-flex cursor-pointer"
                  :title="row.grade_status === 'Publicada' ? 'Editar Escala (Admin)' : 'Editar Escala'"
                >
                  <PencilSquareIcon class="h-4 w-4" />
                </button>

                <!-- Delete button (only if not published or if admin) -->
                <button 
                  v-if="row.grade_id && (row.grade_status !== 'Publicada' || authStore.isAdmin)" 
                  @click="deleteGrade(row.grade_id)" 
                  class="p-1 text-paper-danger hover:bg-paper-danger/10 rounded transition-colors inline-flex cursor-pointer"
                  title="Excluir Escala"
                >
                  <TrashIcon class="h-4 w-4" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Footer Legend -->
      <div class="px-5 py-3 bg-gray-50/80 border-t border-gray-200 flex flex-wrap items-center justify-between gap-3 text-xs text-gray-600">
        <div class="flex flex-wrap items-center gap-3">
          <span class="font-bold text-gray-700 uppercase tracking-wider text-[11px]">Legendas:</span>
          <div class="flex items-center gap-1.5">
            <span class="inline-block w-5 py-0.5 rounded text-[10px] font-bold text-center bg-blue-100 text-blue-800">M</span>
            <span>Manhã</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="inline-block w-5 py-0.5 rounded text-[10px] font-bold text-center bg-amber-100 text-amber-800">T</span>
            <span>Tarde</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="inline-block w-5 py-0.5 rounded text-[10px] font-bold text-center bg-purple-100 text-purple-800">N</span>
            <span>Noite</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="inline-block w-5 py-0.5 rounded text-[10px] font-bold text-center bg-emerald-100 text-emerald-800">D</span>
            <span>Diurno</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="inline-block w-5 py-0.5 rounded text-[10px] font-bold text-center bg-rose-100 text-rose-700">FE</span>
            <span>Férias</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="inline-flex items-center justify-center w-5 py-0.5 rounded text-[9px] font-bold bg-teal-50 text-teal-700 border border-dashed border-teal-400">M</span>
            <span class="text-teal-800 font-medium">Plantão em Outra Unidade (Carga Dividida)</span>
          </div>
        </div>
        <div class="flex items-center gap-3 text-[11px] text-gray-500">
          <div class="flex items-center gap-1.5">
            <span class="inline-block w-3.5 h-3.5 bg-amber-100 border-l-2 border-l-amber-500 border border-amber-300 rounded-xs"></span>
            <span>Escalado no dia selecionado</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="inline-block w-3 h-3 bg-gray-100 border border-gray-300 rounded-xs"></span>
            <span>Fim de semana</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- VISÃO 2: CALENDÁRIO MENSAL COM PROFISSIONAIS ALOCADOS POR DIA -->
    <!-- ============================================================ -->
    <div v-else class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <!-- Calendar Header -->
      <div class="bg-paper-sidebar text-white px-5 py-3.5 flex flex-wrap justify-between items-center gap-3">
        <div class="flex items-center gap-2 flex-wrap">
          <div class="flex items-center gap-2">
            <CalendarIcon class="h-5 w-5 text-blue-200" />
            <h3 class="font-semibold text-sm">
              Visão Calendário · {{ getUnidadeNomeDisplay() }} · {{ mesesNomes[selectedMes - 1] }} / {{ selectedAno }}
            </h3>
          </div>
          <span class="text-xs bg-blue-500/30 text-blue-100 px-2.5 py-0.5 rounded-full font-medium">
            {{ sortedMatrixData.length }} colaborador(es) no filtro
          </span>
          <!-- Active filters chips -->
          <div v-if="activeFiltersList.length > 0" class="flex items-center gap-1.5 flex-wrap">
            <span 
              v-for="(f, fIdx) in activeFiltersList" 
              :key="fIdx"
              class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium bg-white/15 text-white border border-white/20 shadow-2xs"
            >
              <span class="text-blue-200 text-[10px] font-bold uppercase tracking-wider">{{ f.label }}:</span>
              <span class="font-semibold text-amber-300">{{ f.value }}</span>
            </span>
          </div>
        </div>

        <!-- Legenda rápida no topo do calendário -->
        <div class="flex items-center gap-2.5 text-xs text-blue-200">
          <span class="inline-flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-xs bg-blue-100 border border-blue-300 inline-block"></span> M</span>
          <span class="inline-flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-xs bg-amber-100 border border-amber-300 inline-block"></span> T</span>
          <span class="inline-flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-xs bg-purple-100 border border-purple-300 inline-block"></span> N</span>
          <span class="inline-flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-xs bg-emerald-100 border border-emerald-300 inline-block"></span> D</span>
          <span class="inline-flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-xs bg-rose-100 border border-rose-300 inline-block"></span> FE</span>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="p-16 text-center text-gray-500">
        <div class="flex flex-col items-center justify-center gap-3">
          <div class="w-10 h-10 border-4 border-paper-primary border-t-transparent rounded-full animate-spin"></div>
          <span class="text-sm font-medium">Carregando calendário de escalas...</span>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="sortedMatrixData.length === 0" class="p-16 text-center text-gray-500">
        <p class="font-semibold text-gray-700 text-base">Nenhum colaborador encontrado para os filtros selecionados.</p>
        <p class="text-xs text-gray-400 mt-1">Selecione uma unidade ou ajuste os filtros para ver a distribuição diária.</p>
      </div>

      <!-- Calendar Month Grid -->
      <div v-else class="p-4 sm:p-5">
        <!-- Dias da Semana Header (Dom - Sáb) -->
        <div class="grid grid-cols-7 gap-2 mb-2 notranslate" translate="no">
          <div 
            v-for="(nomeDia, dIdx) in diasSemanaNomes" 
            :key="dIdx"
            class="text-center py-2 text-xs font-bold uppercase tracking-wider rounded-lg notranslate"
            :class="(dIdx === 0 || dIdx === 6) ? 'bg-gray-100 text-gray-500' : 'bg-slate-50 text-paper-sidebar'"
            translate="no"
          >
            {{ nomeDia }}
          </div>
        </div>

        <!-- Grid de Células do Mês -->
        <div class="grid grid-cols-7 gap-2">
          <!-- Células vazias de offset antes do dia 1 -->
          <div 
            v-for="offset in calendarStartOffset" 
            :key="'offset-' + offset"
            class="min-h-[140px] bg-gray-50/50 rounded-xl border border-dashed border-gray-200/80 p-2 opacity-40 select-none"
          ></div>

          <!-- Células de cada dia do mês -->
          <div 
            v-for="cell in calendarDaysGrid" 
            :key="cell.dia"
            class="min-h-[140px] rounded-xl border p-2 flex flex-col transition-all duration-150 hover:shadow-md"
            :class="[
              cell.feriadoNome ? 'bg-rose-50/30 border-rose-200 ring-1 ring-rose-200/50' : 
              (cell.isWeekend ? 'bg-slate-50/70 border-gray-200' : 'bg-white border-gray-200 hover:border-paper-primary/40')
            ]"
          >
            <!-- Day Cell Header -->
            <div class="flex items-center justify-between pb-1.5 mb-1.5 border-b border-gray-100">
              <div class="flex items-center gap-1.5">
                <span 
                  class="font-black text-sm w-7 h-7 flex items-center justify-center rounded-lg"
                  :class="cell.feriadoNome ? 'bg-rose-500 text-white shadow-2xs' : (cell.isWeekend ? 'bg-gray-200 text-gray-700' : 'bg-paper-primary/10 text-paper-primary')"
                >
                  {{ cell.dia }}
                </span>
                <span 
                  v-if="cell.feriadoNome" 
                  class="text-[10px] font-bold text-rose-700 truncate max-w-[110px]"
                  :title="'Feriado: ' + cell.feriadoNome"
                >
                  {{ cell.feriadoNome }}
                </span>
              </div>

              <!-- Contagem de profissionais alocados no dia -->
              <span 
                class="text-[10.5px] font-bold px-1.5 py-0.5 rounded-full"
                :class="cell.alocados.length > 0 ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' : 'bg-gray-100 text-gray-400'"
                :title="`${cell.alocados.length} profissional(is) alocado(s) neste dia`"
              >
                {{ cell.alocados.length }}
              </span>
            </div>

            <!-- Lista de Profissionais Alocados no Dia -->
            <div class="flex-1 overflow-y-auto space-y-1 max-h-[170px] pr-0.5 scrollbar-thin">
              <template v-if="cell.alocados.length > 0">
                <div 
                  v-for="(alocado, aIdx) in cell.alocados.slice(0, 5)" 
                  :key="aIdx"
                  @click="openEditarGrade(alocado.colaborador)"
                  class="flex items-center gap-1.5 p-1 rounded-md text-[11px] hover:bg-paper-primary/10 transition-colors cursor-pointer border border-transparent hover:border-paper-primary/20 group"
                  :title="`${alocado.colaborador.nome} (${alocado.colaborador.cargo || 'Sem Cargo'}) - Turno: ${alocado.sigla} - Clique para abrir detalhes/editar`"
                >
                  <!-- Badge do Turno / Sigla -->
                  <span 
                    class="w-5 h-4.5 rounded text-[9.5px] font-black flex items-center justify-center shrink-0 uppercase shadow-2xs"
                    :class="alocado.is_outra_unidade 
                      ? 'border border-dashed border-teal-500 bg-teal-50 text-teal-800' 
                      : getSiglaBadgeClass(alocado.sigla)"
                  >
                    {{ alocado.sigla || 'P' }}
                  </span>

                  <!-- Nome do Colaborador e Cargo -->
                  <div class="truncate flex-1 min-w-0">
                    <p class="font-medium text-gray-800 text-[10.5px] leading-tight truncate group-hover:text-paper-primary">
                      {{ alocado.colaborador.nome }}
                    </p>
                    <p v-if="alocado.colaborador.cargo && alocado.colaborador.cargo !== '-'" class="text-[9px] text-gray-400 truncate leading-none mt-0.5">
                      {{ alocado.colaborador.cargo }}
                    </p>
                  </div>
                </div>

                <!-- Botão "Mais N profissionais" caso exceda 5 -->
                <button 
                  v-if="cell.alocados.length > 5"
                  @click="openCalendarDiaDetalhes(cell)"
                  class="w-full text-center py-1 text-[10.5px] font-semibold text-paper-primary hover:text-paper-primary-hover hover:bg-paper-primary/5 rounded border border-dashed border-paper-primary/30 transition-colors cursor-pointer"
                  title="Clique para ver todos os profissionais escalados neste dia"
                >
                  +{{ cell.alocados.length - 5 }} mais profissionais
                </button>
              </template>

              <!-- Sem profissionais alocados -->
              <div v-else class="h-full flex items-center justify-center text-[10.5px] text-gray-300 italic py-4">
                Nenhum escalado
              </div>
            </div>

            <!-- Botão Ver Todos no rodapé da célula se houver alocados -->
            <div v-if="cell.alocados.length > 0" class="pt-1 mt-1 border-t border-gray-100 flex justify-end">
              <button 
                type="button" 
                @click="openCalendarDiaDetalhes(cell)"
                class="text-[10px] text-gray-500 hover:text-paper-primary font-medium transition-colors cursor-pointer inline-flex items-center gap-0.5"
                title="Expandir lista completa de profissionais deste dia"
              >
                <span>Ver lista completa</span>
                <span>→</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Calendar Footer Legend -->
      <div class="px-5 py-3 bg-gray-50/80 border-t border-gray-200 flex flex-wrap items-center justify-between gap-3 text-xs text-gray-600">
        <div class="flex flex-wrap items-center gap-3">
          <span class="font-bold text-gray-700 uppercase tracking-wider text-[11px]">Legendas de Turno:</span>
          <div class="flex items-center gap-1.5">
            <span class="inline-block w-5 py-0.5 rounded text-[10px] font-bold text-center bg-blue-100 text-blue-800">M</span>
            <span>Manhã</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="inline-block w-5 py-0.5 rounded text-[10px] font-bold text-center bg-amber-100 text-amber-800">T</span>
            <span>Tarde</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="inline-block w-5 py-0.5 rounded text-[10px] font-bold text-center bg-purple-100 text-purple-800">N</span>
            <span>Noite</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="inline-block w-5 py-0.5 rounded text-[10px] font-bold text-center bg-emerald-100 text-emerald-800">D</span>
            <span>Diurno</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="inline-block w-5 py-0.5 rounded text-[10px] font-bold text-center bg-rose-100 text-rose-700">FE</span>
            <span>Férias</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="inline-flex items-center justify-center w-5 py-0.5 rounded text-[9px] font-bold bg-teal-50 text-teal-700 border border-dashed border-teal-400">EXT</span>
            <span class="text-teal-800 font-medium">Outra Unidade</span>
          </div>
        </div>
        <div class="text-[11px] text-gray-500">
          Dica: Clique no nome do colaborador ou em "Ver lista completa" para visualizar e editar os plantões.
        </div>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- MODAL DE DETALHES DE PROFISSIONAIS DO DIA NO CALENDÁRIO -->
    <!-- ============================================================ -->
    <div v-if="calendarDiaDetalhes" class="fixed inset-0 bg-black/50 backdrop-blur-xs flex items-center justify-center z-50 p-4 transition-all">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[85vh] overflow-hidden flex flex-col transform transition-all">
        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center bg-paper-sidebar text-white shrink-0">
          <div>
            <h3 class="text-lg font-bold flex items-center gap-2">
              <CalendarIcon class="h-5 w-5 text-blue-200" />
              <span>Dia {{ calendarDiaDetalhes.dia }} de {{ mesesNomes[selectedMes - 1] }} de {{ selectedAno }}</span>
              <span class="text-sm font-normal text-blue-200">({{ calendarDiaDetalhes.diaSemanaNome }})</span>
            </h3>
            <p v-if="calendarDiaDetalhes.feriadoNome" class="text-xs text-rose-300 font-bold mt-0.5">
              🎉 Feriado: {{ calendarDiaDetalhes.feriadoNome }}
            </p>
            <p v-else class="text-xs text-blue-200 mt-0.5">
              {{ getUnidadeNomeDisplay() }} · Total: {{ calendarDiaDetalhes.alocados.length }} profissional(is) alocado(s)
            </p>
          </div>
          <button 
            type="button" 
            @click="closeCalendarDiaDetalhes"
            class="text-gray-300 hover:text-white p-1 rounded-lg hover:bg-white/10 transition-colors cursor-pointer"
          >
            <XMarkIcon class="h-6 w-6" />
          </button>
        </div>

        <!-- Body: Lista Completa dos Colaboradores Alocados -->
        <div class="p-5 overflow-y-auto max-h-[60vh] space-y-2">
          <div 
            v-for="(alocado, idx) in calendarDiaDetalhes.alocados" 
            :key="idx"
            class="flex items-center justify-between p-3 rounded-xl border border-gray-200 hover:border-paper-primary/40 bg-gray-50/50 hover:bg-white transition-all shadow-2xs"
          >
            <div class="flex items-center gap-3">
              <!-- Badge da Sigla do Turno -->
              <span 
                class="w-8 h-8 rounded-lg text-xs font-black flex items-center justify-center uppercase shadow-xs shrink-0"
                :class="alocado.is_outra_unidade 
                  ? 'border-2 border-dashed border-teal-500 bg-teal-50 text-teal-800' 
                  : getSiglaBadgeClass(alocado.sigla)"
              >
                {{ alocado.sigla || 'P' }}
              </span>

              <div>
                <p class="font-bold text-gray-900 text-sm">
                  {{ alocado.colaborador.nome }}
                  <span v-if="alocado.colaborador.matricula" class="text-xs font-normal text-gray-500">
                    ({{ alocado.colaborador.matricula }})
                  </span>
                </p>
                <div class="flex items-center gap-2 text-xs text-gray-500 mt-0.5 flex-wrap">
                  <span v-if="alocado.colaborador.cargo && alocado.colaborador.cargo !== '-'" class="font-medium text-gray-700">
                    🏷️ {{ alocado.colaborador.cargo }}
                  </span>
                  <span v-if="alocado.colaborador.posto_nome" class="text-blue-700 font-medium">
                    📍 {{ alocado.colaborador.posto_nome }}
                  </span>
                  <span v-if="alocado.is_ferias" class="text-rose-600 font-bold bg-rose-50 px-1.5 py-0.2 rounded border border-rose-200">
                    🏖️ Férias
                  </span>
                  <span v-if="alocado.is_outra_unidade" class="text-teal-700 font-bold bg-teal-50 px-1.5 py-0.2 rounded border border-teal-200">
                    🌐 Outra Unidade
                  </span>
                </div>
              </div>
            </div>

            <!-- Ações -->
            <div class="flex items-center gap-2">
              <button 
                type="button" 
                @click="closeCalendarDiaDetalhes(); openEditarGrade(alocado.colaborador)"
                class="px-3 py-1.5 bg-paper-primary hover:bg-paper-primary-hover text-white rounded-lg text-xs font-semibold transition-all shadow-xs inline-flex items-center gap-1 cursor-pointer"
              >
                <PencilSquareIcon class="h-3.5 w-3.5" />
                <span>Ver / Editar Escala</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-6 py-3 border-t border-gray-200 bg-gray-50 flex justify-end shrink-0">
          <button 
            type="button" 
            @click="closeCalendarDiaDetalhes"
            class="px-4 py-2 bg-white hover:bg-gray-100 text-gray-700 border border-gray-300 rounded-lg text-sm font-medium transition-colors cursor-pointer"
          >
            Fechar
          </button>
        </div>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- MODAL 1: CRIAR / EDITAR ESCALA DO COLABORADOR -->
    <!-- ============================================================ -->
    <div v-if="showCriarModal" class="fixed inset-0 bg-black/50 backdrop-blur-xs flex items-center justify-center z-50 p-4 transition-all">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[92vh] overflow-hidden flex flex-col transform transition-all">
        <!-- Modal Header -->
        <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center bg-paper-sidebar text-white shrink-0">
          <div>
            <h3 class="text-lg font-bold">
              {{ (isEditingCollaborator || editingGradeId) ? 'Editar Escala do Colaborador' : 'Criar Nova Escala' }}
            </h3>
            <p class="text-xs text-blue-200">
              Período: {{ mesesNomes[criarForm.mes - 1] }} / {{ criarForm.ano }}
            </p>
          </div>
          <button @click="closeCriarModal" class="text-white hover:text-gray-300 text-xl font-bold p-1 cursor-pointer">&times;</button>
        </div>

        <!-- Modal Body -->
        <div ref="modalBodyRef" class="p-6 overflow-y-auto space-y-5 flex-1">
          <div v-if="modalError" class="bg-rose-50 border-2 border-rose-300 text-rose-800 p-4 rounded-xl text-sm font-semibold flex items-start justify-between gap-3 shadow-xs">
            <div class="flex items-start gap-2.5">
              <span class="text-rose-600 text-base leading-none mt-0.5">⚠️</span>
              <div>
                <p class="font-bold text-rose-900">Não foi possível salvar a escala:</p>
                <p class="text-xs text-rose-700 mt-0.5 font-normal">{{ modalError }}</p>
              </div>
            </div>
            <button type="button" @click="modalError = ''" class="text-rose-400 hover:text-rose-700 p-1 cursor-pointer">
              &times;
            </button>
          </div>

          <!-- Lock Banner if Published and non-admin -->
          <div 
            v-if="isGradeBloqueada" 
            class="p-3.5 bg-rose-50 rounded-xl border border-rose-200 text-xs text-rose-900 flex items-start gap-2.5 shadow-xs"
          >
            <LockClosedIcon class="h-5 w-5 text-rose-600 shrink-0 mt-0.5" />
            <div>
              <p class="font-bold text-rose-950">
                Escala Publicada para a DIVGP. (Bloqueada para Edição):
              </p>
              <p class="mt-0.5 text-rose-800">
                Esta escala já foi homologada e publicada para a Divisão de Gestão de Pessoas. O gerente da área não pode mais alterar os turnos ou excluir a escala. Caso seja necessário realizar alterações, solicite a reabertura à DIVGP. ou a um administrador do sistema.
              </p>
            </div>
          </div>

          <!-- Basic Data Selection -->
          <!-- Modo Edição: exibe TODOS os dados do colaborador, cargo, matrícula, vínculo e lotação informativos e bloqueados (somente leitura), sem permitir alteração indevida -->
          <div v-if="isEditingCollaborator || editingGradeId" class="bg-slate-50 border border-slate-200 rounded-xl p-4 shadow-xs">
            <div class="flex items-center justify-between border-b border-slate-200 pb-3 mb-3">
              <div class="flex items-center gap-3">
                <div class="w-11 h-11 rounded-full bg-paper-primary/10 text-paper-primary flex items-center justify-center font-bold text-base border border-paper-primary/20">
                  {{ (selectedFuncionarioObj?.nome || 'C').charAt(0) }}
                </div>
                <div>
                  <div class="flex items-center gap-2">
                    <h4 class="font-bold text-base text-gray-900 leading-tight">
                      {{ selectedFuncionarioObj?.nome }}
                    </h4>
                    <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-200 text-slate-700">
                      ID #{{ selectedFuncionarioObj?.id }}
                    </span>
                  </div>
                  <div class="flex flex-wrap items-center gap-2 mt-1 text-xs text-gray-600">
                    <span>SIAPE / Matrícula: <b class="font-mono text-gray-900">{{ selectedFuncionarioObj?.matricula }}</b></span>
                    <span>·</span>
                    <span>Vínculo: <b class="text-gray-900">{{ selectedFuncionarioObj?.vinculo?.nome || 'CLT/RJU' }}</b></span>
                    <span>·</span>
                    <span>Escala Padrão: <b class="text-purple-800 font-mono">{{ selectedFuncionarioObj?.escala?.sigla || selectedFuncionarioObj?.escala?.codigo || '-' }}</b></span>
                  </div>
                </div>
              </div>
              <div class="flex flex-col items-end gap-1">
                <span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-300 flex items-center gap-1 shadow-xs">
                  <span>🔒</span>
                  <span>Cadastro Protegido</span>
                </span>
                <span class="text-[10px] text-gray-400">Nome, Matrícula e Lotação fixos</span>
              </div>
            </div>

            <!-- Dados Detalhados de Lotação e Cargo (Bloqueados para Edição) -->
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 bg-white p-3 rounded-lg border border-slate-200/80 text-xs">
              <div>
                <span class="text-gray-400 block uppercase tracking-wider text-[10px] font-bold">Unidade / Lotação (UORG)</span>
                <span class="font-bold text-gray-800 mt-0.5 block truncate" :title="unidades.find(u => u.id === criarForm.unidade_id)?.nome">
                  🏛️ {{ unidades.find(u => u.id === criarForm.unidade_id)?.nome || 'Unidade ' + criarForm.unidade_id }}
                </span>
              </div>

              <div>
                <span class="text-gray-400 block uppercase tracking-wider text-[10px] font-bold">Posto de Serviço</span>
                <span class="font-bold text-gray-800 mt-0.5 block truncate">
                  📍 {{ todosPostos.find(p => p.id === criarForm.posto_id)?.nome || 'Geral (Todos)' }}
                </span>
              </div>

              <div>
                <span class="text-gray-400 block uppercase tracking-wider text-[10px] font-bold">Cargo Efetivo</span>
                <span class="font-bold text-blue-900 mt-0.5 block truncate" :title="selectedFuncionarioObj?.cargo?.nome">
                  💼 {{ selectedFuncionarioObj?.cargo?.nome || 'Não informado' }}
                </span>
              </div>

              <div>
                <span class="text-gray-400 block uppercase tracking-wider text-[10px] font-bold">Carga Horária Semanal</span>
                <span class="font-bold text-emerald-800 mt-0.5 block">
                  ⏱️ {{ selectedFuncionarioObj?.carga_horaria || selectedFuncionarioObj?.cargo?.carga_horaria || 40 }}h / semana
                </span>
              </div>
            </div>
          </div>

          <!-- Modo Criação Nova: permite selecionar Unidade, Posto e Colaborador -->
          <div v-else class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div class="form-group mb-0">
              <label class="form-label">Unidade <span class="text-red-500">*</span></label>
              <select 
                v-model="criarForm.unidade_id" 
                @change="onCriarUnidadeChange"
                class="form-control"
                required
              >
                <option v-for="u in unidadesDisponiveis" :key="u.id" :value="u.id">
                  {{ u.nome }} {{ u.sigla ? `(${u.sigla})` : '' }}
                </option>
              </select>
            </div>

            <div class="form-group mb-0">
              <label class="form-label">Posto de Serviço</label>
              <select 
                v-model="criarForm.posto_id" 
                @change="onCriarPostoChange"
                class="form-control"
              >
                <option :value="null">Geral (Todos)</option>
                <option v-for="p in todosPostos.filter(x => (x.uorg_id === criarForm.unidade_id || x.unidade_id === criarForm.unidade_id) && postoIdsComFuncionarios.has(x.id)).sort((a, b) => (a.nome || '').localeCompare(b.nome || '', 'pt-BR', { sensitivity: 'base' }))" :key="p.id" :value="p.id">
                  {{ p.nome }}
                </option>
              </select>
            </div>

            <div class="form-group mb-0 md:col-span-2">
              <label class="form-label">Colaborador <span class="text-red-500">*</span></label>
              <select 
                v-model="criarForm.funcionario_id" 
                @change="onFuncionarioChange"
                class="form-control"
                required
              >
                <option :value="0" disabled>Selecione o colaborador...</option>
                <option v-for="f in funcionariosDisponiveis" :key="f.id" :value="f.id">
                  {{ f.nome }} ({{ f.matricula }}) — {{ f.cargo?.nome || '' }}
                </option>
              </select>
              <p v-if="criarForm.unidade_id && funcionariosDisponiveis.length === 0" class="text-[10px] text-amber-600 mt-1">
                Nenhum colaborador lotado nesta unidade{{ criarForm.posto_id ? '/posto' : '' }}.
              </p>
              <p v-else-if="criarForm.unidade_id" class="text-[10px] text-gray-500 mt-1">
                {{ funcionariosDisponiveis.length }} colaborador(es) disponível(is)
              </p>
            </div>
          </div>

          <!-- Status da Escala (Comum aos dois modos) -->
          <div class="form-group mb-0">
            <label class="form-label flex items-center justify-between">
              <span>Status da Escala</span>
              <span class="text-[10px] text-emerald-700 font-semibold">DIVGP.</span>
            </label>
            <select 
              v-model="criarForm.status" 
              :disabled="isGradeBloqueada"
              class="form-control"
            >
              <option value="Rascunho">⚪ Em Elaboração</option>
              <option value="Enviada">🔵 Enviada (Aguardando chefia)</option>
              <option value="Aprovada">🟡 Aprovada (Validada)</option>
              <option value="Publicada">🟢 Publicada (Visível para DIVGP)</option>
            </select>
            <p class="text-[10px] text-gray-500 mt-1">
              * Ao cadastrar, a escala é salva inicialmente como <b class="text-gray-700">"Em Elaboração"</b> e só fica disponível para a DIVGP quando homologada como <b class="text-emerald-700">"Publicada"</b>.
            </p>
          </div>

          <!-- Multi-unit notice if collaborator is linked to 2+ units -->
          <div 
            v-if="selectedFuncionarioObj && selectedFuncionarioObj.lotacoes && selectedFuncionarioObj.lotacoes.length > 1" 
            class="p-3.5 bg-amber-50 rounded-xl border border-amber-200 text-xs text-amber-900 flex items-start gap-2.5 shadow-xs"
          >
            <span class="text-lg leading-none mt-0.5">⚡</span>
            <div>
              <p class="font-bold text-amber-950">
                Colaborador com Múltiplas Lotações / Carga Horária Dividida:
              </p>
              <p class="mt-0.5 text-amber-800">
                Atua em: <span class="font-semibold">{{ selectedFuncionarioObj.lotacoes.map((l: any) => l.unidade?.nome || 'Unidade').join(' e ') }}</span>.
                Você está configurando a escala para a unidade <span class="font-semibold text-amber-950 underline">{{ unidades.find(u => u.id === Number(criarForm.unidade_id))?.nome || 'selecionada' }}</span>.
              </p>
            </div>
          </div>

          <!-- Quick Fill Assistant -->
          <div v-if="!isGradeBloqueada" class="bg-gray-50 p-4 rounded-xl border border-gray-200 space-y-3">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <h4 class="text-xs font-bold uppercase text-paper-sidebar tracking-wider">
                Preenchimento Rápido / Código da Escala
              </h4>
              <span class="text-[11px] text-gray-500">Aplica o código da escala selecionado aos dias úteis</span>
            </div>

            <!-- Holiday Notice in Modal -->
            <div 
              v-if="Object.keys(feriadosMesCriarMap).length > 0" 
              class="p-2.5 bg-rose-50/80 rounded-lg border border-rose-200/80 text-[11px] text-rose-800 flex items-center gap-2"
            >
              <span class="font-bold">📅 Feriados em {{ mesesNomes[criarForm.mes - 1] }}:</span>
              <span>
                {{ Object.entries(feriadosMesCriarMap).map(([d, nome]) => `Dia ${d} (${nome})`).join(' · ') }}
              </span>
            </div>

            <div class="flex flex-wrap items-center gap-3">
              <select v-model="quickFillSigla" class="form-control w-auto min-w-[240px] text-sm">
                <option value="">Selecione a Escala...</option>
                <optgroup v-if="sortedEscalas.length > 0" label="Escalas Cadastradas">
                  <option v-for="e in sortedEscalas" :key="e.id" :value="e.sigla">
                    {{ e.sigla }}{{ e.descricao ? ' - ' + e.descricao : '' }} ({{ formatTime(e.inicio_jornada) }} às {{ formatTime(e.fim_jornada) }}){{ e.apenas_assistenciais ? ' · Assistencial' : '' }}
                  </option>
                </optgroup>
                <optgroup v-if="sortedLegendas.length > 0" label="Legendas / Turnos Gerais">
                  <option v-for="l in sortedLegendas" :key="l.id" :value="l.sigla">
                    {{ l.sigla }} - {{ l.descricao }}
                  </option>
                </optgroup>
              </select>

              <!-- Botão para Selecionar Dias Específicos -->
              <button 
                type="button" 
                @click="openSelecionarDiasModal" 
                class="px-3.5 py-1.5 bg-paper-primary hover:bg-paper-primary-hover text-white rounded-md text-xs font-semibold transition-colors cursor-pointer flex items-center gap-1.5 shadow-xs"
                title="Abrir tela de calendário para marcar os dias específicos onde este código será aplicado"
              >
                <CalendarIcon class="h-4 w-4" />
                <span>Selecionar Dias...</span>
              </button>

              <button 
                type="button" 
                @click="applyQuickFill('weekdays')" 
                class="px-3 py-1.5 bg-blue-50 text-blue-700 border border-blue-200 rounded-md text-xs font-medium hover:bg-blue-100 transition-colors cursor-pointer"
              >
                Preencher Dias Úteis (Seg-Sex)
              </button>
              <button 
                type="button" 
                @click="applyQuickFill('all')" 
                class="px-3 py-1.5 bg-gray-200 text-gray-700 rounded-md text-xs font-medium hover:bg-gray-300 transition-colors cursor-pointer"
              >
                Preencher Todos os Dias
              </button>

              <label class="inline-flex items-center gap-1.5 text-xs text-gray-700 font-medium cursor-pointer ml-1 select-none">
                <input 
                  type="checkbox" 
                  v-model="respeitarFeriadosDiarista" 
                  class="rounded text-paper-primary focus:ring-paper-primary h-4 w-4"
                />
                <span>Respeitar Feriados (Folga Diaristas)</span>
              </label>

              <button 
                type="button" 
                @click="clearAllDias" 
                class="px-3 py-1.5 bg-rose-50 text-rose-700 border border-rose-200 rounded-md text-xs font-medium hover:bg-rose-100 transition-colors ml-auto cursor-pointer"
              >
                Limpar Todos
              </button>
            </div>
          </div>

          <!-- Live Workload Balance Card -->
          <div 
            v-if="selectedFuncionarioObj" 
            class="p-4 rounded-xl border transition-all"
            :class="[
              computedHorasCriarModal.ultrapassou 
                ? 'bg-rose-50 border-rose-300 text-rose-950 shadow-xs' 
                : (computedHorasCriarModal.horasEscaladas === computedHorasCriarModal.tetoMensal 
                    ? 'bg-emerald-50 border-emerald-300 text-emerald-950 shadow-2xs' 
                    : 'bg-blue-50/70 border-blue-200 text-blue-950')
            ]"
          >
            <div class="flex flex-wrap items-center justify-between gap-3">
              <div>
                <span class="text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">
                  <span v-if="computedHorasCriarModal.ultrapassou" class="text-rose-700">⚠️ Carga Horária Excedida</span>
                  <span v-else-if="computedHorasCriarModal.horasEscaladas === computedHorasCriarModal.tetoMensal" class="text-emerald-700">🟢 Carga Horária 100% Preenchida</span>
                  <span v-else class="text-blue-800">⚖️ Acompanhamento de Carga Horária (Tempo Real)</span>
                </span>
                <div class="text-2xl font-extrabold font-mono mt-0.5 flex items-baseline gap-2">
                  <span :class="computedHorasCriarModal.ultrapassou ? 'text-rose-700' : (computedHorasCriarModal.horasEscaladas === computedHorasCriarModal.tetoMensal ? 'text-emerald-700' : 'text-paper-sidebar')">
                    {{ computedHorasCriarModal.horasEscaladas }}h
                  </span>
                  <span class="text-xs font-normal text-gray-500">
                    / limite mensal de <b>{{ computedHorasCriarModal.tetoMensal }}h</b> (Cargo: {{ selectedFuncionarioObj?.cargo?.nome || 'Colaborador' }} - {{ computedHorasCriarModal.chSemanal }}h/sem)
                  </span>
                </div>
              </div>

              <div class="text-right">
                <span 
                  v-if="computedHorasCriarModal.ultrapassou" 
                  class="px-3 py-1 rounded-lg text-xs font-bold bg-rose-600 text-white shadow-xs inline-block animate-pulse"
                >
                  Ultrapassou em +{{ computedHorasCriarModal.horasExcedentes }}h!
                </span>
                <span 
                  v-else-if="computedHorasCriarModal.saldoRestante > 0" 
                  class="text-xs font-bold text-blue-800 bg-blue-100/80 px-2.5 py-1 rounded-lg inline-block"
                >
                  Faltam {{ computedHorasCriarModal.saldoRestante }}h para completar
                </span>
                <span 
                  v-else 
                  class="px-2.5 py-1 rounded-lg text-xs font-bold bg-emerald-600 text-white inline-block shadow-2xs"
                >
                  ✓ Carga Ideal Completa
                </span>
              </div>
            </div>

            <!-- Progress Bar -->
            <div class="w-full bg-gray-200 rounded-full h-2.5 mt-3 overflow-hidden">
              <div 
                class="h-2.5 rounded-full transition-all duration-300"
                :class="[
                  computedHorasCriarModal.ultrapassou ? 'bg-rose-600' : 
                  (computedHorasCriarModal.horasEscaladas === computedHorasCriarModal.tetoMensal ? 'bg-emerald-600' : 'bg-blue-600')
                ]"
                :style="{ width: computedHorasCriarModal.porcentagemAlocada + '%' }"
              ></div>
            </div>

            <p v-if="computedHorasCriarModal.ultrapassou" class="text-xs text-rose-700 font-semibold mt-2.5 flex items-center gap-1.5">
              <span>Aviso:</span> A escala excede a carga horária contratual mensal permitida. Reduza a quantidade de turnos para não ultrapassar ou habilite a autorização de horas adicionais.
            </p>
          </div>

          <!-- Day by day matrix editor -->
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <label class="form-label mb-0 flex items-center gap-2">
                <span class="font-bold text-sm text-gray-800">Alocação Diária (Dias 1 a {{ totalDiasMesCriar }})</span>
                <span class="text-xs font-normal text-gray-500">Mês de {{ mesesNomes[criarForm.mes - 1] }} / {{ criarForm.ano }}</span>
              </label>
              <span v-if="!isGradeBloqueada" class="text-xs text-paper-primary font-medium">Selecione ou altere o código em cada dia</span>
              <span v-else class="text-xs text-amber-700 font-semibold bg-amber-50 px-2 py-0.5 rounded border border-amber-200">Modo Leitura (Bloqueada)</span>
            </div>

            <!-- Grade em Blocos de Dias para Atualização Direta -->
            <div class="grid grid-cols-4 sm:grid-cols-7 md:grid-cols-10 gap-2">
              <div 
                v-for="d in criarDias" 
                :key="'card-dia-' + d.dia"
                class="p-2 rounded-lg border text-center transition-all"
                :class="[
                  isWeekendInMes(d.dia, criarForm.mes, criarForm.ano) 
                    ? 'bg-gray-100/90 border-gray-300' 
                    : 'bg-white border-gray-200 hover:border-paper-primary',
                  d.legenda_sigla ? 'border-paper-primary/40 shadow-xs' : ''
                ]"
              >
                <div class="flex justify-between items-center text-[10px] text-gray-500 font-semibold mb-1">
                  <span class="font-bold text-gray-700">Dia {{ d.dia }}</span>
                  <span :class="feriadosMesCriarMap[d.dia] ? 'text-rose-600 font-bold' : ''">
                    {{ feriadosMesCriarMap[d.dia] ? 'FER' : getDiaSemanaSiglaMes(d.dia, criarForm.mes, criarForm.ano) }}
                  </span>
                </div>
                <select 
                  v-model="d.legenda_sigla" 
                  :disabled="isGradeBloqueada"
                  :class="[
                    isGradeBloqueada ? 'bg-gray-50 text-gray-500 cursor-not-allowed' : 'bg-white',
                    d.legenda_sigla ? 'font-bold text-paper-sidebar border-paper-primary' : 'text-gray-400'
                  ]"
                  class="w-full text-center text-xs uppercase rounded py-1 px-0.5 border border-gray-200 focus:border-paper-primary focus:ring-1 focus:ring-paper-primary cursor-pointer transition-colors"
                >
                  <option value="">-</option>
                  <!-- Escalas Cadastradas -->
                  <optgroup v-if="sortedEscalas.length > 0" label="Escalas Cadastradas">
                    <option v-for="e in sortedEscalas" :key="e.id" :value="e.sigla">
                      {{ e.sigla }}{{ e.descricao ? ' - ' + e.descricao : '' }}
                    </option>
                  </optgroup>
                  <!-- Legendas de Folgas / Afastamentos -->
                  <optgroup label="Folgas e Afastamentos">
                    <option value="A">A - Afastamento</option>
                    <option value="F">F - Folga</option>
                    <option value="FE">FE - Férias</option>
                    <option value="FJ">FJ - Falta Justificada</option>
                    <option value="FR">FR - Feriado</option>
                    <option value="LM">LM - Licença Médica</option>
                    <option value="LP">LP - Licença Prêmio</option>
                  </optgroup>
                </select>
              </div>
            </div>
          </div>

          <!-- Observações -->
          <div class="form-group mb-0">
            <label class="form-label">Observações</label>
            <textarea 
              v-model="criarForm.observacao" 
              rows="2" 
              :disabled="isGradeBloqueada"
              :class="[isGradeBloqueada ? 'bg-gray-50 cursor-not-allowed' : '']"
              placeholder="Anotações sobre plantões, trocas ou orientações da chefia..."
              class="form-control text-sm"
            ></textarea>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="px-6 py-4 border-t border-gray-200 bg-gray-50 flex justify-between items-center gap-3 shrink-0">
          <div>
            <!-- Admin unlock button if editing a published grade -->
            <button 
              v-if="editingGradeId && criarForm.status === 'Publicada' && authStore.isAdmin"
              type="button" 
              @click="reabrirGrade(editingGradeId)" 
              class="px-3.5 py-2 bg-amber-100 hover:bg-amber-200 text-amber-900 rounded-lg text-xs font-bold transition-colors flex items-center gap-1.5 cursor-pointer shadow-xs"
            >
              <LockOpenIcon class="h-4 w-4 text-amber-700" />
              <span>Reabrir Escala (Desbloquear)</span>
            </button>
          </div>
          <div class="flex items-center gap-3">
            <button 
              type="button" 
              @click="closeCriarModal" 
              class="px-4 py-2 text-sm text-paper-text hover:bg-gray-200 rounded-lg transition-colors cursor-pointer"
            >
              {{ isGradeBloqueada ? 'Fechar' : 'Cancelar' }}
            </button>
            <button 
              v-if="!isGradeBloqueada"
              type="button" 
              @click="saveCriarGrade" 
              :disabled="saving" 
              class="bg-paper-primary hover:bg-paper-primary-hover text-white px-5 py-2 rounded-lg text-sm font-medium transition-colors shadow-sm cursor-pointer"
            >
              {{ saving ? 'Salvando...' : 'Salvar Escala' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- MODAL 2: COPIAR ESCALA ENTRE MESES / COLABORADORES -->
    <!-- ============================================================ -->
    <div v-if="showCopiarModal" class="fixed inset-0 bg-black/50 backdrop-blur-xs flex items-center justify-center z-50 p-4 transition-all">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-4xl overflow-hidden flex flex-col transform transition-all max-h-[90vh]">
        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center bg-paper-sidebar text-white">
          <div>
            <h3 class="text-lg font-bold">Copiar Escala Mensal</h3>
            <p class="text-xs text-blue-200">
              Copie escalas dos colaboradores filtrados para o mês seguinte (mantendo cada colaborador no seu posto de serviço)
            </p>
          </div>
          <button @click="closeCopiarModal" class="text-white hover:text-gray-300 text-xl font-bold p-1 cursor-pointer">&times;</button>
        </div>

        <!-- Body -->
        <div class="p-6 space-y-4 overflow-y-auto">
          <div v-if="copiarError" class="bg-paper-danger/10 text-paper-danger p-3 rounded-lg text-sm">
            {{ copiarError }}
          </div>

          <!-- Período e Unidade: Origem e Destino -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Origem -->
            <div class="p-3.5 bg-blue-50/70 rounded-xl border border-blue-200/70 space-y-2.5">
              <div class="flex items-center justify-between">
                <span class="text-xs font-bold uppercase text-paper-primary tracking-wider flex items-center gap-1.5">
                  <span>📅 Origem (De onde copiar)</span>
                </span>
                <span class="text-[11px] text-paper-primary font-semibold">
                  {{ mesesNomes[copiarForm.source_mes - 1] }} / {{ copiarForm.source_ano }}
                </span>
              </div>
              <div class="grid grid-cols-2 gap-2">
                <div>
                  <label class="form-label text-[11px] mb-1">Mês Origem</label>
                  <select v-model="copiarForm.source_mes" @change="carregarFuncionariosDestinoComGrade" class="form-control text-xs py-1.5">
                    <option v-for="(nome, idx) in mesesNomes" :key="idx + 1" :value="idx + 1">{{ nome }}</option>
                  </select>
                </div>
                <div>
                  <label class="form-label text-[11px] mb-1">Ano Origem</label>
                  <select v-model="copiarForm.source_ano" @change="carregarFuncionariosDestinoComGrade" class="form-control text-xs py-1.5">
                    <option v-for="ano in anosDisponiveis" :key="ano" :value="ano">{{ ano }}</option>
                  </select>
                </div>
              </div>
              <div>
                <label class="form-label text-[11px] mb-1">Unidade Origem</label>
                <select v-model="copiarForm.source_unidade_id" class="form-control text-xs py-1.5">
                  <option v-for="u in unidadesDisponiveis" :key="u.id" :value="u.id">{{ u.nome }} {{ u.sigla ? `(${u.sigla})` : '' }}</option>
                </select>
              </div>
            </div>

            <!-- Destino -->
            <div class="p-3.5 bg-emerald-50/70 rounded-xl border border-emerald-200/70 space-y-2.5">
              <div class="flex items-center justify-between">
                <span class="text-xs font-bold uppercase text-emerald-800 tracking-wider flex items-center gap-1.5">
                  <span>🎯 Destino (Para qual mês aplicar)</span>
                </span>
                <span class="text-[11px] text-emerald-800 font-semibold">
                  {{ mesesNomes[copiarForm.target_mes - 1] }} / {{ copiarForm.target_ano }}
                </span>
              </div>
              <div class="grid grid-cols-2 gap-2">
                <div>
                  <label class="form-label text-[11px] mb-1">Mês Alvo</label>
                  <select v-model="copiarForm.target_mes" class="form-control text-xs py-1.5">
                    <option v-for="(nome, idx) in mesesNomes" :key="idx + 1" :value="idx + 1">{{ nome }}</option>
                  </select>
                </div>
                <div>
                  <label class="form-label text-[11px] mb-1">Ano Alvo</label>
                  <select v-model="copiarForm.target_ano" class="form-control text-xs py-1.5">
                    <option v-for="ano in anosDisponiveis" :key="ano" :value="ano">{{ ano }}</option>
                  </select>
                </div>
              </div>
              <div class="grid grid-cols-2 gap-2">
                <div>
                  <label class="form-label text-[11px] mb-1">Unidade Alvo</label>
                  <select v-model="copiarForm.target_unidade_id" class="form-control text-xs py-1.5">
                    <option v-for="u in unidadesDisponiveis" :key="u.id" :value="u.id">{{ u.nome }} {{ u.sigla ? `(${u.sigla})` : '' }}</option>
                  </select>
                </div>
                <div>
                  <label class="form-label text-[11px] mb-1">Posto de Serviço</label>
                  <select v-model="copiarForm.target_posto_id" class="form-control text-xs py-1.5">
                    <option :value="null">Geral (Manter de Cada Um)</option>
                    <option v-for="p in postosDaUnidadeAlvo" :key="p.id" :value="p.id">
                      {{ p.nome }}
                    </option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <!-- Modos de seleção e filtros rápidos -->
          <div class="p-3 bg-gray-50 rounded-xl border border-gray-200 space-y-3">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <span class="text-xs font-bold uppercase text-gray-700 tracking-wider">
                Colaboradores para Cópia (De Colaborador para o Mesmo Colaborador)
              </span>
              <div class="flex items-center gap-2">
                <button
                  type="button"
                  @click="selecionarTodosFiltradosOrigem"
                  class="text-xs px-2.5 py-1 bg-white border border-gray-300 hover:bg-gray-100 rounded-md font-semibold text-paper-sidebar shadow-2xs"
                  title="Selecionar todos os colaboradores filtrados da escala"
                >
                  ✓ Selecionar Todos
                </button>
                <button
                  type="button"
                  @click="copiarForm.source_func_ids = []"
                  class="text-xs px-2.5 py-1 bg-white border border-gray-300 hover:bg-gray-100 rounded-md font-semibold text-gray-600 shadow-2xs"
                  title="Desmarcar todos para escolher de um por um"
                >
                  ✕ De um por um (Limpar)
                </button>
              </div>
            </div>

            <!-- Pesquisa de colaborador -->
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-2.5 flex items-center pointer-events-none text-gray-400">
                <MagnifyingGlassIcon class="h-4 w-4" />
              </div>
              <input
                v-model="searchDestinoNome"
                type="text"
                placeholder="Filtrar colaboradores por nome, matrícula, cargo ou posto..."
                class="form-control pl-8.5 pr-8 text-xs py-1.5 bg-white"
              />
              <button
                v-if="searchDestinoNome"
                type="button"
                @click="searchDestinoNome = ''"
                class="absolute inset-y-0 right-0 pr-2.5 flex items-center text-gray-400 hover:text-gray-600"
                title="Limpar pesquisa"
              >
                <XMarkIcon class="h-4 w-4" />
              </button>
            </div>

            <!-- Lista de Colaboradores com Status no Mês Destino -->
            <div class="border border-gray-200 rounded-lg bg-white overflow-hidden shadow-2xs">
              <div class="bg-gray-100/80 border-b border-gray-200 px-3 py-2 flex items-center justify-between text-xs font-semibold text-gray-700">
                <label class="flex items-center gap-2 cursor-pointer select-none">
                  <input
                    type="checkbox"
                    :checked="allOrigemFiltradosSelected"
                    @change="toggleSelectAllOrigem"
                    class="rounded text-paper-primary focus:ring-paper-primary h-4 w-4 cursor-pointer"
                  />
                  <span>{{ searchDestinoNome ? 'Selecionar filtrados na lista' : 'Todos os colaboradores com escala na origem' }}</span>
                </label>
                <span class="text-[11px] text-paper-primary font-bold">
                  {{ copiarForm.source_func_ids.length }} de {{ listaOrigemFiltradaParaCopia.length }} selecionado(s)
                </span>
              </div>

              <div class="max-h-60 overflow-y-auto p-2 space-y-1 divide-y divide-gray-100">
                <div v-if="loadingTargetGrades" class="text-center py-6 text-xs text-gray-400 flex items-center justify-center gap-2">
                  <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-paper-primary"></div>
                  <span>Verificando situação das escalas para {{ mesesNomes[copiarForm.target_mes - 1] }}/{{ copiarForm.target_ano }}...</span>
                </div>
                <div v-else-if="listaOrigemFiltradaParaCopia.length === 0" class="text-center py-6 text-xs text-gray-500">
                  <p class="font-medium text-gray-700">Nenhum colaborador com escala pronta na origem encontrado com os filtros atuais.</p>
                  <p class="text-[11px] text-gray-400 mt-1">Verifique os filtros da tela ou mude a Unidade/Mês de origem.</p>
                </div>
                <label 
                  v-else
                  v-for="f in listaOrigemFiltradaParaCopia" 
                  :key="f.funcionario_id" 
                  class="flex items-center justify-between p-2 hover:bg-gray-50 rounded cursor-pointer text-xs transition-colors"
                  :class="{ 'opacity-60 bg-gray-50': targetFuncionariosComGrade.has(Number(f.funcionario_id)) }"
                >
                  <div class="flex items-center gap-2.5">
                    <input 
                      type="checkbox" 
                      :value="f.funcionario_id" 
                      v-model="copiarForm.source_func_ids" 
                      class="rounded text-paper-primary focus:ring-paper-primary h-4 w-4 cursor-pointer"
                    />
                    <div>
                      <div class="font-semibold text-gray-900 flex items-center gap-1.5">
                        <span>{{ f.nome }}</span>
                        <span class="text-[11px] font-normal text-gray-500">({{ f.matricula }})</span>
                      </div>
                      <div class="text-[11px] text-gray-500 flex items-center gap-2 mt-0.5">
                        <span class="font-medium text-paper-sidebar">{{ f.cargo || '-' }}</span>
                        <span>•</span>
                        <span>Posto: <strong class="text-gray-700">{{ f.posto_nome || 'Geral' }}</strong></span>
                      </div>
                    </div>
                  </div>

                  <!-- Badge de status no mês destino -->
                  <div>
                    <span 
                      v-if="targetFuncionariosComGrade.has(Number(f.funcionario_id))"
                      class="px-2 py-0.5 text-[10px] font-semibold bg-amber-100 text-amber-800 border border-amber-200 rounded-full"
                      title="Este colaborador já possui escala no mês de destino (será substituída ao copiar)"
                    >
                      Já tem escala em {{ mesesNomes[copiarForm.target_mes - 1] }}
                    </span>
                    <span 
                      v-else
                      class="px-2 py-0.5 text-[10px] font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200 rounded-full"
                    >
                      Disponível para copiar
                    </span>
                  </div>
                </label>
              </div>
            </div>

            <div class="flex items-center justify-between text-[11px] text-gray-500 px-1">
              <span>
                {{ copiarForm.source_func_ids.length }} colaborador(es) selecionado(s) para copiar de 
                <strong>{{ mesesNomes[copiarForm.source_mes - 1] }}/{{ copiarForm.source_ano }}</strong> 
                para 
                <strong>{{ mesesNomes[copiarForm.target_mes - 1] }}/{{ copiarForm.target_ano }}</strong>.
              </span>
              <button 
                v-if="copiarForm.source_func_ids.length > 0" 
                type="button" 
                @click="copiarForm.source_func_ids = []"
                class="text-red-600 hover:underline font-medium"
              >
                Limpar seleção
              </button>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-6 py-4 border-t border-gray-200 bg-gray-50 flex justify-between items-center">
          <div class="text-xs text-gray-600 flex items-center gap-1.5">
            <span class="text-amber-500 font-bold">ℹ️</span>
            <span>A cópia mantém o mesmo posto. <strong>Férias, feriados e afastamentos não são copiados</strong>, sendo respeitadas as folgas e o calendário do mês de destino.</span>
          </div>
          <div class="flex items-center gap-3">
            <button 
              type="button" 
              @click="closeCopiarModal" 
              class="px-4 py-2 text-sm text-paper-text hover:bg-gray-200 rounded-lg transition-colors cursor-pointer"
            >
              Cancelar
            </button>
            <button 
              type="button" 
              @click="executeCopiarGrade" 
              :disabled="copiando || copiarForm.source_func_ids.length === 0" 
              class="bg-paper-primary hover:bg-paper-primary-hover text-white px-5 py-2 rounded-lg text-sm font-semibold transition-colors shadow-sm disabled:opacity-50 flex items-center gap-2 cursor-pointer"
            >
              <DocumentDuplicateIcon class="h-4 w-4" />
              <span>{{ copiando ? 'Copiando Escalas...' : `Copiar ${copiarForm.source_func_ids.length} Escala(s)` }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ========================================== -->
    <!-- MODAL 3: SELECIONAR DIAS PARA CÓDIGO/SIGLA -->
    <!-- ========================================== -->
    <div 
      v-if="showSelecionarDiasModal" 
      class="fixed inset-0 z-60 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto"
      @click.self="closeSelecionarDiasModal"
    >
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl border border-gray-200 overflow-hidden transform transition-all my-8 animate-in fade-in zoom-in-95 duration-150">
        <!-- Header -->
        <div class="bg-paper-sidebar text-white px-6 py-4 flex items-center justify-between">
          <div class="flex items-center gap-2.5">
            <div class="p-2 bg-white/10 rounded-lg">
              <CalendarIcon class="h-5 w-5 text-paper-primary" />
            </div>
            <div>
              <h3 class="font-bold text-base">Selecionar Dias para Preenchimento</h3>
              <p class="text-xs text-gray-300">
                Mês de {{ mesesNomes[criarForm.mes - 1] }} / {{ criarForm.ano }} · Escala Selecionada: <span class="text-amber-300 font-bold font-mono bg-white/10 px-1.5 py-0.5 rounded">{{ quickFillSigla }}</span>
              </p>
            </div>
          </div>
          <button 
            @click="closeSelecionarDiasModal" 
            class="text-gray-300 hover:text-white p-1 rounded-lg hover:bg-white/10 transition-colors"
          >
            <XMarkIcon class="h-5 w-5" />
          </button>
        </div>

        <!-- Body -->
        <div class="p-6 space-y-5">
          <!-- Atalhos rápidos de seleção -->
          <div class="flex flex-wrap items-center justify-between gap-2 p-3 bg-gray-50 rounded-xl border border-gray-200">
            <span class="text-xs font-semibold text-gray-700 uppercase">Seleção Rápida:</span>
            <div class="flex flex-wrap items-center gap-1.5">
              <button 
                type="button" 
                @click="selectAllDiasModal"
                class="px-2.5 py-1 text-xs font-medium bg-white border border-gray-300 rounded hover:bg-gray-100 transition-colors"
              >
                Todos os Dias (1 a {{ totalDiasMesCriar }})
              </button>
              <button 
                type="button" 
                @click="selectWeekdaysModal"
                class="px-2.5 py-1 text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200 rounded hover:bg-blue-100 transition-colors"
              >
                Dias Úteis (Seg-Sex)
              </button>
              <button 
                type="button" 
                @click="selectWeekendsModal"
                class="px-2.5 py-1 text-xs font-medium bg-purple-50 text-purple-700 border border-purple-200 rounded hover:bg-purple-100 transition-colors"
              >
                Fins de Semana (Sáb-Dom)
              </button>
              <button 
                type="button" 
                @click="clearSelectionModal"
                class="px-2.5 py-1 text-xs font-medium text-rose-600 hover:bg-rose-50 border border-transparent hover:border-rose-200 rounded transition-colors"
              >
                Limpar Seleção
              </button>
            </div>
          </div>

          <!-- Grade de Dias Interativa -->
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-bold uppercase text-paper-sidebar">Clique nos dias desejados para marcar/desmarcar:</span>
              <span class="text-xs font-bold text-paper-primary">
                {{ selectedDiasParaPreenchimento.length }} dia(s) selecionado(s)
              </span>
            </div>

            <div class="grid grid-cols-4 sm:grid-cols-7 gap-2">
              <button 
                type="button"
                v-for="d in totalDiasMesCriar" 
                :key="d"
                @click="toggleDiaSelecao(d)"
                class="p-2 rounded-xl border text-center transition-all cursor-pointer flex flex-col items-center justify-center relative select-none"
                :class="[
                  selectedDiasParaPreenchimento.includes(d)
                    ? 'bg-paper-primary text-white border-paper-primary shadow-sm scale-[1.02] ring-2 ring-paper-primary/30 font-bold'
                    : (isWeekendInMes(d, criarForm.mes, criarForm.ano)
                        ? 'bg-gray-100 border-gray-200 text-gray-700 hover:bg-gray-200/80'
                        : 'bg-white border-gray-200 text-gray-800 hover:bg-blue-50/50 hover:border-blue-300')
                ]"
              >
                <!-- Badge de Feriado se houver -->
                <span 
                  v-if="feriadosMesCriarMap[d]" 
                  class="absolute top-1 right-1 w-2 h-2 rounded-full bg-rose-500"
                  :title="`Feriado: ${feriadosMesCriarMap[d]}`"
                ></span>

                <span class="text-base font-extrabold font-mono">{{ d }}</span>
                <span 
                  class="text-[10px] uppercase font-semibold"
                  :class="selectedDiasParaPreenchimento.includes(d) ? 'text-white/90' : 'text-gray-500'"
                >
                  {{ getDiaSemanaSiglaMes(d, criarForm.mes, criarForm.ano) }}
                </span>

                <!-- Sigla atual no dia -->
                <span 
                  v-if="criarDias[d - 1]?.legenda_sigla" 
                  class="mt-1 text-[9px] px-1 rounded truncate max-w-[45px]"
                  :class="selectedDiasParaPreenchimento.includes(d) ? 'bg-white/20 text-white' : 'bg-gray-200 text-gray-700 font-mono'"
                >
                  {{ criarDias[d - 1].legenda_sigla }}
                </span>
              </button>
            </div>
          </div>

          <!-- Dica/Resumo -->
          <div class="text-xs text-gray-500 bg-blue-50/60 p-3 rounded-lg border border-blue-100 flex items-start gap-2">
            <span class="text-blue-600 font-bold">ℹ️</span>
            <span>
              Ao confirmar, o código <b class="text-paper-sidebar">{{ quickFillSigla }}</b> será aplicado em todos os <b>{{ selectedDiasParaPreenchimento.length }}</b> dia(s) selecionados acima. Os demais dias permanecerão inalterados.
            </span>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-6 py-4 border-t border-gray-200 bg-gray-50 flex items-center justify-between">
          <div class="text-xs text-gray-500">
            Total selecionado: <b>{{ selectedDiasParaPreenchimento.length }}</b> de {{ totalDiasMesCriar }} dias
          </div>
          <div class="flex items-center gap-3">
            <button 
              type="button" 
              @click="closeSelecionarDiasModal" 
              class="px-4 py-2 text-sm text-paper-text hover:bg-gray-200 rounded-lg transition-colors cursor-pointer"
            >
              Cancelar
            </button>
            <button 
              type="button" 
              @click="aplicarEscalaDiasSelecionados" 
              :disabled="selectedDiasParaPreenchimento.length === 0"
              class="bg-paper-primary hover:bg-paper-primary-hover text-white px-5 py-2 rounded-lg text-sm font-semibold transition-colors shadow-sm disabled:opacity-50 flex items-center gap-2 cursor-pointer"
            >
              <CheckCircleIcon class="h-4 w-4" />
              <span>Aplicar aos {{ selectedDiasParaPreenchimento.length }} Dias</span>
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue';
import { 
  CalendarDaysIcon, 
  DocumentDuplicateIcon, 
  PlusIcon, 
  UserGroupIcon, 
  SunIcon, 
  ArrowsRightLeftIcon, 
  PencilSquareIcon, 
  TrashIcon,
  CheckCircleIcon,
  MegaphoneIcon,
  LockClosedIcon,
  LockOpenIcon,
  EyeIcon,
  MagnifyingGlassIcon,
  XMarkIcon,
  ArrowUpCircleIcon,
  ArrowUturnLeftIcon,
  CalendarIcon,
  TableCellsIcon
} from '@heroicons/vue/24/outline';

import api from '../services/api';
import gradeService, { ColaboradorGradeRow, GradeIndicators } from '../services/gradeService';
import gerenciaService, { UserScopeResponse } from '../services/gerenciaService';
import { useAuthStore } from '../stores/auth';
import { useSearchFilterState } from '../composables/useSearchFilterState';

const authStore = useAuthStore();
const userScope = ref<UserScopeResponse | null>(null);

// ==========================================
// Constantes & Nomes dos Meses
// ==========================================
const mesesNomes = [
  'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
];
const diasSemanaNomes = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
const anosDisponiveis = [2024, 2025, 2026, 2027, 2028];

// ==========================================
// Estado Principal de Filtros & Visualização
// ==========================================
const currentDate = new Date();
const selectedMes = ref<number>(currentDate.getMonth() + 1); // 1-12
const selectedAno = ref<number>(currentDate.getFullYear());
const selectedUnidadeId = ref<number | undefined>(undefined);
const incluirSubordinadas = ref<boolean>(true);
const selectedCargoId = ref<number | undefined>(undefined);
const selectedPostoId = ref<number | undefined>(undefined);
const selectedStatus = ref<string>('Todos');
const searchTerm = ref<string>('');

// Modo de visualização: 'tabela' (grade matricial mensal) ou 'calendario' (calendário mensal por dia)
const viewMode = ref<'tabela' | 'calendario'>('tabela');

// Persistência automática do status da última pesquisa/filtro
const { clearSavedState: clearSavedGradeFilters } = useSearchFilterState('grade', {
  selectedMes,
  selectedAno,
  selectedUnidadeId,
  incluirSubordinadas,
  selectedCargoId,
  selectedPostoId,
  selectedStatus,
  searchTerm
});

const loading = ref<boolean>(false);
const matrixData = ref<ColaboradorGradeRow[]>([]);
const indicators = reactive<GradeIndicators>({
  total_colaboradores: 0,
  total_ferias: 0,
  total_multiplas_lotacoes: 0
});

// Ordenação da grade: 'cargo_escala' (Cargo -> Cód. Escala -> Turnos dos dias -> Nome), 'cargo', 'escala', 'dias_alocados', 'nome', 'horas' ou dia específico (ex: 'dia_10')
const sortColumn = ref<string>('cargo_escala');
const sortDirection = ref<'asc' | 'desc'>('asc');

// Dia selecionado para destacar os colaboradores em escala
const selectedDiaHighlight = ref<number | null>(null);

// Helpers para verificar e quantificar dados de escala do colaborador no mês
const hasDadosEscala = (row: ColaboradorGradeRow): boolean => {
  if (row.grade_id && row.total_horas_escaladas !== undefined && row.total_horas_escaladas > 0) return true;
  if (!row.dias || !Array.isArray(row.dias)) return false;
  return row.dias.some(d => !!d.sigla || d.is_ferias || d.is_outra_unidade);
};

const countDiasAlocados = (row: ColaboradorGradeRow): number => {
  if (!row.dias || !Array.isArray(row.dias)) return 0;
  return row.dias.filter(d => !!d.sigla || d.is_ferias || d.is_outra_unidade).length;
};

// Formata matrícula - nome - cargo limitado a 70 caracteres (com reticências quando exceder)
const formatProfissional70 = (row: ColaboradorGradeRow): string => {
  const matriculaPart = row.matricula ? `${row.matricula} - ` : '';
  const cargoPart = (row.cargo && row.cargo !== '-') ? ` (${row.cargo})` : '';
  const fullText = `${matriculaPart}${row.nome || ''}${cargoPart}`;
  if (fullText.length <= 70) return fullText;
  return fullText.slice(0, 67) + '...';
};

const hasPlantaoNoDia = (row: ColaboradorGradeRow, dia: number): boolean => {
  if (!row.dias || !Array.isArray(row.dias)) return false;
  const d = row.dias.find(item => item.dia === dia);
  if (!d) return false;
  // Considera em escala quem tem sigla de plantão ou plantão em outra unidade
  return !!d.sigla || !!d.is_outra_unidade;
};

const toggleDiaHighlight = (dia: number) => {
  if (selectedDiaHighlight.value === dia) {
    selectedDiaHighlight.value = null;
    sortColumn.value = 'cargo_escala';
    sortDirection.value = 'asc';
  } else {
    selectedDiaHighlight.value = dia;
    sortColumn.value = 'dia_' + dia;
    sortDirection.value = 'asc';
  }
};

// ==========================================
// Barra de Rolagem Horizontal Superior Sincronizada
// ==========================================
const topScrollContainer = ref<HTMLDivElement | null>(null);
const bottomScrollContainer = ref<HTMLDivElement | null>(null);
const matrixTableRef = ref<HTMLTableElement | null>(null);
const tableScrollWidth = ref<number>(0);
let isSyncingScroll = false;

const handleTopScroll = () => {
  if (isSyncingScroll) return;
  isSyncingScroll = true;
  if (bottomScrollContainer.value && topScrollContainer.value) {
    bottomScrollContainer.value.scrollLeft = topScrollContainer.value.scrollLeft;
  }
  requestAnimationFrame(() => {
    isSyncingScroll = false;
  });
};

const handleBottomScroll = () => {
  if (isSyncingScroll) return;
  isSyncingScroll = true;
  if (topScrollContainer.value && bottomScrollContainer.value) {
    topScrollContainer.value.scrollLeft = bottomScrollContainer.value.scrollLeft;
  }
  requestAnimationFrame(() => {
    isSyncingScroll = false;
  });
};

const syncScrollWidth = () => {
  nextTick(() => {
    if (matrixTableRef.value) {
      tableScrollWidth.value = matrixTableRef.value.scrollWidth || 0;
    }
  });
};

const toggleSort = (col: string) => {
  if (sortColumn.value === col) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortColumn.value = col;
    // Para dias_alocados e horas o padrão útil é decrescente; para dia específico (dia_) a ordenação solicitada é ascendente por código/cargo/nome
    sortDirection.value = (col === 'dias_alocados' || col === 'horas') ? 'desc' : 'asc';
  }
};

const sortedMatrixData = computed(() => {
  let list = [...matrixData.value];

  // Filtra imediatamente a grade por Categoria / Cargo se selecionada
  if (selectedCargoId.value) {
    const targetCid = Number(selectedCargoId.value);
    list = list.filter(row => Number(row.cargo_id) === targetCid);
  }

  // Filtra imediatamente a grade por Posto de Serviço se selecionado
  if (selectedPostoId.value) {
    const targetPid = Number(selectedPostoId.value);
    list = list.filter(row => {
      if (row.posto_id && Number(row.posto_id) === targetPid) return true;
      if (row.lotacoes_info && row.lotacoes_info.some((l: any) => l.posto_id === targetPid)) return true;
      const matchingPosto = todosPostos.value.find(p => p.id === targetPid);
      if (matchingPosto && row.posto_nome && row.posto_nome.trim().toLowerCase() === matchingPosto.nome.trim().toLowerCase()) return true;
      return false;
    });
  }

  const dir = sortDirection.value === 'asc' ? 1 : -1;
  const col = sortColumn.value;

  // Helper para comparar Cargo (A-Z) e depois Nome (A-Z)
  const compareByCargoAndNome = (a: ColaboradorGradeRow, b: ColaboradorGradeRow, direction: number = 1): number => {
    const cargoA = (a.cargo && a.cargo !== '-' ? a.cargo : 'Sem Cargo').trim();
    const cargoB = (b.cargo && b.cargo !== '-' ? b.cargo : 'Sem Cargo').trim();
    const cmpCargo = cargoA.localeCompare(cargoB, 'pt-BR', { sensitivity: 'base' });
    if (cmpCargo !== 0) return cmpCargo * direction;
    return (a.nome || '').localeCompare(b.nome || '', 'pt-BR', { sensitivity: 'base' }) * direction;
  };

  return list.sort((a, b) => {
    // 1. Se um dia específico estiver selecionado/destacado (ou ordenação dia_X):
    // Prioridade máxima:
    // 1º: Quem tem alocação/escala no dia (1 antes de 0)
    // 2º: Cargo (A-Z)
    // 3º: Nome do profissional (A-Z)
    if (selectedDiaHighlight.value !== null || col.startsWith('dia_')) {
      const diaNum = selectedDiaHighlight.value !== null 
        ? selectedDiaHighlight.value 
        : parseInt(col.replace('dia_', ''), 10);
      
      const hasPlantaoA = hasPlantaoNoDia(a, diaNum) ? 1 : 0;
      const hasPlantaoB = hasPlantaoNoDia(b, diaNum) ? 1 : 0;

      if (hasPlantaoA !== hasPlantaoB) {
        return hasPlantaoB - hasPlantaoA; // Quem tem alocação no dia vem sempre primeiro
      }

      // Entre quem tem alocação no dia (ou ambos sem alocação no dia):
      // Ordena por Cargo e depois por Nome
      return compareByCargoAndNome(a, b, dir);
    }

    // 2. ORDENAÇÃO GERAL / PADRÃO:
    // Prioridade 1: Quem tem alocação no mês vem antes de quem não tem
    const temAlocacaoA = hasDadosEscala(a) ? 1 : 0;
    const temAlocacaoB = hasDadosEscala(b) ? 1 : 0;
    if (temAlocacaoA !== temAlocacaoB) {
      return temAlocacaoB - temAlocacaoA; // Alocados primeiro (1 antes de 0)
    }

    // Se o usuário clicou especificamente em 'horas' ou 'dias_alocados':
    if (col === 'horas') {
      const hA = a.total_horas_escaladas || 0;
      const hB = b.total_horas_escaladas || 0;
      if (hA !== hB) {
        return (hA - hB) * dir;
      }
      return compareByCargoAndNome(a, b);
    }

    if (col === 'dias_alocados') {
      const countA = countDiasAlocados(a);
      const countB = countDiasAlocados(b);
      if (countA !== countB) {
        return (countA - countB) * dir;
      }
      return compareByCargoAndNome(a, b);
    }

    if (col === 'cargo') {
      const cargoA = (a.cargo && a.cargo !== '-' ? a.cargo : 'Sem Cargo').trim();
      const cargoB = (b.cargo && b.cargo !== '-' ? b.cargo : 'Sem Cargo').trim();
      const cmpCargo = cargoA.localeCompare(cargoB, 'pt-BR', { sensitivity: 'base' });
      if (cmpCargo !== 0) return cmpCargo * dir;
      return (a.nome || '').localeCompare(b.nome || '', 'pt-BR', { sensitivity: 'base' });
    }

    if (col === 'escala') {
      const escA = (a.escala_codigo || a.escala_padrao || '').trim();
      const escB = (b.escala_codigo || b.escala_padrao || '').trim();
      const cmpEsc = escA.localeCompare(escB, 'pt-BR', { sensitivity: 'base' });
      if (cmpEsc !== 0) return cmpEsc * dir;
      return compareByCargoAndNome(a, b);
    }

    // Se o usuário clicou na coluna Nome/Profissional:
    if (col === 'nome') {
      // Quando ordenando especificamente pela coluna Nome, mantendo alocados no topo:
      // se a direção for asc/desc, ordena Cargo e Nome
      return compareByCargoAndNome(a, b, dir);
    }

    // Regra padrão solicitada:
    // Primeiro os que têm as alocações, depois por cargo e ordem alfabética dentro desses alocados
    return compareByCargoAndNome(a, b, dir);
  });
});

// Listas de apoio para os filtros e selects
const unidades = ref<any[]>([]);
const cargos = ref<any[]>([]);
const legendas = ref<any[]>([]);
const escalas = ref<any[]>([]);
const todosFuncionarios = ref<any[]>([]);
const todosPostos = ref<any[]>([]);

// Conjunto de IDs de Unidades subordinadas à unidade selecionada (protegido contra ciclos)
const getDescendantUorgIds = (parentId: number): Set<number> => {
  const result = new Set<number>([parentId]);
  const queue = [parentId];
  let iterations = 0;
  while (queue.length > 0 && iterations < 1000) {
    iterations++;
    const curr = queue.shift()!;
    for (const u of unidades.value) {
      if (u.uorg_pai_id === curr && !result.has(u.id)) {
        result.add(u.id);
        queue.push(u.id);
      }
    }
  }
  return result;
};

// Cargos filtrados de acordo com os filtros ativos (Unidade, Subordinadas, Posto)
const sortedCargos = computed(() => {
  // Se não houver funcionários carregados, exibe a lista geral ordenada
  if (!todosFuncionarios.value || todosFuncionarios.value.length === 0) {
    return [...cargos.value].sort((a, b) => {
      return (a.nome || '').localeCompare(b.nome || '', 'pt-BR', { sensitivity: 'base' });
    });
  }

  let targetUorgIds: Set<number> | null = null;
  if (selectedUnidadeId.value) {
    if (incluirSubordinadas.value) {
      targetUorgIds = getDescendantUorgIds(selectedUnidadeId.value);
    } else {
      targetUorgIds = new Set<number>([selectedUnidadeId.value]);
    }
  }

  const cargoIdsPresentes = new Set<number>();

  for (const f of todosFuncionarios.value) {
    const cid = Number(f.cargo_id || f.cargo?.id);
    if (!cid) continue;

    if (targetUorgIds || selectedPostoId.value) {
      const lotacoes = f.lotacoes;
      if (Array.isArray(lotacoes)) {
        for (const l of lotacoes) {
          const uId = l.uorg_id || l.unidade_id;
          if (targetUorgIds && (!uId || !targetUorgIds.has(Number(uId)))) {
            continue;
          }
          if (selectedPostoId.value && Number(l.posto_id) !== Number(selectedPostoId.value)) {
            continue;
          }
          cargoIdsPresentes.add(cid);
          break;
        }
      }
    } else {
      cargoIdsPresentes.add(cid);
    }
  }

  const list = cargos.value.filter(c => cargoIdsPresentes.has(c.id));
  return [...list].sort((a, b) => {
    return (a.nome || '').localeCompare(b.nome || '', 'pt-BR', { sensitivity: 'base' });
  });
});

const sortedEscalas = computed(() => {
  return [...escalas.value].sort((a, b) => (a.sigla || a.codigo || '').localeCompare(b.sigla || b.codigo || '', 'pt-BR', { sensitivity: 'base' }));
});

const sortedLegendas = computed(() => {
  return [...legendas.value].sort((a, b) => (a.sigla || '').localeCompare(b.sigla || '', 'pt-BR', { sensitivity: 'base' }));
});

// Conjuntos de IDs de Unidades e Postos que possuem funcionários efetivamente lotados
const uorgIdsComFuncionarios = computed(() => {
  const set = new Set<number>();
  todosFuncionarios.value.forEach(f => {
    if (f.lotacoes && Array.isArray(f.lotacoes)) {
      f.lotacoes.forEach((l: any) => {
        const uId = l.uorg_id || l.unidade_id;
        if (uId) set.add(Number(uId));
      });
    }
  });
  return set;
});

const postoIdsComFuncionarios = computed(() => {
  const set = new Set<number>();
  todosFuncionarios.value.forEach(f => {
    if (f.lotacoes && Array.isArray(f.lotacoes)) {
      f.lotacoes.forEach((l: any) => {
        if (l.posto_id) set.add(Number(l.posto_id));
      });
    }
  });
  return set;
});

// Postos filtrados pela UORG selecionada (ordenados alfabeticamente e sem nomes duplicados).
// Quando uma unidade é selecionada, exibe os postos vinculados à UORG ou às suas subordinadas (e se tiverem funcionários lotados ou vinculação à unidade).
const postosFiltrados = computed(() => {
  let list = [...todosPostos.value];
  if (selectedUnidadeId.value) {
    let targetUorgIds: Set<number>;
    if (incluirSubordinadas.value) {
      targetUorgIds = getDescendantUorgIds(selectedUnidadeId.value);
    } else {
      targetUorgIds = new Set<number>([selectedUnidadeId.value]);
    }
    list = list.filter(p => {
      const uId = p.uorg_id || p.unidade_id;
      // Aceita se o posto pertence à UORG/subordinadas, ou se há funcionário com lotação nessa UORG alocado a este posto
      if (uId && targetUorgIds.has(Number(uId))) return true;
      return false;
    });
  } else {
    // Quando nenhuma unidade está selecionada ("Todas as Unidades"), mostra os postos que possuem funcionários lotados
    // ou todos os postos se não houver funcionários carregados
    if (postoIdsComFuncionarios.value.size > 0) {
      list = list.filter(p => postoIdsComFuncionarios.value.has(p.id));
    }
  }
  
  // Deduplicação por nome no combo para não listar o mesmo posto repetido
  const uniqueMap = new Map<string, any>();
  for (const p of list) {
    const nomeNorm = (p.nome || '').trim().toUpperCase();
    if (!uniqueMap.has(nomeNorm)) {
      uniqueMap.set(nomeNorm, p);
    }
  }
  const uniqueList = Array.from(uniqueMap.values());
  return uniqueList.sort((a, b) => (a.nome || '').localeCompare(b.nome || '', 'pt-BR', { sensitivity: 'base' }));
});

// ==========================================
// Permissões de Unidade por Escopo Hierárquico
// Filtra apenas as unidades que possuem funcionários lotados
// ==========================================
const unidadesDisponiveis = computed(() => {
  let list = unidades.value.filter(u => uorgIdsComFuncionarios.value.has(u.id));

  if (userScope.value && !userScope.value.is_admin && userScope.value.unidade_ids !== null) {
    const allowed = new Set(userScope.value.unidade_ids);
    list = list.filter(u => allowed.has(u.id));
  }
  return [...list].sort((a, b) => (a.nome || '').localeCompare(b.nome || '', 'pt-BR', { sensitivity: 'base' }));
});

// Formatação hierárquica em árvore das unidades disponíveis (protegido contra recursão infinita)
const unidadesFormatadasHierarquia = computed(() => {
  const list = unidadesDisponiveis.value;
  if (!list || list.length === 0) return [];

  const map = new Map<number, any>();
  const childrenMap = new Map<number | null, any[]>();

  list.forEach(u => {
    map.set(u.id, u);
  });

  list.forEach(u => {
    const pId = u.uorg_pai_id && map.has(u.uorg_pai_id) ? u.uorg_pai_id : null;
    if (!childrenMap.has(pId)) childrenMap.set(pId, []);
    childrenMap.get(pId)!.push(u);
  });

  childrenMap.forEach(arr => {
    arr.sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'));
  });

  const result: any[] = [];
  const visited = new Set<number>();

  const traverse = (parentId: number | null, depth: number) => {
    if (depth > 20) return; // Evita estouro de pilha
    const children = childrenMap.get(parentId) || [];
    for (const item of children) {
      if (visited.has(item.id)) continue;
      visited.add(item.id);

      let prefix = '';
      if (depth === 1) prefix = '  ↳ ';
      else if (depth === 2) prefix = '    ↳ ';
      else if (depth >= 3) prefix = '      ↳ '.repeat(depth - 2);

      const siglaDisplay = item.sigla ? ` (${item.sigla})` : '';
      const hasSubs = (childrenMap.get(item.id) || []).length > 0;
      const hierBadge = hasSubs ? ' 🏛️' : '';

      result.push({
        ...item,
        display_nome: `${prefix}${item.nome}${siglaDisplay}${hierBadge}`,
        depth
      });
      traverse(item.id, depth + 1);
    }
  };

  traverse(null, 0);

  for (const item of list) {
    if (!visited.has(item.id)) {
      visited.add(item.id);
      result.push({
        ...item,
        display_nome: item.nome + (item.sigla ? ` (${item.sigla})` : ''),
        depth: 0
      });
    }
  }

  return result;
});

// Verifica se o usuário atual é o gestor do nível hierárquico mais alto para a UORG selecionada
const isTopLevelForSelectedUnit = computed(() => {
  if (!userScope.value || userScope.value.is_admin || userScope.value.nivel === 'DIVGP_ADMIN') {
    return true;
  }
  if (!selectedUnidadeId.value) return false;
  const u = unidades.value.find(item => item.id === selectedUnidadeId.value);
  if (!u) return false;

  const userUorgs = new Set(userScope.value.uorg_ids || []);
  
  // Se a UORG é raiz (sem pai) e o usuário a gerencia diretamente
  if (!u.uorg_pai_id && userUorgs.has(u.id)) {
    return true;
  }

  // Se o usuário gerencia algum dos ancestrais superiores na árvore
  let currPai = u.uorg_pai;
  while (currPai) {
    if (userUorgs.has(currPai.id)) return true;
    currPai = currPai.uorg_pai;
  }

  return false;
});

// Quantidade de dias no mês selecionado
const totalDiasMes = computed(() => {
  return new Date(selectedAno.value, selectedMes.value, 0).getDate();
});

// Helper de fim de semana
const isWeekend = (dia: number) => {
  const dt = new Date(selectedAno.value, selectedMes.value - 1, dia);
  const dow = dt.getDay();
  return dow === 0 || dow === 6;
};

const getDiaSemanaSigla = (dia: number) => {
  const dt = new Date(selectedAno.value, selectedMes.value - 1, dia);
  return diasSemanaNomes[dt.getDay()];
};

const isWeekendInMes = (dia: number, mes: number, ano: number) => {
  const dt = new Date(ano, mes - 1, dia);
  const dow = dt.getDay();
  return dow === 0 || dow === 6;
};

const getDiaSemanaSiglaMes = (dia: number, mes: number, ano: number) => {
  const dt = new Date(ano, mes - 1, dia);
  return diasSemanaNomes[dt.getDay()];
};

const getUnidadeNomeDisplay = () => {
  if (!selectedUnidadeId.value) return 'Todas as Unidades';
  const u = unidades.value.find(item => item.id === selectedUnidadeId.value);
  return u ? u.nome : 'Unidade';
};

// Resumo legível dos filtros ativos para exibição no topo da tabela
const activeFiltersList = computed(() => {
  const list: { label: string; value: string; type: string }[] = [];

  // 1. Unidade
  if (selectedUnidadeId.value) {
    const u = unidades.value.find(item => item.id === selectedUnidadeId.value);
    const uNome = u ? (u.sigla ? `${u.nome} (${u.sigla})` : u.nome) : `Unidade #${selectedUnidadeId.value}`;
    const sub = incluirSubordinadas.value ? ' ' : '';
    list.push({ label: 'Unidade', value: `${uNome}${sub}`, type: 'unidade' });
  }

  // 2. Cargo / Categoria
  if (selectedCargoId.value) {
    const c = cargos.value.find(item => item.id === selectedCargoId.value);
    list.push({ label: 'Categoria', value: c ? c.nome : `Cargo #${selectedCargoId.value}`, type: 'cargo' });
  }

  // 3. Posto de Serviço
  if (selectedPostoId.value) {
    const p = todosPostos.value.find(item => item.id === selectedPostoId.value);
    list.push({ label: 'Posto', value: p ? p.nome : `Posto #${selectedPostoId.value}`, type: 'posto' });
  }

  // 4. Status da Escala
  if (selectedStatus.value && selectedStatus.value !== 'Todos') {
    const statusLabels: Record<string, string> = {
      'DIVGP_PUBLICADAS': 'Apenas Publicadas (DIVGP Oficial)',
      'Publicada': 'Publicada (DIVGP)',
      'Enviada_Superior': 'Aguardando Chefia Superior',
      'Devolvida': 'Devolvida para Ajuste',
      'Rascunho': 'Em Elaboração',
      'Pendente': 'Sem Escala Cadastrada'
    };
    list.push({ label: 'Status', value: statusLabels[selectedStatus.value] || selectedStatus.value, type: 'status' });
  }

  // 5. Termo de Busca
  if (searchTerm.value && searchTerm.value.trim()) {
    list.push({ label: 'Busca', value: `"${searchTerm.value.trim()}"`, type: 'busca' });
  }

  return list;
});

// Cores dos badges de sigla
const getSiglaBadgeClass = (sigla: string) => {
  const s = sigla.toUpperCase().trim();
  if (s === 'M') return 'bg-blue-100 text-blue-800 border border-blue-200';
  if (s === 'T') return 'bg-amber-100 text-amber-800 border border-amber-200';
  if (s === 'N') return 'bg-purple-100 text-purple-800 border border-purple-200';
  if (s === 'D') return 'bg-emerald-100 text-emerald-800 border border-emerald-200';
  if (s === 'FE') return 'bg-rose-100 text-rose-800 border border-rose-200';
  if (s === 'FR' || s === 'FER') return 'bg-rose-100 text-rose-800 border border-rose-300 font-bold';
  if (s === 'F') return 'bg-gray-100 text-gray-700 border border-gray-200';
  if (s.includes('SN') || s.includes('SO')) return 'bg-indigo-100 text-indigo-800 border border-indigo-200';
  return 'bg-gray-100 text-gray-800 border border-gray-200';
};

// Tooltip com a descrição completa da escala e horários de início e fim
const getDiaTooltip = (diaItem: any): string => {
  if (!diaItem) return '';
  
  if (diaItem.is_outra_unidade) {
    return diaItem.descricao || `Alocado em outra unidade: ${diaItem.outra_unidade_nome || 'Unidade vinculada'} (${diaItem.outra_unidade_sigla || ''})`;
  }
  
  if (diaItem.is_ferias || diaItem.sigla === 'FE') {
    return 'Férias Regulamentares (FE)';
  }

  if (diaItem.is_feriado && !diaItem.sigla) {
    return `Feriado Oficial: ${diaItem.feriado_nome || 'Feriado'}`;
  }

  const s = diaItem.sigla?.trim();
  if (!s) {
    if (diaItem.is_feriado) return `Feriado Oficial: ${diaItem.feriado_nome || 'Feriado'}`;
    return 'Sem escala cadastrada para este dia';
  }

  const sUpper = s.toUpperCase();

  // 1. Procurar nas escalas cadastradas da instituição
  const esc = escalas.value.find(e => 
    (e.sigla && e.sigla.toUpperCase() === sUpper) || 
    (e.codigo && e.codigo.toUpperCase() === sUpper)
  );

  if (esc) {
    const desc = esc.descricao ? ` - ${esc.descricao}` : '';
    const horario = (esc.inicio_jornada && esc.fim_jornada) 
      ? ` (${formatTime(esc.inicio_jornada)} às ${formatTime(esc.fim_jornada)})` 
      : '';
    const feriadoAviso = diaItem.is_feriado ? ` · Feriado: ${diaItem.feriado_nome || 'Oficial'}` : '';
    return `${esc.sigla}${desc}${horario}${feriadoAviso}`;
  }

  // 2. Procurar nas legendas cadastradas
  const leg = legendas.value.find(l => l.sigla && l.sigla.toUpperCase() === sUpper);
  if (leg) {
    const feriadoAviso = diaItem.is_feriado ? ` · Feriado: ${diaItem.feriado_nome || 'Oficial'}` : '';
    return `${leg.sigla} - ${leg.descricao}${feriadoAviso}`;
  }

  // 3. Padrões conhecidos comuns do hospital
  const padroesConhecidos: Record<string, string> = {
    'F': 'Folga',
    'FR': 'Folga Feriado',
    'FE': 'Férias Regulamentares',
    'LM': 'Licença Médica',
    'LP': 'Licença Prêmio',
    'A': 'Afastamento',
    'FJ': 'Falta Justificada',
    'M': 'Turno Manhã (07:00 às 13:00)',
    'M6': 'Turno Manhã 6h (07:00 às 13:00)',
    'T': 'Turno Tarde (13:00 às 19:00)',
    'T6': 'Turno Tarde 6h (13:00 às 19:00)',
    'N': 'Plantão Noturno 12h (19:00 às 07:00)',
    'SN': 'Serviço Noturno 12h (19:00 às 07:00)',
    'D': 'Plantão Diurno 12h (07:00 às 19:00)',
    'D6': 'Diurno 6 horas',
    'D8': 'Diurno 8 horas (08:00 às 17:00)',
    'SD': 'Serviço Diurno 12h (07:00 às 19:00)',
    'P12': 'Plantão 12h',
    'P12D': 'Plantão 12h Diurno (07:00 às 19:00)',
    'P12N': 'Plantão 12h Noturno (19:00 às 07:00)',
    'P24': 'Plantão 24h',
    '12X36': 'Plantão 12x36'
  };

  if (padroesConhecidos[sUpper]) {
    const feriadoAviso = diaItem.is_feriado ? ` · Feriado: ${diaItem.feriado_nome || 'Oficial'}` : '';
    return `${sUpper} - ${padroesConhecidos[sUpper]}${feriadoAviso}`;
  }

  if (diaItem.descricao) {
    return `${sUpper} - ${diaItem.descricao}`;
  }

  return sUpper;
};

// ==========================================
// Feriados & Calendário
// ==========================================
const feriadosLista = ref<any[]>([]);
const respeitarFeriadosDiarista = ref<boolean>(true);

const feriadosMesMap = computed(() => {
  const map: Record<number, string> = {};
  feriadosLista.value.forEach(f => {
    if (f.data) {
      const parts = f.data.split('-');
      const ano = parseInt(parts[0], 10);
      const mes = parseInt(parts[1], 10);
      const dia = parseInt(parts[2], 10);
      if (ano === Number(selectedAno.value) && mes === Number(selectedMes.value)) {
        map[dia] = f.nome;
      }
    }
  });
  return map;
});

const feriadosMesCriarMap = computed(() => {
  const map: Record<number, string> = {};
  feriadosLista.value.forEach(f => {
    if (f.data) {
      const parts = f.data.split('-');
      const ano = parseInt(parts[0], 10);
      const mes = parseInt(parts[1], 10);
      const dia = parseInt(parts[2], 10);
      if (ano === Number(criarForm.ano) && mes === Number(criarForm.mes)) {
        map[dia] = f.nome;
      }
    }
  });
  return map;
});

// ==========================================
// Estrutura e Dados para Visão Calendário
// ==========================================
export interface CalendarProfissionalAlocado {
  colaborador: ColaboradorGradeRow;
  sigla: string;
  is_ferias: boolean;
  is_outra_unidade: boolean;
  descricao?: string | null;
  diaItem: any;
}

export interface CalendarDayCell {
  dia: number;
  dataStr: string;
  diaSemana: number; // 0 = Dom, 6 = Sáb
  diaSemanaNome: string;
  isWeekend: boolean;
  feriadoNome: string | null;
  alocados: CalendarProfissionalAlocado[];
}

const calendarDaysGrid = computed<CalendarDayCell[]>(() => {
  const list: CalendarDayCell[] = [];
  const ano = Number(selectedAno.value);
  const mes = Number(selectedMes.value);
  const total = totalDiasMes.value;

  for (let d = 1; d <= total; d++) {
    const dt = new Date(ano, mes - 1, d);
    const dow = dt.getDay();
    const dataStr = `${ano}-${String(mes).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
    const feriado = feriadosMesMap.value[d] || null;

    // Colaboradores alocados no dia `d` dentro da lista filtrada `sortedMatrixData`
    const alocados: CalendarProfissionalAlocado[] = [];
    for (const row of sortedMatrixData.value) {
      if (!row.dias || !Array.isArray(row.dias)) continue;
      const diaItem = row.dias.find(item => item.dia === d);
      if (!diaItem) continue;

      const hasAlocacao = !!diaItem.sigla || !!diaItem.is_outra_unidade || !!diaItem.is_ferias;
      if (hasAlocacao) {
        alocados.push({
          colaborador: row,
          sigla: diaItem.sigla || (diaItem.is_ferias ? 'FE' : (diaItem.is_outra_unidade ? 'EXT' : '')),
          is_ferias: !!diaItem.is_ferias || diaItem.sigla === 'FE',
          is_outra_unidade: !!diaItem.is_outra_unidade,
          descricao: diaItem.descricao,
          diaItem
        });
      }
    }

    list.push({
      dia: d,
      dataStr,
      diaSemana: dow,
      diaSemanaNome: diasSemanaNomes[dow],
      isWeekend: dow === 0 || dow === 6,
      feriadoNome: feriado,
      alocados
    });
  }

  return list;
});

// Offset de dias vazios antes do dia 1 no grid mensal do calendário
const calendarStartOffset = computed<number>(() => {
  const dt = new Date(Number(selectedAno.value), Number(selectedMes.value) - 1, 1);
  return dt.getDay(); // 0 (Domingo) a 6 (Sábado)
});

// Modal / Popup de detalhes dos profissionais de um dia no calendário
const calendarDiaDetalhes = ref<CalendarDayCell | null>(null);
const openCalendarDiaDetalhes = (diaCell: CalendarDayCell) => {
  calendarDiaDetalhes.value = diaCell;
};
const closeCalendarDiaDetalhes = () => {
  calendarDiaDetalhes.value = null;
};

// ==========================================
// Busca de Dados (API)
// ==========================================
let searchTimeout: any = null;
const onSearchInput = () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    fetchData();
  }, 350);
};

const clearSearch = () => {
  searchTerm.value = '';
  selectedDiaHighlight.value = null;
  fetchData();
};

const onPostoChange = () => {
  if (selectedPostoId.value) {
    const targetPid = Number(selectedPostoId.value);
    const foundPosto = todosPostos.value.find(p => p.id === targetPid);
    if (foundPosto) {
      const parentUorgId = foundPosto.uorg_id || foundPosto.unidade_id;
      if (parentUorgId) {
        selectedUnidadeId.value = parentUorgId;
      }
    }
  }

  // Se o cargo previamente selecionado não existir no novo posto selecionado, reseta
  if (selectedCargoId.value) {
    const aindaExisteCargo = sortedCargos.value.some(c => c.id === selectedCargoId.value);
    if (!aindaExisteCargo) {
      selectedCargoId.value = undefined;
    }
  }

  fetchData();
};

const onUnidadeChange = () => {
  // Se o posto previamente selecionado não pertence aos postos filtrados da nova unidade, reseta
  if (selectedPostoId.value) {
    const aindaExiste = postosFiltrados.value.some(p => p.id === selectedPostoId.value);
    if (!aindaExiste) {
      selectedPostoId.value = undefined;
    }
  }

  // Se o cargo previamente selecionado não pertence aos cargos da nova unidade, reseta
  if (selectedCargoId.value) {
    const aindaExisteCargo = sortedCargos.value.some(c => c.id === selectedCargoId.value);
    if (!aindaExisteCargo) {
      selectedCargoId.value = undefined;
    }
  }

  fetchData();
};

const clearFilters = () => {
  selectedUnidadeId.value = undefined;
  selectedCargoId.value = undefined;
  selectedPostoId.value = undefined;
  selectedStatus.value = 'Todos';
  searchTerm.value = '';
  selectedDiaHighlight.value = null;
  clearSavedGradeFilters();
  fetchData();
};

const fetchData = async () => {
  loading.value = true;
  try {
    const isDivgp = selectedStatus.value === 'DIVGP_PUBLICADAS';
    const statusParam = (selectedStatus.value !== 'Todos' && !isDivgp) ? selectedStatus.value : undefined;

    const [matrixRes, indRes] = await Promise.all([
      gradeService.getMatrix({
        mes: selectedMes.value,
        ano: selectedAno.value,
        unidade_id: selectedUnidadeId.value,
        incluir_subordinadas: selectedUnidadeId.value ? incluirSubordinadas.value : false,
        cargo_id: selectedCargoId.value,
        posto_id: selectedPostoId.value,
        search: searchTerm.value || undefined,
        status: statusParam,
        apenas_publicadas: isDivgp
      }),
      gradeService.getIndicators({
        mes: selectedMes.value,
        ano: selectedAno.value,
        unidade_id: selectedUnidadeId.value,
        incluir_subordinadas: selectedUnidadeId.value ? incluirSubordinadas.value : false,
        cargo_id: selectedCargoId.value,
        posto_id: selectedPostoId.value,
        search: searchTerm.value || undefined
      })
    ]);

    matrixData.value = matrixRes;

    // Se houver filtros adicionais ativos (como status, cargo, posto ou busca), 
    // garantir que os indicadores reflitam exatamente o universo dos colaboradores exibidos
    if (statusParam || isDivgp) {
      indicators.total_colaboradores = matrixRes.length;
      indicators.total_ferias = matrixRes.filter(r => r.is_ferias_mes || r.dias?.some(d => d.is_ferias || d.sigla === 'FE')).length;
      indicators.total_multiplas_lotacoes = matrixRes.filter(r => r.has_multiple_lotacoes || (r.total_lotacoes && r.total_lotacoes > 1)).length;
    } else {
      indicators.total_colaboradores = indRes.total_colaboradores;
      indicators.total_ferias = indRes.total_ferias;
      indicators.total_multiplas_lotacoes = indRes.total_multiplas_lotacoes;
    }
  } catch (error) {
    console.error('Erro ao buscar dados da grade:', error);
  } finally {
    loading.value = false;
    syncScrollWidth();
  }
};

const enviarSuperiorSingleGrade = async (gradeId: number) => {
  if (!confirm('Deseja aprovar e encaminhar esta escala para análise do Chefe da Unidade?')) return;
  try {
    await gradeService.enviarSuperior(gradeId);
    alert('Escala aprovada e enviada para o Chefe da Unidade com sucesso!');
    await fetchData();
  } catch (err: any) {
    alert('Erro ao aprovar para a unidade: ' + (err.response?.data?.detail || err.message));
  }
};

const enviarLoteSuperior = async () => {
  if (!selectedUnidadeId.value) {
    alert('Selecione uma UORG específica para aprovar todas as escalas.');
    return;
  }
  const uNome = getUnidadeNomeDisplay();
  if (!confirm(`Deseja aprovar e encaminhar todas as escalas do posto/UORG "${uNome}" (${mesesNomes[selectedMes.value - 1]}/${selectedAno.value}) para o Chefe da Unidade?`)) return;
  try {
    const res = await gradeService.enviarLoteSuperior(Number(selectedUnidadeId.value), Number(selectedMes.value), Number(selectedAno.value));
    alert(res.message || 'Escalas aprovadas para a Unidade com sucesso!');
    await fetchData();
  } catch (err: any) {
    alert('Erro ao aprovar escalas para a unidade: ' + (err.response?.data?.detail || err.message));
  }
};

const devolverSingleGrade = async (gradeId: number) => {
  const motivo = prompt('Informe o motivo/orientação de ajuste para devolver a escala ao Chefe do Posto:');
  if (motivo === null) return;
  try {
    await gradeService.devolverGrade(gradeId, motivo || undefined);
    alert('Escala devolvida para correção do Chefe do Posto com sucesso!');
    await fetchData();
  } catch (err: any) {
    alert('Erro ao devolver escala: ' + (err.response?.data?.detail || err.message));
  }
};

const publishSingleGrade = async (gradeId: number) => {
  if (!confirm('Deseja homologar e enviar esta escala para a DIVGP? Após aprovação final na DIVGP ela ficará publicada e não poderá ser alterada.')) return;
  try {
    await gradeService.publishGrade(gradeId);
    alert('Escala enviada para a DIVGP / Homologada com sucesso!');
    await fetchData();
  } catch (err: any) {
    alert('Erro ao enviar escala para a DIVGP: ' + (err.response?.data?.detail || err.message));
  }
};

const publishAllUnidade = async () => {
  if (!selectedUnidadeId.value) {
    alert('Selecione uma Unidade específica para enviar todas as escalas.');
    return;
  }
  const uNome = getUnidadeNomeDisplay();
  if (!confirm(`Confirmar envio de todas as escalas dos postos da Unidade "${uNome}" para o mês ${mesesNomes[selectedMes.value - 1]}/${selectedAno.value} para a DIVGP?`)) return;
  try {
    const res = await gradeService.publishAllInUnit(Number(selectedUnidadeId.value), Number(selectedMes.value), Number(selectedAno.value));
    alert(res.message || 'Todas as escalas foram enviadas com sucesso para a DIVGP!');
    await fetchData();
  } catch (err: any) {
    alert('Erro ao publicar escalas da unidade: ' + (err.response?.data?.detail || err.message));
  }
};

const fetchAuxiliaryData = async () => {
  try {
    const [unidadesRes, cargosRes, legendasRes, escalasRes, funcRes, feriadosRes, postosRes, scopeRes] = await Promise.all([
      api.get('/api/uorgs'),
      api.get('/api/cargos'),
      api.get('/api/legendas'),
      api.get('/api/escalas'),
      api.get('/api/funcionarios'),
      api.get('/api/feriados'),
      api.get('/api/postos'),
      gerenciaService.getMyScope().catch(() => null)
    ]);
    unidades.value = unidadesRes.data;
    cargos.value = cargosRes.data;
    legendas.value = legendasRes.data;
    escalas.value = escalasRes.data;
    todosFuncionarios.value = funcRes.data;
    feriadosLista.value = feriadosRes.data;
    todosPostos.value = postosRes.data;
    userScope.value = scopeRes;

    // Se for gerente de UORG/posto exclusivo e não tiver unidade selecionada, seleciona a primeira do escopo
    const allowedIds = scopeRes?.uorg_ids || scopeRes?.unidade_ids;
    if (scopeRes && !scopeRes.is_admin && allowedIds && allowedIds.length > 0) {
      if (!selectedUnidadeId.value || !allowedIds.includes(selectedUnidadeId.value)) {
        selectedUnidadeId.value = allowedIds[0];
      }
    }
  } catch (error) {
    console.error('Erro ao carregar dados auxiliares:', error);
  }
};

// Exclusão de escala
const deleteGrade = async (gradeId: number) => {
  if (!confirm('Deseja realmente excluir esta escala mensal?')) return;
  try {
    await gradeService.deleteGrade(gradeId);
    fetchData();
  } catch (err) {
    alert('Erro ao excluir escala.');
  }
};

// ==========================================
// MODAL 1: CRIAR / EDITAR ESCALA
// ==========================================
const showCriarModal = ref(false);
const editingGradeId = ref<number | null>(null);
const isEditingCollaborator = ref(false);
const saving = ref(false);
const modalError = ref('');
const quickFillSigla = ref('');
const modalBodyRef = ref<HTMLElement | null>(null);
const toastMessage = ref('');
const toastTimeout = ref<any>(null);

const showToast = (msg: string) => {
  if (toastTimeout.value) clearTimeout(toastTimeout.value);
  toastMessage.value = msg;
  toastTimeout.value = setTimeout(() => {
    toastMessage.value = '';
  }, 4000);
};

// Helper para formatar hora HH:mm
const formatTime = (timeStr?: string | null) => {
  if (!timeStr) return '';
  return timeStr.substring(0, 5);
};

// ==========================================
// MODAL SELEÇÃO DE DIAS PARA PREENCHIMENTO RÁPIDO
// ==========================================
const showSelecionarDiasModal = ref(false);
const selectedDiasParaPreenchimento = ref<number[]>([]);

const openSelecionarDiasModal = () => {
  if (!quickFillSigla.value) {
    alert('Por favor, selecione primeiro um Código de Escala no combo antes de selecionar os dias.');
    return;
  }
  // Inicializa a seleção com os dias que já possuem essa sigla preenchida (ou vazio)
  const jaPreenchidos = criarDias.value
    .filter(d => d.legenda_sigla && d.legenda_sigla.toUpperCase() === quickFillSigla.value.toUpperCase())
    .map(d => d.dia);
  selectedDiasParaPreenchimento.value = jaPreenchidos.length > 0 ? [...jaPreenchidos] : [];
  showSelecionarDiasModal.value = true;
};

const closeSelecionarDiasModal = () => {
  showSelecionarDiasModal.value = false;
};

const toggleDiaSelecao = (dia: number) => {
  const idx = selectedDiasParaPreenchimento.value.indexOf(dia);
  if (idx > -1) {
    selectedDiasParaPreenchimento.value.splice(idx, 1);
  } else {
    selectedDiasParaPreenchimento.value.push(dia);
  }
};

const selectAllDiasModal = () => {
  const todos: number[] = [];
  for (let d = 1; d <= totalDiasMesCriar.value; d++) {
    todos.push(d);
  }
  selectedDiasParaPreenchimento.value = todos;
};

const selectWeekdaysModal = () => {
  const uteis: number[] = [];
  const feriados = feriadosMesCriarMap.value;
  for (let d = 1; d <= totalDiasMesCriar.value; d++) {
    const isWk = isWeekendInMes(d, criarForm.mes, criarForm.ano);
    const isFer = !!feriados[d];
    if (!isWk && !(isFer && respeitarFeriadosDiarista.value)) {
      uteis.push(d);
    }
  }
  selectedDiasParaPreenchimento.value = uteis;
};

const selectWeekendsModal = () => {
  const fds: number[] = [];
  for (let d = 1; d <= totalDiasMesCriar.value; d++) {
    if (isWeekendInMes(d, criarForm.mes, criarForm.ano)) {
      fds.push(d);
    }
  }
  selectedDiasParaPreenchimento.value = fds;
};

const clearSelectionModal = () => {
  selectedDiasParaPreenchimento.value = [];
};

const aplicarEscalaDiasSelecionados = () => {
  if (!quickFillSigla.value) {
    alert('Nenhum código de escala selecionado.');
    return;
  }
  if (selectedDiasParaPreenchimento.value.length === 0) {
    alert('Selecione pelo menos um dia para aplicar o código de escala.');
    return;
  }

  const diasSet = new Set(selectedDiasParaPreenchimento.value);
  criarDias.value.forEach(d => {
    if (diasSet.has(d.dia)) {
      d.legenda_sigla = quickFillSigla.value;
      d.descricao = undefined;
    }
  });

  showSelecionarDiasModal.value = false;
};

const criarForm = reactive({
  funcionario_id: 0,
  unidade_id: 0,
  posto_id: null as number | null,
  mes: 1,
  ano: 2026,
  status: 'Rascunho',
  observacao: ''
});

interface CriarDiaItem {
  dia: number;
  legenda_sigla: string;
  descricao?: string;
}
const criarDias = ref<CriarDiaItem[]>([]);

const isGradeBloqueada = computed(() => {
  return !!editingGradeId.value && criarForm.status === 'Publicada' && !authStore.isAdmin;
});

const reabrirGrade = async (gradeId: number) => {
  if (!confirm('Deseja reabrir esta escala? Ela retornará ao status "Rascunho" e permitirá novas edições pelo gestor da área.')) return;
  try {
    await gradeService.reabrirGrade(gradeId);
    if (showCriarModal.value && editingGradeId.value === gradeId) {
      criarForm.status = 'Rascunho';
    }
    await fetchData();
    alert('Escala reaberta com sucesso!');
  } catch (err: any) {
    alert('Erro ao reabrir escala: ' + (err.response?.data?.detail || err.message));
  }
};

const totalDiasMesCriar = computed(() => {
  return new Date(criarForm.ano, criarForm.mes, 0).getDate();
});

const funcionariosDisponiveis = computed(() => {
  const unidadeId = Number(criarForm.unidade_id);
  const postoId = criarForm.posto_id ? Number(criarForm.posto_id) : null;

  if (!unidadeId) return todosFuncionarios.value;

  const filtered = todosFuncionarios.value.filter(f => {
    // Se estiver editando esta escala e for o próprio funcionário, sempre inclui
    if ((isEditingCollaborator.value || editingGradeId.value) && f.id === Number(criarForm.funcionario_id)) {
      return true;
    }

    if (!f.lotacoes || f.lotacoes.length === 0) return false;
    return f.lotacoes.some((lot: any) => {
      const lotUorgId = lot.uorg_id || lot.unidade_id;
      if (lotUorgId !== unidadeId) return false;
      // Filtrar por posto se selecionado
      if (postoId && lot.posto_id !== postoId) return false;
      // Apenas lotações ativas (sem data_fim ou data_fim futura)
      if (lot.data_fim) {
        const fim = new Date(lot.data_fim);
        if (fim < new Date()) return false;
      }
      return true;
    });
  });

  // Garantir que se houver um funcionario_id selecionado ele esteja na lista
  if (criarForm.funcionario_id && !filtered.some(f => f.id === Number(criarForm.funcionario_id))) {
    const current = todosFuncionarios.value.find(f => f.id === Number(criarForm.funcionario_id));
    if (current) {
      filtered.unshift(current);
    }
  }

  return [...filtered].sort((a, b) => (a.nome || '').localeCompare(b.nome || '', 'pt-BR', { sensitivity: 'base' }));
});

const editingRowFallback = ref<ColaboradorGradeRow | null>(null);

const selectedFuncionarioObj = computed(() => {
  const found = todosFuncionarios.value.find(f => f.id === Number(criarForm.funcionario_id));
  if (found) return found;
  if (editingRowFallback.value && editingRowFallback.value.funcionario_id === Number(criarForm.funcionario_id)) {
    return {
      id: editingRowFallback.value.funcionario_id,
      nome: editingRowFallback.value.nome,
      matricula: editingRowFallback.value.matricula,
      carga_horaria: editingRowFallback.value.carga_horaria_total || 40,
      cargo: { nome: editingRowFallback.value.cargo },
      cargo_id: editingRowFallback.value.cargo_id,
      escala: { sigla: editingRowFallback.value.escala_padrao },
      lotacoes: editingRowFallback.value.lotacoes_info || []
    };
  }
  return null;
});

const TURNOS_DIARISTA_MAP: Record<string, number> = {
  M: 6, M6: 6, MANHA: 6, 'MANHÃ': 6, M4: 6, M9: 6, M11: 6, M12: 6, M14: 6, M15: 6, M16: 6, M17: 6, M20: 6,
  T: 6, T6: 6, TARDE: 6, T4: 6, T7: 6, T11: 6, T12: 6, T13: 6, T15: 6, T16: 6, T17: 6, T19: 6, T20: 6,
  M1: 4, M2: 4, M3: 4, M5: 4, M19: 4,
  T1: 4, T2: 4, T3: 4, T5: 4, T9: 4,
  M8: 8, M10: 8, T8: 8, T10: 8, D8: 8, ADM: 8, '8H': 8,
  MT1: 8, MT2: 8, MT3: 8, MT4: 8, MT5: 8, MT6: 8, MT7: 8, MT8: 8, MT11: 8, MT12: 8, MT13: 8, MT16: 8,
  MT22: 8, MT23: 8, MT24: 8, MT25: 8, MT26: 8, MT27: 8, MT28: 8, MT29: 8, MT30: 8, MT47: 8, MT49: 8,
  MT9: 6, MT10: 6,
  MT14: 10, MT15: 10, MT17: 10, MT18: 10, MT19: 10, MT20: 10, MT21: 10,
  M13: 5, M18: 5, T14: 5, T18: 5,
  M7: 12,
  AFIN6: 6, AFIN4: 4, AFIN8: 8,
  FD6: 6, FD8: 8, FD: 6,
  FE4: 4, FE5: 5, FE6: 6, FE7: 7, FE8: 8
};

const TURNOS_PLANTONISTA_MAP: Record<string, number> = {
  D: 12, SD: 12, DIA: 12, DIURNO: 12, P12D: 12, '12X36': 12, P12: 12,
  D1: 12, D2: 12, D3: 12, D4: 12, D5: 12, D6: 12, D7: 12, D9: 12,
  N: 12, SN: 12, NOITE: 12, NOTURNO: 12, P12N: 12,
  N1: 12, N2: 12, N3: 12, N4: 12, N5: 12, N6: 12, N7: 12, N8: 12, N9: 12,
  FE10: 10, FE12: 12, FE12D: 12, FE12N: 12, FE16: 16, FE18: 18, FE20: 20, FE24: 24,
  P24: 24, '24H': 24, DN1: 24, DN2: 24, DN3: 24, DN4: 24, DN5: 24, DN6: 24,
  SOB: 12, SOB12: 12, SOB24: 24
};

const obterHorasDiaristaModal = (siglas: Array<string | null | undefined>, chSemanal: number, escalaPadrao?: any): number => {
  const turnosDiaristas: number[] = [];
  let qtdPlantonista = 0;
  let temFeriadoOuFerias = false;
  const auxDiarista = new Set(['FD', 'FD0', 'FD6', 'FD8', 'FE4', 'FE5', 'FE6', 'FE7', 'FE8']);

  for (const raw of siglas) {
    if (!raw) continue;
    const s = raw.trim().toUpperCase();
    if (s in TURNOS_PLANTONISTA_MAP) {
      qtdPlantonista++;
    } else if (s in TURNOS_DIARISTA_MAP && !auxDiarista.has(s)) {
      turnosDiaristas.push(TURNOS_DIARISTA_MAP[s]);
    } else if (['FR', 'FD', 'FD0', 'FD6', 'FD8', 'FER', 'FERIADO', 'FE', 'FERIAS', 'FÉRIAS'].includes(s) || auxDiarista.has(s)) {
      temFeriadoOuFerias = true;
    }
  }

  if (qtdPlantonista > 0 && qtdPlantonista >= turnosDiaristas.length) {
    return 0;
  }

  if (turnosDiaristas.length > 0) {
    const freq: Record<number, number> = {};
    for (const h of turnosDiaristas) {
      freq[h] = (freq[h] || 0) + 1;
    }
    return Number(Object.keys(freq).sort((a, b) => freq[Number(b)] - freq[Number(a)])[0]);
  }

  if (escalaPadrao) {
    const escSigla = (escalaPadrao.sigla || '').trim().toUpperCase();
    const escCodigo = (escalaPadrao.codigo || '').trim().toUpperCase();
    if (escSigla in TURNOS_DIARISTA_MAP) return TURNOS_DIARISTA_MAP[escSigla];
    if (
      ['DIARISTA', '5X2', 'ADM', 'SEG-SEX', '40H', '30H', '20H'].some(t => escSigla.includes(t)) ||
      escCodigo.includes('DIARISTA')
    ) {
      if (chSemanal === 30 || chSemanal === 24) return 6;
      if (chSemanal === 20) return 4;
      if (chSemanal === 40) return 8;
      return Math.round((chSemanal / 5) * 10) / 10;
    }
  }

  if (temFeriadoOuFerias && qtdPlantonista === 0) {
    if (chSemanal >= 40) return 8;
    if (chSemanal <= 20) return 4;
    return 6;
  }
  return 0;
};

const calcularHorasSigla = (
  sigla?: string | null,
  horasDiarista: number = 0,
  horasFeriasDia: number = 0,
  isDiaUtilSemana: boolean = true
): number => {
  if (!sigla) return 0;
  const s = sigla.trim().toUpperCase();

  // Folga diarista compensada com carga explícita
  if (s === 'FD6') {
    return isDiaUtilSemana ? (horasDiarista > 0 ? horasDiarista : 6) : 0;
  }
  if (s === 'FD8') {
    return isDiaUtilSemana ? (horasDiarista > 0 ? horasDiarista : 8) : 0;
  }

  // Marcação de feriado (FR, FD, FD0, FER, FERIADO):
  // Para diarista em dia de semana (seg-sex) conta como hora trabalhada; para plantonista ou fim de semana, 0h.
  if (['FR', 'FD', 'FD0', 'FER', 'FERIADO'].includes(s)) {
    return (horasDiarista > 0 && isDiaUtilSemana) ? horasDiarista : 0;
  }

  // Férias genéricas (FE): contabiliza horasFeriasDia nos dias de semana (seg-sex)
  if (['FE', 'FERIAS', 'FÉRIAS'].includes(s)) {
    return (isDiaUtilSemana && horasFeriasDia > 0) ? horasFeriasDia : 0;
  }

  // Mapeamentos padronizados (inclui FE6, FE8, FE12, FE12D, D6, N8, MT16, etc.)
  if (s in TURNOS_DIARISTA_MAP) return TURNOS_DIARISTA_MAP[s];
  if (s in TURNOS_PLANTONISTA_MAP) return TURNOS_PLANTONISTA_MAP[s];

  if (
    ['F', 'FOLGA', 'LM', 'LP', 'A', 'FJ', 'LIC', 'LMS', 'LMT', 'AF', 'AFASTAMENTO'].includes(s) ||
    s.startsWith('CH') ||
    s.startsWith('AB')
  ) {
    return 0;
  }

  // Verificar se há escala cadastrada com essa sigla ou código
  const escalaObj = escalas.value.find(e => e.sigla?.toUpperCase() === s || e.codigo?.toUpperCase() === s);
  if (escalaObj && escalaObj.inicio_jornada && escalaObj.fim_jornada) {
    const [hIni, mIni] = escalaObj.inicio_jornada.split(':').map(Number);
    const [hFim, mFim] = escalaObj.fim_jornada.split(':').map(Number);
    const minIni = hIni * 60 + (mIni || 0);
    const minFim = hFim * 60 + (mFim || 0);
    if (minFim > minIni) {
      return Math.round((minFim - minIni) / 60);
    } else if (minFim < minIni) {
      return Math.round((24 * 60 - minIni + minFim) / 60);
    } else {
      return 0;
    }
  }

  return 6;
};

const computedHorasCriarModal = computed(() => {
  const f = selectedFuncionarioObj.value;
  const chSemanal = f?.carga_horaria || f?.cargo?.carga_horaria || 40;
  const mes = Number(criarForm.mes);
  const ano = Number(criarForm.ano);
  const totalDias = new Date(ano, mes, 0).getDate();

  const siglasModal = criarDias.value.map(d => d.legenda_sigla);
  let horasDiarista = obterHorasDiaristaModal(siglasModal, chSemanal, f?.escala);

  const escalaSigla = f?.escala?.sigla?.toUpperCase() || '';
  const escalaCodigo = f?.escala?.codigo?.toUpperCase() || '';
  const temPlantaoModal = siglasModal.some(raw => raw && raw.trim().toUpperCase() in TURNOS_PLANTONISTA_MAP);

  const isDiarista = (
    horasDiarista > 0 ||
    (!temPlantaoModal && (
      (f?.escala && !f?.escala?.apenas_assistenciais) ||
      ['DIARISTA', '5X2', 'ADM', 'SEG-SEX', '40H', '30H', '20H'].some(term => escalaSigla.includes(term)) ||
      escalaCodigo.includes('DIARISTA')
    ))
  );
  if (isDiarista && horasDiarista === 0) {
    horasDiarista = Math.round((chSemanal / 5) * 10) / 10;
  }

  const feriados = feriadosMesCriarMap.value;
  let horasEscaladas = 0;
  const horasPorDia: Record<number, number> = {};
  const temAlgumDiaPreenchido = siglasModal.some(raw => raw && raw.trim() !== '');

  criarDias.value.forEach(d => {
    const diaNum = Number(d.dia);
    const isWk = isWeekendInMes(diaNum, mes, ano);
    const isFer = !!feriados[diaNum];
    const isDiaUtilSemana = !isWk;
    const horasFeriasDia = isDiaUtilSemana
      ? (horasDiarista > 0 ? horasDiarista : Math.round((chSemanal / 5) * 10) / 10)
      : 0;
    const siglaEfetiva = (d.legenda_sigla && d.legenda_sigla.trim() !== '')
      ? d.legenda_sigla
      : (isDiarista && isFer && isDiaUtilSemana && temAlgumDiaPreenchido ? 'FR' : '');
    const h = calcularHorasSigla(siglaEfetiva, horasDiarista, horasFeriasDia, isDiaUtilSemana);
    horasEscaladas += h;
    horasPorDia[diaNum] = h;
  });

  let diasUteis = 0;
  for (let d = 1; d <= totalDias; d++) {
    const isWk = isWeekendInMes(d, mes, ano);
    const isFer = !!feriados[d];
    const trabalhouNoFeriado = (horasPorDia[d] || 0) > 0;
    if (!isWk && (isDiarista || !isFer || trabalhouNoFeriado)) {
      diasUteis++;
    }
  }

  let tetoMensal = 0;
  if (isDiarista) {
    tetoMensal = Math.round(diasUteis * (chSemanal / 5.0));
  } else {
    tetoMensal = Math.round((chSemanal * totalDias) / 7.0);
  }

  const ultrapassou = horasEscaladas > tetoMensal;
  const horasExcedentes = Math.max(0, horasEscaladas - tetoMensal);
  const saldoRestante = Math.max(0, tetoMensal - horasEscaladas);
  const porcentagemAlocada = tetoMensal > 0 ? Math.min(100, Math.round((horasEscaladas / tetoMensal) * 100)) : 0;

  return {
    chSemanal,
    tetoMensal,
    horasEscaladas,
    ultrapassou,
    horasExcedentes,
    saldoRestante,
    porcentagemAlocada,
    isDiarista
  };
});

const onCriarUnidadeChange = () => {
  // Ao mudar a unidade, reseta o posto e colaborador (o filtro vai atualizar)
  criarForm.posto_id = null;
  criarForm.funcionario_id = 0;
};

const onCriarPostoChange = () => {
  // Ao selecionar um posto, preencher a unidade automaticamente
  if (criarForm.posto_id) {
    const posto = todosPostos.value.find(p => p.id === Number(criarForm.posto_id));
    if (posto && posto.uorg_id && posto.uorg_id !== criarForm.unidade_id) {
      criarForm.unidade_id = posto.uorg_id;
    }
  }
  // Reseta o colaborador selecionado (o filtro vai atualizar)
  criarForm.funcionario_id = 0;
};

const onFuncionarioChange = () => {
  // Não precisa mais alterar a unidade ao selecionar colaborador,
  // pois agora a unidade é selecionada primeiro
};

const openCriarModal = () => {
  modalError.value = '';
  isEditingCollaborator.value = false;
  editingGradeId.value = null;
  editingRowFallback.value = null;
  criarForm.funcionario_id = 0;
  criarForm.unidade_id = selectedUnidadeId.value || (unidades.value[0]?.id || 1);
  criarForm.posto_id = null;
  criarForm.mes = selectedMes.value;
  criarForm.ano = selectedAno.value;
  criarForm.status = 'Rascunho';
  criarForm.observacao = '';

  setupCriarDias();
  showCriarModal.value = true;
};

const openEditarGrade = async (row: ColaboradorGradeRow) => {
  modalError.value = '';
  isEditingCollaborator.value = true;
  editingGradeId.value = row.grade_id;
  editingRowFallback.value = row;
  criarForm.funcionario_id = Number(row.funcionario_id);
  
  // Garantir que a unidade corresponda à da linha clicada ou à UORG selecionada na tela
  const unidId = row.unidade_id ? Number(row.unidade_id) : (selectedUnidadeId.value || (unidades.value[0]?.id || 1));
  criarForm.unidade_id = unidId;

  // Garantir resolução do posto de serviço a partir de lotações ou fallback
  const lotacaoAtual = row.lotacoes_info?.find(l => Number(l.unidade_id) === unidId);
  const postoNomeEncontrado = (row as any).posto_nome || lotacaoAtual?.posto_nome;
  const postoObj = postoNomeEncontrado ? todosPostos.value.find(p => p.nome === postoNomeEncontrado) : null;
  criarForm.posto_id = (row as any).posto_id || (postoObj ? postoObj.id : (lotacaoAtual ? (todosPostos.value.find(p => p.nome === lotacaoAtual.posto_nome)?.id || null) : null));

  criarForm.mes = selectedMes.value;
  criarForm.ano = selectedAno.value;
  criarForm.status = row.grade_status || 'Rascunho';
  criarForm.observacao = row.observacao || '';

  // Buscar dados completos e atualizados do funcionário pela API se disponível
  try {
    const resFunc = await api.get(`/api/funcionarios/${row.funcionario_id}`);
    if (resFunc.data) {
      const idx = todosFuncionarios.value.findIndex(f => f.id === Number(row.funcionario_id));
      if (idx > -1) {
        todosFuncionarios.value[idx] = resFunc.data;
      } else {
        todosFuncionarios.value.push(resFunc.data);
      }
    }
  } catch (e) {
    console.warn('Não foi possível buscar dados adicionais do funcionário:', e);
  }

  // Buscar detalhes da grade caso exista observação gravada
  if (row.grade_id) {
    try {
      const resGrade = await gradeService.getGradeById(Number(row.grade_id));
      if (resGrade && resGrade.observacao !== undefined) {
        criarForm.observacao = resGrade.observacao || '';
      }
    } catch (e) {
      console.warn('Não foi possível buscar detalhes da grade:', e);
    }
  }

  const numDias = totalDiasMesCriar.value;
  const diasList: CriarDiaItem[] = [];

  for (let d = 1; d <= numDias; d++) {
    const existingDia = row.dias.find(item => item.dia === d);
    diasList.push({
      dia: d,
      legenda_sigla: existingDia?.sigla || '',
      descricao: existingDia?.descricao || undefined
    });
  }
  criarDias.value = diasList;
  showCriarModal.value = true;
};

const setupCriarDias = () => {
  const numDias = totalDiasMesCriar.value;
  const diasList: CriarDiaItem[] = [];
  for (let d = 1; d <= numDias; d++) {
    diasList.push({
      dia: d,
      legenda_sigla: ''
    });
  }
  criarDias.value = diasList;
};

const applyQuickFill = (mode: 'weekdays' | 'all') => {
  if (!quickFillSigla.value) {
    alert('Selecione primeiro uma sigla para aplicar.');
    return;
  }
  const feriados = feriadosMesCriarMap.value;
  criarDias.value.forEach(d => {
    const isWk = isWeekendInMes(d.dia, criarForm.mes, criarForm.ano);
    const isFeriado = !!feriados[d.dia];

    if (mode === 'all') {
      d.legenda_sigla = quickFillSigla.value;
      d.descricao = undefined;
    } else if (mode === 'weekdays') {
      if (isWk) {
        d.legenda_sigla = 'F'; // Folga no fim de semana
        d.descricao = undefined;
      } else {
        if (isFeriado && respeitarFeriadosDiarista.value) {
          // Para colaboradores Diaristas em dias de feriado oficial: folga de feriado
          d.legenda_sigla = 'FR';
          d.descricao = `Feriado: ${feriados[d.dia]}`;
        } else {
          d.legenda_sigla = quickFillSigla.value;
          d.descricao = undefined;
        }
      }
    }
  });
};

const clearAllDias = () => {
  criarDias.value.forEach(d => {
    d.legenda_sigla = '';
  });
};

const closeCriarModal = () => {
  showCriarModal.value = false;
  isEditingCollaborator.value = false;
};

const saveCriarGrade = async () => {
  modalError.value = '';

  if (!criarForm.funcionario_id) {
    modalError.value = 'Selecione um colaborador.';
    return;
  }
  if (!criarForm.unidade_id) {
    modalError.value = 'Selecione uma unidade.';
    return;
  }

  if (computedHorasCriarModal.value.ultrapassou && !authStore.isAdmin) {
    modalError.value = `Atenção: A escala atual totaliza ${computedHorasCriarModal.value.horasEscaladas}h e ultrapassa a carga horária contratual mensal permitida (${computedHorasCriarModal.value.tetoMensal}h). Reduza os turnos antes de salvar.`;
    if (modalBodyRef.value) {
      modalBodyRef.value.scrollTop = 0;
    }
    return;
  }

  saving.value = true;

  const diasPayload = criarDias.value
    .filter(d => d.legenda_sigla && d.legenda_sigla.trim() !== '')
    .map(d => ({
      dia: Number(d.dia),
      legenda_sigla: d.legenda_sigla.toUpperCase().trim(),
      descricao: d.descricao
    }));

  try {
    const savedUnidadeId = Number(criarForm.unidade_id);
    const savedMes = Number(criarForm.mes);
    const savedAno = Number(criarForm.ano);

    if (editingGradeId.value) {
      await gradeService.updateGrade(Number(editingGradeId.value), {
        posto_id: criarForm.posto_id ? Number(criarForm.posto_id) : null,
        status: criarForm.status,
        observacao: criarForm.observacao,
        permitir_excedente: authStore.isAdmin && computedHorasCriarModal.value.ultrapassou,
        dias: diasPayload
      });
      showToast('Escala atualizada com sucesso!');
    } else {
      await gradeService.createGrade({
        funcionario_id: Number(criarForm.funcionario_id),
        unidade_id: savedUnidadeId,
        posto_id: criarForm.posto_id ? Number(criarForm.posto_id) : null,
        mes: savedMes,
        ano: savedAno,
        status: criarForm.status,
        observacao: criarForm.observacao,
        permitir_excedente: authStore.isAdmin && computedHorasCriarModal.value.ultrapassou,
        dias: diasPayload
      });
      showToast('Nova escala salva com sucesso!');
    }

    // Sincroniza a tela principal com a unidade, mês e ano da escala recém-salva
    // para garantir que a linha do colaborador apareça imediatamente preenchida
    selectedUnidadeId.value = savedUnidadeId;
    selectedMes.value = savedMes;
    selectedAno.value = savedAno;

    closeCriarModal();
    await fetchData();
  } catch (err: any) {
    console.error('Erro ao salvar escala:', err);
    if (err.response?.data?.detail) {
      modalError.value = err.response.data.detail;
    } else {
      modalError.value = 'Erro ao salvar a escala. Verifique as informações e tente novamente.';
    }
    // Rola o modal até o topo para garantir que o usuário veja o alerta de erro imediatamente
    if (modalBodyRef.value) {
      modalBodyRef.value.scrollTop = 0;
    }
  } finally {
    saving.value = false;
  }
};

// ==========================================
// MODAL 2: COPIAR GRADE
// ==========================================
const showCopiarModal = ref(false);
const copiando = ref(false);
const copiarError = ref('');
const searchDestinoNome = ref('');
const loadingTargetGrades = ref(false);
const targetFuncionariosComGrade = ref<Set<number>>(new Set());

const copiarForm = reactive({
  source_func_id: 0,
  source_func_ids: [] as number[],
  source_unidade_id: 1,
  source_mes: 1,
  source_ano: 2026,
  target_func_ids: [] as number[],
  target_unidade_id: 1,
  target_posto_id: null as number | null,
  target_mes: 1,
  target_ano: 2026
});

// Colaboradores que têm grade/escala cadastrada no mês de origem, respeitando os filtros ativos
const funcionariosOrigemDisponiveis = computed(() => {
  let list = [...matrixData.value.filter(r => r.grade_id)];

  // Respeita filtro de Cargo / Categoria ativo na tela
  if (selectedCargoId.value) {
    const targetCid = Number(selectedCargoId.value);
    list = list.filter(r => Number(r.cargo_id) === targetCid);
  }

  // Respeita filtro de Posto de Serviço ativo na tela
  if (selectedPostoId.value) {
    const targetPid = Number(selectedPostoId.value);
    list = list.filter(r => {
      if (r.posto_id && Number(r.posto_id) === targetPid) return true;
      if (r.lotacoes_info && r.lotacoes_info.some((l: any) => l.posto_id === targetPid)) return true;
      const matchingPosto = todosPostos.value.find(p => p.id === targetPid);
      if (matchingPosto && r.posto_nome && r.posto_nome.trim().toLowerCase() === matchingPosto.nome.trim().toLowerCase()) return true;
      return false;
    });
  }

  return list.sort((a, b) => 
    (a.nome || '').localeCompare(b.nome || '', 'pt-BR', { sensitivity: 'base' })
  );
});

// Lista de colaboradores filtrada pelo campo de pesquisa dentro do modal
const listaOrigemFiltradaParaCopia = computed(() => {
  const query = searchDestinoNome.value.trim().toLowerCase();
  if (!query) {
    return funcionariosOrigemDisponiveis.value;
  }
  return funcionariosOrigemDisponiveis.value.filter(f => {
    const nome = (f.nome || '').toLowerCase();
    const matricula = (f.matricula || '').toLowerCase();
    const cargo = (f.cargo || '').toLowerCase();
    const posto = (f.posto_nome || '').toLowerCase();
    return nome.includes(query) || matricula.includes(query) || cargo.includes(query) || posto.includes(query);
  });
});

const allOrigemFiltradosSelected = computed(() => {
  const list = listaOrigemFiltradaParaCopia.value;
  return list.length > 0 && list.every(f => copiarForm.source_func_ids.includes(Number(f.funcionario_id)));
});

const toggleSelectAllOrigem = () => {
  const list = listaOrigemFiltradaParaCopia.value;
  if (allOrigemFiltradosSelected.value) {
    const filteredIds = new Set(list.map(f => Number(f.funcionario_id)));
    copiarForm.source_func_ids = copiarForm.source_func_ids.filter(id => !filteredIds.has(id));
  } else {
    const currentIds = new Set(copiarForm.source_func_ids);
    list.forEach(f => currentIds.add(Number(f.funcionario_id)));
    copiarForm.source_func_ids = Array.from(currentIds);
  }
};

const selecionarTodosFiltradosOrigem = () => {
  const ids = funcionariosOrigemDisponiveis.value.map(f => Number(f.funcionario_id));
  copiarForm.source_func_ids = ids;
};

const carregarFuncionariosDestinoComGrade = async () => {
  if (!showCopiarModal.value) return;
  loadingTargetGrades.value = true;
  try {
    const res = await gradeService.getMatrix({
      mes: Number(copiarForm.target_mes),
      ano: Number(copiarForm.target_ano),
      unidade_id: copiarForm.target_unidade_id ? Number(copiarForm.target_unidade_id) : undefined,
      posto_id: copiarForm.target_posto_id ? Number(copiarForm.target_posto_id) : undefined,
      cargo_id: selectedCargoId.value ? Number(selectedCargoId.value) : undefined
    });
    const comGrade = new Set<number>();
    res.forEach(r => {
      if (r.grade_id) {
        comGrade.add(Number(r.funcionario_id));
      }
    });
    targetFuncionariosComGrade.value = comGrade;
  } catch (error) {
    console.error('Erro ao carregar grades existentes no destino:', error);
  } finally {
    loadingTargetGrades.value = false;
  }
};

watch(
  [() => copiarForm.target_mes, () => copiarForm.target_ano, () => copiarForm.target_unidade_id, () => copiarForm.target_posto_id],
  () => {
    if (showCopiarModal.value) {
      carregarFuncionariosDestinoComGrade();
    }
  }
);

// Postos da Unidade Alvo selecionada no modal de cópia
const postosDaUnidadeAlvo = computed(() => {
  const unidId = Number(copiarForm.target_unidade_id);
  if (!unidId) return [];
  return todosPostos.value
    .filter(p => Number(p.uorg_id || p.unidade_id) === unidId)
    .sort((a, b) => (a.nome || '').localeCompare(b.nome || '', 'pt-BR', { sensitivity: 'base' }));
});

const openCopiarModal = async () => {
  copiarError.value = '';
  searchDestinoNome.value = '';
  copiarForm.source_unidade_id = selectedUnidadeId.value || (unidades.value[0]?.id || 1);
  copiarForm.source_mes = selectedMes.value;
  copiarForm.source_ano = selectedAno.value;
  copiarForm.target_unidade_id = selectedUnidadeId.value || (unidades.value[0]?.id || 1);
  copiarForm.target_posto_id = selectedPostoId.value ? Number(selectedPostoId.value) : null;

  // Próximo mês por padrão
  let proxMes = selectedMes.value + 1;
  let proxAno = selectedAno.value;
  if (proxMes > 12) {
    proxMes = 1;
    proxAno += 1;
  }
  copiarForm.target_mes = proxMes;
  copiarForm.target_ano = proxAno;

  // Inicialmente marca todos os colaboradores filtrados com escala na tela para serem copiados
  const idsOrigem = funcionariosOrigemDisponiveis.value.map(f => Number(f.funcionario_id));
  copiarForm.source_func_ids = idsOrigem;
  copiarForm.target_func_ids = [...idsOrigem];

  showCopiarModal.value = true;
  await carregarFuncionariosDestinoComGrade();
};

const closeCopiarModal = () => {
  showCopiarModal.value = false;
  searchDestinoNome.value = '';
};

const executeCopiarGrade = async () => {
  if (copiarForm.source_func_ids.length === 0) {
    copiarError.value = 'Selecione ao menos um colaborador para copiar a escala.';
    return;
  }

  copiando.value = true;
  copiarError.value = '';

  try {
    const funcs = copiarForm.source_func_ids.map(Number);
    await gradeService.copyGrade({
      source_func_ids: funcs,
      source_unidade_id: Number(copiarForm.source_unidade_id),
      source_mes: Number(copiarForm.source_mes),
      source_ano: Number(copiarForm.source_ano),
      target_func_ids: funcs,
      target_unidade_id: Number(copiarForm.target_unidade_id),
      target_posto_id: copiarForm.target_posto_id ? Number(copiarForm.target_posto_id) : undefined,
      target_mes: Number(copiarForm.target_mes),
      target_ano: Number(copiarForm.target_ano)
    });

    closeCopiarModal();
    // Muda a visualização para o mês/ano de destino para conferir as escalas geradas
    selectedMes.value = Number(copiarForm.target_mes);
    selectedAno.value = Number(copiarForm.target_ano);
    if (copiarForm.target_unidade_id) {
      selectedUnidadeId.value = Number(copiarForm.target_unidade_id);
    }
    toastMessage.value = `${funcs.length} escala(s) copiada(s) com sucesso para ${mesesNomes[copiarForm.target_mes - 1]}/${copiarForm.target_ano}!`;
    setTimeout(() => {
      toastMessage.value = '';
    }, 4500);

    await fetchData();
  } catch (err: any) {
    if (err.response?.data?.detail) {
      copiarError.value = err.response.data.detail;
    } else {
      copiarError.value = 'Erro ao copiar as escalas.';
    }
  } finally {
    copiando.value = false;
  }
};

// ==========================================
// Lifecycle Hook
// ==========================================
let tableResizeObserver: ResizeObserver | null = null;

watch([() => matrixData.value.length, () => totalDiasMes.value], () => {
  syncScrollWidth();
});

onMounted(async () => {
  await fetchAuxiliaryData();
  await fetchData();

  nextTick(() => {
    syncScrollWidth();
    if (matrixTableRef.value && typeof ResizeObserver !== 'undefined') {
      tableResizeObserver = new ResizeObserver(() => {
        syncScrollWidth();
      });
      tableResizeObserver.observe(matrixTableRef.value);
    }
  });

  window.addEventListener('resize', syncScrollWidth);
});

onUnmounted(() => {
  window.removeEventListener('resize', syncScrollWidth);
  if (tableResizeObserver) {
    tableResizeObserver.disconnect();
    tableResizeObserver = null;
  }
});
</script>
