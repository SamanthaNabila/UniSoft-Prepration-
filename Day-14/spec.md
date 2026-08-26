# Feature Spec: Light / Dark Mode Toggle

## 1. Goal

Implement a clean Light / Dark Mode toggle feature for a landing page. The user should be able to click a toggle switch to invert the theme, dynamically changing both the background color and font colors while retaining their preference across page reloads.

## 2. Technical Scope & Architecture

- **Tech Stack:** HTML5, CSS3 (using CSS Variables), Pure JavaScript (DOM Manipulation & LocalStorage).
- **File Structure:**
  - `index.html` (Semantic HTML layout & section structure)
  - `style.css` (Theme CSS Variables, dynamic font/background color rules, layout styling)
  - `script.js` (Toggle event listeners, DOM state changes, LocalStorage management)

## 3. Acceptance Criteria

- [ ] A visible Toggle Switch / Button is present on the UI showing the current active theme mode.
- [ ] Clicking the toggle dynamically swaps the page background color and font colors to match the selected mode.
- [ ] High contrast and legibility are maintained for text in both Light and Dark modes.
- [ ] The toggle icon and label text (e.g., Sun ☀️ / Moon 🌙) dynamically change based on the active theme.
- [ ] User theme preference is saved in `localStorage` so the mode persists upon page refreshes.
- [ ] On initial page load, the app checks `localStorage`; if no saved state exists, it defaults to Light Mode.

## 4. Out of Scope

- Auto-detecting system OS theme preference (`prefers-color-scheme`) is strictly excluded.
- No additional color themes (such as Sepia, Solarized, or Blue) beyond Light and Dark modes.
- No complex 3D CSS animations or heavy JavaScript transition libraries.
- No third-party CSS frameworks (e.g., Bootstrap, Tailwind CSS).

## 5. Spec Change Log

- 2026-08-26: Initial spec created for Day 14 Lab 9 task.
