<template>
  <div class="orders-container">
    <div class="header">
      <div class="user-info">
        <div class="avatar">{{ userInitial }}</div>
        <div class="user-details">
          <h3>{{ userNickName }}</h3>
          <p>{{ userMobile }}</p>
        </div>
      </div>
      <div class="header-actions">
        <theme-toggle class="header-theme-toggle" />
        <button class="logout-btn" @click="logout">退出登录</button>
      </div>
    </div>

    <div class="tabs">
      <button class="tab-btn" :class="{ active: activeTab === 'pending' }" @click="setActiveTab('pending')">
        待取订单
        <span v-if="pendingCount > 0" class="badge">{{ pendingCount }}</span>
      </button>
      <button class="tab-btn" :class="{ active: activeTab === 'completed' }" @click="setActiveTab('completed')">
        已取订单
      </button>
    </div>

    <div class="content-container">
      <div v-if="loading && !loadingMore" class="loading-container">
        <div class="loading">
          <div class="loading-spinner large"></div>
          <p>加载中...</p>
        </div>
      </div>

      <div v-else-if="activeTab === 'pending' && pendingOrders.length === 0" class="empty-container">
        <div class="empty-state">
          <div class="empty-icon">📬</div>
          <p>没有待取的订单</p>
        </div>
      </div>

      <div v-else-if="activeTab === 'completed' && completedOrders.length === 0" class="empty-container">
        <div class="empty-state">
          <div class="empty-icon">📦</div>
          <p>没有已取的订单</p>
        </div>
      </div>

      <div v-else class="order-list" ref="orderListContainer" @scroll="handleScroll">
        <div class="pull-refresh-container" :class="{ 'refreshing': refreshLoading }">
          <div v-if="refreshLoading" class="pull-refresh-loading">
            <div class="loading-spinner"></div>
            <span>正在刷新...</span>
          </div>

          <template v-if="displayedOrders.length > 0">
            <div class="order-item" v-for="order in displayedOrders"
              :key="order.expressId || order.id || order.packageId" @click="openCabinetModal(order)">
              <div class="order-header">
                <div class="courier-info">
                  <div class="courier-avatar" v-if="order.companyLogoUrl">
                    <img :src="order.companyLogoUrl" alt="快递公司logo" />
                  </div>

                  <div class="courier-details">
                    <div class="courier-name">{{ order.companyName || '丰巢快递' }}</div>
                    <div class="express-no">
                      <span class="express-id clickable">{{ order.expressId || '暂无单号' }}</span>
                      <button v-if="order.expressId" class="copy-text-btn"
                        @click.stop="copyToClipboard($event, order.expressId)" title="复制单号">
                        <svg class="copy-icon" width="14" height="14" viewBox="0 0 24 24" fill="none"
                          xmlns="http://www.w3.org/2000/svg">
                          <path
                            d="M16 3H4C3.45 3 3 3.45 3 4V16C3 16.55 3.45 17 4 17H5V5C5 4.45 5.45 4 6 4H18V3C18 3.45 17.55 3 17 3H16Z"
                            fill="currentColor" />
                          <path
                            d="M20 7H8C7.45 7 7 7.45 7 8V20C7 20.55 7.45 21 8 21H20C20.55 21 21 20.55 21 20V8C21 7.45 20.55 7 20 7ZM19 19H9V9H19V19Z"
                            fill="currentColor" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
                <div class="order-status" :class="getStatusClass(order)">
                  {{ getStatusText(order) }}
                </div>
              </div>

              <div class="order-details">
                <div class="detail-row">
                  <div class="detail-item">
                    <span class="detail-label">收件人:</span>
                    <span class="detail-value">{{ order.clientMobile || '未知' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">派件员:</span>
                    <div class="detail-value clickable" @click.stop="copyToClipboard($event, order.staffMobile)"
                      title="点击复制手机号">
                      {{ order.staffMobile || '未知' }}
                      <button v-if="order.staffMobile" class="copy-text-btn" title="复制手机号">
                        <svg class="copy-icon" width="14" height="14" viewBox="0 0 24 24" fill="none"
                          xmlns="http://www.w3.org/2000/svg">
                          <path
                            d="M16 3H4C3.45 3 3 3.45 3 4V16C3 16.55 3.45 17 4 17H5V5C5 4.45 5.45 4 6 4H18V3C18 3.45 17.55 3 17 3H16Z"
                            fill="currentColor" />
                          <path
                            d="M20 7H8C7.45 7 7 7.45 7 8V20C7 20.55 7.45 21 8 21H20C20.55 21 21 20.55 21 20V8C21 7.45 20.55 7 20 7ZM19 19H9V9H19V19Z"
                            fill="currentColor" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>

                <div class="detail-row">
                  <div class="detail-item">
                    <span class="detail-label">地址:</span>
                    <span class="detail-value">{{ order.address || '未知' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">位置:</span>
                    <span class="detail-value">{{ order.boxLocation || '未知' }}</span>
                  </div>
                </div>

                <div class="detail-row">
                  <div class="detail-item">
                    <span class="detail-label">投递时间:</span>
                    <span class="detail-value">{{ formatTime(order.sendTm) }}</span>
                  </div>
                  <div class="detail-item" v-if="activeTab === 'completed'">
                    <span class="detail-label">取件时间:</span>
                    <span class="detail-value">{{ formatTime(order.pickTm) }}</span>
                  </div>
                  <div class="detail-item" v-else>
                    <span class="detail-label">取件码:</span>
                    <span class="detail-value pickup-code">{{ order.pickupCode || '无' }}</span>
                  </div>
                </div>

                <div class="detail-row custody-fee-row" v-if="order.totalCustodyFee !== 0">
                  <div class="detail-item custody-fee-item">
                    <span class="detail-label">保管费:</span>
                    <span class="fee">{{ order.totalCustodyFee / 100 }}元</span>
                    <span 
                      v-if="order.custodyFeeTag" 
                      :class="['fee-tag', order.custodyFeeTag.includes('会员免费') ? 'fee-tag-free' : '']"
                    >
                      {{ order.custodyFeeTag }}
                    </span>
                  </div>
                </div>
                <div class="action-buttons" v-if="activeTab === 'pending'">
                  <button class="open-box-btn" @click.stop="openBox(order)">打开柜门</button>
                </div>
              </div>
            </div>
          </template>
          <template v-else-if="loading">
            <div class="empty-orders-message">
              <div class="loading-spinner large"></div>
              <p>正在加载订单...</p>
            </div>
          </template>
          <template v-else>
            <div class="empty-orders-message">
              <div class="empty-icon">📦</div>
              <p>{{ activeTab === 'pending' ? '暂无待取快递' : '暂无已取快递' }}</p>
            </div>
          </template>

          <div v-if="displayedOrders.length > 0 && !loading" class="load-more-status">
            <template v-if="loadingMore">
              <div class="loading-spinner"></div>
              <span class="loading-more-text">正在加载更多...</span>
            </template>
            <template v-else-if="noMoreOrders">
              <span class="no-more-text">没有更多订单了</span>
            </template>
          </div>
        </div>
      </div>
    </div>

    <div class="refresh-btn-container">
      <button class="refresh-btn" @click="refreshData" :disabled="refreshLoading">
        <span v-if="refreshLoading" class="loading-spinner"></span>
        <span v-else>刷新</span>
      </button>
    </div>

    <!-- 柜机位置模态框 -->
    <div class="cabinet-modal" v-if="showCabinetModal" @click="closeCabinetModal">
      <div class="cabinet-modal-content" @click.stop>
        <div class="cabinet-modal-header">
          <h3>柜机位置</h3>
          <button class="close-btn" @click="closeCabinetModal">×</button>
        </div>

        <div class="cabinet-modal-body">
          <div v-if="cabinetLoading" class="cabinet-loading">
            <div class="loading-spinner large"></div>
            <p>正在加载柜机信息...</p>
          </div>

          <div v-else-if="cabinetError" class="cabinet-error">
            <p>{{ cabinetError }}</p>
          </div>

          <div v-else-if="cabinetData" class="cabinet-layout">
            <div class="cabinet-info">
              <h4>{{ selectedOrder?.address }}</h4>
              <p class="cabinet-address">{{ selectedOrder?.boxLocation}}</p>
            </div>

            <div class="cabinet-visualization">
              <div v-for="(cabinet, cIndex) in cabinetData.cabinets" :key="cIndex" class="cabinet-column">
                <h5>{{ cabinet.title || `${cIndex + 1}号柜` }}</h5>

                <div class="cabinet-grid" :class="{ 'cabinet-grid-double': cabinet.needsDoubleColumns }">
                  <!-- 按列显示 -->
                  <template v-for="(column, colIndex) in cabinet.columnBoxes" :key="`col-${cIndex}-${colIndex}`">
                    <div class="cabinet-column-boxes">
                      <template v-for="(box, bIndex) in column" :key="`${cIndex}-${colIndex}-${bIndex}`">
                        <div class="cabinet-box" :class="{
                          'cabinet-box-highlighted': isCurrentBox(box),
                          'cabinet-box-occupied': box.status === 'occupied' || box.status === 'current',
                          'cabinet-box-empty': box.status === 'empty',
                          'cabinet-box-other': box.status === 'other',
                          [`box-type-${box.type || 1}`]: true
                        }" :style="{
                          height: box.height ? `${Math.max(30, box.height / 5)}px` : null,
                          width: box.width ? `${Math.max(60, box.width / 5)}px` : null
                        }">
                          <span class="box-label">{{ box.label || `${bIndex + 1}行` }}</span>
                          <span v-if="box.status === 'current'" class="cabinet-current-mark">当前</span>
                        </div>
                      </template>
                    </div>
                  </template>
                </div>
              </div>
            </div>

            <div class="cabinet-legend">
              <div class="legend-item">
                <div class="legend-color current"></div>
                <span>当前快递</span>
              </div>
              <div class="legend-item">
                <div class="legend-color occupied"></div>
                <span>已占用</span>
              </div>
              <div class="legend-item">
                <div class="legend-color empty"></div>
                <span>空闲</span>
              </div>
            </div>
          </div>
        </div>

        <div class="cabinet-modal-footer">
          <button class="primary-btn" @click="closeCabinetModal">知道了</button>
        </div>
      </div>
    </div>

    <div class="copy-message" v-if="showCopyMessage">{{ copyMessage }}</div>
  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import ThemeToggle from '../components/ThemeToggle.vue'

export default {
  name: 'Orders',
  components: {
    ThemeToggle
  },
  setup() {
    const store = useStore()
    const router = useRouter()

    const activeTab = ref('pending')
    const loading = ref(true)
    const refreshLoading = ref(false)
    const loadingMore = ref(false)
    const noMoreOrders = ref(false)
    const currentPage = ref(1)
    const orderListContainer = ref(null)
    const showCabinetModal = ref(false)
    const cabinetLoading = ref(false)
    const cabinetError = ref('')
    const cabinetData = ref(null)
    const selectedOrder = ref(null)
    const copyMessage = ref('')
    const showCopyMessage = ref(false)

    const completedOrders = computed(() => {
      return store.state.completedOrders || []
    })
    const pendingOrders = computed(() => {
      return store.state.pendingOrders || []
    })
    const pendingCount = computed(() => pendingOrders.value.length)

    const displayedOrders = computed(() => {
      return activeTab.value === 'pending' ? pendingOrders.value : completedOrders.value
    })

    const userInitial = computed(() => {
      const phone = store.state.nickName || '巢'
      return phone.charAt(0).toUpperCase()
    })

    const maskedPhone = computed(() => {
      const phone = store.state.phoneNumber
      if (!phone) return '用户'
      return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
    })

    const userNickName = computed(() => {
      return store.state.userInfo?.nickName || maskedPhone.value
    })

    const userMobile = computed(() => {
      return store.state.userInfo?.mobile || '丰巢用户'
    })

    onMounted(async () => {
      if (!store.getters.isAuthenticated) {
        router.push({ name: 'Login' })
        return
      }

      await fetchData()
    })

    const fetchData = async (page = 1) => {
      if (page === 1) {
        loading.value = true
        noMoreOrders.value = false
      }

      try {
        let result
        if (activeTab.value === 'pending') {
          result = await store.dispatch('fetchPendingOrders', { page })
        } else {
          result = await store.dispatch('fetchCompletedOrders', { page })
        }

        if (page > 1) {
          if (!result || !result.success || !result.hasMore) {
            noMoreOrders.value = true
          }
        }

        currentPage.value = page
        return result
      } catch (error) {
        // 获取订单错误处理
        throw error
      } finally {
        if (page === 1) {
          loading.value = false
        }
      }
    }

    const loadMoreOrders = async () => {
      if (loadingMore.value || noMoreOrders.value) return

      loadingMore.value = true

      try {
        await fetchData(currentPage.value + 1)
      } catch (error) {
        // 加载错误处理
      } finally {
        // 确保无论如何都重置loadingMore状态
        loadingMore.value = false
      }
    }

    const handleScroll = async (event) => {
      if (loadingMore.value || noMoreOrders.value) return

      const container = event.target
      const scrollBottom = container.scrollHeight - container.scrollTop - container.clientHeight


      // 当滚动到距离底部50px时加载更多
      if (scrollBottom < 50) {
        await loadMoreOrders()
      }
    }

    const refreshData = async () => {
      refreshLoading.value = true
      currentPage.value = 1
      noMoreOrders.value = false

      try {
        await Promise.all([
          store.dispatch('fetchCompletedOrders', { page: 1, reset: true }),
          store.dispatch('fetchPendingOrders', { page: 1, reset: true })
        ])
      } catch (error) {
        // 刷新订单错误处理
      } finally {
        refreshLoading.value = false
      }
    }

    const setActiveTab = (tab) => {
      if (tab === activeTab.value) return

      activeTab.value = tab
      currentPage.value = 1
      noMoreOrders.value = false

      // 切换选项卡时重新获取数据
      nextTick(() => {
        if (orderListContainer.value) {
          orderListContainer.value.scrollTop = 0
        }
        fetchData(1)
      })
    }

    const logout = () => {
      store.dispatch('logout')
      router.push({ name: 'Login' })
    }

    const getCourierInitial = (courierName) => {
      if (!courierName) return '?'
      return courierName.charAt(0)
    }

    const getStatusClass = (order) => {
      if (activeTab.value === 'pending') {
        if (order.pickStatus === '1') {
          return 'status-overdue'
        } else if (order.pickStatus === '2') {
          return 'status-expiring'
        } else {
          return 'status-pending'
        }
      } else {
        if (order.expressStatus === '2' && order.payStatus === '0' && parseFloat(order.actualFee || 0) > 0) {
          return 'status-unpaid'
        } else {
          return 'status-completed'
        }
      }
    }

    const getStatusText = (order) => {
      if (activeTab.value === 'pending') {
        if (order.pickStatus === '1') {
          return '已逾期'
        } else if (order.pickStatus === '2') {
          return '即将过期'
        } else {
          return order.pickStatusDesc || '待取件'
        }
      } else {
        if (order.expressStatus === '2' && order.payStatus === '1' && parseFloat(order.actualFee || 0) > 0) {
          return '已支付'
        } else if (order.expressStatus === '2' && order.payStatus === '0' && parseFloat(order.actualFee || 0) > 0) {
          return '未支付'
        } else {
          return order.pickStatusDesc || '已取件'
        }
      }
    }

    const formatTime = (timestamp) => {
      if (!timestamp) return '未知'

      try {
        if (typeof timestamp === 'string') {
          if (timestamp.includes('-') && timestamp.includes(':')) {
            return timestamp
          }

          if (!isNaN(timestamp)) {
            timestamp = parseInt(timestamp)
          }
        }

        if (typeof timestamp === 'number') {
          if (timestamp.toString().length === 10) {
            timestamp *= 1000
          }

          const date = new Date(timestamp)
          return `${date.getFullYear()}-${padZero(date.getMonth() + 1)}-${padZero(date.getDate())} ${padZero(date.getHours())}:${padZero(date.getMinutes())}`
        }

        return timestamp
      } catch (e) {
        return timestamp
      }
    }

    const padZero = (num) => {
      return num.toString().padStart(2, '0')
    }

    const openCabinetModal = async (order) => {
      selectedOrder.value = order
      showCabinetModal.value = true
      cabinetLoading.value = true
      cabinetError.value = ''
      cabinetData.value = null

      try {
        // 修正API URL和请求参数
        const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:5000'
        const apiURL = `${baseURL}/post/clientGet/cabinetVisualInfo`

        // 准备请求头
        const headers = {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Authorization': store.state.token || localStorage.getItem('authorization') || ''
        }

        // 准备表单数据
        const formData = new URLSearchParams()
        formData.append('cabinetCode', order.boxName || '')

        const response = await fetch(`${baseURL}/cabinet_location`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': store.state.token || localStorage.getItem('authorization') || ''
          },
          body: JSON.stringify({
            expressId: order.expressId,
            boxId: order.boxNo,
            cabinetCode: order.boxName
          })
        })

        if (!response.ok) {
          throw new Error(`服务器返回错误状态码: ${response.status}`)
        }

        const result = await response.json()

        if (result.success && result.data) {
          cabinetData.value = processLocationData(result.data, order)
          cabinetLoading.value = false
        } else {
          throw new Error(result.message || '获取柜机位置失败')
        }
      } catch (error) {
        cabinetError.value = '无法获取柜机位置信息'
        cabinetLoading.value = false
      }
    }

    const closeCabinetModal = () => {
      showCabinetModal.value = false
    }

    const openBox = async (order) => {
      try {
        // 显示确认对话框
        if (!confirm(`确定要打开柜门取出${order.companyName}的快递吗？`)) {
          return
        }

        // 构建请求参数
        const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:5000'
        const openBoxData = {
          cabinetCode: order.boxName || order.cabinetCode,
          boxId: order.boxNo || order.boxId,
          expressId: order.expressId,
          clientMobile: order.clientMobile,
          staffMobile: order.staffMobile,
          companyLogoUrl: order.companyLogoUrl,
          companyName: order.companyName,
          expressType: order.expressType || 1,
          postId: order.postId,
          code: order.pickupCode || order.code,
          boxGlobalRow: order.boxGlobalRow,
          address: order.address
        }

        // 显示加载状态
        const originalText = event.target.innerText
        event.target.innerText = '开柜中...'
        event.target.disabled = true

        // 调用开柜API
        const response = await fetch(`${baseURL}/openBox`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': store.state.token || localStorage.getItem('authorization') || ''
          },
          body: JSON.stringify(openBoxData)
        })

        // 恢复按钮状态
        event.target.innerText = originalText
        event.target.disabled = false

        if (!response.ok) {
          throw new Error(`服务器返回错误状态码: ${response.status}`)
        }

        const result = await response.json()

        if (result.success) {
          // 开柜成功
          alert('开柜成功，请取出您的快递！')
          // 刷新订单列表
          await refreshData()
        } else {
          // 开柜失败
          alert(`开柜失败: ${result.message || '未知错误'}`)
        }
      } catch (error) {
        alert('开柜操作失败，请稍后重试')
        event.target.innerText = '打开柜门'
        event.target.disabled = false
      }
    }

    const processLocationData = (data, order) => {
      const result = {
        title: '柜机屏幕',
        subtitle: '左侧',
        cabinets: []
      }

      if (!data) {
        cabinetError.value = '服务器返回的数据为空'
        return null
      }

      try {
        if (data.viceList && Array.isArray(data.viceList)) {
          const cabinetMap = {}
          const currentBoxNumber = order.boxNo || ''

          data.viceList.forEach(vice => {
            let cabinetName = '';
            if (vice.vicePosition === 'Z00') {
              cabinetName = '主柜';
            } else if (vice.vicePosition === 'L01') {
              cabinetName = '左1柜';
            } else if (vice.vicePosition === 'R01') {
              cabinetName = '右1柜';
            } else if (vice.vicePosition === 'R02') {
              cabinetName = '右2柜';
            } else {
              cabinetName = `${vice.vicePosition}柜`;
            }

            const cabinet = {
              title: cabinetName,
              boxes: [],
              columns: {}
            }

            if (vice.cellList && Array.isArray(vice.cellList)) {
              vice.cellList.forEach(cell => {
                const column = cell.cellColumn || 1;
                if (!cabinet.columns[column]) {
                  cabinet.columns[column] = [];
                }
                cabinet.columns[column].push(cell);
              });

              Object.keys(cabinet.columns).forEach(column => {
                cabinet.columns[column].sort((a, b) => (a.cellRow || 0) - (b.cellRow || 0));
              });

              const maxRowsPerColumn = 11;
              const hasLongColumns = Object.values(cabinet.columns).some(column => column.length > maxRowsPerColumn);
              cabinet.needsDoubleColumns = hasLongColumns;

              Object.entries(cabinet.columns).forEach(([columnKey, columnCells]) => {
                const columnBoxes = [];
                columnCells.forEach(cell => {
                  const cellId = cell.cellId;
                  let status = 'empty';
                  if (cellId === currentBoxNumber) {
                    status = 'current';
                  } else if (cell.cellStatus === '2' || cell.cellStatus === 2) {
                    status = 'occupied';
                  }

                  const boxData = {
                    label: `${cell.cellRow || ''}行`,
                    status: status,
                    boxId: cell.cellRow,
                    cellNo: cellId,
                    column: cell.cellColumn,
                    width: cell.cellWidth,
                    height: cell.cellHeight,
                    type: cell.cellType
                  }

                  columnBoxes.push(boxData);
                });

                cabinet.columns[columnKey] = columnBoxes;
                cabinet.boxes.push(...columnBoxes);
              });

              cabinet.columnBoxes = Object.values(cabinet.columns);
            }

            if (cabinet.boxes.length > 0) {
              cabinetMap[vice.vicePosition] = cabinet;
            }
          });

          const positionOrder = ['L01', 'Z00', 'R01', 'R02'];
          positionOrder.forEach(position => {
            if (cabinetMap[position]) {
              result.cabinets.push(cabinetMap[position]);
            }
          });

          if (result.cabinets.length === 0) {
            cabinetError.value = '找不到有效的柜机数据';
            return null;
          }
        } else {
          cabinetError.value = '服务器返回的数据格式不正确';
          return null;
        }
      } catch (error) {
        cabinetError.value = '处理柜机数据时出错';
        return null;
      }

      return result;
    }

    const isCurrentBox = (box) => {
      // 检查是否是当前包裹所在的箱格
      if (!selectedOrder.value || !box) return false

      // 获取当前订单的箱格编号
      const currentBoxNo = selectedOrder.value.boxNo || '';

      // 直接比较cellNo和当前箱格编号，不使用其他模糊匹配
      return box.status === 'current' || (box.cellNo === currentBoxNo);
    }

    const copyToClipboard = (event, text) => {
      // 阻止事件冒泡，避免触发父元素的点击事件
      event.stopPropagation()

      if (!text || text === '未知' || text === '暂无单号') return

      navigator.clipboard.writeText(text)
        .then(() => {
          // 显示复制成功消息
          copyMessage.value = `已复制: ${text}`
          showCopyMessage.value = true

          // 3秒后隐藏消息
          setTimeout(() => {
            showCopyMessage.value = false
          }, 3000)
        })
        .catch(err => {
          // 使用备用方法复制
          fallbackCopyToClipboard(text)
        })
    }

    const fallbackCopyToClipboard = (text) => {
      // 创建临时文本区域
      const textArea = document.createElement("textarea")
      textArea.value = text

      // 使元素不可见但存在于DOM中
      textArea.style.position = "fixed"
      textArea.style.left = "-999999px"
      textArea.style.top = "-999999px"
      document.body.appendChild(textArea)

      // 选择文本并尝试复制
      textArea.focus()
      textArea.select()

      try {
        const successful = document.execCommand('copy')
        if (successful) {
          copyMessage.value = `已复制: ${text}`
          showCopyMessage.value = true

          setTimeout(() => {
            showCopyMessage.value = false
          }, 3000)
        }
      } catch (err) {
        // 备用复制失败
      }

      // 清理
      document.body.removeChild(textArea)
    }

    return {
      activeTab,
      loading,
      loadingMore,
      noMoreOrders,
      refreshLoading,
      completedOrders,
      pendingOrders,
      pendingCount,
      displayedOrders,
      userInitial,
      maskedPhone,
      userNickName,
      userMobile,
      setActiveTab,
      refreshData,
      logout,
      getCourierInitial,
      getStatusClass,
      getStatusText,
      formatTime,
      index: (i) => i,
      handleScroll,
      orderListContainer,
      showCabinetModal,
      cabinetLoading,
      cabinetError,
      cabinetData,
      selectedOrder,
      openCabinetModal,
      closeCabinetModal,
      isCurrentBox,
      copyToClipboard,
      copyMessage,
      showCopyMessage,
      openBox
    }
  }
}
</script>

