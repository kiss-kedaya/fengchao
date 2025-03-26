<template>
  <div class="app-container" :class="{ 'dark-theme': isDarkTheme }">
    <!-- 添加光效元素 -->
    <div class="glow-container">
      <div class="glow-circle glow-circle-1"></div>
      <div class="glow-circle glow-circle-2"></div>
      <div class="glow-orb glow-orb-1"></div>
      <div class="glow-orb glow-orb-2"></div>
      <div class="glow-orb glow-orb-3"></div>
    </div>
    
    <!-- 添加浮动粒子 -->
    <div class="particles-container">
      <div v-for="n in 20" :key="n" class="particle" :style="getRandomParticleStyle()"></div>
    </div>
    
    <div class="app-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>
  </div>
</template>

<script>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'App',
  setup() {
    const store = useStore()

    // 获取当前主题
    const isDarkTheme = computed(() => {
      return store.getters.currentTheme === 'dark'
    })

    // 监听系统主题变化
    const handleSystemThemeChange = (e) => {
      if (store.state.theme === 'system') {
        // 触发重新计算主题
        store.dispatch('setTheme', 'system')
      }
    }

    // 生成随机粒子样式
    const getRandomParticleStyle = () => {
      const size = Math.floor(Math.random() * 20) + 5
      const posX = Math.random() * 100
      const posY = Math.random() * 100
      const duration = Math.random() * 30 + 20
      const delay = Math.random() * 10
      const opacity = Math.random() * 0.5 + 0.1
      
      return {
        width: `${size}px`,
        height: `${size}px`,
        left: `${posX}%`,
        top: `${posY}%`,
        animation: `float ${duration}s infinite ease-in-out ${delay}s`,
        opacity: opacity
      }
    }

    onMounted(() => {
      // 初始化主题
      store.dispatch('initTheme')

      // 监听系统主题变化
      window.matchMedia('(prefers-color-scheme: dark)')
        .addEventListener('change', handleSystemThemeChange)
    })

    onUnmounted(() => {
      // 移除监听器
      window.matchMedia('(prefers-color-scheme: dark)')
        .removeEventListener('change', handleSystemThemeChange)
    })

    return {
      isDarkTheme,
      getRandomParticleStyle
    }
  }
}
</script>

<style lang="scss">
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

:root {
  /* 亮色主题变量 - 修改为磨砂白色风格 */
  --bg-primary: linear-gradient(135deg, #f9fafb, #f3f4f6);
  --bg-secondary: rgba(255, 255, 255, 0.85);
  --text-primary: #1f2937;
  --text-secondary: #4b5563;
  --border-color: rgba(229, 231, 235, 0.7);
  --shadow-color: rgba(0, 0, 0, 0.1);
  --card-bg: rgba(255, 255, 255, 0.8);
  --input-bg: rgba(249, 250, 251, 0.9);
  --button-gradient: linear-gradient(135deg, #8b5cf6, #6d28d9);
  --button-text: white;
  --button-shadow: rgba(139, 92, 246, 0.3);
  --accent-color: #8b5cf6;
  --accent-color-light: rgba(139, 92, 246, 0.2);
  --header-bg: rgba(255, 255, 255, 0.85);
  --tab-active-bg: #8b5cf6;
  --card-hover-shadow: rgba(0, 0, 0, 0.12);
  --pending-status: #0ea5e9;
  --completed-status: #22c55e;
  --overdue-status: #ef4444;
  --expiring-status: #f97316;
  --unpaid-status: #f59e0b;
  
  /* 发光效果颜色 */
  --glow-1: rgba(139, 92, 246, 0.3);
  --glow-2: rgba(109, 40, 217, 0.2);
  --glow-3: rgba(255, 255, 255, 0.8);
  --glow-4: rgba(249, 250, 251, 0.6);
  --glow-5: rgba(139, 92, 246, 0.2);
}

.dark-theme {
  /* 暗色主题变量 */
  --bg-primary: linear-gradient(135deg, #1e1b4b, #111827);
  --bg-secondary: rgba(31, 41, 55, 0.85);
  --text-primary: #f9fafb;
  --text-secondary: #d1d5db;
  --border-color: rgba(75, 85, 99, 0.5);
  --shadow-color: rgba(0, 0, 0, 0.4);
  --card-bg: rgba(31, 41, 55, 0.75);
  --input-bg: rgba(55, 65, 81, 0.8);
  --button-gradient: linear-gradient(135deg, #7c3aed, #4338ca);
  --button-text: #f9fafb;
  --button-shadow: rgba(124, 58, 237, 0.4);
  --accent-color: #a78bfa;
  --accent-color-light: rgba(167, 139, 250, 0.2);
  --header-bg: rgba(31, 41, 55, 0.75);
  --tab-active-bg: #7c3aed;
  --card-hover-shadow: rgba(0, 0, 0, 0.4);
  --pending-status: #38bdf8;
  --completed-status: #4ade80;
  --overdue-status: #f87171;
  --expiring-status: #fb923c;
  --unpaid-status: #fbbf24;
  
  /* 发光效果颜色 */
  --glow-1: rgba(124, 58, 237, 0.4);
  --glow-2: rgba(55, 48, 163, 0.3);
  --glow-3: rgba(167, 139, 250, 0.35);
  --glow-4: rgba(99, 102, 241, 0.3);
  --glow-5: rgba(124, 58, 237, 0.25);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Poppins', sans-serif;
  color: var(--text-primary);
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  transition: color 0.3s ease;
  background-color: #111827; /* 默认暗色背景，防止加载时闪烁 */
}

/* 背景和光效容器 */
.app-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--bg-primary);
  position: relative;
  overflow: hidden;
  z-index: 0;
}

/* 光晕效果容器 */
.glow-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  overflow: hidden;
  pointer-events: none;
}

/* 大型光晕圆圈 */
.glow-circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.5;
}

