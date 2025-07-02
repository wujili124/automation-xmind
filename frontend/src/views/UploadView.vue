<template>
  <div class="upload-container">
    <el-card class="upload-card">
      <template #header>
        <div class="card-header">
          <h2>XMind 冒烟测试用例导出工具</h2>
          <p>请上传您的XMind文件进行分析</p>
        </div>
      </template>
      
      <el-upload
        ref="uploadRef"
        class="upload-dragger"
        drag
        action=""
        :auto-upload="false"
        :limit="1"
        accept=".xmind"
        :on-change="handleFileChange"
        :on-exceed="handleExceed"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将XMind文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            只能上传.xmind格式文件，且文件大小不超过10MB
          </div>
        </template>
      </el-upload>
      
      <div class="upload-actions" v-if="selectedFile">
        <el-button type="primary" @click="uploadFile" :loading="uploading">
          {{ uploading ? '分析中...' : '开始分析' }}
        </el-button>
        <el-button @click="clearFile">重新选择</el-button>
      </div>
      
      <div class="file-info" v-if="selectedFile">
        <el-descriptions title="文件信息" :column="2" border>
          <el-descriptions-item label="文件名">{{ selectedFile.name }}</el-descriptions-item>
          <el-descriptions-item label="文件大小">{{ formatFileSize(selectedFile.size) }}</el-descriptions-item>
          <el-descriptions-item label="文件类型">{{ selectedFile.type || '.xmind' }}</el-descriptions-item>
          <el-descriptions-item label="最后修改时间">{{ formatDate(selectedFile.lastModified) }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import type { UploadInstance, UploadFile, UploadFiles } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const uploadRef = ref<UploadInstance>()
const selectedFile = ref<File | null>(null)
const uploading = ref(false)

// API基础URL
const API_BASE_URL = 'http://localhost:8000'

const handleFileChange = (file: UploadFile, files: UploadFiles) => {
  console.log('文件选择:', file.name)
  selectedFile.value = file.raw || null
}

const handleExceed = () => {
  ElMessage.warning('只能选择一个文件!')
}

const clearFile = () => {
  selectedFile.value = null
  uploadRef.value?.clearFiles()
}

const uploadFile = async () => {
  if (!selectedFile.value) {
    ElMessage.error('请先选择XMind文件')
    return
  }
  
  // 验证文件大小 (10MB限制)
  if (selectedFile.value.size > 10 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过10MB')
    return
  }
  
  uploading.value = true
  
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    
    console.log('开始上传文件到后端进行分析...')
    
    const response = await axios.post(`${API_BASE_URL}/api/analyze`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 30000 // 30秒超时
    })
    
    console.log('分析完成:', response.data)
    
    ElMessage.success('文件分析完成!')
    
    // 将分析结果存储到sessionStorage中，避免URL过长
    sessionStorage.setItem('analysisData', JSON.stringify(response.data))
    
    // 跳转到分析结果页面
    router.push({ name: 'analyze' })
    
  } catch (error: any) {
    console.error('文件分析失败:', error)
    
    let errorMessage = '文件分析失败'
    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail
    } else if (error.message) {
      errorMessage = error.message
    }
    
    ElMessageBox.alert(errorMessage, '错误', {
      confirmButtonText: '确定',
      type: 'error'
    })
  } finally {
    uploading.value = false
  }
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (timestamp: number): string => {
  return new Date(timestamp).toLocaleString('zh-CN')
}
</script>

<style scoped>
/* 主容器 - 简洁科技感背景 */
.upload-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
  background: linear-gradient(135deg, #1e1e2e 0%, #2a2d3a 100%);
  position: relative;
}

/* 添加微妙的网格背景 */
.upload-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    linear-gradient(rgba(0, 123, 255, 0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 123, 255, 0.1) 1px, transparent 1px);
  background-size: 50px 50px;
  pointer-events: none;
}

/* 科技感卡片 */
.upload-card {
  width: 100%;
  max-width: 600px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.1),
    0 1px 3px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(20px);
  position: relative;
  overflow: hidden;
}

/* 卡片顶部装饰线 */
.upload-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #007bff, #6f42c1, #007bff);
  background-size: 200% 100%;
}

