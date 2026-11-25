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
  if (tocLinks.length) {
    var secs = tocLinks
      .map(function (a) {
        var id = a.getAttribute("href").slice(1);
        return { id: id, el: document.getElementById(id), link: a };
      })
      .filter(function (s) { return s.el; });

    var updateToc = function () {
      var line = window.scrollY + 130;
      var current = null;
      for (var i = 0; i < secs.length; i++) {
        var top = secs[i].el.getBoundingClientRect().top + window.scrollY;
        if (top <= line) current = secs[i].id;
      }
      // 문서 끝에 도달하면 마지막 항목을 활성화
      if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4) {
        current = secs[secs.length - 1].id;
      }
      secs.forEach(function (s) {
        s.link.classList.toggle("active", s.id === current);
      });
    };
    window.addEventListener("scroll", updateToc, { passive: true });
    window.addEventListener("resize", updateToc);
    updateToc();
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
