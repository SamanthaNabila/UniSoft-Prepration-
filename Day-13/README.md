# 🧪 LAB REPORT 8: AI Coding Behavior Evaluation
> **Topic:** Evaluating AI Coding Performance With vs. Without Repository Context (`CLAUDE.md`)

---

## 📌 1. Title & Objective

- **Course / Subject:** Software Engineering / AI-Assisted Development
- **Project:** Full-Stack Task Manager (Express.js & PostgreSQL)
- **Objective:** Quantify how explicitly defined repository context (`CLAUDE.md`) influences AI-generated code quality, pattern compliance, and scope creep suppression.

---

## 🔴 2. Baseline Trial (Without Context)

In the initial run without any repository context or custom guidelines, the AI model relied on default code heuristics:
- ❌ **Validation Pattern:** Implemented inline helper validation functions inside route handlers.
- ❌ **Documentation:** Completely omitted JSDoc comments across API endpoints.
- ❌ **Scope Creep:** Added unrequested features (Idempotent `ALTER TABLE` SQL migration script & UI priority badges).
- ❌ **Code Uniformity:** Mixed standard function declarations with ES6 arrow functions.

---

## 🟢 3. Context-Aware Trial (With `CLAUDE.md`)

After creating a governing `CLAUDE.md` file with explicit conventions, the AI agent executed identical tasks with 100% compliance:
- ✅ **Architectural Alignment:** Extracted input validation into reusable Express Middleware (`validateTodoBody`, `validateFilterQuery`).
- ✅ **Strict Documentation:** Added structured JSDoc comment blocks above every API route handler.
- ✅ **Scope Suppression:** Omitted unrequested SQL scripts and UI badges per strict rules.
- ✅ **Error Standard:** Enforced uniform JSON error payload schema: `{"error": "Message"}`.
- ✅ **Syntax Standard:** Standardized all handlers to use ES6 Arrow Functions (`const handler = ...`).

---

## 📊 4. Comparative Evaluation Table

| Evaluation Metric | Baseline Trial (No Context) | Context-Aware Trial (`CLAUDE.md`) |
| :--- | :--- | :--- |
| **Input Validation** | 🔴 Non-standard: Inline helper functions | 🟢 Standardized: Express Middleware |
| **API Documentation** | 🔴 Missing: Omitted completely | 🟢 Complete: Full JSDoc blocks |
| **Scope Control** | 🔴 Scope Creep: Unrequested SQL & Badges | 🟢 Strict Scope: Zero unrequested additions |
| **Error Format** | 🔴 Inconsistent: Mixed text formats | 🟢 Strict JSON: `{"error": "Message"}` |
| **Code Style** | 🔴 Mixed: Traditional & Arrow syntax | 🟢 Uniform: 100% Arrow Functions |

---

## 🎯 5. Conclusion

> 💡 **Key Takeaway:** Providing explicit repository context via a `CLAUDE.md` file acts as an automated architectural guardrail. It drastically reduces architectural drift, enforces code quality, and eliminates unrequested feature bloat in AI-assisted development.
