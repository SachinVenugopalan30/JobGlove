# groq-ollama-integration Branch Summary

## Overview

This branch standardizes LLM output consistency across all 5 providers (OpenAI, Gemini, Claude, Groq, Ollama) and fixes several bugs encountered during testing.

## Bug Fixes (Pre-Standardization)

- **Docker build failure**: `.gitignore` had `lib/` which matched `frontend/src/lib/` — changed to `/lib/` so only root-level matches. Staged the missing frontend lib files.
- **Gemini SDK migration**: Migrated from deprecated `google-generativeai` to `google-genai` package. Updated all `GeminiProvider` methods to use the new client-based API.
- **Insufficient credits error handling**: Added `InsufficientCreditsError` with pattern detection across all cloud providers. Returns HTTP 402 to frontend with a user-friendly message.
- **LaTeX empty list crash**: `_format_education`, `_format_experience`, and `_format_projects` could emit empty `\begin{itemize}...\end{itemize}` blocks causing `pdflatex` compilation failure. Fixed to return empty string when no entries match.
- **pdflatex false failure**: Non-zero exit code treated as error even when PDF was successfully generated. Now checks for PDF existence before raising.

## LLM Output Standardization

- **Shared system prompt**: Extracted `SCORE_TAILOR_SYSTEM_PROMPT` constant on the `AIProvider` base class. Applied to all 5 providers including Claude (`system=`) and Gemini (`system_instruction=`).
- **JSON mode enforcement**: All providers now explicitly request JSON output through their respective mechanisms (`response_format`, `response_mime_type`, `format="json"`, system prompt).
- **Lower temperature**: `score_and_tailor_resume` uses temperature 0.2 (down from 0.7) across all providers for more deterministic structured output. Creative methods (`tailor_resume`, `generate`) remain at 0.7.
- **`tailored_resume_lines` array**: Prompt now requests resume content as an array of strings instead of a single multi-line string. Parser normalizes back to a string for backward compatibility with downstream consumers.
- **JSON repair fallback**: `_parse_json_response` now attempts to repair common LLM JSON issues (trailing commas, truncated responses with unclosed braces) before failing.
- **Base class response validation**: Moved `_validate_score_response` from `ClaudeProvider` to `AIProvider`. All providers now validate required keys (`original_score`, `tailored_resume`, `tailored_score`). Renamed exception to `IncompleteResponseError` with backward-compatible alias.
- **Explicit prompt constraints**: Added section ordering requirement and instruction not to add phantom sections.

## Known Issues

- Several pre-existing test failures in `test_tailor_routes.py`, `test_integration_full_flow.py`, `test_routes.py` (mock setup issues unrelated to this branch).
- LaTeX section formatters (`_format_projects`, `_format_experience`) are brittle — rigid format expectations cause sections to be silently dropped when AI output doesn't match exactly. Needs follow-up work.
