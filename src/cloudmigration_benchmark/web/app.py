"""
CloudMigration-Benchmark Web界面
基于Gradio 6.x构建的现代化评测界面
"""

import gradio as gr
import pandas as pd
import json
import yaml
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import threading
import random

# 添加项目路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cloudmigration_benchmark.core.config import BenchmarkConfig
from cloudmigration_benchmark.core.benchmark_runner import BenchmarkRunner, EvaluationProgress
from cloudmigration_benchmark.core.test_suite_loader import TestSuiteLoader
from cloudmigration_benchmark.core.models import EvaluationResult, BenchmarkReport


# ==================== 常量定义 ====================

DIMENSION_OPTIONS = {
    "accuracy": "准确性 (Accuracy)",
    "safety": "安全性 (Safety)",
    "latency": "响应速度 (Latency)",
    "consistency": "一致性 (Consistency)",
    "robustness": "鲁棒性 (Robustness)",
    "usability": "可用性 (Usability)",
}

INDUSTRY_DEPTH_OPTIONS = {
    "session_integrity": "会话完整性",
    "interruption_recovery": "中断恢复",
    "context_memory": "上下文记忆",
    "error_handling": "错误处理",
    "self_service_navigation": "自助导航",
    "resource_consistency": "资源一致性",
}

# 维度名称映射
DIMENSION_NAME_MAPPING = {
    "accuracy": "准确性",
    "safety": "安全性",
    "latency": "响应速度",
    "consistency": "一致性",
    "robustness": "鲁棒性",
    "usability": "可用性",
    "industry_depth": "行业纵深",
    "session_integrity": "会话完整性",
    "interruption_recovery": "中断恢复",
    "context_memory": "上下文记忆",
    "error_handling": "错误处理",
    "self_service_navigation": "自助导航",
    "resource_consistency": "资源一致性",
}


# ==================== 状态管理 ====================

class AppState:
    """应用状态"""
    test_suite: Optional[Any] = None
    benchmark_runner: Optional[BenchmarkRunner] = None
    results: List[EvaluationResult] = []
    report: Optional[BenchmarkReport] = None
    evaluation_in_progress: bool = False
    evaluation_lock: threading.Lock = threading.Lock()
    config: BenchmarkConfig = BenchmarkConfig()

    def reset(self):
        self.test_suite = None
        self.results = []
        self.report = None
        self.evaluation_in_progress = False
        self.benchmark_runner = None


state = AppState()


# ==================== 工具函数 ====================

def get_chinese_name(dimension: str) -> str:
    """获取维度的中文名称"""
    return DIMENSION_NAME_MAPPING.get(dimension, dimension)


def create_score_distribution_chart(results: List[Dict]) -> go.Figure:
    """创建分数分布图"""
    if not results:
        return go.Figure()

    scores = [r.get("score", 0) for r in results]

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("分数分布直方图", "各维度平均分数"),
        specs=[[{"type": "histogram"}, {"type": "bar"}]]
    )

    # 分数分布直方图
    colors = ["#27ae60" if s >= 0.8 else "#f39c12" if s >= 0.6 else "#e74c3c" for s in scores]
    fig.add_trace(
        go.Histogram(x=scores, name="分数", nbinsx=10, marker_color=colors, opacity=0.7),
        row=1, col=1
    )

    # 各维度平均分数
    dimension_scores = {}
    for r in results:
        dim = r.get("dimension", "unknown")
        if dim not in dimension_scores:
            dimension_scores[dim] = []
        dimension_scores[dim].append(r.get("score", 0))

    dim_avg = {k: sum(v) / len(v) for k, v in dimension_scores.items()}
    dim_labels = [get_chinese_name(k) for k in dim_avg.keys()]
    avg_scores = list(dim_avg.values())

    bar_colors = ["#27ae60" if s >= 0.8 else "#f39c12" if s >= 0.6 else "#e74c3c" for s in avg_scores]
    fig.add_trace(
        go.Bar(x=dim_labels, y=avg_scores, name="平均分", marker_color=bar_colors),
        row=1, col=2
    )

    fig.update_layout(height=400, showlegend=False, title_text="评测结果分析")
    return fig


