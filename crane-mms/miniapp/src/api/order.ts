import request from '../utils/request'

export const getMyOrders = () => {
  return request({
    url: '/orders/my',
    method: 'GET'
  })
}

export const getOrderDetail = (id: number) => {
  return request({
    url: `/orders/${id}`,
    method: 'GET'
  })
}

export const checkinOrder = (id: number, data: any) => {
  return request({
    url: `/orders/${id}/checkin`,
    method: 'PUT',
    data
  })
}

export const completeOrder = (id: number, data: any) => {
  return request({
    url: `/orders/${id}/complete`,
    method: 'PUT',
    data
  })
}

export const pushForSign = (id: number, data: any) => {
  return request({
    url: `/orders/${id}/push_sign`,
    method: 'PUT',
    data
  })
}
