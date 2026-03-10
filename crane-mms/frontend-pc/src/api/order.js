import request from '../utils/request'

export const getOrders = (params) => {
    return request.get('/orders', { params })
}

export const getMyOrders = (params) => {
    return request.get('/orders/my', { params })
}

export const getOrderDetail = (id) => {
    return request.get(`/orders/${id}`)
}

export const createOrder = (data) => {
    return request.post('/orders', data)
}

export const checkinOrder = (id, data) => {
    return request.put(`/orders/${id}/checkin`, data)
}

export const completeOrder = (id, data) => {
    return request.put(`/orders/${id}/complete`, data)
}

export const pushForSignOrder = (id, data) => {
    return request.put(`/orders/${id}/push_sign`, data)
}
