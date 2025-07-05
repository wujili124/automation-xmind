const { contextBridge, ipcRenderer } = require('electron');

// 暴露安全的API给渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
  // 获取API基础URL
  getApiBaseUrl: () => ipcRenderer.invoke('get-api-base-url'),
  
  // 可以在这里添加更多的API
}); 