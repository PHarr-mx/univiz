---
name: univiz
description: 当回答涉及趋势、占比、比较、流程、机制、因果、架构、关系、时间线、状态机、算法步骤、参数变化、原图证据，或用户明确要求图表、图解、知识配图、标注、动态/交互演示时使用。以可独立打开的标准 HTML/SVG 和 ECharts 输出跨工具可视化；解释性配图可用生成图。不承接地图、办公附件、海报、头像、写实图片和纯艺术插画。
---

# 统一可视化

将适合图形表达的内容转成可复核、可运行、可跨工具查看的可视化。只选择能明显增加理解的最少模块；不依赖 ZCode、VS Code 或其他宿主注入的样式和运行时。

## 路由

按顺序判断，首次命中即确定主模式：

1. **图示是否明显优于文字？** 否，或用户明确只要文字 → `text_only`。
2. **结论是否依赖用户原图的真实位置、数量、边界、路径或匹配？** 是 → `static_image_overlay`。
3. **核心是否是精确数值的趋势、占比、排行、分布、相关性或多指标比较？** 是 → `echarts`。
4. **核心是否需要解释性插画、视觉隐喻或明确允许的原图参考重绘？** 是，且不要求精确连线、逐字文字或交互 → `generated_illustration`；普通可枚举知识结构继续下一步。
5. **核心是否是可准确枚举的流程、机制、架构、关系、时间线、状态或算法过程？** 是 → `html_svg`。
6. 结构或事实不足以可靠绘制 → `text_only`。

用户明确要求 ECharts/option 时直接选择 `echarts`，但只有明确只要配置时才仅交付 option。原图仅用于观察结构且用户要简化示意时，选择 `html_svg` 并标明“示意”，不得替代原图证据。事实不足时不得用生成图补造。

## 不使用

- 简短事实、确认、普通改写、翻译、闲聊或纯文字已足够清楚。
- 海报、头像、壁纸、写实图片、纯艺术插画或与知识讲解无关的风格化创作。
- 地图、导航、地理轨迹、行政区划、经纬度点位或地图热力。
- PDF、PPT、Word、Excel 等办公附件交付；使用对应文件能力。标准 HTML 可视化页面及配套图片资源属于本 skill 的交付范围。

## 硬规则

- **跨工具默认**：交付完整标准 HTML 文件，自带 CSS、颜色和数据；不用宿主专用 renderer、主题变量或桥接 API 承担核心功能。完整规范见 `references/portable-output.md`。
- **静态默认**：交互必须揭示新的状态、因果、参数变化或证据，不能只做装饰动画或 hover 高亮。
- **证据保真**：依赖原图事实时保持原图像素内容、对象位置和比例；示意图必须显式标明“示意”。
- **数据可复核**：真实数字、年份、人物、事件和专业细节只来自用户材料或合法核验结果；示例数据必须明确标注。
- **数据不可生图**：精确数值、比例、统计关系、坐标和可复核趋势由 ECharts 或确定性 HTML/SVG 承担，生成图只作解释性示意。
- **模式单一**：默认一个主模块。只有第二模块回答独立核心问题时才组合，最多两个；生成式多图确需更多时按章节拆分。
- **初始可读**：HTML 初始源码含核心结论和有意义的静态图或数据表；禁脚本、库加载失败时仍能阅读，不能只靠 catch 或 noscript 填空。
- **失败可降级**：复杂交互 → 静态 HTML/SVG → 结构化文字；任何失败都不能留下空白。
- **地图禁用**：所有模式禁止地图和 ECharts `geo/map`。

## 按需加载

非 `text_only` 模式先完整读取 `references/portable-output.md`，再读一个主文件。它统一交付格式、样式自包含、资源和降级契约；分支文件不能覆盖为宿主专用输出。只追加当前任务需要的专项文件。

| 主模式 | 基础必读 | 出现以下特征时追加读取 |
| --- | --- | --- |
| `echarts` | `references/mode-echarts.md` | 复杂 callback、自由布局、特殊数据格式或移动端密集布局 → `references/echarts-option-spec.md`；明确电脑端/网页端 → `references/echarts-web-pc-spec.md`；该分支选择 Sunburst/Gauge → 对应 `references/echarts-web-pc-sunburst-reference.md` / `references/echarts-web-pc-gauge-reference.md` |
| `static_image_overlay` | `references/mode-image-overlay.md` | 仅“单图 + 单 step + 总 coord 数 ≤2 + 无图例/避让”可只读主文件；总 coord 数 ≥3、steps ≥2、多图，或需要路径、多组配对、计数、图例、标签避让 → 同时读 `references/image-overlay-process-spec.md`、`references/image-overlay-authoring-spec.md` |
| `html_svg` 静态 | `references/mode-html-svg.md` | 高密度排版、专用库或特殊视觉设计 → `references/renderer-trigger-design.md`；明确移动端复杂布局 → `references/renderer-output-mobile.md` |
| `html_svg` 交互 | `references/mode-html-svg.md` | 脚本、动画、动态公式 → `references/renderer-stability-math.md`；拖拽、播放、几何约束、DOM/ECharts 联动 → `references/renderer-interaction-geometry.md` |
| `generated_illustration` | `references/mode-generated-illustration.md` | 必须再完整读取 `references/generated-prompt-rules.md`、`references/generated-style-guide.md`、`references/generated-tool-contracts.md`、`references/shared-quality.md` |
| 组合输出 | 各主模式文件 | 再读 `references/composition.md`，在同一完整网页中组合，不拼接文档根 |

