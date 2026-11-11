const { chromium } = require('playwright-core');
const fs = require('fs');
(async () => {
  const exe = process.env.HOME + '/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome';
  const browser = await chromium.launch({ executablePath: fs.existsSync(exe) ? exe : '/usr/bin/chromium' });
  const base = process.env.BASE || 'http://localhost:8765/automatismes/';
  const out = process.env.OUT || 'captures';
  for (const w of [320, 390]) {
    const m = await browser.newPage({ viewport: { width: w, height: 800 }, deviceScaleFactor: 2 });
    await m.goto(base + 'automatismes-N04-calcul-litteral/');
    await m.$$eval('details', ds => ds.forEach(d => d.open = true));
    await m.waitForTimeout(2500);
    console.log(`lecture ${w}px, tout ouvert : largeur ${await m.evaluate(() => document.documentElement.scrollWidth)}`);
    if (w === 390) await m.screenshot({ path: out + '/10_lecture_mobile_corriges.png', fullPage: true });
    // Flash : toutes les questions marquées « à revoir » => tous les corrigés affichés au bilan
    let pire = 0;
    for (let essai = 0; essai < 5; essai++) {
      await m.goto(base + 'qcm-N04-calcul-litteral/');
      await m.click('.qcm-mode >> nth=1');
      for (let i = 0; i < 6; i++) { await m.click('text=Voir la réponse'); await m.click('.qcm-auto-eval--faux'); }
      await m.waitForTimeout(1500);
      pire = Math.max(pire, await m.evaluate(() => document.documentElement.scrollWidth));
    }
    console.log(`flash ${w}px, 5 tirages : largeur max ${pire}`);
    await m.goto(base + 'qcm-N04-calcul-litteral/');
    await m.click('.qcm-mode >> nth=0');
    await m.click('.qcm-valider');
    await m.waitForTimeout(1500);
    console.log(`QCM ${w}px corrigé : largeur ${await m.evaluate(() => document.documentElement.scrollWidth)}`);
    await m.close();
  }
  await browser.close();
})();
