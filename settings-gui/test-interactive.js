/**
 * Interactive E2E Tests for Papagaio Settings GUI
 * Connects to Electron via Chrome DevTools Protocol
 */

const http = require('http');
const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');

const DEBUG_PORT = 9222;

async function getPages() {
  return new Promise((resolve, reject) => {
    http.get(`http://localhost:${DEBUG_PORT}/json`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(JSON.parse(data)));
    }).on('error', reject);
  });
}

async function connectToPage(wsUrl) {
  return new Promise((resolve) => {
    const ws = new WebSocket(wsUrl);
    let msgId = 1;
    const pending = new Map();

    ws.on('open', () => {
      const send = (method, params = {}) => {
        return new Promise((resolve) => {
          const id = msgId++;
          pending.set(id, resolve);
          ws.send(JSON.stringify({ id, method, params }));
        });
      };
      resolve({ ws, send });
    });

    ws.on('message', (data) => {
      const msg = JSON.parse(data);
      if (msg.id && pending.has(msg.id)) {
        pending.get(msg.id)(msg.result);
        pending.delete(msg.id);
      }
    });
  });
}

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function runTests() {
  console.log('\n🦜 Papagaio Settings GUI - Interactive E2E Tests\n');
  console.log('='.repeat(55));

  const pages = await getPages();
  const mainPage = pages.find(p => p.title.includes('Papagaio'));

  if (!mainPage) {
    console.log('❌ Could not find Papagaio window');
    process.exit(1);
  }

  console.log(`✅ Found window: "${mainPage.title}"`);

  const { ws, send } = await connectToPage(mainPage.webSocketDebuggerUrl);

  // Enable required domains
  await send('Runtime.enable');
  await send('DOM.enable');
  await send('Page.enable');

  let passed = 0;
  let failed = 0;

  async function test(name, fn) {
    try {
      await fn();
      console.log(`✅ ${name}`);
      passed++;
    } catch (error) {
      console.log(`❌ ${name}`);
      console.log(`   Error: ${error.message}`);
      failed++;
    }
  }

  async function evaluate(expression) {
    const result = await send('Runtime.evaluate', {
      expression,
      returnByValue: true,
      awaitPromise: true
    });
    if (result.exceptionDetails) {
      throw new Error(result.exceptionDetails.text);
    }
    return result.result.value;
  }

  async function click(selector) {
    await evaluate(`document.querySelector('${selector}').click()`);
    await sleep(300);
  }

  async function getValue(selector) {
    return evaluate(`document.querySelector('${selector}').value`);
  }

  async function getText(selector) {
    return evaluate(`document.querySelector('${selector}').textContent`);
  }

  async function isVisible(selector) {
    return evaluate(`
      const el = document.querySelector('${selector}');
      el && el.offsetParent !== null
    `);
  }

  async function screenshot(filename) {
    const result = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(filename, Buffer.from(result.data, 'base64'));
    console.log(`   📸 Screenshot: ${filename}`);
  }

  // Test 1: Window title shows correct language
  await test('Window title is in configured language', async () => {
    const title = await evaluate('document.title');
    if (!title.includes('Papagaio')) {
      throw new Error(`Unexpected title: ${title}`);
    }
  });

  // Test 2: General tab is active by default
  await test('General tab is active by default', async () => {
    const isActive = await evaluate(`
      document.querySelector('.tab[data-tab="general"]').classList.contains('active')
    `);
    if (!isActive) throw new Error('General tab not active');
  });

  // Take screenshot of General tab
  await screenshot('/tmp/papagaio-test-01-general.png');

  // Test 3: Click Audio tab
  await test('Click Audio tab', async () => {
    await click('.tab[data-tab="audio"]');
    const isActive = await evaluate(`
      document.querySelector('#audio').classList.contains('active')
    `);
    if (!isActive) throw new Error('Audio tab not active after click');
  });

  await screenshot('/tmp/papagaio-test-02-audio.png');

  // Test 4: Click Transcription tab
  await test('Click Transcription tab', async () => {
    await click('.tab[data-tab="transcription"]');
    const isActive = await evaluate(`
      document.querySelector('#transcription').classList.contains('active')
    `);
    if (!isActive) throw new Error('Transcription tab not active');
  });

  await screenshot('/tmp/papagaio-test-03-transcription.png');

  // Test 5: Click Advanced tab
  await test('Click Advanced tab', async () => {
    await click('.tab[data-tab="advanced"]');
    const isActive = await evaluate(`
      document.querySelector('#advanced').classList.contains('active')
    `);
    if (!isActive) throw new Error('Advanced tab not active');
  });

  await screenshot('/tmp/papagaio-test-04-advanced.png');

  // Test 6: Click License tab
  await test('Click License tab', async () => {
    await click('.tab[data-tab="license"]');
    const isActive = await evaluate(`
      document.querySelector('#license').classList.contains('active')
    `);
    if (!isActive) throw new Error('License tab not active');
  });

  await screenshot('/tmp/papagaio-test-05-license.png');

  // Test 7: Go back to General and test language switch
  await test('Switch language to English', async () => {
    await click('.tab[data-tab="general"]');
    await sleep(200);

    // Click English radio
    await evaluate(`document.querySelector('input[name="language"][value="en"]').click()`);
    await sleep(500);

    // Check if UI updated
    const saveBtn = await getText('#btn-save');
    if (saveBtn !== 'Save') {
      throw new Error(`Expected "Save", got "${saveBtn}"`);
    }
  });

  await screenshot('/tmp/papagaio-test-06-english.png');

  // Test 8: Switch language to Portuguese
  await test('Switch language to Portuguese', async () => {
    await evaluate(`document.querySelector('input[name="language"][value="pt"]').click()`);
    await sleep(500);

    const saveBtn = await getText('#btn-save');
    if (saveBtn !== 'Salvar') {
      throw new Error(`Expected "Salvar", got "${saveBtn}"`);
    }
  });

  await screenshot('/tmp/papagaio-test-07-portuguese.png');

  // Test 9: Quality selector works
  await test('Quality selector - select Fast', async () => {
    await evaluate(`document.querySelector('input[name="model"][value="tiny"]').click()`);
    await sleep(200);
    const isChecked = await evaluate(`document.querySelector('input[name="model"][value="tiny"]').checked`);
    if (!isChecked) throw new Error('Fast quality not selected');
  });

  // Test 10: Quality selector - select High (recommended)
  await test('Quality selector - select High (recommended)', async () => {
    await evaluate(`document.querySelector('input[name="model"][value="small"]').click()`);
    await sleep(200);
    const isChecked = await evaluate(`document.querySelector('input[name="model"][value="small"]').checked`);
    if (!isChecked) throw new Error('High quality not selected');
  });

  // Test 11: Hotkey input works
  await test('Hotkey input accepts text', async () => {
    await evaluate(`document.getElementById('hotkey').value = '<ctrl>+<alt>+t'`);
    const value = await getValue('#hotkey');
    if (value !== '<ctrl>+<alt>+t') {
      throw new Error(`Expected hotkey value, got "${value}"`);
    }
  });

  // Test 12: Hotkey preset button works
  await test('Hotkey preset button works', async () => {
    await click('.preset-btn[data-hotkey="<super>+v"]');
    const value = await getValue('#hotkey');
    if (value !== '<super>+v') {
      throw new Error(`Expected "<super>+v", got "${value}"`);
    }
  });

  // Test 13: Audio - Silence threshold slider
  await test('Silence threshold slider exists and has value', async () => {
    await click('.tab[data-tab="audio"]');
    await sleep(200);
    const value = await getValue('#silence_threshold');
    if (!value || isNaN(parseInt(value))) {
      throw new Error(`Invalid threshold value: ${value}`);
    }
  });

  // Test 14: Transcription language dropdown
  await test('Transcription language dropdown works', async () => {
    await click('.tab[data-tab="transcription"]');
    await sleep(200);

    await evaluate(`document.getElementById('transcription_language').value = 'pt'`);
    const value = await getValue('#transcription_language');
    if (value !== 'pt') {
      throw new Error(`Expected "pt", got "${value}"`);
    }
  });

  // Test 15: Daemon status element exists
  await test('Daemon status indicator exists', async () => {
    const statusText = await getText('.status-text');
    const validStatuses = ['Running', 'Stopped', 'Executando', 'Parado', 'Checking...', 'Verificando...'];
    if (!validStatuses.some(s => statusText.includes(s))) {
      throw new Error(`Unexpected status: "${statusText}"`);
    }
  });

  // Final screenshot
  await click('.tab[data-tab="general"]');
  await sleep(200);
  await screenshot('/tmp/papagaio-test-08-final.png');

  ws.close();

  console.log('='.repeat(55));
  console.log(`\n📊 Results: ${passed} passed, ${failed} failed`);
  console.log(`📸 Screenshots saved to /tmp/papagaio-test-*.png\n`);

  process.exit(failed > 0 ? 1 : 0);
}

runTests().catch(err => {
  console.error('Test failed:', err);
  process.exit(1);
});
