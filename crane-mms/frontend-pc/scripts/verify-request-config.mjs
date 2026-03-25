import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

const requestPath = resolve('src/utils/request.js')
const viteConfigPath = resolve('vite.config.js')

const requestSource = readFileSync(requestPath, 'utf8')
const viteConfigSource = readFileSync(viteConfigPath, 'utf8')

if (requestSource.includes('http://localhost:8001/api/v1')) {
  throw new Error('frontend-pc request config still hardcodes localhost API base URL')
}

if (!requestSource.includes("VITE_API_BASE_URL") && !requestSource.includes("'/api/v1'")) {
  throw new Error('frontend-pc request config is missing an environment-aware or relative API base URL')
}

if (!viteConfigSource.includes("'/api'") || !viteConfigSource.includes('localhost:8001')) {
  throw new Error('frontend-pc vite config is missing the /api proxy for local development')
}

console.log('frontend-pc request config is deployment-safe')
