# univiz

统一可视化 skill。根据内容选择 ECharts、HTML/SVG、原图叠加或解释性知识配图，默认交付可独立打开的标准网页，而不是某个工具专属的渲染片段。

## 跨工具交付

- HTML 使用完整文档结构，自带主题颜色、字体和控件样式，不依赖 ZCode 或 VS Code API。
- 初始源码有静态图、结论和必要数据，脚本被禁或外部库加载失败时仍可读。
- ECharts 默认包含初始化代码和静态替代内容。CDN 版本需要网络；要求完全离线时改用 SVG 或合法打包库。
- 原图可使用获授权的内嵌图片、配套相对资源或真实 HTTPS 地址，保持原图事实与标注位置。
- VS Code 的源码视图不会渲染网页。使用 HTML 预览、Open in Browser 或 Live Server；预览器是否允许脚本由其安全策略决定，不绕过限制。

详细契约见 [SKILL.md](SKILL.md) 与 [跨工具输出规范](references/portable-output.md)。

## 可直接打开的样例

- [无保护左转交互示例](examples/portable-unprotected-left-turn.html)：无需网络；不允许脚本时保留静态图。
- [ECharts 与静态降级](examples/portable-echarts.html)：交互增强使用 ECharts 5.6.0 CDN，静态 SVG 和表格无需网络。
- [原图叠加结构示例](examples/portable-image-overlay.html)：内嵌合成底图，仅用于离线布局回归，不是用户证据。

在浏览器中打开这些 `.html`，或通过支持 HTML 的编辑器预览查看。

## 回归检查

```sh
python3 -B scripts/validate_skill.py
python3 -B scripts/test_portable_html.py
python3 -B scripts/validate_portable_html.py examples/portable-*.html
```

产物检查器采用静态启发式规则，检查文档结构、未定义变量、宿主接口、图片地址等。它不替代浏览器、视觉、可访问性或完整 CSS/JavaScript 测试。

可启动本地测试服务器：

```sh
python3 -B scripts/serve_portable_examples.py
```

默认地址 `http://127.0.0.1:8766/`。给样例 URL 加 `?policy=static` 可通过 CSP 阻止脚本；加 `?policy=offline` 可阻止外部库与联网资源而允许本页脚本。这是资源阻断回归，不等于真实断网或所有编辑器策略。
