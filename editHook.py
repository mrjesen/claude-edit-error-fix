#!/usr/bin/env python3
"""
Claude Code Pre-Edit Hook
在调用Edit工具前，自动修正old_string参数
"""

import sys
import json
import difflib
from pathlib import Path
from typing import Optional, Dict, Any, List

class PreEditValidator:
    def __init__(self):
        self.file_path: Optional[Path] = None
        self.old_string: Optional[str] = None
        self.content: Optional[str] = None
        self.content_lines: List[str] = []
        
    def load_file(self, file_path: str) -> bool:
        """加载文件内容"""
        self.file_path = Path(file_path)
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
                self.content_lines = self.content.splitlines(keepends=True)
            return True
        except Exception:
            return False
            
    def find_all_matches(self, old_string: str) -> List[Dict[str, Any]]:
        """查找所有可能的匹配位置"""
        matches = []
        old_lines = old_string.splitlines(keepends=True)
        
        # 1. 精确匹配
        for i in range(len(self.content_lines) - len(old_lines) + 1):
            chunk = ''.join(self.content_lines[i:i + len(old_lines)])
            if chunk == old_string:
                matches.append({
                    'position': i,
                    'content': chunk,
                    'similarity': 1.0,
                    'lines': list(range(i, i + len(old_lines))),
                    'match_type': 'exact'
                })
                
        # 2. 忽略空白匹配
        if not matches:
            old_normalized = '\n'.join(line.strip() for line in old_lines)
            for i in range(len(self.content_lines) - len(old_lines) + 1):
                chunk = self.content_lines[i:i + len(old_lines)]
                chunk_normalized = '\n'.join(line.strip() for line in chunk)
                if chunk_normalized == old_normalized:
                    matches.append({
                        'position': i,
                        'content': ''.join(chunk),
                        'similarity': 0.95,
                        'lines': list(range(i, i + len(old_lines))),
                        'match_type': 'ignore_whitespace'
                    })
                    
        # 3. 模糊匹配
        if len(matches) <= 1:
            for i in range(len(self.content_lines) - len(old_lines) + 1):
                chunk = self.content_lines[i:i + len(old_lines)]
                chunk_text = ''.join(chunk)
                
                ratio = difflib.SequenceMatcher(None, chunk_text, old_string).ratio()
                if ratio > 0.6:
                    existing = False
                    for m in matches:
                        if m['position'] == i:
                            existing = True
                            break
                    if not existing:
                        matches.append({
                            'position': i,
                            'content': chunk_text,
                            'similarity': ratio,
                            'lines': list(range(i, i + len(old_lines))),
                            'match_type': 'fuzzy'
                        })
                        
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        return matches
        
    def correct_old_string(self, old_string: str) -> Dict[str, Any]:
        """修正old_string"""
        matches = self.find_all_matches(old_string)
        
        if not matches:
            return {
                'found': False,
                'old_string': old_string,
                'method': 'none'
            }
            
        # 选择最佳匹配（相似度最高的）
        best = matches[0]
        
        # 检查是否有多个高相似度匹配（>90%）
        high_quality = [m for m in matches if m['similarity'] >= 0.9]
        if len(high_quality) > 1:
            # 多个高质量匹配，选择第一个（相似度最高的）
            pass
            
        if best['similarity'] >= 0.6:
            return {
                'found': True,
                'old_string': best['content'],
                'method': best['match_type'],
                'similarity': best['similarity'],
                'matches_count': len(matches)
            }
        else:
            return {
                'found': False,
                'old_string': old_string,
                'method': 'low_confidence'
            }

def main():
    try:
        input_data = sys.stdin.read()
        if not input_data:
            sys.exit(1)
            
        data = json.loads(input_data)
        
        # 检查是否是Edit工具的PreToolUse事件
        if data.get('hook_event_name') != 'PreToolUse' or data.get('tool_name') != 'Edit':
            print(input_data)
            sys.exit(0)
            
        tool_input = data.get('tool_input', {})
        file_path = tool_input.get('file_path')
        old_string = tool_input.get('old_string')
        new_string = tool_input.get('new_string')
        
        if not all([file_path, old_string, new_string]):
            print(input_data)
            sys.exit(0)
            
        validator = PreEditValidator()
        if not validator.load_file(file_path):
            print(input_data)
            sys.exit(0)
            
        result = validator.correct_old_string(old_string)
        
        if result['found'] and result['old_string'] != old_string:
            # 修正old_string
            tool_input['old_string'] = result['old_string']
            data['tool_input'] = tool_input
            
            # 添加调试信息到stderr（不影响模型）
            print(f"修正old_string: {result['method']} (相似度: {result.get('similarity', 0):.2%})", file=sys.stderr)
            
        # 输出结果（只有这个会进入stdout被模型读取）
        print(json.dumps(data))
        sys.exit(0)
            
    except Exception:
        # 出错时传递原始输入
        if 'input_data' in locals():
            print(input_data)
        sys.exit(1)

if __name__ == "__main__":
    main()