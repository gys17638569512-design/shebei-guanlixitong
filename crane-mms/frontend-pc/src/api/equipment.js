import request from '../utils/request'

export const getEquipmentDetail = (id) => {
    return request.get(`/equipments/${id}`)
}

export const createEquipment = (data) => {
    return request.post('/equipments', data)
}

export const updateEquipment = (id, data) => {
    return request.put(`/equipments/${id}`, data)
}

export const getEquipmentTemplates = (params) => {
    return request.get('/equipments/templates', { params })
}
