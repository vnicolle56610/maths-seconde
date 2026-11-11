---
title: "Automatismes Seconde – Probabilités et échantillonnage : exercices et QCM corrigés"
description: "24 questions d'automatismes de Seconde (probabilités et échantillonnage), sans calculatrice, en 4 séries chronométrées, avec corrigés détaillés et QCM interactif."
---

# Automatismes N18 — Probabilités et échantillonnage

24 questions **sans calculatrice**, réparties en 4 séries courtes à faire en quelques minutes. Chercher d'abord seul, puis ouvrir le corrigé.

<div class="auto-actions" markdown>
[⚡ Faire le QCM interactif](qcm-N18-probabilites-echantillonnage.md){ .md-button .md-button--primary }
[📄 Diaporama PDF à projeter](AUTOMATISMES_N18_PROBABILITES_ECHANTILLONNAGE.pdf){ .md-button }
[📖 Revoir la notion](../notions/N18-probabilites-echantillonnage.md){ .md-button }
</div>

## Série A — Réactivation – fractions et événements

<p class="auto-meta">⏱ 6 min · Calculatrice interdite</p>

<div class="auto-consigne" markdown>
**Consigne.** Répondre rapidement. Simplifier les fractions lorsque c'est immédiat.
</div>

<ol class="auto-questions">
<li value="1">Dans une urne, <span class="arithmatex">\(3\)</span> boules rouges et <span class="arithmatex">\(7\)</span> bleues. Probabilité de tirer une rouge.</li>
<li value="2">Avec la même urne, probabilité de ne pas tirer rouge.</li>
<li value="3">Calculer <span class="arithmatex">\(1-\dfrac{3}{10}\)</span>.</li>
<li value="4">Si <span class="arithmatex">\(P(A)=0{,}35\)</span>, calculer <span class="arithmatex">\(P(\overline A)\)</span>.</li>
<li value="5">Une probabilité peut-elle valoir <span class="arithmatex">\(1{,}2\)</span> ?</li>
<li value="6">Une probabilité vaut <span class="arithmatex">\(25\,\%\)</span>. L'écrire sous forme décimale.</li>
</ol>

??? tip "Coup de pouce"

    <p><strong>Conseils</strong></p><ul><li>Probabilité = cas favorables / cas possibles, si équiprobabilité.</li><li>Le contraire se calcule avec <span class="arithmatex">\(1-P(A)\)</span>.</li><li><span class="arithmatex">\(25\,\%=0{,}25\)</span>.</li></ul>
    <p><strong>Vigilance</strong></p><ul><li>Une probabilité ne peut pas être négative ni dépasser <span class="arithmatex">\(1\)</span>.</li><li>Le contraire de rouge est « non rouge ».</li></ul>

??? success "Corrigé de la série A"

    <ol class="auto-corrige">
    <li value="1"><span class="arithmatex">\(\dfrac{3}{10}=\)</span><wbr><span class="arithmatex">\(\boxed{0{,}3}\)</span>.</li>
    <li value="2"><span class="arithmatex">\(\dfrac{7}{10}=\)</span><wbr><span class="arithmatex">\(\boxed{0{,}7}\)</span>.</li>
    <li value="3"><span class="arithmatex">\(\boxed{\dfrac{7}{10}}\)</span>.</li>
    <li value="4"><span class="arithmatex">\(1-0{,}35=\boxed{0{,}65}\)</span>.</li>
    <li value="5"><span class="arithmatex">\(\boxed{\text{non}}\)</span>, une probabilité est entre <span class="arithmatex">\(0\)</span> et <span class="arithmatex">\(1\)</span>.</li>
    <li value="6"><span class="arithmatex">\(\boxed{0{,}25}\)</span>.</li>
    </ol>
    <div class="auto-methode"><strong>Méthode.</strong> Commencer par compter l'ensemble de référence. Pour un événement contraire, utiliser <span class="arithmatex">\(P(\overline A)=1-P(A)\)</span>.</div>
    <div class="auto-vigilance"><strong>Vigilance.</strong> Ne pas confondre l'événement contraire avec un événement simplement différent.</div>

