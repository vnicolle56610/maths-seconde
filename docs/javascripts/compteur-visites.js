// Compteur de visites affiché dans le pied de page (données GoatCounter).
document.addEventListener("DOMContentLoaded", function () {
  var pied = document.querySelector(".md-footer-meta__inner");
  if (!pied || pied.querySelector(".compteur-visites")) {
    return;
  }
  fetch("https://maths-vnicolle.goatcounter.com/counter/TOTAL.json")
    .then(function (reponse) {
      if (!reponse.ok) {
        throw new Error("compteur indisponible");
      }
      return reponse.json();
    })
    .then(function (donnees) {
      var total = Number(String(donnees.count).replace(/[^0-9]/g, ""));
      if (!total) {
        return;
      }
      var zone = document.createElement("div");
      zone.className = "compteur-visites";
      zone.textContent =
        "👥 " + total.toLocaleString("fr-FR") + " visites";
      pied.appendChild(zone);
    })
    .catch(function () {
      // API injoignable (réglage désactivé, bloqueur…) : pas de compteur,
      // le site reste intact.
    });
});