/* 卡片头部 */
.card-header {
  text-align: center;
  padding: 32px 24px 24px;
  background: linear-gradient(135deg, rgba(0, 123, 255, 0.03), rgba(111, 66, 193, 0.03));
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.card-header h2 {
  margin: 0 0 12px 0;
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
  letter-spacing: -0.5px;
}

.card-header p {
  margin: 0;
  color: #6c757d;
  font-size: 15px;
  font-weight: 400;
}

/* 上传区域 */
.upload-dragger {
  margin: 32px 24px;
}

:deep(.el-upload-dragger) {
  background: linear-gradient(135deg, #f8f9fa, #ffffff);
  border: 2px dashed #dee2e6;
  border-radius: 12px;
  padding: 48px 24px;
  transition: all 0.3s ease;
  position: relative;
}

:deep(.el-upload-dragger:hover) {
  border-color: #007bff;
  background: linear-gradient(135deg, #f0f8ff, #ffffff);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 123, 255, 0.15);
}

:deep(.el-icon--upload) {
  font-size: 48px;
  color: #007bff;
  margin-bottom: 16px;
  transition: transform 0.3s ease;
}

:deep(.el-upload-dragger:hover .el-icon--upload) {
  transform: scale(1.05);
}

:deep(.el-upload__text) {
  color: #495057;
  font-size: 16px;
  font-weight: 500;
}

:deep(.el-upload__text em) {
  color: #007bff;
  font-weight: 600;
  text-decoration: none;
  font-style: normal;
}

:deep(.el-upload__tip) {
  color: #6c757d;
  font-size: 13px;
  margin-top: 12px;
}

/* 操作按钮区域 */
.upload-actions {
  text-align: center;
  margin: 24px;
  padding: 24px;
  background: rgba(248, 249, 250, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

:deep(.upload-actions .el-button) {
  margin: 0 8px;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.3s ease;
}

:deep(.upload-actions .el-button--primary) {
  background: linear-gradient(135deg, #007bff, #0056b3);
  border: none;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
}

:deep(.upload-actions .el-button--primary:hover) {
  background: linear-gradient(135deg, #0056b3, #004085);
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(0, 123, 255, 0.4);
}

:deep(.upload-actions .el-button--default) {
  background: #ffffff;
  border: 1px solid #dee2e6;
  color: #495057;
}

:deep(.upload-actions .el-button--default:hover) {
  border-color: #007bff;
  color: #007bff;
  background: #f8f9fa;
  transform: translateY(-1px);
}

/* 文件信息区域 */
.file-info {
  margin: 24px;
  background: rgba(248, 249, 250, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

:deep(.file-info .el-descriptions__header) {
  background: linear-gradient(135deg, rgba(0, 123, 255, 0.08), rgba(111, 66, 193, 0.08));
  padding: 16px 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

:deep(.file-info .el-descriptions__title) {
  color: #2c3e50;
  font-size: 16px;
  font-weight: 600;
}

:deep(.file-info .el-descriptions-item__label) {
  background: #f8f9fa;
  color: #495057;
  font-weight: 500;
  border: 1px solid #e9ecef;
}

:deep(.file-info .el-descriptions-item__content) {
  background: #ffffff;
  color: #2c3e50;
  border: 1px solid #e9ecef;
  font-weight: 400;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .upload-container {
    padding: 16px;
  }
  
  .upload-card {
    max-width: 100%;
  }
  
  .card-header {
    padding: 24px 20px 20px;
  }
  
  .card-header h2 {
    font-size: 20px;
  }
  
  .upload-dragger {
    margin: 24px 20px;
  }
  
  :deep(.el-upload-dragger) {
    padding: 40px 20px;
  }
  
  :deep(.el-icon--upload) {
    font-size: 40px;
  }
  
  .upload-actions {
    margin: 20px;
    padding: 20px;
  }
  
  :deep(.upload-actions .el-button) {
    margin: 4px;
    padding: 10px 20px;
    font-size: 13px;
  }
  
  .file-info {
    margin: 20px;
  }
}

/* 加载状态优化 */
:deep(.el-button.is-loading) {
  position: relative;
}

/* 微妙的悬停效果 */
.upload-card:hover {
  transform: translateY(-4px);
  box-shadow: 
    0 25px 50px rgba(0, 0, 0, 0.15),
    0 2px 6px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
  transition: all 0.3s ease;
}
</style> 