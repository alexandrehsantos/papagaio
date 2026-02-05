const { app, BrowserWindow, ipcMain, dialog, nativeTheme, Tray, Menu, nativeImage, Notification } = require('electron');
const path = require('path');
const fs = require('fs');
const os = require('os');
const { execFile } = require('child_process');

// Config file paths
const CONFIG_DIR = path.join(os.homedir(), '.config', 'papagaio');
const CONFIG_FILE = path.join(CONFIG_DIR, 'config.ini');
const LICENSE_FILE = path.join(CONFIG_DIR, '.license');
const TRIAL_FILE = path.join(CONFIG_DIR, '.trial');

let mainWindow;
let tray = null;
let isQuitting = false;
let currentLanguage = 'en';

// Translations for tray menu
const trayTranslations = {
  en: {
    open: 'Open Settings',
    startDaemon: 'Start Daemon',
    stopDaemon: 'Stop Daemon',
    restartDaemon: 'Restart Daemon',
    daemonRunning: 'Daemon: Running',
    daemonStopped: 'Daemon: Stopped',
    quit: 'Quit',
    appName: 'Papagaio',
    started: 'Daemon started',
    stopped: 'Daemon stopped',
    restarted: 'Daemon restarted',
    error: 'Error'
  },
  pt: {
    open: 'Abrir Configurações',
    startDaemon: 'Iniciar Daemon',
    stopDaemon: 'Parar Daemon',
    restartDaemon: 'Reiniciar Daemon',
    daemonRunning: 'Daemon: Executando',
    daemonStopped: 'Daemon: Parado',
    quit: 'Sair',
    appName: 'Papagaio',
    started: 'Daemon iniciado',
    stopped: 'Daemon parado',
    restarted: 'Daemon reiniciado',
    error: 'Erro'
  }
};

function t(key) {
  return trayTranslations[currentLanguage]?.[key] || trayTranslations['en'][key] || key;
}

// Load language from config
function loadLanguageFromConfig() {
  try {
    if (fs.existsSync(CONFIG_FILE)) {
      const content = fs.readFileSync(CONFIG_FILE, 'utf-8');
      const match = content.match(/language\s*=\s*(\w+)/);
      if (match) {
        currentLanguage = match[1];
      }
    }
  } catch (e) {
    console.error('Error loading language:', e);
  }
}

// Check daemon status
function checkDaemonStatus() {
  return new Promise((resolve) => {
    execFile('systemctl', ['--user', 'is-active', 'papagaio'], (error, stdout) => {
      resolve(stdout.trim() === 'active');
    });
  });
}

// Control daemon
function controlDaemon(action) {
  return new Promise((resolve) => {
    execFile('systemctl', ['--user', action, 'papagaio'], (error, stdout, stderr) => {
      if (error) {
        resolve({ success: false, error: stderr || error.message });
      } else {
        resolve({ success: true });
      }
    });
  });
}

// Show notification
function showNotification(title, body) {
  if (Notification.isSupported()) {
    new Notification({ title, body, icon: path.join(__dirname, 'icon.png') }).show();
  }
}

// Create tray icon
async function createTray() {
  const iconPath = path.join(__dirname, 'build', 'icons', '32x32.png');
  const fallbackIcon = path.join(__dirname, 'icon.png');

  let trayIcon;
  if (fs.existsSync(iconPath)) {
    trayIcon = nativeImage.createFromPath(iconPath);
  } else if (fs.existsSync(fallbackIcon)) {
    trayIcon = nativeImage.createFromPath(fallbackIcon).resize({ width: 22, height: 22 });
  } else {
    // Create a simple colored icon as fallback
    trayIcon = nativeImage.createEmpty();
  }

  tray = new Tray(trayIcon);
  tray.setToolTip(t('appName'));

  // Update tray menu
  await updateTrayMenu();

  // Double-click to open window
  tray.on('double-click', () => {
    showWindow();
  });

  // Update status periodically
  setInterval(updateTrayMenu, 5000);
}

