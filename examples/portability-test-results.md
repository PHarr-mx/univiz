# 跨工具改造回归记录

日期：2026-10-26。

## 检查范围

- `python3 -B scripts/validate_skill.py`：入口结构、引用、路由加载预算与旧宿主规则回归。
- `python3 -B scripts/test_portable_html.py`：11 个静态检查回归用例，包含未定义变量、宿主接口、嵌套 CSS 回退、文档标题与图表降级。
- `python3 -B scripts/validate_portable_html.py examples/portable-*.html`：三个标准 HTML 样例。
- 三个 HTML 的内联可执行脚本经 `node --check` 语法检查。

## 实际浏览器行为

使用当前可用的 ZCode 内置浏览器访问普通本地 HTTP 页面；页面上下文中 `window.zcode` 为 `undefined`，未依赖可视化 renderer 注入主题。

| 场景 | 结果 |
| --- | --- |
| 左转页面首屏 | 标准模式 `CSS1Compat`；正文、图例、车辆和路径颜色存在 |
| 左转场景切换 | 六种路口状态的图解及文字反馈正常更新 |
| 375px 视口 | 文档无横向溢出，示意图在局部容器滚动，控件保持在页面内 |
| CSP 禁止所有页面脚本 | 初始静态 SVG、图例和结论存在；场景控件保持禁用 |
| ECharts 正常联网 | ECharts 5.6.0 加载，交互图初始化成功，隐藏替代图，保留完整数据表 |
| CSP 阻止外部资源、允许内联脚本 | ECharts 库不可用时仍显示预置 SVG、结论与 3 行数据；无整页溢出 |

## 未覆盖与边界

没有实际运行独立 Chrome、Firefox、Safari 或 VS Code HTML 预览插件，也没有通过浏览器工具测试 `file://` 导航（当前工具仅支持 HTTP/HTTPS）。因此本记录不声称这些环境都已实测通过。左转和原图结构样例均为单文件内嵌资源，未使用模块、fetch、外部样式或宿主接口；ECharts CDN 增强需要网络。

本轮浏览器检查是 DOM、样式计算与交互行为检查，不是逐像素视觉验收。CSP 资源阻断也不等同真实断网、禁用浏览器 JavaScript 或每一种编辑器沙箱；它验证的是不执行页面脚本 / 不加载外部库时已有的静态基线。
