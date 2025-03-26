<template>
  <div class="verification-container">
    <div class="verification-card">
      <h1 class="title">输入验证码</h1>
      <p class="subtitle">验证码已发送至 {{ maskedPhone }}</p>

      <div class="code-container">
        <input v-for="(n, index) in 6" :key="index" ref="inputs" type="text" maxlength="1" class="code-input"
          v-model="codeDigits[index]" @input="handleInput(index)" @keydown="handleKeydown($event, index)"
          @paste="handlePaste" />
      </div>

      <div class="actions">
        <button class="submit-btn" @click="login" :disabled="loading || !isCompleted">
          <span v-if="loading" class="loading-spinner"></span>
          <span v-else>登录</span>
        </button>

        <div class="resend-container">
          <span v-if="countdown > 0">{{ countdown }}秒后可重新发送</span>
          <button v-else class="resend-btn" @click="resendCode" :disabled="resendLoading">
            <span v-if="resendLoading" class="loading-spinner"></span>
            <span v-else>重新发送</span>
          </button>
        </div>
      </div>

      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'VerificationCode',
  setup() {
    const store = useStore()
    const router = useRouter()

    const inputs = ref([])
    const codeDigits = ref(['', '', '', '', '', ''])
    const loading = ref(false)
    const resendLoading = ref(false)
    const errorMessage = ref('')
    const countdown = ref(60)
    let countdownTimer = null

    const phoneNumber = computed(() => store.state.phoneNumber)

    const maskedPhone = computed(() => {
      if (!phoneNumber.value) return ''
      return phoneNumber.value.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
    })

    const isCompleted = computed(() => {
      return codeDigits.value.every(digit => digit !== '') && codeDigits.value.length === 6
    })

    const verificationCode = computed(() => {
      return codeDigits.value.join('')
    })

    onMounted(() => {
      if (!phoneNumber.value) {
        router.push({ name: 'Login' })
        return
      }

      // Start countdown
      startCountdown()

      // Focus on first input
      setTimeout(() => {
        if (inputs.value[0]) {
          inputs.value[0].focus()
        }
      }, 100)
    })

    onUnmounted(() => {
      clearInterval(countdownTimer)
    })

    const startCountdown = () => {
      countdown.value = 60
      clearInterval(countdownTimer)
      countdownTimer = setInterval(() => {
        if (countdown.value > 0) {
          countdown.value--
        } else {
          clearInterval(countdownTimer)
        }
      }, 1000)
    }

    const handleInput = (index) => {
      if (codeDigits.value[index].length === 1 && index < 5) {
        inputs.value[index + 1].focus()
      }
    }

    const handleKeydown = (event, index) => {
      if (event.key === 'Backspace' && index > 0 && codeDigits.value[index] === '') {
        inputs.value[index - 1].focus()
      }
    }

    const handlePaste = (event) => {
      event.preventDefault()
      const pastedData = event.clipboardData.getData('text').trim()
      if (/^\d+$/.test(pastedData) && pastedData.length <= 6) {
        for (let i = 0; i < Math.min(pastedData.length, 6); i++) {
          codeDigits.value[i] = pastedData[i]
        }
        if (pastedData.length < 6) {
          inputs.value[pastedData.length].focus()
        }
      }
    }

    const login = async () => {
      if (!isCompleted.value) return

      errorMessage.value = ''
      loading.value = true

      try {
        const result = await store.dispatch('login', verificationCode.value)

        if (result.success) {
          router.push({ name: 'Orders' })
        } else {
          errorMessage.value = result.error || '登录失败，请稍后再试'
        }
      } catch (error) {
        errorMessage.value = '系统错误，请稍后再试'
      } finally {
        loading.value = false
      }
    }

    const resendCode = async () => {
      errorMessage.value = ''
      resendLoading.value = true

      try {
        const result = await store.dispatch('sendVerificationCode', {
          phoneNumber: phoneNumber.value
        })

        if (result.success) {
          startCountdown()
        } else {
          errorMessage.value = result.error || '发送验证码失败，请稍后再试'
        }
      } catch (error) {
        errorMessage.value = '系统错误，请稍后再试'
      } finally {
        resendLoading.value = false
      }
    }

    return {
      inputs,
      codeDigits,
      loading,
      resendLoading,
      errorMessage,
      countdown,
      maskedPhone,
      isCompleted,
      handleInput,
      handleKeydown,
      handlePaste,
      login,
      resendCode
    }
  }
}
</script>

<style lang="scss" scoped>
.verification-container {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.verification-card {
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

.icon-container {
  align-self: center;
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
  margin-bottom: 16px;
}

.title {
  text-align: center;
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.subtitle {
  text-align: center;
  font-size: 16px;
  color: var(--text-secondary);
  margin-bottom: 20px;

  .highlight {
    font-weight: 600;
    color: var(--accent-color);
  }
}

.verification-input {
  margin-bottom: 20px;
  
  input {
    font-size: 18px;
    letter-spacing: 2px;
    text-align: center;
  }
}

.timer {
  font-size: 14px;
  text-align: center;
  margin-bottom: 16px;
  color: var(--text-secondary);
}

.resend-btn {
  background: none;
  border: none;
  padding: 0;
  font-size: 14px;
  color: var(--accent-color);
  cursor: pointer;
  box-shadow: none;
  
  &:disabled {
    color: var(--text-secondary);
    cursor: default;
  }
  
  &:hover:not(:disabled) {
    text-decoration: underline;
  }
}

.verify-btn {
  width: 100%;
  padding: 14px;
  font-size: 16px;
  
  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
}

.back-btn {
  background: none;
  border: none;
  padding: 10px;
  font-size: 14px;
  color: var(--text-secondary);
  cursor: pointer;
  margin-top: 16px;
  align-self: center;
  box-shadow: none;
  
  &:hover {
    color: var(--text-primary);
    transform: none;
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
</style>