// Update tray context menu
async function updateTrayMenu() {
  if (!tray) return;

  const isRunning = await checkDaemonStatus();

  const statusLabel = isRunning ? t('daemonRunning') : t('daemonStopped');
  tray.setToolTip(`${t('appName')} - ${statusLabel}`);

  const contextMenu = Menu.buildFromTemplate([
    {
      label: t('appName'),
      enabled: false,
      icon: nativeImage.createFromPath(path.join(__dirname, 'build', 'icons', '16x16.png')).resize({ width: 16, height: 16 })
    },
    { type: 'separator' },
    {
      label: statusLabel,
      enabled: false
    },
    { type: 'separator' },
    {
      label: t('open'),
      click: () => showWindow()
    },
    { type: 'separator' },
    {
      label: t('startDaemon'),
      enabled: !isRunning,
      click: async () => {
        const result = await controlDaemon('start');
        if (result.success) {
          showNotification(t('appName'), t('started'));
          updateTrayMenu();
        }
      }
    },
    {
      label: t('stopDaemon'),
      enabled: isRunning,
      click: async () => {
        const result = await controlDaemon('stop');
        if (result.success) {
          showNotification(t('appName'), t('stopped'));
          updateTrayMenu();
        }
      }
    },
    {
      label: t('restartDaemon'),
      enabled: isRunning,
      click: async () => {
        const result = await controlDaemon('restart');
        if (result.success) {
          showNotification(t('appName'), t('restarted'));
          updateTrayMenu();
        }
      }
    },
    { type: 'separator' },
    {
      label: t('quit'),
      click: () => {
        isQuitting = true;
        app.quit();
      }
    }
  ]);

  tray.setContextMenu(contextMenu);
}