<style lang="scss" scoped>
.orders-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg-primary);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
  background: var(--header-bg);
  box-shadow: 0 2px 10px var(--shadow-color);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: var(--button-gradient);
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 20px;
  font-weight: bold;
  color: var(--button-text);
  box-shadow: 0 4px 10px var(--button-shadow);
}

.user-details {
  h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
  }

  p {
    margin: 0;
    font-size: 14px;
    color: var(--text-secondary);
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-theme-toggle {
  display: inline-flex;
}

.logout-btn {
  background: var(--input-bg);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px var(--shadow-color);

  &:hover {
    background: var(--border-color);
    transform: translateY(-2px);
  }
}

.tabs {
  display: flex;
  padding: 0 20px;
  border-bottom: 1px solid var(--border-color);
  background: var(--header-bg);
}

.tab-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  padding: 10px 20px;
  font-size: 16px;
  font-weight: 500;
  position: relative;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: none;

  &:hover {
    color: var(--accent-color);
  }

  &.active {
    color: var(--accent-color);

    &:after {
      content: '';
      position: absolute;
      bottom: -1px;
      left: 0;
      width: 100%;
      height: 3px;
      background: var(--accent-color);
      border-radius: 3px 3px 0 0;
    }
  }
}

.badge {
  background: var(--overdue-status);
  color: white;
  border-radius: 50%;
  padding: 2px 6px;
  font-size: 12px;
  margin-left: 5px;
}

