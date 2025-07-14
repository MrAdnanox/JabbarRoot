<script lang="ts">
  import { systemHealthStore, type SystemHealth } from '$lib/stores/systemHealthStore';
  
  const statusClasses: Record<SystemHealth[keyof SystemHealth], string> = {
    CONNECTED: 'text-brand-success',
    CONNECTING: 'text-brand-warning',
    DISCONNECTED: 'text-brand-danger',
    AVAILABLE: 'text-brand-success',
    NOT_FOUND: 'text-brand-danger',
  };
</script>

<div>
  <h2 class="text-xl font-bold text-brand-text mb-3">État du Système</h2>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
    {#each Object.entries({
      'PostgreSQL': $systemHealthStore.postgres_status,
      'Graphe SQLite': $systemHealthStore.sqlite_status,
      'Documents Ingérés': $systemHealthStore.total_documents,
      'Chunks Créés': $systemHealthStore.total_chunks
    }) as [label, value]}
      <div class="bg-brand-surface border border-brand-border rounded-lg p-4 text-center">
        <dt class="text-sm font-medium text-brand-text-dim truncate">{label}</dt>
        <dd class="mt-1 text-2xl font-semibold tracking-tight {statusClasses[value] || 'text-brand-text'}">
          {typeof value === 'number' ? value.toLocaleString() : value}
        </dd>
      </div>
    {/each}
  </div>
</div>