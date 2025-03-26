import { createStore } from 'vuex'
import axios from 'axios'

export default createStore({
  state: {
    phoneNumber: '',
    verificationParams: null,
    authorization: localStorage.getItem('authorization') || '',
    userId: localStorage.getItem('userId') || '',
    completedOrders: [],
    pendingOrders: [],
    userInfo: JSON.parse(localStorage.getItem('userInfo')) || null,
    theme: localStorage.getItem('theme') || 'system' // 'light', 'dark', 'system'
  },
  mutations: {
    SET_PHONE_NUMBER(state, phoneNumber) {
      state.phoneNumber = phoneNumber
    },
    SET_VERIFICATION_PARAMS(state, params) {
      state.verificationParams = params
    },
    SET_AUTH(state, { authorization, userId }) {
      state.authorization = authorization
      state.userId = userId
      localStorage.setItem('authorization', authorization)
      localStorage.setItem('userId', userId)
    },
    SET_COMPLETED_ORDERS(state, { orders, reset }) {
      if (reset) {
        state.completedOrders = orders;
      } else {
        state.completedOrders = [...state.completedOrders, ...orders];
      }
    },
    SET_PENDING_ORDERS(state, { orders, reset }) {
      if (reset) {
        state.pendingOrders = orders;
      } else {
        state.pendingOrders = [...state.pendingOrders, ...orders];
      }
    },
    SET_USER_INFO(state, userInfo) {
      state.userInfo = userInfo
      localStorage.setItem('userInfo', JSON.stringify(userInfo))
    },
    SET_THEME(state, theme) {
      state.theme = theme
      localStorage.setItem('theme', theme)
    },
    LOGOUT(state) {
      state.authorization = ''
      state.userId = ''
      state.completedOrders = []
      state.pendingOrders = []
      state.userInfo = null
      localStorage.removeItem('authorization')
      localStorage.removeItem('userId')
      localStorage.removeItem('userInfo')
    }
  },
  actions: {
    async sendVerificationCode({ commit, state }, { phoneNumber, sliderTicket = '', sliderRandstr = '' }) {
      try {
        const response = await axios.post('/send_verification_code', {
          phoneNumber,
          sliderTicket,
          sliderRandstr
        })

        if (response.data.success) {
          commit('SET_PHONE_NUMBER', phoneNumber)
          commit('SET_VERIFICATION_PARAMS', response.data.params)
          return { success: true, data: response.data }
        }

        return { success: false, error: '验证码发送失败' }
      } catch (error) {
        console.error('发送验证码错误:', error)
        return { success: false, error: error.message }
      }
    },

    async login({ commit, state }, verificationCode) {
      try {
        if (!state.verificationParams) {
          return { success: false, error: '验证参数丢失，请重新获取验证码' }
        }

        const response = await axios.post('/login', {
          phoneNumber: state.phoneNumber,
          verificationCode,
          rsaPublicKey: state.verificationParams.rsa_public_key,
          clientIp: state.verificationParams.client_ip,
          requestCode: state.verificationParams.request_code,
          timestamp: state.verificationParams.timestamp
        })

        if (response.data.success) {
          const userId = response.data.data.data.userId
          commit('SET_AUTH', {
            authorization: response.data.authorization,
            userId
          })
          commit('SET_USER_INFO', response.data.data.data)
          return { success: true }
        }

        return { success: false, error: '登录失败' }
      } catch (error) {
        console.error('登录错误:', error)
        return { success: false, error: error.message }
      }
    },

    setTheme({ commit }, theme) {
      commit('SET_THEME', theme)
    },

    initTheme({ commit, state }) {
      // 检测是否支持系统主题
      const supportsDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches
      const supportsLightMode = window.matchMedia('(prefers-color-scheme: light)').matches
      const supportsColorScheme = supportsDarkMode || supportsLightMode
      
      // 如果是系统主题，但不支持系统主题检测，则默认使用亮色主题
      if (state.theme === 'system' && !supportsColorScheme) {
        commit('SET_THEME', 'light')
      }
    },

    async fetchCompletedOrders({ commit, state }, { page = 1, reset = false } = {}) {
      try {
        const response = await axios.get('/completed_orders', {
          headers: {
            Authorization: state.authorization
          },
          params: {
            page,
            limit: 10 // 每页10条
          }
        });

        console.log('已取订单响应:', response.data);

        if (response.data.success) {
          const orders = Array.isArray(response.data.data) ? response.data.data : [];
          commit('SET_COMPLETED_ORDERS', {
            orders,
            reset: reset || page === 1
          });

          return {
            success: true,
            hasMore: orders.length === 10 // 如果返回了10条，认为还有更多
          };
        }

        return { success: false, hasMore: false };
      } catch (error) {
        console.error('获取已完成订单错误:', error);
        return { success: false, hasMore: false };
      }
    },

    async fetchPendingOrders({ commit, state }, { page = 1, reset = false } = {}) {
      try {
        const response = await axios.get('/pending_orders', {
          headers: {
            Authorization: state.authorization
          },
          params: {
            page,
            limit: 10 // 每页10条
          }
        });

        console.log('待取订单响应:', response.data);

        if (response.data.success) {
          const orders = response.data.data?.data || response.data.data || [];
          commit('SET_PENDING_ORDERS', {
            orders,
            reset: reset || page === 1
          });

          return {
            success: true,
            hasMore: orders.length === 10 // 如果返回了10条，认为还有更多
          };
        }

        return { success: false, hasMore: false };
      } catch (error) {
        console.error('获取待处理订单错误:', error);
        return { success: false, hasMore: false };
      }
    },

    logout({ commit }) {
      commit('LOGOUT')
    }
  },
  getters: {
    isAuthenticated: state => !!state.authorization,
    currentTheme: (state) => {
      if (state.theme === 'system') {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
      }
      return state.theme
    }
  }
}) 