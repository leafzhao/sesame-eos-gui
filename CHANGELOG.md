# SESAME EoS GUI - 修改日志 (Changelog)

## v2.2.1 - 2025-08-21

### 🎨 压力分析可视化重大优化 (Major Pressure Analysis Visualization Enhancement)

#### 核心改进 (Core Improvements)
- **🔴 负压区域优化 (Negative Pressure Region Enhancement)**：实现灰色背景填充所有非正压区域 (P ≤ 0)
- **📈 对数正压显示 (Logarithmic Positive Pressure Display)**：使用nipy_spectral色彩映射和对数标尺优化正压值可视化
- **🏷️ P=0等值线标注 (P=0 Contour Lines)**：添加黑色虚线标识零压强边界
- **🛠️ 三层渲染策略 (Three-Layer Rendering Strategy)**：背景填充 → 正值覆盖 → 等值线，完全消除白色边界线问题

#### 专业科学显示 (Professional Scientific Display)  
- **📊 Colorbar格式优化 (Colorbar Format Enhancement)**：使用LogFormatterMathtext实现真正的10^x指数格式显示 (替代1e+08格式)
- **🎯 数值密度提升 (Increased Tick Density)**：colorbar显示12个刻度标记，提供更精确的数值读取
- **💯 GPa单位直接处理 (Direct GPa Unit Handling)**：移除不必要的单位转换，直接使用原始GPa数据

#### EoS类型排序优化 (EoS Type Ordering Enhancement)
- **🔄 智能默认选择 (Smart Default Selection)**：EoS类型优先级调整为 ioncc > ele > ion > total > cc
- **🎛️ 界面同步更新 (UI Synchronization)**：GUI界面自动选择优先级最高的可用EoS类型

### 🧮 算法技术细节 (Algorithm Technical Details)
- **掩码边界问题解决方案 (Mask Boundary Issue Solution)**：采用正值直接覆盖策略，避免masked array边界伪影
- **对数等级计算优化 (Logarithmic Level Calculation)**：动态计算80个对数等级，确保平滑色彩过渡
- **抗锯齿关闭 (Anti-aliasing Disabled)**：`antialiased=False`防止边界模糊，保持清晰对比

### 📋 修改文件清单 (Modified Files)
1. **sesame_analyzer.py**
   - `_analyze_eos_types()`: EoS类型排序 (line 80)
   - `plot_pressure_distribution()`: 完整重写三层渲染策略 (lines 496-541)
   - Colorbar格式化：LogFormatterMathtext + LogLocator (lines 536-541)

2. **main.py**  
   - `update_available_types()`: GUI默认类型选择逻辑 (lines 532-536)
   - 版本号更新至v2.2.1

3. **README.md & README_CN.md**
   - 版本徽章更新至v2.2.1
   - 新功能描述添加

### 🎯 用户体验提升 (User Experience Enhancement)
- **🔍 更直观的压力数据解读 (More Intuitive Pressure Data Interpretation)**：灰色区域清晰标识非物理压力值
- **📊 专业级科学图表 (Professional Scientific Plotting)**：符合学术发表标准的指数格式显示
- **⚡ 智能界面响应 (Smart Interface Response)**：根据数据可用性自动选择最佳EoS类型

---

## v2.1.1 - 2025-08-13

### 🔧 依赖管理改进
- **修复setup.py语法错误**：解决 `import * only allowed at module level` 错误
  - 将 `from opacplot2.convert_opl import *` 改为 `import opacplot2.convert_opl`
  - 修复在函数内使用通配符导入的语法问题
- **新增跳过安装选项**：用户可以选择在缺失依赖时跳过安装
  - GUI模式：三选一对话框（是/否/取消）
  - 命令行模式：选择提示（y/n/q）
  - 有限功能模式：缺失依赖时程序仍可运行（功能受限）

### 🎛️ 用户体验优化  
- **灵活的启动选项**：
  - `Yes/y`: 自动安装缺失依赖
  - `No/n`: 跳过安装，以有限功能模式运行
  - `Cancel/q`: 退出程序
- **改进的错误处理**：
  - 创建虚拟类防止导入错误导致程序崩溃
  - 更清晰的错误消息和用户指导
  - 安装失败时提供替代方案

### 🛠️ 技术改进
- **防护性编程**：添加try-catch包装模块导入
- **虚拟类实现**：为缺失依赖创建占位符类
- **更好的状态管理**：区分完整模式和有限模式

### 📚 文档更新
- **新增安装指南**：`INSTALLATION_GUIDE.md` - 详细的安装和故障排除指南
- **使用场景说明**：不同用户群体的推荐使用方式
- **已知问题解决方案**：hedp兼容性、Cython版本等问题的解决方法

