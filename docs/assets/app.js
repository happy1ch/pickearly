/* PickEarly · 픽얼리 — theme behaviour */
(function () {
  "use strict";

  /* ---------- home: filters + search ---------- */
  var chips = Array.prototype.slice.call(document.querySelectorAll("[data-filter]"));
  var cards = Array.prototype.slice.call(document.querySelectorAll("[data-post]"));
  var searchInput = document.querySelector("[data-search]");
  var emptyState = document.querySelector("[data-empty]");
  var countEls = document.querySelectorAll("[data-result-count]");
  var activeCat = "all";

  function apply() {
    var q = (searchInput && searchInput.value || "").trim().toLowerCase();
    var shown = 0;
    cards.forEach(function (card) {
      var cat = card.getAttribute("data-cat") || "";
      var hay = (card.getAttribute("data-search-text") || "").toLowerCase();
      var matchCat = activeCat === "all" || cat === activeCat;
      var matchQ = !q || hay.indexOf(q) !== -1;
      var ok = matchCat && matchQ;
      card.style.display = ok ? "" : "none";
      if (ok) shown++;
    });
    if (emptyState) emptyState.classList.toggle("show", shown === 0);
    Array.prototype.forEach.call(countEls, function (el) { el.textContent = String(shown); });
  }

  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      activeCat = chip.getAttribute("data-filter");
      chips.forEach(function (c) {
        c.setAttribute("aria-pressed", c === chip ? "true" : "false");
      });
      apply();
    });
  });

  if (searchInput) {
    searchInput.addEventListener("input", apply);
    // "/" focuses search
    document.addEventListener("keydown", function (e) {
      if (e.key === "/" && document.activeElement !== searchInput) {
        e.preventDefault();
        searchInput.focus();
      }
    });
  }

  if (cards.length) apply();

  /* ---------- article: reading progress ---------- */
  var progress = document.querySelector("[data-progress]");
  if (progress) {
    var onScroll = function () {
      var h = document.documentElement;
      var max = h.scrollHeight - h.clientHeight;
      var pct = max > 0 ? (h.scrollTop / max) * 100 : 0;
      progress.style.width = Math.min(100, Math.max(0, pct)) + "%";
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    onScroll();
  }

  /* ---------- article: TOC active section ---------- */
  var tocLinks = Array.prototype.slice.call(document.querySelectorAll("[data-toc-link]"));
  if (tocLinks.length && "IntersectionObserver" in window) {
    var targets = tocLinks
      .map(function (a) { return document.getElementById(a.getAttribute("href").slice(1)); })
      .filter(Boolean);
    var visible = {};
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { visible[en.target.id] = en.isIntersecting ? en.boundingClientRect.top : null; });
      var current = null;
      for (var i = 0; i < targets.length; i++) {
        if (visible[targets[i].id] !== null && visible[targets[i].id] !== undefined) { current = targets[i].id; break; }
      }
      if (current) {
        tocLinks.forEach(function (a) {
          a.classList.toggle("active", a.getAttribute("href") === "#" + current);
        });
      }
    }, { rootMargin: "-92px 0px -60% 0px", threshold: [0, 1] });
    targets.forEach(function (t) { io.observe(t); });
  }

  /* ---------- copy link ---------- */
  var copyBtn = document.querySelector("[data-copy-link]");
  if (copyBtn) {
    copyBtn.addEventListener("click", function () {
      var label = copyBtn.querySelector("[data-copy-label]");
      var original = label ? label.textContent : "";
      var done = function () {
        if (!label) return;
        label.textContent = "링크가 복사되었습니다";
        copyBtn.classList.add("copied");
        setTimeout(function () { label.textContent = original; }, 2000);
      };
      var url = copyBtn.getAttribute("data-copy-link") || window.location.href;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(done, function () { window.prompt("링크를 복사하세요", url); });
      } else {
        window.prompt("링크를 복사하세요", url);
      }
    });
  }
})();
