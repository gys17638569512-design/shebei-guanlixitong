/**
 * 给图片添加水印
 * @param {string} tempFilePath - 原始图片临时路径
 * @param {string} address - 地址文字（来自逆地理编码）
 * @returns {Promise<string>} 加了水印的新临时文件路径
 */
export async function addWatermark(tempFilePath, address) {
    return new Promise((resolve, reject) => {
        const now = new Date();
        const timeStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;

        // 生成一个临时的 canvas-id
        const canvasId = 'watermark-canvas-' + Date.now();

        uni.getImageInfo({
            src: tempFilePath, success: (imgInfo) => {
                const width = imgInfo.width;
                const height = imgInfo.height;

                const ctx = uni.createCanvasContext(canvasId);
                ctx.drawImage(tempFilePath, 0, 0, width, height);

                // 半透明黑色背景条（底部）
                const barHeight = 80;
                ctx.setFillStyle('rgba(0,0,0,0.55)');
                ctx.fillRect(0, height - barHeight, width, barHeight);

                // 白色水印文字
                ctx.setFillStyle('#FFFFFF');
                ctx.setFontSize(22);
                ctx.fillText(timeStr, 20, height - barHeight + 28);
                ctx.setFontSize(18);
                ctx.fillText(address || '位置获取中...', 20, height - barHeight + 60);

                ctx.draw(false, () => {
                    uni.canvasToTempFilePath({
                        canvasId,
                        fileType: 'jpg',
                        quality: 0.9,
                        success: (res) => resolve(res.tempFilePath),
                        fail: reject
                    });
                });
            }, fail: reject
        });
    });
}
