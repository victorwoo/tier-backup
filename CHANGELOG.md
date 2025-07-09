# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/lang/zh-CN/).

## [1.0.0] - 2025-07-09

### Added

- **跨平台支持**：添加了对 macOS 和 Linux 系统的支持
- **rsync 集成**：在 macOS/Linux 系统上使用 rsync 替代 robocopy
- **平台检测功能**：自动检测操作系统类型并选择合适的备份方法
- **macOS 启动脚本**：创建了 `run_backup.sh` 用于 macOS/Linux 系统
- **跨平台配置示例**：在 `config_examples.json` 中添加了 macOS 和 Linux 的配置示例
- **系统要求文档**：更新了系统要求，明确各平台的支持情况

### Changed

- **备份方法优化**：根据操作系统自动选择 robocopy（Windows）或 rsync（macOS/Linux）
- **项目结构**：改进项目结构，，符合现代 Python 项目的最佳实践

---

## 版本说明

### 版本号格式

本项目使用 [语义化版本控制](https://semver.org/lang/zh-CN/)：

- **主版本号**：不兼容的 API 修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

### 更新类型

- **Added**：新功能
- **Changed**：对现有功能的变更
- **Deprecated**：已经不建议使用，准备很快移除的功能
- **Removed**：已经移除的功能
- **Fixed**：对 bug 的修复
- **Security**：对安全性的改进

### 贡献指南

如果您想为项目做出贡献，请：

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

### 支持

如果您遇到问题或有建议，请：

- 查看 [故障排除指南](README.md#故障排除)
- 检查 [日志文件](README.md#日志查看)
- 提交 Issue 到项目仓库
