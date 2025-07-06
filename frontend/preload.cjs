const { contextBridge, ipcRenderer } = require('electron');

// 暴露给渲染进程的API
contextBridge.exposeInMainWorld('electronAPI', {
  // 获取API基础URL
  getApiBaseUrl: () => ipcRenderer.invoke('get-api-base-url'),
  
  // 检查后端状态
  checkBackendStatus: async () => {
    try {
      const baseUrl = await ipcRenderer.invoke('get-api-base-url')
      const response = await fetch(`${baseUrl}/health`)
      if (response.ok) {
        return { status: 'online' }
      }
      return { 
        status: 'error',
        error: `健康检查失败: ${response.status}`
      }
    } catch (error) {
      return {
        status: 'error',
        error: error.message
      }
    }
  }
}); 