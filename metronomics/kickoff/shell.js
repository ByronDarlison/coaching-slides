/* Shared slideshow controller.
   Sidebar, notes, and full screen follow the cash deck chrome. */
(function () {
  "use strict";

  class SlidePresentation {
    constructor() {
      this.slides = Array.from(document.querySelectorAll(".slide"));
      this.currentSlide = 0;
      document.body.classList.toggle("template-review", new URLSearchParams(location.search).get("review") === "template");
      this.wheelLocked = false;
      this.touchStartY = null;
      this.viewportSettling = false;
      this.counter = document.getElementById("controlCount");
      this.notesPanel = document.getElementById("notesPanel");
      this.notesTitle = document.getElementById("notesTitle");
      this.notesBody = document.getElementById("notesBody");
      this.fullscreenButton = document.getElementById("fullscreenButton");
      this.fullscreenLabel = document.getElementById("fullscreenLabel");
      this.sidebar = document.getElementById("slideSidebar");
      this.sidebarToggle = document.getElementById("sidebarToggle");
      this.sidebarBackdrop = document.getElementById("sidebarBackdrop");
      this.desktopQuery = window.matchMedia("(min-width: 1181px)");
      this.drawerQuery = window.matchMedia("(max-width: 1180px)");
      this.setupIntersectionObserver();
      this.setupKeyboardNavigation();
      this.setupTouchNavigation();
      this.setupWheelNavigation();
      this.setupControls();
      this.setupSidebar();
      this.setupNotes();
      this.setupFullscreen();
      this.goToHash();
    }

    goToHash() {
      const match = window.location.hash.match(/^#slide-(\d+)$/);
      const target = match ? Number(match[1]) - 1 : 0;
      this.goTo(Math.max(0, Math.min(target, this.slides.length - 1)), false);
    }

    goTo(index, smooth) {
      if (index < 0 || index >= this.slides.length) return;
      this.currentSlide = index;
      this.slides[index].scrollIntoView({ behavior: smooth && !window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "smooth" : "instant", block: "start" });
      history.replaceState(null, "", "#slide-" + (index + 1));
      this.updateInterface();
    }

    next() { this.goTo(Math.min(this.currentSlide + 1, this.slides.length - 1), true); }
    previous() { this.goTo(Math.max(this.currentSlide - 1, 0), true); }

    updateInterface() {
      if (this.counter) this.counter.textContent = (this.currentSlide + 1) + " / " + this.slides.length;
      document.querySelectorAll(".sidebar-link").forEach((link, index) => {
        const active = index === this.currentSlide;
        link.classList.toggle("active", active);
        link.setAttribute("aria-current", active ? "page" : "false");
      });
      const activeLink = document.querySelector(".sidebar-link.active");
      const sidebarNav = document.getElementById("sidebarNav");
      if (activeLink && sidebarNav) {
        const linkRect = activeLink.getBoundingClientRect();
        const navRect = sidebarNav.getBoundingClientRect();
        const precedingGroup = activeLink.previousElementSibling &&
          activeLink.previousElementSibling.classList.contains("sidebar-group")
          ? activeLink.previousElementSibling
          : null;
        const topAnchor = (precedingGroup || activeLink).getBoundingClientRect();
        if (topAnchor.top < navRect.top + 8) sidebarNav.scrollTop += topAnchor.top - navRect.top - 8;
        if (linkRect.bottom > navRect.bottom) sidebarNav.scrollTop += linkRect.bottom - navRect.bottom + 8;
      }
      const slide = this.slides[this.currentSlide];
      document.body.classList.toggle(
        "dark-slide-controls",
        Boolean(slide && (slide.classList.contains("closing-slide") || slide.classList.contains("comp-rule")))
      );
      if (this.notesPanel.classList.contains("open")) this.renderNotes();
    }

    setupIntersectionObserver() {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) entry.target.classList.add("visible");
        });
      }, { threshold: 0.05 });
      this.slides.forEach((slide) => observer.observe(slide));
      let pending = false;
      document.addEventListener("scroll", (event) => {
        if (event.target instanceof Element && event.target.closest(".slide-sidebar, .notes-panel")) return;
        if (pending || this.viewportSettling) return;
        pending = true;
        requestAnimationFrame(() => {
          pending = false;
          if (this.viewportSettling) return;
          let selected = 0;
          this.slides.forEach((slide, index) => {
            if (slide.getBoundingClientRect().top <= window.innerHeight * 0.35) selected = index;
          });
          if (selected !== this.currentSlide) {
            this.currentSlide = selected;
            history.replaceState(null, "", "#slide-" + (selected + 1));
            this.updateInterface();
          }
        });
      }, { passive: true, capture: true });
      window.addEventListener("hashchange", () => this.goToHash());
    }

    setupKeyboardNavigation() {
      document.addEventListener("keydown", (event) => {
        if (event.target.closest("input, textarea, select, [contenteditable=true]")) return;
        if (event.key === "ArrowRight" || event.key === "ArrowDown" || event.key === "PageDown" || event.key === " ") {
          event.preventDefault();
          this.next();
        }
        if (event.key === "ArrowLeft" || event.key === "ArrowUp" || event.key === "PageUp") {
          event.preventDefault();
          this.previous();
        }
        if (event.key === "Home") {
          event.preventDefault();
          this.goTo(0, true);
        }
        if (event.key === "End") {
          event.preventDefault();
          this.goTo(this.slides.length - 1, true);
        }
        if (event.key === "n" || event.key === "N") this.toggleNotes();
        if (event.key === "f" || event.key === "F") this.toggleFullscreen();
        if (event.key === "s" || event.key === "S") this.toggleSidebar();
        if (event.key === "Escape" && this.notesPanel.classList.contains("open")) this.toggleNotes(false);
        if (event.key === "Escape" && this.sidebar.classList.contains("open")) this.toggleSidebar(false);
      });
    }

    setupTouchNavigation() {
      let start = null;
      document.addEventListener("touchstart", (event) => {
        start = event.changedTouches[0];
      }, { passive: true });
      document.addEventListener("touchend", (event) => {
        if (!start) return;
        const dx = start.clientX - event.changedTouches[0].clientX;
        const dy = start.clientY - event.changedTouches[0].clientY;
        start = null;
        if (event.target.closest(".notes-panel, .slide-sidebar, .controls")) return;
        // Vertical swipes scroll long mobile slides; horizontal swipes change slides.
        if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy) * 2) {
          if (dx > 0) this.next(); else this.previous();
        }
      }, { passive: true });
    }

    setupWheelNavigation() {
      document.addEventListener("wheel", (event) => {
        if (window.matchMedia("(max-width: 899px), (max-height: 599px)").matches) return;
        if (this.wheelLocked || Math.abs(event.deltaY) < 24) return;
        if (this.notesPanel.classList.contains("open")) return;
        if (document.body.classList.contains("sidebar-open")) return;
        if (event.target.closest(".notes-panel, .slide-sidebar, .controls")) return;
        this.wheelLocked = true;
        if (event.deltaY > 0) this.next();
        else this.previous();
        window.setTimeout(() => { this.wheelLocked = false; }, 500);
      }, { passive: true });
    }

    setupControls() {
      document.addEventListener("pointermove", (event) => {
        document.body.classList.toggle(
          "controls-visible",
          event.clientX >= window.innerWidth / 2 && event.clientY >= window.innerHeight / 2
        );
      });
      document.documentElement.addEventListener("pointerleave", () => {
        document.body.classList.remove("controls-visible");
      });
      document.getElementById("previousButton").addEventListener("click", () => this.previous());
      this.fullscreenButton.addEventListener("click", () => this.toggleFullscreen());
      document.getElementById("nextButton").addEventListener("click", () => this.next());
    }

    setupFullscreen() {
      let lastWidth = window.innerWidth;
      window.addEventListener("resize", () => {
        const width = window.innerWidth;
        const reading = window.matchMedia("(max-width: 899px), (max-height: 599px)").matches;
        const heightOnly = width === lastWidth;
        lastWidth = width;
        // Mobile browser toolbars change viewport height during ordinary reading.
        if (reading && heightOnly && !document.fullscreenElement) return;
        this.alignAfterResize();
      });
      document.addEventListener("fullscreenchange", () => {
        document.body.classList.remove("fullscreen-sidebar-open");
        const desktopHidden = document.body.classList.contains("sidebar-hidden");
        this.sidebar.inert = Boolean(document.fullscreenElement) || (this.desktopQuery.matches && desktopHidden);
        const show = !document.fullscreenElement && !desktopHidden;
        const sidebarButton = document.getElementById("sidebarDesktopToggle");
        sidebarButton.textContent = show ? "Hide sidebar" : "Show sidebar";
        sidebarButton.setAttribute("aria-expanded", String(show));
        this.updateFullscreenControl();
        this.alignAfterResize();
      });
      this.updateFullscreenControl();
    }

    alignAfterResize() {
      this.viewportSettling = true;
      clearTimeout(this.resizeTimer);
      this.slides[this.currentSlide].scrollIntoView({ behavior: "instant", block: "start" });
      this.resizeTimer = setTimeout(() => {
        this.slides[this.currentSlide].scrollIntoView({ behavior: "instant", block: "start" });
        requestAnimationFrame(() => { this.viewportSettling = false; });
      }, 250);
    }

    updateFullscreenControl() {
      const isFullscreen = Boolean(document.fullscreenElement);
      this.fullscreenButton.setAttribute("aria-pressed", isFullscreen ? "true" : "false");
      this.fullscreenButton.setAttribute("aria-label", isFullscreen ? "Exit full screen" : "Enter full screen");
      this.fullscreenLabel.textContent = isFullscreen ? "Exit full screen" : "Full screen";
    }

    setupSidebar() {
      const container = document.getElementById("sidebarNav");
      this.slides.forEach((slide, index) => {
        const groupName = slide.dataset.group;
        if (groupName) {
          const group = document.createElement("p");
          group.className = "sidebar-group";
          group.textContent = groupName;
          container.appendChild(group);
        }
        const link = document.createElement("button");
        link.className = "sidebar-link";
        link.type = "button";
        const title = slide.dataset.title || ("Slide " + (index + 1));
        link.innerHTML = '<span class="sidebar-number">' + String(index + 1).padStart(2, "0") +
          '</span><span class="sidebar-label"></span>';
        link.querySelector(".sidebar-label").textContent = title;
        link.setAttribute("aria-label", "Go to slide " + (index + 1) + ": " + title);
        link.addEventListener("click", () => {
          this.goTo(index, false);
          if (document.fullscreenElement || this.drawerQuery.matches) this.toggleSidebar(false);
        });
        container.appendChild(link);
      });
      this.sidebarToggle.addEventListener("click", () => this.toggleSidebar());
      this.sidebarBackdrop.addEventListener("click", () => this.toggleSidebar(false));
      document.getElementById("sidebarDesktopToggle").addEventListener("click", () => this.toggleSidebar());
      this.drawerQuery.addEventListener("change", () => {
        this.sidebar.inert = this.desktopQuery.matches && document.body.classList.contains("sidebar-hidden");
      });
    }

    toggleSidebar(force) {
      const button = document.getElementById("sidebarDesktopToggle");
      if (document.fullscreenElement) {
        const show = typeof force === "boolean" ? force : !document.body.classList.contains("fullscreen-sidebar-open");
        document.body.classList.toggle("fullscreen-sidebar-open", show);
        this.sidebar.inert = !show;
        button.textContent = show ? "Hide sidebar" : "Show sidebar";
        button.setAttribute("aria-expanded", String(show));
        if (show) this.sidebar.querySelector('[aria-current="page"]')?.scrollIntoView({ block: "nearest" });
        return;
      }
      if (this.desktopQuery.matches) {
        const show = typeof force === "boolean" ? force : document.body.classList.contains("sidebar-hidden");
        document.body.classList.toggle("sidebar-hidden", !show);
        this.sidebar.inert = !show;
        button.textContent = show ? "Hide sidebar" : "Show sidebar";
        button.setAttribute("aria-expanded", String(show));
        return;
      }
      const shouldOpen = typeof force === "boolean" ? force : !this.sidebar.classList.contains("open");
      this.sidebar.classList.toggle("open", shouldOpen);
      this.sidebarBackdrop.classList.toggle("visible", shouldOpen);
      document.body.classList.toggle("sidebar-open", shouldOpen);
      this.sidebarToggle.setAttribute("aria-expanded", shouldOpen ? "true" : "false");
      this.sidebarToggle.setAttribute("aria-label", shouldOpen ? "Close slide navigation" : "Open slide navigation");
    }

    setupNotes() {
      document.getElementById("notesClose").addEventListener("click", () => this.toggleNotes(false));
    }

    renderNotes() {
      const slide = this.slides[this.currentSlide];
      const notes = slide.querySelector(".speaker-notes");
      this.notesTitle.textContent = "Slide " + (this.currentSlide + 1) + ": " + (slide.dataset.title || "");
      this.notesBody.replaceChildren();
      if (!notes) {
        const empty = document.createElement("p");
        empty.textContent = "No notes for this slide.";
        this.notesBody.appendChild(empty);
        return;
      }
      notes.querySelectorAll("p").forEach((source) => {
        const copy = document.createElement("p");
        copy.textContent = source.textContent;
        this.notesBody.appendChild(copy);
      });
    }

    toggleNotes(force) {
      const shouldOpen = typeof force === "boolean" ? force : !this.notesPanel.classList.contains("open");
      this.notesPanel.classList.toggle("open", shouldOpen);
      this.notesPanel.setAttribute("aria-hidden", shouldOpen ? "false" : "true");
      if (shouldOpen) this.renderNotes();
    }

    async toggleFullscreen() {
      this.viewportSettling = true;
      try {
        if (!document.fullscreenElement) await document.documentElement.requestFullscreen();
        else await document.exitFullscreen();
      } catch (error) {
        this.viewportSettling = false;
      } finally {
        this.alignAfterResize();
      }
    }
  }

  new SlidePresentation();
}());

