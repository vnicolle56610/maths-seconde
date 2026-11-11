// Vérifie toutes les pages « automatismes en ligne » d'un site construit et servi localement.
// Usage : BASE=http://localhost:8766/automatismes/ OUT=captures NODE_PATH=… node verifier_automatismes_site.js
// Contrôles : formules MathJax sans erreur, figures chargées, aucune largeur > écran
// à 320 et 390 px (corrigés ouverts), QCM : correction cohérente avec la banque,
// mode flash : déroulé complet. Code de sortie 1 si un contrôle échoue.
const { chromium } = require('playwright-core');
const fs = require('fs');
(async () => {
  const exe = process.env.HOME + '/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome';
  const browser = await chromium.launch({ executablePath: fs.existsSync(exe) ? exe : '/usr/bin/chromium' });
  const base = process.env.BASE || 'http://localhost:8766/automatismes/';
  const out = process.env.OUT || 'captures';
  fs.mkdirSync(out, { recursive: true });
  const echecs = [];
  const errs = [];

  const index = await browser.newPage();
  await index.goto(base);
  const lectures = await index.$$eval('a[href*="automatismes-N"]', as => [...new Set(as.map(a => a.getAttribute('href')))]);
  await index.close();
  console.log(`${lectures.length} pages de lecture trouvées dans l'index`);

  for (const href of lectures) {
    const slug = href.replace(/\/$/, '').split('/').pop();
    for (const w of [1280, 390, 320]) {
      const p = await browser.newPage({ viewport: { width: w, height: 900 }, deviceScaleFactor: w < 500 ? 2 : 1 });
      p.on('pageerror', e => errs.push(slug + ' : ' + e));
      await p.goto(new URL(href, base).href);
      await p.$$eval('details', ds => ds.forEach(d => d.open = true));
      await p.waitForFunction(() => document.querySelectorAll('.arithmatex').length === 0 ||
        document.querySelectorAll('mjx-container').length > 0, null, { timeout: 20000 });
      await p.waitForTimeout(1500);
      const r = await p.evaluate(() => ({
        merror: [...document.querySelectorAll('mjx-merror')].map(e => e.textContent),
        brutes: [...document.querySelectorAll('.arithmatex')].filter(s => !s.querySelector('mjx-container')).length,
        imgs: [...document.querySelectorAll('.auto-figure img')].map(i => i.complete && i.naturalWidth > 0),
        largeur: document.documentElement.scrollWidth,
        formules: document.querySelectorAll('mjx-container').length,
      }));
      if (w === 1280) console.log(`${slug} : ${r.formules} formules, ${r.imgs.length} image(s)`);
      if (r.merror.length) echecs.push(`${slug} : erreurs MathJax ${JSON.stringify(r.merror)}`);
      if (r.brutes) echecs.push(`${slug} : ${r.brutes} formule(s) non rendue(s)`);
      if (r.imgs.includes(false)) echecs.push(`${slug} : image non chargée`);
      if (r.largeur > w) echecs.push(`${slug} : largeur ${r.largeur} > ${w}px`);
      if (w === 1280 && /N03/.test(slug)) await p.screenshot({ path: `${out}/${slug}_1280.png`, fullPage: true });
      if (w === 390) await p.screenshot({ path: `${out}/${slug}_390.png`, fullPage: true });
      await p.close();
    }

    // Page QCM
    const qcmUrl = new URL(href.replace('automatismes-N', 'qcm-N'), base).href;
    const q = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
    q.on('pageerror', e => errs.push(slug + ' (QCM) : ' + e));
    await q.goto(qcmUrl);
    await q.waitForSelector('.qcm-mode');
    const banque = await q.evaluate(() => JSON.parse(document.getElementById('banque-automatismes').textContent));
    const nbQcm = banque.questions.filter(x => x.type === 'qcm').length;
    if (nbQcm) {
      await q.click('.qcm-mode >> nth=0');
      await q.waitForSelector('.qcm-option');
      const qs = await q.$$('li.qcm-question');
      for (let i = 0; i < qs.length; i++) { const o = await qs[i].$$('.qcm-option'); await o[i % o.length].click(); }
      await q.click('.qcm-valider');
      await q.waitForTimeout(1500);
      const v = await q.evaluate(() => ({
        score: document.querySelector('.qcm-score').textContent,
        justes: document.querySelectorAll('li.qcm-question--juste').length,
        coherent: [...document.querySelectorAll('li.qcm-question')].every(li => {
          const choisie = li.querySelector('.qcm-option--choisie');
          return li.querySelectorAll('.qcm-option--bonne').length === 1 &&
            (li.classList.contains('qcm-question--juste') === choisie.classList.contains('qcm-option--bonne'));
        }),
        merror: document.querySelectorAll('mjx-merror').length,
        largeur: document.documentElement.scrollWidth,
      }));
      if (!v.coherent || !v.score.startsWith(v.justes + ' /')) echecs.push(`${slug} QCM : correction incohérente (${v.score})`);
      if (v.merror) echecs.push(`${slug} QCM : erreurs MathJax`);
      if (v.largeur > 390) echecs.push(`${slug} QCM : largeur ${v.largeur}`);
      console.log(`  QCM ${nbQcm} questions : score ${v.score}, cohérent ${v.coherent}`);
      if (/N03/.test(slug)) await q.screenshot({ path: `${out}/${slug}_qcm.png`, fullPage: true });
      await q.click('text=Recommencer');
    }
    const nbFlash = banque.questions.filter(x => x.type === 'flash').length;
    if (nbFlash) {
      await q.click(`.qcm-mode >> nth=${nbQcm ? 1 : 0}`);
      const n = Math.min(6, nbFlash);
      for (let i = 0; i < n; i++) {
        if (i === 0 && /N03|N06-second-degre-ineq/.test(slug)) {
          await q.waitForTimeout(1200);
          await q.screenshot({ path: `${out}/${slug}_flash.png`, fullPage: true });
        }
        await q.click('text=Voir la réponse');
        await q.click('.qcm-auto-eval--faux');
      }
      await q.waitForTimeout(1500);
      const f = await q.evaluate(() => ({
        score: document.querySelector('.qcm-score').textContent,
        merror: document.querySelectorAll('mjx-merror').length,
        largeur: document.documentElement.scrollWidth,
      }));
      if (!f.score.startsWith('0 / ' + n)) echecs.push(`${slug} flash : score ${f.score}`);
      if (f.merror) echecs.push(`${slug} flash : erreurs MathJax`);
      if (f.largeur > 390) echecs.push(`${slug} flash : largeur ${f.largeur}`);
      console.log(`  flash ${n}/${nbFlash} : score ${f.score}`);
    }
    await q.close();
  }
  await browser.close();
  echecs.push(...errs.map(e => 'erreur JS : ' + e));
  console.log(echecs.length ? 'ÉCHECS :\n- ' + echecs.join('\n- ') : 'Tous les contrôles sont passés.');
  process.exit(echecs.length ? 1 : 0);
})();