.content-container {
  flex: 1;
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

.loading-container,
.empty-container {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.order-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  height: 100%;
  -webkit-overflow-scrolling: touch;
  overscroll-behavior: contain;
  /* 防止滚动穿透 */

  /* 隐藏滚动条但保留滚动功能 */
  scrollbar-width: none;
  /* Firefox */
  -ms-overflow-style: none;
  /* IE and Edge */

  &::-webkit-scrollbar {
    display: none;
    /* Chrome, Safari and Opera */
  }
}

.order-item {
  background: var(--card-bg);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  animation: fadeIn 0.5s ease;
  border: 1px solid var(--border-color);
  box-shadow: 0 4px 10px var(--shadow-color);
  margin-bottom: 24px;

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 20px var(--card-hover-shadow);
  }
}

.order-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.courier-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.courier-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 16px;
  font-weight: bold;
  color: var(--button-text);
  overflow: hidden;

  img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    background: transparent;
  }
}

.courier-details {
  flex: 1;

  .courier-name {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .express-no {
    margin: 4px 0 0;
    font-size: 13px;
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    gap: 4px;
  }
}

.order-status {
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  text-align: right;
  margin-left: auto;
}

.status-pending {
  background-color: color-mix(in srgb, var(--pending-status) 20%, transparent);
  color: var(--pending-status);
}

.status-completed {
  background-color: color-mix(in srgb, var(--completed-status) 20%, transparent);
  color: var(--completed-status);
}

.status-overdue {
  background-color: color-mix(in srgb, var(--overdue-status) 20%, transparent);
  color: var(--overdue-status);
}

.status-expiring {
  background-color: color-mix(in srgb, var(--expiring-status) 20%, transparent);
  color: var(--expiring-status);
}

.status-unpaid {
  background-color: color-mix(in srgb, var(--unpaid-status) 20%, transparent);
  color: var(--unpaid-status);
}

.order-details {
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  color: var(--text-primary);
}

.detail-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
  min-width: 0;
  /* 确保文本截断正常工作 */
  flex-wrap: wrap;
}

