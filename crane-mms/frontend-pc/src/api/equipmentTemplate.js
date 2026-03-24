import request from '../utils/request'

export const getEquipmentTemplateGroups = (params) => request.get('/equipment-template-groups', { params })

export const createEquipmentTemplateGroup = (data) => request.post('/equipment-template-groups', data)

export const getEquipmentTemplateVersion = (id) => request.get(`/equipment-template-versions/${id}`)

export const createEquipmentTemplateVersion = (data) => request.post('/equipment-template-versions', data)

export const updateEquipmentTemplateVersion = (id, data) => request.put(`/equipment-template-versions/${id}`, data)

export const matchEquipmentTemplate = (params) => request.get('/equipment-template-match', { params })

export const getEquipmentTemplateCandidates = () => request.get('/equipment-template-candidates')

export const createEquipmentTemplateCandidate = (data) => request.post('/equipment-template-candidates', data)

export const approveEquipmentTemplateCandidate = (id, data) => request.post(`/equipment-template-candidates/${id}/approve`, data)

export const rejectEquipmentTemplateCandidate = (id, data) => request.post(`/equipment-template-candidates/${id}/reject`, data)

export const getInspectionBaseTemplates = (params) => request.get('/inspection-base-templates', { params })

export const createInspectionBaseTemplate = (data) => request.post('/inspection-base-templates', data)

export const updateInspectionBaseTemplate = (id, data) => request.put(`/inspection-base-templates/${id}`, data)
