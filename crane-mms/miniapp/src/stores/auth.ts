import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(uni.getStorageSync('token') || '')
  const userInfo = ref(uni.getStorageSync('userInfo') ? JSON.parse(uni.getStorageSync('userInfo')) : null)

  const setAuth = (newToken: string, user: any) => {
    token.value = newToken
    userInfo.value = user
    uni.setStorageSync('token', newToken)
    uni.setStorageSync('userInfo', JSON.stringify(user))
  }

  const logout = () => {
    token.value = ''
    userInfo.value = null
    uni.removeStorageSync('token')
    uni.removeStorageSync('userInfo')
    uni.reLaunch({ url: '/pages/login/login' })
  }

  return {
    token,
    userInfo,
    setAuth,
    logout
  }
})
