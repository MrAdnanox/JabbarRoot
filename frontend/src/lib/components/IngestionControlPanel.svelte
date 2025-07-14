<!-- src/lib/components/IngestionControlPanel.svelte -->
<script lang="ts">
  import { startIngestion, ingestionStatus } from '$lib/services/ingestionService';
  import AdvancedFilePicker from './AdvancedFilePicker.svelte'; // On importe l'instrument

  // État local du container : la liste des fichiers prêts à être ingérés.
  let filesToIngest: File[] = [];

  // Fonction handler qui sera appelée par l'événement de l'enfant.
  function handleFileSelection(event: CustomEvent<{ files: File[] }>) {
    // On met à jour notre état avec les données fournies par l'enfant.
    filesToIngest = event.detail.files;
  }

  // La logique métier reste ici, dans le composant responsable.
  $: isLoading = $ingestionStatus === 'PENDING' || $ingestionStatus === 'RUNNING';
  $: isSubmitDisabled = filesToIngest.length === 0 || isLoading;

  function handleSubmit() {
    if (isSubmitDisabled) return;
    
    const firstFile = filesToIngest[0];
    const path = (firstFile as any).webkitRelativePath || firstFile.name;
    
    startIngestion(path);
  }
</script>

<div>
  <h2 class="text-2xl font-bold text-brand-text mb-4">Panneau de Pilotage de l'Ingestion</h2>
  
  <!-- On utilise le composant enfant et on écoute son événement `change` -->
  <AdvancedFilePicker on:change={handleFileSelection} />

  <!-- Le bouton d'action est la responsabilité du container -->
  <div class="mt-6 text-center">
    <button 
      on:click={handleSubmit} 
      disabled={isSubmitDisabled} 
      class="w-full sm:w-auto bg-brand-primary text-white font-bold py-3 px-8 rounded-lg transition-all transform hover:scale-105 disabled:scale-100 disabled:bg-brand-surface disabled:text-brand-text-dim disabled:cursor-not-allowed"
    >
      {#if isLoading}
        <span>Traitement en cours...</span>
      {:else}
        Lancer l'ingestion ({filesToIngest.length})
      {/if}
    </button>
  </div>
</div>