/* Scrolling timeline (about-timeline layout), ported from the approved About Me prototype.
   The row in focus grows its picture under the text. Real mouse movement picks the row
   under the pointer. Wheel, keys and touch scroll the list and pick the middle row.
   After 5 s idle the list tours itself at 3.5 s per row and loops. Wheel events and
   vertical scroll keys inside the list never change slides. */
(function () {
  "use strict";
  const IDLE_MS = 5000, STEP_MS = 3500;
  const SCROLL_KEYS = new Set(["ArrowUp", "ArrowDown", "PageUp", "PageDown", "Home", "End", " "]);

  function setupTimeline(list) {
    const items = Array.from(list.querySelectorAll(".timeline-item"));
    if (!items.length) return;
    const slide = list.closest(".slide") || list;
    let cur = null, mode = "scroll", hoverTimer = 0, raf = 0, idleTimer = 0, stepTimer = 0;
    let lastX = -1, lastY = -1;
    const behavior = () => (window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth");

    function set(item) {
      if (item && item !== cur) {
        if (cur) cur.classList.remove("active");
        item.classList.add("active");
        cur = item;
      }
    }
    function reveal(item) {
      const r = list.getBoundingClientRect(), b = item.getBoundingClientRect(), pad = r.height * 0.14;
      if (b.bottom > r.bottom - pad) list.scrollBy({ top: b.bottom - (r.bottom - pad), behavior: behavior() });
      else if (b.top < r.top + 8) list.scrollBy({ top: b.top - r.top - 8, behavior: behavior() });
    }
    function pickCentre() {
      const r = list.getBoundingClientRect(), mid = r.top + r.height * 0.42;
      let best = items[0], bestDistance = Infinity;
      for (const item of items) {
        const b = item.getBoundingClientRect();
        const distance = Math.abs((b.top + b.bottom) / 2 - mid);
        if (distance < bestDistance) { bestDistance = distance; best = item; }
      }
      set(best);
    }
    function centre(item) {
      const r = list.getBoundingClientRect(), b = item.getBoundingClientRect();
      list.scrollBy({ top: (b.top + b.bottom) / 2 - (r.top + r.height * 0.42), behavior: behavior() });
    }
    const onScreen = () => {
      const r = slide.getBoundingClientRect();
      return r.top < innerHeight * 0.5 && r.bottom > innerHeight * 0.5 && !document.hidden;
    };
    function step() {
      if (mode !== "auto") return;
      if (onScreen()) {
        const next = items[(items.indexOf(cur) + 1) % items.length];
        set(next);
        if (next === items[0]) list.scrollTo({ top: 0, behavior: "instant" }); // loop: jump straight back to the start, no scroll up
        // Wait for the row to finish growing (0.3 s transition) so the scroll targets its final position.
        else setTimeout(() => { if (mode === "auto") centre(next); }, 380);
      }
      stepTimer = setTimeout(step, STEP_MS);
    }
    function wake() {
      clearTimeout(idleTimer);
      clearTimeout(stepTimer);
      if (mode === "auto") mode = "scroll";
      // Resume the tour from the row now in view, never from a row scrolled far away.
      idleTimer = setTimeout(() => { pickCentre(); mode = "auto"; step(); }, IDLE_MS);
    }

    list.addEventListener("wheel", (event) => { event.stopPropagation(); mode = "scroll"; wake(); }, { passive: true });
    list.addEventListener("keydown", (event) => {
      if (SCROLL_KEYS.has(event.key)) event.stopPropagation();
      mode = "scroll";
      wake();
    });
    list.addEventListener("touchstart", () => { mode = "scroll"; wake(); }, { passive: true });
    list.addEventListener("scroll", () => {
      if (mode !== "scroll") return;
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(pickCentre);
    }, { passive: true });

    // Only real mouse movement counts, so rows shifting under a still pointer never steal focus.
    function onPointer(event) {
      if (event.pointerType && event.pointerType !== "mouse") return;
      if (event.clientX === lastX && event.clientY === lastY) return;
      lastX = event.clientX;
      lastY = event.clientY;
      mode = "hover";
      wake();
      const item = event.target.closest(".timeline-item");
      clearTimeout(hoverTimer);
      if (!item || item === cur) return;
      hoverTimer = setTimeout(() => { set(item); setTimeout(() => reveal(item), 320); }, 40);
    }
    list.addEventListener("pointermove", onPointer);
    list.addEventListener("pointerover", onPointer);
    list.addEventListener("mousemove", onPointer);
    list.addEventListener("pointerleave", () => { clearTimeout(hoverTimer); mode = "scroll"; wake(); });

    document.addEventListener("visibilitychange", wake);
    set(items[0]);
    wake();
  }

  document.querySelectorAll(".timeline-list").forEach(setupTimeline);
}());

/* Replayable animations: an <img data-replay> SVG animation plays once each time its slide comes into view. */
(function () {
  "use strict";
  const imgs = Array.from(document.querySelectorAll("img[data-replay]"));
  if (!imgs.length || !("IntersectionObserver" in window)) return;
  const base = new Map(imgs.map((img) => [img, img.getAttribute("src").split("?")[0]]));
  const seen = new WeakSet();
  const io = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      const img = entry.target;
      if (entry.isIntersecting && entry.intersectionRatio >= 0.6) {
        if (!seen.has(img)) { seen.add(img); img.setAttribute("src", base.get(img) + "?play=" + Date.now()); }
      } else if (entry.intersectionRatio < 0.1) {
        seen.delete(img);
      }
    }
  }, { threshold: [0, 0.1, 0.6] });
  imgs.forEach((img) => io.observe(img));
})();
