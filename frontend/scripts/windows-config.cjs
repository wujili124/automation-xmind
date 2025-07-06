/**
 * Windows平台配置脚本
 * 处理Windows特有的配置和路径问题
 */

const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// 检查当前是否为Windows平台
const isWindows = process.platform === 'win32';

/**
 * 检查Windows系统环境
 */
function checkWindowsEnvironment() {
  if (!isWindows) {
    console.log('不是Windows环境，跳过检查');
    return { supported: false };
  }

  try {
    // 检查Windows版本
    const osInfo = execSync('systeminfo | findstr /B /C:"OS Name" /C:"OS Version"').toString();
    console.log('Windows系统信息:');
    console.log(osInfo);

    // 检查PowerShell版本
    try {
      const psVersion = execSync('powershell -Command "$PSVersionTable.PSVersion"').toString();
      console.log('PowerShell版本:');
      console.log(psVersion);
    } catch (err) {
      console.warn('无法检查PowerShell版本');
    }

    return {
      supported: true,
      osInfo
    };
  } catch (err) {
    console.error('检查Windows环境时出错:', err.message);
    return { supported: false, error: err.message };
  }
}

/**
 * 准备Windows打包配置
 */
function prepareWindowsBuildConfig() {
  // 获取package.json中的现有配置
  const packageJsonPath = path.join(__dirname, '..', 'package.json');
  const packageJson = require(packageJsonPath);
  const existingConfig = packageJson.build || {};
  const existingWinConfig = existingConfig.win || {};

  // 合并配置
  const winConfig = {
    ...existingWinConfig,
    // NSIS安装程序配置
    target: [
      {
        target: "nsis",
        arch: ["x64"]
      }
    ],
    // 图标和其他资源
    icon: path.join(__dirname, '..', 'public', 'favicon.ico'),
    // NSIS配置
    nsis: {
      oneClick: false, // 允许自定义安装选项
      allowToChangeInstallationDirectory: true, // 允许更改安装目录
      installerIcon: path.join(__dirname, '..', 'public', 'favicon.ico'),
      uninstallerIcon: path.join(__dirname, '..', 'public', 'favicon.ico'),
      createDesktopShortcut: true,
      createStartMenuShortcut: true,
      shortcutName: "XMind冒烟测试用例导出工具",
      // 其他NSIS配置
      ...existingWinConfig.nsis
    },
  };

  return winConfig;
}

/**
 * 创建启动脚本
 */
function createStartupScript() {
  const startupScriptPath = path.join(__dirname, '..', 'resources', 'start_app.bat');
  
  // 确保目录存在
  const resourcesDir = path.join(__dirname, '..', 'resources');
  if (!fs.existsSync(resourcesDir)) {
    fs.mkdirSync(resourcesDir, { recursive: true });
  }
  
  const scriptContent = `@echo off
echo 正在启动 XMind冒烟测试用例导出工具...

REM 设置变量
set APP_DIR=%~dp0
cd "%APP_DIR%"

REM 启动应用
start "" "%APP_DIR%\\XMind冒烟测试用例导出工具.exe"

exit
`;

  fs.writeFileSync(startupScriptPath, scriptContent);
  console.log(`创建了启动脚本: ${startupScriptPath}`);
  return startupScriptPath;
}

/**
 * 创建Python环境检查脚本
 */
function createPythonCheckScript() {
  const pythonCheckPath = path.join(__dirname, '..', 'resources', 'check_python.bat');
  
  const scriptContent = `@echo off
echo 检查Python环境...

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
  echo Python未安装或不在PATH中。
  echo 请安装Python并确保其在系统PATH中。
  pause
  exit /b 1
)

echo 找到Python:
python --version

echo 检查pip...
python -m pip --version >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
  echo pip未安装。
  echo 正在尝试安装pip...
  python -m ensurepip
)

echo Python环境检查完成。
exit /b 0
`;

  fs.writeFileSync(pythonCheckPath, scriptContent);
  console.log(`创建了Python检查脚本: ${pythonCheckPath}`);
  return pythonCheckPath;
}

/**
 * 准备Windows平台
 */
function prepareWindows() {
  if (!isWindows) {
    console.log('不是Windows环境，跳过配置');
    return false;
  }

  try {
    console.log('准备Windows平台配置...');
    
    // 检查Windows环境
    const envCheck = checkWindowsEnvironment();
    if (!envCheck.supported) {
      console.log('不是受支持的Windows环境，跳过配置');
      return false;
    }
    
    // 创建启动脚本
    createStartupScript();
    
    // 创建Python检查脚本
    createPythonCheckScript();
    
    // 获取Windows配置
    const winConfig = prepareWindowsBuildConfig();
    
    // 显示配置信息
    console.log('Windows配置已准备完成');
    
    return {
      supported: true,
      winConfig,
    };
  } catch (err) {
    console.error('准备Windows配置时出错:', err.message);
    return false;
  }
}

/**
 * 为Windows更新package.json配置
 */
function updatePackageJsonForWindows() {
  try {
    const packageJsonPath = path.join(__dirname, '..', 'package.json');
    const packageJson = require(packageJsonPath);
    const winConfig = prepareWindowsBuildConfig();
    
    // 更新package.json
    if (!packageJson.build) {
      packageJson.build = {};
    }
    
    // 更新Windows配置
    packageJson.build.win = winConfig;
    
    // 添加额外资源
    if (!packageJson.build.extraResources) {
      packageJson.build.extraResources = [];
    }
    
    // 确保resources目录包含在extraResources中
    let hasResourcesDir = false;
    for (const resource of packageJson.build.extraResources) {
      if (typeof resource === 'object' && resource.from === 'resources') {
        hasResourcesDir = true;
        break;
      }
    }
    
    if (!hasResourcesDir) {
      packageJson.build.extraResources.push({
        from: "resources",
        to: "resources"
      });
    }
    
    // 写入更新后的package.json
    fs.writeFileSync(
      packageJsonPath, 
      JSON.stringify(packageJson, null, 2)
    );
    
    console.log('已更新package.json文件，添加了Windows配置');
    return true;
  } catch (err) {
    console.error('更新package.json失败:', err.message);
    return false;
  }
}

// 如果直接运行此脚本
if (require.main === module) {
  console.log('运行Windows配置助手...');
  
  if (!isWindows) {
    console.log('此脚本应在Windows上运行。检测到当前平台:', process.platform);
    process.exit(1);
  }
  
  const winConfig = prepareWindows();
  if (winConfig) {
    updatePackageJsonForWindows();
    console.log('Windows配置完成! ✅');
  } else {
    console.error('Windows配置失败! ❌');
    process.exit(1);
  }
}

module.exports = {
  checkWindowsEnvironment,
  prepareWindowsBuildConfig,
  prepareWindows,
  updatePackageJsonForWindows
}; 