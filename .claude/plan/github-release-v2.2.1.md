# GitHub Release v2.2.1 - 执行计划

## 📋 任务概述
推送SESAME EoS GUI v2.2.1到GitHub，包含压力分析可视化重大优化和双语文档更新

## 🎯 执行目标
1. 将CHANGELOG移至根目录并添加v2.2.1详细内容
2. 同步更新英文和中文README的版本信息
3. 提交所有更改并推送到GitHub main分支
4. 创建v2.2.1 release标签

## ✨ v2.2.1 主要更新内容

### 🎨 压力分析可视化重大优化
- **三层渲染策略**: 背景填充 → 正值覆盖 → 等值线
- **负压区域优化**: 灰色背景填充所有P ≤ 0区域
- **对数正压显示**: nipy_spectral色彩映射 + 对数标尺
- **专业科学显示**: 10^x指数格式colorbar，12个刻度标记
- **P=0等值线标注**: 黑色虚线标识零压强边界

### 🔄 EoS类型智能排序
- 优先级调整: ioncc > ele > ion > total > cc
- GUI界面自动选择优先级最高的可用类型

## 📁 修改文件清单
- `CHANGELOG.md` (从docs/移动到根目录，添加v2.2.1内容)
- `README.md` (更新v2.2.1功能描述)
- `README_CN.md` (更新v2.2.1中文功能描述)
- `sesame_analyzer.py` (EoS排序 + 压力分析优化)
- `main.py` (GUI默认类型选择逻辑)

## 🚀 GitHub发布策略
- 分支: main
- 标签: v2.2.1
- 提交消息: "🎨 v2.2.1: Major pressure analysis visualization enhancement"
- 发布类型: 新版本发布

## 📊 预期结果
- GitHub上显示最新v2.2.1版本
- 双语文档完整同步
- 所有功能更新清晰记录
- 专业的开源项目发布体验

---
执行时间: 2025-01-21
状态: ✅ 已完成文档更新，准备Git操作