## Série B — Loi de probabilité et événements

<p class="auto-meta">⏱ 7 min · Calculatrice interdite</p>

<div class="auto-consigne" markdown>
**Consigne.** On donne la loi suivante : <span class="arithmatex">\(\begin{array}{c|ccc}x&amp;0&amp;1&amp;2\\hline P(X=x)&amp;0{,}2&amp;0{,}5&amp;0{,}3\end{array}\)</span>. Répondre rapidement.
</div>

<ol class="auto-questions">
<li value="1">Vérifier que les probabilités totalisent <span class="arithmatex">\(1\)</span>.</li>
<li value="2">Calculer <span class="arithmatex">\(P(X=1)\)</span>.</li>
<li value="3">Calculer <span class="arithmatex">\(P(X\neq 0)\)</span>.</li>
<li value="4">Calculer <span class="arithmatex">\(P(X\geqslant1)\)</span>.</li>
<li value="5">Calculer <span class="arithmatex">\(P(X&lt;2)\)</span>.</li>
<li value="6">Quel résultat est le plus probable ?</li>
</ol>

??? tip "Coup de pouce"

    <p><strong>Conseils</strong></p><ul><li>Une loi de probabilité totalise <span class="arithmatex">\(1\)</span>.</li><li>Pour <span class="arithmatex">\(X\neq0\)</span>, penser au contraire.</li><li>Pour une inégalité, additionner les probabilités correspondantes.</li></ul>
    <p><strong>Vigilance</strong></p><ul><li>Ne pas additionner les valeurs de <span class="arithmatex">\(x\)</span>, mais les probabilités.</li><li>Lire correctement les signes <span class="arithmatex">\(&lt;\)</span>, <span class="arithmatex">\(\geqslant\)</span>.</li></ul>

??? success "Corrigé de la série B"

    <ol class="auto-corrige">
    <li value="1"><span class="arithmatex">\(0{,}2+0{,}5+0{,}3=\)</span><wbr><span class="arithmatex">\(\boxed{1}\)</span>.</li>
    <li value="2"><span class="arithmatex">\(\boxed{0{,}5}\)</span>.</li>
    <li value="3"><span class="arithmatex">\(1-0{,}2=\boxed{0{,}8}\)</span>.</li>
    <li value="4"><span class="arithmatex">\(P(X=\)</span><wbr><span class="arithmatex">\(1)+P(X=\)</span><wbr><span class="arithmatex">\(2)=\)</span><wbr><span class="arithmatex">\(0{,}5+0{,}3=\)</span><wbr><span class="arithmatex">\(\boxed{0{,}8}\)</span>.</li>
    <li value="5"><span class="arithmatex">\(P(X=\)</span><wbr><span class="arithmatex">\(0)+P(X=\)</span><wbr><span class="arithmatex">\(1)=\)</span><wbr><span class="arithmatex">\(0{,}2+0{,}5=\)</span><wbr><span class="arithmatex">\(\boxed{0{,}7}\)</span>.</li>
    <li value="6">La probabilité la plus grande est <span class="arithmatex">\(0{,}5\)</span>, donc <span class="arithmatex">\(\boxed{1}\)</span>.</li>
    </ol>
    <div class="auto-methode"><strong>Méthode.</strong> Colorer mentalement les colonnes qui vérifient la condition, puis additionner les probabilités de ces colonnes.</div>
    <div class="auto-vigilance"><strong>Vigilance.</strong> Un résultat probable n'est pas forcément un résultat certain.</div>

## Série C — Arbres pondérés

<p class="auto-meta">⏱ 7 min · Calculatrice interdite</p>

