const QUEUE_KEY = 'offline_task_queue';

/**
 * 将任务推入离线队列（网络不可用时使用）
 * @param {string} taskType - 任务类型，如 'complete_order'
 * @param {object} data - 任务数据
 */
export function pushToQueue(taskType, data) {
    const queue = uni.getStorageSync(QUEUE_KEY) || [];
    queue.push({ taskType, data, createdAt: Date.now() });
    uni.setStorageSync(QUEUE_KEY, queue);
    console.log(`[离线队列] 已入队：${taskType}，当前队列长度：${queue.length}`);
}

/**
 * 处理离线队列（网络恢复后调用）
 * 从 app.js 的网络状态监听中触发
 */
export async function processQueue() {
    const queue = uni.getStorageSync(QUEUE_KEY) || [];
    if (queue.length === 0) return;

    console.log(`[离线队列] 开始处理 ${queue.length} 个待同步任务`);
    const failed = [];

    for (const task of queue) {
        try {
            await executeTask(task);
            console.log(`[离线队列] 任务处理成功：${task.taskType}`);
        } catch (err) {
            console.error(`[离线队列] 任务失败：${task.taskType}`, err);
            failed.push(task);
        }
    }

    // 只保留失败的任务，等待下次重试
    uni.setStorageSync(QUEUE_KEY, failed);

    if (failed.length === 0) {
        uni.showToast({ title: '离线数据已同步', icon: 'success' });
    }
}

async function executeTask(task) {
    const { request } = await import('./request');
    switch (task.taskType) {
        case 'complete_order':
            return request.put(`/orders/${task.data.orderId}/complete`, task.data.payload);
        case 'push_sign':
            return request.put(`/orders/${task.data.orderId}/push_sign`, task.data.payload);
        default:
            console.warn(`[离线队列] 未知任务类型：${task.taskType}`);
    }
}
