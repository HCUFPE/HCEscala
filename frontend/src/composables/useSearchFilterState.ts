import { watch, Ref } from 'vue';

/**
 * Composable para persistir e recuperar filtros de pesquisa no localStorage.
 * Permite que, ao navegar entre telas ou recarregar a página, a última pesquisa
 * e os filtros selecionados pelo usuário sejam automaticamente restaurados.
 *
 * @param storageKey Chave única no localStorage (ex: 'filtro_funcionarios', 'filtro_grade')
 * @param state Objeto com refs que devem ser persistidas e restauradas
 */
export function useSearchFilterState<T extends Record<string, Ref<any>>>(
  storageKey: string,
  state: T
) {
  // 1. Tentar restaurar estado anterior do localStorage
  try {
    const saved = localStorage.getItem(`appgrade_search_${storageKey}`);
    if (saved) {
      const parsed = JSON.parse(saved);
      if (parsed && typeof parsed === 'object') {
        for (const key in state) {
          if (Object.prototype.hasOwnProperty.call(parsed, key)) {
            const val = parsed[key];
            if (val !== undefined) {
              state[key].value = val;
            }
          }
        }
      }
    }
  } catch (err) {
    console.warn(`[useSearchFilterState] Erro ao carregar filtros de ${storageKey}:`, err);
  }

  // 2. Observar mudanças e salvar automaticamente
  watch(
    () => {
      const snapshot: Record<string, any> = {};
      for (const key in state) {
        snapshot[key] = state[key].value;
      }
      return snapshot;
    },
    (newSnapshot) => {
      try {
        localStorage.setItem(`appgrade_search_${storageKey}`, JSON.stringify(newSnapshot));
      } catch (err) {
        console.warn(`[useSearchFilterState] Erro ao salvar filtros de ${storageKey}:`, err);
      }
    },
    { deep: true }
  );

  // 3. Função auxiliar para resetar/limpar o estado salvo
  const clearSavedState = () => {
    try {
      localStorage.removeItem(`appgrade_search_${storageKey}`);
    } catch (err) {
      console.warn(`[useSearchFilterState] Erro ao limpar filtros de ${storageKey}:`, err);
    }
  };

  return {
    clearSavedState
  };
}