`references/routing.md`、`references/shared-quality.md`、`references/tool-contracts.md` 是设计、审计和能力不确定时的参考，除生成式分支上述依赖外，不是正常任务必读。`examples/`、`schemas/` 和 `scripts/` 服务开发与回归。

## 最小内部计划

```json
{
  "mode": "html_svg",
  "behavior": "static",
  "source": "user_content",
  "secondary": null
}
```

- `mode`：`text_only`、`echarts`、`static_image_overlay`、`html_svg`、`generated_illustration`。
- `behavior`：仅 `html_svg` 使用 `static` 或 `interactive`，其他模式为 `not_applicable`。
- `source`：`user_content`、`user_image`、`verified`、`example`、`insufficient`。
- `secondary`：无组合时为 `null`，否则填写第二模式。

## 输出协议

先用文字给结论，再给可视化链接。可写文件时创建主题命名的 `.html`；否则用普通 `html` 代码块给完整源码，说明保存后打开。宿主明确要求的展示包装仅是可选适配，不替代独立网页。不要将 Markdown 围栏写进 `.html` 文件。

### 标准 HTML

每页使用 `<!doctype html>`、`<html lang="zh-CN">`、`head`、UTF-8、viewport、唯一且非空的主题 `title`、`body`。标题放在 `head`，可见标题或 SVG title 不能替代文档 title。CSS 和所用变量自行定义，图形、控件、前景与背景不依赖宿主。普通浏览器与支持 HTML 的编辑器预览是运行目标；源码编辑器、禁脚本 Markdown 预览不保证交互，必须保留静态基线。

### ECharts

默认交付完整 HTML：自带 option、固定版本库引用、初始化、有明确高度的图表容器、缩放处理、预置静态图或数据表。只在绘制成功后隐藏替代图。联网依赖明确标注，要求完全离线时改用静态 SVG 或合法打包库。用户明确只要 option 时才输出小写 `echarts` 配置块，并说明它需要 ECharts 运行环境。

### 原图叠加

先给文字答案，再给保留原图的标准 HTML。底图可为获授权的内嵌图片、配套相对文件或真实 HTTPS URL；保留来源，标明网络依赖。初始源码预置关键静态标注，简单点、框、箭头不需要脚本；密集标记确有收益时才增加 click/tap。

### HTML/SVG

默认自带样式的静态 SVG/HTML；需要交互时用原生 JavaScript，不依赖宿主桥接。控件有即时反馈并支持键盘和 click/tap，动画可暂停、可重置。静态状态和结论先存在于源码中，脚本成功后才启用交互。

### 生成式知识配图

先形成正文与配图计划，再按当前工具 schema 生成；图片紧跟对应段落并标明“解释性图解”。提供可访问的真实图片或文件链接，必要时与正文打包为标准网页；不依赖私有附件 ID。工具不可用时保留文字，结构可准确表达时可改用静态 HTML/SVG。

## 统一交付检查

- 最终产物是否是完整标准 HTML，具有唯一非空的主题 title，而非只在特定工具里生效的片段？
- CSS 类、变量、字体与控件是否有本页定义或有效回退？是否移除了宿主 API 和私有资源协议？
- 图形是否增加理解，模式与素材匹配，数据、术语、单位、时间和来源一致？
- 原图是否保真，示意性质是否明确？
- 窄屏是否无重叠、裁切和整页溢出？
- 禁脚本、离线或库加载失败时是否仍有静态图、数据表和结论？是否诚实标明依赖与测试范围？
- 是否误用了地图、虚构事实，或用网页冒充办公附件？
- 有本地执行能力时运行 `python3 scripts/validate_portable_html.py <产物.html>`，并按跨工具契约验证实际浏览器行为；结构检查不能替代视觉和交互测试。

## 文件职责

- `references/portable-output.md`：所有可视化分支的跨工具交付、标准文档、资源与降级契约。
- 各 `mode-` 前缀的参考文件：各主模式的完整运行契约；其余 `references/` 只处理加载表中的复杂特征。
- `examples/routing-cases.md`：路由回归；`examples/portable-*.html`：独立网页回归样例。
- `schemas/visualization-plan.schema.json`：最小内部计划 Schema。
- `scripts/validate_skill.py`：结构、路由与加载预算校验；`scripts/validate_portable_html.py`：产物可移植性静态检查。