.detail-label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
  white-space: nowrap;
}

.detail-value {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 5px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #9ca3af;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.loading {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #6b7280;
}

.loading-spinner.large {
  width: 40px;
  height: 40px;
  border-width: 4px;
  border: 4px solid #e5e7eb;
  border-top-color: #6366f1;
  margin-bottom: 15px;
}

.refresh-btn-container {
  padding: 20px;
  display: flex;
  justify-content: center;
  background: #ffffff;
  border-top: 1px solid #e5e7eb;
}

.refresh-btn {
  background: #f3f4f6;
  color: #4b5563;
  border: 1px solid #e5e7eb;
  padding: 10px 30px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);

  &:hover:not(:disabled) {
    background: #e5e7eb;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.pickup-code {
  font-weight: bold;
  color: #f59e0b;
  letter-spacing: 1px;
}

.fee-wrapper {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
  flex-wrap: nowrap;
}

.fee {
  color: var(--overdue-status);
  font-weight: 500;
  margin-right: 6px;
  white-space: nowrap;
}

.fee-tag {
  font-size: 12px;
  background-color: color-mix(in srgb, var(--unpaid-status) 20%, transparent);
  color: var(--unpaid-status);
  padding: 2px 6px;
  border-radius: 4px;
  white-space: nowrap;
  display: inline-flex;
  align-self: center;
}

