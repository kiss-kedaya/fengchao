// 导入环境变量兼容层
import './env'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import axios from 'axios'

// 设置axios默认配置
axios.defaults.baseURL = '/api'  // 使用相对路径，将通过Vite代理到后端

const app = createApp(App)

app.config.globalProperties.$axios = axios

app.use(store).use(router).mount('#app') 