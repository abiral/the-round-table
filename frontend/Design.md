# Design System

Distilled from the BotAI reference screenshot. The vibe is **soft, warm, conversational, and AI-native**: lots of breathing room, rounded everything, restrained colour with a single confident primary, and pastel accents reserved for category chips.

This document is the source of truth for visual decisions in this frontend. When in doubt, match the screenshot.

---

## 1. Design Principles

1. **Whitespace is content.** Generous padding everywhere. Sections are separated by space first, dividers second.
2. **Round, never sharp.** Pills for buttons, large radii for cards. No 90-degree corners on interactive elements.
3. **One confident primary, pastel accents.** Indigo / violet is the only "load-bearing" colour. Pastels (peach, mint, sky, lavender, rose) are for category icons and chips, never for primary actions.
4. **Soft background, white surfaces.** The page bg is a faint warm gradient; cards, sidebars, and inputs sit on near-white surfaces with hairline borders.
5. **Type weight, not type size.** Use weight contrast (400 vs 600) before size contrast.
6. **No em dashes anywhere** (consistent with the app's content rule).

---

## 2. Colour Tokens

All values target the **light theme** seen in the screenshot. Dark theme values are listed where they diverge.

### Surfaces

| Token              | Light                          | Notes                                              |
|--------------------|--------------------------------|----------------------------------------------------|
| `bg-app`           | gradient: `#FBF7F3` → `#F4F2FD`| Page background, very subtle warm-to-cool fade.    |
| `bg-surface`       | `#FFFFFF`                      | Cards, input, sidebar.                             |
| `bg-surface-muted` | `#F7F7FB`                      | Hovered list items, secondary surface.             |
| `bg-overlay`       | `rgba(17, 24, 39, 0.04)`       | Subtle hover.                                      |
| `border-subtle`    | `#EAEAF1`                      | Default hairline border.                           |
| `border-strong`    | `#D8D8E3`                      | Focused / pressed borders.                         |

### Brand / primary

| Token              | Value     | Use                                                  |
|--------------------|-----------|------------------------------------------------------|
| `primary-500`      | `#6366F1` | Default primary (buttons, links, send icon).         |
| `primary-600`      | `#5457E5` | Pressed / darker.                                    |
| `primary-400`      | `#818CF8` | Hover gradient start.                                |
| `primary-soft`     | `#EEF1FF` | Soft tinted backgrounds (active sidebar item, focus rings). |
| `primary-on`       | `#FFFFFF` | Text on primary.                                     |
| `primary-gradient` | `linear-gradient(135deg, #7C7BFF 0%, #6366F1 100%)` | Send button, hero CTA. |

### Text

| Token            | Value     | Use                                  |
|------------------|-----------|--------------------------------------|
| `text-strong`    | `#0F1024` | Headings, primary text.              |
| `text-default`   | `#1F2330` | Body.                                |
| `text-muted`     | `#6B7080` | Secondary text, helper copy.         |
| `text-subtle`    | `#9CA0AE` | Disabled, placeholder, section caps. |
| `text-on-primary`| `#FFFFFF` | On primary surfaces.                 |

### Pastel accent set (chip icons & decorative)

These are for **category identity only**. Never use them for buttons or states.

| Token         | Value     | Example use         |
|---------------|-----------|---------------------|
| `accent-mint` | `#A7E0C6` | Get Advice          |
| `accent-peach`| `#F6C9B0` | Image / Photo       |
| `accent-rose` | `#F4B7C3` | Audio               |
| `accent-sky`  | `#B7D6F6` | Search, summarize   |
| `accent-amber`| `#F2D097` | Brainstorm, advice  |
| `accent-lilac`| `#CFC3F4` | Help me write       |
| `accent-coral`| `#F0A89A` | Problem solving     |

Tints / containers for the chip bg are the pastel at **~12% opacity over white**, or `color-mix(in srgb, <pastel> 18%, white)`.

### Semantic

| Token         | Value     |
|---------------|-----------|
| `success`     | `#16A34A` |
| `warning`     | `#D97706` |
| `danger`      | `#DC2626` |
| `info`        | `#0EA5E9` |

### Dark theme deltas (the moon-toggle target)

| Token              | Dark                            |
|--------------------|---------------------------------|
| `bg-app`           | `#0B0B14` with a faint indigo fade |
| `bg-surface`       | `#15151F`                       |
| `bg-surface-muted` | `#1B1B27`                       |
| `border-subtle`    | `#262633`                       |
| `text-strong`      | `#F4F4F8`                       |
| `text-muted`       | `#9CA0AE`                       |
| `primary-soft`     | `#1F1F33`                       |

Pastels remain the same; just lower their text contrast by switching the chip label to `text-strong`.

---

## 3. Typography

- **Font:** Inter (or system-ui fallback). Tabular figures off.
- **Tracking:** Tight on headings (`-0.01em`), normal on body.
- **Section labels** are uppercase with `0.08em` tracking.

| Token        | Size / Line | Weight | Use                                  |
|--------------|-------------|--------|--------------------------------------|
| `display`    | 28 / 34     | 600    | Hero greeting ("Hello, I'm BotAI").  |
| `h1`         | 22 / 28     | 600    | Page titles.                         |
| `h2`         | 16 / 22     | 600    | Card titles.                         |
| `body`       | 14 / 22     | 400    | Default.                             |
| `body-strong`| 14 / 22     | 600    | Strong inline.                       |
| `small`      | 12 / 18     | 400    | Helper, timestamps.                  |
| `label-caps` | 11 / 14     | 600    | Sidebar group caps. Uppercase, tracked. |
| `mono`       | 13 / 20     | 500    | Inline code, model IDs.              |

---

## 4. Spacing, Radius, Shadow

### Spacing scale (in px)

```
2  4  6  8  10  12  16  20  24  32  40  48  64
```

Prefer multiples of 4. Section gaps in main content default to **24px** vertical.

### Radius

| Token        | Value | Use                                  |
|--------------|-------|--------------------------------------|
| `radius-sm`  | 6     | Inline tags.                         |
| `radius-md`  | 10    | Inputs, small cards.                 |
| `radius-lg`  | 16    | Cards.                               |
| `radius-xl`  | 22    | Input bar, message bubbles.          |
| `radius-pill`| 9999  | All button-shaped controls.          |

### Shadow / elevation

| Token         | CSS                                                              |
|---------------|------------------------------------------------------------------|
| `shadow-sm`   | `0 1px 2px rgba(15, 16, 36, 0.04)`                               |
| `shadow-card` | `0 1px 2px rgba(15, 16, 36, 0.04), 0 4px 12px rgba(15, 16, 36, 0.05)` |
| `shadow-pop`  | `0 8px 24px rgba(99, 102, 241, 0.18)`                            |
| `shadow-focus`| `0 0 0 3px rgba(99, 102, 241, 0.18)`                             |

The input bar uses `shadow-card`. The primary send button uses `shadow-pop`.

---

## 5. Layout

- **Sidebar width:** `256px`, full height, scrolls independently.
- **Main column:** centered, `max-width: 800px`, padding `24px 32px`.
- **App padding:** the page itself has no padding; the sidebar is flush left and the main column owns its own gutters.
- **Sticky regions:** top bar and bottom copyright stay pinned; the middle scrolls.

---

## 6. Components

Class snippets below assume Tailwind. They are guides, not contracts.

### 6.1 Sidebar

- White background, `border-r border-subtle`.
- Internal padding: `px-3 py-4`.
- Vertical rhythm: `space-y-1` for nav items, `space-y-4` for groups.
- Three regions: top (logo + utility), middle (nav + recents), bottom (system).
- Bottom region is pinned with `mt-auto` and separated by a hairline `border-t`.

### 6.2 Sidebar group label

```
text-[11px] font-semibold tracking-[0.08em] uppercase text-subtle px-2 mb-1
```

### 6.3 Nav item (primary, "New Chat")

- Full-pill primary button, leading icon, full sidebar width.
- Subtle drop shadow (`shadow-pop` at low intensity).

```
flex items-center gap-2 px-3 py-2 rounded-pill
bg-primary text-white font-medium
shadow-[0_4px_12px_rgba(99,102,241,0.25)]
hover:bg-primary-600
```

### 6.4 Nav item (secondary)

```
flex items-center gap-2 px-3 py-2 rounded-lg
text-default hover:bg-surface-muted
data-[active=true]:bg-primary-soft data-[active=true]:text-primary-600
```

Active state is **soft tinted background + primary text**, not a filled primary.

### 6.5 Recent / history item

```
flex items-center gap-2 px-3 py-1.5 rounded-md
text-default text-sm truncate
hover:bg-surface-muted
```

A small file/chat icon precedes the title. Truncate at one line.

### 6.6 Top bar

- Height: `56px`.
- Three columns: (left) model selector dropdown, (center) empty, (right) theme toggle + Share + avatar.
- No bottom border; the surface change provides separation.

### 6.7 Model selector dropdown

- Two lines stacked: `<Name>` in `body-strong`, `<variant>` in `small text-muted`.
- Small chevron at right. No outline; reveals an outlined pill on hover.

### 6.8 Icon button (top bar, ghost circle)

```
size-9 rounded-full grid place-items-center
text-muted hover:bg-surface-muted hover:text-default
```

### 6.9 Outlined pill button (Share)

```
inline-flex items-center gap-2 px-3 h-9 rounded-pill
border border-subtle text-default hover:border-strong
```

### 6.10 Hero greeting

- Centered, generous top spacing (`pt-16`).
- Robot emoji or logo glyph leads the title, separated by `gap-3`.
- Subtitle in `text-muted`, max-width comfortably narrow (`max-w-md`).

### 6.11 Composer / Input card

The single most important component on the screen.

- Surface: white, `radius-xl`, `border border-subtle`, `shadow-card`.
- Padding: `px-5 pt-4 pb-3`.
- Layout: a free-height textarea on top, then a bottom row split into (left) mode chips, (right) icon group + send.
- Min height ~140px so it does not feel cramped when empty.
- Placeholder colour: `text-subtle`.

```html
<div class="rounded-2xl border border-subtle bg-white shadow-card px-5 pt-4 pb-3">
  <textarea class="w-full bg-transparent resize-none outline-none placeholder:text-subtle" />
  <div class="flex items-center justify-between mt-2">
    <div class="flex gap-2">
      <ModePill icon="search">Search</ModePill>
      <ModePill icon="sparkles">Brainstorm</ModePill>
    </div>
    <div class="flex items-center gap-2">
      <IconButton icon="mic" />
      <IconButton icon="paperclip" />
      <SendButton />
    </div>
  </div>
</div>
```

### 6.12 Mode pill (Search / Brainstorm)

- Hairline border, transparent bg, small leading icon, label.

```
inline-flex items-center gap-1.5 h-8 px-3 rounded-pill
border border-subtle text-muted text-sm
hover:border-strong hover:text-default
data-[active=true]:bg-primary-soft data-[active=true]:text-primary-600 data-[active=true]:border-transparent
```

### 6.13 Send button (circular)

- Solid primary, circular, up-arrow icon, `shadow-pop`.

```
size-10 rounded-full grid place-items-center
bg-primary-gradient text-white shadow-pop
hover:brightness-105 active:brightness-95
disabled:opacity-40 disabled:shadow-none
```

### 6.14 Suggestion / category chip

The row of "Image Generator", "Video Generator", etc.

- Outlined pill, leading icon in a **pastel circle**, label in `text-default`.
- Subtle hover lift.

```html
<button class="inline-flex items-center gap-2 h-9 pl-2 pr-4 rounded-pill
               border border-subtle bg-white hover:shadow-card hover:-translate-y-px transition">
  <span class="size-6 rounded-full grid place-items-center bg-accent-peach/40 text-[#A85A2F]">
    <ImageIcon class="size-3.5" />
  </span>
  <span class="text-sm text-default">Image Generator</span>
</button>
```

Icon background colour cycles through the pastel set per category. Keep the **icon glyph colour the darker tone of the same pastel**, never primary indigo.

### 6.15 "New" badge

```
inline-flex items-center px-2 h-5 rounded-pill text-[10px] font-semibold
bg-rose-100 text-rose-600
```

### 6.16 Status dot (sidebar bottom rows)

A `2px` filled circle on the right edge of "Support", "Settings". Indicates dot colour by intent:
- `accent-mint` for OK
- `accent-amber` for action recommended

### 6.17 Avatar

- `size-9 rounded-full`, hairline border (`border border-subtle`), no shadow.

### 6.18 Section divider (main content)

Used sparingly, only between unrelated content blocks.

```
border-t border-subtle my-6
```

### 6.19 Empty / loading / error states

- **Empty:** centered, muted icon, one-line title, one-line helper. Same hero structure as the greeting.
- **Loading:** three bouncing dots (already used in the app) in `text-subtle`.
- **Error:** soft red surface `bg-rose-50 border border-rose-200 text-rose-700`, `radius-md`, inline.

---

## 7. Motion

- Default transition: `transition-all duration-150 ease-out`.
- Hover lifts: `-translate-y-px` plus shadow upgrade.
- Avoid spring physics; this is a calm UI.
- Streaming cursor: a single thin caret pulsing at `1.2s ease-in-out infinite`.

---

## 8. Iconography

- Line icons only (Lucide). Stroke width `1.5`, default size `16` in compact spots, `18` in primary buttons, `20` in chips with pastel circles.
- Never mix line + filled icon styles in the same row.

---

## 9. Accessibility

- Contrast: text on white meets WCAG AA (`text-muted` against white is the floor).
- Focus ring: `shadow-focus` (3px primary-tinted ring), never browser default.
- Every icon button has an aria-label.
- Pill chips are real `<button>` elements with `aria-pressed` when toggleable.
- Reduced motion: disable hover lifts and the streaming cursor pulse when `prefers-reduced-motion: reduce`.

---

## 10. Application Notes (mapping to this app)

How the existing components in [src/components/chat/](src/components/chat/) map onto this system:

| Existing component   | Becomes                                                            |
|----------------------|--------------------------------------------------------------------|
| `App.tsx` shell      | Two-column layout: sidebar + main with the centered hero on idle.  |
| `InputBar.tsx`       | The composer card (§6.11) with mode pills (§6.12) + send (§6.13).  |
| `ChatWindow.tsx`     | Streams replace the hero once a conversation starts.               |
| `MessageBubble.tsx`  | Keep agent / user / chirp variants. Move to `radius-xl` and `shadow-sm`. |
| `PauseBanner.tsx`    | Soft `primary-soft` background, no shadow, `radius-md`.            |
| `ExportPanel.tsx`    | Category chip grid (§6.14) themed with the pastel set.             |
| `AgentBadge.tsx`     | Stays as-is; ensure its dot colour comes from `ROLE_COLORS`, not raw Tailwind. |
| New: `Sidebar.tsx`   | Sessions history, "New Chat" primary, settings at the bottom.      |
| New: `TopBar.tsx`    | Model selector + theme toggle + share + avatar.                    |

When implementing, lean on this Design.md before reaching for ad-hoc Tailwind. If a value here looks wrong in practice, update this file in the same PR so it stays the source of truth.
