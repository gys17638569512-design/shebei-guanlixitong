import request from '../utils/request'

export const getEquipments = (params) => {
    return request.get('/equipments', { params })
}

export const getEquipmentDetail = (id) => {
    return request.get(`/equipments/${id}`)
}

export const createEquipment = (data) => {
    return request.post('/equipments', data)
}

export const updateEquipment = (id, data) => {
    return request.put(`/equipments/${id}`, data)
}

export const deleteEquipment = (id) => {
    return request.delete(`/equipments/${id}`)
}

export const getEquipmentTemplates = (params) => {
    return request.get('/equipments/templates', { params })
}
