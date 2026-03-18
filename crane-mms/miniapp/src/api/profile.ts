import request from '../utils/request'

export const getMyProfile = () => {
  return request({
    url: '/users/me',
    method: 'GET'
  })
}

export const updateMyProfile = (data: any) => {
  return request({
    url: '/users/me',
    method: 'PUT',
    data
  })
}

export const bindMyWechat = (data: any) => {
  return request({
    url: '/users/me/wechat-binding',
    method: 'POST',
    data
  })
}

export const unbindMyWechat = (scene = 'miniapp') => {
  return request({
    url: `/users/me/wechat-binding?scene=${scene}`,
    method: 'DELETE'
  })
}
