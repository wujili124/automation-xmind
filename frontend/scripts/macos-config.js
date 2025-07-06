/**
 * macOS平台配置脚本
 * 处理macOS特有的配置和检查，包括签名和公证
 */

const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// 检查当前是否为macOS平台
const isMacOS = process.platform === 'darwin';

/**
 * 检查macOS系统环境
 */
function checkMacOSEnvironment() {
  if (!isMacOS) {
    console.log('不是macOS环境，跳过检查');
    return { supported: false };
  }

  try {
    // 检查macOS版本
    const osVersion = execSync('sw_vers -productVersion').toString().trim();
    console.log(`macOS 版本: ${osVersion}`);

    // 检查Xcode命令行工具
    try {
      execSync('xcode-select -p');
      console.log('已安装Xcode命令行工具');
    } catch (err) {
      console.warn('未安装Xcode命令行工具，某些功能可能不可用');
      console.warn('建议运行: xcode-select --install');
    }

    // 检查是否有Apple开发者证书
    let hasCertificate = false;
    try {
      const certOutput = execSync('security find-identity -v -p codesigning').toString();
      hasCertificate = certOutput.includes('Apple Development') || 
                       certOutput.includes('Developer ID Application') ||
                       certOutput.includes('Apple Distribution');
      
      if (hasCertificate) {
        console.log('找到有效的Apple签名证书');
      } else {
        console.warn('未找到有效的Apple签名证书，应用将无法签名');
      }
    } catch (err) {
      console.warn('检查签名证书时出错:', err.message);
    }

    return {
      supported: true,
      osVersion,
      hasCertificate,
    };
  } catch (err) {
    console.error('检查macOS环境时出错:', err.message);
    return { supported: false, error: err.message };
  }
}

/**
 * 准备macOS打包配置
 * @param {Object} options 打包选项
 * @returns {Object} macOS特定的electron-builder配置
 */
function prepareMacOSBuildConfig(options = {}) {
  // 获取package.json中的现有配置
  const packageJsonPath = path.join(__dirname, '..', 'package.json');
  const packageJson = require(packageJsonPath);
  const existingConfig = packageJson.build || {};
  const existingMacConfig = existingConfig.mac || {};

  // 合并配置
  const macConfig = {
    ...existingMacConfig,
    // 基本配置
    category: 'public.app-category.developer-tools',
    darkModeSupport: true,
    hardenedRuntime: true,
    gatekeeperAssess: false,
    // 额外的配置
    entitlements: path.join(__dirname, 'entitlements.mac.plist'),
    entitlementsInherit: path.join(__dirname, 'entitlements.mac.plist'),
    // 签名配置（如果有证书）
    ...getSigningConfig(),
  };

  // 如果有notarize配置，添加afterSign钩子
  if (options.notarize) {
    macConfig.notarize = options.notarize;
  }

  return macConfig;
}

/**
 * 获取签名配置
 */
