/// <reference types="vite/client" />

// 为Vue组件提供类型支持
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

// Electron API 类型定义
interface ElectronAPI {
  getApiBaseUrl: () => Promise<string>;
  // 可以在这里添加更多的API方法
}

// 扩展Window接口，添加electronAPI属性
interface Window {
  electronAPI?: ElectronAPI;
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