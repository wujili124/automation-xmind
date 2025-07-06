const { app, BrowserWindow, ipcMain, dialog, globalShortcut } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

// 确定正确的python_finder路径
const isDev = !app.isPackaged;
let pythonFinderPath;

try {
  // 开发环境使用相对路径
  if (isDev) {
    pythonFinderPath = './scripts/python_finder.cjs';
    console.log(`Development mode, using path: ${pythonFinderPath}`);
  } else {
    // 生产环境尝试不同的可能路径
    const possiblePaths = [
      path.join(__dirname, 'scripts', 'python_finder.cjs'),
      path.join(process.resourcesPath, 'scripts', 'python_finder.cjs'),
      path.join(app.getAppPath(), 'scripts', 'python_finder.cjs')
    ];
    
    console.log('Checking possible python_finder paths:');
    possiblePaths.forEach(p => console.log(` - ${p} (exists: ${fs.existsSync(p)})`));
    
    // 找到第一个存在的路径
    pythonFinderPath = possiblePaths.find(p => fs.existsSync(p));
    
    if (!pythonFinderPath) {
      console.error('Could not find python_finder.cjs module!');
      throw new Error('Missing required module: python_finder.cjs');
    }
    
    console.log(`Production mode, using path: ${pythonFinderPath}`);
  }
  
  const { findPythonExecutable } = require(pythonFinderPath);
} catch (error) {
  console.error(`Error loading python_finder module: ${error.message}`);
  process.exit(1);
}

// 正确引入 findPythonExecutable 函数
const { findPythonExecutable } = require(pythonFinderPath);

// 保存Python进程的引用
let pythonProcess = null;
let mainWindow = null;

