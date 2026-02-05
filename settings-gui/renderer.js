const { ipcRenderer, shell } = require('electron');
const { setLanguage, t, applyTranslations } = require('./i18n');

let config = {};

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
  await loadConfig();
  await updateDaemonStatus();
  await loadLicenseStatus();
  setupEventListeners();

  // Update daemon status every 5 seconds
  setInterval(updateDaemonStatus, 5000);
});

// Load configuration
async function loadConfig() {
  config = await ipcRenderer.invoke('load-config');
  populateForm();

  // Apply translations based on configured language
  const language = config.General?.language || 'en';
  setLanguage(language);
}

// Populate form with config values
function populateForm() {
  // General
  const model = config.General?.model || 'small';
  document.querySelector(`input[name="model"][value="${model}"]`).checked = true;

  const language = config.General?.language || 'en';
  document.querySelector(`input[name="language"][value="${language}"]`).checked = true;

  const hotkey = config.General?.hotkey || '<ctrl>+<alt>+v';
  document.getElementById('hotkey').value = hotkey;

  // Audio
  const threshold = config.Audio?.silence_threshold || '400';
  document.getElementById('silence_threshold').value = threshold;
  document.getElementById('silence_threshold_value').textContent = threshold;

  const duration = config.Audio?.silence_duration || '5.0';
  document.getElementById('silence_duration').value = parseFloat(duration);

  const maxTime = config.Audio?.max_recording_time || '3600';
  document.getElementById('max_recording_time').value = parseInt(maxTime);

  const transLang = config.Audio?.transcription_language || 'auto';
  document.getElementById('transcription_language').value = transLang;

  // Advanced
  const editBeforeSend = config.General?.edit_before_send === 'true';
  document.getElementById('edit_before_send').checked = editBeforeSend;

  const useYdotool = config.Advanced?.use_ydotool === 'true';
  document.getElementById('use_ydotool').checked = useYdotool;

  const typingDelay = config.Advanced?.typing_delay || '0.1';
  document.getElementById('typing_delay').value = parseFloat(typingDelay);

  const cacheDir = config.General?.cache_dir || '~/.cache/whisper-models';
  document.getElementById('cache_dir').value = cacheDir;
}

// Collect form values into config object
function collectFormValues() {
  // General
  config.General = config.General || {};
  config.General.model = document.querySelector('input[name="model"]:checked').value;
  config.General.language = document.querySelector('input[name="language"]:checked').value;
  config.General.hotkey = document.getElementById('hotkey').value;
  config.General.cache_dir = document.getElementById('cache_dir').value;
  config.General.edit_before_send = document.getElementById('edit_before_send').checked ? 'true' : 'false';

  // Audio
  config.Audio = config.Audio || {};
  config.Audio.silence_threshold = document.getElementById('silence_threshold').value;
  config.Audio.silence_duration = document.getElementById('silence_duration').value;
  config.Audio.max_recording_time = document.getElementById('max_recording_time').value;
  config.Audio.transcription_language = document.getElementById('transcription_language').value;

  // Advanced
  config.Advanced = config.Advanced || {};
  config.Advanced.use_ydotool = document.getElementById('use_ydotool').checked ? 'true' : 'false';
  config.Advanced.typing_delay = document.getElementById('typing_delay').value;

  return config;
}

// Save configuration
async function saveConfig() {
  const configToSave = collectFormValues();
  const result = await ipcRenderer.invoke('save-config', configToSave);

  if (result.success) {
    showToast(t('configSaved'), 'success');
  } else {
    showToast(t('saveFailed') + ' ' + result.error, 'error');
  }

  return result.success;
}

// Save and restart daemon
async function saveAndRestart() {
  const saved = await saveConfig();
  if (!saved) return;

  showToast(t('restarting'), 'info');

  const result = await ipcRenderer.invoke('restart-daemon');

  if (result.success) {
    showToast(t('restartSuccess'), 'success');
  } else {
    showToast(t('restartFailed') + ' ' + result.error, 'error');
  }

  await updateDaemonStatus();
}

// Update daemon status
async function updateDaemonStatus() {
  const isActive = await ipcRenderer.invoke('check-daemon-status');
  const statusEl = document.getElementById('daemon-status');
  const textEl = statusEl.querySelector('.status-text');

  statusEl.className = 'daemon-status ' + (isActive ? 'running' : 'stopped');
  textEl.textContent = isActive ? t('daemonRunning') : t('daemonStopped');
}

