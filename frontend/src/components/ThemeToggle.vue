<template>
  <div class="theme-toggle">
    <button @click="toggleThemeMenu" class="theme-toggle-button" :title="themeButtonTitle">
      <span v-if="currentTheme === 'light'" class="icon">☀️</span>
      <span v-else-if="currentTheme === 'dark'" class="icon">🌙</span>
      <span v-else class="icon">🖥️</span>
    </button>

    <div v-if="showMenu" class="theme-menu">
      <div class="theme-option" :class="{ active: selectedTheme === 'light' }" @click="setTheme('light')">
        <span class="icon">☀️</span>
        <span>亮色</span>
      </div>
      <div class="theme-option" :class="{ active: selectedTheme === 'dark' }" @click="setTheme('dark')">
        <span class="icon">🌙</span>
        <span>暗色</span>
      </div>
      <div class="theme-option" :class="{ active: selectedTheme === 'system' }" @click="setTheme('system')">
        <span class="icon">🖥️</span>
        <span>跟随系统</span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'ThemeToggle',
  setup() {
    const store = useStore()
    const showMenu = ref(false)

    // 选中的主题（存储的主题）
    const selectedTheme = computed(() => store.state.theme)

    // 当前应用的主题（实际展示的主题）
    const currentTheme = computed(() => store.getters.currentTheme)

    // 主题按钮标题
    const themeButtonTitle = computed(() => {
      switch (selectedTheme.value) {
        case 'light': return '当前：亮色主题'
        case 'dark': return '当前：暗色主题'
        default: return '当前：跟随系统'
      }
    })

    // 切换主题菜单显示状态
    const toggleThemeMenu = () => {
      showMenu.value = !showMenu.value
    }

    // 设置主题
    const setTheme = (theme) => {
      store.dispatch('setTheme', theme)
      showMenu.value = false
    }

    // 点击外部关闭菜单
    const handleClickOutside = (event) => {
      const themeToggle = event.target.closest('.theme-toggle')
      if (!themeToggle && showMenu.value) {
        showMenu.value = false
      }
    }

    onMounted(() => {
      document.addEventListener('click', handleClickOutside)
    })

    onUnmounted(() => {
      document.removeEventListener('click', handleClickOutside)
    })

    return {
      showMenu,
      selectedTheme,
      currentTheme,
      themeButtonTitle,
      toggleThemeMenu,
      setTheme
    }
  }
}
</script>

<style lang="scss" scoped>
.theme-toggle {
  position: relative;
  display: inline-block;
}

.theme-toggle-button {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  background: var(--button-gradient);
  border: none;
  box-shadow: 0 4px 12px var(--button-shadow);
  transition: all 0.3s ease;
  padding: 0;
  position: relative;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px var(--button-shadow);
  }

  .icon {
    font-size: 22px;
  }
}

.theme-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 12px;
  background: var(--card-bg);
  border-radius: 12px;
  box-shadow: 0 8px 24px var(--shadow-color);
  padding: 12px;
  width: 160px;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

.theme-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s ease;
  color: var(--text-primary);

  &:hover {
    background: var(--input-bg);
  }

  &.active {
    background: var(--accent-color-light);
    color: var(--accent-color);
    font-weight: 500;
  }

  .icon {
    font-size: 18px;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .theme-toggle-button {
    width: 42px;
    height: 42px;

    .icon {
      font-size: 20px;
    }
  }

  .theme-menu {
    width: 150px;
    right: -10px;
  }

  .theme-option {
    padding: 10px;
    font-size: 15px;
  }
}

@media (max-width: 576px) {
  .theme-toggle-button {
    width: 38px;
    height: 38px;

    .icon {
      font-size: 18px;
    }
  }

  .theme-menu {
    width: 140px;
  }
}
</style>