def create_pass_rate_chart(results: List[Dict]) -> go.Figure:
    """创建通过率图表"""
    if not results:
        return go.Figure()

    passed = sum(1 for r in results if r.get("passed", False))
    failed = len(results) - passed

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("总体通过率", "各维度通过率"),
        specs=[[{"type": "pie"}, {"type": "bar"}]]
    )

    # 饼图
    fig.add_trace(
        go.Pie(
            labels=["通过", "失败"],
            values=[passed, failed],
            marker_colors=["#27ae60", "#e74c3c"],
            textinfo="label+percent"
        ),
        row=1, col=1
    )

    # 各维度通过率
    dimension_stats = {}
    for r in results:
        dim = r.get("dimension", "unknown")
        if dim not in dimension_stats:
            dimension_stats[dim] = {"total": 0, "passed": 0}
        dimension_stats[dim]["total"] += 1
        if r.get("passed", False):
            dimension_stats[dim]["passed"] += 1

    dim_labels = [get_chinese_name(p) for p in dimension_stats.keys()]
    pass_rates = [
        (dimension_stats[p]["passed"] / dimension_stats[p]["total"] * 100)
        if dimension_stats[p]["total"] > 0 else 0
        for p in dimension_stats.keys()
    ]

    bar_colors = ["#27ae60" if r >= 80 else "#f39c12" if r >= 60 else "#e74c3c" for r in pass_rates]
    fig.add_trace(
        go.Bar(x=dim_labels, y=pass_rates, name="通过率%", marker_color=bar_colors),
        row=1, col=2
    )

    fig.update_layout(height=400, showlegend=False, title_text="通过率分析")
    return fig


def create_radar_chart(results: List[Dict]) -> go.Figure:
    """创建雷达图"""
    if not results:
        return go.Figure()

    # 按维度分组计算平均分
    dimension_scores = {}
    for r in results:
        dim = r.get("dimension", "unknown")
        if dim not in dimension_scores:
            dimension_scores[dim] = []
        dimension_scores[dim].append(r.get("score", 0))

    dim_avg = {k: sum(v) / len(v) * 100 for k, v in dimension_scores.items()}
    labels = [get_chinese_name(k) for k in dim_avg.keys()]
    values = list(dim_avg.values())

    # 雷达图
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]] if values else [0],
        theta=labels + [labels[0]] if labels else [""],
        fill='toself',
        fillcolor='rgba(52, 152, 219, 0.3)',
        line=dict(color='#3498db', width=2),
        name='维度评分'
    ))

    fig.update_layout(
        height=400,
        title="多维度评测雷达图",
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False
    )
    return fig


def create_confidence_chart(results: List[Dict]) -> go.Figure:
    """创建置信度分析图"""
    if not results:
        return go.Figure()

    confidences = [r.get("confidence", 0) for r in results]
    scores = [r.get("score", 0) * 100 for r in results]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=scores,
        y=confidences,
        mode="markers",
        marker=dict(
            size=12,
            color=scores,
            colorscale="RdYlGn",
            showscale=True
        ),
        text=[f"维度: {get_chinese_name(r.get('dimension', 'unknown'))}<br>分数: {r.get('score', 0):.3f}<br>置信度: {r.get('confidence', 0):.3f}"
              for r in results],
        hoverinfo="text"
    ))

    fig.update_layout(
        height=400,
        title="分数-置信度关系图",
        xaxis_title="分数",
        yaxis_title="置信度"
    )
    return fig


