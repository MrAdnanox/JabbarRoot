// src/lib/stores/systemHealthStore.ts

import { writable } from 'svelte/store';

// 1. Définir la structure de nos données avec une interface TypeScript pour la robustesse
export interface SystemHealth {
  postgres_status: 'CONNECTED' | 'DISCONNECTED' | 'CONNECTING';
  sqlite_status: 'AVAILABLE' | 'NOT_FOUND';
  total_documents: number;
  total_chunks: number;
}

// 2. Créer le store avec des données initiales simulées
//    L'utilisation de 'writable' signifie que ses données peuvent être modifiées de l'extérieur.
const initialHealth: SystemHealth = {
  postgres_status: 'CONNECTED',
  sqlite_status: 'AVAILABLE',
  total_documents: 0,
  total_chunks: 0,
};

export const systemHealthStore = writable<SystemHealth>(initialHealth);

// Optionnel : Simuler une mise à jour des données après quelques secondes
// pour voir la réactivité de l'interface.
setTimeout(() => {
    systemHealthStore.update(currentHealth => {
        return {
            ...currentHealth,
            total_documents: 152,
            total_chunks: 4321,
        };
    });
}, 2000);