<div class="auto-consigne" markdown>
**Consigne.** Utiliser les branches de l'arbre. Multiplier le long d'un chemin, additionner les chemins compatibles.
</div>

<ol class="auto-questions">
<li value="1">On a <span class="arithmatex">\(P(A)=0{,}4\)</span>. Calculer <span class="arithmatex">\(P(\overline A)\)</span>.</li>
<li value="2">On a <span class="arithmatex">\(P(A)=0{,}4\)</span> et <span class="arithmatex">\(P_A(B)=0{,}25\)</span>. Calculer <span class="arithmatex">\(P(A\cap B)\)</span>.</li>
<li value="3">On a <span class="arithmatex">\(P(A)=0{,}4\)</span> et <span class="arithmatex">\(P_A(\overline B)=0{,}75\)</span>. Vérifier la cohérence avec la question précédente.</li>
<li value="4">On a <span class="arithmatex">\(P(\overline A)=0{,}6\)</span> et <span class="arithmatex">\(P_{\overline A}(B)=0{,}5\)</span>. Calculer <span class="arithmatex">\(P(\overline A\cap B)\)</span>.</li>
<li value="5">En déduire <span class="arithmatex">\(P(B)\)</span> avec les données des questions 2 et 4.</li>
<li value="6">Si <span class="arithmatex">\(P(B)=0{,}4\)</span>, calculer <span class="arithmatex">\(P(\overline B)\)</span>.</li>
</ol>

??? tip "Coup de pouce"

    <p><strong>Conseils</strong></p><ul><li>Chemin : on multiplie.</li><li>Plusieurs chemins : on additionne.</li><li>Deux branches issues d'un même noeud totalisent <span class="arithmatex">\(1\)</span>.</li></ul>
    <p><strong>Vigilance</strong></p><ul><li><span class="arithmatex">\(P_A(B)\)</span> n'est pas <span class="arithmatex">\(P(A\cap B)\)</span>.</li><li>Une probabilité conditionnelle dépend de la branche précédente.</li></ul>

??? success "Corrigé de la série C"

    <ol class="auto-corrige">
    <li value="1"><span class="arithmatex">\(1-0{,}4=\boxed{0{,}6}\)</span>.</li>
    <li value="2"><span class="arithmatex">\(0{,}4\times0{,}25=\)</span><wbr><span class="arithmatex">\(\boxed{0{,}10}\)</span>.</li>
    <li value="3"><span class="arithmatex">\(0{,}25+0{,}75=\boxed{1}\)</span>, les branches issues de <span class="arithmatex">\(A\)</span> sont cohérentes.</li>
    <li value="4"><span class="arithmatex">\(0{,}6\times0{,}5=\)</span><wbr><span class="arithmatex">\(\boxed{0{,}30}\)</span>.</li>
    <li value="5"><span class="arithmatex">\(P(B)=\)</span><wbr><span class="arithmatex">\(0{,}10+0{,}30=\)</span><wbr><span class="arithmatex">\(\boxed{0{,}40}\)</span>.</li>
    <li value="6"><span class="arithmatex">\(1-0{,}4=\boxed{0{,}6}\)</span>.</li>
    </ol>
    <div class="auto-methode"><strong>Méthode.</strong> Sur un arbre, un chemin correspond à une intersection. Un événement final peut regrouper plusieurs chemins.</div>
    <div class="auto-vigilance"><strong>Vigilance.</strong> Écrire <span class="arithmatex">\(P(A\cap B)=\)</span><wbr><span class="arithmatex">\(P(A)\times P_A(B)\)</span>, pas seulement <span class="arithmatex">\(P_A(B)\)</span>.</div>

## Série D — Type épreuve anticipée – probabilités

<p class="auto-meta">⏱ 5 min · Calculatrice interdite</p>

<div class="auto-consigne" markdown>
**Consigne.** Choisir une seule réponse. Aucune justification n'est demandée.
</div>

