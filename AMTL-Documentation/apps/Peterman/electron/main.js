/**
 * Peterman Desktop Application - Main Process
 * 
 * Electron main process for Peterman AI Brand Presence Command Centre.
 * Handles window management, system tray, and Flask backend integration.
 */

const { app, BrowserWindow, Tray, Menu, nativeImage, ipcMain } = require('electron');
const path = require('path');
const { spawn, exec } = require('child_process');

// Configuration
const FLASK_PORT = 5008;
const FLASK_HOST = 'localhost';
const STARTUP_TIMEOUT = 30000; // 30 seconds

// Global references
let mainWindow = null;
let tray = null;
let flaskProcess = null;
let currentScore = 50; // Default score for tray icon

// Score colours for system tray
const SCORE_COLOURS = {
    critical: '#E53935',  // Red: 0-25
    warning: '#FF9800',   // Amber: 25-50
    good: '#C9944A',      // Gold: 50-75
    excellent: '#4CAF50'  // Platinum: 75-100
};

/**
 * Get colour for current score
 */
function getScoreColour(score) {
    if (score >= 75) return SCORE_COLOURS.excellent;
    if (score >= 50) return SCORE_COLOURS.good;
    if (score >= 25) return SCORE_COLOURS.warning;
    return SCORE_COLOURS.critical;
}

/**
 * Create the main application window
 */
function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1000,
        minHeight: 700,
        title: 'Peterman',
        backgroundColor: '#0A0E14', // Dark theme background
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
        show: false // Don't show until ready
    });

    // Load the Flask app
    const url = `http://${FLASK_HOST}:${FLASK_PORT}`;
    mainWindow.loadURL(url);

    // Show window when ready
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
        console.log('[Peterman] Main window shown');
    });

    // Handle window close - minimise to tray instead
    mainWindow.on('close', (event) => {
        if (!app.isQuitting) {
            event.preventDefault();
            mainWindow.hide();
            console.log('[Peterman] Window hidden to tray');
        }
    });

    // Open DevTools in development
    if (process.argv.includes('--dev')) {
        mainWindow.webContents.openDevTools();
    }

    return mainWindow;
}

/**
 * Create system tray icon
 */
function createTray() {
    // Create a simple coloured icon for the tray
    const iconSize = 16;
    const canvas = `
        <svg width="${iconSize}" height="${iconSize}" xmlns="http://www.w3.org/2000/svg">
            <circle cx="8" cy="8" r="7" fill="${getScoreColour(currentScore)}" stroke="#0A0E14" stroke-width="1"/>
            <text x="8" y="12" text-anchor="middle" fill="white" font-size="8" font-family="Arial">P</text>
        </svg>
    `;
    
    // Use a simple icon - in production would use proper icon files
    const icon = nativeImage.createEmpty();
    
    tray = new Tray(icon.isEmpty() ? nativeImage.createFromDataURL('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAbwAAAG8B8aLcQwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAADPSURBVDiNpZMxDoJAEEXfLhQewMbOxtLGO3gFb2BnZ2Nn5xW8gqW1hY2F4A1ILEQxIMvlL5PJzOT/nYRMVGZmrqCpWoKZmVlVVa8g0pCIZBFJhEgCVRXWex8GgaaJ1xizEBEkIokkIokgIomIqKpqAJAkSZIkCYDv+yiKwjAMWZa9ruv6DABEVFV9j+P4DmDbtm3btn3fR1H0bYyJUuqfMRaAYRiGYRjGfwWwAJkZWJYl27ZJkuQ/AAt8h5zA5XzWwQAAAABJRU5ErkJggg==') : icon);

    tray.setToolTip('Peterman - AI Brand Presence');
    
    updateTrayMenu();

    // Tray click - show window
    tray.on('click', () => {
        if (mainWindow) {
            if (mainWindow.isVisible()) {
                mainWindow.focus();
            } else {
                mainWindow.show();
            }
        }
    });

    console.log('[Peterman] System tray created');
}

/**
 * Update tray context menu
 */
