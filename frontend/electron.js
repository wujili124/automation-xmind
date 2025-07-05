import { app, BrowserWindow, ipcMain } from 'electron';
import path from 'path';
import { spawn } from 'child_process';
import isDev from 'electron-is-dev';
import fs from 'fs';
import { fileURLToPath } from 'url';

// 获取当前文件的目录路径 (ES模块中的__dirname替代)
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 保存Python进程的引用
let pythonProcess = null;
let mainWindow = null;

// 启动Python后端
function startPythonBackend() {
  return new Promise((resolve, reject) => {
    console.log('Starting Python backend...');
    
    // 确定Python后端路径
    const isWindows = process.platform === 'win32';
    const backendDir = path.join(app.getAppPath(), '..', 'backend');
    const pythonExecutable = path.join(backendDir, isWindows ? 'venv\\Scripts\\python.exe' : 'venv/bin/python');
    const mainScript = path.join(backendDir, 'main.py');
    
    // 检查Python可执行文件是否存在
    if (!fs.existsSync(pythonExecutable)) {
      console.error(`Python executable not found: ${pythonExecutable}`);
      reject(new Error(`Python executable not found: ${pythonExecutable}`));
      return;
    }
    
    // 启动Python进程
    pythonProcess = spawn(pythonExecutable, [mainScript], {
      cwd: backendDir,
      env: { ...process.env, ELECTRON_RUN: '1' }
    });
    
    // 处理Python进程输出
    pythonProcess.stdout.on('data', (data) => {
      console.log(`Python stdout: ${data}`);
      if (data.toString().includes('正在启动XMind冒烟测试用例导出工具API服务器')) {
        console.log('Python backend started successfully');
        resolve();
      }
    });
    
    pythonProcess.stderr.on('data', (data) => {
      console.error(`Python stderr: ${data}`);
    });
    
    pythonProcess.on('error', (error) => {
      console.error(`Failed to start Python process: ${error}`);
      reject(error);
    });
    
    pythonProcess.on('close', (code) => {
      console.log(`Python process exited with code ${code}`);
      pythonProcess = null;
    });
    
    // 设置超时，避免无限等待
    setTimeout(() => {
      resolve(); // 即使没看到特定输出也继续
    }, 5000);
  });
}

// 创建主窗口
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });
  
  // 加载应用
  const startUrl = isDev 
    ? 'http://localhost:5173' // 开发环境使用Vite服务
    : `file://${path.join(__dirname, 'dist/index.html')}`; // 生产环境使用构建后的文件
  
  mainWindow.loadURL(startUrl);
  
  // 开发环境打开开发者工具
  if (isDev) {
    mainWindow.webContents.openDevTools();
  }
  
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// 应用准备就绪时创建窗口
app.whenReady().then(async () => {
  try {
    // 先启动Python后端
    await startPythonBackend();
    // 然后创建窗口
    createWindow();
  } catch (error) {
    console.error('Failed to initialize:', error);
    app.quit();
  }
  
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// 所有窗口关闭时退出应用
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// 应用退出前清理
app.on('will-quit', () => {
  // 终止Python进程
  if (pythonProcess) {
    console.log('Terminating Python backend...');
    pythonProcess.kill();
    pythonProcess = null;
  }
});

// 处理IPC通信
ipcMain.handle('get-api-base-url', () => {
  return 'http://localhost:8000'; // 返回API基础URL
}); 