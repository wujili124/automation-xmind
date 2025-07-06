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

// 保存Python进程的引用和端口号
let pythonProcess = null;
let pythonPort = null;
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
      
      // 显示错误对话框
      dialog.showErrorBox('后端启动失败', 
        '未找到Python可执行文件，应用无法正常工作。\n\n' +
        '请确保以下任一条件满足：\n' +
        '1. Python虚拟环境完整（包含所有依赖）\n' +
        '2. 系统安装了Python 3.8或更高版本\n' +
        '\n详细错误：找不到可用的Python环境'
      );
      
      reject(new Error(errorMsg));
      return;
    }
    
    console.log(`使用 ${pythonInfo.pythonType} 类型的Python: ${pythonInfo.executablePath}`);
    
    // 检查Python环境
    const checkPythonEnv = spawn(pythonInfo.executablePath, ['-c', 'import fastapi, uvicorn, lxml']);
    checkPythonEnv.on('error', (err) => {
      console.error('Python环境检查失败:', err);
      dialog.showErrorBox('后端启动失败', 
        '无法启动Python环境。\n\n' +
        '错误原因：\n' +
        `${err.message}\n\n` +
        '请确保Python环境中安装了所有必要的依赖。'
      );
      reject(err);
    });
    
    checkPythonEnv.on('exit', (code) => {
      if (code !== 0) {
        console.error(`Python环境检查失败，退出码: ${code}`);
        dialog.showErrorBox('后端启动失败',
          'Python环境缺少必要的依赖。\n\n' +
          '请确保以下Python包已正确安装：\n' +
          '- fastapi\n' +
          '- uvicorn\n' +
          '- lxml'
        );
        reject(new Error(`Python环境检查失败，退出码: ${code}`));
        return;
      }
      
      // 启动后端服务
      pythonProcess = spawn(pythonInfo.executablePath, [
        path.join(pythonInfo.backendDir, 'main.py')
      ], {
        env: { ...process.env, ELECTRON_RUN: '1' },
        cwd: pythonInfo.backendDir  // 设置工作目录为后端目录
      });
      
      // 收集Python进程的输出
      let pythonOutput = '';
      
      pythonProcess.stdout.on('data', (data) => {
        const output = data.toString();
        pythonOutput += output;
        console.log(`Python后端输出: ${output}`);
      });
      
      pythonProcess.stderr.on('data', (data) => {
        const error = data.toString();
        pythonOutput += error;
        console.error(`Python后端错误: ${error}`);
      });
      
      pythonProcess.on('error', (error) => {
        console.error(`Python进程启动失败: ${error.message}`);
        dialog.showErrorBox('后端启动失败', 
          '无法启动Python后端进程。\n\n' +
          '错误信息：\n' +
          error.message + '\n\n' +
          '请检查Python环境是否正确安装。'
        );
        reject(error);
      });
      
      pythonProcess.on('exit', (code, signal) => {
        if (code !== 0) {
          console.error(`Python进程异常退出，退出码: ${code}, 信号: ${signal}`);
          console.error('Python输出:', pythonOutput);
          
          dialog.showErrorBox('后端启动失败', 
            'Python后端服务异常退出。\n\n' +
            `退出码: ${code}\n` +
            `信号: ${signal || 'none'}\n\n` +
            '详细输出：\n' +
            pythonOutput
          );
          
          reject(new Error(`Python进程异常退出，退出码: ${code}`));
        }
      });
      
      // 等待端口文件出现并读取端口号
      const portFile = path.join(pythonInfo.backendDir, '.port');
      let retries = 30;  // 最多等待30秒
      
      const checkPort = () => {
        if (fs.existsSync(portFile)) {
          try {
            pythonPort = parseInt(fs.readFileSync(portFile, 'utf8').trim());
            console.log(`Python后端使用端口: ${pythonPort}`);
            
            // 测试端口连接
            fetch(`http://127.0.0.1:${pythonPort}/health`)
              .then(response => {
                if (response.ok) {
                  console.log('后端服务启动成功');
                  resolve();
                } else {
                  throw new Error(`健康检查失败: ${response.status}`);
                }
              })
              .catch(error => {
                if (retries > 0) {
                  retries--;
                  setTimeout(checkPort, 1000);
                } else {
                  console.error('后端服务启动超时');
                  dialog.showErrorBox('后端启动失败', 
                    '后端服务启动超时。\n\n' +
                    '详细输出：\n' +
                    pythonOutput
                  );
                  reject(new Error('后端服务启动超时'));
                }
              });
          } catch (error) {
            console.error(`读取端口文件失败: ${error}`);
            if (retries > 0) {
              retries--;
              setTimeout(checkPort, 1000);
            } else {
              reject(new Error('读取端口文件失败'));
            }
          }
        } else {
          if (retries > 0) {
            retries--;
            setTimeout(checkPort, 1000);
          } else {
            reject(new Error('等待端口文件超时'));
          }
        }
      };
      
      // 开始检查端口
      setTimeout(checkPort, 1000);
    });
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

// 获取API基础URL的IPC处理器
ipcMain.handle('get-api-base-url', () => {
  return `http://127.0.0.1:${pythonPort}`;
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