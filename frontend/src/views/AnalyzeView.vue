<template>
  <div class="analyze-container">
    <el-card class="analyze-card">
      <template #header>
        <div class="card-header">
          <h2>XMind文件分析结果</h2>
          <el-button @click="goBack" link class="back-btn">
            <el-icon><ArrowLeft /></el-icon>
            返回上传
          </el-button>
        </div>
      </template>
      
      <!-- 文件基本信息 -->
      <div class="file-summary" v-if="analysisData">
        <el-descriptions title="文件概览" :column="2" border>
          <el-descriptions-item label="文件名">{{ analysisData.filename }}</el-descriptions-item>
          <el-descriptions-item label="总节点数">{{ analysisData.total_nodes }}</el-descriptions-item>
          <el-descriptions-item label="适合冒烟测试">{{ analysisData.suitable_for_smoke }}</el-descriptions-item>
          <el-descriptions-item label="发现标识符">{{ analysisData.markers_found.length }} 种</el-descriptions-item>
        </el-descriptions>
      </div>
      
      <!-- 标识符详情 -->
      <div class="markers-section" v-if="analysisData?.markers_found.length">
        <h3>检测到的标识符</h3>
        <el-row :gutter="20">
          <el-col :span="24" v-for="marker in analysisData.markers_found" :key="marker.markerId">
            <el-card class="marker-card" shadow="hover">
              <div class="marker-info">
                <div class="marker-header">
                  <el-tag :type="getMarkerType(marker.markerId)" size="large">
                    {{ marker.symbol }}
                  </el-tag>
                  <span class="marker-count">{{ marker.count }} 个节点</span>
                </div>
                <div class="marker-samples" v-if="marker.sample_nodes?.length">
                  <p class="samples-title">示例节点：</p>
                  <el-tag
                    v-for="sample in marker.sample_nodes"
                    :key="sample"
                    size="small"
                    class="sample-tag"
                  >
                    {{ sample }}
                  </el-tag>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <!-- 无标识符提示 -->
      <div class="no-markers" v-else>
        <el-empty>
          <template #description>
            <div class="empty-description">
              <h3>未检测到任何标识符</h3>
              <p>您的XMind文件中没有包含以下支持的标识符：</p>
              <div class="supported-markers">
                <el-tag class="marker-tag">重要 (红色叹号)</el-tag>
                <el-tag class="marker-tag">优先级1-5 (红色1-灰色5)</el-tag>
                <el-tag class="marker-tag">红旗/黄旗</el-tag>
                <el-tag class="marker-tag">红星/黄星</el-tag>
              </div>
              <p class="tip-text">
                💡 提示：请在XMind中为需要导出的测试用例节点添加标识符，然后重新上传文件
              </p>
            </div>
          </template>
          <div class="empty-actions">
            <el-button type="primary" @click="goBack">重新上传文件</el-button>
            <el-button @click="showInstructions">查看使用说明</el-button>
          </div>
        </el-empty>
      </div>
      
      <!-- 操作按钮 -->
      <div class="actions" v-if="analysisData?.markers_found.length">
        <el-button type="primary" size="large" @click="goToExport">
          选择标识符并导出用例
        </el-button>
      </div>
    </el-card>
    
    <!-- 使用说明对话框 -->
    <el-dialog v-model="showInstructionsDialog" title="XMind标识符使用说明" width="600px">
      <div class="instructions-content">
        <h4>如何在XMind中添加标识符：</h4>
        <ol>
          <li>在XMind中选择要标记的节点</li>
          <li>右键选择"标记" → "标识符"</li>
          <li>选择以下支持的标识符之一：
            <ul>
              <li><strong>重要</strong> - 红色叹号标识符</li>
              <li><strong>优先级1-5</strong> - 数字1(红)到5(灰)标识符</li>
              <li><strong>旗帜</strong> - 红旗或黄旗标识符</li>
              <li><strong>星星</strong> - 红星或黄星标识符</li>
            </ul>
          </li>
          <li>保存XMind文件后重新上传</li>
        </ol>
        
        <el-alert
          title="推荐做法"
          type="info"
          :closable="false"
          show-icon
        >
          <p>为了生成高质量的冒烟测试用例，建议：</p>
          <ul>
            <li>使用"重要"标识符标记核心功能测试用例</li>
            <li>使用"优先级1-3"标记高优先级测试场景</li>
            <li>使用"红旗"标记关键风险点</li>
            <li>使用"红星"标记必测功能</li>
          </ul>
        </el-alert>
      </div>
      
      <template #footer>
        <el-button @click="showInstructionsDialog = false">关闭</el-button>
        <el-button type="primary" @click="goBack">重新上传文件</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'

