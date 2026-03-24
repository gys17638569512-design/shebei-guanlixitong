import { defineStore } from 'pinia'
import request from '../utils/request'
import { LEGACY_ROLE_PERMISSION_FALLBACK } from '../constants/permissions'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user')) || null
  }),
  
  actions: {
    persistAuthState() {
      if (this.token) {
        localStorage.setItem('token', this.token)
      } else {
        localStorage.removeItem('token')
      }

      if (this.user) {
        localStorage.setItem('user', JSON.stringify(this.user))
      } else {
        localStorage.removeItem('user')
      }
    },

    getEffectivePermissions() {
      const explicitPermissions = this.user?.effective_permissions
      if (Array.isArray(explicitPermissions)) {
        return explicitPermissions
      }
      return LEGACY_ROLE_PERMISSION_FALLBACK[this.user?.role] || []
    },

    hasPermission(permission) {
      if (!permission) return true
      return this.getEffectivePermissions().includes(permission)
    },

    hasAllPermissions(permissions = []) {
      return permissions.every((permission) => this.hasPermission(permission))
    },

    hasAnyPermission(permissions = []) {
      return permissions.some((permission) => this.hasPermission(permission))
    },

    async fetchCurrentUser() {
      if (!this.token) return null
      const profile = await request.get('/users/me')
      this.user = profile
      this.persistAuthState()
      return profile
    },

    async login(username, password) {
      try {
        console.log('Attempting login with:', { username, password })
        const response = await request.post('/auth/login', {
          username,
          password
        })
        
        console.log('Login response:', response)
        this.token = response.access_token
        this.user = response.user
        this.persistAuthState()
        
        return response
      } catch (error) {
        console.error('Login error:', error)
        console.error('Error details:', error.response || error.message)
        throw error
      }
    },
    
    logout() {
      this.token = ''
      this.user = null
      this.persistAuthState()
    }
  }
})