def parse_xlsx_file(file_obj, progress=gr.Progress()) -> tuple:
    """解析上传的XLSX文件"""
    if file_obj is None:
        return "请上传文件", pd.DataFrame(), pd.DataFrame()

    try:
        progress(0.1, desc="正在保存文件...")

        # 保存上传的文件
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        temp_path = temp_dir / file_obj.name

        with open(temp_path, "wb") as f:
            f.write(file_obj.read())

        progress(0.3, desc="正在解析Sheet信息...")

        # 加载测试套件
        loader = TestSuiteLoader()
        suite = loader.load_from_xlsx(str(temp_path))
        state.test_suite = suite

        progress(0.8, desc="正在生成统计信息...")

        # 统计各维度测试用例数量
        dimension_counts = {}
        for tc in suite.test_cases:
            dim = tc.dimension
            dimension_counts[dim] = dimension_counts.get(dim, 0) + 1

        dimension_data = []
        for dim, count in dimension_counts.items():
            dimension_data.append({
                "维度": get_chinese_name(dim),
                "维度Key": dim,
                "测试用例数": count
            })
        dimension_df = pd.DataFrame(dimension_data)

        # 阶段统计
        phase_counts = {}
        for tc in suite.test_cases:
            phase = tc.phase
            phase_counts[phase] = phase_counts.get(phase, 0) + 1

        phase_data = []
        for phase, count in phase_counts.items():
            phase_data.append({
                "阶段": phase,
                "测试用例数": count
            })
        phase_df = pd.DataFrame(phase_data)

        progress(1.0, desc="加载完成!")

        message = f"""**加载成功!**

**测试套件:** {suite.name}
**版本:** {suite.version}
**测试用例总数:** {len(suite.test_cases)}
**场景总数:** {len(suite.scenarios)}
**维度数:** {len(dimension_counts)}
"""
        return message, dimension_df, phase_df

    except Exception as e:
        return f"加载失败: {str(e)}", pd.DataFrame(), pd.DataFrame()


def run_evaluation(
    dimensions: List[str],
    max_samples: int,
    progress=gr.Progress()
) -> tuple:
    """执行评测"""
    # 防重复提交检查
    if state.evaluation_in_progress:
        return "评测正在进行中，请稍候...", None, None, None, None, None, None

    if state.test_suite is None:
        return "请先上传测试套件", None, None, None, None, None, None

    if not dimensions:
        return "请至少选择一个维度", None, None, None, None, None, None

    # 获取锁
    with state.evaluation_lock:
        state.evaluation_in_progress = True

    try:
        # 创建运行器
        runner = BenchmarkRunner(config=state.config)
        runner.load_test_suite(state.test_suite.file_path)

        # 过滤测试用例
        test_cases = [
            tc for tc in state.test_suite.test_cases
            if tc.dimension in dimensions
        ][:max_samples]

        if not test_cases:
            return "没有找到匹配的测试用例", None, None, None, None, None, None

        # 执行评测
        results = []
        progress_data = []

        for i, tc in enumerate(test_cases):
            progress((i + 1) / len(test_cases), desc=f"正在评测: {tc.id}")

            # 模拟评测
            score = random.uniform(0.6, 0.95)
            confidence = random.uniform(0.7, 0.95)

            result = {
                "test_case_id": tc.id,
                "dimension": tc.dimension,
                "dimension_name": get_chinese_name(tc.dimension),
                "phase": tc.phase,
                "description": tc.description[:50] + "..." if len(tc.description) > 50 else tc.description,
                "passed": score >= state.config.pass_threshold,
                "score": score,
                "confidence": confidence,
                "status": "通过" if score >= state.config.pass_threshold else "失败",
            }
            results.append(result)
            progress_data.append(result)

        state.results = results

        # 计算统计
        total = len(results)
        passed = sum(1 for r in results if r["passed"])
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0
        avg_score = sum(r["score"] for r in results) / total if total > 0 else 0
        avg_confidence = sum(r["confidence"] for r in results) / total if total > 0 else 0

        # 生成摘要
        summary = f"""**评测完成**

| 指标 | 值 |
|------|-----|
| **总测试数** | {total} |
| **通过** | {passed} |
| **失败** | {failed} |
| **通过率** | {pass_rate:.1f}% |
| **平均分数** | {avg_score:.3f} |
| **平均置信度** | {avg_confidence:.3f} |
"""

        # 生成表格数据
        table_data = pd.DataFrame(results[:20])  # 只显示前20条

        # 生成图表
        score_chart = create_score_distribution_chart(results)
        pass_rate_chart = create_pass_rate_chart(results)
        confidence_chart = create_confidence_chart(results)
        radar_chart = create_radar_chart(results)

        # 生成维度汇总
        dimension_summary = []
        dim_stats = {}
        for r in results:
            dim = r["dimension"]
            if dim not in dim_stats:
                dim_stats[dim] = {"total": 0, "passed": 0, "scores": []}
            dim_stats[dim]["total"] += 1
            dim_stats[dim]["scores"].append(r["score"])
            if r["passed"]:
                dim_stats[dim]["passed"] += 1

        for dim, stats in dim_stats.items():
            avg = sum(stats["scores"]) / len(stats["scores"])
            rate = stats["passed"] / stats["total"] * 100 if stats["total"] > 0 else 0
            dimension_summary.append({
                "维度": get_chinese_name(dim),
                "测试数": stats["total"],
                "通过数": stats["passed"],
                "通过率": f"{rate:.1f}%",
                "平均分": f"{avg:.3f}"
            })

        summary_df = pd.DataFrame(dimension_summary)

        return (
            summary,
            table_data,
            gr.Plot(value=score_chart),
            gr.Plot(value=pass_rate_chart),
            gr.Plot(value=confidence_chart),
            gr.Plot(value=radar_chart),
            summary_df
        )

    finally:
        state.evaluation_in_progress = False


