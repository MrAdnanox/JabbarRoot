// src/app.d.ts
declare global {
	namespace App {
		// interface Error {}
		// interface Locals {}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}

    // On étend les types globaux de React (que Svelte utilise sous le capot pour les types DOM)
	namespace React {
		interface InputHTMLAttributes<T> extends HTMLAttributes<T> {
			webkitdirectory?: string;
		}
	}
}

export {};