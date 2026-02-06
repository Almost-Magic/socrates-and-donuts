/**
 * Elaine Desktop — Electron Main Process
 * 
 * System tray app that connects to Elaine's Flask API (localhost:5000).
 * Provides: morning briefing, gravity field, gatekeeper status, quick actions.
 * 
 * Almost Magic Tech Lab
 */

const { app, BrowserWindow, Tray, Menu, nativeImage, ipcMain, Notification } = require('electron');
const path = require('path');

let mainWindow = null;
let tray = null;

const ELAINE_URL = 'http://127.0.0.1:5000';

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 860,
    minWidth: 900,
    minHeight: 600,
    resizable: true,
    frame: false,
    transparent: false,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    },
    icon: path.join(__dirname, 'assets', 'icon.png'),
    title: 'Elaine — Chief of Staff',
    skipTaskbar: false,
  });

  mainWindow.loadFile('renderer/index.html');

  mainWindow.on('close', (event) => {
    // Minimise to tray instead of closing
    event.preventDefault();
    mainWindow.hide();
  });
}

function createTray() {
  const iconPath = path.join(__dirname, 'assets', 'tray-icon.png');
  // Fallback to a default if icon doesn't exist
  let trayIcon;
  try {
    trayIcon = nativeImage.createFromPath(iconPath).resize({ width: 16, height: 16 });
  } catch {
    trayIcon = nativeImage.createEmpty();
  }

  tray = new Tray(trayIcon);
  tray.setToolTip('Elaine — AI Chief of Staff');

  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Open Elaine',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.focus();
        }
      },
    },
    { type: 'separator' },
    {
      label: 'Morning Briefing',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.webContents.send('navigate', 'briefing');
        }
      },
    },
    {
      label: 'Gravity Field',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.webContents.send('navigate', 'gravity');
        }
      },
    },
    {
      label: 'Gatekeeper Status',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.webContents.send('navigate', 'gatekeeper');
        }
      },
    },
    { type: 'separator' },
    {
      label: 'Quick Check (Gatekeeper)',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.webContents.send('navigate', 'quick-check');
        }
      },
    },
    { type: 'separator' },
    {
      label: 'Quit Elaine',
      click: () => {
        mainWindow.destroy();
        app.quit();
      },
    },
  ]);

  tray.setContextMenu(contextMenu);

  tray.on('click', () => {
    if (mainWindow) {
      if (mainWindow.isVisible()) {
        mainWindow.hide();
      } else {
        mainWindow.show();
        mainWindow.focus();
      }
    }
  });
}

// ── IPC Handlers (renderer talks to Elaine API via main process) ──

ipcMain.handle('elaine-api', async (event, method, path, body) => {
  try {
    const url = `${ELAINE_URL}${path}`;
    const options = {
      method: method || 'GET',
      headers: { 'Content-Type': 'application/json' },
    };
    if (body && method !== 'GET') {
      options.body = JSON.stringify(body);
    }
    const response = await fetch(url, options);
    return await response.json();
  } catch (error) {
    return { error: `Elaine not reachable: ${error.message}` };
  }
});

ipcMain.handle('show-notification', async (event, title, body) => {
  new Notification({ title, body }).show();
});

// ── App Lifecycle ──

app.whenReady().then(() => {
  createWindow();
  createTray();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  // Don't quit — stay in tray
});
