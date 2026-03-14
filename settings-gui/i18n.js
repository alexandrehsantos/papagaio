const translations = {
  en: {
    // Header
    appTitle: 'Papagaio Settings',
    daemonRunning: 'Running',
    daemonStopped: 'Stopped',
    daemonChecking: 'Checking...',

    // Tabs
    tabGeneral: 'General',
    tabAudio: 'Audio',
    tabTranscription: 'Transcription',
    tabAdvanced: 'Advanced',
    tabLicense: 'License',

    // General Tab
    recognitionQuality: 'Recognition Quality',
    recognitionQualityDesc: 'Choose based on your needs',
    qualityFast: 'Fast',
    qualityFastDesc: 'Quick dictation',
    qualityBalanced: 'Balanced',
    qualityBalancedDesc: 'Everyday use',
    qualityHigh: 'High',
    qualityHighDesc: 'Best for most',
    qualityMaximum: 'Maximum',
    qualityMaximumDesc: 'Best accuracy',
    recommended: 'Recommended',

    hotkey: 'Hotkey',
    hotkeyDesc: 'Global shortcut to activate voice input',
    hotkeyPlaceholder: 'Press keys or type manually',
    capture: 'Capture',
    stop: 'Stop',
    presets: 'Presets:',
    hotkeyHint: 'Format: <ctrl>+<shift>+<alt>+key (e.g., <ctrl>+<alt>+v)',

    interfaceLanguage: 'Interface Language',
    interfaceLanguageDesc: 'Language for messages and notifications',
    langEnglish: 'English',
    langPortuguese: 'Português',

    // Audio Tab
    silenceThreshold: 'Silence Threshold',
    silenceThresholdDesc: 'Volume level to detect silence (RMS). Lower = more sensitive',
    silenceDuration: 'Silence Duration',
    silenceDurationDesc: 'Seconds of silence before auto-stop recording',
    seconds: 'seconds',
    maxRecordingTime: 'Max Recording Time',
    maxRecordingTimeDesc: 'Maximum recording duration limit',
    maxRecordingTimeHint: '3600 seconds = 1 hour',

    // Transcription Tab
    transcriptionLanguage: 'Transcription Language',
    transcriptionLanguageDesc: 'Force a specific language or use auto-detection',
    autoDetect: 'Auto-detect',
    transcriptionHint: 'Forcing a language improves accuracy when auto-detect fails',
    transcriptionTip: 'Tip',
    transcriptionTipText: 'If you primarily speak one language, setting it explicitly can significantly improve transcription accuracy, especially for short phrases.',

    // Language options
    langGroupCommon: 'Common',
    langGroupAsian: 'Asian',
    langGroupOther: 'Other',
    langPt: 'Portuguese',
    langEn: 'English',
    langEs: 'Spanish',
    langFr: 'French',
    langDe: 'German',
    langIt: 'Italian',
    langJa: 'Japanese',
    langZh: 'Chinese',
    langKo: 'Korean',
    langHi: 'Hindi',
    langTh: 'Thai',
    langVi: 'Vietnamese',
    langId: 'Indonesian',
    langRu: 'Russian',
    langAr: 'Arabic',
    langNl: 'Dutch',
    langPl: 'Polish',
    langTr: 'Turkish',
    langUk: 'Ukrainian',
    langCs: 'Czech',
    langEl: 'Greek',
    langRo: 'Romanian',
    langDa: 'Danish',
    langFi: 'Finnish',
    langHu: 'Hungarian',
    langNo: 'Norwegian',
    langSv: 'Swedish',

    // Advanced Tab
    keyboardBackend: 'Keyboard Backend',
    keyboardBackendDesc: 'Method used to type transcribed text',
    forceYdotool: 'Force ydotool (for Wayland)',
    keyboardBackendHint: 'Leave unchecked for auto-detection (xdotool for X11, ydotool for Wayland)',
    typingDelay: 'Typing Delay',
    typingDelayDesc: 'Delay before typing begins (to ensure focus)',

    // License Tab
    checkingLicense: 'Checking license...',
    licensed: 'Licensed',
    registeredTo: 'Registered to:',
    licenseActive: 'License active',
    trial: 'Trial',
    daysRemaining: 'days remaining',
    trialMessage: 'Purchase a license to support development!',
    trialExpired: 'Trial Expired',
    trialExpiredMessage: 'Please purchase a license to continue using Papagaio.',
    activateLicense: 'Activate License',
    activateLicenseDesc: 'Enter your license key from Gumroad',
    licenseKeyPlaceholder: 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX',
    activate: 'Activate License',
    purchaseLicense: 'Purchase a License',
    purchaseMessage: 'Support development and unlock unlimited use!',
    buyOnGumroad: 'Buy on Gumroad - $29',

    // Footer
    version: 'Papagaio',
    cancel: 'Cancel',
    save: 'Save',
    saveRestart: 'Save & Restart',

    // Toasts
    configSaved: 'Configuration saved!',
    saveFailed: 'Failed to save:',
    restarting: 'Restarting daemon...',
    restartSuccess: 'Daemon restarted successfully!',
    restartFailed: 'Failed to restart daemon:',
    enterLicenseKey: 'Please enter a license key',
    validatingLicense: 'Validating license...',
    usePapagaioActivate: 'Please use papagaio-activate for license validation'
  },

  pt: {
    // Header
    appTitle: 'Configurações do Papagaio',
    daemonRunning: 'Executando',
    daemonStopped: 'Parado',
    daemonChecking: 'Verificando...',

    // Tabs
    tabGeneral: 'Geral',
    tabAudio: 'Áudio',
    tabTranscription: 'Transcrição',
    tabAdvanced: 'Avançado',
    tabLicense: 'Licença',

    // General Tab
    recognitionQuality: 'Qualidade de Reconhecimento',
    recognitionQualityDesc: 'Escolha conforme sua necessidade',
    qualityFast: 'Rápido',
    qualityFastDesc: 'Ditado rápido',
    qualityBalanced: 'Equilibrado',
    qualityBalancedDesc: 'Uso diário',
    qualityHigh: 'Alto',
    qualityHighDesc: 'Melhor para maioria',
    qualityMaximum: 'Máximo',
    qualityMaximumDesc: 'Melhor precisão',
    recommended: 'Recomendado',

    hotkey: 'Tecla de Atalho',
    hotkeyDesc: 'Atalho global para ativar entrada de voz',
    hotkeyPlaceholder: 'Pressione teclas ou digite manualmente',
    capture: 'Capturar',
    stop: 'Parar',
    presets: 'Predefinidos:',
    hotkeyHint: 'Formato: <ctrl>+<shift>+<alt>+tecla (ex: <ctrl>+<alt>+v)',

    interfaceLanguage: 'Idioma da Interface',
    interfaceLanguageDesc: 'Idioma para mensagens e notificações',
    langEnglish: 'English',
    langPortuguese: 'Português',

    // Audio Tab
    silenceThreshold: 'Limite de Silêncio',
    silenceThresholdDesc: 'Nível de volume para detectar silêncio (RMS). Menor = mais sensível',
    silenceDuration: 'Duração do Silêncio',
    silenceDurationDesc: 'Segundos de silêncio antes de parar a gravação automaticamente',
    seconds: 'segundos',
    maxRecordingTime: 'Tempo Máximo de Gravação',
    maxRecordingTimeDesc: 'Limite máximo de duração da gravação',
    maxRecordingTimeHint: '3600 segundos = 1 hora',

    // Transcription Tab
    transcriptionLanguage: 'Idioma da Transcrição',
    transcriptionLanguageDesc: 'Forçar um idioma específico ou usar detecção automática',
    autoDetect: 'Detectar automaticamente',
    transcriptionHint: 'Forçar um idioma melhora a precisão quando a detecção automática falha',
    transcriptionTip: 'Dica',
    transcriptionTipText: 'Se você fala principalmente um idioma, configurá-lo explicitamente pode melhorar significativamente a precisão da transcrição, especialmente para frases curtas.',

    // Language options
    langGroupCommon: 'Comuns',
    langGroupAsian: 'Asiáticos',
    langGroupOther: 'Outros',
    langPt: 'Português',
    langEn: 'Inglês',
    langEs: 'Espanhol',
    langFr: 'Francês',
    langDe: 'Alemão',
    langIt: 'Italiano',
    langJa: 'Japonês',
    langZh: 'Chinês',
    langKo: 'Coreano',
    langHi: 'Hindi',
    langTh: 'Tailandês',
    langVi: 'Vietnamita',
    langId: 'Indonésio',
    langRu: 'Russo',
    langAr: 'Árabe',
    langNl: 'Holandês',
    langPl: 'Polonês',
    langTr: 'Turco',
    langUk: 'Ucraniano',
    langCs: 'Tcheco',
    langEl: 'Grego',
    langRo: 'Romeno',
    langDa: 'Dinamarquês',
    langFi: 'Finlandês',
    langHu: 'Húngaro',
    langNo: 'Norueguês',
    langSv: 'Sueco',

    // Advanced Tab
    keyboardBackend: 'Backend de Teclado',
    keyboardBackendDesc: 'Método usado para digitar o texto transcrito',
    forceYdotool: 'Forçar ydotool (para Wayland)',
    keyboardBackendHint: 'Deixe desmarcado para detecção automática (xdotool para X11, ydotool para Wayland)',
    typingDelay: 'Atraso de Digitação',
    typingDelayDesc: 'Atraso antes de começar a digitar (para garantir foco)',

    // License Tab
    checkingLicense: 'Verificando licença...',
    licensed: 'Licenciado',
    registeredTo: 'Registrado para:',
    licenseActive: 'Licença ativa',
    trial: 'Teste',
    daysRemaining: 'dias restantes',
    trialMessage: 'Compre uma licença para apoiar o desenvolvimento!',
    trialExpired: 'Teste Expirado',
    trialExpiredMessage: 'Por favor, compre uma licença para continuar usando o Papagaio.',
    activateLicense: 'Ativar Licença',
    activateLicenseDesc: 'Digite sua chave de licença do Gumroad',
    licenseKeyPlaceholder: 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX',
    activate: 'Ativar Licença',
    purchaseLicense: 'Comprar uma Licença',
    purchaseMessage: 'Apoie o desenvolvimento e desbloqueie uso ilimitado!',
    buyOnGumroad: 'Comprar no Gumroad - $29',

    // Footer
    version: 'Papagaio',
    cancel: 'Cancelar',
    save: 'Salvar',
    saveRestart: 'Salvar e Reiniciar',

    // Toasts
    configSaved: 'Configuração salva!',
    saveFailed: 'Falha ao salvar:',
    restarting: 'Reiniciando daemon...',
    restartSuccess: 'Daemon reiniciado com sucesso!',
    restartFailed: 'Falha ao reiniciar daemon:',
    enterLicenseKey: 'Por favor, digite uma chave de licença',
    validatingLicense: 'Validando licença...',
    usePapagaioActivate: 'Por favor, use papagaio-activate para validação de licença'
  }
};

