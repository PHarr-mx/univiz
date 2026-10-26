# 跨工具可移植输出契约

所有可视化分支先遵守本文件；分支文件只补充绘图方法，不能重新引入宿主依赖。

## 目标与边界

默认产物是一个标准、完整、可独立打开的 HTML 文档。在普通浏览器用 `file://` 打开或由普通静态服务器提供时，均能显示核心内容；VS Code 可通过支持 HTML 的预览插件或 Open in Browser / Live Server 打开。同一份 HTML 是内容真源，ZCode 等宿主的展示包装只是传输方式。

编辑器的源码视图不负责渲染 HTML；Markdown 预览、CSP 或沙箱可能禁止脚本、外部资源甚至 HTML。不要承诺绕过这些限制：保留静态图、数据与结论，并明确交互需要允许 JavaScript 的 HTML 预览或浏览器。完全不支持 HTML 的环境，使用配套文字或 Markdown 数据表。

## 默认交付

- 有文件写入能力时，创建主题命名的 UTF-8 `.html` 文件并给出链接；不要只输出仅宿主识别的 renderer 或 echarts 块。静态 HTML 页面不等于 PDF/PPT 等附件制作任务，不受附件排除规则影响。
- 只能回复文本时，用普通 `html` 代码块输出完整文档，说明保存为 `.html` 后打开；代码围栏不是文件内容。宿主强制要求专用包装时可在展示层适配，但被包装的内容或链接目标仍须是同一份独立文档。
- 默认一个 HTML 文档，最多两个核心模块放在同一 `main` 中，不拼接多个 `html` 根。网页本身包含结论、图例、单位和必要来源，不能只在聊天正文中解释。
- 用户明确只要 ECharts option、SVG 源码或片段时，按所需格式给出并说明它不是独立网页；这不是默认交付。
- 生成式知识配图仍由图片工具生成；使用真实可访问的图片文件或 URL 及替代文字，而非宿主私有附件 ID。可保存图片时提供本地文件链接；需要统一网页时将图片和正文放入标准 HTML。不得假装临时图片 URL 可永久访问。

## 标准文档与自带样式

文档具有 `<!doctype html>`、`<html lang="zh-CN">`、显式 `head` / `body`，`head` 内包含 UTF-8、viewport 和唯一非空的主题 `title`。使用系统字体；所有用到的 CSS 类和变量都要在文档内定义，或在每个 `var()` 处提供有效回退。SVG 中同样适用，包含脚本动态生成的属性。

不要依赖 `--foreground`、`--background`、`--viz-series-*`、`.form-select`、`.text-muted` 等宿主注入的主题或控件样式；可改为本页命名的 `--viz-*` 并赋具体颜色。根节点显式设置前景色、背景色、字号和行高；控件自带边框、背景、字体和可见焦点。默认浅色主题即可，暗色适配必须自行定义，不能靠宿主补齐。

SVG 使用明确的 `viewBox`、`xmlns`、可读的文字大小和可访问的 `title` / `desc`；`width:100%;height:auto;display:block`。不要依赖全局 ID 或浏览器把 ID 自动挂到 window；脚本以当前文档根节点查询。窄屏允许换行，必要的图表滚动须局部实现，不能让整页溢出。

## 运行时与降级

- 默认使用原生 HTML/CSS/SVG 和普通内联脚本，不依赖框架、构建工具、模块服务器、`fetch` 本地 JSON、跨域请求或扩展 API。离线演示应在单文件内含数据和资源。
- 不使用 `window.zcode`、`acquireVsCodeApi`、宿主消息事件、专用工具桥接或私有资源协议驱动绘图。可选的宿主集成只允许作为用户明确要求的单独适配层，移除后核心功能不变。
- 初始源码就有有意义的静态图、文字和/或数据表，不把所有内容放进等待 JS 初始化的空容器。禁脚本时显示静态状态与说明；交互控件初始禁用或隐藏，初始化成功后再启用。
- 脚本放在对应 DOM 之后，或等待 DOMContentLoaded；能力检测后再使用 ResizeObserver 等可选 API。先在离屏节点构造新图，成功后再替换旧图，避免清空后异常留下空白。
- 播放、切换、拖拽等在无宿主 API 时正常工作。需要保存状态时可使用内存；使用 localStorage 时捕获拒绝访问异常，不能阻止首屏与交互。
- 不假定任意预览器允许 JS，也不宣称 `<noscript>` 能识别所有沙箱拦截。静态基线始终存在，脚本增强成功后才按需隐藏或替换。

## ECharts、图片与外部资源

默认 ECharts 交付也使用完整 HTML：显式加载固定版本的 HTTPS ECharts 脚本，定义 option，初始化有明确高度的容器，并处理 resize。库未加载、初始化异常或脚本被禁时，预置静态 SVG 图或可读数据表与结论仍可见；只在成功绘制后隐藏替代图，不删除可访问的数据表。链接版本和网络需求应写明。

“跨工具”不等于“所有依赖离线可用”。如果用户要求完全离线，优先确定性 SVG；必须保留 ECharts 时使用合法取得并随产物提供的本地库，或将库内联并保留许可证，不把 CDN 版本称作离线版。不要复制来源不明的库。

原图优先使用已获授权的内嵌 data URI 或随 HTML 一同提供的相对资源；不能下载时可使用真实 HTTPS 原图，并标明需要联网。标注几何和原图比例不变，不能为了离线改造而重绘证据。图片加载失败时，替代文字、文字结论和证据限制仍可读。

## 最小结构示例

下面只是结构，不是任务的默认内容。实际回复要按主题重新绘图。

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>任务的具体主题</title>
  <style>
    :root { color-scheme: light; --viz-fg: #172033; --viz-bg: #ffffff; --viz-accent: #2563eb; }
    * { box-sizing: border-box; }
    body { margin: 0; background: var(--viz-bg); color: var(--viz-fg); font: 16px/1.6 system-ui, sans-serif; }
    main { max-width: 960px; margin: auto; padding: 24px; }
    svg { display: block; width: 100%; height: auto; }
  </style>
</head>
<body>
  <main>
    <h1>任务的具体主题</h1>
    <p>初始即能阅读的核心结论。</p>
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 100" role="img" aria-labelledby="diagram-title diagram-desc">
      <title id="diagram-title">图解标题</title>
      <desc id="diagram-desc">图解的文字说明。</desc>
      <rect x="10" y="10" width="580" height="80" rx="8" fill="#eff6ff" stroke="#2563eb"/>
      <text x="300" y="58" text-anchor="middle" fill="#172033" font-size="18">按当前任务绘制有意义的静态图</text>
    </svg>
  </main>
</body>
</html>
```

## 交付前验证

1. 检查最终 `.html`，而非只检查聊天包装：完整文档、主题标题、自定义属性有定义或回退、无宿主 API/私有 URL、核心静态内容存在。
2. 有本地执行能力时运行 `python3 scripts/validate_portable_html.py <产物.html>`；它只做静态启发式检查，不能证明视觉质量、全部 CSS 正确或交互成功。
3. 有浏览器能力时在不注入宿主主题或桥接的普通页面上下文中验证首屏、至少一次核心交互和窄屏。另测禁脚本/外部库失败的基线；不能仅凭“在 ZCode 中能显示”判定跨工具通过。
4. 记录实际测试环境。未运行 Chrome、Firefox、Safari 或 VS Code 预览时，不声称它们均已实测；可说明使用标准 Web 能力及尚未覆盖的环境。
