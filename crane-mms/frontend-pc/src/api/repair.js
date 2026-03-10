import request from '@/utils/request'

export const getRepairOrders = (params) => {
    return request.get('/repairs', { params })
}

export const createRepairOrder = (data) => {
    return request.post('/repairs', data)
}

export const updateRepairOrder = (id, data) => {
    return request.put(`/repairs/${id}`, data)
}

export const getRepairDetail = (id) => {
    return request.get(`/repairs/${id}`)
}
