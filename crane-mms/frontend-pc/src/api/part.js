import request from '@/utils/request'

export const getAllParts = () => {
    return request.get('/parts')
}

export const createPart = (data) => {
    return request.post('/parts', data)
}

export const updatePart = (id, data) => {
    return request.put(`/parts/${id}`, data)
}

export const adjustPartStock = (id, action, quantity) => {
    return request.put(`/parts/${id}/stock`, { action, quantity })
}
