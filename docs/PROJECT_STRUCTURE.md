# 项目结构说明

## 目录结构

```
tier-backup/
├── src/                    # 源代码目录
│   ├── core/              # 核心功能模块
│   │   ├── __init__.py
│   │   └── tier_backup.py # 主备份逻辑
│   ├── utils/             # 工具函数模块
│   │   └── __init__.py
│   ├── tests/             # 测试模块
│   │   ├── __init__.py
│   │   ├── test_backup_logic.py
│   │   ├── test_compression.py
│   │   └── test_symlink.py
│   └── __init__.py
├── config/                # 配置文件目录
│   ├── back_config.json   # 主配置文件
│   ├── test_config.json   # 测试配置
│   └── config_examples.json # 配置示例
├── scripts/               # 脚本文件目录
│   ├── run_backup.bat     # Windows启动脚本
│   └── run_backup.sh      # Linux/macOS启动脚本
├── docs/                  # 文档目录
│   ├── QUICK_START.md     # 快速开始指南
│   ├── COMPRESSION_GUIDE.md # 压缩功能说明
│   ├── SYMLINK_GUIDE.md   # 软链接功能说明
│   └── PROJECT_STRUCTURE.md # 项目结构说明
├── examples/              # 示例文件目录
│   └── prepare_test_env.py # 测试环境准备脚本
├── README.md              # 主说明文档（项目根目录）
├── CHANGELOG.md           # 更新日志（项目根目录）
├── tier_backup.py         # 主入口文件
├── pyproject.toml         # Python项目配置
├── Makefile              # 构建和开发工具
├── .gitignore            # Git忽略文件
└── LICENSE               # 许可证文件
```

## 模块说明

### 核心模块 (src/core/)

- **tier_backup.py**: 主要的备份逻辑实现
  - 备份策略判断
  - 文件复制和压缩
  - 软链接创建
  - 自动清理功能
  - 磁盘空间管理

### 工具模块 (src/utils/)

- 预留用于存放通用工具函数
- 如文件操作、日志记录、配置管理等

### 测试模块 (src/tests/)

- **test_backup_logic.py**: 备份逻辑测试
- **test_compression.py**: 压缩功能测试
- **test_symlink.py**: 软链接功能测试

### 配置文件 (config/)

- **back_config.json**: 主配置文件
- **test_config.json**: 测试专用配置
- **config_examples.json**: 配置示例和说明

### 脚本文件 (scripts/)

- **run_backup.bat**: Windows系统启动脚本
- **run_backup.sh**: Linux/macOS系统启动脚本

### 文档

- **README.md**: 项目主要说明文档（项目根目录）
- **CHANGELOG.md**: 版本更新日志（项目根目录）
- **docs/QUICK_START.md**: 快速开始指南
- **docs/COMPRESSION_GUIDE.md**: 压缩功能详细说明
- **docs/SYMLINK_GUIDE.md**: 软链接功能详细说明
- **docs/PROJECT_STRUCTURE.md**: 项目结构说明（本文档）

## 开发工作流

### 1. 安装开发环境

```bash
make install
```

### 2. 运行测试

```bash
make test
```

### 3. 代码检查

```bash
make lint
```

### 4. 代码格式化

```bash
make format
```

### 5. 运行备份

```bash
# 使用默认配置
make backup

# 交互式选择配置
make run
```

### 6. 构建发布包

```bash
make dist
```

## 配置管理

配置文件统一放在 `config/` 目录下：

- 主配置文件：`config/back_config.json`
- 测试配置：`config/test_config.json`
- 配置示例：`config/config_examples.json`

## 日志文件

备份过程中生成的日志文件位置：

- 主日志：`backup.log`（项目根目录）
- 测试日志：测试过程中可能生成的临时日志文件

## 备份文件结构

备份文件按照以下结构组织：

```
backup/
├── hourly/           # 每小时备份
├── daily/            # 每日备份
└── weekly/           # 每周备份
```

每个备份目录下包含：
- 实际备份文件（目录或压缩包）
- 软链接备份（如果启用）
- 元数据文件（backup_info.json）

## 扩展性

项目结构设计考虑了未来的扩展性：

1. **模块化设计**: 核心功能、工具函数、测试分离
2. **配置管理**: 统一的配置文件管理
3. **跨平台支持**: Windows和Unix系统的脚本支持
4. **开发工具**: 完整的开发工具链支持
5. **文档完善**: 详细的文档说明 