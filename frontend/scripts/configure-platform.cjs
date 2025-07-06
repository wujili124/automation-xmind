/**
 * 跨平台配置脚本
 * 根据当前平台选择适当的配置
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 检测当前平台
const platform = process.platform;
console.log(`检测到平台: ${platform}`);

// 初始化配置对象
let platformConfig = {
  supported: false,
  platform
};

// 根据平台加载相应的配置模块
try {
  switch (platform) {
    case 'darwin': // macOS
      console.log('加载macOS配置...');
      const macModule = require('./macos-config.cjs');
      const macConfig = macModule.prepareMacOS();
      if (macConfig) {
        console.log('应用macOS配置...');
        macModule.updatePackageJsonForMacOS();
        platformConfig = { ...platformConfig, ...macConfig, supported: true };
      }
      break;
      
    case 'win32': // Windows
      console.log('加载Windows配置...');
      const winModule = require('./windows-config.cjs');
      const winConfig = winModule.prepareWindows();
      if (winConfig) {
        console.log('应用Windows配置...');
        winModule.updatePackageJsonForWindows();
        platformConfig = { ...platformConfig, ...winConfig, supported: true };
      }
      break;
      
    case 'linux': // Linux
      console.log('Linux平台暂未实现自动配置，请手动配置');
      break;
      
    default:
      console.log('未知平台:', platform);
  }
  
  if (platformConfig.supported) {
    console.log(`${platform}平台配置完成 ✅`);
    
    // 准备公共资源目录
    const resourcesDir = path.join(__dirname, '..', 'resources');
    if (!fs.existsSync(resourcesDir)) {
      fs.mkdirSync(resourcesDir, { recursive: true });
    }
    
    // 更新package.json以包含resources目录
    updatePackageJsonResources();
    
    // 创建平台信息文件
    const platformInfoPath = path.join(resourcesDir, 'platform-info.json');
    fs.writeFileSync(
      platformInfoPath, 
      JSON.stringify({
        platform,
        configuredAt: new Date().toISOString(),
        supported: true
      }, null, 2)
    );
  } else {
    console.log(`${platform}平台配置失败 ❌`);
  }
} catch (err) {
  console.error('平台配置出错:', err.message);
}

/**
 * 更新package.json以包含resources目录
 */
function updatePackageJsonResources() {
  try {
    const packageJsonPath = path.join(__dirname, '..', 'package.json');
    const packageJson = require(packageJsonPath);
    
    // 确保build配置存在
    if (!packageJson.build) {
      packageJson.build = {};
    }
    
    // 确保extraResources配置存在
    if (!packageJson.build.extraResources) {
      packageJson.build.extraResources = [];
    }
    
    // 检查resources目录是否已包含在配置中
    let hasResourcesDir = false;
    for (const resource of packageJson.build.extraResources) {
      if (typeof resource === 'object' && resource.from === 'resources') {
        hasResourcesDir = true;
        break;
      }
    }
    
    // 如果没有包含，添加它
    if (!hasResourcesDir) {
      packageJson.build.extraResources.push({
        from: "resources",
        to: "resources"
      });
      
      // 写入更新后的package.json
      fs.writeFileSync(
        packageJsonPath, 
        JSON.stringify(packageJson, null, 2)
      );
      
      console.log('已更新package.json添加resources目录');
    }
  } catch (err) {
    console.error('更新package.json失败:', err.message);
  }
}

/**
 * 创建跨平台启动脚本
 */
function createCrossPlatformStartupScript() {
  try {
    const resourcesDir = path.join(__dirname, '..', 'resources');
    
    // 为不同平台创建启动脚本
    if (platform === 'win32') {
      // Windows .bat脚本
      const batScript = path.join(resourcesDir, 'start.bat');
      const batContent = `@echo off
echo 启动应用...
start "" "%~dp0\\..\\XMind冒烟测试用例导出工具.exe"
exit
`;
      fs.writeFileSync(batScript, batContent);
      console.log(`创建了Windows启动脚本: ${batScript}`);
    } else if (platform === 'darwin') {
      // macOS .sh脚本
      const shScript = path.join(resourcesDir, 'start.sh');
      const shContent = `#!/bin/bash
echo "启动应用..."
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
open "$DIR/../XMind冒烟测试用例导出工具.app"
`;
      fs.writeFileSync(shScript, shContent);
      fs.chmodSync(shScript, '755'); // 设置可执行权限
      console.log(`创建了macOS启动脚本: ${shScript}`);
    } else if (platform === 'linux') {
      // Linux .sh脚本
      const shScript = path.join(resourcesDir, 'start.sh');
      const shContent = `#!/bin/bash
echo "启动应用..."
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
"$DIR/../xmind-automation-tool" &
`;
      fs.writeFileSync(shScript, shContent);
      fs.chmodSync(shScript, '755'); // 设置可执行权限
      console.log(`创建了Linux启动脚本: ${shScript}`);
    }
  } catch (err) {
    console.error('创建启动脚本失败:', err.message);
  }
}

// 创建跨平台启动脚本
createCrossPlatformStartupScript(); 