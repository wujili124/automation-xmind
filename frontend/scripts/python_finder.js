/**
 * Python查找工具
 * 帮助Electron应用找到正确的Python后端
 * 
 * 支持以下三种场景:
 * 1. PyInstaller打包的独立可执行文件
 * 2. 便携式Python虚拟环境
 * 3. 系统安装的Python
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 平台特定变量
const isWindows = process.platform === 'win32';
const isMac = process.platform === 'darwin';
const isLinux = process.platform === 'linux';

/**
 * 在给定路径检查可执行文件是否存在并可执行
 */
function checkExecutable(filePath) {
  try {
    if (!fs.existsSync(filePath)) {
      return false;
    }
    
    // 在Windows上，只要文件存在就可以
    if (isWindows) {
      return true;
    }
    
    // 在Unix系统上，检查是否有执行权限
    const stats = fs.statSync(filePath);
    // 检查文件所有者执行权限位 (100 in binary is 4)
    return !!(stats.mode & 0o100);
  } catch (err) {
    return false;
  }
}

/**
 * 查找Python可执行文件
 * @param {string} appPath 应用根目录路径
 * @param {string} resourcesPath 资源目录路径
 * @returns {{pythonType: string, executablePath: string, backendDir: string}}
 */
function findPythonExecutable(appPath, resourcesPath) {
  const backendDir = path.join(resourcesPath, 'backend');
  let result = {
    pythonType: 'unknown',
    executablePath: '',
    backendDir: backendDir,
    mainScript: path.join(backendDir, 'main.py')
  };
  
  console.log(`查找Python后端，应用目录: ${appPath}, 资源目录: ${resourcesPath}`);
  
  // 1. 首先检查PyInstaller打包的可执行文件
  const pyinstallerDir = path.join(backendDir, 'dist', 'xmind_backend');
  const pyinstallerExe = path.join(
    pyinstallerDir,
    isWindows ? 'xmind_backend.exe' : 'xmind_backend'
  );
  
  if (checkExecutable(pyinstallerExe)) {
    console.log(`找到PyInstaller打包的可执行文件: ${pyinstallerExe}`);
    result.pythonType = 'pyinstaller';
    result.executablePath = pyinstallerExe;
    result.mainScript = ''; // PyInstaller不需要主脚本
    return result;
  }
  
  // 2. 检查便携式Python虚拟环境
  const pythonEnvDir = path.join(backendDir, 'python_env');
  const readyFile = path.join(pythonEnvDir, '.ready');
  
  if (fs.existsSync(readyFile)) {
    const venvPython = path.join(
      pythonEnvDir,
      'venv',
      isWindows ? 'Scripts/python.exe' : 'bin/python'
    );
    
    if (checkExecutable(venvPython)) {
      console.log(`找到便携式Python虚拟环境: ${venvPython}`);
      result.pythonType = 'venv';
      result.executablePath = venvPython;
      return result;
    }
    
    const minicondaPython = path.join(
      pythonEnvDir,
      'miniconda',
      'bin',
      'python'
    );
    
    if (checkExecutable(minicondaPython)) {
      console.log(`找到Miniconda Python: ${minicondaPython}`);
      result.pythonType = 'miniconda';
      result.executablePath = minicondaPython;
      return result;
    }
  }
  
  // 3. 检查系统Python
  try {
    let systemPythonPath = '';
    if (isWindows) {
      systemPythonPath = execSync('where python').toString().trim().split('\n')[0];
    } else {
      systemPythonPath = execSync('which python3').toString().trim();
    }
    
    if (systemPythonPath && checkExecutable(systemPythonPath)) {
      console.log(`找到系统Python: ${systemPythonPath}`);
      result.pythonType = 'system';
      result.executablePath = systemPythonPath;
      return result;
    }
  } catch (err) {
    console.log('未找到系统Python');
  }
  
  // 4. 检查开发环境中的后端
  const devBackendDir = path.join(appPath, '..', 'backend');
  if (fs.existsSync(devBackendDir)) {
    const devVenvPython = path.join(
      devBackendDir, 
      'venv',
      isWindows ? 'Scripts/python.exe' : 'bin/python'
    );
    
    if (checkExecutable(devVenvPython)) {
      console.log(`找到开发环境虚拟环境Python: ${devVenvPython}`);
      result.pythonType = 'dev_venv';
      result.executablePath = devVenvPython;
      result.backendDir = devBackendDir;
      result.mainScript = path.join(devBackendDir, 'main.py');
      return result;
    }
  }
  
  // 未找到Python
  console.log('未找到任何可用的Python后端');
  return result;
}

module.exports = {
  findPythonExecutable
}; 