.fee-tag-free {
  background-color: color-mix(in srgb, var(--completed-status) 20%, transparent);
  color: var(--completed-status);
  font-weight: 500;
}

.loading-spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid color-mix(in srgb, var(--accent-color) 30%, transparent);
  border-radius: 50%;
  border-top-color: var(--accent-color);
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.load-more-status {
  padding: 15px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #6b7280;
  font-size: 14px;
  text-align: center;
  width: 100%;
  min-height: 50px;
}

.loading-more-text,
.no-more-text {
  display: inline-block;
  padding: 8px 15px;
  border-radius: 20px;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  box-shadow: 0 1px 2px var(--shadow-color);
}

.loading-more-text {
  margin-left: 8px;
  background-color: var(--input-bg);
}

.no-more-text {
  background-color: transparent;
}

.empty-orders-message {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: var(--text-secondary);
}

// 模态框样式
.cabinet-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
  backdrop-filter: blur(4px);
}

.cabinet-modal-content {
  width: 96%;
  max-width: 800px;
  max-height: 85vh;
  background-color: var(--bg-secondary);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 10px 30px var(--shadow-color);
  display: flex;
  flex-direction: column;
}

.cabinet-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);

  h3 {
    margin: 0;
    color: var(--text-primary);
    font-size: 18px;
    font-weight: 600;
  }

  .close-btn {
    background: none;
    border: none;
    color: var(--text-secondary);
    font-size: 24px;
    cursor: pointer;
    padding: 0;
    margin: 0;
    line-height: 1;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;

    &:hover {
      background-color: var(--input-bg);
    }
  }
}

