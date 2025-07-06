/**
 * 后端连接管理
 */
import axios from 'axios'

// 默认API基础URL
let API_BASE_URL = 'http://localhost:8000'

// 是否在Electron环境
const isElectron = !!window.electronAPI

/**
 * 初始化后端连接
 * 获取API基础URL并检查连接状态
 */
export async function initializeBackend() {
  if (!isElectron) return { isElectron: false, apiUrl: API_BASE_URL }
  
  try {
    // 获取API基础URL
    API_BASE_URL = await window.electronAPI!.getApiBaseUrl()
    
    // 检查后端状态
    const status = await checkBackendStatus()
    
    return {
      isElectron: true,
      apiUrl: API_BASE_URL,
      status
    }
  } catch (error) {
    console.error('初始化后端连接失败:', error)
    return { 
      isElectron: true, 
      apiUrl: API_BASE_URL,
      status: {
        status: 'error' as const,
        error: '初始化连接失败'
      }
    }
  }
}

/**
 * 检查后端连接状态
 */
export async function checkBackendStatus(): Promise<BackendStatus> {
  if (!isElectron) {
    // 在浏览器环境中，直接尝试连接API
    try {
      await axios.get(`${API_BASE_URL}/health`, { timeout: 3000 })
      return { status: 'online' }
    } catch (error) {
      return { 
        status: 'offline',
        error: '无法连接到后端API'
      }
    }
  }
  
  // 在Electron环境中，使用IPC通信
  try {
    return await window.electronAPI!.checkBackendStatus()
  } catch (error) {
    return {
      status: 'error',
      error: '检查后端状态失败'
    }
  }
}

/**
 * 获取API客户端
 */
export function getApiClient() {
  return axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000
  })
}

/**
 * 获取API基础URL
 */
export function getApiBaseUrl() {
  return API_BASE_URL
} 