# Industry Depth Evaluation Design — CloudMigration-Benchmark-Project

## 1. Overview

### 1.1 Purpose

Industry depth evaluation measures the AI Agent's ability to autonomously complete cloud migration tasks through multi-turn conversations. Unlike the six core AI dimensions (accuracy, safety, latency, consistency, robustness, usability), industry depth evaluation focuses on **end-to-end task completion capability** in professional cloud migration scenarios.

### 1.2 Scope

The industry depth evaluation is designed for scenarios where:
- Users lack cloud migration expertise
- Tasks require multi-step completion across phases
- Context must be maintained across extended conversations
- System failures or interruptions may occur

### 1.3 Evaluation Structure

```
Industry Depth Evaluation
├── Session Integrity (会话完整性)
├── Interruption Recovery (中断恢复)
├── Context Memory (上下文记忆)
├── Error Handling (错误处理)
├── Self-Service Navigation (自助导航)
└── Resource Consistency (资源一致性)
```

---

## 2. Evaluation Dimensions

### 2.1 Session Integrity (会话完整性)

**Purpose**: Evaluate whether the AI can guide users to complete an entire cloud migration journey without task failures or abandonment.

**Evaluation Method**:
- Track the completion status of all critical phases
- Measure the ratio of successfully completed phases to total phases
- Identify where and why journeys are abandoned

**Phases of Cloud Migration Journey**:
1. `resource_discovery` - Resource inventory and assessment
2. `cloud_strategy` - Cloud strategy and roadmap planning
3. `workload_analysis` - Workload analysis and categorization
4. `migration_plan` - Migration plan creation
5. `risk_assessment` - Risk identification and mitigation
6. `cost_estimation` - Cost estimation and optimization
7. `report_generation` - Final report generation

**Scoring Criteria**:

| Level | Score Range | Criteria |
|-------|-------------|----------|
| Excellent | 0.9-1.0 | All critical phases completed, no guidance needed |
| Good | 0.8-0.9 | All critical phases completed with minimal guidance |
| Pass | 0.6-0.8 | Critical phases completed with moderate guidance |
| Fail | <0.6 | Critical phases incomplete or abandoned |

**Test Case Template**:
```python
{
    "id": "TC-SI-001",
    "dimension": "session_integrity",
    "journey_phases": [
        "resource_discovery",
        "cloud_strategy",
        "migration_plan",
        "report_generation"
    ],
    "critical_phases": ["resource_discovery", "migration_plan"],
    "expected_output": {
        "completed_phases": [...],
        "completion_rate": 1.0,
        "guidance_required": False
    },
    "input_data": {
        "initial_query": "我们要迁移100台服务器到云端"
    }
}
```

**Evaluation Logic**:
1. Parse the conversation history to identify completed phases
2. Check if all critical phases are completed
3. Calculate the completion rate
4. Determine if human intervention was required

---

### 2.2 Interruption Recovery (中断恢复)

**Purpose**: Evaluate the AI's ability to seamlessly resume after conversation interruptions, maintaining context and state continuity.

**Evaluation Method**:
- Simulate conversation interruptions at various points
- Verify state preservation and context restoration
- Measure recovery time and accuracy

**Interruption Scenarios**:

| Scenario | Description | Recovery Requirements |
|----------|-------------|---------------------|
| Session Timeout | User reconnection after timeout | Restore previous context, confirm state |
| Multi-turn Gap | User returns after several turns | Recall earlier discussion points |
| System Error | Chat history lost, need to rebuild | Reconstruct from partial information |
| Context Switch | User changes topic abruptly | Maintain both old and new contexts |