// 启动Python后端
function startPythonBackend() {
  return new Promise((resolve, reject) => {
    console.log('Starting Python backend...');
    
    // 使用Python查找工具查找可用的Python后端
    const pythonInfo = findPythonExecutable(
      app.getAppPath(), 
      isDev ? path.join(app.getAppPath(), '..') : process.resourcesPath
    );
    
    if (!pythonInfo.executablePath) {
      const errorMsg = '未找到Python可执行文件，无法启动后端服务';
      console.error(errorMsg);
      
      // 显示错误但继续尝试启动应用
      dialog.showMessageBox({
        type: 'warning',
        title: '后端启动警告',
        message: '未找到Python可执行文件，应用可能无法正常工作',
        detail: `应用将继续启动，但某些功能可能不可用。`,
        buttons: ['继续']
      });
      
      resolve(); // 即使没找到Python也继续
      return;
    }
    
    console.log(`使用 ${pythonInfo.pythonType} 类型的Python: ${pythonInfo.executablePath}`);
    console.log(`后端目录: ${pythonInfo.backendDir}`);
    
    // 根据Python类型启动后端
    if (pythonInfo.pythonType === 'pyinstaller') {
      // PyInstaller打包的独立可执行文件
      pythonProcess = spawn(pythonInfo.executablePath, [], {
        cwd: pythonInfo.backendDir,
        env: { ...process.env, ELECTRON_RUN: '1' }
      });
    } else {
      // 其他类型的Python (venv, miniconda, system)
      if (!pythonInfo.mainScript || !fs.existsSync(pythonInfo.mainScript)) {
        console.error(`主脚本不存在: ${pythonInfo.mainScript}`);
        
        dialog.showMessageBox({
          type: 'warning',
          title: '后端启动警告',
          message: '找不到Python主脚本',
          detail: `未找到: ${pythonInfo.mainScript}\n应用将继续启动，但某些功能可能不可用。`,
          buttons: ['继续']
        });
        
        resolve();
        return;
      }
      
      // 启动Python进程
      pythonProcess = spawn(pythonInfo.executablePath, [pythonInfo.mainScript], {
        cwd: pythonInfo.backendDir,
        env: { ...process.env, ELECTRON_RUN: '1' }
      });
    }
    
    // 处理Python进程输出
    pythonProcess.stdout.on('data', (data) => {
      console.log(`Python stdout: ${data}`);
      if (data.toString().includes('正在启动XMind冒烟测试用例导出工具API服务器') ||
          data.toString().includes('Application startup complete')) {
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
      console.log('Python backend startup timeout reached, continuing anyway');
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
      preload: path.join(__dirname, 'preload.cjs')
    },
    show: false // 先不显示窗口，等加载完成后再显示
  });
  
  // 加载应用 - 正确处理开发环境和打包环境的路径
  let startUrl;
  
  if (isDev) {
    // 开发环境使用Vite服务
    startUrl = 'http://localhost:5173';
  } else {
    // 生产环境 - 检查可能的路径
    const possiblePaths = [
      path.join(process.resourcesPath, 'dist', 'index.html'),
      path.join(app.getAppPath(), 'dist', 'index.html'),
      path.join(__dirname, 'dist', 'index.html')
    ];
    
    console.log('检查可能的index.html路径:');
    possiblePaths.forEach(p => console.log(` - ${p} (存在: ${fs.existsSync(p)})`));
    
    // 找到第一个存在的路径
    const existingPath = possiblePaths.find(p => fs.existsSync(p));
    
    if (existingPath) {
      startUrl = `file://${existingPath}`;
      console.log(`找到index.html, 加载: ${startUrl}`);
    } else {
      console.error('未找到index.html文件，应用可能无法正常工作');
      startUrl = `file://${path.join(process.resourcesPath, 'dist', 'index.html')}`;
    }
  }
  
  console.log(`Loading URL: ${startUrl} (isDev: ${isDev})`);
  
  // 添加加载错误处理
  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
    console.error(`Failed to load URL: ${errorDescription} (${errorCode})`);
    
    // 显示错误对话框
    dialog.showErrorBox('加载失败', `应用程序加载失败: ${errorDescription}\n\n加载路径: ${startUrl}`);
    
    // 尝试重新加载
    if (!isDev) {
      setTimeout(() => mainWindow.loadURL(startUrl), 1000);
    }
  });
  
  // 窗口准备好后显示
  mainWindow.once('ready-to-show', () => {
    console.log('Window ready to show');
    mainWindow.show();
  });
  
  mainWindow.loadURL(startUrl);
  
  // 开发环境打开开发者工具
  // if (isDev) {
    // 热键打开开发者工具command+option+i
    globalShortcut.register('CommandOrControl+Option+I', () => {
      mainWindow.webContents.openDevTools();
    });
  // }
  
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// 应用准备就绪时创建窗口
app.whenReady().then(async () => {
  try {
    console.log(`应用启动 - 环境: ${isDev ? '开发' : '生产'}`);
    console.log(`App path: ${app.getAppPath()}`);
    console.log(`__dirname: ${__dirname}`);
    console.log(`resourcesPath: ${process.resourcesPath}`);
    
    // 先启动Python后端
    await startPythonBackend();
    
    // 然后创建窗口
    createWindow();
  } catch (error) {
    console.error('Failed to initialize:', error);
    dialog.showErrorBox('初始化失败', `应用程序初始化失败: ${error.message}`);
    app.quit();
  }
  
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('quit', () => {
  // 确保Python进程被终止
  if (pythonProcess !== null) {
    pythonProcess.kill();
    pythonProcess = null;
  }
});

// 处理IPC通信
ipcMain.handle('get-api-base-url', () => {
  return 'http://127.0.0.1:8000'; // 返回API基础URL，使用IP地址而不是localhost
});

// 检查后端是否可访问
ipcMain.handle('check-backend-status', async () => {
  try {
    console.log('Checking backend status...');
    const http = require('http');
    
    return new Promise((resolve) => {
      const req = http.get('http://127.0.0.1:8000/health', (res) => {
        let data = '';
        res.on('data', (chunk) => {
          data += chunk;
        });
        
        res.on('end', () => {
          console.log(`Backend health check response: ${data}`);
          resolve({ status: 'online', statusCode: res.statusCode });
        });
      });
      
      req.on('error', (err) => {
        console.error(`Backend health check failed: ${err.message}`);
        resolve({ status: 'offline', error: err.message });
      });
      
      req.setTimeout(3000, () => {
        req.destroy();
        console.log('Backend health check timed out');
        resolve({ status: 'timeout', error: 'Request timed out' });
      });
    });
  } catch (error) {
    console.error(`Error checking backend status: ${error.message}`);
    return { status: 'error', error: error.message };
  }
}); 