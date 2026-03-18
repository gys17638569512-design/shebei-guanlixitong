import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(uni.getStorageSync('token') || '')
  const userInfo = ref(uni.getStorageSync('userInfo') ? JSON.parse(uni.getStorageSync('userInfo')) : null)

  const setUserInfo = (user: any) => {
    userInfo.value = user
    uni.setStorageSync('userInfo', JSON.stringify(user))
  }

  const setAuth = (newToken: string, user: any) => {
    token.value = newToken
    uni.setStorageSync('token', newToken)
    setUserInfo(user)
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
    setUserInfo,
    setAuth,
    logout
  }
})
