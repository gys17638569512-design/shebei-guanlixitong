const deepClone = (value) => JSON.parse(JSON.stringify(value))

const platformSettings = {
  company_name: '数字化起重机维修维保系统',
  short_name: '起重机维保',
  system_name: '数字化起重机维修维保系统',
  system_subtitle: '全生命周期设备服务平台',
  logo_url: '/brand-mark.svg',
  favicon_url: '/brand-mark.svg',
  seal_url: '/brand-mark.svg',
  support_phone: '400-800-1234',
  support_email: 'service@example.com',
  address: '中国 · 设备运维服务中心',
  pc_login_title: '管理端登录',
  portal_login_title: '客户端登录',
  worker_login_title: '工人端登录',
  report_header_text: '数字化起重机维修维保系统',
  report_footer_text: '如有疑问请联系平台客服',
  theme_primary: '#1677ff',
  theme_secondary: '#0ea5e9',
  is_active: true,
  updated_at: '2026-03-18 09:00'
}

const employeeAccounts = [
  {
    id: 1,
    name: '管理员',
    username: 'admin',
    role: 'ADMIN',
    department: '平台运营部',
    job_title: '系统管理员',
    phone: '13800000001',
    wechat_bound: true,
    mobile_bound: true,
    status: 'ACTIVE',
    last_login_at: '2026-03-18 08:28',
    must_change_password: false
  },
  {
    id: 2,
    name: '李经理',
    username: 'manager01',
    role: 'MANAGER',
    department: '维保业务部',
    job_title: '业务经理',
    phone: '13800000002',
    wechat_bound: true,
    mobile_bound: true,
    status: 'ACTIVE',
    last_login_at: '2026-03-18 08:14',
    must_change_password: false
  },
  {
    id: 3,
    name: '张工程师',
    username: 'tech01',
    role: 'TECH',
    department: '现场服务部',
    job_title: '技术工程师',
    phone: '13800000003',
    wechat_bound: false,
    mobile_bound: true,
    status: 'ACTIVE',
    last_login_at: '2026-03-17 19:42',
    must_change_password: true
  }
]

let nextEmployeeId = 4

export const getPlatformSettings = async () => deepClone(platformSettings)

export const savePlatformSettings = async (payload) => {
  Object.assign(platformSettings, payload, {
    updated_at: new Date().toLocaleString('zh-CN', { hour12: false })
  })
  return deepClone(platformSettings)
}

export const listEmployeeAccounts = async () => deepClone(employeeAccounts)

export const createEmployeeAccount = async (payload) => {
  const employee = {
    id: nextEmployeeId++,
    name: payload.name,
    username: payload.username,
    role: payload.role,
    department: payload.department || '',
    job_title: payload.job_title || '',
    phone: payload.phone || '',
    wechat_bound: Boolean(payload.wechat_bound),
    mobile_bound: Boolean(payload.mobile_bound || payload.phone),
    status: payload.status || 'ACTIVE',
    last_login_at: '未登录',
    must_change_password: true
  }

  employeeAccounts.unshift(employee)
  return deepClone(employee)
}

export const updateEmployeeAccount = async (id, payload) => {
  const index = employeeAccounts.findIndex((item) => item.id === id)
  if (index === -1) {
    throw new Error('员工账号不存在')
  }

  employeeAccounts[index] = {
    ...employeeAccounts[index],
    ...payload,
    mobile_bound: Boolean(payload.mobile_bound ?? employeeAccounts[index].mobile_bound),
    wechat_bound: Boolean(payload.wechat_bound ?? employeeAccounts[index].wechat_bound)
  }

  return deepClone(employeeAccounts[index])
}

export const resetEmployeePassword = async (id, password) => {
  const index = employeeAccounts.findIndex((item) => item.id === id)
  if (index === -1) {
    throw new Error('员工账号不存在')
  }

  employeeAccounts[index].must_change_password = true
  employeeAccounts[index].password_reset = Boolean(password)
  employeeAccounts[index].password_updated_at = new Date().toLocaleString('zh-CN', { hour12: false })
  return deepClone(employeeAccounts[index])
}

export const toggleEmployeeStatus = async (id, status) => {
  const index = employeeAccounts.findIndex((item) => item.id === id)
  if (index === -1) {
    throw new Error('员工账号不存在')
  }

  employeeAccounts[index].status = status
  return deepClone(employeeAccounts[index])
}
