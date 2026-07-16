# Claude Edit Error Fix

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A pre-edit hook for Claude Code that automatically fixes `old_string` parameter mismatches when using the Edit tool.

## Problem

When Claude Code attempts to edit files using the Edit tool, it often generates an `old_string` that doesn't exactly match the current file content due to:
- Extra or missing whitespace
- Inconsistent line endings
- Slight formatting differences
- Context drift between file reads and edit attempts

This causes edit operations to fail, requiring manual intervention or retries.

## Solution

This hook intercepts Edit tool calls before execution, automatically detects and corrects the `old_string` parameter to match the actual file content using multiple matching strategies:

1. **Exact Match**: Direct string comparison
2. **Whitespace-Insensitive Match**: Ignores leading/trailing whitespace differences
3. **Fuzzy Match**: Uses sequence similarity algorithm (threshold > 60%)

## Installation

1. Place the script in your Claude Code hooks directory:
   ```bash
   mkdir -p ~/.claude/hooks
   cp claude-edit-error-fix.py ~/.claude/hooks/editHook.py
   chmod +x ~/.claude/hooks/editHook.py
   ```

2. Configure Claude Code to use the hook by adding to your settings:
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

## Usage

The hook runs automatically whenever Claude Code invokes the Edit tool. No manual intervention is required.

### How It Works

1. Claude Code sends a tool call with `file_path`, `old_string`, and `new_string`
2. The hook intercepts the call and reads the actual file content
3. It searches for the best matching block using three strategies:
   - First: Exact match
   - Second: Whitespace-normalized match
   - Third: Fuzzy similarity match (>60%)
4. If a match is found, it corrects `old_string` to match the actual content
5. The corrected tool call is passed to Claude Code for execution

### Debugging

The hook outputs diagnostic information to stderr:
```
修正old_string: ignore_whitespace (相似度: 95.00%)
```

## Requirements

- Python 3.6+
- Claude Code with hook support

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For issues and feature requests, please open an issue on GitHub.