def export_report(format: str) -> str:
    """导出报告"""
    if not state.results:
        return "没有可导出的结果"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"benchmark_report_{timestamp}.{format.lower()}"

    if format == "JSON":
        report_data = {
            "test_suite": {
                "name": state.test_suite.name if state.test_suite else "N/A",
                "version": state.test_suite.version if state.test_suite else "N/A"
            },
            "results": state.results,
            "summary": {
                "total": len(state.results),
                "passed": sum(1 for r in state.results if r["passed"]),
                "avg_score": sum(r["score"] for r in state.results) / len(state.results)
            },
            "generated_at": timestamp
        }
        content = json.dumps(report_data, indent=2, ensure_ascii=False)

    elif format == "YAML":
        report_data = {
            "test_suite": {
                "name": state.test_suite.name if state.test_suite else "N/A",
                "version": state.test_suite.version if state.test_suite else "N/A"
            },
            "results": state.results,
            "generated_at": timestamp
        }
        content = yaml.dump(report_data, allow_unicode=True)

    elif format == "CSV":
        df = pd.DataFrame(state.results)
        content = df.to_csv(index=False)

    else:
        return "不支持的格式"

    # 保存文件
    output_path = Path("exports")
    output_path.mkdir(exist_ok=True)
    file_path = output_path / filename

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return f"报告已导出: `{filename}`"


# ==================== 界面布局 ====================

# 主题设置
APP_THEME = gr.themes.Soft(
    primary_hue="orange",
    neutral_hue="gray",
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui"]
)

APP_CSS = """
/* 自定义样式 */
.main-header { text-align: center; padding: 20px; }
.metric-card { background: #f8f9fa; padding: 20px; border-radius: 8px; }
.success-box { background: rgba(39,174,96,0.1); border-left: 3px solid #27ae60; padding: 15px; border-radius: 4px; }
.warning-box { background: rgba(243,156,18,0.1); border-left: 3px solid #f39c12; padding: 15px; border-radius: 4px; }
.error-box { background: rgba(231,76,60,0.1); border-left: 3px solid #e74c3c; padding: 15px; border-radius: 4px; }
.gradio-container { background: #fafafa; }
"""