// Show main window
function showWindow() {
  if (mainWindow) {
    if (mainWindow.isMinimized()) {
      mainWindow.restore();
    }
    mainWindow.show();
    mainWindow.focus();
  } else {
    createWindow();
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 700,
    height: 600,
    minWidth: 600,
    minHeight: 500,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    },
    icon: path.join(__dirname, 'icon.png'),
    title: 'Papagaio Settings',
    show: false
  });

  mainWindow.loadFile('index.html');
  mainWindow.setMenuBarVisibility(false);

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Minimize to tray instead of closing
  mainWindow.on('close', (event) => {
    if (!isQuitting) {
      event.preventDefault();
      mainWindow.hide();
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// App ready
app.whenReady().then(async () => {
  loadLanguageFromConfig();
  createWindow();
  await createTray();
});

// Prevent app from quitting when all windows are closed (keep tray)
app.on('window-all-closed', () => {
  // Don't quit on macOS unless explicitly quitting
  if (process.platform !== 'darwin' && isQuitting) {
    app.quit();
  }
});

app.on('activate', () => {
  showWindow();
});

app.on('before-quit', () => {
  isQuitting = true;
});

// Parse INI file
function parseINI(content) {
  const config = {};
  let currentSection = null;

  content.split('\n').forEach(line => {
    line = line.trim();
    if (!line || line.startsWith('#') || line.startsWith(';')) return;

    const sectionMatch = line.match(/^\[(.+)\]$/);
    if (sectionMatch) {
      currentSection = sectionMatch[1];
      config[currentSection] = {};
      return;
    }

    const keyValueMatch = line.match(/^([^=]+)=(.*)$/);
    if (keyValueMatch && currentSection) {
      config[currentSection][keyValueMatch[1].trim()] = keyValueMatch[2].trim();
    }
  });

  return config;
}

// Generate INI content
function generateINI(config) {
  let content = '# Papagaio Configuration\n\n';

  for (const section in config) {
    content += `[${section}]\n`;
    for (const key in config[section]) {
      content += `${key} = ${config[section][key]}\n`;
    }
    content += '\n';
  }

  return content;
}

// Default configuration
function getDefaults() {
  return {
    General: {
      model: 'small',
      language: 'en',
      hotkey: '<ctrl>+<alt>+v',
      cache_dir: path.join(os.homedir(), '.cache', 'whisper-models')
    },
    Audio: {
      silence_threshold: '400',
      silence_duration: '5.0',
      max_recording_time: '3600',
      transcription_language: 'auto'
    },
    Advanced: {
      use_ydotool: 'false',
      typing_delay: '0.3'
    }
  };
}

// Load configuration
ipcMain.handle('load-config', async () => {
  try {
    if (!fs.existsSync(CONFIG_DIR)) {
      fs.mkdirSync(CONFIG_DIR, { recursive: true });
    }

    if (fs.existsSync(CONFIG_FILE)) {
      const content = fs.readFileSync(CONFIG_FILE, 'utf-8');
      const config = parseINI(content);

      // Merge with defaults
      const defaults = getDefaults();
      for (const section in defaults) {
        if (!config[section]) config[section] = {};
        for (const key in defaults[section]) {
          if (config[section][key] === undefined) {
            config[section][key] = defaults[section][key];
          }
        }
      }

      // Update current language
      if (config.General?.language) {
        currentLanguage = config.General.language;
        updateTrayMenu();
      }

      return config;
    }

    return getDefaults();
  } catch (error) {
    console.error('Error loading config:', error);
    return getDefaults();
  }
});

// Save configuration
ipcMain.handle('save-config', async (event, config) => {
  try {
    if (!fs.existsSync(CONFIG_DIR)) {
      fs.mkdirSync(CONFIG_DIR, { recursive: true });
    }

    const content = generateINI(config);
    fs.writeFileSync(CONFIG_FILE, content);

    // Update language if changed
    if (config.General?.language) {
      currentLanguage = config.General.language;
      updateTrayMenu();
    }

    return { success: true };
  } catch (error) {
    console.error('Error saving config:', error);
    return { success: false, error: error.message };
  }
});

// Restart daemon using execFile (safer than exec)
ipcMain.handle('restart-daemon', async () => {
  const result = await controlDaemon('restart');
  if (result.success) {
    updateTrayMenu();
  }
  return result;
});

// Check daemon status using execFile
ipcMain.handle('check-daemon-status', async () => {
  return checkDaemonStatus();
});

// Get license status
ipcMain.handle('get-license-status', async () => {
  try {
    // Check for valid license
    if (fs.existsSync(LICENSE_FILE)) {
      const licenseData = JSON.parse(fs.readFileSync(LICENSE_FILE, 'utf-8'));
      if (licenseData.key) {
        return {
          status: 'licensed',
          email: licenseData.email,
          message: 'License active'
        };
      }
    }

    // Check trial status
    if (fs.existsSync(TRIAL_FILE)) {
      const trialData = JSON.parse(fs.readFileSync(TRIAL_FILE, 'utf-8'));
      const startDate = new Date(trialData.start_date);
      const now = new Date();
      const elapsed = Math.floor((now - startDate) / (1000 * 60 * 60 * 24));
      const remaining = Math.max(0, 7 - elapsed);

      if (remaining > 0) {
        return {
          status: 'trial',
          remaining_days: remaining,
          message: `Trial: ${remaining} days remaining`
        };
      } else {
        return {
          status: 'expired',
          message: 'Trial expired. Please purchase a license.'
        };
      }
    }

    // First run - create trial
    const trialData = {
      start_date: new Date().toISOString(),
      machine_id: os.hostname()
    };
    fs.writeFileSync(TRIAL_FILE, JSON.stringify(trialData));

    return {
      status: 'trial',
      remaining_days: 7,
      message: 'Trial: 7 days remaining'
    };
  } catch (error) {
    return {
      status: 'error',
      message: error.message
    };
  }
});

// Browse for directory
ipcMain.handle('browse-directory', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory']
  });

  if (!result.canceled && result.filePaths.length > 0) {
    return result.filePaths[0];
  }
  return null;
});

// Get system theme
ipcMain.handle('get-theme', () => {
  return nativeTheme.shouldUseDarkColors ? 'dark' : 'light';
});
