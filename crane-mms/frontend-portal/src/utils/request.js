import axios from 'axios'
import { showFailToast } from 'vant'
import 'vant/es/toast/style'
import router from '../router'
import { clearPortalSession } from './portalAuth'

const request = axios.create({
  baseURL: '/api/v1/portal', // 注意：客户门户所有接口都在 /portal 前缀下
  timeout: 10000
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('portal_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    const res = response.data
    if (res.code === 200) {
      return res.data
    } else {
      showFailToast(res.msg || '业务异常')
      if (res.code === 401) {
        clearPortalSession()
        router.push('/login')
      }
      return Promise.reject(new Error(res.msg || 'Error'))
    }
  },
  error => {
    const status = error.response ? error.response.status : null
    const res = error.response ? error.response.data : null

    if (status === 401 || (res && res.code === 401)) {
      clearPortalSession()
      router.push('/login')
    } else {
      showFailToast(res?.msg || '网络连接异常')
    }
    return Promise.reject(error)
  }
)

export default request
