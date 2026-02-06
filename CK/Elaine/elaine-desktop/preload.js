/**
 * Elaine Desktop — Preload Script
 * Secure bridge: renderer can call Elaine API through ipcRenderer.
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('elaine', {
  // Call Elaine API: elaine.api('GET', '/api/status')
  api: (method, path, body) => ipcRenderer.invoke('elaine-api', method, path, body),

  // Show desktop notification
  notify: (title, body) => ipcRenderer.invoke('show-notification', title, body),

  // Listen for navigation from tray menu
  onNavigate: (callback) => ipcRenderer.on('navigate', (event, page) => callback(page)),
});