function getSigningConfig() {
  // 检查是否有开发者ID证书
  try {
    const certOutput = execSync('security find-identity -v -p codesigning').toString();
    const developerIdMatch = certOutput.match(/\b(Developer ID Application:[^"]+)/);
    
    if (developerIdMatch) {
      const identity = developerIdMatch[1];
      console.log(`使用证书: ${identity}`);
      return {
        identity: identity,
        provisioningProfile: process.env.PROVISIONING_PROFILE,
        // 如果要进行公证，还需要这些设置
        hardenedRuntime: true,
        gatekeeperAssess: false,
      };
    }

    // 如果没有开发者ID证书，尝试任何Apple证书
    const anyAppleCertMatch = certOutput.match(/\b(Apple Development:[^"]+)/);
    if (anyAppleCertMatch) {
      const identity = anyAppleCertMatch[1];
      console.log(`使用开发证书: ${identity}`);
      return {
        identity: identity
      };
    }
  } catch (err) {
    console.warn('获取签名证书时出错:', err.message);
  }

  // 如果没有证书，返回空对象
  console.warn('未找到签名证书，应用将不会被签名');
  return {};
}

/**
 * 创建macOS权限配置文件
 */
function createEntitlementsFile() {
  const entitlementsPath = path.join(__dirname, 'entitlements.mac.plist');
  const entitlements = `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>com.apple.security.cs.allow-jit</key>
    <true/>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.cs.disable-library-validation</key>
    <true/>
    <key>com.apple.security.cs.allow-dyld-environment-variables</key>
    <true/>
    <key>com.apple.security.files.user-selected.read-write</key>
    <true/>
    <key>com.apple.security.network.client</key>
    <true/>
    <key>com.apple.security.network.server</key>
    <true/>
  </dict>
</plist>
`;

  fs.writeFileSync(entitlementsPath, entitlements);
  console.log(`创建了权限文件: ${entitlementsPath}`);
  return entitlementsPath;
}

/**
 * 创建notarize脚本
 */
function createNotarizeScript() {
  const notarizePath = path.join(__dirname, 'notarize.js');
  const notarizeContent = `// macOS公证脚本
const { notarize } = require('@electron/notarize');
const { build } = require('../package.json');

exports.default = async function notarizing(context) {
  const { electronPlatformName, appOutDir } = context;
  
  // 只对macOS进行公证
  if (electronPlatformName !== 'darwin') {
    return;
  }
  
  // 检查环境变量
  if (!process.env.APPLE_ID || !process.env.APPLE_APP_SPECIFIC_PASSWORD) {
    console.warn('缺少Apple ID或应用专用密码环境变量，跳过公证');
    return;
  }
  
  console.log('正在提交应用进行公证...');
  
  const appName = context.packager.appInfo.productFilename;
  
  try {
    // 提交公证请求
    await notarize({
      tool: 'notarytool',
      appBundleId: build.appId,
      appPath: \`\${appOutDir}/\${appName}.app\`,
      appleId: process.env.APPLE_ID,
      appleIdPassword: process.env.APPLE_APP_SPECIFIC_PASSWORD,
      teamId: process.env.APPLE_TEAM_ID
    });
    
    console.log(\`\${appName} 已成功公证 ✅\`);
  } catch (error) {
    console.error(\`公证失败: \${error.message}\`);
    throw error;
  }
};
`;

  fs.writeFileSync(notarizePath, notarizeContent);
  console.log(`创建了公证脚本: ${notarizePath}`);
  return notarizePath;
}

/**
 * 准备macOS平台
 */
function prepareMacOS() {
  if (!isMacOS) {
    console.log('不是macOS环境，跳过配置');
    return false;
  }

  try {
    console.log('准备macOS平台配置...');
    
    // 检查macOS环境
    const envCheck = checkMacOSEnvironment();
    if (!envCheck.supported) {
      console.log('不是受支持的macOS环境，跳过配置');
      return false;
    }
    
    // 创建权限文件
    createEntitlementsFile();
    
    // 如果有签名证书，创建公证脚本
    if (envCheck.hasCertificate) {
      createNotarizeScript();
      
      // 安装notarize依赖
      try {
        console.log('安装公证所需的依赖...');
        execSync('npm install --save-dev @electron/notarize', { stdio: 'inherit' });
      } catch (err) {
        console.warn('安装公证依赖失败:', err.message);
      }
    }
    
    // 获取macOS配置
    const macConfig = prepareMacOSBuildConfig({
      notarize: envCheck.hasCertificate ? './scripts/notarize.js' : undefined
    });
    
    // 显示配置信息
    console.log('macOS配置已准备完成');
    
    return {
      supported: true,
      macConfig,
      entitlementsPath: path.join(__dirname, 'entitlements.mac.plist'),
      notarizePath: envCheck.hasCertificate ? path.join(__dirname, 'notarize.js') : null,
    };
  } catch (err) {
    console.error('准备macOS配置时出错:', err.message);
    return false;
  }
}

/**
 * 为macOS更新package.json配置
 */
function updatePackageJsonForMacOS() {
  try {
    const packageJsonPath = path.join(__dirname, '..', 'package.json');
    const packageJson = require(packageJsonPath);
    const macConfig = prepareMacOSBuildConfig();
    
    // 更新package.json
    if (!packageJson.build) {
      packageJson.build = {};
    }
    
    // 更新mac配置
    packageJson.build.mac = macConfig;
    
    // 检查是否需要更新afterSign钩子
    if (macConfig.notarize && !packageJson.build.afterSign) {
      packageJson.build.afterSign = './scripts/notarize.js';
    }
    
    // 写入更新后的package.json
    fs.writeFileSync(
      packageJsonPath, 
      JSON.stringify(packageJson, null, 2)
    );
    
    console.log('已更新package.json文件，添加了macOS配置');
    return true;
  } catch (err) {
    console.error('更新package.json失败:', err.message);
    return false;
  }
}

// 如果直接运行此脚本
if (require.main === module) {
  console.log('运行macOS配置助手...');
  
  if (!isMacOS) {
    console.log('此脚本应在macOS上运行。检测到当前平台:', process.platform);
    process.exit(1);
  }
  
  const macConfig = prepareMacOS();
  if (macConfig) {
    updatePackageJsonForMacOS();
    console.log('macOS配置完成! ✅');
  } else {
    console.error('macOS配置失败! ❌');
    process.exit(1);
  }
}

module.exports = {
  checkMacOSEnvironment,
  prepareMacOSBuildConfig,
  prepareMacOS,
  updatePackageJsonForMacOS
}; 