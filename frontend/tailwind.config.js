// frontend/tailwind.config.js
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        'brand-bg': '#0D1117',        
        'brand-surface': '#161B22',   
        'brand-border': '#30363D',    
        'brand-text': '#E6EDF3',       
        'brand-text-dim': '#8B949E',    
        'brand-primary': '#58A6FF',     
        'brand-success': '#3FB950',    
        'brand-danger': '#F85149',     
        'brand-warning': '#D29922',   
      },
    },
  },
  plugins: [
      require('@tailwindcss/forms'),
      require('@tailwindcss/typography'),
  ],
};