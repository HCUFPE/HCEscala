import { createRouter, createWebHistory, NavigationGuardNext } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import Home from '../views/Home.vue';
import Login from '../views/Login.vue';
import Admin from '../views/Admin.vue';

import Exemplos from '../views/Exemplos.vue';
import Pacientes from '../views/Pacientes.vue';
import Grade from '../views/Grade.vue';
import Legendas from '../views/Legendas.vue';
import Escalas from '../views/Escalas.vue';

import Funcionarios from '../views/Funcionarios.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { layout: 'LoginLayout' },
  },
  {
    path: '/admin',
    name: 'Admin',
    component: Admin,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/audit-logs',
    name: 'Auditoria',
    component: () => import('../views/AuditLogs.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },

  {
    path: '/exemplos',
    name: 'Exemplos',
    component: Exemplos,
  },
  {
    path: '/grade',
    alias: '/escala',
    name: 'Escala',
    component: Grade,
  },
  {
    path: '/legendas',
    name: 'Legendas',
    component: Legendas,
  },
  {
    path: '/escalas',
    name: 'Escalas',
    component: Escalas,
  },
  {
    path: '/cargos',
    name: 'Cargos',
    component: () => import('../views/Cargos.vue')
  },
  {
    path: '/vinculos',
    name: 'Vinculos',
    component: () => import('../views/Vinculos.vue')
  },
  {
    path: '/organizacao',
    name: 'Organizacao',
    component: () => import('../views/Organizacao.vue')
  },
  {
    path: '/funcionarios',
    name: 'Funcionarios',
    component: Funcionarios
  },
  {
    path: '/feriados',
    name: 'Feriados',
    component: () => import('../views/Feriados.vue')
  },
  {
    path: '/gerentes',
    name: 'Gerentes',
    component: () => import('../views/Gerentes.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/painel-divgp',
    name: 'PainelDivgp',
    component: () => import('../views/PainelDivgp.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/painel-digp',
    redirect: '/painel-divgp'
  },
  {
    path: '/pacientes',
    name: 'Pacientes',
    component: Pacientes,
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  linkActiveClass: 'bg-paper-active-link',
  linkExactActiveClass: 'bg-paper-active-link',
});

router.beforeEach(async (to, _from, next: NavigationGuardNext) => {
  const authStore = useAuthStore();

  // Se a rota for Login e o usuário já estiver autenticado, vai para a página inicial
  if (to.name === 'Login') {
    if (authStore.isAuthenticated) {
      return next({ name: 'Home' });
    }
    return next();
  }

  // Todas as rotas do sistema requerem autenticação obrigatória
  if (!authStore.isAuthenticated) {
    return next({ name: 'Login', query: { redirect: to.fullPath } });
  }

  // Se a rota requerer administrador do sistema e o usuário não for admin
  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    return next({ name: 'Home' });
  }

  next();
});

export default router;