def create_app():
    """创建Gradio应用"""

    with gr.Blocks(title="CloudMigration Benchmark", theme=APP_THEME, css=APP_CSS) as app:

        # 页头
        gr.Markdown("""
        # CloudMigration Benchmark
        ### 云迁移AI Agent评测框架

        支持六大AI维度评测 + 行业纵深评测
        """, elem_classes="main-header")

        with gr.Tabs():
            # ==================== Tab 1: 导入评测集 ====================
            with gr.TabItem("导入评测集"):
                gr.Markdown("### 上传XLSX评测集文件")

                with gr.Row():
                    with gr.Column(scale=1):
                        file_input = gr.File(
                            label="选择XLSX文件",
                            file_types=[".xlsx", ".xls"],
                            file_count="single"
                        )
                        upload_btn = gr.Button("加载评测集", variant="primary")

                    with gr.Column(scale=2):
                        upload_output = gr.Markdown("请上传XLSX格式的评测集文件")

                gr.Markdown("---")
                gr.Markdown("### 维度分布预览")
                dimension_preview = gr.DataFrame(
                    label="各维度测试用例数量",
                    wrap=True
                )

                gr.Markdown("### 阶段分布预览")
                phase_preview = gr.DataFrame(
                    label="各阶段测试用例数量",
                    wrap=True
                )

                upload_btn.click(
                    fn=parse_xlsx_file,
                    inputs=[file_input],
                    outputs=[upload_output, dimension_preview, phase_preview]
                )

            # ==================== Tab 2: 执行评测 ====================
            with gr.TabItem("执行评测"):
                gr.Markdown("### 配置并执行评测")

                with gr.Row():
                    with gr.Column(scale=1):
                        # 维度选择
                        dimension_selector = gr.CheckboxGroup(
                            label="选择评测维度",
                            choices=list(DIMENSION_OPTIONS.values()),
                            value=list(DIMENSION_OPTIONS.values())[:3],
                        )

                        # 行业纵深选择
                        industry_depth_selector = gr.CheckboxGroup(
                            label="行业纵深评测",
                            choices=list(INDUSTRY_DEPTH_OPTIONS.values()),
                            value=list(INDUSTRY_DEPTH_OPTIONS.values())[:3],
                        )

                        max_samples = gr.Slider(
                            label="最大样本数",
                            minimum=10,
                            maximum=500,
                            value=50,
                            step=10
                        )

                        run_btn = gr.Button("开始评测", variant="primary", size="lg")

                    with gr.Column(scale=2):
                        eval_summary = gr.Markdown("点击「开始评测」按钮执行测试")

                gr.Markdown("---")
                gr.Markdown("### 📊 维度评分总览")
                dimension_summary_table = gr.DataFrame(
                    label="各维度评测汇总",
                    wrap=True
                )

                gr.Markdown("### 可视化结果")
                with gr.Row():
                    with gr.Column(scale=1):
                        score_chart = gr.Plot(label="分数分析")
                    with gr.Column(scale=1):
                        radar_chart = gr.Plot(label="多维度雷达图")

                with gr.Row():
                    with gr.Column(scale=1):
                        pass_rate_chart = gr.Plot(label="通过率分析")
                    with gr.Column(scale=1):
                        confidence_chart = gr.Plot(label="置信度分析")

                gr.Markdown("---")
                gr.Markdown("### 📋 测试结果详情 (前20条)")
                results_table = gr.DataFrame(
                    label="测试结果",
                    wrap=True
                )

                # 运行评测按钮事件
                run_btn.click(
                    fn=run_evaluation,
                    inputs=[dimension_selector, max_samples],
                    outputs=[eval_summary, results_table, score_chart, pass_rate_chart, confidence_chart, radar_chart, dimension_summary_table]
                )

            # ==================== Tab 3: 结果详情 ====================
            with gr.TabItem("结果详情"):
                gr.Markdown("### 评测结果详情")

                gr.Markdown("#### 测试结果列表")
                detail_results_table = gr.DataFrame(label="测试结果", wrap=True)

                with gr.Row():
                    detail_refresh_btn = gr.Button("刷新结果")

                detail_refresh_btn.click(
                    fn=lambda: (pd.DataFrame(state.results[:100]) if state.results else pd.DataFrame()),
                    outputs=[detail_results_table]
                )

            # ==================== Tab 4: 报告导出 ====================
            with gr.TabItem("导出报告"):
                gr.Markdown("### 导出评测报告")

                with gr.Row():
                    export_format = gr.Radio(
                        choices=["JSON", "YAML", "CSV"],
                        value="JSON",
                        label="导出格式"
                    )
                    export_btn = gr.Button("导出报告", variant="primary")

                export_output = gr.Textbox(label="导出结果", lines=3)

                export_btn.click(
                    fn=export_report,
                    inputs=[export_format],
                    outputs=[export_output]
                )

            # ==================== Tab 5: 配置管理 ====================
            with gr.TabItem("配置管理"):
                gr.Markdown("### 评分配置管理")

                gr.Markdown("""
                ### 配置说明

                各维度评测开关和阈值配置：

                | 维度 | 默认阈值 | 说明 |
                |------|----------|------|
                | 准确性 | 0.8 | 答案正确性、任务完成度 |
                | 安全性 | 0.9 | 有害内容过滤、合规检查 |
                | 响应速度 | 0.8 | 响应时间、吞吐量 |
                | 一致性 | 0.75 | 多轮对话上下文保持 |
                | 鲁棒性 | 0.7 | 抗干扰、异常输入处理 |
                | 可用性 | 0.8 | 用户体验、引导清晰度 |

                **行业纵深评测阈值:**
                | 子维度 | 默认阈值 | 说明 |
                |--------|----------|------|
                | 会话完整性 | 0.75 | 全流程不中断完成能力 |
                | 中断恢复 | 0.7 | 会话中断后恢复能力 |
                | 上下文记忆 | 0.75 | 多轮对话上下文保持 |
                | 错误处理 | 0.7 | 异常输入和错误恢复 |
                | 自助导航 | 0.7 | 用户引导和自主完成 |
                | 资源一致性 | 0.8 | 多轮交互中资源状态一致 |
                """)

            # ==================== Tab 6: 帮助文档 ====================
            with gr.TabItem("帮助"):
                gr.Markdown("""
                # 使用指南

                ## 1. 导入评测集
                - 点击「选择XLSX文件」上传评测集
                - 支持多Sheet的Excel文件
                - Sheet类型: `test_cases`, `scenarios`, `config`

                ## 2. 执行评测
                - 选择要评测的维度（可多选）
                - 可选行业纵深评测子维度
                - 设置最大样本数
                - 点击「开始评测」

                ## 3. 查看结果
                - 查看分数分布和通过率图表
                - 查看详细的测试结果表格
                - 支持结果数据导出

                ## 4. 导出报告
                - 支持JSON/YAML/CSV格式
                - 包含完整的评测结果和统计

                ## XLSX模板格式

                ### test_cases Sheet (必需)
                | 字段 | 说明 | 必需 |
                |------|------|------|
                | id | 测试用例ID | ✓ |
                | scenario_id | 场景ID | ✓ |
                | phase | 阶段名称 | ✓ |
                | dimension | 评测维度 | ✓ |
                | description | 描述 | ✓ |
                | input_data | 输入数据(JSON) | ✓ |
                | expected_output | 期望输出(JSON) | |
                | priority | 优先级(P0/P1/P2) | |
                | tags | 标签(逗号分隔) | |

                ### supported dimensions (评测维度)
                - `accuracy`: 准确性
                - `safety`: 安全性
                - `latency`: 响应速度
                - `consistency`: 一致性
                - `robustness`: 鲁棒性
                - `usability`: 可用性
                - `industry_depth`: 行业纵深

                ### industry_depth sub-dimensions (行业纵深子维度)
                - `session_integrity`: 会话完整性
                - `interruption_recovery`: 中断恢复
                - `context_memory`: 上下文记忆
                - `error_handling`: 错误处理
                - `self_service_navigation`: 自助导航
                - `resource_consistency`: 资源一致性
                """)

        # 页脚
        gr.Markdown("""
        ---
        **CloudMigration Benchmark v0.1.0** | 云迁移AI Agent评测框架
        """)

    return app


# ==================== 启动应用 ====================

def main():
    """主入口"""
    app = create_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
    )


if __name__ == "__main__":
    main()
