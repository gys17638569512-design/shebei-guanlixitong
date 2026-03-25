import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1'

const request = axios.create({
  baseURL: apiBaseUrl,
  timeout: 10000
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    const res = response.data
    if (res.code === 200) {
      return res.data
    } else {
      ElMessage.error(res.msg || 'Error')
      if (res.code === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        router.push('/login')
      }
      return Promise.reject(new Error(res.msg || 'Error'))
    }
  },
  error => {
    if (error.response) {
      const status = error.response.status
      const res = error.response.data

      if (status === 401 || (res && res.code === 401)) {
        // 未授权，跳转到登录页
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        router.push('/login')
      } else if (res && res.msg) {
        ElMessage.error(res.msg)
      } else if (status === 403) {
        ElMessage.error('权限不足')
      } else if (status === 404) {
        ElMessage.error('接口不存在')
      } else if (status === 500) {
        ElMessage.error('服务器错误')
      } else if (status === 400 || status === 422) {
        ElMessage.error('请求参数错误')
      } else {
        ElMessage.error('请求失败')
      }
    } else {
      ElMessage.error('网络错误')
    }
    return Promise.reject(error)
  }
)

export default request
