import App from './App.svelte';
import './app.css';

const target = document.getElementById('app') || document.body;
const app = new App({ target });

export default app;