interface MarkerInfo {
  markerId: string
  symbol: string
  count: number
  sample_nodes?: string[]
}

interface AnalysisData {
  filename: string
  markers_found: MarkerInfo[]
  total_nodes: number
  suitable_for_smoke: number
  file_data: string
}

const router = useRouter()
const route = useRoute()
const analysisData = ref<AnalysisData | null>(null)
const showInstructionsDialog = ref(false)

onMounted(() => {
  // 从sessionStorage中获取分析结果，而不是从URL query参数
  try {
    const dataStr = sessionStorage.getItem('analysisData')
    if (dataStr) {
      analysisData.value = JSON.parse(dataStr)
      console.log('分析数据加载成功:', analysisData.value)
    } else {
      ElMessage.warning('未找到分析数据，请重新上传文件')
      goBack()
    }
  } catch (error) {
    console.error('解析分析数据失败:', error)
    ElMessage.error('数据解析失败，请重新上传文件')
    goBack()
  }
})

const goBack = () => {
  router.push({ name: 'upload' })
}

const goToExport = () => {
  if (!analysisData.value) {
    ElMessage.error('分析数据不存在')
    return
  }
  
  // 将分析数据存储到sessionStorage中，避免URL过长
  sessionStorage.setItem('analysisData', JSON.stringify(analysisData.value))
  
  // 跳转到导出页面
  router.push({ name: 'export' })
}

const showInstructions = () => {
  showInstructionsDialog.value = true
}

const getMarkerType = (markerId: string): string => {
  // 根据标识符ID返回对应的标签类型（颜色）
  if (markerId === 'important') return 'danger'
  if (markerId.startsWith('priority-1')) return 'danger'
  if (markerId.startsWith('priority-2')) return 'warning'
  if (markerId.startsWith('priority-3')) return 'primary'
  if (markerId.startsWith('priority-4')) return 'success'
  if (markerId.startsWith('priority-5')) return 'info'
  if (markerId.includes('red')) return 'danger'
  if (markerId.includes('yellow')) return 'warning'
  return 'primary'
}
</script>