.glow-circle-1 {
  top: -20%;
  right: -10%;
  width: 80vh;
  height: 80vh;
  background: var(--glow-1);
  animation: pulse 15s infinite alternate;
}

.glow-circle-2 {
  bottom: -30%;
  left: -15%;
  width: 90vh;
  height: 90vh;
  background: var(--glow-2);
  animation: pulse 18s infinite alternate-reverse;
}

/* 小型光球 */
.glow-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(30px);
  opacity: 0.6;
}

.glow-orb-1 {
  top: 25%;
  left: 10%;
  width: 15vw;
  height: 15vw;
  background: var(--glow-3);
  animation: float 20s infinite ease-in-out;
}

.glow-orb-2 {
  top: 65%;
  right: 20%;
  width: 12vw;
  height: 12vw;
  background: var(--glow-4);
  animation: float 25s infinite ease-in-out 5s;
}

.glow-orb-3 {
  top: 40%;
  right: 30%;
  width: 8vw;
  height: 8vw;
  background: var(--glow-5);
  animation: float 18s infinite ease-in-out 2s;
}

/* 粒子效果 */
.particles-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  overflow: hidden;
  pointer-events: none;
}

.particle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  box-shadow: 0 0 10px 2px rgba(255, 255, 255, 0.3);
  pointer-events: none;
}

/* 内容容器 - 添加玻璃态效果 */
.app-content {
  width: 90%;
  max-width: 1200px;
  height: 90%;
  background: var(--bg-secondary);
  border-radius: 16px;
  box-shadow: 0 10px 30px var(--shadow-color);
  overflow: hidden;
  transition: all 0.3s ease;
  position: relative;
  z-index: 2;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

button {
  background: var(--button-gradient);
  color: var(--button-text);
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px var(--button-shadow);
  backdrop-filter: blur(5px);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px var(--button-shadow);
  }

  &:active {
    transform: translateY(0);
  }
}

input {
  background: var(--input-bg);
  border: 1px solid var(--border-color);
  padding: 12px 16px;
  border-radius: 8px;
  color: var(--text-primary);
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);

  &:focus {
    outline: none;
    border-color: var(--accent-color);
    box-shadow: 0 0 0 3px var(--accent-color-light);
  }

  &::placeholder {
    color: var(--text-secondary);
  }
}

.card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 20px var(--shadow-color);
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.1);

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px var(--card-hover-shadow);
  }
}

.icon-container {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 16px;
  background: var(--input-bg);
  transition: all 0.3s ease;
}

/* 动画效果 */
@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.05);
    opacity: 0.7;
  }
  100% {
    transform: scale(1);
    opacity: 0.5;
  }
}

@keyframes float {
  0% {
    transform: translateY(0) translateX(0);
  }
  25% {
    transform: translateY(-20px) translateX(10px);
  }
  50% {
    transform: translateY(0) translateX(20px);
  }
  75% {
    transform: translateY(20px) translateX(10px);
  }
  100% {
    transform: translateY(0) translateX(0);
  }
}

/* 媒体查询适配 */
@media (max-width: 768px) {
  .glow-circle-1, .glow-circle-2 {
    width: 60vh;
    height: 60vh;
  }
  
  .glow-orb-1, .glow-orb-2, .glow-orb-3 {
    width: 20vw;
    height: 20vw;
  }
}
</style>