const { chromium } = require('playwright-core');
const fs = require('fs');
(async () => {
  const exe = process.env.HOME + '/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome';
  const browser = await chromium.launch({ executablePath: fs.existsSync(exe) ? exe : '/usr/bin/chromium' });
  const errs = [];
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  page.on('pageerror', e => errs.push(String(e)));
  const base = process.env.BASE || 'http://localhost:8765/automatismes/';
  await page.goto(base + 'automatismes-N04-calcul-litteral/');
  await page.waitForFunction(() => document.querySelectorAll('mjx-container').length > 20, null, { timeout: 20000 });
  console.log('formules rendues (lecture) :', await page.$$eval('mjx-container', x => x.length));
  console.log('erreurs MathJax :', await page.$$eval('mjx-merror', x => x.map(e => e.textContent)));
  await page.screenshot({ path: (process.env.OUT||'captures')+'/1_lecture_haut.png' });
  const details = await page.$$('details.success');
  await details[2].evaluate(d => d.open = true);
  await details[3].evaluate(d => d.open = true);
  await page.waitForTimeout(800);
  await page.screenshot({ path: (process.env.OUT||'captures')+'/2_lecture_pleine.png', fullPage: true });

  await page.goto(base + 'qcm-N04-calcul-litteral/');
  await page.waitForSelector('.qcm-mode');
  await page.screenshot({ path: (process.env.OUT||'captures')+'/3_qcm_accueil.png' });
  await page.click('.qcm-mode >> nth=0');
  await page.waitForFunction(() => document.querySelectorAll('.qcm-option mjx-container').length >= 20, null, { timeout: 15000 });
  const qs = await page.$$('.qcm-question');
  for (let i = 0; i < qs.length; i++) { const opts = await qs[i].$$('.qcm-option'); await opts[i % 2].click(); }
  await page.screenshot({ path: (process.env.OUT||'captures')+'/4_qcm_en_cours.png' });
  // Score attendu calculé indépendamment depuis la banque et les choix cliqués
  await page.click('.qcm-valider');
  await page.waitForTimeout(1200);
  console.log('score affiché :', await page.textContent('.qcm-score'));
  const verif = await page.evaluate(() => [...document.querySelectorAll('.qcm-question')].map(li => {
    const bonne = li.querySelectorAll('.qcm-option--bonne').length;
    const choisie = li.querySelector('.qcm-option--choisie');
    const juste = li.classList.contains('qcm-question--juste');
    const coherent = juste ? choisie.classList.contains('qcm-option--bonne') : !choisie.classList.contains('qcm-option--bonne');
    return bonne === 1 && coherent ? 'ok' : 'INCOHERENT';
  }));
  console.log('cohérence correction :', verif.join(','));
  await page.screenshot({ path: (process.env.OUT||'captures')+'/5_qcm_corrige.png', fullPage: true });

  const m = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
  m.on('pageerror', e => errs.push(String(e)));
  await m.goto(base + 'qcm-N04-calcul-litteral/');
  await m.waitForSelector('.qcm-mode');
  await m.click('.qcm-mode >> nth=1');
  await m.waitForTimeout(1500);
  await m.screenshot({ path: (process.env.OUT||'captures')+'/6_flash_mobile_question.png' });
  for (let i = 0; i < 6; i++) {
    await m.click('text=Voir la réponse');
    await m.waitForTimeout(400);
    if (i === 0) await m.screenshot({ path: (process.env.OUT||'captures')+'/7_flash_mobile_reponse.png' });
    await m.click(i % 3 === 0 ? '.qcm-auto-eval--faux' : '.qcm-auto-eval--juste');
  }
  await m.waitForTimeout(1200);
  console.log('score flash :', await m.textContent('.qcm-score'));
  await m.screenshot({ path: (process.env.OUT||'captures')+'/8_flash_mobile_bilan.png', fullPage: true });
  console.log('largeur QCM mobile :', await m.evaluate(() => document.documentElement.scrollWidth));
  await m.goto(base + 'automatismes-N04-calcul-litteral/');
  await m.waitForTimeout(2500);
  await m.screenshot({ path: (process.env.OUT||'captures')+'/9_lecture_mobile.png' });
  console.log('largeur lecture mobile :', await m.evaluate(() => document.documentElement.scrollWidth));
  console.log('erreurs console :', errs);
  await browser.close();
})();