function updateTrayMenu() {
    const contextMenu = Menu.buildFromTemplate([
        {
            label: 'Peterman',
            enabled: false
        },
        {
            label: `Score: ${currentScore}`,
            enabled: false
        },
        { type: 'separator' },
        {
            label: 'Open Peterman',
            click: () => {
                mainWindow.show();
                mainWindow.focus();
            }
        },
        {
            label: 'Refresh Data',
            click: () => {
                if (mainWindow) {
                    mainWindow.webContents.send('refresh-data');
                }
            }
        },
        { type: 'separator' },
        {
            label: 'Quit',
            click: () => {
                app.isQuitting = true;
                app.quit();
            }
        }
    ]);

    tray.setContextMenu(contextMenu);
}

/**
 * Start the Flask backend
 */
function startFlask() {
    console.log('[Peterman] Starting Flask backend...');
    
    // Use start.bat on Windows for proper environment setup
    const isWindows = process.platform === 'win32';
    const appPath = path.join(__dirname, '..');
    
    if (isWindows) {
        // Try to use start.bat first, fallback to python
        const startBatPath = path.join(appPath, 'start.bat');
        const fs = require('fs');
        
        if (fs.existsSync(startBatPath)) {
            console.log('[Peterman] Using start.bat for Flask...');
            flaskProcess = spawn('cmd', ['/c', 'start.bat'], {
                cwd: appPath,
                stdio: ['ignore', 'pipe', 'pipe'],
                detached: false,
                shell: true
            });
        } else {
            console.log('[Peterman] Using python directly...');
            flaskProcess = spawn('python', ['run.py'], {
                cwd: appPath,
                stdio: ['ignore', 'pipe', 'pipe'],
                detached: false
            });
        }
    } else {
        flaskProcess = spawn('python3', ['run.py'], {
            cwd: appPath,
            stdio: ['ignore', 'pipe', 'pipe'],
            detached: false
        });
    }

    // Log Flask output
    flaskProcess.stdout.on('data', (data) => {
        console.log(`[Flask] ${data}`);
    });

    flaskProcess.stderr.on('data', (data) => {
        console.error(`[Flask Error] ${data}`);
    });

    flaskProcess.on('error', (err) => {
        console.error('[Peterman] Failed to start Flask:', err);
    });

    flaskProcess.on('exit', (code) => {
        console.log(`[Peterman] Flask exited with code ${code}`);
        if (!app.isQuitting) {
            // Restart Flask if it crashes
            console.log('[Peterman] Restarting Flask...');
            setTimeout(startFlask, 2000);
        }
    });

    // Wait for Flask to be ready
    return waitForFlask();
}

/**
 * Wait for Flask to be ready
 */
function waitForFlask() {
    return new Promise((resolve, reject) => {
        const startTime = Date.now();
        
        const checkInterval = setInterval(() => {
            const http = require('http');
            
            const req = http.get(`http://${FLASK_HOST}:${FLASK_PORT}/api/health`, (res) => {
                clearInterval(checkInterval);
                console.log('[Peterman] Flask backend is ready');
                resolve();
            });
            
            req.on('error', () => {
                // Still waiting...
                if (Date.now() - startTime > STARTUP_TIMEOUT) {
                    clearInterval(checkInterval);
                    console.warn('[Peterman] Flask startup timeout, continuing anyway...');
                    resolve(); // Resolve anyway to show window
                }
            });
        }, 1000);
    });
}

/**
 * Update score from renderer process
 */
ipcMain.on('update-score', (event, score) => {
    currentScore = score;
    updateTrayMenu();
    console.log(`[Peterman] Score updated: ${score}`);
});

// App ready
app.whenReady().then(async () => {
    console.log('[Peterman] Application starting...');
    
    // Start Flask backend first
    await startFlask();
    
    // Create window and tray
    createWindow();
    createTray();
    
    console.log('[Peterman] Application ready');
});

// Handle all windows closed
app.on('window-all-closed', () => {
    // Don't quit on window close - stay in tray
    if (process.platform !== 'darwin') {
        // Keep running in tray
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    } else {
        mainWindow.show();
    }
});

// Clean shutdown
app.on('before-quit', () => {
    console.log('[Peterman] Shutting down...');
    app.isQuitting = true;
    
    if (flaskProcess) {
        flaskProcess.kill();
        console.log('[Peterman] Flask process killed');
    }
});

app.on('quit', () => {
    console.log('[Peterman] Application quit');
});
