# Reference

## Error Handling

| Condition                        | Action                                              |
|----------------------------------|-----------------------------------------------------|
| No content to save               | Ask the user what they want to memorize              |
| Ambiguous topic                  | Ask the user to clarify or suggest a filename        |
| Bank directory cannot be created | Report the permission or filesystem error            |
| Write/append fails               | Report the error from `memorize.py` stderr output    |
| Diff fails to apply              | Report patch failure; suggest overwriting instead     |
| `patch` command not found        | Report that `patch` is required and must be installed |
| Target file missing for diff     | Report the file does not exist; suggest a full write  |
| No memories match search         | Answer the question normally; offer to save the answer |
| Memory file unreadable           | Report the error; answer without the stored context  |
| Bank directory does not exist    | No memories stored yet; proceed without recall       |

## Gotchas

- The `memorize.py` script must be invoked from the skill directory or with its
  full path so it can resolve correctly.
- When piping content via `echo`, use a heredoc for multi-line content to
  preserve formatting:
  ```bash
  python3 scripts/memorize.py --stdin -o "TOPIC.md" << 'EOF'
  content here
  EOF
  ```
- The `--diff` flag expects a unified diff format. If the user describes changes
  in natural language, generate the diff before passing it to the script.
- File names are case-sensitive on Linux but not on macOS. Stick to the
  UPPERCASE convention to avoid collisions.
- The `--append` flag does not add a separator between existing and new content.
  Include a leading newline or heading in the appended content to keep the
  document readable.

## Security

- Do not save credentials, tokens, passwords, or other secrets into memory
  files. If the user asks to memorize content that contains secrets, strip or
  mask them first and warn the user.
- Validate that the `-o` filename does not contain path traversal sequences
  (`../`). The script writes into the bank directory; the filename should be a
  plain name, not a relative path.
- Memory files are stored in the user's home directory with default filesystem
  permissions. They are not encrypted.
