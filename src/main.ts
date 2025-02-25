import App from './App.svelte';
import './app.css';

// Force SPA mode and ensure proper DOM mounting
const target = document.getElementById('app') || document.body;
if (!target.hasChildNodes()) {
  const app = new App({
    target,
  });

  export default app;
}