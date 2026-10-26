#!/usr/bin/env python3
"""Heuristic checks for standalone visualizations; not a browser or CSS validator."""
from __future__ import annotations

import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path


class Document(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[tuple[str, dict[str, str | None]]] = []
        self.stack: list[str] = []
        self.titles: list[str] = []
        self.styles: list[str] = []
        self.scripts: list[tuple[dict[str, str | None], str]] = []
        self.text: list[str] = []
        self._title: list[str] | None = None
        self._script: tuple[dict[str, str | None], list[str]] | None = None
        self._style: list[str] | None = None
        self.static_graphics = 0
        self.static_cells = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        self.tags.append((tag, attributes))
        if tag not in {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
                       'link', 'meta', 'param', 'source', 'track', 'wbr'}:
            self.stack.append(tag)
        if tag == 'title' and 'head' in self.stack and 'svg' not in self.stack:
            self._title = []
        if tag == 'script':
            self._script = (attributes, [])
        if tag == 'style':
            self._style = []
        if 'style' in attributes:
            self.styles.append(attributes['style'] or '')
        if tag in {'path', 'rect', 'line', 'polyline', 'polygon', 'circle', 'ellipse'} and 'svg' in self.stack:
            self.static_graphics += 1

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag == 'title' and self._title is not None:
            self.titles.append(''.join(self._title).strip())
            self._title = None
        if tag == 'script' and self._script is not None:
            attrs, chunks = self._script
            self.scripts.append((attrs, ''.join(chunks)))
            self._script = None
        if tag == 'style' and self._style is not None:
            self.styles.append(''.join(self._style))
            self._style = None
        if tag in self.stack:
            self.stack = self.stack[:len(self.stack) - 1 - self.stack[::-1].index(tag)]

    def handle_data(self, data: str) -> None:
        if self._script is not None:
            self._script[1].append(data)
        elif self._style is not None:
            self._style.append(data)
        elif self._title is not None:
            self._title.append(data)
        elif 'body' in self.stack and data.strip():
            self.text.append(data.strip())
            if 'td' in self.stack:
                self.static_cells += 1


def variable_uses(source: str):
    """Yield custom property uses with a top-level fallback, including nested var()."""
    for match in re.finditer(r'var\(\s*(--[\w-]+)', source):
        depth, index, fallback = 1, match.end(), False
        while index < len(source) and depth:
            char = source[index]
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
            elif char == ',' and depth == 1:
                fallback = bool(source[index + 1:].split(')', 1)[0].strip())
            index += 1
        yield match.group(1), fallback


def validate(source: str) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    document = Document()
    document.feed(source)
    if not re.match(r'\s*<!doctype\s+html\s*>', source, re.I):
        errors.append('缺少 HTML5 doctype，或文件前含 Markdown 包装')
    for tag in ('html', 'head', 'body'):
        if len([item for item, _ in document.tags if item == tag]) != 1:
            errors.append(f'需要且只能有一个显式 {tag} 元素')
        if not re.search(rf'</{tag}\s*>', source, re.I):
            errors.append(f'缺少 {tag} 结束标签')
    html = next((attrs for tag, attrs in document.tags if tag == 'html'), {})
    if not html.get('lang'):
        errors.append('html 缺少 lang')
    if len(document.titles) != 1 or not all(document.titles):
        errors.append('head 内需要唯一非空的文档 title')
    metas = [attrs for tag, attrs in document.tags if tag == 'meta']
    if not any((attrs.get('charset') or '').lower() == 'utf-8' for attrs in metas):
        errors.append('缺少 UTF-8 meta charset')
    if not any((attrs.get('name') or '').lower() == 'viewport'
               and 'width=device-width' in (attrs.get('content') or '') for attrs in metas):
        errors.append('缺少响应式 viewport meta')
    if not document.text:
        errors.append('初始 body 没有可读文字')
    if not (document.static_graphics or document.static_cells
            or any(tag == 'img' and attrs.get('alt') for tag, attrs in document.tags)):
        warnings.append('未发现预置 SVG 几何、表格数据或带 alt 的图片；需人工确认静态基线')
    for tag, attrs in document.tags:
        if tag == 'svg' and (not attrs.get('viewbox') or not attrs.get('xmlns')):
            errors.append('SVG 需要 viewBox 与 xmlns')
        if tag == 'img' and not attrs.get('alt'):
            errors.append('图片缺少非空 alt')
        for name in ('src', 'href'):
            value = attrs.get(name) or ''
            if re.match(r'(?:zcode|vscode-webview|vscode-resource|blob|file):', value, re.I):
                errors.append(f'不可移植的资源地址: {value[:100]}')
            if value.startswith(('https://', 'http://', '//')):
                warnings.append(f'外部资源需要联网: {value[:100]}')
    scripts = '\n'.join(text for _, text in document.scripts)
    if re.search(r'\b(?:window\s*\.\s*zcode|acquireVsCodeApi)\b|zcode:set_globals', scripts):
        errors.append('核心文件含宿主专用 API，应移至单独适配层')
    definitions = set(re.findall(r'(--[\w-]+)\s*:', '\n'.join(document.styles)))
    undefined = {name for name, fallback in variable_uses(source)
                 if name not in definitions and not fallback}
    if undefined:
        errors.append('CSS 变量未定义且没有回退: ' + ', '.join(sorted(undefined)))
    if re.search(r'<script\b[^>]*\bsrc\s*=.*?echarts', source, re.I):
        if not (document.static_graphics or document.static_cells):
            errors.append('ECharts 需要预置静态图或数据表作为失败基线')
    if re.search(r'\bfetch\s*\(|type\s*=\s*[\"\']module[\"\']', source):
        warnings.append('包含 fetch 或模块脚本，需额外验证 file:// 与离线行为')
    return {'status': 'FAIL' if errors else 'PASS', 'errors': errors,
            'warnings': list(dict.fromkeys(warnings))}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', nargs='+', type=Path)
    args = parser.parse_args()
    results = []
    for path in args.paths:
        try:
            result = validate(path.read_text(encoding='utf-8'))
        except (OSError, UnicodeError) as exc:
            result = {'status': 'FAIL', 'errors': [str(exc)], 'warnings': []}
        results.append({'path': str(path), **result})
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return int(any(result['status'] == 'FAIL' for result in results))


if __name__ == '__main__':
    raise SystemExit(main())
