<template>
  <div id="app">
    <NuxtRouteAnnouncer />
    <NuxtPage />
  </div>
</template>

<style>
/* ponytail: token architecture — cinema studio direction. Upgrade path: extract to tokens.css when adding pages. */
:root {
  /* Surface elevation: base → raised → overlay (lightness shifts only, one hue) */
  --surface-0: #0c0d11;
  --surface-1: #131519;
  --surface-2: #1a1c22;
  --surface-3: #22252c;
  --surface-4: #2a2d36;

  /* Text hierarchy: 4 levels */
  --ink-primary: #edeef0;
  --ink-secondary: #9ea2ad;
  --ink-tertiary: #6b6f7b;
  --ink-muted: #484c57;

  /* Borders: rgba blends, whisper-quiet */
  --edge: rgba(255, 255, 255, 0.06);
  --edge-strong: rgba(255, 255, 255, 0.10);
  --edge-focus: rgba(232, 178, 80, 0.4);

  /* Brand: warm amber — projector glow */
  --brand: #e8b250;
  --brand-hover: #f0c36a;
  --brand-muted: rgba(232, 178, 80, 0.12);
  --brand-subtle: rgba(232, 178, 80, 0.06);

  /* Semantic */
  --success: #3ec97a;
  --success-muted: rgba(62, 201, 122, 0.12);
  --warning: #e8a840;
  --danger: #e85454;
  --danger-muted: rgba(232, 84, 84, 0.12);

  /* Controls */
  --control-bg: #111318;
  --control-border: rgba(255, 255, 255, 0.08);
  --control-border-hover: rgba(255, 255, 255, 0.14);
  --control-border-focus: rgba(232, 178, 80, 0.5);

  /* Spacing: 4px base */
  --sp-1: 4px;
  --sp-2: 8px;
  --sp-3: 12px;
  --sp-4: 16px;
  --sp-5: 20px;
  --sp-6: 24px;
  --sp-8: 32px;
  --sp-10: 40px;
  --sp-12: 48px;

  /* Radius scale */
  --radius-xs: 4px;
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;

  /* Motion */
  --ease-out: cubic-bezier(0.23, 1, 0.32, 1);
  --duration-fast: 120ms;
  --duration-normal: 180ms;
}

*,
*::before,
*::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  font-size: 14px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

body {
  font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--surface-0);
  color: var(--ink-primary);
  min-height: 100vh;
  line-height: 1.5;
}

#app {
  min-height: 100vh;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--ink-muted); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--ink-tertiary); }

/* Selection */
::selection {
  background: var(--brand-muted);
  color: var(--ink-primary);
}
</style>
