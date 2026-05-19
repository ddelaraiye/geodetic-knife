#!/usr/bin/env python3
"""
add_themes.py — Injects a 3-theme system (Classic / Light / Dark) into Geodetic Knife.
Classic = original look preserved (no overrides).
Light  = clean minimal (inspired by Inter/glass aesthetic).
Dark   = full dark mode.
Floating theme picker in bottom-right corner with smooth transitions.
"""
import os, sys

# ──────────────────────────────────────────────────────────────
# 1. Anti-FOUC  (inline <script> in <head>, runs before paint)
# ──────────────────────────────────────────────────────────────
ANTI_FOUC = (
    '<script>'
    '/* THEME_SYSTEM_ANTI_FOUC */'
    '!function(){'
    'var t=localStorage.getItem("geodetic_theme")||"classic";'
    'if(t!=="classic")document.documentElement.setAttribute("data-theme",t);'
    '}();'
    '</script>'
)

# ──────────────────────────────────────────────────────────────
# 2. Theme CSS  (all variables + override rules + picker styles)
# ──────────────────────────────────────────────────────────────
THEME_CSS = r"""<style>
/* ═══════════════════════════════════════════════
   THEME SYSTEM v1  —  Geodetic Knife
   ═══════════════════════════════════════════════ */

/* ── Light Theme Variables ── */
[data-theme="light"] {
    --t-bg: #F8F8F7;
    --t-bg-alt: #EFEFEF;
    --t-card: #FFFFFF;
    --t-card-hover: #F5F5F4;
    --t-header-bg: linear-gradient(135deg, #FFFFFF 0%, #F2F2F0 100%);
    --t-header-text: #2B2D31;
    --t-header-sub: #8B8D92;
    --t-text: #2B2D31;
    --t-text-sec: #8B8D92;
    --t-text-muted: #B0B2B6;
    --t-accent: #076EFF;
    --t-accent-h: #0057CC;
    --t-accent2: #5B8DEF;
    --t-accent2-h: #4A7AD9;
    --t-accent-glow: rgba(7,110,255,0.15);
    --t-border: #E2E3E4;
    --t-border-lt: #EDEDEF;
    --t-shadow: 0 1px 4px rgba(0,0,0,0.04);
    --t-shadow-lg: 0 4px 16px rgba(0,0,0,0.08);
    --t-input-bg: #FFFFFF;
    --t-input-bd: #E2E3E4;
    --t-input-fc: #076EFF;
    --t-input-txt: #2B2D31;
    --t-input-ph: #B0B2B6;
    --t-tab-on-bg: #076EFF;
    --t-tab-on-txt: #FFFFFF;
    --t-tab-off-bg: rgba(0,0,0,0.03);
    --t-tab-off-txt: #8B8D92;
    --t-tab-hov-bg: rgba(0,0,0,0.06);
    --t-th-bg: #F0F1F2;
    --t-th-txt: #2B2D31;
    --t-td-bd: #E2E3E4;
    --t-tr-stripe: #FAFAF9;
    --t-td-txt: #2B2D31;
    --t-ok: #22C55E;      --t-ok-bg: #DCFCE7;
    --t-warn: #F59E0B;    --t-warn-bg: #FEF3C7;
    --t-err: #EF4444;     --t-err-bg: #FEE2E2;
    --t-info: #3B82F6;    --t-info-bg: #DBEAFE;
    --t-sb: #D0D1D2;      --t-sb-h: #B0B1B2;
    --t-picker-bg: #FFFFFF;
    --t-picker-bd: #E2E3E4;
    --t-overlay: rgba(0,0,0,0.25);
}

/* ── Dark Theme Variables ── */
[data-theme="dark"] {
    --t-bg: #0F0F0F;
    --t-bg-alt: #1A1A1A;
    --t-card: #1A1A1A;
    --t-card-hover: #242424;
    --t-header-bg: linear-gradient(135deg, #0A0A0F 0%, #14141E 100%);
    --t-header-text: #E3E3E3;
    --t-header-sub: #9CA3AF;
    --t-text: #E3E3E3;
    --t-text-sec: #9CA3AF;
    --t-text-muted: #6B7280;
    --t-accent: #5B9BFF;
    --t-accent-h: #4A8AE0;
    --t-accent2: #A78BFA;
    --t-accent2-h: #8B6CF0;
    --t-accent-glow: rgba(91,155,255,0.2);
    --t-border: #2A2A2A;
    --t-border-lt: #1F1F1F;
    --t-shadow: 0 2px 12px rgba(0,0,0,0.3);
    --t-shadow-lg: 0 4px 24px rgba(0,0,0,0.5);
    --t-input-bg: #252525;
    --t-input-bd: #3A3A3A;
    --t-input-fc: #5B9BFF;
    --t-input-txt: #E3E3E3;
    --t-input-ph: #6B7280;
    --t-tab-on-bg: #5B9BFF;
    --t-tab-on-txt: #FFFFFF;
    --t-tab-off-bg: rgba(255,255,255,0.04);
    --t-tab-off-txt: #9CA3AF;
    --t-tab-hov-bg: rgba(255,255,255,0.08);
    --t-th-bg: #252525;
    --t-th-txt: #E3E3E3;
    --t-td-bd: #2A2A2A;
    --t-tr-stripe: #161616;
    --t-td-txt: #E3E3E3;
    --t-ok: #4ADE80;      --t-ok-bg: rgba(74,222,128,0.12);
    --t-warn: #FBBF24;    --t-warn-bg: rgba(251,191,36,0.12);
    --t-err: #F87171;     --t-err-bg: rgba(248,113,113,0.12);
    --t-info: #60A5FA;    --t-info-bg: rgba(96,165,250,0.12);
    --t-sb: #3A3A3A;      --t-sb-h: #4A4A4A;
    --t-picker-bg: #1E1E1E;
    --t-picker-bd: #333333;
    --t-overlay: rgba(0,0,0,0.65);
}

/* ═══ Override rules ═══ */
/* Only apply when data-theme is set (Light or Dark).
   Classic mode = no data-theme = no overrides = original look. */

/* ── Smooth transitions ── */
[data-theme] body,
[data-theme] .card,
[data-theme] .panel,
[data-theme] button,
[data-theme] input,
[data-theme] select,
[data-theme] textarea,
[data-theme] table,
[data-theme] th,
[data-theme] td,
[data-theme] .tab-btn,
[data-theme] .badge,
[data-theme] header,
[data-theme] .hero,
[data-theme] .hero *,
[data-theme] .app-header {
    transition:
        background-color 0.35s ease,
        color 0.35s ease,
        border-color 0.35s ease,
        box-shadow 0.35s ease,
        background-image 0.35s ease;
}

/* ── Body ── */
[data-theme] body {
    background-color: var(--t-bg) !important;
    color: var(--t-text) !important;
    background-image: none !important;
}

/* ── Header / Hero ── */
[data-theme] header,
[data-theme] .header,
[data-theme] .hero,
[data-theme] .hero-section,
[data-theme] .app-header,
[data-theme] [class*="hero"],
[data-theme] [class*="Hero"] {
    background: var(--t-header-bg) !important;
    color: var(--t-header-text) !important;
    border-bottom-color: var(--t-border) !important;
}
[data-theme] header h1,
[data-theme] header h2,
[data-theme] header h3,
[data-theme] header p,
[data-theme] header span,
[data-theme] header li,
[data-theme] .header h1,
[data-theme] .header h2,
[data-theme] .header p,
[data-theme] .hero h1,
[data-theme] .hero h2,
[data-theme] .hero h3,
[data-theme] .hero p,
[data-theme] .hero span,
[data-theme] .hero li,
[data-theme] .hero-section h1,
[data-theme] .hero-section p,
[data-theme] .app-header h1,
[data-theme] .app-header p {
    color: var(--t-header-text) !important;
}
[data-theme] header .subtitle,
[data-theme] .hero .subtitle,
[data-theme] [class*="hero"] .subtitle,
[data-theme] header .tagline,
[data-theme] .hero .tagline {
    color: var(--t-header-sub) !important;
}

/* ── Cards / Panels ── */
[data-theme] .card,
[data-theme] .panel,
[data-theme] .result-card,
[data-theme] .stat-card,
[data-theme] .info-card,
[data-theme] .box,
[data-theme] .well,
[data-theme] [class*="card"],
[data-theme] [class*="Card"],
[data-theme] [class*="panel"],
[data-theme] [class*="Panel"],
[data-theme] [class*="container"]:not(.theme-picker):not(.theme-options) {
    background-color: var(--t-card) !important;
    border-color: var(--t-border) !important;
    box-shadow: var(--t-shadow) !important;
    color: var(--t-text) !important;
}

/* ── Buttons ── */
[data-theme] button:not(.theme-toggle-btn):not(.theme-option),
[data-theme] .btn,
[data-theme] [class*="btn"],
[data-theme] [class*="Btn"],
[data-theme] input[type="button"],
[data-theme] input[type="submit"] {
    transition: background-color 0.2s, color 0.2s, border-color 0.2s, box-shadow 0.2s !important;
}
[data-theme] .btn-primary,
[data-theme] [class*="btn-primary"],
[data-theme] [class*="btnPrimary"],
[data-theme] button.primary {
    background-color: var(--t-accent) !important;
    color: #fff !important;
    border-color: var(--t-accent) !important;
}
[data-theme] .btn-primary:hover,
[data-theme] [class*="btn-primary"]:hover {
    background-color: var(--t-accent-h) !important;
}
[data-theme] .btn-success,
[data-theme] [class*="btn-success"],
[data-theme] [class*="btnSuccess"],
[data-theme] button.success {
    background-color: var(--t-ok) !important;
    color: #fff !important;
    border-color: var(--t-ok) !important;
}
[data-theme] .btn-danger,
[data-theme] [class*="btn-danger"],
[data-theme] [class*="btnDanger"],
[data-theme] button.danger {
    background-color: var(--t-err) !important;
    color: #fff !important;
    border-color: var(--t-err) !important;
}
[data-theme] .btn-warning,
[data-theme] [class*="btn-warning"],
[data-theme] button.warning {
    background-color: var(--t-warn) !important;
    color: #fff !important;
    border-color: var(--t-warn) !important;
}
[data-theme] .btn-outline,
[data-theme] [class*="btn-outline"],
[data-theme] [class*="btnOutline"],
[data-theme] button.outline,
[data-theme] .btn-secondary,
[data-theme] [class*="btn-secondary"],
[data-theme] button.secondary {
    background-color: transparent !important;
    color: var(--t-accent) !important;
    border-color: var(--t-accent) !important;
}
[data-theme] .btn-outline:hover,
[data-theme] .btn-secondary:hover {
    background-color: var(--t-accent-glow) !important;
}

/* ── Inputs ── */
[data-theme] input:not([type="checkbox"]):not([type="radio"]):not([type="color"]):not([type="file"]),
[data-theme] select,
[data-theme] textarea {
    background-color: var(--t-input-bg) !important;
    border-color: var(--t-input-bd) !important;
    color: var(--t-input-txt) !important;
}
[data-theme] input:focus,
[data-theme] select:focus,
[data-theme] textarea:focus {
    border-color: var(--t-input-fc) !important;
    outline-color: var(--t-input-fc) !important;
    box-shadow: 0 0 0 3px var(--t-accent-glow) !important;
}
[data-theme] input::placeholder,
[data-theme] textarea::placeholder {
    color: var(--t-input-ph) !important;
    opacity: 1 !important;
}
[data-theme] label {
    color: var(--t-text-sec) !important;
}

/* ── Tabs ── */
[data-theme] .tab-btn,
[data-theme] .tab,
[data-theme] .nav-tab,
[data-theme] [class*="tab-btn"],
[data-theme] [class*="tabButton"],
[data-theme] [data-tab] {
    background-color: var(--t-tab-off-bg) !important;
    color: var(--t-tab-off-txt) !important;
    border-color: transparent !important;
}
[data-theme] .tab-btn:hover,
[data-theme] .tab:hover,
[data-theme] [data-tab]:hover {
    background-color: var(--t-tab-hov-bg) !important;
}
[data-theme] .tab-btn.active,
[data-theme] .tab.active,
[data-theme] [data-tab].active,
[data-theme] .tab-btn.active-tab,
[data-theme] [class*="tab-btn"].active {
    background-color: var(--t-tab-on-bg) !important;
    color: var(--t-tab-on-txt) !important;
    border-color: var(--t-tab-on-bg) !important;
}

/* ── Tables ── */
[data-theme] table {
    border-color: var(--t-td-bd) !important;
    color: var(--t-td-txt) !important;
}
[data-theme] thead,
[data-theme] th {
    background-color: var(--t-th-bg) !important;
    color: var(--t-th-txt) !important;
    border-color: var(--t-td-bd) !important;
}
[data-theme] td {
    border-color: var(--t-td-bd) !important;
    color: var(--t-td-txt) !important;
}
[data-theme] tr:nth-child(even),
[data-theme] tr:nth-child(even) td {
    background-color: var(--t-tr-stripe) !important;
}

/* ── Text ── */
[data-theme] h1,
[data-theme] h2,
[data-theme] h3,
[data-theme] h4,
[data-theme] h5,
[data-theme] h6 {
    color: var(--t-text) !important;
}
[data-theme] p,
[data-theme] span,
[data-theme] li {
    color: var(--t-text-sec);
}
[data-theme] a,
[data-theme] a:visited {
    color: var(--t-accent) !important;
}
[data-theme] small,
[data-theme] .text-muted,
[data-theme] [class*="muted"],
[data-theme] [class*="subtitle"],
[data-theme] [class*="description"] {
    color: var(--t-text-muted) !important;
}

/* ── Badges / Status ── */
[data-theme] .badge,
[data-theme] [class*="badge"] {
    border-radius: 9999px;
    padding: 2px 10px;
    font-size: 12px;
    font-weight: 600;
}
[data-theme] .badge-success,
[data-theme] [class*="badge-success"],
[data-theme] [class*="status-ok"],
[data-theme] [class*="status-active"],
[data-theme] .status-active {
    background-color: var(--t-ok-bg) !important;
    color: var(--t-ok) !important;
}
[data-theme] .badge-warning,
[data-theme] [class*="badge-warning"],
[data-theme] [class*="status-warn"],
[data-theme] [class*="status-pending"] {
    background-color: var(--t-warn-bg) !important;
    color: var(--t-warn) !important;
}
[data-theme] .badge-danger,
[data-theme] [class*="badge-danger"],
[data-theme] [class*="status-err"],
[data-theme] [class*="status-error"],
[data-theme] [class*="status-inactive"] {
    background-color: var(--t-err-bg) !important;
    color: var(--t-err) !important;
}
[data-theme] .badge-info,
[data-theme] [class*="badge-info"],
[data-theme] [class*="status-info"] {
    background-color: var(--t-info-bg) !important;
    color: var(--t-info) !important;
}

/* ── Scrollbar ── */
[data-theme] ::-webkit-scrollbar { width: 8px; height: 8px; }
[data-theme] ::-webkit-scrollbar-track { background: var(--t-bg); }
[data-theme] ::-webkit-scrollbar-thumb { background: var(--t-sb); border-radius: 4px; }
[data-theme] ::-webkit-scrollbar-thumb:hover { background: var(--t-sb-h); }

/* ── Modals / Overlays ── */
[data-theme] .modal-backdrop,
[data-theme] .overlay,
[data-theme] [class*="backdrop"] {
    background-color: var(--t-overlay) !important;
}
[data-theme] .modal,
[data-theme] .modal-content,
[data-theme] .dialog,
[data-theme] [class*="modal"],
[data-theme] [class*="dialog"] {
    background-color: var(--t-card) !important;
    border-color: var(--t-border) !important;
    color: var(--t-text) !important;
}

/* ── Footer ── */
[data-theme] footer,
[data-theme] .footer {
    background-color: var(--t-bg-alt) !important;
    color: var(--t-text-muted) !important;
    border-top-color: var(--t-border) !important;
}

/* ── Code / Pre ── */
[data-theme] code,
[data-theme] pre {
    background-color: var(--t-bg-alt) !important;
    color: var(--t-text) !important;
    border-color: var(--t-border) !important;
}

/* ── Divider / HR ── */
[data-theme] hr,
[data-theme] .divider {
    border-color: var(--t-border) !important;
}

/* ═══════════════════════════════════════════════
   THEME PICKER UI
   ═══════════════════════════════════════════════ */
.theme-picker {
    position: fixed;
    bottom: 24px;
    right: 24px;
    z-index: 99999;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.theme-toggle-btn {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: var(--t-picker-bg, #FFFFFF);
    border: 2px solid var(--t-picker-bd, #E0E0E0);
    box-shadow: 0 2px 12px rgba(0,0,0,0.1), 0 0 0 0 var(--t-accent-glow, transparent);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--t-accent, #076EFF);
    transition: transform 0.25s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.25s ease;
    padding: 0;
}
.theme-toggle-btn:hover {
    transform: scale(1.12);
    box-shadow: 0 4px 20px rgba(0,0,0,0.15), 0 0 0 4px var(--t-accent-glow, rgba(7,110,255,0.12));
}
.theme-toggle-btn:active {
    transform: scale(0.95);
}

.theme-options {
    position: absolute;
    bottom: 62px;
    right: 0;
    background: var(--t-picker-bg, #FFFFFF);
    border: 1px solid var(--t-picker-bd, #E0E0E0);
    border-radius: 16px;
    padding: 8px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.12);
    display: flex;
    flex-direction: column;
    gap: 4px;
    min-width: 160px;
    opacity: 0;
    transform: translateY(8px) scale(0.95);
    pointer-events: none;
    transition: opacity 0.2s ease, transform 0.2s cubic-bezier(0.34,1.56,0.64,1);
}
.theme-options.open {
    opacity: 1;
    transform: translateY(0) scale(1);
    pointer-events: auto;
}

.theme-option {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    border: none;
    background: transparent;
    border-radius: 12px;
    cursor: pointer;
    transition: background-color 0.15s ease;
    font-size: 13px;
    font-weight: 500;
    color: #555;
    font-family: inherit;
    width: 100%;
    text-align: left;
}
[data-theme="dark"] .theme-option { color: #ccc; }
.theme-option:hover { background-color: var(--t-bg-alt, #f0f0f0); }
.theme-option.active {
    background-color: var(--t-accent-glow, rgba(7,110,255,0.08));
    font-weight: 600;
}

.theme-swatch {
    width: 30px;
    height: 30px;
    border-radius: 10px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}
.theme-swatch-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
}

.theme-option-label {
    flex: 1;
    line-height: 1;
}
.theme-option-check {
    width: 18px;
    height: 18px;
    opacity: 0;
    transition: opacity 0.15s;
    color: var(--t-accent, #076EFF);
}
.theme-option.active .theme-option-check {
    opacity: 1;
}

/* ── Responsive ── */
@media (max-width: 600px) {
    .theme-picker { bottom: 16px; right: 16px; }
    .theme-toggle-btn { width: 44px; height: 44px; }
    .theme-options { min-width: 140px; bottom: 56px; }
    .theme-option { padding: 8px 10px; font-size: 12px; }
    .theme-swatch { width: 26px; height: 26px; border-radius: 8px; }
}
</style>"""

