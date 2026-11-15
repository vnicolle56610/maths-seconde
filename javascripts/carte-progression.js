// Carte de progression : affichage agrandi qui garde les bulles cliquables
// (voir scripts/carte_progression.py). Délégation d'événements : rien à
// réinitialiser au changement de page.
(function () {
  function cadre() { return document.querySelector(".carte-progression-cadre"); }
  function ouvrir() {
    var c = cadre(); if (!c) return;
    c.classList.add("carte-ouverte");
    document.documentElement.style.overflow = "hidden";
    var f = c.querySelector(".carte-fermer"); if (f) f.focus();
  }
  function fermer() {
    var c = cadre(); if (!c || !c.classList.contains("carte-ouverte")) return;
    c.classList.remove("carte-ouverte");
    document.documentElement.style.overflow = "";
  }
  document.addEventListener("click", function (e) {
    if (e.target.closest(".carte-agrandir")) { ouvrir(); return; }
    if (e.target.closest(".carte-fermer")) { fermer(); return; }
    // clic sur le fond (hors de l'image) : fermer
    if (e.target.classList && e.target.classList.contains("carte-ouverte")) fermer();
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") fermer(); });
})();
