---
trigger: always_on
---

# AI Assistant Rules & Guidelines (Antigravity IDE)

## 1. Project Context

You are assisting in a 24-hour hackathon to build the Carmel Kinneret Trail App. Time is of the essence. Code must be robust, generic, scalable, and work exactly as intended on the first run. No over-engineering, but no sloppy shortcuts that break later.

## 2. Tech Stack

- **Client**: React Native (Expo), TypeScript, Maplibre GL Native, Clerk for Auth.
- **Server**: FastAPI, Python, SQLAlchemy (async), PostgreSQL.

## 3. Coding Standards

- **Zero Fluff**: Do not apologize. Do not output conversational filler. Output the code, explain only what is necessary for implementation.
- **Type Safety**: Strictly type all TypeScript and Python (using Pydantic). No `any` types.
- **Clean Architecture**: Keep routing, business logic, and database operations separated.
- **Scalability**: Write generic helper functions for repetitive tasks (e.g., handling spatial JSON data, Clerk auth extraction).

## 4. UI/UX & Design Language: "Clarified Air"

All frontend components must strictly adhere to the "Clarified Air" design system. The app should feel **clean, minimal, rounded, lightweight, and inviting**, allowing the outdoor content to be the focal point.

- **Floating Layout**: UI elements like bottom navigation bars, turn-by-turn instruction cards, and action buttons must float above the map layer without touching the screen edges.
- **Soft Geometry**: Use aggressive rounding. Navigation bars and buttons should be full pill shapes (`borderRadius: 9999`), and feed/content cards should use large border radii (`16px` to `20px`).
- **Weightlessness (Diffuse Shadows)**: UI elements should feel light. Use subtle drop-shadows with low opacity (e.g., `0.05` to `0.08`) and high blur/radius to lift elements gently off the map or background. Avoid harsh, solid borders.
- **Heavy Whitespace**: Give elements ample room to breathe. Maintain consistent, generous padding and margins. Do not cram components or text.
- **Purposeful Palette**: Use a pristine off-white/white base (`#F8F9FA` for backgrounds, `#FFFFFF` for floating surfaces). Reserve colors strictly for utility and hierarchy: Leaf-green (`#48BB78`) for routes and navigation, deep water-blue (`#3182CE`) for markers and active tabs, and subtle red (`#E53E3E`) for likes and destructive actions.

## 5. Documentation Mandate (CRITICAL)

For **every** major feature, architectural decision, or significant change, you MUST generate or update a Markdown file in the `docs/` directory.

- These files must be compatible with **Docusaurus**.
- **Format requirement**:
  1.  **User Story**: Brief explanation of the feature from the user's perspective.
  2.  **Dev Implementation**: Technical breakdown, API endpoints used, state management changes, and DB schema interactions.
  3.  **Next Steps/Known Limits**: What to look out for during the rest of the hackathon.
- Do not write code for a new feature without outputting its corresponding `.md` documentation file.
