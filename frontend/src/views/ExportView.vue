<template>
  <div class="export-container">
    <el-card class="export-card">
      <template #header>
        <div class="card-header">
          <h2>导出冒烟测试用例</h2>
          <el-button @click="goBack" link class="back-btn">
            <el-icon><ArrowLeft /></el-icon>
            返回分析
          </el-button>
        </div>
      </template>

      <!-- 标识符选择区域 -->
      <div class="marker-selection" v-if="analysisData">
        <h3>选择要导出的标识符</h3>
        <div class="selection-controls">
          <el-button @click="selectAll" size="small">全选</el-button>
          <el-button @click="selectNone" size="small">清空</el-button>
          <span class="selection-info"
            >已选择 {{ selectedMarkers.length }} /
            {{ analysisData.markers_found.length }} 个标识符</span
          >
        </div>

        <el-row :gutter="20" class="marker-list">
          <el-col :span="12" v-for="marker in analysisData.markers_found" :key="marker.markerId">
            <el-card class="marker-item" shadow="hover">
              <div class="marker-content">
                <el-checkbox
                  v-model="selectedMarkers"
                  :value="marker.markerId"
                  size="large"
                  class="marker-checkbox"
                >
                  <div class="marker-details">
                    <el-tag :type="getMarkerType(marker.markerId)" size="default">
                      {{ marker.symbol }}
                    </el-tag>
                    <span class="marker-count">{{ marker.count }} 个节点</span>
                  </div>
                </el-checkbox>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 导出操作区域 -->
      <div class="export-actions" v-if="selectedMarkers.length > 0">
        <el-divider />
        <div class="actions-header">
          <h3>导出设置</h3>
          <p>将根据选中的标识符生成冒烟测试用例</p>
        </div>

        <div class="action-buttons">
          <el-button type="primary" size="large" @click="exportTestCases" :loading="exporting">
            {{ exporting ? "生成中..." : "导出冒烟用例" }}
          </el-button>
        </div>
      </div>

      <!-- 结果展示区域 -->
      <div class="result-section" v-if="exportResult">
        <el-divider />
        <div class="result-header">
          <h3>导出结果</h3>
          <div class="result-summary">
            <el-tag type="success"
              >成功生成 {{ exportResult.smoke_test_suite.metadata.total_cases }} 个冒烟用例</el-tag
            >
          </div>
        </div>

        <!-- 表格展示 -->
        <div class="table-display">
          <div class="display-controls">
            <el-tabs v-model="activeTab" class="result-tabs">
              <el-tab-pane label="测试用例表格" name="table">
                <div class="table-controls">
                  <el-button @click="exportExcel" type="success" size="small">
                    <el-icon><Document /></el-icon>
                    导出Excel
                  </el-button>
                  <el-button @click="exportXMind" type="primary" size="small">
                    <el-icon><FolderOpened /></el-icon>
                    导出XMind
                  </el-button>
                </div>

                <el-table
                  :data="testCasesTableData"
                  border
                  stripe
                  class="test-cases-table"
                  :default-sort="{ prop: 'case_id', order: 'ascending' }"
                >
                  <el-table-column prop="case_id" label="用例ID" width="120" sortable />
                  <el-table-column
                    prop="title"
                    label="测试用例标题"
                    min-width="200"
                    show-overflow-tooltip
                  />
                  <el-table-column prop="module" label="模块" width="150" show-overflow-tooltip />
                  <el-table-column prop="priority" label="优先级" width="80" align="center">
                    <template #default="scope">
                      <el-tag :type="getPriorityType(scope.row.priority)" size="small">
                        {{ scope.row.priority }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="steps_count" label="步骤数" width="80" align="center" />
                  <el-table-column prop="markers" label="标识符" width="120">
                    <template #default="scope">
                      <el-tag
                        v-for="marker in scope.row.markers"
                        :key="marker"
                        :type="getMarkerType(marker)"
                        size="small"
                        class="marker-tag"
                      >
                        {{ marker }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="100" align="center">
                    <template #default="scope">
                      <el-button @click="showTestCaseDetail(scope.row)" type="text" size="small">
                        查看详情
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </el-tab-pane>

              <el-tab-pane label="JSON数据" name="json">
                <div class="json-controls">
                  <el-button @click="copyToClipboard" type="default" size="small">
                    <el-icon><CopyDocument /></el-icon>
                    复制JSON
                  </el-button>
                  <el-button @click="downloadJson" type="default" size="small">
                    <el-icon><Download /></el-icon>
                    下载JSON
                  </el-button>
                </div>

                <el-input
                  v-model="formattedJson"
                  type="textarea"
                  :rows="20"
                  readonly
                  class="json-textarea"
                  placeholder="JSON数据将在这里显示..."
                />
              </el-tab-pane>
            </el-tabs>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 测试用例详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="测试用例详情" width="800px">
      <div v-if="selectedTestCase" class="test-case-detail">
        <el-descriptions title="用例信息" :column="2" border>
          <el-descriptions-item label="用例ID">{{ selectedTestCase.case_id }}</el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tag :type="getPriorityType(selectedTestCase.priority)">
              {{ selectedTestCase.priority }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="测试模块">{{
            selectedTestCase.module
          }}</el-descriptions-item>
          <el-descriptions-item label="测试路径">{{
            selectedTestCase.test_path
          }}</el-descriptions-item>
        </el-descriptions>

        <h4 style="margin-top: 20px">测试步骤</h4>
        <el-table :data="selectedTestCase.steps" border class="steps-table">
          <el-table-column prop="step" label="步骤" width="60" align="center" />
          <el-table-column prop="action" label="操作步骤" min-width="200" />
          <el-table-column prop="expected" label="预期结果" min-width="200" />
        </el-table>

        <div v-if="selectedTestCase.smoke_criteria" style="margin-top: 20px">
          <h4>冒烟测试指标</h4>
          <el-tag
            v-if="selectedTestCase.smoke_criteria.is_core_function"
            type="danger"
            class="criteria-tag"
          >
            核心功能
          </el-tag>
          <el-tag
            v-if="selectedTestCase.smoke_criteria.affects_main_flow"
            type="warning"
            class="criteria-tag"
          >
            影响主流程
          </el-tag>
          <el-tag type="info" class="criteria-tag">
            {{ selectedTestCase.smoke_criteria.execution_time }}
          </el-tag>
        </div>
      </div>

      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { ArrowLeft, CopyDocument, Download, Document, FolderOpened } from "@element-plus/icons-vue";
import axios from "axios";
import * as XLSX from "xlsx";

interface MarkerInfo {
  markerId: string;
  symbol: string;
  count: number;
  sample_nodes?: string[];
}

interface AnalysisData {
  filename: string;
  markers_found: MarkerInfo[];
  total_nodes: number;
  suitable_for_smoke: number;
  file_data: string;
}

interface ExportResult {
  smoke_test_suite: {
    metadata: {
      source_file: string;
      export_time: string;
      selected_markers: string[];
      total_cases: number;
    };
    test_cases: any[];
  };
}

const router = useRouter();
const route = useRoute();
const analysisData = ref<AnalysisData | null>(null);
const selectedMarkers = ref<string[]>([]);
const exportResult = ref<ExportResult | null>(null);
const exporting = ref(false);
const activeTab = ref("table");
const showDetailDialog = ref(false);
const selectedTestCase = ref<any | null>(null);

// API基础URL
const API_BASE_URL = "http://localhost:8000";

// 格式化后的JSON字符串
const formattedJson = computed(() => {
  if (!exportResult.value) return "";
  return JSON.stringify(exportResult.value, null, 2);
});

// 表格数据
const testCasesTableData = computed(() => {
  if (!exportResult.value || !exportResult.value.smoke_test_suite.test_cases) return [];

  return exportResult.value.smoke_test_suite.test_cases.map((testCase) => ({
    case_id: testCase.case_id,
    title: testCase.title,
    module: testCase.module,
    priority: testCase.priority,
    steps_count: testCase.steps ? testCase.steps.length : 0,
    markers: testCase.markers || [],
    test_path: testCase.test_path,
    steps: testCase.steps || [],
    smoke_criteria: testCase.smoke_criteria,
  }));
});

onMounted(() => {
  // 从sessionStorage中获取分析数据，而不是从URL query参数
  try {
    const dataStr = sessionStorage.getItem("analysisData");
    if (dataStr) {
      analysisData.value = JSON.parse(dataStr);
      console.log("分析数据加载成功:", analysisData.value);

      // 默认选择所有标识符
      if (analysisData.value?.markers_found) {
        selectedMarkers.value = analysisData.value.markers_found.map((m) => m.markerId);
      }
    } else {
      ElMessage.warning("未找到分析数据，请重新分析文件");
      goBack();
    }
  } catch (error) {
    console.error("解析分析数据失败:", error);
    ElMessage.error("数据解析失败，请重新分析文件");
    goBack();
  }
});

const goBack = () => {
  router.push({ name: "analyze" });
};

const selectAll = () => {
  if (analysisData.value?.markers_found) {
    selectedMarkers.value = analysisData.value.markers_found.map((m) => m.markerId);
  }
};

const selectNone = () => {
  selectedMarkers.value = [];
};

const getMarkerType = (markerId: string): string => {
  if (markerId === "important") return "danger";
  if (markerId.startsWith("priority-1")) return "danger";
  if (markerId.startsWith("priority-2")) return "warning";
  if (markerId.startsWith("priority-3")) return "primary";
  if (markerId.startsWith("priority-4")) return "success";
  if (markerId.startsWith("priority-5")) return "info";
  if (markerId.includes("red")) return "danger";
  if (markerId.includes("yellow")) return "warning";
  return "primary";
};

const getPriorityType = (priority: string): string => {
  if (priority === "important") return "danger";
  if (priority.startsWith("priority-1")) return "danger";
  if (priority.startsWith("priority-2")) return "warning";
  if (priority.startsWith("priority-3")) return "primary";
  if (priority.startsWith("priority-4")) return "success";
  if (priority.startsWith("priority-5")) return "info";
  return "primary";
};

const exportTestCases = async () => {
  if (!analysisData.value || selectedMarkers.value.length === 0) {
    ElMessage.error("请至少选择一个标识符");
    return;
  }

  exporting.value = true;

  try {
    console.log("开始导出冒烟用例...", {
      selectedMarkers: selectedMarkers.value,
      fileData: analysisData.value.file_data ? "已提供" : "缺失",
    });

    const response = await axios.post(
      `${API_BASE_URL}/api/export`,
      {
        selected_markers: selectedMarkers.value,
        file_data: analysisData.value.file_data,
      },
      {
        timeout: 30000, // 30秒超时
      }
    );

    exportResult.value = response.data;
    console.log("导出完成:", exportResult.value);

    if (exportResult.value) {
      ElMessage.success(
        `成功生成 ${exportResult.value.smoke_test_suite.metadata.total_cases} 个冒烟用例!`
      );
    }
  } catch (error: any) {
    console.error("导出失败:", error);

    let errorMessage = "导出失败";
    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    } else if (error.message) {
      errorMessage = error.message;
    }

    ElMessageBox.alert(errorMessage, "错误", {
      confirmButtonText: "确定",
      type: "error",
    });
  } finally {
    exporting.value = false;
  }
};

const copyToClipboard = async () => {
  if (!formattedJson.value) {
    ElMessage.error("没有可复制的内容");
    return;
  }

  try {
    await navigator.clipboard.writeText(formattedJson.value);
    ElMessage.success("已复制到剪贴板");
  } catch (error) {
    console.error("复制失败:", error);
    ElMessage.error("复制失败，请手动选择复制");
  }
};

const downloadJson = () => {
  if (!exportResult.value) {
    ElMessage.error("没有可下载的内容");
    return;
  }

  const blob = new Blob([formattedJson.value], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `smoke_test_cases_${new Date().getTime()}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  ElMessage.success("文件下载已开始");
};

const exportExcel = async () => {
  if (!exportResult.value || !testCasesTableData.value.length) {
    ElMessage.error("没有可导出的测试用例数据");
    return;
  }

  if (!analysisData.value?.file_data) {
    ElMessage.error("缺少原始文件数据，无法生成Excel");
    return;
  }

  try {
    ElMessage.info("正在生成增强层级合并Excel文件...");
    
    console.log("调用增强层级合并API:", {
      selectedMarkers: selectedMarkers.value,
      hasFileData: !!analysisData.value.file_data
    });
    
    // 调用后端的增强层级合并API
    const response = await axios.post(
      `${API_BASE_URL}/api/export-enhanced-hierarchical`,
      {
        selected_markers: selectedMarkers.value,
        file_data: analysisData.value.file_data,
      },
      {
        timeout: 30000, // 30秒超时
      }
    );
    
    if (response.data.success) {
      console.log("增强层级合并Excel生成成功:", {
        hasMergedCells: response.data.export_details?.merged_regions_count > 0,
        mergedRegions: response.data.export_details?.merged_regions_count,
        dataRows: response.data.export_details?.data_rows,
        features: response.data.export_details?.features
      });
      
      // 将base64数据转换为Blob
      const binaryString = atob(response.data.file_data);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      const blob = new Blob([bytes], { 
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
      });
      
      // 下载文件
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      
      const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, "-");
      a.download = `🔥增强层级合并_冒烟测试用例_${timestamp}.xlsx`;
      
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      // 显示详细的成功信息
      const details = response.data.export_details;
      const mergedCount = details?.merged_regions_count || 0;
      const dataRows = details?.data_rows || 0;
      const features = details?.features || [];
      
      ElMessage.success({
        message: `🎉 增强层级合并Excel导出成功！\n✅ 数据行数: ${dataRows}行\n✅ 智能合并: ${mergedCount}个区域\n✅ 特性: ${features.slice(0, 2).join(", ")}`,
        duration: 8000,
        showClose: true
      });
      
      console.log("Excel文件下载完成，文件名包含🔥标识");
      
    } else {
      throw new Error(response.data.message || "后端处理失败");
    }
    
  } catch (error: any) {
    console.error("增强Excel导出失败:", error);
    
    let errorMessage = "增强Excel导出失败";
    if (error.response?.data?.detail) {
      errorMessage = `后端错误: ${error.response.data.detail}`;
    } else if (error.message) {
      errorMessage = `错误: ${error.message}`;
    }
    
    ElMessage.error(errorMessage);
    
    // 如果后端失败，提供传统Excel作为备选方案
    ElMessageBox.confirm(
      '增强版导出失败，是否生成传统格式Excel作为备选？',
      '导出失败',
      {
        confirmButtonText: '生成传统格式',
        cancelButtonText: '取消',
        type: 'warning',
      }
    ).then(() => {
      exportExcelTraditional();
    }).catch(() => {
      ElMessage.info('已取消导出');
    });
  }
};

// 传统Excel导出方法（作为备选方案）
const exportExcelTraditional = () => {
  try {
    // 准备Excel数据
    const excelData = testCasesTableData.value.map((testCase) => ({
      用例ID: testCase.case_id,
      测试用例标题: testCase.title,
      模块: testCase.module,
      优先级: testCase.priority,
      标识符: testCase.markers.join(", "),
      测试路径: testCase.test_path,
      步骤数: testCase.steps_count,
      测试步骤: testCase.steps
        .map((step: any, index: number) => `${step.step}. ${step.action} -> ${step.expected}`)
        .join("\n"),
      是否核心功能: testCase.smoke_criteria?.is_core_function ? "是" : "否",
      是否影响主流程: testCase.smoke_criteria?.affects_main_flow ? "是" : "否",
      执行时间: testCase.smoke_criteria?.execution_time || "< 2分钟",
    }));

    // 创建工作簿
    const wb = XLSX.utils.book_new();

    // 创建测试用例列表工作表
    const ws1 = XLSX.utils.json_to_sheet(excelData);

    // 设置列宽
    const colWidths = [
      { wch: 12 }, // 用例ID
      { wch: 30 }, // 测试用例标题
      { wch: 15 }, // 模块
      { wch: 8 }, // 优先级
      { wch: 20 }, // 标识符
      { wch: 40 }, // 测试路径
      { wch: 8 }, // 步骤数
      { wch: 50 }, // 测试步骤
      { wch: 12 }, // 是否核心功能
      { wch: 12 }, // 是否影响主流程
      { wch: 12 }, // 执行时间
    ];
    ws1["!cols"] = colWidths;

    // 添加工作表到工作簿
    XLSX.utils.book_append_sheet(wb, ws1, "冒烟测试用例");

    // 创建汇总信息工作表
    const summaryData = [
      ["项目", "值"],
      ["源文件", exportResult.value.smoke_test_suite.metadata.source_file],
      [
        "导出时间",
        new Date(exportResult.value.smoke_test_suite.metadata.export_time).toLocaleString("zh-CN"),
      ],
      ["选中标识符", exportResult.value.smoke_test_suite.metadata.selected_markers.join(", ")],
      ["总用例数", exportResult.value.smoke_test_suite.metadata.total_cases],
      ["", ""],
      ["标识符统计", ""],
      ["P1 (高优先级)", excelData.filter((item) => item["优先级"] === "P1").length],
      ["P2 (中优先级)", excelData.filter((item) => item["优先级"] === "P2").length],
      ["P3 (标准优先级)", excelData.filter((item) => item["优先级"] === "P3").length],
      ["", ""],
      ["冒烟测试统计", ""],
      ["核心功能用例", excelData.filter((item) => item["是否核心功能"] === "是").length],
      ["影响主流程用例", excelData.filter((item) => item["是否影响主流程"] === "是").length],
    ];

    const ws2 = XLSX.utils.aoa_to_sheet(summaryData);
    ws2["!cols"] = [{ wch: 20 }, { wch: 30 }];
    XLSX.utils.book_append_sheet(wb, ws2, "导出汇总");

    // 生成文件名
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, "-");
    const filename = `传统格式_冒烟测试用例_${timestamp}.xlsx`;

    // 导出文件
    XLSX.writeFile(wb, filename);

    ElMessage.success(`传统格式Excel文件已导出: ${filename}`);
  } catch (error) {
    console.error("传统Excel导出失败:", error);
    ElMessage.error("传统Excel导出失败，请重试");
  }
};

const exportXMind = async () => {
  if (!exportResult.value || !testCasesTableData.value.length) {
    ElMessage.error("没有可导出的测试用例数据");
    return;
  }
  
  if (!analysisData.value?.file_data) {
    ElMessage.error("缺少原始文件数据，无法保持原始样式");
    return;
  }

  try {
    ElMessage.info("正在调用后端过滤XMind文件...");
    
    // 提取测试用例标题
    const testCaseTitles = testCasesTableData.value.map(tc => tc.title);
    
    console.log("准备调用后端API:", {
      selectedMarkers: selectedMarkers.value,
      testCaseTitlesCount: testCaseTitles.length,
      testCaseTitles: testCaseTitles.slice(0, 5) // 显示前5个标题
    });
    
    // 调用后端API进行XMind文件过滤
    const response = await axios.post(
      `${API_BASE_URL}/api/export-xmind`,
      {
        selected_markers: selectedMarkers.value,
        file_data: analysisData.value.file_data,
        test_case_titles: testCaseTitles
      },
      {
        timeout: 60000, // 60秒超时，因为文件处理可能需要更长时间
      }
    );
    
    if (response.data.success) {
      console.log("后端处理成功:", {
        originalSize: response.data.processing_details?.original_size,
        filteredSize: response.data.processing_details?.filtered_size,
        nodesFiltered: response.data.processing_details?.nodes_removed,
        compressionRatio: response.data.processing_details?.compression_ratio,
        processingEngine: response.data.processing_details?.processing_engine,
        sheetsProcessed: response.data.processing_details?.sheets_processed,
        sheetsRemoved: response.data.processing_details?.sheets_removed,
        targetMarkers: response.data.processing_details?.target_markers
      });
      
      // 将base64数据转换为Blob
      const binaryString = atob(response.data.file_data);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      const blob = new Blob([bytes], { type: 'application/vnd.xmind' });
      
      // 下载文件
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      
      const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, "-");
      a.download = `冒烟测试用例_基于标识符_${timestamp}.xmind`;
      
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      // 显示详细的成功信息
      const details = response.data.processing_details;
      const nodesRemoved = details?.nodes_removed || 0;
      const compressionRatio = details?.compression_ratio || "N/A";
      const targetMarkers = details?.target_markers?.join(", ") || "";
      
      ElMessage.success({
        message: `XMind文件导出成功！\n基于标识符: [${targetMarkers}]\n删除节点: ${nodesRemoved}个\n压缩率: ${compressionRatio}`,
        duration: 6000,
        showClose: true
      });
    } else {
      throw new Error(response.data.message || "后端处理失败");
    }
    
  } catch (error: any) {
    console.error("XMind导出失败:", error);
    
    let errorMessage = "XMind导出失败";
    if (error.response?.data?.detail) {
      errorMessage = `后端错误: ${error.response.data.detail}`;
    } else if (error.message) {
      errorMessage = `错误: ${error.message}`;
    }
    
    ElMessage.error(errorMessage);
  }
};

const showTestCaseDetail = (testCase: any) => {
  selectedTestCase.value = testCase;
  showDetailDialog.value = true;
};
</script>

<style scoped>

/* 主容器 - 科技感背景 */
.export-container {
  min-height: 100vh;
  padding: 20px;
  background: linear-gradient(135deg, #1e1e2e 0%, #2a2d3a 100%);
  position: relative;
}

/* 添加微妙的网格背景 */
.export-container::before {
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
.export-card {
  max-width: 1200px;
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
.export-card::before {
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
.export-card:hover {
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

/* 标识符选择区域 */
.marker-selection {
  margin: 32px 24px;
}

.marker-selection h3 {
  margin: 0 0 24px 0;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
}

.selection-controls {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding: 16px 20px;
  background: rgba(248, 249, 250, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

:deep(.selection-controls .el-button) {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

:deep(.selection-controls .el-button--default) {
  background: #ffffff;
  border: 1px solid #dee2e6;
  color: #495057;
}

:deep(.selection-controls .el-button--default:hover) {
  border-color: #007bff;
  color: #007bff;
  background: #f8f9fa;
  transform: translateY(-1px);
}

.selection-info {
  color: #6c757d;
  font-size: 14px;
  font-weight: 500;
  margin-left: auto;
}

.marker-list {
  margin-bottom: 24px;
}

/* 标识符卡片 */
.marker-item {
  margin-bottom: 16px;
  height: 100%;
  background: rgba(248, 249, 250, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  overflow: hidden;
}

.marker-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 123, 255, 0.15);
  border-color: rgba(0, 123, 255, 0.2);
}

.marker-content {
  padding: 20px;
}

.marker-checkbox {
  width: 100%;
}

:deep(.marker-checkbox .el-checkbox__label) {
  width: 100%;
}

.marker-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-left: 16px;
  width: 100%;
}

.marker-count {
  color: #6c757d;
  font-size: 14px;
  font-weight: 500;
}

/* 导出操作区域 */
.export-actions {
  margin: 32px 24px;
}

:deep(.export-actions .el-divider) {
  border-color: rgba(0, 123, 255, 0.2);
}

.actions-header {
  text-align: center;
  margin-bottom: 24px;
  padding: 24px;
  background: rgba(248, 249, 250, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.actions-header h3 {
  margin: 0 0 12px 0;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
}

.actions-header p {
  margin: 0;
  color: #6c757d;
  font-size: 15px;
  line-height: 1.5;
}

.action-buttons {
  text-align: center;
  margin-top: 20px;
}

:deep(.action-buttons .el-button) {
  padding: 14px 32px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 16px;
  transition: all 0.3s ease;
}

:deep(.action-buttons .el-button--primary) {
  background: linear-gradient(135deg, #007bff, #0056b3);
  border: none;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
}

:deep(.action-buttons .el-button--primary:hover) {
  background: linear-gradient(135deg, #0056b3, #004085);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 123, 255, 0.4);
}

/* 结果展示区域 */
.result-section {
  margin: 32px 24px 24px;
}

:deep(.result-section .el-divider) {
  border-color: rgba(0, 123, 255, 0.2);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 20px;
  background: rgba(248, 249, 250, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.result-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
}

.result-summary {
  display: flex;
  gap: 12px;
}

/* 表格显示区域 */
.table-display {
  background: rgba(248, 249, 250, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  padding: 24px;
  margin-top: 20px;
  height: 500px;
  overflow-y: scroll;
}

.display-controls {
  margin-bottom: 20px;
  display: flex;
  gap: 12px;
}

.result-tabs {
  width: 100%;
  min-height: 400px;
}

:deep(.result-tabs .el-tabs__header) {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  padding: 8px;
  margin-bottom: 20px;
}

:deep(.result-tabs .el-tabs__nav) {
  border: none;
}

:deep(.result-tabs .el-tabs__item) {
  border-radius: 6px;
  padding: 8px 16px;
  margin-right: 4px;
  transition: all 0.3s ease;
}

:deep(.result-tabs .el-tabs__item.is-active) {
  background: #007bff;
  color: #ffffff;
}

:deep(.result-tabs .el-tabs__item:hover) {
  background: rgba(0, 123, 255, 0.1);
  color: #007bff;
}

.table-controls {
  margin-bottom: 16px;
  display: flex;
  gap: 12px;
}

:deep(.table-controls .el-button) {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

:deep(.table-controls .el-button--success) {
  background: linear-gradient(135deg, #28a745, #1e7e34);
  border: none;
  box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
}

:deep(.table-controls .el-button--success:hover) {
  background: linear-gradient(135deg, #1e7e34, #155724);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.4);
}

:deep(.table-controls .el-button--default) {
  background: #ffffff;
  border: 1px solid #dee2e6;
  color: #495057;
}

:deep(.table-controls .el-button--default:hover) {
  border-color: #007bff;
  color: #007bff;
  background: #f8f9fa;
  transform: translateY(-1px);
}

/* 表格样式 */
.test-cases-table {
  margin-top: 20px;
  border-radius: 8px;
  overflow: hidden;
}

:deep(.test-cases-table .el-table__header) {
  background: linear-gradient(135deg, rgba(0, 123, 255, 0.08), rgba(111, 66, 193, 0.08));
}

:deep(.test-cases-table .el-table__header th) {
  background: transparent;
  color: #2c3e50;
  font-weight: 600;
  border-color: rgba(0, 0, 0, 0.1);
}

:deep(.test-cases-table .el-table__body tr:hover) {
  background: rgba(0, 123, 255, 0.05);
}

.marker-tag {
  margin-right: 4px;
  margin-bottom: 4px;
}

/* JSON控制区域 */
.json-controls {
  margin-bottom: 16px;
  display: flex;
  gap: 12px;
}

:deep(.json-controls .el-button) {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

:deep(.json-controls .el-button--default) {
  background: #ffffff;
  border: 1px solid #dee2e6;
  color: #495057;
}

:deep(.json-controls .el-button--default:hover) {
  border-color: #007bff;
  color: #007bff;
  background: #f8f9fa;
  transform: translateY(-1px);
}

/* JSON文本区域 */
.json-textarea {
  font-family: "Monaco", "Menlo", "Ubuntu Mono", monospace;
  font-size: 12px;
  border-radius: 8px;
}

:deep(.json-textarea .el-textarea__inner) {
  font-family: "Monaco", "Menlo", "Ubuntu Mono", monospace;
  font-size: 12px;
  line-height: 1.4;
  background: rgba(248, 249, 250, 0.8);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

/* 对话框样式 */
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

/* 测试用例详情 */
.test-case-detail {
  padding: 20px;
}

:deep(.test-case-detail .el-descriptions__header) {
  background: linear-gradient(135deg, rgba(0, 123, 255, 0.08), rgba(111, 66, 193, 0.08));
  padding: 16px 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 8px 8px 0 0;
}

:deep(.test-case-detail .el-descriptions__title) {
  color: #2c3e50;
  font-size: 16px;
  font-weight: 600;
}

:deep(.test-case-detail .el-descriptions-item__label) {
  background: #f8f9fa;
  color: #495057;
  font-weight: 500;
  border: 1px solid #e9ecef;
}

:deep(.test-case-detail .el-descriptions-item__content) {
  background: #ffffff;
  color: #2c3e50;
  border: 1px solid #e9ecef;
  font-weight: 400;
}

.steps-table {
  margin-top: 20px;
  border-radius: 8px;
  overflow: hidden;
}

:deep(.steps-table .el-table__header) {
  background: linear-gradient(135deg, rgba(0, 123, 255, 0.08), rgba(111, 66, 193, 0.08));
}

:deep(.steps-table .el-table__header th) {
  background: transparent;
  color: #2c3e50;
  font-weight: 600;
  border-color: rgba(0, 0, 0, 0.1);
}

.criteria-tag {
  margin-left: 8px;
  margin-right: 8px;
  margin-bottom: 4px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .export-container {
    padding: 16px;
  }
  
  .export-card {
    max-width: 100%;
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
  
  .marker-selection,
  .export-actions,
  .result-section {
    margin: 24px 20px;
  }
  
  .selection-controls {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .selection-info {
    margin-left: 0;
  }
  
  .result-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .table-display {
    padding: 16px;
  }
  
  .display-controls,
  .table-controls,
  .json-controls {
    flex-direction: column;
    gap: 8px;
  }
  
  :deep(.action-buttons .el-button) {
    padding: 12px 24px;
    font-size: 14px;
  }
  
  .test-case-detail {
    padding: 16px;
  }
  
  .marker-content {
    padding: 16px;
  }
}
</style>

