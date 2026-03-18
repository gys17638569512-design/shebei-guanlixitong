import request from '../utils/request'

export function fetchAccountCenter() {
  return request.get('/customer/account-center')
}

export function updateMainAccount(payload) {
  return request.put('/customer/account-center/main-account', payload)
}

export function createSubAccount(payload) {
  return request.post('/customer/account-center/sub-accounts', payload)
}

export function updateCompanyProfile(payload) {
  return request.put('/customer/account-center/company-profile', payload)
}

export function bindWechatAccount(payload) {
  return request.post('/customer/account-center/wechat-bindings', payload)
}
