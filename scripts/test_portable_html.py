#!/usr/bin/env python3
"""Regression checks for portable HTML policy and representative documents."""
from pathlib import Path
import re
import unittest

from validate_portable_html import validate

ROOT = Path(__file__).resolve().parents[1]


def page(content: str, css: str = '') -> str:
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>回归示例</title><style>{css}</style></head><body><p>示例数据</p>
    {content}</body></html>'''


SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
<rect width="80" height="80" fill="#2563eb"/></svg>'''


class PortabilityTests(unittest.TestCase):
    def test_standalone_svg(self):
        self.assertEqual(validate(page(SVG))['status'], 'PASS')

    def test_original_fragment_is_rejected(self):
        result = validate('<div style="color:var(--foreground)">片段</div>')
        self.assertEqual(result['status'], 'FAIL')
        self.assertTrue(any('CSS 变量' in error for error in result['errors']))

    def test_defined_variables_and_fallbacks(self):
        content = SVG.replace('#2563eb', 'var(--accent)')
        self.assertEqual(validate(page(content, ':root{--accent:#2563eb}'))['status'], 'PASS')
        self.assertEqual(validate(page(content.replace('var(--accent)', 'var(--accent, #2563eb)')))['status'], 'PASS')
        self.assertEqual(validate(page(content))['status'], 'FAIL')

    def test_nested_variable_fallback(self):
        content = SVG.replace('#2563eb', 'var(--accent, var(--other, #2563eb))')
        self.assertEqual(validate(page(content))['status'], 'PASS')
        self.assertEqual(validate(page(content.replace(', #2563eb', '')))['status'], 'FAIL')

    def test_host_bridge_is_rejected(self):
        result = validate(page(SVG + '<script>window.zcode.setWidgetState({})</script>'))
        self.assertTrue(any('宿主' in error for error in result['errors']))

    def test_svg_title_is_not_document_title(self):
        source = page(SVG.replace('<rect', '<title>图标题</title><rect'))
        self.assertEqual(validate(source)['status'], 'PASS')
        source = source.replace('<title>回归示例</title>', '')
        self.assertEqual(validate(source)['status'], 'FAIL')

    def test_echarts_without_static_baseline_fails(self):
        chart = '<div id="chart"></div><script src="https://cdn.example/echarts.min.js"></script>'
        self.assertEqual(validate(page(chart))['status'], 'FAIL')
        self.assertEqual(validate(page(chart + '<table><tr><td>12</td></tr></table>'))['status'], 'PASS')

    def test_remote_resources_are_disclosed(self):
        result = validate(page('<img src="https://example.com/image.png" alt="证据图">'))
        self.assertEqual(result['status'], 'PASS')
        self.assertTrue(any('联网' in warning for warning in result['warnings']))

    def test_private_image_protocol_is_rejected(self):
        self.assertEqual(validate(page('<img src="vscode-resource:/image.png" alt="证据图">'))['status'], 'FAIL')

    def test_portable_examples(self):
        examples = list((ROOT / 'examples').glob('portable-*.html'))
        self.assertGreaterEqual(len(examples), 3)
        for example in examples:
            with self.subTest(example=example.name):
                result = validate(example.read_text(encoding='utf-8'))
                self.assertEqual(result['errors'], [])

    def test_old_output_contracts_do_not_return(self):
        forbidden = [
            '禁 `<!DOCTYPE>`/`<head>`/`<body>`',
            '不使用 DOCTYPE、head、body',
            '宿主负责 HTML 包装',
            '普通数据图不得同时再输出 HTML 版 ECharts',
        ]
        for path in [ROOT / 'SKILL.md', *(ROOT / 'references').glob('*.md')]:
            text = path.read_text(encoding='utf-8')
            for stale in forbidden:
                with self.subTest(path=path.name, stale=stale):
                    self.assertNotIn(stale, text)


if __name__ == '__main__':
    unittest.main()
