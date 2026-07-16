# Claude Edit Error Fix

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

一个用于 Claude Code 的修复edit工具的hook，可在调用 Edit 工具时自动修正 `old_string` 参数不匹配的问题。

## 问题描述

当 Claude Code 尝试使用 Edit 工具编辑文件时，生成的 `old_string` 常常因以下原因无法与当前文件内容精确匹配：

- 多余或缺失的空白字符
- 不一致的行尾符
- 细微的格式差异
- 文件读取和编辑操作之间的上下文漂移

这会导致编辑操作失败，需要人工干预或重试。

## 解决方案

本钩子在 Edit 工具执行前进行拦截，通过多种匹配策略自动检测并修正 `old_string` 参数以匹配实际文件内容：

1. **精确匹配**：直接字符串比较
2. **忽略空白匹配**：忽略首尾空白差异
3. **模糊匹配**：使用序列相似度算法（阈值 > 60%）

## 安装

1. 将脚本放置到 Claude Code 的钩子目录：
   ```bash
   mkdir -p ~/.claude/hooks
   cp claude-edit-error-fix.py ~/.claude/hooks/editHook.py
   chmod +x ~/.claude/hooks/editHook.py
   ```

2. 在设置中配置 Claude Code 使用该钩子：
   ```json
   {
     "hooks": {
       "PreToolUse": [
         {
           "matcher": "Edit",
           "command": "~/.claude/hooks/editHook.py"
         }
       ]
     }
   }
   ```

## 使用方法

钩子在 Claude Code 调用 Edit 工具时自动运行，无需手动干预。

### 工作原理

1. Claude Code 发送包含 `file_path`、`old_string` 和 `new_string` 的工具调用
2. 钩子拦截调用并读取实际文件内容
3. 使用三种策略搜索最佳匹配块：
   - 优先：精确匹配
   - 其次：忽略空白的匹配
   - 再次：模糊相似度匹配（>60%）
4. 如果找到匹配，修正 `old_string` 以匹配实际内容
5. 修正后的工具调用传递给 Claude Code 执行

### 调试信息

钩子会向 stderr 输出诊断信息：
```
修正old_string: ignore_whitespace (相似度: 95.00%)
```

## 系统要求

- Python 3.6+
- 支持钩子功能的 Claude Code

## 许可证

Apache License 2.0 - 详见 [LICENSE](LICENSE) 文件。

## 贡献

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个 Pull Request

## 支持

如有问题或功能请求，请在 GitHub 上提交 Issue。