# ──────────────────────────────────────────────────────────────
# 3. Theme Picker HTML  (injected right after <body>)
# ──────────────────────────────────────────────────────────────
THEME_HTML = r"""<!-- THEME_SYSTEM_PICKER -->
<div id="theme-picker" class="theme-picker">
  <button id="theme-toggle-btn" class="theme-toggle-btn" title="Change Theme">
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="12" r="4"/>
      <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/>
    </svg>
  </button>
  <div id="theme-options" class="theme-options">
    <button class="theme-option" data-set-theme="classic">
      <div class="theme-swatch" style="background:linear-gradient(135deg,#1a1a2e,#0f3460);">
        <div class="theme-swatch-dot" style="background:#f0a500;"></div>
      </div>
      <span class="theme-option-label">Classic</span>
      <svg class="theme-option-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
    </button>
    <button class="theme-option" data-set-theme="light">
      <div class="theme-swatch" style="background:#F8F8F7;border:1px solid #E2E3E4;">
        <div class="theme-swatch-dot" style="background:#076EFF;"></div>
      </div>
      <span class="theme-option-label">Light</span>
      <svg class="theme-option-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
    </button>
    <button class="theme-option" data-set-theme="dark">
      <div class="theme-swatch" style="background:#0F0F0F;border:1px solid #333;">
        <div class="theme-swatch-dot" style="background:#5B9BFF;"></div>
      </div>
      <span class="theme-option-label">Dark</span>
      <svg class="theme-option-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
    </button>
  </div>
</div>"""