**Test Case Template**:
```python
{
    "id": "TC-IR-001",
    "dimension": "interruption_recovery",
    "interruption_point": 3,  # Turn number where interruption occurs
    "pre_interrupt_state": {
        "current_phase": "resource_discovery",
        "discovered_resources": ["VM-001", "VM-002"],
        "progress_percentage": 40
    },
    "pre_interrupt_history": [
        {"turn": 1, "content": "我们要迁移100台服务器"},
        {"turn": 2, "content": "其中有60台Windows, 40台Linux"},
        {"turn": 3, "content": "请继续分析"}
    ],
    "expected_output": {
        "context_restored": True,
        "state_preserved": True,
        "recovery_time_turns": 1
    },
    "input_data": {
        "post_interrupt_query": "继续之前的分析"
    }
}
```

**Scoring Criteria**:

| Level | Score Range | Criteria |
|-------|-------------|----------|
| Excellent | 0.9-1.0 | Full context restoration, no information loss |
| Good | 0.7-0.9 | Context mostly restored, minor details missing |
| Pass | 0.5-0.7 | Partial restoration, requires user clarification |
| Fail | <0.5 | Context lost, cannot continue task |

**Recovery Quality Metrics**:
- **Context Accuracy**: Percentage of context correctly restored
- **State Continuity**: Whether the interrupted task can continue
- **Information Integrity**: No hallucinated or contradicting information

---

### 2.3 Context Memory (上下文记忆)

**Purpose**: Evaluate the AI's ability to maintain and recall relevant information across extended multi-turn conversations.

**Evaluation Method**:
- Introduce information in early turns
- Test recall accuracy in later turns
- Measure relevance weighting of recalled information

**Memory Types**:

| Memory Type | Description | Retention Period |
|-------------|-------------|------------------|
| Short-term | Current conversation context | Session duration |
| Medium-term | Related discussion points | Last 20 turns |
| Long-term | Critical constraints and requirements | Entire journey |

**Test Case Template**:
```python
{
    "id": "TC-CM-001",
    "dimension": "context_memory",
    "conversation_flow": [
        {"turn": 1, "speaker": "user", "content": "我们有50台Windows服务器"},
        {"turn": 2, "speaker": "agent", "content": "已记录50台Windows服务器"},
        {"turn": 3, "speaker": "user", "content": "还有20台Linux服务器"},
        {"turn": 4, "speaker": "agent", "content": "已记录20台Linux服务器"},
        {"turn": 5, "speaker": "user", "content": "我们总共有多少台服务器?"},
        {"turn": 6, "speaker": "agent", "content": "根据之前的对话，您共有70台服务器"},
        {"turn": 7, "speaker": "user", "content": "它们的操作系统分布如何?"},
        {"turn": 8, "speaker": "agent", "content": "Windows占71%，Linux占29%"}
    ],
    "memory_tests": [
        {
            "turn": 6,
            "test": "recall_total_count",
            "expected": "70台服务器"
        },
        {
            "turn": 8,
            "test": "recall_os_distribution",
            "expected": "50台Windows + 20台Linux"
        }
    ]
}
```

**Scoring Criteria**:

| Level | Score Range | Criteria |
|-------|-------------|----------|
| Excellent | 0.95-1.0 | Perfect recall with accurate quantification |
| Good | 0.85-0.95 | Correct recall, minor quantification errors |
| Pass | 0.7-0.85 | Major points recalled, some details lost |
| Fail | <0.7 | Critical information forgotten or confused |

**Memory Accuracy Metrics**:
- **Recall Precision**: Correct items / Total items recalled
- **Relevance Score**: Relevant recall / Total recall
- **Temporal Accuracy**: Correct timing of recalled information

---

### 2.4 Error Handling (错误处理)

**Purpose**: Evaluate the AI's ability to gracefully handle errors, invalid inputs, and unexpected situations during cloud migration conversations.

**Evaluation Method**:
- Inject various error scenarios into conversations
- Measure recovery success and user guidance quality
- Assess error message clarity and helpfulness

**Error Categories**:

| Error Type | Description | Example Scenarios |
|------------|-------------|-------------------|
| Input Error | Invalid or malformed user input | Malformed JSON, invalid date format |
| Constraint Violation | Request violates system constraints | Exceeding resource limits |
| Conflict State | Conflicting information provided | Contradictory requirements |
| External Failure | External system/API failures | Cloud API timeout |
| Ambiguous Request | Unclear or incomplete request | Missing critical parameters |

**Test Case Template**:
```python
{
    "id": "TC-EH-001",
    "dimension": "error_handling",
    "scenario": "constraint_violation",
    "conversation": [
        {"turn": 1, "speaker": "user", "content": "请分配10000台虚拟机的预算"},
        {"turn": 2, "speaker": "agent", "content": "检测到超出限制", "error": true},
        {"turn": 3, "speaker": "agent", "content": "最大支持1000台，是否调整为1000?"}
    ],
    "expected_output": {
        "error_detected": True,
        "error_category": "constraint_violation",
        "recovery_suggestion": True,
        "alternative_provided": True,
        "user_clarity": "high"
    }
}
```

**Scoring Criteria**:

| Level | Score Range | Criteria |
|-------|-------------|----------|
| Excellent | 0.9-1.0 | Error detected, clear message, actionable solution |
| Good | 0.75-0.9 | Error detected, reasonable guidance |
| Pass | 0.6-0.75 | Error acknowledged, recovery attempted |
| Fail | <0.6 | Error ignored or incorrect handling |

**Error Handling Quality Metrics**:
- **Detection Rate**: Errors correctly identified / Total errors
- **Clarity Score**: User understanding of error and solution
- **Recovery Rate**: Successful error recovery / Total error occurrences

---

### 2.5 Self-Service Navigation (自助导航)

**Purpose**: Evaluate the AI's ability to guide users through complex cloud migration tasks without requiring expert assistance.

**Evaluation Method**:
- Provide incomplete or ambiguous user requests
- Measure the AI's guidance effectiveness
- Track task completion with minimal expert intervention

**Navigation Scenarios**:

| Scenario | Description | Success Criteria |
|----------|-------------|------------------|
| Goal Decomposition | Break complex goals into steps | Clear step breakdown |
| Decision Support | Help users make informed choices | Pros/cons presented |
| Path Finding | Navigate to correct workflow | Optimal path followed |
| Dead End Recovery | Recover from user confusion | Redirect gracefully |

**Test Case Template**:
```python
{
    "id": "TC-SN-001",
    "dimension": "self_service_navigation",
    "user_goal": "将我们的数据中心迁移到AWS",
    "initial_context": {
        "user_expertise": "low",
        "available_time": "limited",
        "budget": "constrained"
    },
    "expected_output": {
        "initial_assessment": True,
        "step_breakdown": [
            "步骤1: 资源盘点",
            "步骤2: 目标云平台选择",
            "步骤3: 迁移策略制定",
            "步骤4: 实施计划"
        ],
        "guidance_clarity": "high",
        "expert_intervention_required": False
    }
}
```

**Scoring Criteria**:

| Level | Score Range | Criteria |
|-------|-------------|----------|
| Excellent | 0.9-1.0 | Natural navigation, no expert needed |
| Good | 0.8-0.9 | Effective guidance, minimal prompts |
| Pass | 0.6-0.8 | Functional guidance, some confusion |
| Fail | <0.6 | User lost or abandoned task |

**Navigation Quality Metrics**:
- **Step Clarity**: Users understand each step's purpose
- **Path Optimality**: Follows best practice workflow
- **User Confidence**: User feels capable of completing task

---

### 2.6 Resource Consistency (资源一致性)

**Purpose**: Evaluate the AI's ability to maintain accurate and consistent resource state across multi-turn conversations and multiple mentions.

**Evaluation Method**:
- Track resource mentions across conversation turns
- Verify consistency of resource attributes
- Detect and flag contradictions

**Resource Types**:

| Resource Type | Examples | Consistency Requirements |
|---------------|----------|-------------------------|
| Compute | VMs, Containers | Count, specs, regions |
| Storage | Volumes, Buckets | Capacity, access patterns |
| Network | VPCs, Subnets | CIDR, connectivity |
| Security | IAM, Roles | Permissions, policies |
| Cost | Budgets, Billing | Estimates, actuals |

**Test Case Template**:
```python
{
    "id": "TC-RC-001",
    "dimension": "resource_consistency",
    "conversation": [
        {"turn": 1, "content": "我们需要创建10台VM"},
        {"turn": 2, "content": "每台VM需要4核CPU和8GB内存"},
        {"turn": 3, "content": "请确认VM规格"},
        {"turn": 4, "content": "确认: 10台VM，每台4核CPU、8GB内存"},
        {"turn": 5, "content": "修改为每台8核CPU"},
        {"turn": 6, "content": "确认: 10台VM，每台8核CPU、8GB内存"}
    ],
    "consistency_checks": [
        {
            "turn": 4,
            "check": "vm_count_consistency",
            "expected": "10",
            "actual": "10",
            "consistent": True
        },
        {
            "turn": 6,
            "check": "cpu_change_consistency",
            "expected": "8核",
            "actual": "8核",
            "consistent": True,
            "previous_value": "4核"
        }
    ]
}
```

**Scoring Criteria**:

| Level | Score Range | Criteria |
|-------|-------------|----------|
| Excellent | 0.95-1.0 | Perfect consistency, no contradictions |
| Good | 0.9-0.95 | Minor inconsistencies, self-corrected |
| Pass | 0.8-0.9 | Detectible inconsistencies, flagged |
| Fail | <0.8 | Contradictions remain, user confused |

**Consistency Metrics**:
- **Attribute Accuracy**: Correct attributes / Total attributes
- **Contradiction Detection**: Contradictions identified / Total contradictions
- **Self-correction Rate**: Self-corrected / Total inconsistencies

---

## 3. Evaluation Engine

### 3.1 Industry Depth Evaluator

```python
class IndustryDepthEvaluator:
    def __init__(self, config=None):
        self.evaluators = {
            "session_integrity": SessionIntegrityEvaluator(),
            "interruption_recovery": InterruptionRecoveryEvaluator(),
            "context_memory": ContextMemoryEvaluator(),
            "error_handling": ErrorHandlingEvaluator(),
            "self_service_navigation": SelfServiceNavigationEvaluator(),
            "resource_consistency": ResourceConsistencyEvaluator(),
        }

    def evaluate_all(self, test_case, response) -> Dict[str, EvaluationResult]:
        results = {}
        for name, evaluator in self.evaluators.items():
            results[name] = evaluator.evaluate(test_case, response)
        return results

    def get_overall_score(self, results) -> float:
        weights = {
            "session_integrity": 0.25,
            "interruption_recovery": 0.15,
            "context_memory": 0.20,
            "error_handling": 0.15,
            "self_service_navigation": 0.15,
            "resource_consistency": 0.10,
        }
        weighted_sum = sum(
            results[name].score * weights[name]
            for name in results
        )
        return weighted_sum / sum(weights.values())
```

### 3.2 Evaluation Result Structure

```python
@dataclass
class IndustryDepthResult:
    dimension: str
    score: float
    level: ScoreLevel
    details: Dict[str, Any]
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimension": self.dimension,
            "score": self.score,
            "level": self.level.value,
            "details": self.details,
            "recommendations": self.recommendations,
        }
```

---

## 4. Test Suite Structure

### 4.1 XLSX Format

The industry depth test suite uses the same XLSX format as core dimensions, with additional columns:

