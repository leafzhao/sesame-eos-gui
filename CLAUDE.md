# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

SESAME EoS GUI 是一个独立的桌面应用程序，用于分析SESAME状态方程数据文件。基于Python Tkinter GUI框架，集成opacplot2和hedp科学计算库。

## 核心架构

### 主要组件
- **main.py**: 主GUI应用程序，包含完整的多标签页界面和事件处理逻辑
- **sesame_analyzer.py**: SESAME数据分析核心模块，基于opacplot2实现数据加载、分析和可视化
- **opac_converter.py**: 文件格式转换模块，支持SESAME到CN4/IONMIX格式转换
- **launch.py**: 智能启动器，处理依赖检查和自动安装
- **setup.py**: 自动化依赖安装脚本，处理复杂的opacplot2和hedp安装需求

### GUI架构模式
采用tkinter Notebook（标签页）架构，包含五个主要功能模块：
1. **Material Report**: 材料属性分析报告
2. **D-T Grid Visualization**: 密度-温度网格可视化（20x8英寸大尺寸图表）
3. **Pressure Analysis**: 压强分布分析（双层渲染：灰色负值区域+对数色标正值区域）
4. **Internal Energy Analysis**: 内能分布分析
5. **SES to CN4 Conversion**: 格式转换功能

### 依赖管理架构
三层依赖管理策略：
1. **核心依赖**: numpy, scipy, matplotlib, tkinter（基础科学计算和GUI）
2. **关键依赖**: opacplot2（从GitHub安装，SESAME文件处理核心）
3. **扩展依赖**: hedp（从GitHub安装，格式转换功能，需要cython<3.0约束）

## 常用开发命令

### 应用启动
```bash
# 推荐方式（自动处理依赖）
python launch.py

# 直接启动（需要依赖已安装）
python main.py
```

### 依赖管理
```bash
# 自动安装/修复所有依赖
python setup.py

# 手动安装基础依赖
pip install -r requirements.txt

# 手动安装关键依赖（GitHub源）
pip install git+https://github.com/flash-center/opacplot2.git
pip install "cython<3.0"
pip install git+https://github.com/luli/hedp.git
```

### 测试验证
```bash
# 完整安装测试（验证所有组件）
python test_installation.py

# 快速功能测试（使用示例文件）
# 测试文件位于 examples/ 目录：3719.ses, 3720.ses, 7592.ses
```

## 关键实现细节

### 压强分析优化（v2.2.1）
压强可视化采用三步优化策略：
1. **灰色背景填充**: 消除掩码边界白线问题
2. **正值区域覆盖**: 使用80级对数等高线，nipy_spectral色彩映射
3. **P=0等值线**: 黑色虚线标示零压力边界

关键代码模式：
```python
# 背景填充
ax.contourf(D, T, np.ones_like(P_GPa), colors=['lightgray'])

# 正值覆盖
cs = ax.contourf(D, T, P_positive, levels=levels,
                norm=LogNorm(), cmap='nipy_spectral', 
                extend='max', antialiased=False)

# P=0等值线
ax.contour(D, T, P_GPa, levels=[0.0], colors=['k'], 
          linewidths=1.5, linestyles='--')
```

### 数据处理约束
- **压强单位**: 直接使用GPa（v2.2.1移除了dyne/cm²转换）
- **温度单位**: eV
- **密度单位**: g/cm³（质量密度）和atoms/cm³（离子密度）
- **Cython版本**: 必须<3.0以保证hedp兼容性

### matplotlib集成要点
- 使用FigureCanvasTkAgg嵌入tkinter
- 所有matplotlib操作必须在主线程执行
- 使用plt.close('all')确保内存清理
- 大图表需要GridSpec精确布局控制

## 错误处理原则

### 优雅降级
- 缺少opacplot2时提供手动安装引导
- 缺少hedp时转换功能限制但GUI仍可用
- 依赖安装失败时显示详细错误信息和解决建议

### 用户友好错误信息
GUI错误消息框显示：
- 具体错误原因
- 建议解决方案
- 相关命令行操作

## 项目文件结构关键点

- **examples/**: 包含测试用SESAME文件，用于功能验证
- **docs/**: 详细文档，包含CHANGELOG.md版本历史
- **requirements.txt**: 基础Python包依赖（不包括GitHub依赖）
- **setup.py**: 完整依赖安装脚本，处理所有复杂安装逻辑

## 开发注意事项

- 遵循KISS、DRY、SOLID原则
- matplotlib图表操作需要异常处理
- GUI操作使用threading避免界面冻结，但matplotlib调用必须在主线程
- 所有依赖变更需同步更新setup.py中的安装逻辑
- 新功能需要在test_installation.py中添加相应测试