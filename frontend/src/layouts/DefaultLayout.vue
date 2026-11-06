<template>
  <div class="relative h-screen overflow-hidden md:flex">
    <!-- Mobile Menu -->
    <div class="bg-paper-sidebar text-gray-100 flex justify-between items-center md:hidden shrink-0 px-2">
      <router-link to="/" class="flex items-center gap-2 p-3 text-white font-extrabold text-lg">
        <CalendarDaysIcon class="h-6 w-6 text-paper-primary" />
        <span>HC Escalas</span>
      </router-link>
      <button @click="sidebarOpen = !sidebarOpen" class="p-3 focus:outline-none focus:bg-paper-active-link rounded-lg">
        <Bars3Icon class="h-6 w-6" />
      </button>
    </div>

    <!-- Sidebar -->
    <aside :class="{ '-translate-x-full': !sidebarOpen }" class="bg-paper-sidebar text-gray-100 w-64 space-y-6 py-7 px-2 absolute inset-y-0 left-0 transform md:relative md:translate-x-0 transition duration-200 ease-in-out z-20 h-full shrink-0">
      <div @click="() => router.push('/')" class="cursor-pointer text-white flex items-center space-x-3 px-4 group">
        <div class="p-2 bg-paper-primary/20 group-hover:bg-paper-primary/30 rounded-xl transition-colors border border-paper-primary/30">
          <CalendarDaysIcon class="h-7 w-7 text-white"/>
        </div>
        <div class="flex flex-col">
          <span class="text-xl font-extrabold tracking-tight">HC Escalas</span>
          <span class="text-[9px] text-blue-200 uppercase tracking-wider font-semibold">HC-UFPE / EBSERH</span>
        </div>
      </div>
      <div class="px-4 my-6">
        <div class="border-t border-white border-opacity-20"></div>
      </div>

      <nav>
        <router-link to="/" class="flex items-center space-x-2 py-2.5 px-4 rounded transition duration-200 hover:bg-paper-active-link hover:text-white">
          <HomeIcon class="h-6 w-6"/>
          <span>Home</span>
        </router-link>

        <router-link to="/grade" class="flex items-center space-x-2 py-2.5 px-4 rounded transition duration-200 hover:bg-paper-active-link hover:text-white">
          <CalendarIcon class="h-6 w-6" />
          <span>Escala</span>
        </router-link>

        <router-link to="/legendas" class="flex items-center space-x-2 py-2.5 px-4 rounded transition duration-200 hover:bg-paper-active-link hover:text-white">
          <TagIcon class="h-6 w-6" />
          <span>Legendas</span>
        </router-link>

        <router-link to="/escalas" class="flex items-center space-x-2 py-2.5 px-4 rounded transition duration-200 hover:bg-paper-active-link hover:text-white">
          <ClockIcon class="h-6 w-6" />
          <span>Códigos de Escala</span>
        </router-link>

        <router-link to="/cargos" class="flex items-center space-x-2 py-2.5 px-4 rounded transition duration-200 hover:bg-paper-active-link hover:text-white">
          <BriefcaseIcon class="h-6 w-6" />
          <span>Cargos</span>
        </router-link>

        <router-link to="/vinculos" class="flex items-center space-x-2 py-2.5 px-4 rounded transition duration-200 hover:bg-paper-active-link hover:text-white">
          <IdentificationIcon class="h-6 w-6" />
          <span>Vínculos</span>
        </router-link>

        <router-link to="/organizacao" class="flex items-center space-x-2 py-2.5 px-4 rounded transition duration-200 hover:bg-paper-active-link hover:text-white">
          <BuildingOfficeIcon class="h-6 w-6" />
          <span>Unidades Organizacionais</span>
        </router-link>

        <router-link to="/funcionarios" class="flex items-center space-x-2 py-2.5 px-4 rounded transition duration-200 hover:bg-paper-active-link hover:text-white">
          <UserGroupIcon class="h-6 w-6" />
          <span>Funcionários</span>
        </router-link>

        <router-link to="/feriados" class="flex items-center space-x-2 py-2.5 px-4 rounded transition duration-200 hover:bg-paper-active-link hover:text-white">
          <CalendarDaysIcon class="h-6 w-6" />
          <span>Feriados</span>
        </router-link>

        <div class="px-4 my-3">
          <div class="border-t border-white border-opacity-10"></div>
        </div>

        <router-link to="/painel-divgp" class="flex items-center space-x-2 py-2.5 px-4 rounded transition duration-200 hover:bg-purple-900/60 hover:text-white text-purple-200">
          <BuildingLibraryIcon class="h-6 w-6 text-purple-300" />
          <span class="font-bold">Painel DIVGP</span>
        </router-link>

        <router-link to="/gerentes" class="flex items-center space-x-2 py-2.5 px-4 rounded transition duration-200 hover:bg-paper-active-link hover:text-white">
          <ShieldCheckIcon class="h-6 w-6" />
          <span>Gerentes</span>
        </router-link>

        <!-- Menu Exclusivo do Administrador -->
        <template v-if="authStore.isAdmin">
          <div class="px-4 my-3">
            <div class="border-t border-white border-opacity-10"></div>
          </div>
          <router-link to="/audit-logs" class="flex items-center space-x-2 py-2.5 px-4 rounded transition duration-200 hover:bg-red-900/50 hover:text-white text-red-200 font-medium">
            <ClipboardDocumentListIcon class="h-6 w-6 text-red-300" />
            <span>Logs & Auditoria</span>
          </router-link>
          <router-link to="/admin" class="flex items-center space-x-2 py-2.5 px-4 rounded transition duration-200 hover:bg-emerald-900/50 hover:text-white text-emerald-200 font-medium">
            <CircleStackIcon class="h-6 w-6 text-emerald-300" />
            <span>Backup do Banco</span>
          </router-link>
          <router-link v-if="false" to="/audit-logs">
          </router-link>
        </template>
      </nav>
    </aside>

    <!-- Content -->
    <div class="flex-1 flex flex-col bg-paper-bg overflow-y-auto h-full">
      <header class="flex justify-between items-center p-6 bg-white/80 backdrop-blur-md border-b border-gray-300 sticky top-0 z-10">
        <div>
          <h1 class="text-2xl font-semibold text-paper-text">{{ $route.name }}</h1>
        </div>
        <div>
          <router-link v-if="!authStore.isAuthenticated" to="/login">
            <Button variant="primary">
              <template #icon>
                <ArrowRightOnRectangleIcon class="h-5 w-5" />
              </template>
              Login
            </Button>
          </router-link>
          <ProfileDropdown v-else />
        </div>
      </header>
      <main class="flex-1">
        <div class="container py-4 md:py-6">
          <router-view />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import {
  HomeIcon,
  Bars3Icon,
  ArrowRightOnRectangleIcon,
  CalendarIcon,
  TagIcon,
  ClockIcon,
  BriefcaseIcon,
  IdentificationIcon,
  BuildingOfficeIcon,
  UserGroupIcon,
  CalendarDaysIcon,
  BuildingLibraryIcon,
  ShieldCheckIcon,
  ClipboardDocumentListIcon,
  CircleStackIcon,
} from '@heroicons/vue/24/outline';
import ProfileDropdown from '../components/ProfileDropdown.vue';
import Button from '../components/Button.vue';
import { useAuthStore } from '../stores/auth';

const sidebarOpen = ref(false);
const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();


// Close sidebar on route change
watch(() => route.path, () => {
  sidebarOpen.value = false;
});
</script>