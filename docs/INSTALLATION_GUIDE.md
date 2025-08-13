# SESAME EoS GUI - 安装指南

## 🚀 快速启动

### 方法1：使用启动器（推荐）
```bash
cd sesame-eos-gui
python launch.py
```

### 方法2：直接运行
```bash
cd sesame-eos-gui
python main.py
```

## 📦 依赖管理选项

程序启动时，如果检测到缺失依赖，你将看到以下选项：

### GUI界面（main.py）
当运行 `python main.py` 时，如果缺失依赖会弹出对话框：

```
Missing required dependencies: opacplot2, hedp

Options:

• Click 'Yes' to install automatically
• Click 'No' to skip installation and try to run anyway  
• Click 'Cancel' to exit

Auto-install will add:
• opacplot2 from GitHub
• hedp from GitHub
• Required scientific libraries

Note: Some features may not work without missing dependencies.
```

**选择说明**：
- **Yes**: 自动安装所有缺失的依赖
- **No**: 跳过安装，以有限功能模式运行
- **Cancel**: 退出程序

### 命令行界面（launch.py）
当运行 `python launch.py` 时，会显示：

```
SESAME EoS GUI Launcher
==============================
✅ opacplot2 found
❌ hedp missing (CRITICAL - needed for format conversion)
✅ Scientific libraries found

⚠️  Missing dependencies detected.

Options:
  y/yes - Install automatically
  n/no  - Skip installation and try to run anyway
  q/quit - Exit

Your choice (y/n/q):
```

**输入选项**：
- **y** 或 **yes**: 运行自动安装
- **n** 或 **no**: 跳过安装继续运行
- **q** 或 **quit**: 退出程序

## 🛠️ 有限功能模式

当你选择跳过安装时，程序会以"有限功能模式"运行：

### ✅ 可用功能
- GUI界面正常显示
- 所有界面元素可以操作
- 基本的程序逻辑

### ❌ 受限功能
- **SESAME文件加载**: 无法加载.ses文件（需要opacplot2）
- **数据分析**: 无法进行任何数据分析（需要opacplot2）
- **图形生成**: 无法生成所有图表（需要opacplot2）
- **格式转换**: 无法进行SES到CN4转换（需要opacplot2和hedp）

### 💡 有限模式的用途
- **界面预览**: 查看程序界面和功能布局
- **教学演示**: 展示程序功能而不需要安装复杂依赖
- **开发测试**: 测试GUI组件而不依赖外部库

## 🔧 手动安装依赖

如果自动安装失败，你可以手动安装：

### 完整安装
```bash
# 1. 安装基础科学库
pip install numpy scipy matplotlib tables numba

# 2. 安装opacplot2
pip install git+https://github.com/flash-center/opacplot2.git

# 3. 安装compatible Cython (重要！)
pip install "cython<3.0"

# 4. 安装hedp
pip install git+https://github.com/luli/hedp.git
```

### 最小安装（仅分析功能）
如果只需要基本的SESAME分析功能：
```bash
pip install numpy scipy matplotlib tables
pip install git+https://github.com/flash-center/opacplot2.git
```

## 🚨 已知问题和解决方案

### hedp兼容性问题
**问题**: `cannot import name 'cumtrapz' from 'scipy.integrate'`

**原因**: hedp与新版本scipy不兼容

**解决方案**:
```bash
# 选项1: 降级scipy
pip install "scipy<1.14.0"

# 选项2: 跳过hedp安装，使用有限功能模式
# 选择"No"跳过安装，程序仍可进行SESAME分析（但无法转换格式）
```

### Cython版本问题
**问题**: hedp编译失败

**解决方案**:
```bash
pip uninstall cython -y
pip install "cython<3.0"
pip install git+https://github.com/luli/hedp.git
```

### 网络连接问题
**问题**: 无法从GitHub下载包

**解决方案**:
```bash
# 使用镜像源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple numpy scipy matplotlib
# 然后手动下载opacplot2和hedp的源码进行安装
```

## 🎯 推荐安装流程

### 新用户
1. 运行 `python launch.py`
2. 如果提示缺失依赖，选择 `y` 自动安装
3. 如果安装成功，程序自动重启
4. 如果安装失败，可选择 `n` 体验有限功能模式

### 开发者/高级用户
1. 运行 `python test_installation.py` 检查环境
2. 根据需要手动安装特定依赖
3. 运行 `python main.py` 直接启动

### 演示/教学
1. 运行程序，选择跳过安装（`n` 或 `No`）
2. 使用有限功能模式展示界面
3. 后续需要时再安装依赖

## 📋 测试安装

```bash
# 全面测试
python test_installation.py

# 快速测试
python -c "
try:
    import opacplot2
    print('✅ opacplot2 available')
except ImportError:
    print('❌ opacplot2 missing')

try:
    import hedp  
    print('✅ hedp available')
except ImportError as e:
    print(f'❌ hedp issue: {e}')
"
```

## 💡 使用建议

- **首次使用**: 尝试自动安装，体验完整功能
- **演示用途**: 使用跳过模式，快速展示界面
- **开发调试**: 根据需要选择性安装依赖
- **生产环境**: 确保所有依赖都正确安装

通过这种灵活的依赖管理方式，用户可以根据自己的需求选择最合适的安装和使用方式！