<style scoped>
/* 主容器 - 科技感背景 */
.analyze-container {
  min-height: 100vh;
  padding: 20px;
  background: linear-gradient(135deg, #1e1e2e 0%, #2a2d3a 100%);
  position: relative;
}

/* 添加微妙的网格背景 */
.analyze-container::before {
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
.analyze-card {
  max-width: 1000px;
  margin: 0 auto 20px;
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
  transition: all 0.3s ease;
}

/* 卡片顶部装饰线 */
.analyze-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #007bff, #6f42c1, #007bff);
  background-size: 200% 100%;
}

/* 卡片悬停效果 */
.analyze-card:hover {
  transform: translateY(-4px);
  box-shadow: 
    0 25px 50px rgba(0, 0, 0, 0.15),
    0 2px 6px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 32px 24px 24px;
  background: linear-gradient(135deg, rgba(0, 123, 255, 0.03), rgba(111, 66, 193, 0.03));
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.card-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
  letter-spacing: -0.5px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #007bff;
  font-weight: 500;
  transition: all 0.3s ease;
}

.back-btn:hover {
  color: #0056b3;
  transform: translateX(-2px);
}

/* 文件概览区域 */
.file-summary {
  margin: 32px 24px;
  background: rgba(248, 249, 250, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

:deep(.file-summary .el-descriptions__header) {
  background: linear-gradient(135deg, rgba(0, 123, 255, 0.08), rgba(111, 66, 193, 0.08));
  padding: 16px 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

:deep(.file-summary .el-descriptions__title) {
  color: #2c3e50;
  font-size: 16px;
  font-weight: 600;
}

:deep(.file-summary .el-descriptions-item__label) {
  background: #f8f9fa;
  color: #495057;
  font-weight: 500;
  border: 1px solid #e9ecef;
}

:deep(.file-summary .el-descriptions-item__content) {
  background: #ffffff;
  color: #2c3e50;
  border: 1px solid #e9ecef;
  font-weight: 400;
}

/* 标识符区域 */
.markers-section {
  margin: 32px 24px;
}

.markers-section h3 {
  margin: 0 0 24px 0;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
}

/* 标识符卡片 */
.marker-card {
  margin-bottom: 16px;
  background: rgba(248, 249, 250, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  overflow: hidden;
}

.marker-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 123, 255, 0.15);
  border-color: rgba(0, 123, 255, 0.2);
}

.marker-info {
  padding: 20px;
}

.marker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.marker-count {
  color: #6c757d;
  font-weight: 600;
  font-size: 14px;
}

.marker-samples {
  margin-top: 16px;
}

.samples-title {
  margin: 0 0 12px 0;
  color: #495057;
  font-size: 14px;
  font-weight: 500;
}

.sample-tag {
  margin-right: 8px;
  margin-bottom: 8px;
  background: rgba(0, 123, 255, 0.1);
  color: #007bff;
  border: 1px solid rgba(0, 123, 255, 0.2);
}

/* 无标识符提示区域 */
.no-markers {
  text-align: center;
  padding: 60px 24px;
  background: rgba(248, 249, 250, 0.8);
  margin: 32px 24px;
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.empty-description h3 {
  color: #2c3e50;
  margin-bottom: 16px;
  font-weight: 600;
}

.empty-description p {
  color: #6c757d;
  margin-bottom: 16px;
  line-height: 1.6;
}

.supported-markers {
  margin: 20px 0;
}

.marker-tag {
  margin: 6px 8px 6px 0;
  background: rgba(0, 123, 255, 0.1);
  color: #007bff;
  border: 1px solid rgba(0, 123, 255, 0.2);
}

.tip-text {
  color: #6c757d;
  font-size: 14px;
  margin-top: 20px;
  line-height: 1.6;
}

.empty-actions {
  margin-top: 24px;
}

:deep(.empty-actions .el-button) {
  margin: 0 8px;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

:deep(.empty-actions .el-button--primary) {
  background: linear-gradient(135deg, #007bff, #0056b3);
  border: none;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
}

:deep(.empty-actions .el-button--primary:hover) {
  background: linear-gradient(135deg, #0056b3, #004085);
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(0, 123, 255, 0.4);
}

:deep(.empty-actions .el-button--default) {
  background: #ffffff;
  border: 1px solid #dee2e6;
  color: #495057;
}

:deep(.empty-actions .el-button--default:hover) {
  border-color: #007bff;
  color: #007bff;
  background: #f8f9fa;
  transform: translateY(-1px);
}

/* 操作按钮区域 */
.actions {
  text-align: center;
  margin: 32px 24px 24px;
  padding: 24px;
  background: rgba(248, 249, 250, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-top: 1px solid rgba(0, 123, 255, 0.2);
}

:deep(.actions .el-button) {
  padding: 14px 32px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 16px;
  transition: all 0.3s ease;
}

:deep(.actions .el-button--primary) {
  background: linear-gradient(135deg, #007bff, #0056b3);
  border: none;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
}

:deep(.actions .el-button--primary:hover) {
  background: linear-gradient(135deg, #0056b3, #004085);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 123, 255, 0.4);
}

/* 说明对话框样式 */
:deep(.el-dialog) {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

:deep(.el-dialog__header) {
  background: linear-gradient(135deg, rgba(0, 123, 255, 0.03), rgba(111, 66, 193, 0.03));
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 16px 16px 0 0;
}

:deep(.el-dialog__title) {
  color: #2c3e50;
  font-weight: 600;
}

.instructions-content h4 {
  color: #2c3e50;
  margin-bottom: 16px;
  font-weight: 600;
}

.instructions-content ol {
  margin-left: 20px;
  color: #495057;
  line-height: 1.6;
}

.instructions-content ul {
  margin-left: 20px;
  margin-top: 8px;
}

.instructions-content li {
  margin-bottom: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .analyze-container {
    padding: 16px;
  }
  
  .card-header {
    padding: 24px 20px 20px;
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .card-header h2 {
    font-size: 20px;
  }
  
  .file-summary,
  .markers-section,
  .no-markers,
  .actions {
    margin: 24px 20px;
  }
  
  .no-markers {
    padding: 40px 20px;
  }
  
  .marker-info {
    padding: 16px;
  }
  
  .marker-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  :deep(.actions .el-button) {
    padding: 12px 24px;
    font-size: 14px;
  }
  
  :deep(.empty-actions .el-button) {
    margin: 4px;
    padding: 10px 20px;
  }
}
</style> 