
<template>
  <RouterView/>
</template>

<style>
/*
 * Global reset.
 *
 */

:root {
  color-scheme: dark;

  /* TODO: ADD brand colours  */
  --lf-green: #92c13b;
  --lf-green-rgb: 146, 193, 59;
  --lf-green-light: #b1d670;

  --lf-blue: #5bc0c9;
  --lf-blue-rgb: 91, 192, 201;

  /* Surfaces */
  --ink: #07070c;
  --surface: #101220;
  --surface-2: #171a2c;
  --line: rgba(255, 255, 255, 0.08);

  /* Semantic aliases used throughout the app */
  --volt: var(--lf-green);
  --volt-rgb: var(--lf-green-rgb);
  --volt-light: var(--lf-green-light);
  --volt-dim: rgba(var(--volt-rgb), 0.14);

  --cyan: var(--lf-blue);
  --cyan-rgb: var(--lf-blue-rgb);

  --coral: #ff5c6c;
  --coral-rgb: 255, 92, 108;

  /* Text */
  --text: #f5f6fb;
  --text-dim: #9294a8;
  --text-faint: #54566b;

  /* Type */
  --font-display: 'Space Grotesk', sans-serif;
  --font-body: 'Inter', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}

*,
*::before,
*::after {
  box-sizing: border-box;
}

html,
body {
  width: 100%;
  height: 100%;

  margin: 0;
  padding: 0;

  background: #07070c;

  overflow: hidden;
}

#app {
  position: fixed;
  inset: 0;

  overflow: hidden;
}
</style>