let currentLang = 'en';

function setLanguage(lang) {
  currentLang = lang;
  applyTranslations();
}

function t(key) {
  return translations[currentLang]?.[key] || translations['en'][key] || key;
}

function applyTranslations() {
  // Header
  document.querySelector('.logo h1').textContent = t('appTitle');
  document.title = t('appTitle');

  // Tabs
  const tabs = document.querySelectorAll('.tab');
  const tabKeys = ['tabGeneral', 'tabAudio', 'tabTranscription', 'tabAdvanced', 'tabLicense'];
  tabs.forEach((tab, i) => {
    if (tabKeys[i]) tab.textContent = t(tabKeys[i]);
  });

  // General Tab
  const generalSection = document.getElementById('general');
  const settingGroups = generalSection.querySelectorAll('.setting-group');

  // Recognition Quality
  settingGroups[0].querySelector('h3').textContent = t('recognitionQuality');
  settingGroups[0].querySelector('.description').textContent = t('recognitionQualityDesc');

  const qualityCards = settingGroups[0].querySelectorAll('.quality-card');
  const qualityData = [
    { name: 'qualityFast', desc: 'qualityFastDesc' },
    { name: 'qualityBalanced', desc: 'qualityBalancedDesc' },
    { name: 'qualityHigh', desc: 'qualityHighDesc' },
    { name: 'qualityMaximum', desc: 'qualityMaximumDesc' }
  ];
  qualityCards.forEach((card, i) => {
    card.querySelector('.quality-name').textContent = t(qualityData[i].name);
    card.querySelector('.quality-desc').textContent = t(qualityData[i].desc);
    const badge = card.querySelector('.quality-badge');
    if (badge) badge.textContent = t('recommended');
  });

  // Hotkey
  settingGroups[1].querySelector('h3').textContent = t('hotkey');
  settingGroups[1].querySelector('.description').textContent = t('hotkeyDesc');
  document.getElementById('hotkey').placeholder = t('hotkeyPlaceholder');
  settingGroups[1].querySelector('.preset-label').textContent = t('presets');
  settingGroups[1].querySelector('.hint').textContent = t('hotkeyHint');

  // Interface Language
  settingGroups[2].querySelector('h3').textContent = t('interfaceLanguage');
  settingGroups[2].querySelector('.description').textContent = t('interfaceLanguageDesc');
  const langLabels = settingGroups[2].querySelectorAll('.radio-label');
  langLabels[0].textContent = t('langEnglish');
  langLabels[1].textContent = t('langPortuguese');

  // Audio Tab
  const audioSection = document.getElementById('audio');
  const audioGroups = audioSection.querySelectorAll('.setting-group');

  audioGroups[0].querySelector('h3').textContent = t('silenceThreshold');
  audioGroups[0].querySelector('.description').textContent = t('silenceThresholdDesc');

  audioGroups[1].querySelector('h3').textContent = t('silenceDuration');
  audioGroups[1].querySelector('.description').textContent = t('silenceDurationDesc');
  audioGroups[1].querySelector('.unit').textContent = t('seconds');

  audioGroups[2].querySelector('h3').textContent = t('maxRecordingTime');
  audioGroups[2].querySelector('.description').textContent = t('maxRecordingTimeDesc');
  audioGroups[2].querySelector('.unit').textContent = t('seconds');
  audioGroups[2].querySelector('.hint').textContent = t('maxRecordingTimeHint');

  // Transcription Tab
  const transSection = document.getElementById('transcription');
  const transGroup = transSection.querySelector('.setting-group');
  transGroup.querySelector('h3').textContent = t('transcriptionLanguage');
  transGroup.querySelector('.description').textContent = t('transcriptionLanguageDesc');
  transGroup.querySelector('.hint').textContent = t('transcriptionHint');

  const select = document.getElementById('transcription_language');
  select.options[0].textContent = t('autoDetect');
  const optgroups = select.querySelectorAll('optgroup');
  optgroups[0].label = t('langGroupCommon');
  optgroups[1].label = t('langGroupAsian');
  optgroups[2].label = t('langGroupOther');

  // Update language options
  const langMap = {
    'pt': 'langPt', 'en': 'langEn', 'es': 'langEs', 'fr': 'langFr',
    'de': 'langDe', 'it': 'langIt', 'ja': 'langJa', 'zh': 'langZh',
    'ko': 'langKo', 'hi': 'langHi', 'th': 'langTh', 'vi': 'langVi',
    'id': 'langId', 'ru': 'langRu', 'ar': 'langAr', 'nl': 'langNl',
    'pl': 'langPl', 'tr': 'langTr', 'uk': 'langUk', 'cs': 'langCs',
    'el': 'langEl', 'ro': 'langRo', 'da': 'langDa', 'fi': 'langFi',
    'hu': 'langHu', 'no': 'langNo', 'sv': 'langSv'
  };
  select.querySelectorAll('option[value]').forEach(opt => {
    if (opt.value !== 'auto' && langMap[opt.value]) {
      opt.textContent = t(langMap[opt.value]);
    }
  });

  const infoBox = transSection.querySelector('.info-box');
  infoBox.querySelector('h4').textContent = '💡 ' + t('transcriptionTip');
  infoBox.querySelector('p').textContent = t('transcriptionTipText');

  // Advanced Tab
  const advSection = document.getElementById('advanced');
  const advGroups = advSection.querySelectorAll('.setting-group');

  advGroups[0].querySelector('h3').textContent = t('keyboardBackend');
  advGroups[0].querySelector('.description').textContent = t('keyboardBackendDesc');
  advGroups[0].querySelector('.checkbox-label').textContent = t('forceYdotool');
  advGroups[0].querySelector('.hint').textContent = t('keyboardBackendHint');

  advGroups[1].querySelector('h3').textContent = t('typingDelay');
  advGroups[1].querySelector('.description').textContent = t('typingDelayDesc');
  advGroups[1].querySelector('.unit').textContent = t('seconds');

  // License Tab
  const licSection = document.getElementById('license');
  const actSection = document.getElementById('activation-section');
  if (actSection.style.display !== 'none') {
    actSection.querySelector('h3').textContent = t('activateLicense');
    actSection.querySelector('.description').textContent = t('activateLicenseDesc');
    document.getElementById('license_key').placeholder = t('licenseKeyPlaceholder');
    document.getElementById('activate_btn').textContent = t('activate');
  }

  const licInfoBox = licSection.querySelector('.info-box');
  licInfoBox.querySelector('h4').textContent = '🛒 ' + t('purchaseLicense');
  licInfoBox.querySelector('p').textContent = t('purchaseMessage');
  licInfoBox.querySelector('.btn-link').textContent = t('buyOnGumroad');

  // Footer
  document.getElementById('btn-cancel').textContent = t('cancel');
  document.getElementById('btn-save').textContent = t('save');
  document.getElementById('btn-save-restart').textContent = t('saveRestart');
}

module.exports = { translations, setLanguage, t, applyTranslations };
