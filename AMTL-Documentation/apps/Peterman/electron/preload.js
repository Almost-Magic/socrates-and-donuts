/**
 * Peterman Desktop Application - Preload Script
 * 
 * Exposes safe APIs to the renderer process.
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods to the renderer process
contextBridge.exposeInMainWorld('electronAPI', {
    /**
     * Update the system tray score
     * @param {number} score - The current Peterman score (0-100)
     */
    updateScore: (score) => {
        ipcRenderer.send('update-score', score);
    },
    
    /**
     * Listen for refresh events from main process
     * @param {Function} callback - Callback function
     */
    onRefresh: (callback) => {
        ipcRenderer.on('refresh-data', () => callback());
    },
    
    /**
     * Check if running in Electron
     */
    isElectron: true,
    
    /**
     * Get platform info
     */
    platform: process.platform,
    
    /**
     * Remove refresh listener
     */
    removeRefreshListener: () => {
        ipcRenderer.removeAllListeners('refresh-data');
    }
});

// Log that preload is ready
console.log('[Peterman Preload] Initialised');
