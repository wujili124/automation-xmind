import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// 为了支持组件内使用ElMessage等方法
import 'element-plus/es/components/message/style/css'
import 'element-plus/es/components/message-box/style/css'

const app = createApp(App)

app.use(router)

app.mount('#app')
