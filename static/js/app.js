/* Resuma.pk - minimal vanilla JS for interactivity */
(function () {
  "use strict";

  const getCookie = (name) => {
    const match = document.cookie.match(new RegExp("(^|;\\s*)" + name + "=([^;]*)"));
    return match ? decodeURIComponent(match[2]) : null;
  };

  document.addEventListener("DOMContentLoaded", function () {
    /* ---------- Sticky header shadow ---------- */
    const header = document.querySelector("[data-header]");
    if (header) {
      const onScroll = () => {
        header.classList.toggle("shadow-md", window.scrollY > 8);
        header.classList.toggle("shadow-ink-900/5", window.scrollY > 8);
      };
      window.addEventListener("scroll", onScroll, { passive: true });
      onScroll();
    }

    /* ---------- Mobile menu ---------- */
    const menuToggle = document.querySelector("[data-menu-toggle]");
    const mobileMenu = document.querySelector("[data-mobile-menu]");
    if (menuToggle && mobileMenu) {
      menuToggle.addEventListener("click", () => {
        const open = mobileMenu.classList.toggle("hidden");
        menuToggle.setAttribute("aria-expanded", String(!open));
      });
    }

    /* ---------- Toasts ---------- */
    document.querySelectorAll("[data-toast]").forEach((toast) => {
      const dismiss = toast.querySelector("[data-dismiss-toast]");
      const hide = () => toast.remove();
      dismiss && dismiss.addEventListener("click", hide);
      setTimeout(hide, 6000);
    });

    /* ---------- Modals (apply) ---------- */
    const modal = document.querySelector("[data-apply-modal]");
    const openBtn = document.querySelector("[data-open-apply]");
    const closeBtn = document.querySelector("[data-close-apply]");
    if (modal) {
      const open = () => {
        modal.classList.remove("hidden");
        modal.classList.add("flex");
        document.body.style.overflow = "hidden";
      };
      const close = () => {
        modal.classList.add("hidden");
        modal.classList.remove("flex");
        document.body.style.overflow = "";
      };
      openBtn && openBtn.addEventListener("click", open);
      closeBtn && closeBtn.addEventListener("click", close);
      modal.addEventListener("click", (e) => {
        if (e.target === modal) close();
      });
      document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") close();
      });
    }

    /* ---------- Save job (AJAX) ---------- */
    const saveBtn = document.querySelector("[data-save-job]");
    if (saveBtn) {
      saveBtn.addEventListener("click", async () => {
        try {
          const res = await fetch(saveBtn.dataset.url, {
            method: "POST",
            headers: {
              "X-CSRFToken": getCookie("csrftoken"),
              "X-Requested-With": "XMLHttpRequest",
            },
          });
          if (!res.ok) throw new Error();
          const data = await res.json();
          const icon = saveBtn.querySelector("[data-save-icon]");
          const text = saveBtn.querySelector("[data-save-text]");
          if (data.saved) {
            icon.classList.add("text-forest-600");
            icon.classList.remove("text-ink-400");
            icon.innerHTML = `<svg class="h-5 w-5" viewBox="0 0 24 24" fill="currentColor"><path d="M6.5 4.5h11a1 1 0 0 1 1 1v14l-6.5-3.75L5.5 19.5v-14a1 1 0 0 1 1-1Z"/></svg>`;
            text.textContent = "Saved";
            saveBtn.setAttribute("aria-pressed", "true");
          } else {
            icon.classList.remove("text-forest-600");
            icon.classList.add("text-ink-400");
            icon.innerHTML = `<svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8"><path stroke-linecap="round" stroke-linejoin="round" d="M6.5 4.5h11a1 1 0 0 1 1 1v14l-6.5-3.75L5.5 19.5v-14a1 1 0 0 1 1-1Z"/></svg>`;
            text.textContent = "Save job";
            saveBtn.setAttribute("aria-pressed", "false");
          }
        } catch (e) {
          window.location.href = "/login/";
        }
      });
    }

    /* ---------- Employer: toggle job status ---------- */
    document.querySelectorAll("[data-toggle-job]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        try {
          const res = await fetch(btn.dataset.url, {
            method: "POST",
            headers: {
              "X-CSRFToken": getCookie("csrftoken"),
              "X-Requested-With": "XMLHttpRequest",
            },
          });
          if (!res.ok) throw new Error();
          location.reload();
        } catch (e) {
          alert("Could not update job status. Please try again.");
        }
      });
    });

    /* ---------- Employer: delete job ---------- */
    document.querySelectorAll("[data-delete-job]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        if (!confirm(btn.dataset.confirm || "Are you sure?")) return;
        const res = await fetch(btn.dataset.url, {
          method: "POST",
          headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "X-Requested-With": "XMLHttpRequest",
          },
        });
        if (res.ok) {
          window.location.href = "/dashboard/employer/";
        } else {
          alert("Could not delete job.");
        }
      });
    });

    /* ---------- Employer: application status ---------- */
    document.querySelectorAll("[data-app-status]").forEach((select) => {
      select.addEventListener("change", async () => {
        const body = new URLSearchParams({ status: select.value });
        const res = await fetch(select.dataset.url, {
          method: "POST",
          headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "X-Requested-With": "XMLHttpRequest",
          },
          body,
        });
        if (!res.ok) alert("Could not update status.");
      });
    });

    /* ---------- Newsletter ---------- */
    const newsletter = document.querySelector("[data-newsletter]");
    if (newsletter) {
      newsletter.addEventListener("submit", (e) => {
        e.preventDefault();
        const input = newsletter.querySelector("input[type='email']");
        const btn = newsletter.querySelector("button");
        btn.textContent = "Subscribed ✓";
        btn.classList.add("!bg-forest-500", "!text-white");
        input.value = "";
      });
    }
  });
})();