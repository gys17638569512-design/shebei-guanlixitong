import request from '../utils/request'

export const getCustomers = (params) => {
    return request.get('/customers', { params })
}

export const getCustomerDetail = (id) => {
    return request.get(`/customers/${id}`)
}

export const createCustomer = (data) => {
    return request.post('/customers', data)
}

export const updateCustomer = (id, data) => {
    return request.put(`/customers/${id}`, data)
}

export const deleteCustomer = (id) => {
    return request.delete(`/customers/${id}`)
}