---

## v2.1.0 - 2025-08-13

### 🔧 核心依赖修复
- **修复hedp为核心依赖**：hedp现在被正确识别为核心库，必须安装才能进行SES到CN4的转换功能
- 更新依赖检查逻辑，将hedp从可选依赖改为必需依赖
- 修复启动器中的依赖验证消息

### 🎯 用户界面改进
- **调整标签页顺序**：将"Pressure Analysis"标签移至"Internal Energy Analysis"之前，优化工作流程
- 改进标签页布局，使分析流程更符合物理学习惯

### 🧮 算法优化

#### Internal Energy Analysis
- **重写最小正内能温度算法**：
  - 新算法：遍历所有密度维度，对每个密度找到第一个正内能温度索引
  - 取所有密度中最大的最小索引，确保所有密度下内能都为正值
  - 算法更准确地反映物理意义：找到所有密度下内能均为正的最低温度
- **优化标签显示位置**：
  - 动态计算标签位置，避免与等高线重叠
  - 使用黄色背景和黑色边框，提高可读性
  - 标签位置基于图表范围自动调整

#### Pressure Analysis  
- **新增最小正压强温度标注**：
  - 实现与内能分析相同的算法逻辑
  - 找到所有密度下压强均为正值的最低温度
  - 用青色虚线标注最小正压强温度
  - 添加动态位置的标签说明

### 📊 图形显示优化

#### 布局改进
- **优化所有图形的显示布局**：
  - D-T网格图：调整为15x7尺寸，优化子图间距
  - 内能/压强分布图：12x9尺寸，留足边距防止标签被遮挡
  - 所有图形统一使用`subplots_adjust`精确控制边距
  - 移除不稳定的`tight_layout()`调用

#### 交互增强
- **增强图形交互功能**：
  - 光标悬停显示准确的数据值
  - 内能图显示：密度、温度、内能值 (ρ=1.23e+00 g/cm³, T=4.56e+02 eV, U=1.234 MJ/kg)
  - 压强图显示：密度、温度、压强值 (ρ=1.23e+00 g/cm³, T=4.56e+02 eV, P=1.234 GPa)
  - 自动处理最近邻插值，确保数据值准确性

### 🔨 技术改进
- 统一图形创建的matplotlib配置，确保跨平台一致性
- 改进错误处理，防止交互功能失败时影响主程序
- 优化内存使用，及时清理matplotlib图形对象

### 📋 详细更改列表

#### 文件修改
1. **main.py**
   - 修复依赖检查函数，hedp改为必需依赖
   - 调整标签页创建顺序

2. **launch.py** 
   - 更新依赖检查消息，明确hedp的重要性
   - 改进错误提示信息

3. **sesame_analyzer.py**
   - 重写`plot_internal_energy_distribution()`中的最小正温度算法
   - 重写`plot_pressure_distribution()`添加最小正压强温度功能
   - 为所有图形函数添加增强的光标数据显示
   - 优化所有图形的布局参数
   - 改进标签定位算法

### 🐛 修复的问题
- 修复内能分析中最小正温度计算不准确的问题
- 解决图形标签被窗口边缘遮挡的显示问题  
- 修复matplotlib布局不一致导致的显示异常
- 解决交互模式下光标位置显示不准确的问题

### 🆕 新功能
- 压强分析中的最小正压强温度检测和可视化
- 增强的图形交互：实时显示准确的物理量数值
- 改进的图形布局，更好地适应不同屏幕尺寸

### 📈 性能优化
- 减少不必要的matplotlib重绘操作
- 优化数组索引查找算法，提高交互响应速度
- 改进内存管理，防止图形对象累积

---

## v2.0.0 - 2025-08-12

### 🎉 首次独立发布
- 将GUI程序从opacplot2项目中独立出来
- 实现自动依赖管理和安装
- 创建开箱即用的独立应用程序

### ✨ 核心功能
- SESAME文件加载和分析
- 材料属性报告生成  
- 密度-温度网格可视化
- 内能分布分析
- 压强分布分析
- SES到CN4格式转换

### 🔧 技术架构
- 模块化设计：`sesame_analyzer.py`, `opac_converter.py`
- 智能启动器：`launch.py`
- 自动安装：`setup.py`
- 测试框架：`test_installation.py`

---

## 版本说明

- **主版本号**：重大架构更改或不兼容的API变更
- **次版本号**：新功能添加，保持向后兼容
- **修订号**：bug修复和小幅改进

### 图例
- 🎉 重大更新
- ✨ 新功能
- 🔧 改进
- 🐛 bug修复
- 📊 图形/UI改进
- 🧮 算法优化
- 📈 性能优化
- 📋 文档更新