// Load license status
async function loadLicenseStatus() {
  const status = await ipcRenderer.invoke('get-license-status');
  const statusEl = document.getElementById('license-status');
  const titleEl = document.getElementById('license-title');
  const messageEl = document.getElementById('license-message');
  const activationEl = document.getElementById('activation-section');

  statusEl.className = 'license-status ' + status.status;

  if (status.status === 'licensed') {
    titleEl.textContent = '✅ ' + t('licensed');
    messageEl.textContent = status.email ? `${t('registeredTo')} ${status.email}` : t('licenseActive');
    activationEl.style.display = 'none';
  } else if (status.status === 'trial') {
    titleEl.textContent = `⏱️ ${t('trial')} - ${status.remaining_days} ${t('daysRemaining')}`;
    messageEl.textContent = t('trialMessage');
    activationEl.style.display = 'block';
  } else {
    titleEl.textContent = '⚠️ ' + t('trialExpired');
    messageEl.textContent = t('trialExpiredMessage');
    activationEl.style.display = 'block';
  }
}

// Setup event listeners
function setupEventListeners() {
  // Tab switching
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

      tab.classList.add('active');
      document.getElementById(tab.dataset.tab).classList.add('active');
    });
  });

  // Range slider
  const threshold = document.getElementById('silence_threshold');
  threshold.addEventListener('input', () => {
    document.getElementById('silence_threshold_value').textContent = threshold.value;
  });

  // Browse cache directory (if element exists)
  const browseBtn = document.getElementById('browse_cache');
  if (browseBtn) {
    browseBtn.addEventListener('click', async () => {
      const path = await ipcRenderer.invoke('browse-directory');
      if (path) {
        document.getElementById('cache_dir').value = path;
      }
    });
  }

  // Hotkey capture
  const hotkeyInput = document.getElementById('hotkey');
  const captureBtn = document.getElementById('capture_hotkey');
  let isCapturing = false;

  captureBtn.addEventListener('click', () => {
    if (isCapturing) {
      isCapturing = false;
      captureBtn.textContent = t('capture');
      hotkeyInput.classList.remove('capturing');
      hotkeyInput.placeholder = t('hotkeyPlaceholder');
    } else {
      isCapturing = true;
      captureBtn.textContent = t('stop');
      hotkeyInput.classList.add('capturing');
      hotkeyInput.placeholder = t('hotkeyPlaceholder');
      hotkeyInput.focus();
    }
  });

  hotkeyInput.addEventListener('keydown', (e) => {
    if (!isCapturing) return;
    e.preventDefault();

    const parts = [];
    if (e.ctrlKey) parts.push('<ctrl>');
    if (e.shiftKey) parts.push('<shift>');
    if (e.altKey) parts.push('<alt>');
    if (e.metaKey) parts.push('<super>');

    // Add the main key if it's not a modifier
    const key = e.key.toLowerCase();
    if (!['control', 'shift', 'alt', 'meta'].includes(key)) {
      parts.push(key);
      hotkeyInput.value = parts.join('+');

      // Stop capturing after key is pressed
      isCapturing = false;
      captureBtn.textContent = t('capture');
      hotkeyInput.classList.remove('capturing');
      hotkeyInput.placeholder = t('hotkeyPlaceholder');
    }
  });

  // Preset buttons
  document.querySelectorAll('.preset-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      hotkeyInput.value = btn.dataset.hotkey;
    });
  });

  // Language change - update UI immediately
  document.querySelectorAll('input[name="language"]').forEach(radio => {
    radio.addEventListener('change', (e) => {
      setLanguage(e.target.value);
    });
  });

  // Buttons
  document.getElementById('btn-cancel').addEventListener('click', () => {
    window.close();
  });

  document.getElementById('btn-save').addEventListener('click', saveConfig);

  document.getElementById('btn-save-restart').addEventListener('click', saveAndRestart);

  // External links
  document.querySelectorAll('a[target="_blank"]').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      shell.openExternal(link.href);
    });
  });

  // License activation
  document.getElementById('activate_btn')?.addEventListener('click', async () => {
    const key = document.getElementById('license_key').value.trim();
    if (!key) {
      showToast(t('enterLicenseKey'), 'error');
      return;
    }

    showToast(t('validatingLicense'), 'info');

    // For now, just save the key locally (real validation would call Gumroad API)
    // This is simplified - the Python license module handles actual validation
    showToast(t('usePapagaioActivate'), 'info');
  });
}

// Toast notification
function showToast(message, type = 'info') {
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);

  setTimeout(() => toast.classList.add('show'), 10);
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}
