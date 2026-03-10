import request from '../utils/request'

export const login = (data: any) => {
  // `login_type: 'pwd'` is explicitly added here for portal login.
  return request({
    url: '/portal/auth/login',
    method: 'POST',
    data: { ...data, login_type: 'pwd' }
  })
}
