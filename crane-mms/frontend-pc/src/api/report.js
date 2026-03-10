import request from '@/utils/request'

export const getReportArchive = () => {
    return request.get('/orders/reports/archive')
}