.cabinet-modal-body {
  padding: 15px 0;
  overflow-y: auto;
  max-height: calc(85vh - 130px);
}

.cabinet-loading,
.cabinet-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;

  p {
    margin-top: 15px;
    color: var(--text-secondary);
  }
}

.cabinet-error p {
  color: var(--overdue-status);
}

.cabinet-info {
  margin-bottom: 20px;
  text-align: center;
  padding: 0 20px;

  h4 {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 8px 0;
  }

  .cabinet-address {
    font-size: 14px;
    color: var(--text-secondary);
    margin: 0;
  }
}

.cabinet-visualization {
  display: flex;
  justify-content: center;
  flex-wrap: nowrap;
  gap: 10px;
  margin-bottom: 20px;
  overflow-x: auto;
  padding: 0 10px 10px 10px;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  -ms-overflow-style: none;
  width: 100%;

  &::-webkit-scrollbar {
    display: none;
  }
}

.cabinet-column {
  flex-shrink: 0;

  h5 {
    text-align: center;
    margin: 0 0 10px 0;
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .cabinet-grid {
    display: flex;
    gap: 5px;
    justify-content: center;
    width: auto;
    min-width: fit-content;

    &.cabinet-grid-double {
      flex-wrap: wrap;
      width: 130px;
      justify-content: space-between;
    }
  }

  .cabinet-column-boxes {
    display: flex;
    flex-direction: column;
    gap: 3px;
    min-width: 50px;
  }
}

.cabinet-box {
  min-height: 28px;
  min-width: 50px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  position: relative;
  box-sizing: border-box;

  &.box-type-1 {
    /* 小型箱格 */
    height: 30px;
  }

  &.box-type-2 {
    /* 中型箱格 */
    height: 40px;
  }

  &.box-type-3 {
    /* 大型箱格 */
    height: 50px;
  }

  &.cabinet-box-empty {
    background-color: color-mix(in srgb, var(--completed-status) 20%, transparent);
    border-color: var(--completed-status);
  }

  &.cabinet-box-occupied {
    background-color: var(--input-bg);
    border-color: var(--border-color);
  }

  &.cabinet-box-highlighted {
    background-color: color-mix(in srgb, var(--accent-color) 20%, transparent);
    border-color: var(--accent-color);
    box-shadow: 0 0 0 2px var(--accent-color);
    transform: scale(1.05);
    z-index: 1;
  }

  .cabinet-current-mark {
    position: absolute;
    top: -5px;
    right: -5px;
    background-color: var(--accent-color);
    color: var(--button-text);
    border-radius: 4px;
    padding: 1px 4px;
    font-size: 10px;
  }
}

.box-label {
  font-size: 11px;
}

.cabinet-legend {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--text-secondary);
}

