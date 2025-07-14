<!-- src/lib/components/AdvancedFilePicker.svelte -->

<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  // Ce composant est un "instrument" parfait et autonome.
  // Il ne connaît rien du monde extérieur, sauf qu'il doit signaler quand il a fait son travail.
  const dispatch = createEventDispatcher();

  // Utilisation d'une Map pour stocker les fichiers uniques, garantissant la déduplication.
  let selectedFiles = new Map<string, File>();
  
  let isDragOver = false;
  let fileInput: HTMLInputElement;
  let folderInput: HTMLInputElement;

  /**
   * Crée un identifiant unique pour un fichier pour la déduplication.
   * @param {File} file - L'objet Fichier.
   * @returns {string} - Un identifiant unique.
   */
  function getFileId(file: File): string {
    return `${file.name}-${file.size}-${file.lastModified}`;
  }

  /**
   * Gère les fichiers ajoutés (depuis un input ou un glisser-déposer).
   * @param {FileList | null} files - La liste des fichiers à traiter.
   */
  function handleFiles(files: FileList | null) {
    if (!files || files.length === 0) return;

    let changed = false;
    for (const file of files) {
      const fileId = getFileId(file);
      if (!selectedFiles.has(fileId)) {
        selectedFiles.set(fileId, file);
        changed = true;
      }
    }

    if (changed) {
      selectedFiles = selectedFiles; // Déclenche la mise à jour réactive de Svelte
      // ÉVÉNEMENT CLÉ : On notifie le parent que la sélection a changé.
      dispatch('change', { files: Array.from(selectedFiles.values()) });
    }
  }

  /**
   * Supprime un fichier de la sélection.
   * @param {string} fileId - L'identifiant du fichier à supprimer.
   */
  function removeFile(fileId: string) {
    selectedFiles.delete(fileId);
    selectedFiles = selectedFiles; // Déclenche la mise à jour
    // ÉVÉNEMENT CLÉ : On notifie aussi lors d'une suppression.
    dispatch('change', { files: Array.from(selectedFiles.values()) });
  }
  
  /**
   * Gère l'accessibilité au clavier pour la zone de dépôt.
   * @param {KeyboardEvent} e - L'événement clavier.
   */
  function handleKeyDown(e: KeyboardEvent) {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      fileInput.click();
    }
  }
</script>

<!-- Le conteneur principal utilise les couleurs du thème "Janus" -->
<div class="bg-brand-surface p-6 rounded-xl shadow-lg w-full border border-brand-border">
  <h3 class="text-xl font-bold text-brand-text mb-4">Sélecteur de Fichiers</h3>

  <!-- Zone de Glisser-Déposer -->
  <div
    class="flex flex-col items-center justify-center p-8 mb-4 rounded-lg cursor-pointer border-2 border-dashed transition-colors"
    class:border-brand-primary={isDragOver}
    class:bg-brand-bg={isDragOver}
    class:border-brand-border={!isDragOver}
    on:dragover|preventDefault={() => isDragOver = true}
    on:dragleave|preventDefault={() => isDragOver = false}
    on:drop|preventDefault={(e) => { handleFiles(e.dataTransfer?.files ?? null); isDragOver = false; }}
    on:click={() => fileInput.click()}
    on:keydown={handleKeyDown}
    role="button"
    tabindex="0"
    aria-label="Zone de glisser-déposer pour les fichiers"
  >
    <svg class="w-10 h-10 mb-3 text-brand-text-dim" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
    </svg>
    <p class="text-md font-semibold text-brand-text">Glissez et déposez des fichiers ici</p>
    <p class="text-xs text-brand-text-dim">ou cliquez pour sélectionner</p>
  </div>

  <!-- Boutons d'action -->
  <div class="flex flex-col sm:flex-row justify-center gap-4 mb-4">
    <!-- OPTION 1: Sélection de fichiers multiples -->
    <input type="file" bind:this={fileInput} on:change={(e) => handleFiles(e.currentTarget.files)} multiple class="hidden" />
    <button on:click={() => fileInput.click()} class="bg-brand-primary hover:opacity-90 text-white font-semibold py-2 px-4 rounded-lg shadow-md transition duration-300 transform hover:scale-105">
      Sélectionner des Fichiers
    </button>
    
    <!-- OPTION 2: Sélection d'un dossier (et de tous ses fichiers) -->
    <input type="file" bind:this={folderInput} on:change={(e) => handleFiles(e.currentTarget.files)} webkitdirectory multiple class="hidden" />
    <button on:click={() => folderInput.click()} class="bg-brand-success hover:opacity-90 text-white font-semibold py-2 px-4 rounded-lg shadow-md transition duration-300 transform hover:scale-105">
      Sélectionner un Dossier
    </button>
  </div>

  <!-- Liste des Fichiers Sélectionnés -->
  <div class="mt-6">
    <h4 class="text-lg font-semibold text-brand-text mb-2">Fichiers Sélectionnés :</h4>
    <div class="bg-brand-bg border border-brand-border rounded-lg max-h-60 overflow-y-auto">
      {#if selectedFiles.size === 0}
        <p class="p-4 text-center text-brand-text-dim">Aucun fichier sélectionné.</p>
      {:else}
        <ul class="divide-y divide-brand-border">
          {#each Array.from(selectedFiles.entries()) as [fileId, file] (fileId)}
            <li class="flex items-center justify-between p-3 hover:bg-brand-surface transition-colors">
              <div class="flex flex-col overflow-hidden">
                <span class="text-brand-text font-medium text-sm break-all">{file.name}</span>
                <span class="text-xs text-brand-text-dim">({(file.size / 1024 / 1024).toFixed(2)} Mo)</span>
              </div>
              <button
                on:click={() => removeFile(fileId)}
                class="ml-3 flex-shrink-0 p-1 rounded-full text-brand-danger hover:bg-brand-danger/20 focus:outline-none focus:ring-2 focus:ring-brand-danger"
                aria-label="Supprimer {file.name}"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </li>
          {/each}
        </ul>
      {/if}
    </div>
  </div>
</div>