<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <div id="app">
    <header class="app-header">
      <div class="header-content">
        <h1 class="app-title">XMind 冒烟测试用例导出工具</h1>
      </div>
    </header>
    
    <main class="app-main">
      <RouterView />
    </main>
    
    <footer class="app-footer">
      <p>&copy; 2024 XMind 冒烟测试用例导出工具</p>
    </footer>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  background-color: #f5f7fa;
  color: #303133;
}

#app {
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, #409eff 0%, #5cb3f7 100%);
  color: white;
  padding: 20px 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.app-title {
  font-size: 24px;
  font-weight: 600;
  text-align: center;
}

.app-main {
  flex: 1;
  min-height: calc(100vh - 120px);
}

.app-footer {
  background-color: #f8f9fa;
  text-align: center;
  padding: 20px;
  color: #909399;
  border-top: 1px solid #ebeef5;
}

.app-footer p {
  margin: 0;
  font-size: 14px;
}
</style>
