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
