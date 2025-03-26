<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="title">丰巢快递</h1>
      <div class="logo-container">
        <div class="logo">巢</div>
      </div>
      <div class="form-group">
        <label for="phone">手机号码</label>
        <input type="tel" id="phone" v-model="phoneNumber" placeholder="请输入手机号码" maxlength="11" />
      </div>
      <button class="submit-btn" @click="sendVerificationCode" :disabled="loading">
        <span v-if="loading" class="loading-spinner"></span>
        <span v-else>获取验证码</span>
      </button>
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'Login',
  setup() {
    const store = useStore()
    const router = useRouter()

    const phoneNumber = ref('')
    const loading = ref(false)
    const errorMessage = ref('')

    const validatePhoneNumber = (phone) => {
      const phoneRegex = /^1[3-9]\d{9}$/
      return phoneRegex.test(phone)
    }

    const sendVerificationCode = async () => {
      errorMessage.value = ''

      if (!phoneNumber.value) {
        errorMessage.value = '请输入手机号码'
        return
      }

      if (!validatePhoneNumber(phoneNumber.value)) {
        errorMessage.value = '请输入有效的手机号码'
        return
      }

      loading.value = true

      try {
        const result = await store.dispatch('sendVerificationCode', {
          phoneNumber: phoneNumber.value
        })

        if (result.success) {
          router.push({ name: 'Verification' })
        } else {
          errorMessage.value = result.error || '发送验证码失败，请稍后再试'
        }
      } catch (error) {
        errorMessage.value = '系统错误，请稍后再试'
      } finally {
        loading.value = false
      }
    }

    return {
      phoneNumber,
      loading,
      errorMessage,
      sendVerificationCode
    }
  }
}
</script>

<style lang="scss" scoped>
.login-container {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: 40px;
  background: var(--bg-secondary);
  border-radius: 16px;
  box-shadow: 0 10px 30px var(--shadow-color);
  display: flex;
  flex-direction: column;
  gap: 24px;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 40px var(--card-hover-shadow);
  }
}

.title {
  text-align: center;
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 10px;
  background: var(--button-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.logo-container {
  display: flex;
  justify-content: center;
  margin-bottom: 10px;
}

.logo {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--button-gradient);
  font-size: 28px;
  font-weight: bold;
  color: var(--button-text);
  box-shadow: 0 10px 25px var(--button-shadow);
  animation: pulse 3s infinite;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;

  label {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-secondary);
  }

  input {
    width: 100%;
  }
}

.submit-btn {
  width: 100%;
  padding: 14px;
  font-size: 16px;
  margin-top: 10px;
  position: relative;
  overflow: hidden;
  z-index: 1;

  &:before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: all 0.6s;
    z-index: -1;
  }

  &:hover:before {
    left: 100%;
  }

  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
}

.error-message {
  color: var(--overdue-status);
  font-size: 14px;
  text-align: center;
  margin-top: 10px;
}

.loading-spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: var(--button-text);
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 var(--button-shadow);
  }

  70% {
    box-shadow: 0 0 0 10px rgba(99, 102, 241, 0);
  }

  100% {
    box-shadow: 0 0 0 0 rgba(99, 102, 241, 0);
  }
}
</style>