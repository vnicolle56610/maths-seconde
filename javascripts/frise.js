/* Mini-frise des repères historiques.
   Dans la page (dans l'encadré « historique »), un paragraphe texte suivi de :
     {: .frise data-annee="820" }            (une date)
     {: .frise data-annee="-1800" data-fin="-1600" }   (une période)
     {: .frise data-annee="150" data-etiquette="IIe s." }  (date approximative)
   Le texte reste lisible sans JavaScript ; le script ajoute la frise au-dessus.
   Les périodes ont toutes la même largeur : la position est linéaire à
   l'intérieur de chaque période seulement. */
(function () {
  var PERIODES = [
    { nom: "Antiquité", debut: -3000, fin: 500 },
    { nom: "Moyen Âge", debut: 500, fin: 1450 },
    { nom: "Renaissance", debut: 1450, fin: 1600 },
    { nom: "XVIIe–XVIIIe", debut: 1600, fin: 1800 },
    { nom: "XIXe", debut: 1800, fin: 1900 },
    { nom: "XXe–XXIe", debut: 1900, fin: 2030 }
  ];

  function position(annee) {
    var n = PERIODES.length;
    for (var i = 0; i < n; i++) {
      var p = PERIODES[i];
      if (annee < p.fin || i === n - 1) {
        var f = (annee - p.debut) / (p.fin - p.debut);
        f = Math.max(0, Math.min(1, f));
        return ((i + f) / n) * 100;
      }
    }
    return 100;
  }

  function formater(annee) {
    return annee < 0 ? "−" + Math.abs(annee) : String(annee);
  }

  function construire(el) {
    if (el.dataset.friseFaite) return;
    var annee = parseInt(el.dataset.annee, 10);
    if (isNaN(annee)) return;
    var fin = parseInt(el.dataset.fin, 10);
    el.dataset.friseFaite = "1";

    var frise = document.createElement("div");
    frise.className = "frise-barre";
    frise.setAttribute("aria-hidden", "true");

    var actif = position(annee);
    PERIODES.forEach(function (p, i) {
      var seg = document.createElement("span");
      seg.className = "frise-periode";
      var a = position(p.debut), b = position(p.fin);
      if (i === PERIODES.length - 1) b = 100;
      if (actif >= a && actif <= b) seg.className += " frise-periode--active";
      seg.textContent = p.nom;
      frise.appendChild(seg);
    });

    var x = position(annee);
    if (!isNaN(fin)) {
      var plage = document.createElement("span");
      plage.className = "frise-plage";
      plage.style.left = x + "%";
      plage.style.width = Math.max(position(fin) - x, 0.8) + "%";
      frise.appendChild(plage);
      x = (x + position(fin)) / 2;
    }
    var point = document.createElement("span");
    point.className = "frise-point";
    point.style.left = x + "%";
    var etiquette = document.createElement("span");
    etiquette.className = "frise-annee";
    etiquette.textContent = el.dataset.etiquette ||
      (isNaN(fin) ? formater(annee) : formater(annee) + "–" + formater(fin));
    if (x < 15) etiquette.className += " frise-annee--gauche";
    if (x > 85) etiquette.className += " frise-annee--droite";
    point.appendChild(etiquette);
    frise.appendChild(point);

    el.parentNode.insertBefore(frise, el);
  }

  function initialiser() {
    document.querySelectorAll(".frise").forEach(construire);
  }

  if (window.document$ && window.document$.subscribe) {
    window.document$.subscribe(initialiser);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialiser);
  } else {
    initialiser();
  }
})();