<ol class="auto-questions">
<li value="1">Si <span class="arithmatex">\(P(A)=0{,}62\)</span>, <span class="arithmatex">\(P(\overline A)\)</span> : A <span class="arithmatex">\(0{,}62\)</span> ; B <span class="arithmatex">\(1{,}62\)</span> ; C <span class="arithmatex">\(0{,}38\)</span> ; D <span class="arithmatex">\(-0{,}62\)</span>.</li>
<li value="2">Si <span class="arithmatex">\(P(A)=0{,}3\)</span> et <span class="arithmatex">\(P_A(B)=0{,}4\)</span>, <span class="arithmatex">\(P(A\cap B)\)</span> : A <span class="arithmatex">\(0{,}7\)</span> ; B <span class="arithmatex">\(0{,}12\)</span> ; C <span class="arithmatex">\(0{,}4\)</span> ; D <span class="arithmatex">\(0{,}3\)</span>.</li>
<li value="3">Une probabilité possible : A <span class="arithmatex">\(-0{,}2\)</span> ; B <span class="arithmatex">\(1{,}4\)</span> ; C <span class="arithmatex">\(0{,}8\)</span> ; D <span class="arithmatex">\(120\,\%\)</span>.</li>
<li value="4">En simulation, une fréquence observée : A égale toujours à la probabilité, B peut fluctuer, C vaut toujours <span class="arithmatex">\(0\)</span>, D vaut toujours <span class="arithmatex">\(1\)</span>.</li>
<li value="5">Dans une loi de probabilité, la somme vaut : A <span class="arithmatex">\(0\)</span> ; B <span class="arithmatex">\(0{,}5\)</span> ; C <span class="arithmatex">\(1\)</span> ; D <span class="arithmatex">\(100\)</span>.</li>
<li value="6">Si <span class="arithmatex">\(P(A)=1\)</span>, <span class="arithmatex">\(A\)</span> est : A impossible, B certain, C contraire, D indépendant.</li>
</ol>

??? tip "Coup de pouce"

    <p><strong>Conseils</strong></p><ul><li>Contrôler que la réponse est entre <span class="arithmatex">\(0\)</span> et <span class="arithmatex">\(1\)</span>.</li><li>Pour un chemin d'arbre, multiplier.</li><li>En simulation, distinguer fréquence et probabilité.</li></ul>
    <p><strong>Vigilance</strong></p><ul><li>Une fréquence expérimentale varie d'un échantillon à l'autre.</li><li>La somme d'une loi vaut <span class="arithmatex">\(1\)</span>, pas <span class="arithmatex">\(100\)</span> sauf en pourcentage.</li></ul>

??? success "Corrigé de la série D"

    <ol class="auto-corrige">
    <li value="1"><strong class="auto-resultat">réponse C</strong>.</li>
    <li value="2"><strong class="auto-resultat">réponse B</strong> : <span class="arithmatex">\(0{,}3\times0{,}4=0{,}12\)</span>.</li>
    <li value="3"><strong class="auto-resultat">réponse C</strong>.</li>
    <li value="4"><strong class="auto-resultat">réponse B</strong>.</li>
    <li value="5"><strong class="auto-resultat">réponse C</strong>.</li>
    <li value="6"><strong class="auto-resultat">réponse B</strong>.</li>
    </ol>
    <div class="auto-methode"><strong>Méthode.</strong> Les QCM de probabilités se contrôlent souvent par l'ordre de grandeur et l'intervalle <span class="arithmatex">\([0;1]\)</span>.</div>
    <div class="auto-vigilance"><strong>Vigilance.</strong> Une réponse supérieure à <span class="arithmatex">\(1\)</span> est impossible pour une probabilité.</div>

---

*Ces questions reprennent le diaporama d'automatismes N18 utilisé en classe. Licence CC BY-NC-SA 4.0 : réutilisation libre en classe, en citant la source.*
