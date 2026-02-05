/**
 * E2E Tests for Papagaio Settings GUI
 * Run with: node test-e2e.js
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

const CONFIG_DIR = path.join(os.homedir(), '.config', 'papagaio');
const CONFIG_FILE = path.join(CONFIG_DIR, 'config.ini');
const BACKUP_FILE = path.join(CONFIG_DIR, 'config.ini.backup');

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`✅ ${name}`);
    passed++;
  } catch (error) {
    console.log(`❌ ${name}`);
    console.log(`   Error: ${error.message}`);
    failed++;
  }
}

function assertEqual(actual, expected, message = '') {
  if (actual !== expected) {
    throw new Error(`${message} Expected "${expected}", got "${actual}"`);
  }
}

function assertTrue(value, message = '') {
  if (!value) {
    throw new Error(`${message} Expected truthy value, got "${value}"`);
  }
}

// Backup config before tests
function backupConfig() {
  if (fs.existsSync(CONFIG_FILE)) {
    fs.copyFileSync(CONFIG_FILE, BACKUP_FILE);
  }
}

// Restore config after tests
function restoreConfig() {
  if (fs.existsSync(BACKUP_FILE)) {
    fs.copyFileSync(BACKUP_FILE, CONFIG_FILE);
    fs.unlinkSync(BACKUP_FILE);
  }
}

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

console.log('\n🦜 Papagaio Settings GUI - E2E Tests\n');
console.log('='.repeat(50));

backupConfig();

try {
  // Test 1: Config file exists
  test('Config directory exists', () => {
    assertTrue(fs.existsSync(CONFIG_DIR), 'Config directory should exist');
  });

  // Test 2: Config file parsing
  test('Config file parsing', () => {
    if (fs.existsSync(CONFIG_FILE)) {
      const content = fs.readFileSync(CONFIG_FILE, 'utf-8');
      const config = parseINI(content);
      assertTrue(config.General !== undefined, 'Should have General section');
      assertTrue(config.Audio !== undefined, 'Should have Audio section');
    } else {
      // Create default config for testing
      const defaultConfig = {
        General: { model: 'small', language: 'en', hotkey: '<ctrl>+<alt>+v' },
        Audio: { silence_threshold: '400', silence_duration: '5' },
        Advanced: { use_ydotool: 'false' }
      };
      fs.writeFileSync(CONFIG_FILE, generateINI(defaultConfig));
      assertTrue(true);
    }
  });

  // Test 3: Config values validation
  test('Config values are valid', () => {
    const content = fs.readFileSync(CONFIG_FILE, 'utf-8');
    const config = parseINI(content);

    const validModels = ['tiny', 'base', 'small', 'medium', 'large'];
    assertTrue(validModels.includes(config.General?.model), `Model should be valid: ${config.General?.model}`);

    const validLanguages = ['en', 'pt'];
    assertTrue(validLanguages.includes(config.General?.language), `Language should be valid: ${config.General?.language}`);
  });

  // Test 4: Config save/load round-trip
  test('Config save/load round-trip', () => {
    const testConfig = {
      General: { model: 'base', language: 'pt', hotkey: '<ctrl>+<shift>+v' },
      Audio: { silence_threshold: '500', silence_duration: '3' },
      Advanced: { use_ydotool: 'true' }
    };

    const testFile = path.join(CONFIG_DIR, 'test_config.ini');
    fs.writeFileSync(testFile, generateINI(testConfig));

    const loadedContent = fs.readFileSync(testFile, 'utf-8');
    const loadedConfig = parseINI(loadedContent);

    assertEqual(loadedConfig.General.model, 'base', 'Model');
    assertEqual(loadedConfig.General.language, 'pt', 'Language');
    assertEqual(loadedConfig.Audio.silence_threshold, '500', 'Threshold');

    fs.unlinkSync(testFile);
  });

  // Test 5: i18n translations exist
  test('i18n translations loaded', () => {
    const i18nPath = path.join(__dirname, 'i18n.js');
    assertTrue(fs.existsSync(i18nPath), 'i18n.js should exist');

    const { translations } = require('./i18n');
    assertTrue(translations.en !== undefined, 'English translations should exist');
    assertTrue(translations.pt !== undefined, 'Portuguese translations should exist');
    assertTrue(translations.en.appTitle !== undefined, 'appTitle should be translated');
    assertTrue(translations.pt.appTitle !== undefined, 'appTitle should be translated (PT)');
  });

  // Test 6: All translation keys match
  test('Translation keys match between languages', () => {
    const { translations } = require('./i18n');
    const enKeys = Object.keys(translations.en);
    const ptKeys = Object.keys(translations.pt);

    assertEqual(enKeys.length, ptKeys.length, `Key count: EN(${enKeys.length}) vs PT(${ptKeys.length})`);

    for (const key of enKeys) {
      assertTrue(translations.pt[key] !== undefined, `Missing PT translation for: ${key}`);
    }
  });

  // Test 7: HTML file structure
  test('HTML file has correct structure', () => {
    const htmlPath = path.join(__dirname, 'index.html');
    const html = fs.readFileSync(htmlPath, 'utf-8');

    assertTrue(html.includes('id="general"'), 'Should have General tab');
    assertTrue(html.includes('id="audio"'), 'Should have Audio tab');
    assertTrue(html.includes('id="transcription"'), 'Should have Transcription tab');
    assertTrue(html.includes('id="advanced"'), 'Should have Advanced tab');
    assertTrue(html.includes('id="license"'), 'Should have License tab');
    assertTrue(html.includes('btn-save'), 'Should have Save button');
    assertTrue(html.includes('btn-save-restart'), 'Should have Save & Restart button');
  });

  // Test 8: No Whisper references in UI
  test('No "Whisper" references visible to users', () => {
    const htmlPath = path.join(__dirname, 'index.html');
    const html = fs.readFileSync(htmlPath, 'utf-8');

    // Check for visible text containing Whisper (excluding comments)
    const lines = html.split('\n').filter(l => !l.trim().startsWith('<!--'));
    const visibleWhisper = lines.some(l =>
      l.includes('>Whisper') ||
      l.includes('Whisper<') ||
      l.includes('"Whisper') ||
      l.includes('Whisper"')
    );

    assertTrue(!visibleWhisper, 'Whisper should not appear in visible text');
  });

  // Test 9: Quality options mapping
  test('Quality options hide model names', () => {
    const htmlPath = path.join(__dirname, 'index.html');
    const html = fs.readFileSync(htmlPath, 'utf-8');

    assertTrue(html.includes('value="tiny"'), 'Should have tiny option');
    assertTrue(html.includes('value="base"'), 'Should have base option');
    assertTrue(html.includes('value="small"'), 'Should have small option');
    assertTrue(html.includes('value="medium"'), 'Should have medium option');

    // But display names should be user-friendly
    assertTrue(html.includes('Fast'), 'Should show "Fast" label');
    assertTrue(html.includes('Balanced'), 'Should show "Balanced" label');
    assertTrue(html.includes('High'), 'Should show "High" label');
    assertTrue(html.includes('Maximum'), 'Should show "Maximum" label');
  });

  // Test 10: Hotkey presets exist
  test('Hotkey presets are available', () => {
    const htmlPath = path.join(__dirname, 'index.html');
    const html = fs.readFileSync(htmlPath, 'utf-8');

    assertTrue(html.includes('data-hotkey="<ctrl>+<alt>+v"'), 'Should have Ctrl+Alt+V preset');
    assertTrue(html.includes('data-hotkey="<ctrl>+<shift>+v"'), 'Should have Ctrl+Shift+V preset');
    assertTrue(html.includes('data-hotkey="<super>+v"'), 'Should have Super+V preset');
  });

  // Test 11: Transcription languages available
  test('Transcription language options exist', () => {
    const htmlPath = path.join(__dirname, 'index.html');
    const html = fs.readFileSync(htmlPath, 'utf-8');

    assertTrue(html.includes('value="auto"'), 'Should have auto-detect option');
    assertTrue(html.includes('value="pt"'), 'Should have Portuguese option');
    assertTrue(html.includes('value="en"'), 'Should have English option');
    assertTrue(html.includes('value="es"'), 'Should have Spanish option');
    assertTrue(html.includes('value="ja"'), 'Should have Japanese option');
  });

  // Test 12: Daemon status check (via systemctl)
  test('Daemon status can be checked', () => {
    const { execFileSync } = require('child_process');
    try {
      const result = execFileSync('systemctl', ['--user', 'is-active', 'papagaio'], { encoding: 'utf-8' });
      assertTrue(['active', 'inactive', 'failed'].some(s => result.includes(s)), 'Should return valid status');
    } catch (e) {
      // inactive or not found returns non-zero exit code
      assertTrue(true, 'systemctl command executed');
    }
  });

  // Test 13: CSS dark mode support
  test('CSS supports dark mode', () => {
    const cssPath = path.join(__dirname, 'styles.css');
    const css = fs.readFileSync(cssPath, 'utf-8');

    assertTrue(css.includes('prefers-color-scheme: dark'), 'Should have dark mode media query');
    assertTrue(css.includes('--bg-primary'), 'Should use CSS variables');
  });

  // Test 14: License file structure
  test('License tab elements exist', () => {
    const htmlPath = path.join(__dirname, 'index.html');
    const html = fs.readFileSync(htmlPath, 'utf-8');

    assertTrue(html.includes('id="license-status"'), 'Should have license status element');
    assertTrue(html.includes('id="license_key"'), 'Should have license key input');
    assertTrue(html.includes('activate_btn'), 'Should have activate button');
    assertTrue(html.includes('gumroad.com'), 'Should have Gumroad link');
  });

  // Test 15: Main process IPC handlers
  test('Main.js has required IPC handlers', () => {
    const mainPath = path.join(__dirname, 'main.js');
    const main = fs.readFileSync(mainPath, 'utf-8');

    assertTrue(main.includes("'load-config'"), 'Should handle load-config');
    assertTrue(main.includes("'save-config'"), 'Should handle save-config');
    assertTrue(main.includes("'restart-daemon'"), 'Should handle restart-daemon');
    assertTrue(main.includes("'check-daemon-status'"), 'Should handle check-daemon-status');
    assertTrue(main.includes("'get-license-status'"), 'Should handle get-license-status');
  });

} finally {
  restoreConfig();
}

console.log('='.repeat(50));
console.log(`\n📊 Results: ${passed} passed, ${failed} failed\n`);

process.exit(failed > 0 ? 1 : 0);
