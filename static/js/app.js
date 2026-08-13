/* Resuma.pk — minimal vanilla JS for interactivity */
(function () {
  "use strict";

  const getCookie = (name) => {
    const match = document.cookie.match(new RegExp("(^|;\\s*)" + name + "=([^;]*)"));
    return match ? decodeURIComponent(match[2]) : null;
  };

  const ICON_BOOKMARK = `<svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8"><path stroke-linecap="round" stroke-linejoin="round" d="M6.5 4.5h11a1 1 0 0 1 1 1v14l-6.5-3.75L5.5 19.5v-14a1 1 0 0 1 1-1Z"/></svg>`;
  const ICON_BOOKMARK_FILLED = `<svg class="h-5 w-5" viewBox="0 0 24 24" fill="currentColor"><path d="M6.5 4.5h11a1 1 0 0 1 1 1v14l-6.5-3.75L5.5 19.5v-14a1 1 0 0 1 1-1Z"/></svg>`;

  function postJSON(url, body) {
    return fetch(url, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams(body),
    });
  }

  function toast(message, type) {
    const wrap = document.createElement("div");
    wrap.className = "fixed inset-x-0 bottom-5 z-[60] flex justify-center px-4 pointer-events-none";
    wrap.innerHTML =
      `<div class="pointer-events-auto card flex items-center gap-3 border-l-4 px-4 py-3 text-sm shadow-lg ` +
      (type === "error" ? "border-l-red-500" : "border-l-forest-600") +
      `"><span class="inline-flex h-2 w-2 rounded-full ` +
      (type === "error" ? "bg-red-500" : "bg-forest-600") +
      `"></span><span class="text-ink-800">${message}</span></div>`;
    document.body.appendChild(wrap);
    setTimeout(() => wrap.remove(), 4000);
  }

  document.addEventListener("DOMContentLoaded", function () {
    /* ---------- Sticky header shadow + active nav ---------- */
    const header = document.querySelector("[data-header]");
    if (header) {
      const onScroll = () => header.classList.toggle("shadow-md", window.scrollY > 8);
      window.addEventListener("scroll", onScroll, { passive: true });
      onScroll();
    }
    const path = location.pathname;
    document.querySelectorAll(".nav-link").forEach((a) => {
      const href = a.getAttribute("href");
      if (href && path === href) {
        a.classList.add("nav-link-active");
        a.setAttribute("aria-current", "page");
      }
    });

    /* ---------- Mobile menu (slide-in) ---------- */
    const menuToggle = document.querySelector("[data-menu-toggle]");
    const mobileMenu = document.querySelector("[data-mobile-menu]");
    if (menuToggle && mobileMenu) {
      menuToggle.addEventListener("click", () => {
        const open = mobileMenu.classList.toggle("hidden");
        menuToggle.setAttribute("aria-expanded", String(!open));
      });
      mobileMenu.querySelectorAll("a").forEach((a) =>
        a.addEventListener("click", () => {
          mobileMenu.classList.add("hidden");
          menuToggle.setAttribute("aria-expanded", "false");
        })
      );
    }

    /* ---------- Scroll reveal ---------- */
    const revealEls = document.querySelectorAll(".reveal");
    if ("IntersectionObserver" in window && revealEls.length) {
      const io = new IntersectionObserver(
        (entries) => {
          entries.forEach((e) => {
            if (e.isIntersecting) {
              e.target.classList.add("revealed");
              io.unobserve(e.target);
            }
          });
        },
        { threshold: 0.08, rootMargin: "0px 0px -40px 0px" }
      );
      revealEls.forEach((el) => io.observe(el));
    } else {
      revealEls.forEach((el) => el.classList.add("revealed"));
    }

    /* ---------- Toasts (server-rendered messages) ---------- */
    document.querySelectorAll("[data-toast]").forEach((t) => {
      const hide = () => t.remove();
      t.querySelector("[data-dismiss-toast]")?.addEventListener("click", hide);
      setTimeout(hide, 6000);
    });

    /* ---------- Apply modal ---------- */
    const modal = document.querySelector("[data-apply-modal]");
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
      document.querySelector("[data-open-apply]")?.addEventListener("click", open);
      document.querySelector("[data-close-apply]")?.addEventListener("click", close);
      modal.addEventListener("click", (e) => e.target === modal && close());
      document.addEventListener("keydown", (e) => e.key === "Escape" && close());
    }

    /* ---------- Save job (AJAX, multi-button) ---------- */
    document.querySelectorAll("[data-save-job]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        if (!getCookie("sessionid") && !getCookie("csrftoken")) {
          window.location.href = "/login/?next=" + encodeURIComponent(location.pathname);
          return;
        }
        const icon = btn.querySelector("svg");
        try {
          const res = await postJSON(btn.dataset.url, {});
          if (!res.ok) throw new Error();
          const data = await res.json();
          btn.setAttribute("aria-pressed", String(data.saved));
          btn.querySelector("svg").outerHTML = data.saved ? ICON_BOOKMARK_FILLED : ICON_BOOKMARK;
          btn.querySelector("svg").classList.add("text-forest-600");
          toast(data.saved ? "Job saved to your dashboard." : "Removed from saved jobs.");
        } catch (e) {
          toast("Please sign in to save jobs.", "error");
        }
      });
    });

    /* ---------- Employer: toggle job status ---------- */
    document.querySelectorAll("[data-toggle-job]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        try {
          const res = await postJSON(btn.dataset.url, {});
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
        const res = await postJSON(btn.dataset.url, {});
        if (res.ok) window.location.href = "/dashboard/employer/";
        else alert("Could not delete job.");
      });
    });

    /* ---------- Employer: application status ---------- */
    document.querySelectorAll("[data-app-status]").forEach((select) => {
      select.addEventListener("change", async () => {
        const res = await postJSON(select.dataset.url, { status: select.value });
        if (res.ok) toast("Applicant status updated.");
        else alert("Could not update status.");
      });
    });

    /* ---------- Share / copy link ---------- */
    document.querySelectorAll("[data-share]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        try {
          await navigator.clipboard.writeText(location.href);
          toast("Link copied to clipboard.");
        } catch (e) {
          toast("Could not copy link.", "error");
        }
      });
    });

    /* ---------- Newsletter / job alerts (AJAX) ---------- */
    document.querySelectorAll("[data-newsletter]").forEach((form) => {
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const input = form.querySelector("input[type='email']");
        const btn = form.querySelector("button");
        const res = await postJSON("/alerts/subscribe/", { email: input.value });
        const data = await res.json().catch(() => ({}));
        if (res.ok && data.ok) {
          toast(data.message || "Subscribed!");
          input.value = "";
          btn.innerHTML = "✓";
        } else {
          toast(data.message || "Please enter a valid email.", "error");
        }
      });
    });

    /* ---------- Live filtering (auto-submit on change) ---------- */
    const filterForm = document.querySelector("[data-filter-form]");
    if (filterForm) {
      filterForm.querySelectorAll("select, input").forEach((el) => {
        el.addEventListener("change", () => {
          const results = document.querySelector("[data-results]");
          if (results) results.classList.add("opacity-40", "pointer-events-none");
          filterForm.requestSubmit ? filterForm.requestSubmit() : filterForm.submit();
        });
      });
    }
  });
})();