# ──────────────────────────────────────────────────────────────
# 4. Theme JavaScript  (injected before </body>)
# ──────────────────────────────────────────────────────────────
THEME_JS = r"""<script>
/* THEME_SYSTEM_JS */
(function() {
    'use strict';
    var KEY = 'geodetic_theme';
    var THEMES = ['classic', 'light', 'dark'];

    function getTheme() {
        var stored = localStorage.getItem(KEY);
        return (stored && THEMES.indexOf(stored) !== -1) ? stored : 'classic';
    }

    function applyTheme(theme) {
        if (theme === 'classic') {
            document.documentElement.removeAttribute('data-theme');
        } else {
            document.documentElement.setAttribute('data-theme', theme);
        }
        localStorage.setItem(KEY, theme);
        updatePickerUI(theme);
    }

    function updatePickerUI(theme) {
        var opts = document.querySelectorAll('.theme-option');
        for (var i = 0; i < opts.length; i++) {
            var isActive = opts[i].getAttribute('data-set-theme') === theme;
            opts[i].classList.toggle('active', isActive);
        }
        updateToggleIcon(theme);
    }

    function updateToggleIcon(theme) {
        var btn = document.getElementById('theme-toggle-btn');
        if (!btn) return;
        var icons = {
            classic: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>',
            light:   '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>',
            dark:    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>'
        };
        btn.innerHTML = icons[theme] || icons.classic;
    }

    // Wire up picker
    var toggleBtn = document.getElementById('theme-toggle-btn');
    var optionsEl = document.getElementById('theme-options');

    if (toggleBtn && optionsEl) {
        toggleBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            optionsEl.classList.toggle('open');
        });

        document.addEventListener('click', function(e) {
            if (!e.target.closest('.theme-picker')) {
                optionsEl.classList.remove('open');
            }
        });

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                optionsEl.classList.remove('open');
            }
        });

        var optBtns = document.querySelectorAll('.theme-option');
        for (var i = 0; i < optBtns.length; i++) {
            optBtns[i].addEventListener('click', function() {
                var theme = this.getAttribute('data-set-theme');
                applyTheme(theme);
                optionsEl.classList.remove('open');
            });
        }

        // Init
        applyTheme(getTheme());
    }
})();
</script>"""

