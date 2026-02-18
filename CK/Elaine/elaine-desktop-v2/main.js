const { app, BrowserWindow, Tray, Menu, nativeImage, shell } = require('electron')
const path = require('path')

const ELAINE_URL = 'http://172.18.240.96:5000'

let tray = null
let win = null
let isQuitting = false

function createWindow() {
  win = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    title: 'ELAINE — Almost Magic',
    icon: path.join(__dirname, 'assets/icon.png'),
    show: false,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: false
    }
  })

  win.loadURL(ELAINE_URL)

  win.webContents.on('did-fail-load', () => {
    win.loadFile(path.join(__dirname, 'offline.html'))
  })

  win.once('ready-to-show', () => {
    win.show()
  })

  win.on('close', (e) => {
    if (!isQuitting) {
      e.preventDefault()
      win.hide()
      tray.displayBalloon({
        title: 'ELAINE',
        content: 'Still running in the background. Click the tray icon to return.',
        icon: path.join(__dirname, 'assets/icon.png')
      })
    }
  })
}

function createTray() {
  const icon = nativeImage.createFromPath(path.join(__dirname, 'assets/tray-icon.png'))
  tray = new Tray(icon)
  tray.setToolTip('ELAINE — Almost Magic Tech Lab')

  const menu = Menu.buildFromTemplate([
    { label: 'Open ELAINE', click: () => { win.show(); win.focus() } },
    { label: 'Morning Briefing', click: () => {
        win.show()
        win.webContents.executeJavaScript(`
          fetch('/api/briefing/morning').then(r=>r.json()).then(d=>console.log(d))
        `)
      }
    },
    { type: 'separator' },
    { label: 'Open in Browser', click: () => shell.openExternal(ELAINE_URL) },
    { type: 'separator' },
    { label: 'Quit ELAINE', click: () => { isQuitting = true; app.quit() } }
  ])

  tray.setContextMenu(menu)

  tray.on('click', () => {
    if (win.isVisible()) {
      win.hide()
    } else {
      win.show()
      win.focus()
    }
  })
}

app.whenReady().then(() => {
  app.setLoginItemSettings({
    openAtLogin: true,
    openAsHidden: true,
    name: 'ELAINE'
  })

  createWindow()
  createTray()
})

app.on('window-all-closed', (e) => {
  e.preventDefault()
})

app.on('before-quit', () => {
  isQuitting = true
})
