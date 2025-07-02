import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import UploadView from '../views/UploadView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/upload'
    },
    {
      path: '/upload',
      name: 'upload',
      component: UploadView,
      meta: { title: '上传XMind文件' }
    },
    {
      path: '/analyze',
      name: 'analyze',
      component: () => import('../views/AnalyzeView.vue'),
      meta: { title: '分析结果' }
    },
    {
      path: '/export',
      name: 'export',
      component: () => import('../views/ExportView.vue'),
      meta: { title: '导出冒烟用例' }
    },
  ],
})

export default router
