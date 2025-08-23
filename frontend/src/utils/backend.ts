/**
 * 后端连接管理
 */
import axios from 'axios'

// API基础URL - 在开发环境使用相对路径，生产环境使用绝对路径
const API_BASE_URL = import.meta.env.DEV ? '' : 'http://localhost:8000'

/**
 * 初始化后端连接
 * 检查连接状态
 */
export async function initializeBackend() {
  try {
    // 检查后端状态
    const status = await checkBackendStatus()
    
    return {
      apiUrl: API_BASE_URL,
      status
    }
  } catch (error) {
    console.error('初始化后端连接失败:', error)
    return { 
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