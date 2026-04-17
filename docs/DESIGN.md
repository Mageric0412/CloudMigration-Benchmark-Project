# Design System — CloudMigration-Benchmark-Project

## 1. Product Context

- **What this is**: 云迁移AI Agent评测框架 - 专注于评估AI在云迁移场景中的运维能力
- **Who it's for**: 云架构师、DevOps工程师、SRE团队、AI研究员
- **Space/industry**: 云评估 / MLOps / DevOps 仪表板 / AI Agent评测
- **Project type**: Web App (Gradio) + Python SDK

## 2. Design Philosophy

### 2.1 核心理念

**"精准、专业、值得信赖"**

作为一个专业的AI评测工具，设计语言传达的是：
- **严谨精确**: 数据驱动的评测需要清晰、专业的视觉呈现
- **技术洞察**: 不是冰冷的机器界面，而是传达"人为判断"的专业感
- **高效直观**: 评测工作流需要高效、减少认知负担

### 2.2 差异化定位

区别于竞品（企业级蓝调/科技感），本项目采用：
- **暖中性色调**: 传达专业与人文感
- **单一强调色**: 突出关键数据与操作
- **清晰的信息层次**: 让复杂数据一目了然

## 3. Typography

### 3.1 字体选择

| 用途 | 字体 | 理由 |
|------|------|------|
| **Display/Hero** | Instrument Sans Bold | 几何无衬线，传达技术严谨感 |
| **Body** | DM Sans Regular | 高可读性，人文感 |
| **UI/Labels** | DM Sans | 与Body保持一致 |
| **Data/Tables** | JetBrains Mono | 等宽字体，tabular-nums确保数字对齐 |
| **Chinese** | Noto Sans SC | 完整的中文字符支持 |

### 3.2 字体加载

```
Google Fonts: Instrument Sans, DM Sans, JetBrains Mono, Noto Sans SC
```

### 3.3 字体比例

| 层级 | 尺寸 | 字重 | 字间距 | 行高 |
|------|------|------|--------|------|
| Hero | 48px | 700 | -0.02em | 1.2 |
| H1 | 32px | 700 | -0.01em | 1.3 |
| H2 | 24px | 600 | 0 | 1.4 |
| H3 | 18px | 600 | 0 | 1.5 |
| Body | 16px | 400 | 0 | 1.7 |
| Caption | 12px | 400 | 0.05em | 1.5 |
| Code | 14px | 400 | 0 | 1.6 |

## 4. Color System

### 4.1 色彩策略

**暖中性 + 单一强调色**

这种配色方案在企业级工具中独树一帜，区别于常见的蓝色科技风。

### 4.2 主色板

```
Primary Text:      #1a1a1a   (深色标题、主要文字)
Background:        #FAFAF8   (暖白主背景)
Surface:           #F0EFEB   (米灰卡片/容器背景)
Surface Hover:     #E8E7E2   (交互状态)
Border:            #D4D3CF   (分割线、边框)
Accent:            #E85D04   (暖橙强调色 - CTA、关键数据)
Accent Hover:      #D45403   (按钮悬停状态)
Muted:             #6B6B6B   (次要文字、辅助信息)
```

### 4.3 语义色

```
Success:    #2D6A4F  (深绿 - 通过状态、正确指标)
Warning:    #BC6C25  (赭色 - 警告状态、需要关注)
Error:      #9B2226  (深红 - 失败状态、错误信息)
Info:       #3498DB  (蓝色 - 信息提示)
```

### 4.4 分数颜色映射

```
Excellent (>= 0.9):  #27AE60  (鲜绿)
Good      (>= 0.8):  #2ECC71  (浅绿)
Pass      (>= 0.6):  #F39C12  (橙色)
Fail      (< 0.6):   #E74C3C  (红色)
```

### 4.5 暗色模式

降低亮度但保持暖色调：

```
Dark Text:    #E8E7E2
Dark Background: #1a1a1a
Dark Surface: #2a2a2a
Dark Border:  #404040
```

## 5. Spacing System

### 5.1 基础间距单位

**Base Unit: 4px**

### 5.2 间距比例

| Token | 大小 | 用途 |
|-------|------|------|
| 2xs | 2px | 紧凑元素间距 |
| xs | 4px | 标签与内容间距 |
| sm | 8px | 相关元素分组 |
| md | 16px | 标准间距 |
| lg | 24px | 区块间距 |
| xl | 32px | 大区块间距 |
| 2xl | 48px | 页面级间距 |
| 3xl | 64px | 区块分隔 |

### 5.3 组件内间距

```
Button Padding:     12px 24px  (竖直 水平)
Card Padding:      20px       (内边距)
Input Padding:      12px 16px
Table Cell Padding: 12px 16px
```

## 6. Layout System

### 6.1 网格系统

```
Grid Columns:     12
Max Width:         1200px
Gutter:            24px
Column Padding:     16px
```

### 6.2 内容宽度

```
Main Content:      1200px   (最大宽度)
Reading Width:     680px    (文档、说明文字)
Form Width:        480px    (表单输入)
```

### 6.3 圆角

