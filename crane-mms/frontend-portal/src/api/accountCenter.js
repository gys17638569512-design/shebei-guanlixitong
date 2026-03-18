import request from '../utils/request'

export function fetchAccountCenter() {
  return request.get('/customer/account-center')
}

export function fetchCurrentPortalAccount() {
  return request.get('/account/me')
}

export function updateCurrentPortalAccount(payload) {
  return request.put('/account/me', payload)
}

export function updateCurrentPortalPassword(password) {
  return request.put('/account/me/password', { password })
}

export function updateMainAccount(payload) {
  return request.put('/customer/account-center/main-account', payload)
}

export function createSubAccount(payload) {
  return request.post('/customer/account-center/sub-accounts', payload)
}

export function updateSubAccount(id, payload) {
  return request.put(`/customer/account-center/sub-accounts/${id}`, payload)
}

export function updateSubAccountStatus(id, is_active) {
  return request.put(`/customer/account-center/sub-accounts/${id}/status`, { is_active })
}

export function resetSubAccountPassword(id, password) {
  return request.put(`/customer/account-center/sub-accounts/${id}/reset-password`, { password })
}

export function updateCompanyProfile(payload) {
  return request.put('/customer/account-center/company-profile', payload)
}

export function bindWechatAccount(payload) {
  return request.post('/customer/account-center/wechat-bindings', payload)
}
