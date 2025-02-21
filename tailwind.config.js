/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        'primary': '#22c55e',
        'secondary': '#0ea5e9',
        'accent': '#6366f1'
      }
    }
  },
  plugins: [require('@tailwindcss/typography')]
};
