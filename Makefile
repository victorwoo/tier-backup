.PHONY: help install test lint format clean backup run

# 默认目标
help:
	@echo "Tier Backup - 智能分层备份解决方案"
	@echo ""
	@echo "可用命令:"
	@echo "  install    - 安装开发依赖"
	@echo "  test       - 运行测试"
	@echo "  lint       - 代码检查"
	@echo "  format     - 代码格式化"
	@echo "  clean      - 清理临时文件"
	@echo "  backup     - 运行备份（使用默认配置）"
	@echo "  run        - 运行备份（交互式选择配置）"
	@echo "  build      - 构建包"
	@echo "  dist       - 创建发布包"

# 安装开发依赖
install:
	pip install -e ".[dev]"

# 运行测试
test:
	pytest src/tests/ -v

# 代码检查
lint:
	flake8 src/
	mypy src/

# 代码格式化
format:
	black src/
	isort src/

# 清理临时文件
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/

# 运行备份（使用默认配置）
backup:
	python tier_backup.py

# 运行备份（交互式选择配置）
run:
	@echo "可用的配置文件:"
	@ls -1 config/*.json | sed 's/^/  /'
	@echo ""
	@read -p "请输入配置文件路径 (默认: config/back_config.json): " config_file; \
	if [ -z "$$config_file" ]; then \
		config_file="config/back_config.json"; \
	fi; \
	if [ -f "$$config_file" ]; then \
		python tier_backup.py "$$config_file"; \
	else \
		echo "错误: 配置文件 $$config_file 不存在"; \
		exit 1; \
	fi

# 构建包
build:
	python -m build

# 创建发布包
dist: clean build
	@echo "发布包已创建在 dist/ 目录中" 