分层圆角 - 不是统一的"泡泡"效果：

```
sm:   4px    (按钮、输入框)
md:   8px    (卡片、面板)
lg:   12px   (模态框、大卡片)
full: 9999px (胶囊按钮)
```

## 7. Motion Design

### 7.1 动效理念

**Minimal-functional** - 仅功能性过渡

评测工具不需要花哨动画，专注于状态切换反馈和进度指示。

### 7.2 动效规格

| 属性 | 值 | 用途 |
|------|------|------|
| Easing In | ease-in | 元素退出 |
| Easing Out | ease-out | 元素进入 |
| Duration Fast | 100ms | 状态切换 |
| Duration Base | 200ms | 标准过渡 |
| Duration Slow | 300ms | 大区块动画 |

### 7.3 允许动画的属性

```
✓ opacity
✓ transform (translate, scale)
✓ color
✓ background-color
✗ width, height (避免layout抖动)
✗ position (避免重排)
```

### 7.4 进度动画

评测进度使用实时更新而非动画：
- 使用 `gr.Progress()` 实时显示
- 进度条颜色根据完成度变化
- 数字百分比实时更新

## 8. Component Library

### 8.1 按钮

| 类型 | 样式 | 用途 |
|------|------|------|
| Primary | 背景#E85D04, 文字白色 | 主要操作 |
| Secondary | 边框#D4D3CF, 背景透明 | 次要操作 |
| Ghost | 文字#6B6B6B | 辅助操作 |
| Danger | 背景#9B2226 | 危险操作 |

**按钮状态**:
- Default: 标准样式
- Hover: Accent Hover / Surface Hover
- Active: 缩小0.98
- Disabled: opacity 0.5, cursor not-allowed

### 8.2 卡片

```
Background:  #FFFFFF 或 #F0EFEB
Border:     1px solid #D4D3CF
Radius:     8px
Shadow:     0 2px 4px rgba(0,0,0,0.04)
Padding:    20px
```

**卡片类型**:
- **Metric Card**: 显示单个指标的数值
- **Data Card**: 显示表格或列表
- **Action Card**: 包含操作按钮

### 8.3 数据表格

```
Header:     #F0EFEB 背景, 字重600
Row:        白色背景
Row Hover:  #FAFAF8 背景
Border:     1px solid #E8E7E2
Cell:       12px 16px padding
```

**表格功能**:
- 列排序
- 行选择
- 分页
- 固定列
- 响应式滚动

### 8.4 进度指示器

- **Linear Progress**: 实心条，颜色渐变
- **Circular Progress**: 圆形进度环
- **Step Progress**: 分步骤指示器

### 8.5 图表配色

雷达图/饼图使用的颜色序列：

```
Chart Colors:
  #3498DB  (蓝色)
  #E85D04  (橙色)
  #27AE60  (绿色)
  #9B2226  (红色)
  #BC6C25  (棕色)
  #2ECC71  (浅绿)
  #E74C3C  (浅红)
```

## 9. Responsive Breakpoints

| Breakpoint | Width | Columns | 用途 |
|------------|-------|---------|------|
| Mobile | < 640px | 4 | 手机 |
| Tablet | 640-1024px | 8 | 平板 |
| Desktop | 1024-1440px | 12 | 标准桌面 |
| Wide | > 1440px | 12 | 大屏 |

## 10. Accessibility

### 10.1 颜色对比

```
Normal Text (>= 16px):  3:1
Large Text (>= 24px):   3:1
UI Components:          4.5:1
```

### 10.2 焦点指示

```
Outline:    2px solid #E85D04
Offset:     2px
Style:      solid
```

### 10.3 ARIA标签

所有交互组件必须有：
- `aria-label` 或 `aria-labelledby`
- `role` 属性
- 键盘导航支持

## 11. Gradio Theming

### 11.1 自定义主题配置

```python
APP_THEME = gr.themes.Soft(
    primary_hue="orange",      # 暖橙主色调
    neutral_hue="gray",        # 中性灰
    font=[gr.themes.GoogleFont("DM Sans"), "ui-sans-serif", "system-ui"]
)
```

### 11.2 CSS变量

```css
:root {
    --primary: #E85D04;
    --primary-hover: #D45403;
    --background: #FAFAF8;
    --surface: #F0EFEB;
    --text: #1a1a1a;
    --muted: #6B6B6B;
    --border: #D4D3CF;
    --success: #27AE60;
    --warning: #F39C12;
    --error: #E74C3C;
}
```

## 12. Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-17 | Initial design system created | CloudMigration-Benchmark项目初始化 |
| 2026-04-17 | Warm Neutrals + Orange accent | 区别于企业蓝，传达专业人文感 |
| 2026-04-17 | Instrument Sans + DM Sans | 技术严谨感与人文可读性平衡 |
| 2026-04-17 | Gradio 6.x Soft theme | 现代、简洁的UI框架 |

## 13. Future Considerations

- [ ] 深色模式完整支持
- [ ] 移动端适配优化
- [ ] 打印样式支持
- [ ] 国际化(i18n)预留
- [ ] 自定义主题API
