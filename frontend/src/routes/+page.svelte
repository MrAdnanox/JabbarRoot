<!-- src/routes/+page.svelte -->
<script lang="ts">
  // Import des composants "Container" ou de haut niveau
  import SystemHealthDashboard from '$lib/components/SystemHealthDashboard.svelte';
  import IngestionControlPanel from '$lib/components/IngestionControlPanel.svelte';
  import LogViewer from '$lib/components/LogViewer.svelte';
</script>

<div class="bg-brand-bg text-brand-text min-h-screen font-sans antialiased">
<main class="max-w-5xl mx-auto p-4 sm:p-6 lg:p-8">
  <header class="text-center mb-12">
    <h1 class="text-4xl lg:text-5xl font-extrabold text-brand-text">
      Console d'Opérations <span class="text-brand-primary">"Janus"</span>
    </h1>
    <p class="mt-3 text-lg text-brand-text-dim">
      Interface de pilotage pour l'écosystème d'analyse JabbarRoot.
    </p>
  </header>

  <!-- 
    HIÉRARCHIE DE RENDU CORRECTE :
    Chaque composant est une section distincte de la page.
    IngestionControlPanel contient déjà le sélecteur de fichiers.
  -->
  <div class="space-y-10">
    <SystemHealthDashboard />
    
    <!-- POINT DE VÉRITÉ UNIQUE POUR L'INGESTION -->
    <IngestionControlPanel />
    
    <LogViewer />
  </div>
</main>
</div>