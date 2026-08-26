const THEME_STORAGE_KEY = "luma-theme";
const themeToggle = document.querySelector("[data-theme-toggle]");
const themeIcon = document.querySelector("[data-theme-icon]");
const themeLabel = document.querySelector("[data-theme-label]");

function getSavedTheme() {
  const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);
  return savedTheme === "dark" ? "dark" : "light";
}

function updateTheme(theme) {
  const isDarkMode = theme === "dark";

  document.documentElement.dataset.theme = theme;
  themeIcon.textContent = isDarkMode ? "🌙" : "☀️";
  themeLabel.textContent = isDarkMode ? "Dark Mode" : "Light Mode";
  themeToggle.setAttribute(
    "aria-label",
    isDarkMode ? "Switch to light mode" : "Switch to dark mode",
  );
  themeToggle.setAttribute("aria-pressed", String(isDarkMode));
}

if (themeToggle && themeIcon && themeLabel) {
  let activeTheme = getSavedTheme();
  updateTheme(activeTheme);

  themeToggle.addEventListener("click", () => {
    activeTheme = activeTheme === "light" ? "dark" : "light";
    updateTheme(activeTheme);
    localStorage.setItem(THEME_STORAGE_KEY, activeTheme);
  });
}
