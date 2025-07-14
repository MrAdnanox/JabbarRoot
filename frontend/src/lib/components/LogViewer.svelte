<!-- src/lib/components/LogViewer.svelte -->
<script lang="ts">
    import { ingestionLogs, ingestionStatus } from '$lib/services/ingestionService';
  
    const levelClasses = {
      INFO: 'text-text-secondary',
      WARN: 'text-warning',
      ERROR: 'text-danger',
    };
  </script>
  
  {#if $ingestionLogs.length > 0}
    <section class="bg-bg-inset p-4 rounded-lg shadow-inner mt-6 font-mono text-sm max-h-96 overflow-y-auto border border-border-primary">
      {#each $ingestionLogs as log, i (i)}
        <div>
          <span class="text-text-secondary/50">{log.timestamp.toLocaleTimeString()}</span>
          <span class="font-bold {levelClasses[log.level]} mx-2">{log.level}</span>
          <span class="text-text-primary">{log.message}</span>
        </div>
      {/each}
  
      {#if $ingestionStatus === 'SUCCESS'}
        <div class="mt-2 text-success font-bold">--- JOB TERMINÉ AVEC SUCCÈS ---</div>
      {:else if $ingestionStatus === 'FAILED'}
        <div class="mt-2 text-danger font-bold">--- JOB ÉCHOUÉ ---</div>
      {/if}
    </section>
  {/if}