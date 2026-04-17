"""
XLSX评测集加载器 - CloudMigration-Benchmark-Project
支持多Sheet、多文件批量导入
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from enum import Enum
import json
import pandas as pd
from openpyxl import load_workbook

from cloudmigration_benchmark.core.models import TestCase, Scenario


logger = logging.getLogger(__name__)


class SheetType(Enum):
    """Sheet类型"""
    TEST_CASES = "test_cases"
    SCENARIOS = "scenarios"
    CONFIG = "config"
    EXPECTED = "expected"
    METRICS = "metrics"
    THRESHOLDS = "thresholds"


@dataclass
class SheetInfo:
    """Sheet信息"""
    name: str
    sheet_type: SheetType
    rows: int
    columns: int
    data: pd.DataFrame


@dataclass
class LoadedTestSuite:
    """已加载的测试套件"""
    name: str
    version: str
    test_cases: List[TestCase] = field(default_factory=list)
    scenarios: List[Scenario] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    sheet_info: List[SheetInfo] = field(default_factory=list)
    file_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_test_cases_by_dimension(self, dimension: str) -> List[TestCase]:
        """按维度获取测试用例"""
        return [tc for tc in self.test_cases if tc.dimension == dimension]

    def get_test_cases_by_phase(self, phase: str) -> List[TestCase]:
        """按阶段获取测试用例"""
        return [tc for tc in self.test_cases if tc.phase == phase]

    def get_test_cases_by_scenario(self, scenario_id: str) -> List[TestCase]:
        """按场景获取测试用例"""
        return [tc for tc in self.test_cases if tc.scenario_id == scenario_id]


class TestSuiteLoader:
    """
    测试套件加载器

    支持:
    - 多Sheet XLSX文件
    - 批量文件导入
    - 文件夹批量导入
    - 增量导入
    """

    SHEET_TYPE_KEYWORDS = {
        SheetType.TEST_CASES: ["test_cases", "testcase", "test_case", "用例"],
        SheetType.SCENARIOS: ["scenarios", "scenario", "场景"],
        SheetType.CONFIG: ["config", "configuration", "配置"],
        SheetType.EXPECTED: ["expected", "expected_output", "期望"],
        SheetType.METRICS: ["metrics", "metric", "指标"],
        SheetType.THRESHOLDS: ["thresholds", "threshold", "阈值"],
    }

    REQUIRED_COLUMNS_TEST_CASES = ["id", "scenario_id", "phase", "dimension", "description", "input_data"]

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def load_from_xlsx(self, file_path: str) -> LoadedTestSuite:
        """
        从XLSX文件加载测试套件

        Args:
            file_path: XLSX文件路径

        Returns:
            LoadedTestSuite对象
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        self.logger.info(f"正在加载测试套件: {file_path}")

        # 加载Excel文件
        try:
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
        except Exception as e:
            raise ValueError(f"无法读取Excel文件: {e}")

        # 解析每个Sheet
        sheets_info = []
        test_cases = []
        scenarios = []
        config = {}

        for sheet_name in sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            sheet_type = self._detect_sheet_type(sheet_name, df)

            sheet_info = SheetInfo(
                name=sheet_name,
                sheet_type=sheet_type,
                rows=len(df),
                columns=len(df.columns),
                data=df,
            )
            sheets_info.append(sheet_info)

            # 根据Sheet类型解析数据
            if sheet_type == SheetType.TEST_CASES:
                test_cases.extend(self._parse_test_cases(df))
            elif sheet_type == SheetType.SCENARIOS:
                scenarios.extend(self._parse_scenarios(df))
            elif sheet_type == SheetType.CONFIG:
                config.update(self._parse_config(df))

        # 获取套件名称和版本
        name = config.get("name", path.stem)
        version = config.get("version", "1.0.0")

        suite = LoadedTestSuite(
            name=name,
            version=version,
            test_cases=test_cases,
            scenarios=scenarios,
            config=config,
            sheet_info=sheets_info,
            file_path=str(path),
        )

        self.logger.info(f"加载完成: {len(test_cases)}个测试用例, {len(scenarios)}个场景")
        return suite

    def load_multiple(self, file_paths: List[str]) -> List[LoadedTestSuite]:
        """
        批量加载多个XLSX文件

        Args:
            file_paths: XLSX文件路径列表

        Returns:
            LoadedTestSuite列表
        """
        suites = []
        for file_path in file_paths:
            try:
                suite = self.load_from_xlsx(file_path)
                suites.append(suite)
            except Exception as e:
                self.logger.error(f"加载文件失败 {file_path}: {e}")
                continue
        return suites

    def load_from_folder(self, folder_path: str, pattern: str = "*.xlsx") -> List[LoadedTestSuite]:
        """
        从文件夹批量加载XLSX文件

        Args:
            folder_path: 文件夹路径
            pattern: 文件匹配模式

        Returns:
            LoadedTestSuite列表
        """
        path = Path(folder_path)
        if not path.exists() or not path.is_dir():
            raise ValueError(f"文件夹不存在: {folder_path}")

        xlsx_files = list(path.glob(pattern))
        self.logger.info(f"找到 {len(xlsx_files)} 个XLSX文件")

        return self.load_multiple([str(f) for f in xlsx_files])

    def get_sheet_info(self, file_path: str) -> List[Dict[str, Any]]:
        """
        获取XLSX文件的Sheet信息预览

        Args:
            file_path: XLSX文件路径

        Returns:
            Sheet信息列表
        """
        excel_file = pd.ExcelFile(file_path)
        sheet_info = []

        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            sheet_type = self._detect_sheet_type(sheet_name, df)

            sheet_info.append({
                "name": sheet_name,
                "type": sheet_type.value,
                "rows": len(df),
                "columns": len(df.columns),
                "columns_list": list(df.columns),
            })

        return sheet_info

    def _detect_sheet_type(self, sheet_name: str, df: pd.DataFrame) -> SheetType:
        """检测Sheet类型"""
        sheet_name_lower = sheet_name.lower()

        # 按名称匹配
        for sheet_type, keywords in self.SHEET_TYPE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in sheet_name_lower:
                    return sheet_type

        # 按列名匹配 (对于test_cases sheet)
        columns_lower = [c.lower() for c in df.columns]
        if any(col in columns_lower for col in ["id", "test_case_id", "case_id"]):
            return SheetType.TEST_CASES

        # 按列名匹配 (对于scenarios sheet)
        if any(col in columns_lower for col in ["scenario_id", "scenario_name"]):
            return SheetType.SCENARIOS

        # 默认返回TEST_CASES
        return SheetType.TEST_CASES

    def _parse_test_cases(self, df: pd.DataFrame) -> List[TestCase]:
        """解析测试用例"""
        test_cases = []

        for _, row in df.iterrows():
            try:
                # 处理ID列
                tc_id = str(row.get("id", row.get("test_case_id", f"TC_{len(test_cases)}")))

                # 处理input_data列 - 可能是JSON字符串或字典
                input_data = row.get("input_data", row.get("input", "{}"))
                if isinstance(input_data, str):
                    try:
                        input_data = json.loads(input_data)
                    except json.JSONDecodeError:
                        input_data = {"raw": input_data}

                # 处理expected_output列
                expected_output = row.get("expected_output", row.get("expected", None))
                if isinstance(expected_output, str) and expected_output:
                    try:
                        expected_output = json.loads(expected_output)
                    except json.JSONDecodeError:
                        expected_output = {"raw": expected_output}

                # 处理tags列
                tags = row.get("tags", "")
                if isinstance(tags, str):
                    tags = [t.strip() for t in tags.split(",") if t.strip()]
                elif not isinstance(tags, list):
                    tags = []

                test_case = TestCase(
                    id=tc_id,
                    scenario_id=str(row.get("scenario_id", "")),
                    dimension=str(row.get("dimension", "accuracy")),
                    phase=str(row.get("phase", "general")),
                    description=str(row.get("description", "")),
                    input_data=input_data,
                    expected_output=expected_output,
                    priority=str(row.get("priority", "P1")),
                    tags=tags,
                    timeout_ms=int(row.get("timeout_ms", 30000)),
                    retry_count=int(row.get("retry_count", 0)),
                    response_format=str(row.get("response_format", "text")),
                    metadata={},
                )
                test_cases.append(test_case)

            except Exception as e:
                self.logger.warning(f"解析测试用例行失败: {e}")
                continue

        return test_cases

    def _parse_scenarios(self, df: pd.DataFrame) -> List[Scenario]:
        """解析场景"""
        scenarios = []

        for _, row in df.iterrows():
            try:
                # 处理test_case_ids列
                tc_ids = row.get("test_case_ids", "")
                if isinstance(tc_ids, str):
                    tc_ids = [t.strip() for t in tc_ids.split(",") if t.strip()]
                elif not isinstance(tc_ids, list):
                    tc_ids = []

                scenario = Scenario(
                    id=str(row.get("id", row.get("scenario_id", f"SC_{len(scenarios)}"))),
                    name=str(row.get("name", row.get("scenario_name", ""))),
                    description=str(row.get("description", "")),
                    test_case_ids=tc_ids,
                    metadata={},
                )
                scenarios.append(scenario)

            except Exception as e:
                self.logger.warning(f"解析场景行失败: {e}")
                continue

        return scenarios

    def _parse_config(self, df: pd.DataFrame) -> Dict[str, Any]:
        """解析配置"""
        config = {}

        for _, row in df.iterrows():
            key = row.get("key", row.get("name", row.get("dimension", "")))
            value = row.get("value", row.get("enabled", row.get("config", "")))

            if key:
                config[str(key)] = value

        return config

    def save_to_xlsx(self, suite: LoadedTestSuite, output_path: str):
        """
        保存测试套件到XLSX文件

        Args:
            suite: LoadedTestSuite对象
            output_path: 输出文件路径
        """
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            # 保存test_cases sheet
            if suite.test_cases:
                tc_data = []
                for tc in suite.test_cases:
                    tc_data.append({
                        "id": tc.id,
                        "scenario_id": tc.scenario_id,
                        "dimension": tc.dimension,
                        "phase": tc.phase,
                        "description": tc.description,
                        "input_data": json.dumps(tc.input_data, ensure_ascii=False),
                        "expected_output": json.dumps(tc.expected_output, ensure_ascii=False) if tc.expected_output else "",
                        "priority": tc.priority,
                        "tags": ",".join(tc.tags),
                        "timeout_ms": tc.timeout_ms,
                        "retry_count": tc.retry_count,
                        "response_format": tc.response_format,
                    })
                tc_df = pd.DataFrame(tc_data)
                tc_df.to_excel(writer, sheet_name="test_cases", index=False)

            # 保存scenarios sheet
            if suite.scenarios:
                sc_data = []
                for sc in suite.scenarios:
                    sc_data.append({
                        "id": sc.id,
                        "name": sc.name,
                        "description": sc.description,
                        "test_case_ids": ",".join(sc.test_case_ids),
                    })
                sc_df = pd.DataFrame(sc_data)
                sc_df.to_excel(writer, sheet_name="scenarios", index=False)

            # 保存config sheet
            if suite.config:
                config_data = [{"key": k, "value": v} for k, v in suite.config.items()]
                config_df = pd.DataFrame(config_data)
                config_df.to_excel(writer, sheet_name="config", index=False)

        self.logger.info(f"测试套件已保存: {output_path}")


# 便捷函数
def load_test_suite(file_path: str) -> LoadedTestSuite:
    """加载测试套件"""
    loader = TestSuiteLoader()
    return loader.load_from_xlsx(file_path)


def load_test_suites_from_folder(folder_path: str) -> List[LoadedTestSuite]:
    """从文件夹加载多个测试套件"""
    loader = TestSuiteLoader()
    return loader.load_from_folder(folder_path)
