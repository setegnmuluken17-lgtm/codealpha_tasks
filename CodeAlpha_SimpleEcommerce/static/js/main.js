window.addEventListener("load", () => {
  const loader = document.querySelector("[data-loader]");
  if (loader) setTimeout(() => loader.remove(), 450);
});

const root = document.documentElement;
const toggle = document.querySelector("[data-theme-toggle]");
const savedTheme = localStorage.getItem("theme");
if (savedTheme) root.dataset.theme = savedTheme;
const savedBg = localStorage.getItem("bg-choice");
if (savedBg && savedBg !== "default") root.dataset.bg = savedBg;
const setThemeIcon = () => {
  if (!toggle) return;
  toggle.innerHTML = root.dataset.theme === "dark" ? '<i class="fa-solid fa-sun"></i>' : '<i class="fa-solid fa-moon"></i>';
};
setThemeIcon();
if (toggle) toggle.addEventListener("click", () => {
  root.dataset.theme = root.dataset.theme === "dark" ? "light" : "dark";
  localStorage.setItem("theme", root.dataset.theme);
  setThemeIcon();
});

const bgButtons = document.querySelectorAll("[data-bg-choice]");
const setActiveBg = () => {
  const current = root.dataset.bg || "default";
  bgButtons.forEach(button => {
    button.classList.toggle("active", button.dataset.bgChoice === current);
  });
};
bgButtons.forEach(button => {
  button.addEventListener("click", () => {
    const choice = button.dataset.bgChoice;
    if (choice === "default") {
      delete root.dataset.bg;
      localStorage.removeItem("bg-choice");
    } else {
      root.dataset.bg = choice;
      localStorage.setItem("bg-choice", choice);
    }
    setActiveBg();
    const picker = button.closest(".bg-picker");
    if (picker) picker.removeAttribute("open");
  });
});
setActiveBg();

const menuToggle = document.querySelector("[data-menu-toggle]");
const nav = document.querySelector("[data-nav]");
if (menuToggle && nav) menuToggle.addEventListener("click", () => nav.classList.toggle("open"));

const profileToggle = document.querySelector("[data-profile-toggle]");
const profileDropdown = document.querySelector("[data-profile-dropdown]");
if (profileToggle && profileDropdown) profileToggle.addEventListener("click", () => profileDropdown.classList.toggle("open"));

const searchInput = document.querySelector("[data-search-input]");
const suggestions = document.querySelector("[data-suggestions]");
if (searchInput && suggestions) {
  searchInput.addEventListener("input", async () => {
    const q = searchInput.value.trim();
    if (q.length < 2) { suggestions.style.display = "none"; suggestions.innerHTML = ""; return; }
    const res = await fetch(`${searchInput.dataset.suggestionsUrl}?q=${encodeURIComponent(q)}`);
    const data = await res.json();
    suggestions.innerHTML = data.results.map(item => `<a href="/products/${item.id}/">${item.name}</a>`).join("");
    suggestions.style.display = data.results.length ? "block" : "none";
  });
}

document.querySelectorAll("[data-thumb]").forEach(button => {
  button.addEventListener("click", () => {
    const main = document.querySelector("[data-main-image]");
    if (main) main.src = button.dataset.thumb;
  });
});

const countdown = document.querySelector("[data-countdown]");
if (countdown) {
  const end = Date.now() + 1000 * 60 * 60 * 24;
  setInterval(() => {
    const diff = Math.max(0, end - Date.now());
    const d = Math.floor(diff / 86400000);
    const h = Math.floor(diff / 3600000) % 24;
    const m = Math.floor(diff / 60000) % 60;
    const s = Math.floor(diff / 1000) % 60;
    countdown.innerHTML = [d, h, m, s].map(v => `<span>${String(v).padStart(2, "0")}</span>`).join("");
  }, 1000);
}

const testimonials = document.querySelectorAll("[data-testimonials] article");
let testimonialIndex = 0;
if (testimonials.length) setInterval(() => {
  testimonials[testimonialIndex].classList.remove("active");
  testimonialIndex = (testimonialIndex + 1) % testimonials.length;
  testimonials[testimonialIndex].classList.add("active");
}, 3200);

const backTop = document.querySelector("[data-back-top]");
if (backTop) {
  window.addEventListener("scroll", () => backTop.classList.toggle("show", window.scrollY > 500));
  backTop.addEventListener("click", () => window.scrollTo({top: 0, behavior: "smooth"}));
}

const pass1 = document.querySelector("#id_password1");
const pass2 = document.querySelector("#id_password2");
if (pass1 && pass2) {
  const check = () => pass2.classList.toggle("password-match", pass1.value && pass1.value === pass2.value);
  pass1.addEventListener("input", check);
  pass2.addEventListener("input", check);
}

const registerForm = document.querySelector("[data-register-form]");
if (registerForm) {
  const email = registerForm.querySelector("[data-register-email]");
  const password = registerForm.querySelector("[data-register-password]");
  const confirmPassword = registerForm.querySelector("[data-register-confirm]");
  const emailError = registerForm.querySelector("[data-email-error]");
  const confirmSuccess = registerForm.querySelector("[data-confirm-success]");
  const rules = {
    length: registerForm.querySelector("[data-rule='length']"),
    upper: registerForm.querySelector("[data-rule='upper']"),
    lower: registerForm.querySelector("[data-rule='lower']"),
    number: registerForm.querySelector("[data-rule='number']"),
    special: registerForm.querySelector("[data-rule='special']"),
  };

  const setRule = (key, ok) => {
    if (!rules[key]) return;
    rules[key].classList.toggle("ok", ok);
    const icon = rules[key].querySelector("span");
    if (icon) icon.textContent = ok ? "✓" : "×";
  };

  const validateEmail = () => {
    if (!email || !emailError) return;
    const value = email.value.trim();
    const ok = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
    email.classList.toggle("input-invalid", value.length > 0 && !ok);
    email.classList.toggle("input-valid", value.length > 0 && ok);
    emailError.textContent = value.length > 0 && !ok ? "Invalid email format." : "";
  };

  const validatePassword = () => {
    if (!password) return;
    const value = password.value;
    const checks = {
      length: value.length >= 8 && value.length <= 64,
      upper: /[A-Z]/.test(value),
      lower: /[a-z]/.test(value),
      number: /\d/.test(value),
      special: /[^A-Za-z0-9]/.test(value),
    };
    Object.entries(checks).forEach(([key, ok]) => setRule(key, ok));
    const allValid = Object.values(checks).every(Boolean);
    password.classList.toggle("input-valid", value.length > 0 && allValid);
    password.classList.toggle("input-invalid", value.length > 0 && !allValid);
    return allValid;
  };

  const validateConfirm = () => {
    if (!password || !confirmPassword) return;
    const ok = password.value.length > 0 && password.value === confirmPassword.value;
    confirmPassword.classList.toggle("password-match", ok);
    confirmPassword.classList.toggle("input-invalid", confirmPassword.value.length > 0 && !ok);
    if (confirmSuccess) confirmSuccess.textContent = ok ? "Passwords match." : "";
  };

  if (email) email.addEventListener("input", validateEmail);
  if (password) password.addEventListener("input", () => { validatePassword(); validateConfirm(); });
  if (confirmPassword) confirmPassword.addEventListener("input", validateConfirm);
  validateEmail();
  validatePassword();
  validateConfirm();
}
