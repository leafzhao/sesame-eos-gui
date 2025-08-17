# SESAME EoS GUI Analysis Tool

<div align="center">

[![English](https://img.shields.io/badge/Language-English-blue.svg)](README.md)
[![中文](https://img.shields.io/badge/语言-中文-red.svg)](README_CN.md)

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macOS%20%7C%20linux-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Version](https://img.shields.io/badge/version-2.2.0-blue.svg)

**开箱即用的SESAME方程状态数据分析工具**

</div>

## ✨ 主要特性

### 🔧 **开箱即用**
- **自动依赖管理**: 无需手动安装复杂依赖，程序自动处理opacplot2和hedp的安装
- **智能安装**: 自动处理Cython版本兼容性问题
- **跨平台支持**: Windows、macOS、Linux通用

### 📊 **SESAME文件分析**
- 加载和分析SESAME格式文件(.ses)
- 自动检测材料ID和基本属性
- 支持单精度和双精度格式
- 生成全面的材料属性报告

### 📈 **数据可视化**
- **密度-温度网格**: 交互式网格点分布图
- **内能分析**: 等高线图，自动检测正内能温度
- **压强分析**: 压强分布可视化
- 支持不同EoS类型(total、electron、ion等)
- 导出图表为PNG、PDF、SVG格式

### 🔄 **格式转换 (v2.2.0强化功能)**
- **精确转换**: 将SESAME文件转换为CN4/IONMIX格式
- **离子密度网格**: 直接使用opacplot2的原生离子数密度数据
- **100%准确**: 与原始opac-convert命令输出完全一致
- **参数验证**: 智能参数验证和建议
- **实时进度**: 转换过程可视化显示

## 🚀 快速开始

### 方法1：使用启动器（推荐）
```bash
git clone <your-repo-url>
cd sesame-eos-gui
python launch.py
```

启动器会：
1. 自动检查依赖
2. 如需要会自动安装opacplot2和hedp
3. 启动GUI界面

### 方法2：手动安装
```bash
git clone <your-repo-url>
cd sesame-eos-gui

# 安装依赖
python setup.py

# 启动GUI
python main.py
```

## 📋 系统要求

- Python 3.8或更高版本
- 网络连接（首次运行时安装依赖）
- 操作系统：Windows、macOS、Linux

## 📖 使用指南

### 1. **加载SESAME文件**
- 点击"Load SES File"按钮
- 选择.ses格式的SESAME文件
- 程序自动分析并显示基本信息

### 2. **查看材料报告**
- 切换到"Material Report"标签
- 点击"Generate Report"查看详细分析
- 可保存报告为文本文件

### 3. **可视化密度-温度网格**
- 切换到"D-T Grid Visualization"标签
- 选择EoS类型（total、electron、ion等）
- 点击"Generate Plot"创建可视化图表
- 支持多种格式导出

### 4. **分析内能分布**
- 切换到"Internal Energy Analysis"标签
- 选择EoS类型
- 点击"Analyze & Plot"执行分析
- 查看最小正内能温度

### 5. **转换文件格式**
- 切换到"SES to CN4 Conversion"标签
- 配置转换参数（原子序数、分数等）
- 点击"Load Suggested Parameters"获取自动建议
- 点击"Convert to CN4"执行转换

## 🔧 依赖管理

程序自动管理以下依赖：

### 核心依赖
- `opacplot2`: SESAME数据处理库
- `hedp`: 高能密度物理包
- `numpy`, `scipy`, `matplotlib`: 科学计算库

### 重要说明
- 程序会自动安装 `cython<3.0` 以确保hedp兼容性
- 首次运行可能需要几分钟来安装依赖
- 安装过程会显示进度信息

## 🗂️ 项目结构

```
sesame-eos-gui/
├── main.py              # 主GUI应用程序
├── launch.py            # 启动器脚本
├── setup.py             # 依赖安装脚本
├── requirements.txt     # Python包依赖
├── sesame_analyzer.py   # SESAME数据分析模块
├── opac_converter.py    # 格式转换模块
└── README.md           # 使用说明
```

## ⚠️ 故障排除

### 常见问题

1. **依赖安装失败**
   ```bash
   # 手动安装
   python setup.py
   ```

2. **Cython版本问题**
   ```bash
   pip uninstall cython -y
   pip install "cython<3.0"
   ```

3. **opacplot2安装失败**
   ```bash
   pip install git+https://github.com/flash-center/opacplot2.git
   ```

4. **hedp安装失败**
   ```bash
   pip install "cython<3.0"
   pip install git+https://github.com/luli/hedp.git
   ```

### 获取帮助

如遇到问题，请检查：
1. Python版本是否>=3.8
2. 网络连接是否正常
3. 是否有足够的磁盘空间
4. 终端/命令提示符的权限

## 📝 更新日志

### v2.2.0 (2024-08)
- **🎯 核心修复**: 格式转换功能重大改进
- **✅ 精确转换**: 直接使用`eos_dict['idens']`作为离子数密度网格
- **🔧 代码优化**: 移除手动密度转换逻辑，减少81行代码(-20%)
- **📊 100%准确**: 与opac-convert命令输出完全一致（二进制级别匹配）
- **🎨 遵循原则**: 严格按照KISS、DRY、SRP软件工程原则重构
- **📋 完整验证**: 添加benchmark测试工具确保转换正确性

### v2.1.1
- 改进转换功能的错误处理
- 优化用户界面响应

### v2.0
- 重写为独立应用，无需安装在opacplot2目录中
- 自动依赖管理
- 改进的用户界面
- 更好的错误处理

### v1.0
- 初始版本
- 基本的SESAME文件分析功能

## 🤝 贡献

欢迎提交问题报告和功能建议！

## 📄 许可证

MIT License - 详见LICENSE文件

---

**开始使用：运行 `python launch.py` 即可！**