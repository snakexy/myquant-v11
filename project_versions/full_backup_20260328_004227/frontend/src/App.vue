<template>
  <div id="app" class="app-container">
    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
</script>

<style lang="scss">
:root {
  --primary: #2563eb;
  --secondary: #2962ff;
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
  --info: #3b82f6;
  --accent-blue: #2962ff;

  --bg-deep: #0a0a0f;
  --bg-surface: #1a1a2e;
  --bg-elevated: #252530;

  --text-primary: #f8fafc;
  --text-secondary: #cbd5e1;
  --text-muted: #94a3b8;

  --border-light: rgba(255, 255, 255, 0.1);
  --border-medium: rgba(255, 255, 255, 0.2);

  --font-family-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-family-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  width: 100%;
  height: 100%;
  background: var(--bg-deep);
  color: var(--text-primary);
  font-family: var(--font-family-primary);
}

.app-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg-deep);
  color: var(--text-primary);
}

.app-main {
  flex: 1;
  min-height: 0;
  height: 100%;
  overflow: hidden;
  padding: 0;
  background: var(--bg-deep);
}
</style>