.legend-color {
  width: 14px;
  height: 14px;
  border-radius: 3px;

  &.current {
    background-color: color-mix(in srgb, var(--accent-color) 20%, transparent);
    border: 1px solid var(--accent-color);
  }

  &.occupied {
    background-color: var(--input-bg);
    border: 1px solid var(--border-color);
  }

  &.empty {
    background-color: color-mix(in srgb, var(--completed-status) 20%, transparent);
    border: 1px solid var(--completed-status);
  }
}

.cabinet-modal-footer {
  padding: 15px 20px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: center;
}

.primary-btn {
  background: var(--button-gradient);
  color: var(--button-text);
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px var(--button-shadow);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 10px var(--button-shadow);
  }

  &:active {
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

// 添加自定义下拉刷新样式
.pull-refresh-container {
  min-height: 100%;
  position: relative;
  overflow: visible;
  /* 修改为visible，防止限制滚动 */

  &.refreshing {
    padding-top: 50px;
  }
}

.pull-refresh-loading {
  height: 50px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: var(--bg-primary);
  color: var(--accent-color);
  font-size: 14px;
  border-bottom: 1px solid var(--border-color);

  .loading-spinner {
    margin-right: 8px;
  }
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

@media (max-width: 480px) {
  .cabinet-modal-content {
    width: 98%;
  }

  .cabinet-visualization {
    padding: 0 5px 10px 5px;
    gap: 5px;
    justify-content: flex-start;
  }

  .cabinet-column-boxes {
    min-width: 45px !important;
  }

  .cabinet-box {
    min-width: 45px;
    min-height: 25px;
  }

  .cabinet-column .cabinet-grid {
    gap: 3px;
  }

  .cabinet-column .cabinet-grid.cabinet-grid-double {
    width: 110px;
  }

  .order-details {
    grid-template-columns: 1fr;
    gap: 12px;
    padding: 16px;
  }

  .detail-item {
    display: flex;
    flex-wrap: wrap;

    .label {
      min-width: 65px;
      flex-shrink: 0;
    }

    .value {
      flex: 1;
      min-width: 0;
    }

    .fee-tag {
      margin-left: auto;
      margin-top: 2px;
    }
  }

  .order-header {
    padding: 15px;
  }

  .courier-avatar {
    width: 40px;
    height: 40px;
  }
}

.clickable {
  cursor: pointer;
  transition: all 0.4s ease;

  &:hover {
    color: #6366f1;
    text-decoration: underline;
  }

  &:active {
    color: #4338ca;
  }
}

.copy-text-btn {
  border: none;
  background: none;
  padding: 2px;
  cursor: pointer;
  border-radius: 4px;
  color: var(--accent-color);
  box-shadow: none;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    background-color: var(--accent-color-light);
    transform: none;
  }
}

.copy-message {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background-color: var(--card-bg);
  color: var(--text-primary);
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 4px 15px var(--shadow-color);
  z-index: 1000;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  0% {
    opacity: 0;
    transform: translate(-50%, 10px);
  }

  100% {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}

.action-buttons {
  margin-top: 6px;
}

.open-box-btn {
  background: var(--button-gradient);
  color: var(--button-text);
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px var(--button-shadow);
  width: 100%;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 10px var(--button-shadow);
  }

  &:active {
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
    transform: none;
  }
}

.express-id {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.copy-icon {
  color: var(--accent-color);
  opacity: 0.8;
}

/* 手机端响应式布局 */
@media (max-width: 576px) {
  .detail-row {
    flex-direction: column;
    gap: 8px;
  }

  .custody-fee-row {
    flex-direction: row;
  }

  .detail-item {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
  }

  .order-details {
    padding: 12px 16px;
    gap: 8px;
  }

  .courier-details {
    max-width: 200px;
  }

  .express-id {
    max-width: 150px;
  }

  .fee-tag {
    font-size: 11px;
    padding: 1px 5px;
  }
}

/* 更小屏幕的优化 */
@media (max-width: 360px) {
  .order-header {
    padding: 12px 14px;
  }

  .courier-avatar {
    width: 36px;
    height: 36px;
    font-size: 14px;
  }

  .courier-name {
    font-size: 14px;
  }

  .express-no {
    font-size: 12px;
  }

  .detail-label {
    font-size: 12px;
  }

  .detail-value {
    font-size: 13px;
  }

  .fee-wrapper {
    flex-direction: row;
    gap: 5px;
  }
}

.custody-fee-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.fee {
  color: var(--overdue-status);
  font-weight: 500;
  margin-left: 5px;
}

.fee-tag {
  font-size: 12px;
  background-color: color-mix(in srgb, var(--unpaid-status) 20%, transparent);
  color: var(--unpaid-status);
  padding: 2px 6px;
  border-radius: 4px;
  white-space: nowrap;
  flex-shrink: 0;
}

.fee-tag-free {
  background-color: color-mix(in srgb, var(--completed-status) 20%, transparent);
  color: var(--completed-status);
  font-weight: 500;
}

.custody-fee-item {
  display: flex;
  align-items: center;
  gap: 5px;
  flex-wrap: nowrap;
  overflow: visible;
}

.fee {
  color: var(--overdue-status);
  font-weight: 500;
  white-space: nowrap;
}

.fee-tag {
  font-size: 12px;
  background-color: color-mix(in srgb, var(--unpaid-status) 20%, transparent);
  color: var(--unpaid-status);
  padding: 2px 6px;
  border-radius: 4px;
  white-space: nowrap;
  display: inline-block;
  margin-left: 2px;
}

@media (max-width: 576px) {
  .custody-fee-item {
    width: 100%;
    flex-wrap: nowrap;
  }
}
</style>