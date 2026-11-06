<template>
  <div class="space-y-6">
    <!-- Header with Period Selection -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white p-5 rounded-2xl border border-gray-200 shadow-xs">
      <div>
        <h1 class="text-xl sm:text-2xl font-black text-gray-900 flex items-center gap-2">
          <BuildingLibraryIcon class="h-7 w-7 text-purple-700" />
          <span>Painel Institucional DIVGP · Gestão de Escalas</span>
        </h1>
        <p class="text-xs sm:text-sm text-gray-500 mt-1">
          Acompanhamento e homologação em tempo real de todas as escalas e status de entrega por setor e unidade hospitalar pela Divisão de Gestão de Pessoas (DIVGP).
        </p>
      </div>

      <!-- Month / Year Selector -->
      <div class="flex items-center gap-2 bg-gray-50 p-1.5 rounded-xl border border-gray-200 shrink-0">
        <select v-model="selectedMes" @change="fetchAllData" class="form-control text-xs font-bold py-1.5 w-auto">
          <option v-for="(nome, idx) in mesesNomes" :key="idx" :value="idx + 1">
            {{ nome }}
          </option>
        </select>
        <select v-model="selectedAno" @change="fetchAllData" class="form-control text-xs font-bold py-1.5 w-auto">
          <option v-for="ano in anosDisponiveis" :key="ano" :value="ano">
            {{ ano }}
          </option>
        </select>
        <button 
          @click="fetchAllData" 
          class="p-1.5 bg-paper-primary hover:bg-paper-primary-hover text-white rounded-lg transition-colors cursor-pointer"
          title="Recarregar Dados"
        >
          <ArrowPathIcon class="h-4 w-4" :class="{ 'animate-spin': loading || loadingEscalas }" />
        </button>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="flex items-center gap-2 border-b border-gray-200">
      <button 
        @click="activeTab = 'todas_escalas'" 
        class="flex items-center gap-2 px-5 py-3 font-bold text-sm border-b-2 transition-all cursor-pointer"
        :class="activeTab === 'todas_escalas' ? 'border-purple-600 text-purple-700 bg-purple-50/50 rounded-t-lg' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
      >
        <ListBulletIcon class="h-4 w-4" />
        <span>Todas as Escalas & Status</span>
        <span class="px-2 py-0.5 rounded-full text-xs font-black bg-purple-100 text-purple-800">
          {{ todasEscalasLista.length }}
        </span>
      </button>

      <button 
        @click="activeTab = 'unidades'" 
        class="flex items-center gap-2 px-5 py-3 font-bold text-sm border-b-2 transition-all cursor-pointer"
        :class="activeTab === 'unidades' ? 'border-purple-600 text-purple-700 bg-purple-50/50 rounded-t-lg' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
      >
        <BuildingOfficeIcon class="h-4 w-4" />
        <span>Resumo por UORG / Unidades</span>
        <span class="px-2 py-0.5 rounded-full text-xs font-black bg-gray-100 text-gray-700">
          {{ sumario.total_unidades }}
        </span>
      </button>
    </div>

    <!-- TAB 1: TODAS AS ESCALAS & STATUS (VISÃO NOMINAL INSTITUCIONAL) -->
    <div v-if="activeTab === 'todas_escalas'" class="space-y-6 animate-fade-in">
      <!-- KPI Status Mini Cards -->
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <!-- Total -->
        <div class="bg-white p-3.5 rounded-xl border border-gray-200 shadow-xs">
          <p class="text-[10px] font-bold uppercase text-gray-400">Total Colaboradores</p>
          <p class="text-xl font-black text-gray-900 mt-0.5">{{ countStatusTotal }}</p>
        </div>

        <!-- Publicadas -->
        <div class="bg-white p-3.5 rounded-xl border border-emerald-200 bg-emerald-50/30 shadow-xs">
          <p class="text-[10px] font-bold uppercase text-emerald-700">🟢 Publicadas (DIVGP)</p>
          <p class="text-xl font-black text-emerald-800 mt-0.5">{{ countStatusPublicadas }}</p>
        </div>

        <!-- Aguardando Superior -->
        <div class="bg-white p-3.5 rounded-xl border border-blue-200 bg-blue-50/30 shadow-xs">
          <p class="text-[10px] font-bold uppercase text-blue-700">🔵 Aguardando Sup.</p>
          <p class="text-xl font-black text-blue-800 mt-0.5">{{ countStatusEnviadas }}</p>
        </div>

        <!-- Devolvidas -->
        <div class="bg-white p-3.5 rounded-xl border border-rose-200 bg-rose-50/30 shadow-xs">
          <p class="text-[10px] font-bold uppercase text-rose-700">🟠 Devolvidas p/ Ajuste</p>
          <p class="text-xl font-black text-rose-800 mt-0.5">{{ countStatusDevolvidas }}</p>
        </div>

        <!-- Em Elaboração -->
        <div class="bg-white p-3.5 rounded-xl border border-gray-200 bg-gray-50/50 shadow-xs">
          <p class="text-[10px] font-bold uppercase text-gray-500">⚪ Em Elaboração</p>
          <p class="text-xl font-black text-gray-700 mt-0.5">{{ countStatusRascunho }}</p>
        </div>

        <!-- Sem Escala -->
        <div class="bg-white p-3.5 rounded-xl border border-amber-200 bg-amber-50/30 shadow-xs">
          <p class="text-[10px] font-bold uppercase text-amber-700">🔴 Sem Escala</p>
          <p class="text-xl font-black text-amber-800 mt-0.5">{{ countStatusSemEscala }}</p>
        </div>
      </div>

      <!-- Filters Section -->
      <Card>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 items-end">
          <!-- Search -->
          <div class="form-group mb-0">
            <label class="form-label">Buscar Colaborador</label>
            <div class="relative">
              <input 
                v-model="searchEscalaTerm" 
                type="text" 
                placeholder="Nome ou SIAPE..."
                class="form-control pl-8 text-xs font-medium"
              />
              <MagnifyingGlassIcon class="h-4 w-4 text-gray-400 absolute left-2.5 top-2.5" />
            </div>
          </div>

          <!-- Filter Status -->
          <div class="form-group mb-0">
            <label class="form-label">Status da Escala</label>
            <select v-model="filterEscalaStatus" class="form-control text-xs font-medium">
              <option value="TODOS">Todos os Status</option>
              <option value="Enviada_Superior">🔵 Aguardando Chefia Superior</option>
              <option value="Devolvida">🟠 Devolvida para Ajuste</option>
              <option value="Rascunho">⚪ Em Elaboração</option>
              <option value="Publicada">🟢 Publicada (Oficial DIVGP)</option>
              <option value="SEM_ESCALA">🔴 Sem Escala Cadastrada</option>
            </select>
          </div>

          <!-- Filter UORG Pai -->
          <div class="form-group mb-0">
            <label class="form-label">UORG Pai (Gerência / Divisão)</label>
            <select v-model="filterEscalaUorgPai" class="form-control text-xs font-medium">
              <option value="TODOS">Todas as UORGs Pai</option>
              <option v-for="p in uorgsPaiDisponiveis" :key="p" :value="p">
                {{ p }}
              </option>
            </select>
          </div>

          <!-- Filter UORG -->
          <div class="form-group mb-0">
            <label class="form-label">UORG / Unidade</label>
            <select v-model="filterEscalaUorg" class="form-control text-xs font-medium">
              <option value="TODOS">Todas as UORGs</option>
              <option v-for="u in uorgsFiltradasSelect" :key="u.id" :value="u.id">
                {{ u.nome }}
              </option>
            </select>
          </div>

          <!-- Filter Cargo -->
          <div class="form-group mb-0">
            <label class="form-label">Categoria / Cargo</label>
            <select v-model="filterEscalaCargo" class="form-control text-xs font-medium">
              <option value="TODOS">Todos os Cargos</option>
              <option v-for="c in sortedCargosDisponiveis" :key="c.id" :value="c.id">
                {{ c.nome }}
              </option>
            </select>
          </div>
        </div>

        <!-- Table of All Scales -->
        <div class="mt-4 overflow-x-auto border border-gray-200 rounded-xl overflow-hidden">
          <table class="w-full text-xs text-left">
            <thead class="bg-gray-50 text-paper-sidebar uppercase font-bold text-[11px] border-b border-gray-200 select-none">
              <tr>
                <th class="px-3.5 py-3">Colaborador / SIAPE</th>
                <th class="px-3 py-3">Cargo · Cód. Escala</th>
                <th class="px-3.5 py-3">UORG · UORG Pai</th>
                <th class="px-2.5 py-3">Posto</th>
                <th class="px-2.5 py-3 text-center">Carga Horária</th>
                <th class="px-3 py-3 text-center">Status da Escala</th>
                <th class="px-3 py-3">Observações / Motivo</th>
                <th class="px-3 py-3 text-center">Ações DIVGP</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-if="loadingEscalas">
                <td colspan="8" class="px-4 py-12 text-center text-gray-500">
                  <div class="flex flex-col items-center justify-center gap-2">
                    <div class="w-7 h-7 border-4 border-paper-primary border-t-transparent rounded-full animate-spin"></div>
                    <span>Carregando todas as escalas do hospital...</span>
                  </div>
                </td>
              </tr>

              <tr v-else-if="filteredTodasEscalas.length === 0">
                <td colspan="8" class="px-4 py-12 text-center text-gray-500">
                  <p class="font-medium text-gray-700">Nenhuma escala encontrada para os filtros selecionados.</p>
                  <p class="text-xs text-gray-400 mt-1">Tente ajustar o status, a unidade ou o termo de busca.</p>
                </td>
              </tr>

              <tr 
                v-else 
                v-for="item in filteredTodasEscalas" 
                :key="`${item.funcionario_id}-${item.uorg_id}`" 
                class="hover:bg-slate-50 transition-colors group"
              >
                <!-- Colaborador -->
                <td class="px-3.5 py-2.5 font-medium text-gray-900">
                  <div class="font-bold text-gray-900 truncate max-w-[200px]" :title="item.nome">{{ item.nome }}</div>
                  <div class="text-[10px] text-gray-500 font-mono">SIAPE: {{ item.matricula }}</div>
                </td>

                <!-- Cargo e Escala Padrão -->
                <td class="px-3 py-2.5">
                  <div class="text-gray-800 font-medium truncate max-w-[170px]" :title="item.cargo">{{ item.cargo }}</div>
                  <div class="flex items-center gap-1.5 mt-0.5 text-[10px]">
                    <span class="font-semibold text-purple-700 bg-purple-50 px-1.5 py-0.2 rounded border border-purple-200">
                      Escala: {{ item.escala_padrao }}
                    </span>
                    <span v-if="item.is_diarista" class="text-sky-700 bg-sky-50 px-1 py-0.2 rounded font-bold border border-sky-200">
                      Diarista
                    </span>
                  </div>
                </td>

                <!-- UORG e UORG Pai -->
                <td class="px-3.5 py-2.5">
                  <div class="font-semibold text-gray-800 text-[11px] truncate max-w-[210px]" :title="item.uorg_nome">
                    {{ item.uorg_nome }}
                  </div>
                  <div class="text-[10px] text-gray-400 truncate max-w-[210px]" :title="item.uorg_pai_nome">
                    ↳ {{ item.uorg_pai_nome }}
                  </div>
                </td>

                <!-- Posto -->
                <td class="px-2.5 py-2.5 text-gray-600 text-[11px]">
                  {{ item.posto_nome }}
                </td>

                <!-- Carga Horária -->
                <td class="px-2.5 py-2.5 text-center">
                  <div class="font-bold text-[11px]" :class="item.total_horas_escaladas >= item.carga_horaria_mensal_teto ? 'text-emerald-700' : 'text-gray-800'">
                    {{ item.total_horas_escaladas }}h / {{ item.carga_horaria_mensal_teto }}h
                  </div>
                  <div class="text-[10px]" :class="item.saldo_horas > 0 ? 'text-amber-600' : (item.saldo_horas < 0 ? 'text-rose-600 font-bold' : 'text-emerald-600 font-bold')">
                    <span v-if="item.saldo_horas > 0">Faltam {{ item.saldo_horas }}h</span>
                    <span v-else-if="item.saldo_horas < 0">Excede +{{ Math.abs(item.saldo_horas) }}h</span>
                    <span v-else>✓ 100%</span>
                  </div>
                </td>

                <!-- Status da Escala -->
                <td class="px-3 py-2.5 text-center">
                  <span 
                    class="px-2 py-0.5 rounded-full text-[10px] font-bold border inline-flex items-center gap-1"
                    :class="{
                      'bg-emerald-100 text-emerald-900 border-emerald-300': item.grade_status === 'Publicada',
                      'bg-blue-100 text-blue-900 border-blue-300': item.grade_status === 'Enviada_Superior' || item.grade_status === 'Enviada',
                      'bg-rose-100 text-rose-900 border-rose-300': item.grade_status === 'Devolvida',
                      'bg-amber-100 text-amber-900 border-amber-300': item.grade_status === 'Aprovada',
                      'bg-gray-100 text-gray-700 border-gray-300': item.grade_status === 'Rascunho',
                      'bg-red-50 text-red-800 border-red-200': item.grade_status === 'Sem Escala'
                    }"
                  >
                    <span v-if="item.grade_status === 'Publicada'">🟢 Publicada (DIVGP)</span>
                    <span v-else-if="item.grade_status === 'Enviada_Superior' || item.grade_status === 'Enviada'">🔵 Aguardando Sup.</span>
                    <span v-else-if="item.grade_status === 'Devolvida'">🟠 Devolvida</span>
                    <span v-else-if="item.grade_status === 'Aprovada'">🟡 Aprovada</span>
                    <span v-else-if="item.grade_status === 'Rascunho'">⚪ Em Elaboração</span>
                    <span v-else>🔴 Sem Escala</span>
                  </span>
                </td>

                <!-- Observações -->
                <td class="px-3 py-2.5 text-[10px] text-gray-500 max-w-[180px]">
                  <div v-if="item.observacao" class="truncate text-amber-800 font-medium bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200" :title="item.observacao">
                    💬 {{ item.observacao }}
                  </div>
                  <div v-else-if="item.login_responsavel" class="text-gray-400">
                    Alt: {{ item.login_responsavel }}
                  </div>
                  <div v-else class="text-gray-300">-</div>
                </td>

                <!-- Ações DIVGP -->
                <td class="px-3 py-2.5 text-center space-x-1 whitespace-nowrap">
                  <!-- Homologar & Publicar Oficial (DIVGP pode sempre) -->
                  <button 
                    v-if="item.grade_id && item.grade_status !== 'Publicada'" 
                    @click="publishEscalaDivgp(item.grade_id)" 
                    class="p-1 text-emerald-700 hover:bg-emerald-50 rounded transition-colors inline-flex cursor-pointer"
                    title="Homologar e Publicar Escala para a DIVGP"
                  >
                    <CheckCircleIcon class="h-4 w-4" />
                  </button>

                  <!-- Devolver com Apontamento -->
                  <button 
                    v-if="item.grade_id && (item.grade_status === 'Enviada_Superior' || item.grade_status === 'Enviada')" 
                    @click="devolverEscalaDivgp(item.grade_id)" 
                    class="p-1 text-amber-600 hover:bg-amber-50 rounded transition-colors inline-flex cursor-pointer"
                    title="Devolver Escala para Ajustes da Chefia Local"
                  >
                    <ArrowUturnLeftIcon class="h-4 w-4" />
                  </button>

                  <!-- Reabrir Escala Publicada -->
                  <button 
                    v-if="item.grade_id && item.grade_status === 'Publicada'" 
                    @click="reabrirEscalaDivgp(item.grade_id)" 
                    class="p-1 text-amber-600 hover:bg-amber-50 rounded transition-colors inline-flex cursor-pointer"
                    title="Reabrir Escala (Retornar para Rascunho / Desbloquear)"
                  >
                    <LockOpenIcon class="h-4 w-4" />
                  </button>

                  <!-- Abrir Módulo de Escala da UORG -->
                  <router-link 
                    :to="`/grade?uorg_id=${item.uorg_id}&mes=${selectedMes}&ano=${selectedAno}`"
                    class="p-1 text-purple-700 hover:bg-purple-50 rounded transition-colors inline-flex cursor-pointer"
                    title="Abrir Matriz Completa da Escala"
                  >
                    <ArrowTopRightOnSquareIcon class="h-4 w-4" />
                  </router-link>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>
    </div>

    <!-- TAB 2: RESUMO CONSOLIDADO POR UNIDADE (UORG) -->
    <div v-if="activeTab === 'unidades'" class="space-y-6 animate-fade-in">
      <!-- KPI Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Total Unidades -->
        <div class="bg-white p-4 rounded-xl border border-gray-200 shadow-xs flex items-center gap-3">
          <div class="p-3 bg-blue-50 rounded-xl text-blue-700">
            <BuildingOfficeIcon class="h-6 w-6" />
          </div>
          <div>
            <p class="text-[11px] font-bold uppercase text-gray-400">Total de Unidades</p>
            <p class="text-2xl font-black text-gray-900">{{ sumario.total_unidades }}</p>
          </div>
        </div>

        <!-- 100% Homologadas -->
        <div class="bg-white p-4 rounded-xl border border-gray-200 shadow-xs flex items-center gap-3">
          <div class="p-3 bg-emerald-50 rounded-xl text-emerald-700">
            <CheckBadgeIcon class="h-6 w-6" />
          </div>
          <div>
            <p class="text-[11px] font-bold uppercase text-gray-400">100% Publicadas</p>
            <p class="text-2xl font-black text-emerald-700">{{ sumario.unidades_100 }}</p>
          </div>
        </div>

        <!-- Unidades Pendentes -->
        <div class="bg-white p-4 rounded-xl border border-gray-200 shadow-xs flex items-center gap-3">
          <div class="p-3 bg-amber-50 rounded-xl text-amber-700">
            <ExclamationTriangleIcon class="h-6 w-6" />
          </div>
          <div>
            <p class="text-[11px] font-bold uppercase text-gray-400">Com Pendências</p>
            <p class="text-2xl font-black text-amber-700">{{ sumario.unidades_pendentes }}</p>
          </div>
        </div>

        <!-- Percentual Geral -->
        <div class="bg-white p-4 rounded-xl border border-gray-200 shadow-xs flex flex-col justify-between">
          <div class="flex items-center justify-between">
            <p class="text-[11px] font-bold uppercase text-gray-400">Conformidade Geral</p>
            <span class="text-xs font-bold" :class="sumario.percentual_geral >= 80 ? 'text-emerald-700' : 'text-amber-700'">
              {{ sumario.percentual_geral }}%
            </span>
          </div>
          <div class="mt-2">
            <div class="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
              <div 
                class="h-full rounded-full transition-all duration-500" 
                :class="sumario.percentual_geral === 100 ? 'bg-emerald-500' : 'bg-blue-600'"
                :style="{ width: `${sumario.percentual_geral}%` }"
              ></div>
            </div>
            <p class="text-[10px] text-gray-500 mt-1">
              {{ sumario.total_publicadas }} de {{ sumario.total_colaboradores }} grades publicadas
            </p>
          </div>
        </div>
      </div>

      <!-- Filters and Table -->
      <Card>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4 items-end">
          <div class="form-group mb-0">
            <label class="form-label">Buscar Unidade</label>
            <div class="relative">
              <input 
                v-model="searchTerm" 
                type="text" 
                placeholder="Nome da unidade..."
                class="form-control pl-9 text-sm"
              />
              <MagnifyingGlassIcon class="h-4 w-4 text-gray-400 absolute left-3 top-3" />
            </div>
          </div>

          <div class="form-group mb-0">
            <label class="form-label">Filtrar por Status</label>
            <select v-model="filterStatus" class="form-control text-sm">
              <option value="TODOS">Todas as Unidades</option>
              <option value="HOMOLOGADA_100">100% Homologadas (Concluídas)</option>
              <option value="PARCIAL">Parcialmente Enviadas</option>
              <option value="SEM_ENVIO">Sem Envio de Grades</option>
            </select>
          </div>

          <div class="form-group mb-0">
            <label class="form-label">Filtrar por UORG Pai</label>
            <select v-model="filterSetor" class="form-control text-sm">
              <option value="TODOS">Todas as UORGs Pai</option>
              <option v-for="setorNome in setoresDisponiveis" :key="setorNome" :value="setorNome">
                {{ setorNome }}
              </option>
            </select>
          </div>
        </div>

        <!-- Units Table -->
        <div class="overflow-x-auto border border-gray-200 rounded-xl overflow-hidden">
          <table class="w-full text-xs text-left">
            <thead class="bg-gray-50 text-paper-sidebar uppercase font-bold text-[11px] border-b border-gray-200">
              <tr>
                <th class="px-4 py-3.5">Unidade Organizacional (UORG) / UORG Pai</th>
                <th class="px-4 py-3.5 text-center">Colaboradores</th>
                <th class="px-4 py-3.5 text-center">Publicadas (DIVGP)</th>
                <th class="px-4 py-3.5 text-center">Pendentes</th>
                <th class="px-4 py-3.5 text-center">Sem Grade</th>
                <th class="px-4 py-3.5 min-w-[140px]">Progresso</th>
                <th class="px-4 py-3.5 text-center">Status</th>
                <th class="px-4 py-3.5 text-center">Ações</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-if="loading">
                <td colspan="8" class="px-4 py-12 text-center text-gray-500">
                  <div class="flex flex-col items-center justify-center gap-2">
                    <div class="w-7 h-7 border-4 border-paper-primary border-t-transparent rounded-full animate-spin"></div>
                    <span>Calculando indicadores institucionais DIVGP...</span>
                  </div>
                </td>
              </tr>

              <tr v-else-if="filteredUnidades.length === 0">
                <td colspan="8" class="px-4 py-12 text-center text-gray-500">
                  <p class="font-medium text-gray-700">Nenhuma unidade encontrada para os filtros selecionados.</p>
                </td>
              </tr>

              <tr 
                v-else 
                v-for="u in filteredUnidades" 
                :key="u.unidade_id" 
                class="hover:bg-slate-50 transition-colors"
              >
                <td class="px-4 py-3 font-medium text-gray-900">
                  <div class="font-bold text-gray-900 text-sm">{{ u.uorg_nome || u.unidade_nome }}</div>
                  <div class="text-[11px] text-gray-500">UORG Pai: {{ u.uorg_pai_nome || u.setor_nome }}</div>
                </td>

                <td class="px-4 py-3 text-center font-bold text-gray-800">
                  {{ u.total_colaboradores }}
                </td>

                <td class="px-4 py-3 text-center">
                  <span class="px-2 py-0.5 rounded-md font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">
                    {{ u.total_publicadas }}
                  </span>
                </td>

                <td class="px-4 py-3 text-center">
                  <span 
                    class="px-2 py-0.5 rounded-md font-bold"
                    :class="u.total_pendentes > 0 ? 'bg-amber-50 text-amber-800 border border-amber-200' : 'text-gray-400'"
                  >
                    {{ u.total_pendentes }}
                  </span>
                </td>

                <td class="px-4 py-3 text-center">
                  <span 
                    class="px-2 py-0.5 rounded-md font-bold"
                    :class="u.total_sem_grade > 0 ? 'bg-rose-50 text-rose-800 border border-rose-200' : 'text-gray-400'"
                  >
                    {{ u.total_sem_grade }}
                  </span>
                </td>

                <td class="px-4 py-3">
                  <div class="flex items-center justify-between text-[11px] font-bold mb-1">
                    <span>{{ u.percentual_conclusao }}%</span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
                    <div 
                      class="h-full rounded-full transition-all"
                      :class="u.percentual_conclusao === 100 ? 'bg-emerald-500' : (u.percentual_conclusao > 0 ? 'bg-blue-600' : 'bg-gray-300')"
                      :style="{ width: `${u.percentual_conclusao}%` }"
                    ></div>
                  </div>
                </td>

                <td class="px-4 py-3 text-center">
                  <span 
                    class="px-2.5 py-1 rounded-full text-[10px] font-bold inline-flex items-center gap-1"
                    :class="{
                      'bg-emerald-100 text-emerald-900 border border-emerald-300': u.status_homologacao === 'HOMOLOGADA_100',
                      'bg-amber-100 text-amber-900 border border-amber-300': u.status_homologacao === 'PARCIAL',
                      'bg-rose-100 text-rose-900 border border-rose-300': u.status_homologacao === 'SEM_ENVIO'
                    }"
                  >
                    <span v-if="u.status_homologacao === 'HOMOLOGADA_100'">🟢 100% Homologada</span>
                    <span v-else-if="u.status_homologacao === 'PARCIAL'">🟡 Parcial</span>
                    <span v-else>🔴 Sem Envio</span>
                  </span>
                </td>

                <td class="px-4 py-3 text-center space-x-1.5">
                  <button 
                    @click="filtrarEscalasPorUnidade(u)"
                    class="px-2.5 py-1.5 bg-purple-50 hover:bg-purple-100 text-purple-800 border border-purple-200 rounded-lg text-xs font-bold transition-colors cursor-pointer inline-flex items-center gap-1"
                    title="Ver todas as escalas e status desta unidade"
                  >
                    <ListBulletIcon class="h-3.5 w-3.5" />
                    <span>Ver Escalas</span>
                  </button>

                  <button 
                    @click="openFaltantesModal(u)"
                    class="px-2.5 py-1.5 bg-rose-50 hover:bg-rose-100 text-rose-800 border border-rose-200 rounded-lg text-xs font-bold transition-colors cursor-pointer inline-flex items-center gap-1"
                    title="Ver colaboradores faltantes/sem escala"
                  >
                    <EyeIcon class="h-3.5 w-3.5" />
                    <span>Faltantes</span>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>
    </div>

    <!-- Modal: Colaboradores Faltantes / Pendentes -->
    <div v-if="showFaltantesModal" class="fixed inset-0 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-fade-in">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-2xl overflow-hidden flex flex-col max-h-[85vh]">
        <!-- Header -->
        <div class="px-6 py-4 bg-paper-sidebar text-white flex justify-between items-center shrink-0">
          <div>
            <h3 class="text-lg font-bold">
              Grades Faltantes / Pendentes: {{ selectedUnidadeObj?.uorg_nome || selectedUnidadeObj?.unidade_nome }}
            </h3>
            <p class="text-xs text-blue-200">
              Período: {{ mesesNomes[selectedMes - 1] }} / {{ selectedAno }} · UORG Pai: {{ selectedUnidadeObj?.uorg_pai_nome || selectedUnidadeObj?.setor_nome }}
            </p>
          </div>
          <button @click="showFaltantesModal = false" class="text-white hover:text-gray-300 text-xl font-bold p-1 cursor-pointer">&times;</button>
        </div>

        <!-- Body -->
        <div class="p-6 overflow-y-auto flex-1 space-y-4">
          <div v-if="loadingFaltantes" class="py-12 text-center text-gray-500">
            <div class="w-7 h-7 border-4 border-paper-primary border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
            <span>Consultando colaboradores pendentes...</span>
          </div>

          <div v-else-if="faltantesLista.length === 0" class="py-12 text-center text-gray-500">
            <p class="font-bold text-emerald-700 text-base">🎉 Parabéns! Nenhuma pendência encontrada.</p>
            <p class="text-xs text-gray-400 mt-1">Todos os colaboradores desta unidade possuem escala publicada para este mês.</p>
          </div>

          <div v-else>
            <div class="p-3 bg-amber-50 rounded-xl border border-amber-200 text-xs text-amber-900 mb-3 flex items-center gap-2">
              <span class="text-base font-bold">⚠️</span>
              <span>
                Existem <b>{{ faltantesLista.length }} colaborador(es)</b> com escala pendente de publicação nesta unidade.
              </span>
            </div>

            <div class="border border-gray-200 rounded-xl overflow-hidden">
              <table class="w-full text-xs text-left">
                <thead class="bg-gray-50 text-paper-sidebar uppercase font-bold text-[11px] border-b border-gray-200">
                  <tr>
                    <th class="px-3.5 py-2.5">Colaborador</th>
                    <th class="px-3.5 py-2.5">Cargo / Escala Padrão</th>
                    <th class="px-3.5 py-2.5">Posto</th>
                    <th class="px-3.5 py-2.5 text-center">Status Atual</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                  <tr v-for="f in faltantesLista" :key="f.funcionario_id" class="hover:bg-gray-50">
                    <td class="px-3.5 py-2.5 font-medium">
                      <div class="font-bold text-gray-900">{{ f.nome }}</div>
                      <div class="text-[10px] text-gray-500 font-mono">SIAPE: {{ f.matricula }}</div>
                    </td>
                    <td class="px-3.5 py-2.5 text-gray-700">
                      <div>{{ f.cargo }}</div>
                      <div class="text-[10px] text-gray-500 font-semibold">Cód. Escala: {{ f.escala_padrao }}</div>
                    </td>
                    <td class="px-3.5 py-2.5 text-gray-600">
                      {{ f.posto_nome }}
                    </td>
                    <td class="px-3.5 py-2.5 text-center">
                      <span 
                        class="px-2 py-0.5 rounded-full text-[10px] font-bold border"
                        :class="f.grade_status === 'Rascunho' ? 'bg-gray-100 text-gray-700 border-gray-300' : 'bg-red-50 text-red-700 border-red-200'"
                      >
                        {{ f.grade_status === 'Rascunho' ? '⚪ Em Rascunho' : '🔴 Sem Escala' }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-6 py-4 border-t border-gray-200 bg-gray-50 flex justify-end items-center gap-3 shrink-0">
          <button 
            type="button" 
            @click="showFaltantesModal = false" 
            class="px-5 py-2 bg-paper-primary hover:bg-paper-primary-hover text-white rounded-lg text-xs font-bold transition-colors cursor-pointer"
          >
            Fechar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { 
  BuildingLibraryIcon, 
  BuildingOfficeIcon, 
  CheckBadgeIcon, 
  ExclamationTriangleIcon, 
  MagnifyingGlassIcon, 
  ArrowPathIcon,
  EyeIcon,
  ListBulletIcon,
  CheckCircleIcon,
  ArrowUturnLeftIcon,
  LockOpenIcon,
  ArrowTopRightOnSquareIcon
} from '@heroicons/vue/24/outline';

import Card from '../components/Card.vue';
import api from '../services/api';
import gradeService from '../services/gradeService';
import divgpService, { 
  DivgpSumario, 
  DivgpUnidadeStatusItem, 
  DivgpFaltanteItem,
  DivgpEscalaDetalheItem 
} from '../services/divgpService';
import { useSearchFilterState } from '../composables/useSearchFilterState';

const mesesNomes = [
  'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
];
const anosDisponiveis = [2024, 2025, 2026, 2027, 2028];

const currentDate = new Date();
const selectedMes = ref<number>(currentDate.getMonth() + 1);
const selectedAno = ref<number>(currentDate.getFullYear());

// Controle de Abas: 'todas_escalas' ou 'unidades'
const activeTab = ref<'todas_escalas' | 'unidades'>('todas_escalas');

// ==========================================
// Estado Tab 1: Todas as Escalas
// ==========================================
const loadingEscalas = ref(false);
const todasEscalasLista = ref<DivgpEscalaDetalheItem[]>([]);
const searchEscalaTerm = ref('');
const filterEscalaStatus = ref('TODOS');
const filterEscalaUorgPai = ref('TODOS');
const filterEscalaUorg = ref<number | 'TODOS'>('TODOS');
const filterEscalaCargo = ref<number | 'TODOS'>('TODOS');

// Persistência automática do status da última pesquisa/filtro
useSearchFilterState('painel_divgp', {
  selectedMes,
  selectedAno,
  activeTab,
  searchEscalaTerm,
  filterEscalaStatus,
  filterEscalaUorgPai,
  filterEscalaUorg,
  filterEscalaCargo
});

const cargosDisponiveis = ref<any[]>([]);
const uorgsDisponiveis = ref<any[]>([]);

// Contagens de Status
const countStatusTotal = computed(() => todasEscalasLista.value.length);
const countStatusPublicadas = computed(() => todasEscalasLista.value.filter(e => e.grade_status === 'Publicada').length);
const countStatusEnviadas = computed(() => todasEscalasLista.value.filter(e => e.grade_status === 'Enviada_Superior' || e.grade_status === 'Enviada').length);
const countStatusDevolvidas = computed(() => todasEscalasLista.value.filter(e => e.grade_status === 'Devolvida').length);
const countStatusRascunho = computed(() => todasEscalasLista.value.filter(e => e.grade_status === 'Rascunho').length);
const countStatusSemEscala = computed(() => todasEscalasLista.value.filter(e => e.grade_status === 'Sem Escala').length);

const uorgsPaiDisponiveis = computed(() => {
  const set = new Set<string>();
  todasEscalasLista.value.forEach(e => {
    if (e.uorg_pai_nome) set.add(e.uorg_pai_nome);
  });
  return Array.from(set).sort((a, b) => a.localeCompare(b, 'pt-BR', { sensitivity: 'base' }));
});

const sortedCargosDisponiveis = computed(() => {
  return [...cargosDisponiveis.value].sort((a, b) => 
    (a.nome || '').localeCompare(b.nome || '', 'pt-BR', { sensitivity: 'base' })
  );
});

const uorgsFiltradasSelect = computed(() => {
  let list = uorgsDisponiveis.value;
  if (filterEscalaUorgPai.value !== 'TODOS') {
    list = uorgsDisponiveis.value.filter(u => u.uorg_pai?.nome === filterEscalaUorgPai.value);
  }
  return [...list].sort((a, b) => 
    (a.nome || '').localeCompare(b.nome || '', 'pt-BR', { sensitivity: 'base' })
  );
});

const filteredTodasEscalas = computed(() => {
  return todasEscalasLista.value.filter(item => {
    // Filtro por Status
    if (filterEscalaStatus.value !== 'TODOS') {
      if (filterEscalaStatus.value === 'SEM_ESCALA' && item.grade_status !== 'Sem Escala') {
        return false;
      }
      if (filterEscalaStatus.value !== 'SEM_ESCALA' && item.grade_status !== filterEscalaStatus.value) {
        return false;
      }
    }

    // Filtro por UORG Pai
    if (filterEscalaUorgPai.value !== 'TODOS' && item.uorg_pai_nome !== filterEscalaUorgPai.value) {
      return false;
    }

    // Filtro por UORG
    if (filterEscalaUorg.value !== 'TODOS' && item.uorg_id !== filterEscalaUorg.value) {
      return false;
    }

    // Filtro por Cargo
    if (filterEscalaCargo.value !== 'TODOS' && item.cargo_id !== filterEscalaCargo.value) {
      return false;
    }

    // Busca textual
    if (searchEscalaTerm.value.trim()) {
      const term = searchEscalaTerm.value.toLowerCase().trim();
      const matchNome = item.nome.toLowerCase().includes(term);
      const matchMatr = item.matricula.toLowerCase().includes(term);
      if (!matchNome && !matchMatr) return false;
    }

    return true;
  });
});

// ==========================================
// Estado Tab 2: Resumo por Unidade
// ==========================================
const loading = ref(false);
const sumario = reactive<DivgpSumario>({
  total_unidades: 0,
  unidades_100: 0,
  unidades_pendentes: 0,
  total_colaboradores: 0,
  total_publicadas: 0,
  percentual_geral: 0
});
const unidadesLista = ref<DivgpUnidadeStatusItem[]>([]);

// Filtros de Unidades
const searchTerm = ref('');
const filterStatus = ref('TODOS');
const filterSetor = ref('TODOS');

// Modal Faltantes
const showFaltantesModal = ref(false);
const loadingFaltantes = ref(false);
const selectedUnidadeObj = ref<DivgpUnidadeStatusItem | null>(null);
const faltantesLista = ref<DivgpFaltanteItem[]>([]);

const setoresDisponiveis = computed(() => {
  const set = new Set<string>();
  unidadesLista.value.forEach(u => {
    const nome = u.uorg_pai_nome || u.setor_nome;
    if (nome) set.add(nome);
  });
  return Array.from(set).sort((a, b) => a.localeCompare(b, 'pt-BR', { sensitivity: 'base' }));
});

const filteredUnidades = computed(() => {
  return unidadesLista.value.filter(u => {
    if (filterStatus.value !== 'TODOS' && u.status_homologacao !== filterStatus.value) {
      return false;
    }
    const uorgPai = u.uorg_pai_nome || u.setor_nome;
    if (filterSetor.value !== 'TODOS' && uorgPai !== filterSetor.value) {
      return false;
    }
    if (searchTerm.value.trim()) {
      const term = searchTerm.value.toLowerCase().trim();
      const matchUnid = (u.uorg_nome || u.unidade_nome).toLowerCase().includes(term);
      const matchSet = uorgPai.toLowerCase().includes(term);
      if (!matchUnid && !matchSet) return false;
    }
    return true;
  });
});

// ==========================================
// Ações e Busca de Dados
// ==========================================
const fetchAllData = async () => {
  await Promise.all([
    fetchStatusUnidades(),
    fetchTodasEscalas()
  ]);
};

const fetchStatusUnidades = async () => {
  loading.value = true;
  try {
    const res = await divgpService.getStatusUnidades(selectedMes.value, selectedAno.value);
    sumario.total_unidades = res.sumario.total_unidades;
    sumario.unidades_100 = res.sumario.unidades_100;
    sumario.unidades_pendentes = res.sumario.unidades_pendentes;
    sumario.total_colaboradores = res.sumario.total_colaboradores;
    sumario.total_publicadas = res.sumario.total_publicadas;
    sumario.percentual_geral = res.sumario.percentual_geral;

    unidadesLista.value = res.unidades;
  } catch (error) {
    console.error('Erro ao buscar status institucional DIVGP:', error);
  } finally {
    loading.value = false;
  }
};

const fetchTodasEscalas = async () => {
  loadingEscalas.value = true;
  try {
    todasEscalasLista.value = await divgpService.getTodasEscalas({
      mes: selectedMes.value,
      ano: selectedAno.value
    });
  } catch (error) {
    console.error('Erro ao buscar todas as escalas DIVGP:', error);
  } finally {
    loadingEscalas.value = false;
  }
};

const fetchAuxiliary = async () => {
  try {
    const [cargosRes, uorgsRes] = await Promise.all([
      api.get('/api/cargos'),
      api.get('/api/uorgs')
    ]);
    cargosDisponiveis.value = cargosRes.data;
    uorgsDisponiveis.value = uorgsRes.data;
  } catch (e) {
    console.error('Erro ao carregar dados auxiliares:', e);
  }
};

// Alternar para a aba de todas as escalas já filtrando pela UORG clicada
const filtrarEscalasPorUnidade = (u: DivgpUnidadeStatusItem) => {
  const targetId = u.uorg_id || u.unidade_id;
  filterEscalaUorg.value = targetId;
  filterEscalaStatus.value = 'TODOS';
  activeTab.value = 'todas_escalas';
};

const openFaltantesModal = async (u: DivgpUnidadeStatusItem) => {
  selectedUnidadeObj.value = u;
  showFaltantesModal.value = true;
  loadingFaltantes.value = true;
  try {
    const targetId = u.uorg_id || u.unidade_id;
    faltantesLista.value = await divgpService.getFaltantes(targetId, selectedMes.value, selectedAno.value);
  } catch (error) {
    console.error('Erro ao buscar faltantes da unidade:', error);
    faltantesLista.value = [];
  } finally {
    loadingFaltantes.value = false;
  }
};

// Ações diretas da DIVGP sobre uma escala
const publishEscalaDivgp = async (gradeId: number) => {
  if (!confirm('Deseja homologar e publicar esta escala como oficial para a DIVGP?')) return;
  try {
    await gradeService.publishGrade(gradeId);
    alert('Escala homologada e publicada com sucesso!');
    await fetchAllData();
  } catch (err: any) {
    alert('Erro ao publicar: ' + (err.response?.data?.detail || err.message));
  }
};

const devolverEscalaDivgp = async (gradeId: number) => {
  const motivo = prompt('Informe a orientação/motivo para devolução da escala pela DIVGP:');
  if (motivo === null) return;
  try {
    await gradeService.devolverGrade(gradeId, motivo || undefined);
    alert('Escala devolvida para ajustes com sucesso!');
    await fetchAllData();
  } catch (err: any) {
    alert('Erro ao devolver: ' + (err.response?.data?.detail || err.message));
  }
};

const reabrirEscalaDivgp = async (gradeId: number) => {
  if (!confirm('Deseja reabrir esta escala publicada? Ela retornará para o status de rascunho.')) return;
  try {
    await gradeService.reabrirGrade(gradeId);
    alert('Escala reaberta com sucesso!');
    await fetchAllData();
  } catch (err: any) {
    alert('Erro ao reabrir: ' + (err.response?.data?.detail || err.message));
  }
};

onMounted(async () => {
  await Promise.all([
    fetchAuxiliary(),
    fetchAllData()
  ]);
});
</script>