# ──────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(script_dir, 'public', 'index.html')

    if not os.path.isfile(html_path):
        print('[ERR] public/index.html not found at: ' + html_path)
        sys.exit(1)

    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    if 'THEME_SYSTEM_ANTI_FOUC' in html:
        print('[OK] Theme system already applied. Skipping.')
        return

    # Inject 1: Anti-FOUC before </head>
    if '</head>' in html:
        html = html.replace('</head>', ANTI_FOUC + '\n</head>', 1)
        print('[OK] Anti-FOUC script injected')
    else:
        print('[WARN] </head> not found — skipping anti-FOUC')

    # Inject 2: Theme CSS before </head>
    if '</head>' in html:
        html = html.replace('</head>', THEME_CSS + '\n</head>', 1)
        print('[OK] Theme CSS injected')
    else:
        print('[WARN] </head> not found — skipping theme CSS')

    # Inject 3: Theme picker HTML after <body>
    if '<body' in html:
        # Insert after the <body...> opening tag
        import re
        html = re.sub(r'(<body[^>]*>)', r'\1\n' + THEME_HTML.replace('\\', '\\\\'), html, count=1)
        print('[OK] Theme picker HTML injected')
    else:
        print('[WARN] <body> not found — skipping picker HTML')

    # Inject 4: Theme JS before </body>
    if '</body>' in html:
        html = html.replace('</body>', THEME_JS + '\n</body>', 1)
        print('[OK] Theme JS injected')
    else:
        print('[WARN] </body> not found — skipping theme JS')

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print()
    print('='*50)
    print('  Theme system applied successfully!')
    print('  3 variants: Classic / Light / Dark')
    print('  Floating picker in bottom-right corner')
    print('  Preference saved to localStorage')
    print('='*50)

if __name__ == '__main__':
    main()
