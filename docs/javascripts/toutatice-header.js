// Bouton « Toutatice » dans le bandeau d'en-tête : accès à Pronote via l'ENT.
var TOUTATICE_URL = "https://www.toutatice.fr/portail";
var TOUTATICE_ICONE =
  '<svg viewBox="0 0 16 16" aria-hidden="true">' +
  '<rect width="16" height="16" rx="3" fill="#ffffff"/>' +
  '<rect x="1.5" y="1.5" width="2.6" height="13" fill="#78cbe0"/>' +
  '<rect x="4.1" y="1.5" width="2.6" height="13" fill="#f39224"/>' +
  '<rect x="6.7" y="1.5" width="2.6" height="13" fill="#bbd030"/>' +
  '<rect x="9.3" y="1.5" width="2.6" height="13" fill="#ffffff"/>' +
  '<rect x="11.9" y="1.5" width="2.6" height="13" fill="#e61649"/>' +
  '<rect x="0.5" y="0.5" width="15" height="15" rx="2.5" fill="none" stroke="rgba(13,27,42,0.25)"/>' +
  "</svg>";

document.addEventListener("DOMContentLoaded", function () {
  // Les liens Toutatice des menus s'ouvrent dans un nouvel onglet.
  document
    .querySelectorAll('a[href^="https://www.toutatice.fr"]')
    .forEach(function (link) {
      link.setAttribute("target", "_blank");
      link.setAttribute("rel", "noopener");
    });

  var header = document.querySelector(".md-header__inner");
  if (!header || header.querySelector(".toutatice-header-link")) {
    return;
  }
  var lien = document.createElement("a");
  lien.className = "toutatice-header-link";
  lien.href = TOUTATICE_URL;
  lien.target = "_blank";
  lien.rel = "noopener";
  lien.title = "Accéder à Pronote via Toutatice";
  lien.innerHTML = TOUTATICE_ICONE + "<span>Toutatice</span>";
  header.appendChild(lien);
});