**test_cases Sheet** (Industry Depth):
| Column | Type | Description |
|--------|------|-------------|
| id | string | Test case ID |
| dimension | string | Always "industry_depth" |
| sub_dimension | string | Specific dimension (session_integrity, etc.) |
| phase | string | Test phase |
| description | string | Test description |
| input_data | JSON | Input conversation/context |
| expected_output | JSON | Expected evaluation result |
| priority | string | P0/P1/P2 |
| tags | string | Comma-separated tags |

### 4.2 Mock Data

```python
# data/mock/industry_depth_mock.py

INDUSTRY_DEPTH_TEST_CASES = {
    "session_integrity": [
        {
            "id": "SI-001",
            "journey_phases": ["resource_discovery", "cloud_strategy"],
            "critical_phases": ["resource_discovery"],
            "expected_completion_rate": 1.0,
        },
        # ... more test cases
    ],
    "interruption_recovery": [...],
    "context_memory": [...],
    "error_handling": [...],
    "self_service_navigation": [...],
    "resource_consistency": [...],
}
```

---

## 5. Integration with Core Evaluation

### 5.1 Combined Evaluation Flow

```
User Input
    │
    ▼
┌─────────────────────────────┐
│   Core Dimensions Eval      │
│  (Accuracy, Safety, etc.)   │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│  Industry Depth Eval        │
│  (Session Integrity, etc.)  │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│   Combined Report          │
└─────────────────────────────┘
```

### 5.2 Scoring Configuration

```yaml
# config/industry_depth.yaml
dimensions:
  industry_depth:
    enabled: true
    weight: 1.0
    sub_dimensions:
      session_integrity:
        weight: 0.25
        threshold: 0.7
      interruption_recovery:
        weight: 0.15
        threshold: 0.6
      context_memory:
        weight: 0.20
        threshold: 0.75
      error_handling:
        weight: 0.15
        threshold: 0.7
      self_service_navigation:
        weight: 0.15
        threshold: 0.7
      resource_consistency:
        weight: 0.10
        threshold: 0.8
```

---

## 6. Best Practices

### 6.1 Test Case Design

1. **Cover all 6 sub-dimensions** with balanced test cases
2. **Include edge cases** for interruption and error scenarios
3. **Provide clear expected outputs** for deterministic evaluation
4. **Balance difficulty levels** (P0, P1, P2 priorities)

### 6.2 Evaluation Interpretation

1. **Overall score** represents autonomous completion capability
2. **Sub-dimension breakdown** identifies specific improvement areas
3. **Recommendations** provide actionable improvement guidance
4. **Trend tracking** monitors progress over multiple evaluations

### 6.3 Improvement Recommendations

Based on evaluation results:

| Weak Area | Recommendation |
|-----------|----------------|
| Low Session Integrity | Improve end-to-end task completion guidance |
| Low Interruption Recovery | Implement better context preservation |
| Low Context Memory | Enhance information retention mechanisms |
| Low Error Handling | Add better error detection and recovery |
| Low Self-Service Navigation | Improve user guidance and step decomposition |
| Low Resource Consistency | Implement stricter state management |

---

## 7. Appendix

### 7.1 Evaluation Metrics Summary

| Dimension | Key Metric | Target Threshold |
|-----------|------------|------------------|
| Session Integrity | Completion Rate | >= 0.85 |
| Interruption Recovery | Context Accuracy | >= 0.80 |
| Context Memory | Recall Precision | >= 0.90 |
| Error Handling | Recovery Rate | >= 0.75 |
| Self-Service Navigation | Path Optimality | >= 0.80 |
| Resource Consistency | Contradiction Detection | >= 0.95 |

### 7.2 Related Documentation

- `DEVELOPMENT.md` - Module API reference
- `TESTING.md` - Test execution guide
- `USER_GUIDE.md` - End-user documentation

---

## 8. Changelog

### v0.1.0 (2026-04-17)
- Initial release of industry depth evaluation
- Six sub-dimensions: session_integrity, interruption_recovery, context_memory, error_handling, self_service_navigation, resource_consistency
- Integration with core evaluation framework
- Mock data and test suite support