import request from '@/utils/request'

export const fetchPlatformSettings = () => request.get('/settings/platform')

export const persistPlatformSettings = (payload) => request.put('/settings/platform', payload)

export const fetchEmployeeAccounts = async () => {
  const res = await request.get('/users', {
    params: { skip: 0, limit: 200 }
  })
  return res.items || []
}

export const addEmployeeAccount = (payload) => request.post('/users', payload)

export const editEmployeeAccount = (id, payload) => request.put(`/users/${id}`, payload)

export const refreshEmployeePassword = (id, password) => request.put(`/users/${id}/reset-password`, { password })

export const changeEmployeeStatus = (id, status) => request.put(`/users/${id}/status`, { status })
