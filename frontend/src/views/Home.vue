<template>
  <div class="space-y-6">
    <!-- Hero Banner -->
    <div class="bg-gradient-to-r from-paper-sidebar via-blue-900 to-indigo-900 text-white rounded-2xl p-6 sm:p-8 shadow-md relative overflow-hidden">
      <div class="relative z-10 max-w-2xl">
        <div class="flex items-center gap-3 mb-3">
          <div class="p-2 bg-white/10 backdrop-blur-xs rounded-xl border border-white/20">
            <CalendarDaysIcon class="h-8 w-8 text-blue-300" />
          </div>
          <div>
            <h1 class="text-2xl sm:text-3xl font-black tracking-tight">HC Escalas</h1>
            <p class="text-xs text-blue-200 uppercase tracking-widest font-semibold">Sistema de Gestão de Escalas de Serviço do Hospital das Clínicas da UFPE</p>
          </div>
        </div>
        <p class="text-sm text-blue-100 mt-2 leading-relaxed">
          Plataforma centralizada para planejamento, distribuição mensal de turnos, divisão de carga horária entre unidades, controle de férias, integração com calendário de feriados e homologação de escalas para a DIVGP..
        </p>
        <div class="mt-5 flex flex-wrap gap-3">
          <router-link 
            to="/grade" 
            class="px-5 py-2.5 bg-paper-primary hover:bg-paper-primary-hover text-white rounded-xl text-xs font-bold transition-all shadow-sm flex items-center gap-2"
          >
            <CalendarDaysIcon class="h-4 w-4" />
            <span>Acessar Gestão de Escalas</span>
          </router-link>
          <router-link 
            to="/funcionarios" 
            class="px-4 py-2.5 bg-white/10 hover:bg-white/20 text-white rounded-xl text-xs font-medium transition-all backdrop-blur-xs flex items-center gap-2 border border-white/20"
          >
            <UserGroupIcon class="h-4 w-4" />
            <span>Colaboradores</span>
          </router-link>
        </div>
      </div>
    </div>

    <!-- Quick Navigation Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <router-link 
        to="/grade"
        class="bg-white p-5 rounded-2xl border border-gray-200 hover:border-paper-primary hover:shadow-md transition-all group flex flex-col justify-between"
      >
        <div>
          <div class="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
            <CalendarDaysIcon class="h-5 w-5" />
          </div>
          <h3 class="font-bold text-gray-900 text-sm">Escala Mensal</h3>
          <p class="text-xs text-gray-500 mt-1">Elaboração, replicação, validação e publicação de escalas para a DIVGP..</p>
        </div>
        <span class="text-xs text-paper-primary font-bold mt-4 inline-flex items-center gap-1 group-hover:translate-x-1 transition-transform">
          Gerenciar &rarr;
        </span>
      </router-link>

      <router-link 
        to="/funcionarios" 
        class="bg-white p-5 rounded-2xl border border-gray-200 hover:border-paper-primary hover:shadow-md transition-all group flex flex-col justify-between"
      >
        <div>
          <div class="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
            <UserGroupIcon class="h-5 w-5" />
          </div>
          <h3 class="font-bold text-gray-900 text-sm">Funcionários & Lotações</h3>
          <p class="text-xs text-gray-500 mt-1">Cadastro de profissionais, múltiplos vínculos, postos de trabalho e férias.</p>
        </div>
        <span class="text-xs text-paper-primary font-bold mt-4 inline-flex items-center gap-1 group-hover:translate-x-1 transition-transform">
          Consultar &rarr;
        </span>
      </router-link>

      <router-link 
        to="/feriados" 
        class="bg-white p-5 rounded-2xl border border-gray-200 hover:border-paper-primary hover:shadow-md transition-all group flex flex-col justify-between"
      >
        <div>
          <div class="w-10 h-10 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
            <CalendarIcon class="h-5 w-5" />
          </div>
          <h3 class="font-bold text-gray-900 text-sm">Feriados</h3>
          <p class="text-xs text-gray-500 mt-1">Calendário oficial de feriados nacionais, estaduais, municipais e institucionais.</p>
        </div>
        <span class="text-xs text-paper-primary font-bold mt-4 inline-flex items-center gap-1 group-hover:translate-x-1 transition-transform">
          Ver Calendário &rarr;
        </span>
      </router-link>

      <router-link 
        to="/escalas" 
        class="bg-white p-5 rounded-2xl border border-gray-200 hover:border-paper-primary hover:shadow-md transition-all group flex flex-col justify-between"
      >
        <div>
          <div class="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
            <ClockIcon class="h-5 w-5" />
          </div>
          <h3 class="font-bold text-gray-900 text-sm">Códigos de Escala & Legendas</h3>
          <p class="text-xs text-gray-500 mt-1">Configuração de jornadas, horários de turnos (M, T, N, D) e siglas operacionais.</p>
        </div>
        <span class="text-xs text-paper-primary font-bold mt-4 inline-flex items-center gap-1 group-hover:translate-x-1 transition-transform">
          Configurar &rarr;
        </span>
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { 
  CalendarDaysIcon, 
  UserGroupIcon, 
  CalendarIcon, 
  ClockIcon 
} from '@heroicons/vue/24/outline';
</script>
