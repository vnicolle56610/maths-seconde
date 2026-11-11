---
title: "QCM automatismes Seconde – Probabilités et échantillonnage (interactif, corrigé)"
description: "QCM en ligne d'automatismes de Seconde (probabilités et échantillonnage) : chronomètre, score immédiat et correction détaillée, sans calculatrice."
---

# QCM interactif — Probabilités et échantillonnage

Entraînement **sans calculatrice**. Rien n'est enregistré ni envoyé : tout se passe dans le navigateur.

[← Énoncés et corrigés à lire](automatismes-N18-probabilites-echantillonnage.md)

<div class="auto-qcm" data-banque="banque-automatismes"></div>

<script type="application/json" id="banque-automatismes">
{
 "notion": "N18",
 "cle": "N18",
 "titre": "Probabilités et échantillonnage",
 "niveau": "Seconde",
 "series": [
  {
   "lettre": "A",
   "theme": "Réactivation – fractions et événements",
   "duree": "6 min",
   "consigne": "Répondre rapidement. Simplifier les fractions lorsque c'est immédiat.",
   "qcm": false,
   "figure": ""
  },
  {
   "lettre": "B",
   "theme": "Loi de probabilité et événements",
   "duree": "7 min",
   "consigne": "On donne la loi suivante : <span class=\"arithmatex\">\\(\\begin{array}{c|ccc}x&amp;0&amp;1&amp;2\\\\hline P(X=x)&amp;0{,}2&amp;0{,}5&amp;0{,}3\\end{array}\\)<\/span>. Répondre rapidement.",
   "qcm": false,
   "figure": ""
  },
  {
   "lettre": "C",
   "theme": "Arbres pondérés",
   "duree": "7 min",
   "consigne": "Utiliser les branches de l'arbre. Multiplier le long d'un chemin, additionner les chemins compatibles.",
   "qcm": false,
   "figure": ""
  },
  {
   "lettre": "D",
   "theme": "Type épreuve anticipée – probabilités",
   "duree": "5 min",
   "consigne": "Choisir une seule réponse. Aucune justification n'est demandée.",
   "qcm": false,
   "figure": ""
  }
 ],
 "questions": [
  {
   "id": "N18-A1",
   "serie": "A",
   "theme": "Réactivation – fractions et événements",
   "type": "flash",
   "enonce": "Dans une urne, <span class=\"arithmatex\">\\(3\\)<\/span> boules rouges et <span class=\"arithmatex\">\\(7\\)<\/span> bleues. Probabilité de tirer une rouge.",
   "contexte": [],
   "choix": [],
   "bonne": null,
   "corrige": "<span class=\"arithmatex\">\\(\\dfrac{3}{10}=\\)<\/span><wbr><span class=\"arithmatex\">\\(\\boxed{0{,}3}\\)<\/span>.",
   "methode": "Commencer par compter l'ensemble de référence. Pour un événement contraire, utiliser <span class=\"arithmatex\">\\(P(\\overline A)=1-P(A)\\)<\/span>."
  },
  {
   "id": "N18-A2",
   "serie": "A",
   "theme": "Réactivation – fractions et événements",
   "type": "flash",
   "enonce": "Avec la même urne, probabilité de ne pas tirer rouge.",
   "contexte": [],
   "choix": [],
   "bonne": null,
   "corrige": "<span class=\"arithmatex\">\\(\\dfrac{7}{10}=\\)<\/span><wbr><span class=\"arithmatex\">\\(\\boxed{0{,}7}\\)<\/span>.",
   "methode": "Commencer par compter l'ensemble de référence. Pour un événement contraire, utiliser <span class=\"arithmatex\">\\(P(\\overline A)=1-P(A)\\)<\/span>."
  },
  {
   "id": "N18-A3",
   "serie": "A",
   "theme": "Réactivation – fractions et événements",
   "type": "flash",
   "enonce": "Calculer <span class=\"arithmatex\">\\(1-\\dfrac{3}{10}\\)<\/span>.",
   "contexte": [],
   "choix": [],
   "bonne": null,
   "corrige": "<span class=\"arithmatex\">\\(\\boxed{\\dfrac{7}{10}}\\)<\/span>.",
   "methode": "Commencer par compter l'ensemble de référence. Pour un événement contraire, utiliser <span class=\"arithmatex\">\\(P(\\overline A)=1-P(A)\\)<\/span>."
  },
  {
   "id": "N18-A4",
   "serie": "A",
   "theme": "Réactivation – fractions et événements",
   "type": "flash",
   "enonce": "Si <span class=\"arithmatex\">\\(P(A)=0{,}35\\)<\/span>, calculer <span class=\"arithmatex\">\\(P(\\overline A)\\)<\/span>.",
   "contexte": [],
   "choix": [],
   "bonne": null,
   "corrige": "<span class=\"arithmatex\">\\(1-0{,}35=\\boxed{0{,}65}\\)<\/span>.",
   "methode": "Commencer par compter l'ensemble de référence. Pour un événement contraire, utiliser <span class=\"arithmatex\">\\(P(\\overline A)=1-P(A)\\)<\/span>."
  },
  {
   "id": "N18-A5",
   "serie": "A",
   "theme": "Réactivation – fractions et événements",
   "type": "flash",
   "enonce": "Une probabilité peut-elle valoir <span class=\"arithmatex\">\\(1{,}2\\)<\/span> ?",
   "contexte": [],
   "choix": [],
   "bonne": null,
   "corrige": "<span class=\"arithmatex\">\\(\\boxed{\\text{non}}\\)<\/span>, une probabilité est entre <span class=\"arithmatex\">\\(0\\)<\/span> et <span class=\"arithmatex\">\\(1\\)<\/span>.",
   "methode": "Commencer par compter l'ensemble de référence. Pour un événement contraire, utiliser <span class=\"arithmatex\">\\(P(\\overline A)=1-P(A)\\)<\/span>."
  },
  {
   "id": "N18-A6",
   "serie": "A",
   "theme": "Réactivation – fractions et événements",
   "type": "flash",
   "enonce": "Une probabilité vaut <span class=\"arithmatex\">\\(25\\,\\%\\)<\/span>. L'écrire sous forme décimale.",
   "contexte": [],
   "choix": [],
   "bonne": null,
   "corrige": "<span class=\"arithmatex\">\\(\\boxed{0{,}25}\\)<\/span>.",
   "methode": "Commencer par compter l'ensemble de référence. Pour un événement contraire, utiliser <span class=\"arithmatex\">\\(P(\\overline A)=1-P(A)\\)<\/span>."
  },
  {
   "id": "N18-B1",
   "serie": "B",
   "theme": "Loi de probabilité et événements",
   "type": "flash",
   "enonce": "Vérifier que les probabilités totalisent <span class=\"arithmatex\">\\(1\\)<\/span>.",
   "contexte": [],
   "choix": [],
   "bonne": null,
   "corrige": "<span class=\"arithmatex\">\\(0{,}2+0{,}5+0{,}3=\\)<\/span><wbr><span class=\"arithmatex\">\\(\\boxed{1}\\)<\/span>.",
   "methode": "Colorer mentalement les colonnes qui vérifient la condition, puis additionner les probabilités de ces colonnes."
  },
  {
   "id": "N18-B2",
   "serie": "B",
   "theme": "Loi de probabilité et événements",
   "type": "flash",
   "enonce": "Calculer <span class=\"arithmatex\">\\(P(X=1)\\)<\/span>.",
   "contexte": [],
   "choix": [],
   "bonne": null,
   "corrige": "<span class=\"arithmatex\">\\(\\boxed{0{,}5}\\)<\/span>.",
   "methode": "Colorer mentalement les colonnes qui vérifient la condition, puis additionner les probabilités de ces colonnes."
  },
  {
   "id": "N18-B3",
   "serie": "B",
   "theme": "Loi de probabilité et événements",
   "type": "flash",
   "enonce": "Calculer <span class=\"arithmatex\">\\(P(X\\neq 0)\\)<\/span>.",
   "contexte": [],
   "choix": [],
   "bonne": null,
   "corrige": "<span class=\"arithmatex\">\\(1-0{,}2=\\boxed{0{,}8}\\)<\/span>.",
   "methode": "Colorer mentalement les colonnes qui vérifient la condition, puis additionner les probabilités de ces colonnes."
  },
  {
   "id": "N18-B4",
   "serie": "B",
   "theme": "Loi de probabilité et événements",
   "type": "flash",
   "enonce": "Calculer <span class=\"arithmatex\">\\(P(X\\geqslant1)\\)<\/span>.",
   "contexte": [],
   "choix": [],
   "bonne": null,
   "corrige": "<span class=\"arithmatex\">\\(P(X=\\)<\/span><wbr><span class=\"arithmatex\">\\(1)+P(X=\\)<\/span><wbr><span class=\"arithmatex\">\\(2)=\\)<\/span><wbr><span class=\"arithmatex\">\\(0{,}5+0{,}3=\\)<\/span><wbr><span class=\"arithmatex\">\\(\\boxed{0{,}8}\\)<\/span>.",
   "methode": "Colorer mentalement les colonnes qui vérifient la condition, puis additionner les probabilités de ces colonnes."
  },
  {
   "id": "N18-B5",
   "serie": "B",
   "theme": "Loi de probabilité et événements",
   "type": "flash",
   "enonce": "Calculer <span class=\"arithmatex\">\\(P(X&lt;2)\\)<\/span>.",
   "contexte": [],
   "choix": [],
   "bonne": null,
   "corrige": "<span class=\"arithmatex\">\\(P(X=\\)<\/span><wbr><span class=\"arithmatex\">\\(0)+P(X=\\)<\/span><wbr><span class=\"arithmatex\">\\(1)=\\)<\/span><wbr><span class=\"arithmatex\">\\(0{,}2+0{,}5=\\)<\/span><wbr><span class=\"arithmatex\">\\(\\boxed{0{,}7}\\)<\/span>.",
   "methode": "Colorer mentalement les colonnes qui vérifient la condition, puis additionner les probabilités de ces colonnes."
  },
  {
   "id": "N18-B6",
   "serie": "B",
   "theme": "Loi de probabilité et événements",
   "type": "flash",
   "enonce": "Quel résultat est le plus probable ?",
   "contexte": [],
   "choix": [],
   "bonne": null,
   "corrige": "La probabilité la plus grande est <span class=\"arithmatex\">\\(0{,}5\\)<\/span>, donc <span class=\"arithmatex\">\\(\\boxed{1}\\)<\/span>.",
   "methode": "Colorer mentalement les colonnes qui vérifient la condition, puis additionner les probabilités de ces colonnes."
  },
  {
   "id": "N18-C1",
   "serie": "C",
   "theme": "Arbres pondérés",
   "type": "flash",
   "enonce": "On a <span class=\"arithmatex\">\\(P(A)=0{,}4\\)<\/span>. Calculer <span class=\"arithmatex\">\\(P(\\overline A)\\)<\/span>.",
   "contexte": [],
   "choix": [],
   "bonne": null,
   "corrige": "<span class=\"arithmatex\">\\(1-0{,}4=\\boxed{0{,}6}\\)<\/span>.",
   "methode": "Sur un arbre, un chemin correspond à une intersection. Un événement final peut regrouper plusieurs chemins."
  },
  {
   "id": "N18-C2",
   "serie": "C",
   "theme": "Arbres pondérés",
   "type": "flash",
   "enonce": "On a <span class=\"arithmatex\">\\(P(A)=0{,}4\\)<\/span> et <span class=\"arithmatex\">\\(P_A(B)=0{,}25\\)<\/span>. Calculer <span class=\"arithmatex\">\\(P(A\\cap B)\\)<\/span>.",
   "contexte": [],
   "choix": [],
   "bonne": null,
   "corrige": "<span class=\"arithmatex\">\\(0{,}4\\times0{,}25=\\)<\/span><wbr><span class=\"arithmatex\">\\(\\boxed{0{,}10}\\)<\/span>.",
   "methode": "Sur un arbre, un chemin correspond à une intersection. Un événement final peut regrouper plusieurs chemins."
  },
  {
   "id": "N18-C3",
   "serie": "C",
   "theme": "Arbres pondérés",
   "type": "flash",
   "enonce": "On a <span class=\"arithmatex\">\\(P(A)=0{,}4\\)<\/span> et <span class=\"arithmatex\">\\(P_A(\\overline B)=0{,}75\\)<\/span>. Vérifier la cohérence avec la question précédente.",
   "contexte": [
    "<strong>Q1.<\/strong> On a <span class=\"arithmatex\">\\(P(A)=0{,}4\\)<\/span>. Calculer <span class=\"arithmatex\">\\(P(\\overline A)\\)<\/span>.",
    "<strong>Q2.<\/strong> On a <span class=\"arithmatex\">\\(P(A)=0{,}4\\)<\/span> et <span class=\"arithmatex\">\\(P_A(B)=0{,}25\\)<\/span>. Calculer <span class=\"arithmatex\">\\(P(A\\cap B)\\)<\/span>."
   ],
   "choix": [],
   "bonne": null,
   "corrige": "<span class=\"arithmatex\">\\(0{,}25+0{,}75=\\boxed{1}\\)<\/span>, les branches issues de <span class=\"arithmatex\">\\(A\\)<\/span> sont cohérentes.",
   "methode": "Sur un arbre, un chemin correspond à une intersection. Un événement final peut regrouper plusieurs chemins."
  },
  {
   "id": "N18-C4",
   "serie": "C",
   "theme": "Arbres pondérés",
   "type": "flash",
   "enonce": "On a <span class=\"arithmatex\">\\(P(\\overline A)=0{,}6\\)<\/span> et <span class=\"arithmatex\">\\(P_{\\overline A}(B)=0{,}5\\)<\/span>. Calculer <span class=\"arithmatex\">\\(P(\\overline A\\cap B)\\)<\/span>.",
   "contexte": [],
   "choix": [],
   "bonne": null,
   "corrige": "<span class=\"arithmatex\">\\(0{,}6\\times0{,}5=\\)<\/span><wbr><span class=\"arithmatex\">\\(\\boxed{0{,}30}\\)<\/span>.",
   "methode": "Sur un arbre, un chemin correspond à une intersection. Un événement final peut regrouper plusieurs chemins."
  },
  {
   "id": "N18-C5",
   "serie": "C",
   "theme": "Arbres pondérés",
   "type": "flash",
   "enonce": "En déduire <span class=\"arithmatex\">\\(P(B)\\)<\/span> avec les données des questions 2 et 4.",
   "contexte": [],
   "choix": [],
   "bonne": null,
   "corrige": "<span class=\"arithmatex\">\\(P(B)=\\)<\/span><wbr><span class=\"arithmatex\">\\(0{,}10+0{,}30=\\)<\/span><wbr><span class=\"arithmatex\">\\(\\boxed{0{,}40}\\)<\/span>.",
   "methode": "Sur un arbre, un chemin correspond à une intersection. Un événement final peut regrouper plusieurs chemins."
  },
  {
   "id": "N18-C6",
   "serie": "C",
   "theme": "Arbres pondérés",
   "type": "flash",
   "enonce": "Si <span class=\"arithmatex\">\\(P(B)=0{,}4\\)<\/span>, calculer <span class=\"arithmatex\">\\(P(\\overline B)\\)<\/span>.",
   "contexte": [],
   "choix": [],
   "bonne": null,
   "corrige": "<span class=\"arithmatex\">\\(1-0{,}4=\\boxed{0{,}6}\\)<\/span>.",
   "methode": "Sur un arbre, un chemin correspond à une intersection. Un événement final peut regrouper plusieurs chemins."
  },
  {
   "id": "N18-D1",
   "serie": "D",
   "theme": "Type épreuve anticipée – probabilités",
   "type": "flash",
   "enonce": "Si <span class=\"arithmatex\">\\(P(A)=0{,}62\\)<\/span>, <span class=\"arithmatex\">\\(P(\\overline A)\\)<\/span> : A <span class=\"arithmatex\">\\(0{,}62\\)<\/span> ; B <span class=\"arithmatex\">\\(1{,}62\\)<\/span> ; C <span class=\"arithmatex\">\\(0{,}38\\)<\/span> ; D <span class=\"arithmatex\">\\(-0{,}62\\)<\/span>.",
   "contexte": [],
   "choix": [],
   "bonne": null,
   "corrige": "<strong class=\"auto-resultat\">réponse C<\/strong>.",
   "methode": "Les QCM de probabilités se contrôlent souvent par l'ordre de grandeur et l'intervalle <span class=\"arithmatex\">\\([0;1]\\)<\/span>."
  },
  {
   "id": "N18-D2",
   "serie": "D",
   "theme": "Type épreuve anticipée – probabilités",
   "type": "flash",
   "enonce": "Si <span class=\"arithmatex\">\\(P(A)=0{,}3\\)<\/span> et <span class=\"arithmatex\">\\(P_A(B)=0{,}4\\)<\/span>, <span class=\"arithmatex\">\\(P(A\\cap B)\\)<\/span> : A <span class=\"arithmatex\">\\(0{,}7\\)<\/span> ; B <span class=\"arithmatex\">\\(0{,}12\\)<\/span> ; C <span class=\"arithmatex\">\\(0{,}4\\)<\/span> ; D <span class=\"arithmatex\">\\(0{,}3\\)<\/span>.",
   "contexte": [],
   "choix": [],
   "bonne": null,
   "corrige": "<strong class=\"auto-resultat\">réponse B<\/strong> : <span class=\"arithmatex\">\\(0{,}3\\times0{,}4=0{,}12\\)<\/span>.",
   "methode": "Les QCM de probabilités se contrôlent souvent par l'ordre de grandeur et l'intervalle <span class=\"arithmatex\">\\([0;1]\\)<\/span>."
  },
  {
   "id": "N18-D3",
   "serie": "D",
   "theme": "Type épreuve anticipée – probabilités",
   "type": "flash",
   "enonce": "Une probabilité possible : A <span class=\"arithmatex\">\\(-0{,}2\\)<\/span> ; B <span class=\"arithmatex\">\\(1{,}4\\)<\/span> ; C <span class=\"arithmatex\">\\(0{,}8\\)<\/span> ; D <span class=\"arithmatex\">\\(120\\,\\%\\)<\/span>.",
   "contexte": [],
   "choix": [],
   "bonne": null,
   "corrige": "<strong class=\"auto-resultat\">réponse C<\/strong>.",
   "methode": "Les QCM de probabilités se contrôlent souvent par l'ordre de grandeur et l'intervalle <span class=\"arithmatex\">\\([0;1]\\)<\/span>."
  },
  {
   "id": "N18-D4",
   "serie": "D",
   "theme": "Type épreuve anticipée – probabilités",
   "type": "flash",
   "enonce": "En simulation, une fréquence observée : A égale toujours à la probabilité, B peut fluctuer, C vaut toujours <span class=\"arithmatex\">\\(0\\)<\/span>, D vaut toujours <span class=\"arithmatex\">\\(1\\)<\/span>.",
   "contexte": [],
   "choix": [],
   "bonne": null,
   "corrige": "<strong class=\"auto-resultat\">réponse B<\/strong>.",
   "methode": "Les QCM de probabilités se contrôlent souvent par l'ordre de grandeur et l'intervalle <span class=\"arithmatex\">\\([0;1]\\)<\/span>."
  },
  {
   "id": "N18-D5",
   "serie": "D",
   "theme": "Type épreuve anticipée – probabilités",
   "type": "flash",
   "enonce": "Dans une loi de probabilité, la somme vaut : A <span class=\"arithmatex\">\\(0\\)<\/span> ; B <span class=\"arithmatex\">\\(0{,}5\\)<\/span> ; C <span class=\"arithmatex\">\\(1\\)<\/span> ; D <span class=\"arithmatex\">\\(100\\)<\/span>.",
   "contexte": [],
   "choix": [],
   "bonne": null,
   "corrige": "<strong class=\"auto-resultat\">réponse C<\/strong>.",
   "methode": "Les QCM de probabilités se contrôlent souvent par l'ordre de grandeur et l'intervalle <span class=\"arithmatex\">\\([0;1]\\)<\/span>."
  },
  {
   "id": "N18-D6",
   "serie": "D",
   "theme": "Type épreuve anticipée – probabilités",
   "type": "flash",
   "enonce": "Si <span class=\"arithmatex\">\\(P(A)=1\\)<\/span>, <span class=\"arithmatex\">\\(A\\)<\/span> est : A impossible, B certain, C contraire, D indépendant.",
   "contexte": [],
   "choix": [],
   "bonne": null,
   "corrige": "<strong class=\"auto-resultat\">réponse B<\/strong>.",
   "methode": "Les QCM de probabilités se contrôlent souvent par l'ordre de grandeur et l'intervalle <span class=\"arithmatex\">\\([0;1]\\)<\/span>."
  }
 ]
}
</script>

<noscript>Le QCM interactif nécessite JavaScript. Les énoncés et corrigés sont aussi disponibles <a href="../automatismes-N18-probabilites-echantillonnage/">en lecture</a>.</noscript>
