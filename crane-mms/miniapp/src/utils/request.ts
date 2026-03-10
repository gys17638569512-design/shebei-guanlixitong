/**
 * 移动端通用请求封装
 * 基于 uni.request 的 Promise 封装，完美适配小程序与 H5
 */

const BASE_URL = 'http://127.0.0.1:8001/api/v1'

const request = (options: UniApp.RequestOptions) => {
  return new Promise((resolve, reject) => {
    // 自动补白 Token
    const token = uni.getStorageSync('token')
    const header = options.header || {}
    if (token) {
      header['Authorization'] = `Bearer ${token}`
    }

    uni.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data,
      header: header,
      success: (res) => {
        const data = res.data as any
        if (data.code === 200) {
          resolve(data.data)
        } else {
          // 业务错误处理
          uni.showToast({
            title: data.msg || '服务器异常',
            icon: 'none'
          })
          if (data.code === 401) {
            uni.removeStorageSync('token')
            uni.reLaunch({ url: '/pages/login/login' })
          }
          reject(data)
        }
      },
      fail: (err) => {
        uni.showToast({
          title: '网络连接失败',
          icon: 'none'
        })
        reject(err)
      }
    })
  })
}

export default request
