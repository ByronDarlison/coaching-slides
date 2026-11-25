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
      this.settleDeepLink();
    }

    // A link to a later slide is followed before the pictures above it have loaded.
    // Each picture that arrives moves the page, so keep the linked slide at the top
    // until the page has loaded or the reader starts to move.
    settleDeepLink() {
      const target = this.currentSlide;
      if (!target) return;
      let settled = false;
      const align = () => {
        if (!settled) this.slides[target].scrollIntoView({ behavior: "instant", block: "start" });
      };
      const stop = () => {
        if (settled) return;
        settled = true;
        this.viewportSettling = false;
        document.removeEventListener("load", align, true);
      };
      this.viewportSettling = true;
      document.addEventListener("load", align, true);
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(align);
      window.addEventListener("load", () => { align(); requestAnimationFrame(() => { align(); stop(); }); });
      ["wheel", "touchstart", "keydown", "pointerdown"].forEach((type) => {
        window.addEventListener(type, stop, { once: true, passive: true, capture: true });
      });
    }

    // A link names a slide (#bhag-what-is) so it survives slides being added or cut.
    // The older numeric form (#slide-30) still works.
    hashIndex(hash) {
      const match = hash.match(/^#slide-(\d+)$/);
      if (match) return Math.max(0, Math.min(Number(match[1]) - 1, this.slides.length - 1));
      const name = decodeURIComponent(hash.slice(1));
      const found = name ? this.slides.findIndex((slide) => slide.dataset && slide.dataset.name === name) : -1;
      return found < 0 ? 0 : found;
    }

    slideHash(index) {
      const slide = this.slides[index];
      const name = slide && slide.dataset && slide.dataset.name;
      return "#" + (name || "slide-" + (index + 1));
    }

    goToHash() {
      this.goTo(this.hashIndex(window.location.hash), false);
    }

    goTo(index, smooth) {
      if (index < 0 || index >= this.slides.length) return;
      this.currentSlide = index;
      this.slides[index].scrollIntoView({ behavior: smooth && !window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "smooth" : "instant", block: "start" });
      history.replaceState(null, "", this.slideHash(index));
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
            history.replaceState(null, "", this.slideHash(selected));
            this.updateInterface();
          }
        });
      }, { passive: true, capture: true });
      window.addEventListener("hashchange", () => this.goToHash());
    }

    setupKeyboardNavigation() {
      document.addEventListener("keydown", (event) => {
        if (event.target.closest("input, textarea, select, [contenteditable=true]")) return;
        if (document.body.classList.contains("art-zoom-open")) return;
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
        if (event.target.closest(".notes-panel, .slide-sidebar, .controls, .art-zoom")) return;
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
      // A finger or a pen never hovers, so the first touch keeps the controls on screen.
      const touched = (event) => {
        if (event.pointerType && event.pointerType === "mouse") return;
        document.body.classList.add("touch-input");
      };
      document.addEventListener("touchstart", touched, { passive: true });
      document.addEventListener("pointerdown", touched, { passive: true });
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

// On a small screen a large drawing is too small to read in place. Tapping it opens
// a zoom view inside the deck: the drawing at a readable width, scrolling in both
// directions, with its definitions and a Close button. Photos and the deck QR code
// are not drawings and do not zoom.
(() => {
  const small = window.matchMedia("(max-width: 899px), (max-height: 599px)");
  let view = null;
  let opener = null;

  function drawing(target) {
    // The whole panel is the tap target: definition areas cover much of a drawing.
    // A link on the drawing opens its address; it never opens the zoom view as well.
    if (target && target.closest && target.closest("a[href]")) return null;
    const panel = target && target.closest ? target.closest(".story-panel--art") : null;
    const img = panel ? panel.querySelector("img") : null;
    if (!img) return null;
    if (!/\.svg(\?|$)/.test(img.getAttribute("src") || "")) return null;
    if (img.closest(".story-frame--fit") || img.closest("[data-deck-qr]")) return null;
    return img;
  }

  function close() {
    if (!view) return;
    view.remove();
    view = null;
    document.body.classList.remove("art-zoom-open");
    if (opener && opener.focus) opener.focus({ preventScroll: true });
    opener = null;
  }

  function button(label, text, onClick) {
    const control = document.createElement("button");
    control.type = "button";
    control.className = "art-zoom-button";
    control.setAttribute("aria-label", label);
    control.textContent = text;
    control.addEventListener("click", onClick);
    return control;
  }

  function open(img) {
    close();
    const slide = img.closest(".slide");
    const source = img.closest(".art-hot") || img;
    const copy = source.cloneNode(true);
    // A copied dimming mask needs its own id, or two masks in the page share one.
    copy.querySelectorAll("mask[id]").forEach((mask) => {
      const id = mask.id + "-zoom";
      copy.querySelectorAll('[mask="url(#' + mask.id + ')"]').forEach((user) => user.setAttribute("mask", "url(#" + id + ")"));
      mask.id = id;
    });
    copy.querySelectorAll("img[data-replay]").forEach((picture) => picture.removeAttribute("data-replay"));
    if (copy.matches && copy.matches("img[data-replay]")) copy.removeAttribute("data-replay");

    view = document.createElement("div");
    view.className = "art-zoom";
    view.setAttribute("role", "dialog");
    view.setAttribute("aria-modal", "true");
    view.setAttribute("aria-label", "Drawing, enlarged");
    const bar = document.createElement("div");
    bar.className = "art-zoom-bar";
    const title = document.createElement("p");
    title.className = "art-zoom-title";
    title.textContent = (slide && slide.dataset && slide.dataset.title) || "";
    const scroll = document.createElement("div");
    scroll.className = "art-zoom-scroll";
    scroll.tabIndex = 0;
    const canvas = document.createElement("div");
    canvas.className = "art-zoom-canvas";
    canvas.appendChild(copy);
    scroll.appendChild(canvas);

    // Start wide enough to read: about two thirds of the drawing's own size.
    const natural = img.naturalWidth > 400 ? img.naturalWidth : window.innerWidth * 2.5;
    const fit = Math.max(280, window.innerWidth - 24);
    const most = Math.max(fit, natural * 2);
    let width = Math.max(fit, Math.min(natural * 0.65, 1400));
    const smaller = button("Zoom out", "\u2212", () => resize(width / 1.3));
    const larger = button("Zoom in", "+", () => resize(width * 1.3));
    const done = button("Close the enlarged drawing", "Close", close);
    function resize(next) {
      width = Math.min(most, Math.max(fit, next));
      canvas.style.width = Math.round(width) + "px";
      smaller.disabled = width <= fit;
      larger.disabled = width >= most;
    }
    resize(width);

    bar.append(title, smaller, larger, done);
    view.append(bar, scroll);
    document.body.appendChild(view);
    document.body.classList.add("art-zoom-open");
    opener = img.closest("[tabindex]") || document.activeElement;
    done.focus({ preventScroll: true });
  }

  document.addEventListener("click", (event) => {
    if (!small.matches || (view && view.contains(event.target))) return;
    const img = drawing(event.target);
    if (img) open(img);
  });
  document.addEventListener("keydown", (event) => {
    if (view && event.key === "Escape") { event.stopPropagation(); close(); }
  }, true);
  // A definition opened by touch is a sheet fixed to the screen. Put it away when the
  // reader scrolls or touches anything else, so it never follows them down the deck.
  const putAway = (event) => {
    if (!small.matches) return;
    const holder = document.activeElement && document.activeElement.closest ? document.activeElement.closest(".hotspot, .term") : null;
    if (!holder) return;
    if (event.type === "touchstart" && event.target.closest && event.target.closest(".hotspot, .term") === holder) return;
    holder.blur();
  };
  document.addEventListener("scroll", putAway, { passive: true, capture: true });
  document.addEventListener("touchstart", putAway, { passive: true, capture: true });
  // Keep a term's definition inside the slide: shift it sideways when the term sits near an edge.
  const fitTip = (event) => {
    if (small.matches) return;
    const term = event.target && event.target.closest ? event.target.closest(".term") : null;
    if (!term) {
      // A hover box on a drawing: keep it inside the drawing's panel, which clips it.
      const spot = event.target && event.target.closest ? event.target.closest(".hotspot") : null;
      const spotTip = spot ? spot.querySelector(":scope > .hotspot-tip") : null;
      const panel = spot ? spot.closest(".story-panel--art") || spot.closest(".slide-content") || spot.closest(".slide") : null;
      if (!spotTip || !panel) return;
      spotTip.style.setProperty("--tip-dx", "0px");
      const edge = panel.getBoundingClientRect(), at = spotTip.getBoundingClientRect(), inset = 8;
      let shift = 0;
      if (at.left < edge.left + inset) shift = edge.left + inset - at.left;
      else if (at.right > edge.right - inset) shift = edge.right - inset - at.right;
      spotTip.style.setProperty("--tip-dx", shift + "px");
      return;
    }
    const tip = term.querySelector(".hotspot-tip");
    const frame = term.closest(".slide-content") || term.closest(".slide");
    if (!tip || !frame) return;
    tip.style.setProperty("--tip-dx", "0px");
    // Open above the word when there is room, and below it when there is not (a title has none above).
    // A picture in the box shrinks to the room on the side it opens, so the box never leaves the slide.
    term.classList.remove("term--below");
    tip.style.removeProperty("--img-room");
    const box = frame.getBoundingClientRect(), pad = 12, gap = 10;
    const word = term.getBoundingClientRect(), full = tip.getBoundingClientRect().height;
    const above = word.top - box.top - pad - gap, below = box.bottom - word.bottom - pad - gap;
    const under = full > above && below > above;
    if (under) term.classList.add("term--below");
    const picture = tip.querySelector(".term-image");
    const room = under ? below : above;
    // A smaller picture makes a narrower box, whose text may wrap onto more lines: measure again, a few times at most.
    for (let pass = 0; picture && pass < 4; pass += 1) {
      const tall = tip.getBoundingClientRect().height;
      if (tall <= room) break;
      const chrome = tall - picture.getBoundingClientRect().height;
      tip.style.setProperty("--img-room", Math.max(80, Math.floor(room - chrome)) + "px");
    }
    const r = tip.getBoundingClientRect();
    let dx = 0;
    if (r.left < box.left + pad) dx = box.left + pad - r.left;
    else if (r.right > box.right - pad) dx = box.right - pad - r.right;
    tip.style.setProperty("--tip-dx", dx + "px");
  };
  document.addEventListener("mouseover", fitTip, true);
  document.addEventListener("focusin", fitTip, true);
  // Leaving the small-screen layout closes the view, so it never covers the stage.
  const leave = () => { if (!small.matches) close(); };
  if (small.addEventListener) small.addEventListener("change", leave);
})();
