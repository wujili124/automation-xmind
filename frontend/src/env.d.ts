/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

// 为Vue组件提供类型支持
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

// 后端状态类型定义
interface BackendStatus {
  status: 'online' | 'offline' | 'error' | 'timeout' | 'unknown'
  error?: string
  statusCode?: number
  checked?: boolean
}

// 解决VLS相关错误的声明
declare namespace __VLS {
  interface GlobalComponents {}
  interface ComponentCustomProperties {}
  interface SelfComponent {}
  interface PickNotAny {}
  interface FunctionalComponentProps {}
  interface ElementAsFunctionalComponent {}
  interface IntrinsicElements {}
} 