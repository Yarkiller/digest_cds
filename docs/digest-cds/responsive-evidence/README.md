# Responsive evidence (homework Step 6)

Screenshots captured by Playwright during `tests/web-app.spec.js` (`web app responsive`).

| File | Viewport | Page |
|------|----------|------|
| `mobile-320-issue.png` | 320×568 | `/` |
| `mobile-390-issue.png` | 390×844 | `/` |
| `mobile-390-voting.png` | 390×844 | `/voting` |
| `desktop-1280-issue.png` | 1280×800 | `/` |

Assertions: no horizontal overflow; mobile hides «Мария Сидорова»; desktop shows identity + wider search; voting confirm stays in viewport on phone.
