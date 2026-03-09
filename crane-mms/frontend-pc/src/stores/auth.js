import { defineStore } from 'pinia'
import request from '../utils/request'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user')) || null
  }),
  
  actions: {
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
        
        localStorage.setItem('token', this.token)
        localStorage.setItem('user', JSON.stringify(this.user))
        
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
      
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
})