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

- [ ] **Navigation & Branding:**
  - Header/Navbar must feature a clean brand name (e.g., `BrandName` or `DevStudio`) or an icon logo.
  - **STRICT RULE:** Do NOT use lab internal names, day counts, or exercise numbers (e.g., "Day 14", "Lab 9", "Assignment") as the visible logo or brand text in the header.
- [ ] **Typography & Layout:**
  - Clean layout with centered container, modern sans-serif fonts, and soft padding/spacing.
  - No raw unstyled HTML default elements.
- [ ] **Theme Functionality:**
  - Toggle switch in the header top-right corner.
  - Inverts background colors, text colors, and card borders dynamically.
  - Saves choice to `localStorage`.

## 4. Out of Scope

- Auto-detecting system OS theme preference (`prefers-color-scheme`) is strictly excluded.
- No additional color themes (such as Sepia, Solarized, or Blue) beyond Light and Dark modes.
- No complex 3D CSS animations or heavy JavaScript transition libraries.
- No third-party CSS frameworks (e.g., Bootstrap, Tailwind CSS).
- Internal project metadata or lab tracking titles inside the public UI header.

## 5. Spec Change Log

- 2026-08-26: Initial spec created for Day 14 Lab 9 task.
- 2026-08-26: Added strict naming convention rules for Header/Logo to prevent internal metadata (e.g., "Day 14") from appearing as brand text.
