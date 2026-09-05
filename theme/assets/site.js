/* Seigneurie Adjaoudi — le seul script du site.
   Il fait deux choses : ouvrir le menu sur petit ecran, et chercher dans un
   index construit a la construction du site. Aucune requete n'est emise :
   l'index est un fichier du site, charge avec la page. */
(function () {
  "use strict";

  /* ------------------------------------------------------------- menu */
  var bascule = document.querySelector(".bascule");
  var entete = document.querySelector(".hdr");
  if (bascule && entete) {
    bascule.addEventListener("click", function () {
      var ouvert = entete.classList.toggle("ouvert");
      bascule.setAttribute("aria-expanded", ouvert ? "true" : "false");
    });
  }

  /* --------------------------------------------------------- recherche */
  var panneau = document.getElementById("rech");
  var champ = document.getElementById("q");
  var liste = document.getElementById("res");
  var loupe = document.querySelector(".loupe");
  var fermer = document.querySelector(".rech .fermer");
  if (!panneau || !champ || !liste || !loupe) { return; }

  var vide = (document.getElementById("rech-vide") || {}).textContent || "";
  var dernier = null;

  function normalise(s) {
    s = (s || "").toLowerCase();
    if (s.normalize) { s = s.normalize("NFD").replace(/[\u0300-\u036f]/g, ""); }
    return s;
  }

  function ouvre() {
    dernier = document.activeElement;
    panneau.classList.add("on");
    champ.value = "";
    liste.innerHTML = "";
    champ.focus();
    document.addEventListener("keydown", touche, true);
  }

  function ferme() {
    panneau.classList.remove("on");
    document.removeEventListener("keydown", touche, true);
    if (dernier && dernier.focus) { dernier.focus(); }
  }

  function touche(e) {
    if (e.key === "Escape") { e.preventDefault(); ferme(); return; }
    if (e.key !== "Tab") { return; }
    var f = panneau.querySelectorAll("input, button, a[href]");
    if (!f.length) { return; }
    var premier = f[0], der = f[f.length - 1];
    if (e.shiftKey && document.activeElement === premier) {
      e.preventDefault(); der.focus();
    } else if (!e.shiftKey && document.activeElement === der) {
      e.preventDefault(); premier.focus();
    }
  }

  function cherche() {
    var q = normalise(champ.value).trim();
    liste.innerHTML = "";
    if (q.length < 2) { return; }
    var mots = q.split(/\s+/);
    var idx = window.__IDX || [];
    var trouves = [];
    for (var i = 0; i < idx.length; i++) {
      var e = idx[i];
      var foin = normalise(e.t + " " + e.p + " " + e.x);
      var titre = normalise(e.t);
      var score = 0, tous = true;
      for (var m = 0; m < mots.length; m++) {
        if (foin.indexOf(mots[m]) === -1) { tous = false; break; }
        score += titre.indexOf(mots[m]) !== -1 ? 3 : 1;
      }
      if (tous) { trouves.push([score, e]); }
    }
    trouves.sort(function (a, b) { return b[0] - a[0]; });
    if (!trouves.length) {
      var li = document.createElement("li");
      li.textContent = vide;
      li.style.padding = "12px 4px";
      liste.appendChild(li);
      return;
    }
    for (var j = 0; j < trouves.length && j < 12; j++) {
      var d = trouves[j][1];
      var el = document.createElement("li");
      var a = document.createElement("a");
      a.href = d.u;
      var ou = document.createElement("span");
      ou.className = "ou";
      ou.textContent = d.p;
      a.appendChild(ou);
      a.appendChild(document.createTextNode(d.t));
      el.appendChild(a);
      liste.appendChild(el);
    }
  }

  loupe.addEventListener("click", ouvre);
  if (fermer) { fermer.addEventListener("click", ferme); }
  panneau.addEventListener("click", function (e) {
    if (e.target === panneau) { ferme(); }
  });
  champ.addEventListener("input", cherche);
})();
