// src/lib/services/ingestionService.ts
import { writable } from 'svelte/store';

// 1. Définir les états possibles du job d'ingestion
export type IngestionStatus = 'IDLE' | 'PENDING' | 'RUNNING' | 'SUCCESS' | 'FAILED';
export interface LogEntry {
  level: 'INFO' | 'ERROR' | 'WARN';
  message: string;
  timestamp: Date;
}

// 2. Créer des stores pour que les composants puissent réagir à l'état du job
export const ingestionStatus = writable<IngestionStatus>('IDLE');
export const ingestionLogs = writable<LogEntry[]>([]);
export const currentJobId = writable<string | null>(null);

// 3. La fonction principale que nos composants appelleront
//    C'est une simulation d'une communication WebSocket.
export function startIngestion(path: string) {
  // Réinitialiser l'état au début
  ingestionStatus.set('PENDING');
  ingestionLogs.set([]);
  currentJobId.set(null);

  console.log(`[SERVICE] Demande d'ingestion pour le chemin : ${path}`);

  // ---- SIMULATION D'UN FLUX WEBSOCKET ----
  const mockJobId = `job-${Math.random().toString(36).substring(2, 9)}`;
  
  // Simuler le démarrage du job
  setTimeout(() => {
    ingestionStatus.set('RUNNING');
    currentJobId.set(mockJobId);
    _addLog('INFO', `Job ${mockJobId} démarré pour ${path}`);
  }, 1000);

  // Simuler des logs qui arrivent au fur et à mesure
  setTimeout(() => _addLog('INFO', 'Executing ParsingStage...'), 2000);
  setTimeout(() => _addLog('INFO', 'Executing AnalysisStage...'), 3500);
  setTimeout(() => _addLog('ERROR', 'Failed to embed chunk 42. Retrying...'), 5000);
  setTimeout(() => _addLog('INFO', 'Executing StorageStage...'), 6500);

  // Simuler la fin du job
  setTimeout(() => {
    ingestionStatus.set('SUCCESS');
    _addLog('INFO', `Job ${mockJobId} terminé avec succès.`);
  }, 8000);
  // Pour tester l'état FAILED, décommentez la ligne suivante et commentez la précédente
  // setTimeout(() => { ingestionStatus.set('FAILED'); _addLog('ERROR', `Job ${mockJobId} a échoué.`); }, 8000);
}

// ---- Helper interne pour ajouter un log ----
function _addLog(level: LogEntry['level'], message: string) {
  ingestionLogs.update(currentLogs => {
    return [...currentLogs, { level, message, timestamp: new Date() }];
  });
}