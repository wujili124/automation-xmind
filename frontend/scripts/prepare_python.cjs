/**
 * 此脚本用于在构建前准备Python环境
 * 它会:
 * 1. 创建一个干净的虚拟环境
 * 2. 安装必要的依赖
 * 3. 准备Python环境供Electron使用
 */

const { spawn, execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// 路径配置
const rootDir = path.resolve(__dirname, '../..');
const backendDir = path.join(rootDir, 'backend');
const pythonEnvDir = path.join(backendDir, 'python_env');
const venvDir = path.join(pythonEnvDir, 'venv');
const requirementsPath = path.join(backendDir, 'requirements.txt');

// 检测操作系统
const isWindows = process.platform === 'win32';
const isMac = process.platform === 'darwin';
const pythonCommand = isWindows ? 'python' : 'python3';
const pipCommand = isWindows ? 'pip' : 'pip3';

/**
 * 运行命令并返回Promise
 */
function runCommand(command, args, options = {}) {
  return new Promise((resolve, reject) => {
    console.log(`执行命令: ${command} ${args.join(' ')}`);
    
    const proc = spawn(command, args, {
      ...options,
      stdio: 'inherit'
    });
    
    proc.on('close', (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`Command failed with exit code ${code}`));
      }
    });
    
    proc.on('error', (err) => {
      reject(err);
    });
  });
}

/**
 * 检查Python是否安装
 */
async function checkPythonInstallation() {
  try {
    // 检查Python版本
    const versionCmd = isWindows ? 'python --version' : 'python3 --version';
    const version = execSync(versionCmd).toString().trim();
    console.log(`检测到Python: ${version}`);
    
    // 检查pip版本
    const pipVersionCmd = isWindows ? 'pip --version' : 'pip3 --version';
    const pipVersion = execSync(pipVersionCmd).toString().trim();
    console.log(`检测到pip: ${pipVersion}`);
    
    return true;
  } catch (err) {
    console.error('未检测到Python或pip:', err.message);
    return false;
  }
}

/**
 * 创建Python虚拟环境
 */
async function createVirtualEnv() {
  console.log(`创建Python虚拟环境: ${venvDir}`);
  
  // 如果虚拟环境已存在，先删除
  if (fs.existsSync(venvDir)) {
    console.log('删除已存在的虚拟环境...');
    fs.rmSync(venvDir, { recursive: true, force: true });
  }
  
  // 创建虚拟环境，使用--copies选项创建独立的Python解释器副本
  await runCommand(pythonCommand, ['-m', 'venv', '--copies', venvDir]);
  console.log('虚拟环境创建成功');
  
  // 安装依赖
  console.log('安装Python依赖...');
  
  // 在Windows上使用不同的激活命令
  const activateCmd = isWindows ? 
    `${venvDir}\\Scripts\\activate.bat && ` :
    `source "${venvDir}/bin/activate" && `;
  
  // 获取虚拟环境中的Python和pip路径
  const venvPython = isWindows ? 
    path.join(venvDir, 'Scripts', 'python.exe') :
    path.join(venvDir, 'bin', 'python3');
  
  const venvPip = isWindows ? 
    path.join(venvDir, 'Scripts', 'pip.exe') :
    path.join(venvDir, 'bin', 'pip3');
  
  // 先升级pip
  if (isWindows) {
    await runCommand('cmd', ['/c', `${activateCmd} ${venvPip} install --upgrade pip`]);
  } else {
    await runCommand('bash', ['-c', `${activateCmd} ${venvPip} install --upgrade pip`]);
  }
  
  // 安装wheel（避免某些包安装失败）
  if (isWindows) {
    await runCommand('cmd', ['/c', `${activateCmd} ${venvPip} install wheel`]);
  } else {
    await runCommand('bash', ['-c', `${activateCmd} ${venvPip} install wheel`]);
  }
  
  // 安装依赖
  if (isWindows) {
    await runCommand('cmd', ['/c', `${activateCmd} ${venvPip} install -r "${requirementsPath}"`]);
  } else {
    await runCommand('bash', ['-c', `${activateCmd} ${venvPip} install -r "${requirementsPath}"`]);
  }
  console.log('依赖安装完成');
  
  // 验证安装
  console.log('验证依赖安装...');
  const verifyCmd = isWindows ?
    `${activateCmd} ${venvPython} -c "import fastapi, uvicorn, lxml"` :
    `${activateCmd} ${venvPython} -c 'import fastapi, uvicorn, lxml'`;
  
  try {
    if (isWindows) {
      await runCommand('cmd', ['/c', verifyCmd]);
    } else {
      await runCommand('bash', ['-c', verifyCmd]);
    }
    console.log('依赖验证成功');
  } catch (err) {
    console.error('依赖验证失败:', err);
    throw new Error('Python依赖安装验证失败');
  }
  
  // 创建环境准备标记
  fs.writeFileSync(path.join(pythonEnvDir, '.ready'), 'ready');
  console.log(`创建环境准备标记: ${path.join(pythonEnvDir, '.ready')}`);
}

/**
 * 创建环境准备标记文件
 */
function createReadyFlag() {
  const readyFlagPath = path.join(pythonEnvDir, '.ready');
  fs.writeFileSync(readyFlagPath, new Date().toISOString());
  console.log(`创建环境准备标记: ${readyFlagPath}`);
}

/**
 * 主函数
 */
async function main() {
  console.log('开始准备Python环境...');
  
  try {
    // 检查Python安装
    const isPythonInstalled = await checkPythonInstallation();
    if (!isPythonInstalled) {
      throw new Error('未检测到Python安装，请先安装Python');
    }
    
    // 创建虚拟环境
    await createVirtualEnv();
    
    // 创建准备完成标记
    createReadyFlag();
    
    console.log('Python环境准备完成！✅');
  } catch (err) {
    console.error('Python环境准备失败:', err.message);
    process.exit(1);
  }
}

// 执行主函数
main(); 