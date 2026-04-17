# CLAUDE.md - CloudMigration-Benchmark-Project

## 项目概述
云迁移AI Agent评测框架 - 专注于评估AI在云迁移场景中的运维能力。

## 技术栈
- **UI**: Gradio 6.x
- **数据处理**: pandas, openpyxl
- **可视化**: Plotly
- **配置**: PyYAML
- **测试**: pytest

## 项目结构
```
CloudMigration-Benchmark-Project/
├── src/cloudmigration_benchmark/
│   ├── core/           # 核心模块
│   ├── evaluation/     # 评测维度
│   ├── web/            # Web界面
│   └── api/            # API接口
├── data/               # 测试数据
├── tests/              # 单元测试
└── docs/               # 文档
```

## 关键文件
- `src/cloudmigration_benchmark/core/scoring_engine.py` - 评分引擎
- `src/cloudmigration_benchmark/core/test_suite_loader.py` - XLSX加载器
- `src/cloudmigration_benchmark/evaluation/dimensions.py` - 六大AI维度
- `src/cloudmigration_benchmark/evaluation/industry_depth.py` - 行业纵深评测
- `src/cloudmigration_benchmark/web/app.py` - Gradio界面

## 六大AI评测维度
1. 准确性 (Accuracy)
2. 安全性 (Safety)
3. 响应速度 (Latency)
4. 一致性 (Consistency)
5. 鲁棒性 (Robustness)
6. 可用性 (Usability)

## 行业纵深评测
- 会话完整性
- 中断恢复
- 上下文记忆
- 错误处理
- 自助导航
- 资源一致性

## 运行方式
```bash
# 安装依赖
pip install -e .

# 启动Web界面
cmb

# 运行测试
pytest tests/
```

## Gradio 6.x 注意事项
- 使用 `file_count="single"` 而非 `file_count=1`
- 进度使用 `gr.Progress()` 而非类型注解
- 组件需在事件处理器之前定义
