document.addEventListener('DOMContentLoaded', () => {
  // --- Sidebar Toggle ---
  const sidebar = document.getElementById('appSidebar');
  const sidebarToggle = document.getElementById('sidebarToggle');
  const mobileMenuBtn = document.getElementById('mobileMenuBtn');
  const sidebarBackdrop = document.getElementById('sidebarBackdrop');

  // Desktop collapse
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
      // Save preference to localStorage if desired
    });
  }

  // Mobile overlay
  if (mobileMenuBtn && sidebar && sidebarBackdrop) {
    const toggleMobileMenu = () => {
      sidebar.classList.toggle('mobile-open');
      sidebarBackdrop.classList.toggle('active');
      document.body.style.overflow = sidebar.classList.contains('mobile-open') ? 'hidden' : '';
    };

    mobileMenuBtn.addEventListener('click', toggleMobileMenu);
    sidebarBackdrop.addEventListener('click', toggleMobileMenu);
  }

  // --- Dialogs ---
  document.querySelectorAll("[data-dialog-target]").forEach((trigger) => {
    trigger.addEventListener("click", () => {
      const dialog = document.getElementById(trigger.dataset.dialogTarget);
      if (dialog) {
        dialog.showModal();
      }
    });
  });

  document.querySelectorAll(".dialog-close").forEach((button) => {
    button.addEventListener("click", () => {
      const dialog = button.closest("dialog");
      if (dialog) {
        dialog.close();
      }
    });
  });

  document.querySelectorAll(".preview-dialog").forEach((dialog) => {
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) {
        dialog.close();
      }
    });
  });

  // --- Copy Buttons ---
  document.querySelectorAll(".copy-button").forEach((button) => {
    button.addEventListener("click", async () => {
      const textarea = button.closest(".copy-block").querySelector("textarea");
      if (textarea) {
        await navigator.clipboard.writeText(textarea.value);
        const originalText = button.textContent;
        button.textContent = "Copied!";
        button.classList.add("btn-success");
        button.classList.remove("btn-outline-secondary");
        setTimeout(() => {
          button.textContent = originalText;
          button.classList.remove("btn-success");
          button.classList.add("btn-outline-secondary");
        }, 1200);
      }
    });
  });

  // --- Entrance Animations (Intersection Observer) ---
  const animateElements = document.querySelectorAll('.panel, .persona-card, .media-card, .review-card, .profile-media-card');
  
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.animation = `fadeInUp 0.5s ease forwards`;
          observer.unobserve(entry.target);
        }
      });
    }, {
      rootMargin: '0px 0px -40px 0px',
      threshold: 0.1
    });

    animateElements.forEach((el, index) => {
      // Set initial state for animation
      el.style.opacity = '0';
      el.style.transform = 'translateY(16px)';
      // Stagger slightly based on order in DOM if they appear together
      el.style.animationDelay = `${(index % 10) * 0.05}s`;
      observer.observe(el);
    });
  } else {
    // Fallback if no observer
    animateElements.forEach(el => {
      el.style.opacity = '1';
      el.style.transform = 'none';
    });
  }
});
