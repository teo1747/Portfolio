// Project filters and deep links. The page works without this script:
// every project is shown and every detail can still be opened.
(function () {
  var root = document.getElementById("projects");
  if (!root) return;
  var chips = root.querySelectorAll(".chip");
  var cards = root.querySelectorAll(".proj");
  var lang = document.documentElement.lang;

  var count = document.createElement("p");
  count.className = "count";
  count.setAttribute("aria-live", "polite");
  root.querySelector(".filters").after(count);

  function show(filter) {
    var n = 0;
    cards.forEach(function (c) {
      var on = filter === "all" || c.dataset.cat === filter;
      c.hidden = !on;
      if (on) n++;
    });
    chips.forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.filter === filter)); });
    count.textContent = lang === "fr"
      ? n + (n > 1 ? " projets affichés" : " projet affiché")
      : n + (n === 1 ? " project shown" : " projects shown");
  }

  chips.forEach(function (b) {
    b.addEventListener("click", function () { show(b.dataset.filter); });
  });

  // Links like #p-tcu from the experience section: make the card visible and open it.
  function openTarget() {
    var id = decodeURIComponent(location.hash.slice(1));
    if (!id || id.indexOf("p-") !== 0) return;
    var card = document.getElementById(id);
    if (!card) return;
    if (card.hidden) show("all");
    var d = card.querySelector("details");
    if (d) d.open = true;
  }
  window.addEventListener("hashchange", openTarget);

  show("all");
  openTarget();
})();

// Lightbox for project photos and screenshots. Without JS the link opens the image.
(function () {
  var links = document.querySelectorAll("a[data-zoom]");
  if (!links.length || typeof HTMLDialogElement === "undefined") return;
  var fr = document.documentElement.lang === "fr";
  var dlg = document.createElement("dialog");
  dlg.className = "lightbox";
  dlg.innerHTML = '<button type="button">' + (fr ? "Fermer" : "Close") + '</button><img alt=""><p></p>';
  document.body.appendChild(dlg);
  var img = dlg.querySelector("img"), cap = dlg.querySelector("p");
  dlg.querySelector("button").addEventListener("click", function () { dlg.close(); });
  dlg.addEventListener("click", function (ev) { if (ev.target === dlg || ev.target === img) dlg.close(); });
  links.forEach(function (a) {
    a.addEventListener("click", function (ev) {
      ev.preventDefault();
      var thumb = a.querySelector("img");
      var fc = a.parentElement.querySelector("figcaption");
      img.src = a.href;
      img.alt = thumb ? thumb.alt : "";
      cap.textContent = fc ? fc.textContent : "";
      dlg.showModal();
    });
  });
})();
