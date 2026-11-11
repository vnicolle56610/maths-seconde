// QCM interactif d'automatismes — JavaScript pur, sans serveur.
// La banque de questions est embarquée dans la page (balise <script type="application/json">),
// générée automatiquement depuis la source LaTeX. Rien n'est envoyé : seul le meilleur
// score est mémorisé dans le navigateur (si le stockage local est disponible).
(function () {
  "use strict";

  var LETTRES = ["A", "B", "C", "D"];

  function el(tag, classe, html) {
    var n = document.createElement(tag);
    if (classe) n.className = classe;
    if (html !== undefined) n.innerHTML = html;
    return n;
  }

  function melanger(t) {
    var a = t.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var x = a[i]; a[i] = a[j]; a[j] = x;
    }
    return a;
  }

  function typeset(noeud) {
    if (window.MathJax && MathJax.typesetPromise) {
      MathJax.typesetPromise([noeud]).catch(function () {});
    }
  }

  function minutes(duree) {
    var m = /(\d+)\s*min/.exec(duree || "");
    return m ? parseInt(m[1], 10) : 0;
  }

  function formatTemps(s) {
    var m = Math.floor(s / 60), r = s % 60;
    return m + ":" + (r < 10 ? "0" : "") + r;
  }

  function lireRecord(cle) {
    try { return JSON.parse(localStorage.getItem(cle) || "null"); } catch (e) { return null; }
  }
  function ecrireRecord(cle, valeur) {
    try { localStorage.setItem(cle, JSON.stringify(valeur)); } catch (e) { /* stockage indisponible */ }
  }

  // ------------------------------------------------------------------ Chronomètre
  function Chrono(zone, limite, finAuto) {
    var debut = Date.now(), id = null, self = this;
    this.ecoule = function () { return Math.round((Date.now() - debut) / 1000); };
    function tic() {
      var e = self.ecoule();
      if (limite) {
        var reste = Math.max(0, limite - e);
        zone.textContent = "⏱ " + formatTemps(reste);
        zone.classList.toggle("qcm-chrono--urgent", reste <= 30);
        if (reste === 0) { self.stop(); finAuto(); }
      } else {
        zone.textContent = "⏱ " + formatTemps(e);
      }
    }
    this.stop = function () { if (id) { clearInterval(id); id = null; } };
    tic();
    id = setInterval(tic, 1000);
  }

  // ------------------------------------------------------------------ Application
  function Application(racine, banque) {
    this.racine = racine;
    this.banque = banque;
    this.cle = "automatismes-" + banque.niveau + "-" + (banque.cle || banque.notion);
    this.accueil();
  }

  Application.prototype.vider = function () {
    if (this.chrono) this.chrono.stop();
    this.racine.innerHTML = "";
  };

  Application.prototype.accueil = function () {
    var self = this, b = this.banque;
    this.vider();
    var qcm = b.questions.filter(function (q) { return q.type === "qcm"; });
    var flash = b.questions.filter(function (q) { return q.type === "flash"; });
    var serieQcm = b.series.filter(function (s) { return s.qcm; })[0];
    var record = lireRecord(this.cle) || {};

    var carte = el("div", "qcm-carte");
    carte.appendChild(el("h2", "qcm-titre", "Choisir un entraînement"));
    var grille = el("div", "qcm-modes");

    if (qcm.length) {
      var m1 = el("button", "qcm-mode");
      m1.type = "button";
      m1.innerHTML = "<strong>QCM chronométré</strong>" +
        "<span>" + qcm.length + " questions · " + (serieQcm && serieQcm.duree ? serieQcm.duree : "sans limite") +
        " · une seule bonne réponse</span>" +
        (record.qcm ? "<em>Meilleur score : " + record.qcm + "/" + qcm.length + "</em>" : "");
      m1.addEventListener("click", function () { self.lancerQcm(qcm, minutes(serieQcm && serieQcm.duree) * 60); });
      grille.appendChild(m1);
    }
    if (flash.length) {
      var m2 = el("button", "qcm-mode");
      m2.type = "button";
      var nb = Math.min(6, flash.length);
      m2.innerHTML = "<strong>Questions flash</strong>" +
        "<span>" + nb + " questions tirées au hasard parmi " + flash.length +
        " · réponse à trouver de tête, puis auto-correction</span>" +
        (record.flash ? "<em>Meilleur score : " + record.flash + "/" + nb + "</em>" : "");
      m2.addEventListener("click", function () { self.lancerFlash(melanger(flash).slice(0, nb)); });
      grille.appendChild(m2);
    }
    carte.appendChild(grille);
    carte.appendChild(el("p", "qcm-note",
      "Sans calculatrice. Un brouillon est autorisé ; les réponses ne sont envoyées nulle part."));
    this.racine.appendChild(carte);
  };

  Application.prototype.serie = function (q) {
    return this.banque.series.filter(function (x) { return x.lettre === q.serie; })[0] || {};
  };

  Application.prototype.consigne = function (q) {
    return this.serie(q).consigne || "";
  };

  // Figure de la série (repliable en mode QCM, affichée en mode flash) et
  // questions précédentes dont dépend l'énoncé.
  Application.prototype.supports = function (q, replier) {
    var frag = document.createDocumentFragment();
    var figure = this.serie(q).figure;
    if (figure) {
      if (replier) {
        var d = el("details", "qcm-figure");
        d.appendChild(el("summary", "", "Voir la figure"));
        d.appendChild(el("div", "", figure));
        frag.appendChild(d);
      } else {
        frag.appendChild(el("div", "qcm-figure", figure));
      }
    }
    if (q.contexte && q.contexte.length) {
      frag.appendChild(el("div", "qcm-contexte",
        "<strong>Dans la même série :</strong> " + q.contexte.join(" ")));
    }
    return frag;
  };

  // ---------------------------------------------------------------- Mode QCM
  Application.prototype.lancerQcm = function (questions, limite) {
    var self = this;
    this.vider();
    var tirage = melanger(questions).map(function (q) {
      var ordre = melanger([0, 1, 2, 3].slice(0, q.choix.length));
      return { q: q, ordre: ordre, choisi: null };
    });

    var barre = el("div", "qcm-barre");
    var progression = el("span", "qcm-progression");
    var chronoZone = el("span", "qcm-chrono");
    barre.appendChild(progression);
    barre.appendChild(chronoZone);
    this.racine.appendChild(barre);

    var liste = el("ol", "qcm-liste");
    tirage.forEach(function (t, i) {
      var li = el("li", "qcm-question");
      li.appendChild(self.supports(t.q, true));
      li.appendChild(el("div", "qcm-enonce", t.q.enonce));
      var choix = el("div", "qcm-choix");
      t.ordre.forEach(function (k, pos) {
        var b = el("button", "qcm-option",
          '<span class="qcm-lettre">' + LETTRES[pos] + "</span><span>" + t.q.choix[k] + "</span>");
        b.type = "button";
        b.setAttribute("aria-pressed", "false");
        b.addEventListener("click", function () {
          if (self.termine) return;
          t.choisi = k;
          Array.prototype.forEach.call(choix.children, function (c) {
            c.classList.remove("qcm-option--choisie");
            c.setAttribute("aria-pressed", "false");
          });
          b.classList.add("qcm-option--choisie");
          b.setAttribute("aria-pressed", "true");
          majProgression();
        });
        choix.appendChild(b);
      });
      li.appendChild(choix);
      li.appendChild(el("div", "qcm-retour"));
      t.noeud = li;
      liste.appendChild(li);
    });
    this.racine.appendChild(liste);

    var valider = el("button", "md-button md-button--primary qcm-valider", "Valider mes réponses");
    valider.type = "button";
    this.racine.appendChild(valider);

    function majProgression() {
      var n = tirage.filter(function (t) { return t.choisi !== null; }).length;
      progression.textContent = n + " / " + tirage.length + " répondues";
    }
    majProgression();

    this.termine = false;
    function corriger() {
      if (self.termine) return;
      self.termine = true;
      self.chrono.stop();
      var score = 0;
      tirage.forEach(function (t) {
        var juste = t.choisi === t.q.bonne;
        if (juste) score++;
        t.noeud.classList.add(juste ? "qcm-question--juste" : "qcm-question--faux");
        Array.prototype.forEach.call(t.noeud.querySelectorAll(".qcm-option"), function (b, pos) {
          b.disabled = true;
          if (t.ordre[pos] === t.q.bonne) b.classList.add("qcm-option--bonne");
          else if (t.ordre[pos] === t.choisi) b.classList.add("qcm-option--fausse");
        });
        var posBonne = t.ordre.indexOf(t.q.bonne);
        var entete = juste ? "✔ Bonne réponse" :
          (t.choisi === null ? "✘ Sans réponse" : "✘ Réponse incorrecte") +
          " — la bonne réponse était " + LETTRES[posBonne];
        t.noeud.querySelector(".qcm-retour").innerHTML =
          "<strong>" + entete + ".</strong> " + t.q.corrige;
      });
      valider.remove();
      self.bilan(score, tirage.length, "qcm", self.chrono.ecoule());
      typeset(self.racine);
    }
    valider.addEventListener("click", corriger);
    this.chrono = new Chrono(chronoZone, limite, corriger);
    typeset(this.racine);
  };

  // ---------------------------------------------------------------- Mode flash
  Application.prototype.lancerFlash = function (questions) {
    var self = this, i = 0, resultats = [];
    this.vider();
    var barre = el("div", "qcm-barre");
    var progression = el("span", "qcm-progression");
    var chronoZone = el("span", "qcm-chrono");
    barre.appendChild(progression);
    barre.appendChild(chronoZone);
    this.racine.appendChild(barre);
    var zone = el("div", "qcm-flash");
    this.racine.appendChild(zone);
    this.chrono = new Chrono(chronoZone, 0, function () {});

    function afficher() {
      var q = questions[i];
      progression.textContent = "Question " + (i + 1) + " / " + questions.length;
      zone.innerHTML = "";
      var carte = el("div", "qcm-question");
      carte.appendChild(el("div", "qcm-consigne", self.consigne(q)));
      carte.appendChild(self.supports(q, false));
      carte.appendChild(el("div", "qcm-enonce qcm-enonce--grand", q.enonce));
      var voir = el("button", "md-button md-button--primary", "Voir la réponse");
      voir.type = "button";
      carte.appendChild(voir);
      voir.addEventListener("click", function () {
        voir.remove();
        carte.appendChild(el("div", "qcm-retour qcm-retour--visible", q.corrige));
        var auto = el("div", "qcm-auto-eval");
        auto.appendChild(el("span", "", "J'avais trouvé :"));
        [["juste", "✔ juste"], ["faux", "✘ à revoir"]].forEach(function (c) {
          var b = el("button", "md-button qcm-auto-eval--" + c[0], c[1]);
          b.type = "button";
          b.addEventListener("click", function () {
            resultats.push({ q: q, juste: c[0] === "juste" });
            i++;
            if (i < questions.length) afficher(); else fin();
          });
          auto.appendChild(b);
        });
        carte.appendChild(auto);
        typeset(carte);
      });
      zone.appendChild(carte);
      typeset(carte);
    }

    function fin() {
      self.chrono.stop();
      zone.innerHTML = "";
      var score = resultats.filter(function (r) { return r.juste; }).length;
      var aRevoir = resultats.filter(function (r) { return !r.juste; });
      if (aRevoir.length) {
        var bloc = el("div", "qcm-a-revoir");
        bloc.appendChild(el("h3", "", "À revoir"));
        aRevoir.forEach(function (r) {
          var d = el("div", "qcm-question qcm-question--faux");
          d.appendChild(self.supports(r.q, true));
          d.appendChild(el("div", "qcm-enonce", r.q.enonce));
          d.appendChild(el("div", "qcm-retour qcm-retour--visible", r.q.corrige));
          if (r.q.methode) d.appendChild(el("div", "qcm-methode", "<strong>Méthode.</strong> " + r.q.methode));
          bloc.appendChild(d);
        });
        zone.appendChild(bloc);
      }
      self.bilan(score, resultats.length, "flash", self.chrono.ecoule());
      typeset(self.racine);
    }
    afficher();
  };

  // ---------------------------------------------------------------- Bilan
  Application.prototype.bilan = function (score, total, mode, secondes) {
    var self = this;
    var record = lireRecord(this.cle) || {};
    var nouveau = !record[mode] || score > record[mode];
    if (nouveau) { record[mode] = score; ecrireRecord(this.cle, record); }
    var message = score === total ? "Parfait !" :
      score >= total * 0.66 ? "Bien joué, encore un petit effort." :
      "Relis les corrigés puis recommence : les automatismes viennent avec la répétition.";
    var b = el("div", "qcm-bilan");
    b.innerHTML = '<p class="qcm-score">' + score + " / " + total + "</p>" +
      "<p>" + message + "</p>" +
      "<p class=\"qcm-note\">Temps : " + formatTemps(secondes) +
      (nouveau && score > 0 ? " · nouveau meilleur score" : "") + "</p>";
    var rejouer = el("button", "md-button md-button--primary", "Recommencer");
    rejouer.type = "button";
    rejouer.addEventListener("click", function () { self.accueil(); window.scrollTo(0, self.racine.offsetTop - 80); });
    b.appendChild(rejouer);
    this.racine.insertBefore(b, this.racine.firstChild);
    window.scrollTo(0, this.racine.offsetTop - 80);
  };

  // ---------------------------------------------------------------- Démarrage
  function demarrer() {
    var racines = document.querySelectorAll(".auto-qcm[data-banque]");
    Array.prototype.forEach.call(racines, function (racine) {
      if (racine.dataset.pret) return;
      var source = document.getElementById(racine.dataset.banque);
      if (!source) return;
      try {
        racine.dataset.pret = "1";
        new Application(racine, JSON.parse(source.textContent));
      } catch (e) {
        racine.textContent = "Le QCM n'a pas pu être chargé.";
      }
    });
  }
  if (window.document$ && window.document$.subscribe) {
    window.document$.subscribe(demarrer);   // compatible navigation instantanée Material
  } else {
    document.addEventListener("DOMContentLoaded", demarrer);
  }
})();
