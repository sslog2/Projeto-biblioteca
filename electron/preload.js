// preload.js — executado no contexto isolado da janela
// Expõe apenas APIs seguras ao renderer via contextBridge se necessário.
const { contextBridge } = require('electron');

// Exemplo: expõe versão da plataforma (inofensivo)
contextBridge.exposeInMainWorld('electronAPI', {
  platform: process.platform,
});
