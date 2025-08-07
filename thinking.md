# Thinking Notes - GPT-OSS Tool Calling Implementation

## Overview
The task is to implement proper OpenAI function calling functionality in the existing TUI application while preserving the working AI thinking panel feature.

## Key Documentation Analysis

### 1. GPT-OSS README.md
- **Models**: gpt-oss-120b (117B params, 5.1B active) and gpt-oss-20b (21B params, 3.6B active)
- **Critical**: Models were trained using harmony response format and MUST use this format
- **Tool Support**: Native function calling, browser tool, python execution, structured outputs
- **Quantization**: Native MXFP4 for MoE layer, allows single H100 GPU operation

### 2. Ollama Integration (docs/run-locally-ollama.md)
- **API Compatibility**: Ollama exposes Chat Completions-compatible API at `http://localhost:11434/v1`
- **OpenAI SDK**: Can use OpenAI SDK with `base_url="http://localhost:11434/v1"` and dummy api_key
- **Function Calling Example**:
```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather in a given city",
        "parameters": {
            "type": "object", 
            "properties": {"city": {"type": "string"}},
            "required": ["city"]
        }
    }
}]
response = client.chat.completions.create(model="gpt-oss:20b", messages=[...], tools=tools)
```
- **Important**: Chain-of-thought reasoning requires returning reasoning back to subsequent calls

### 3. Harmony Format (harmony/README.md & docs/python.md)
- **Purpose**: Response format for gpt-oss models defining conversation structures and tool calls
- **Key Point**: Format is designed to mimic OpenAI Responses API
- **Critical**: gpt-oss should NOT be used without harmony format
- **Components**: Multiple channels (analysis, commentary, final), tool namespaces, structured outputs
- **Python Package**: `openai-harmony` available via pip

### 4. Current Implementation Analysis

#### Working Components:
- **Thinking Panel**: Works via `/api/generate` endpoint, extracts "thinking" field from response
- **TUI Structure**: Clean 2-panel layout (Chat + Thinking) using Textual framework
- **Tools**: Executable command-line tools (glop, grep, read, search, readymyfiles, filewrite)

#### Broken Components:
- **Tool Calling**: Multiple failed attempts using various approaches
- **Integration Issue**: Can't combine thinking panel with proper function calling

#### Code Structure:
- `gpt_oss_tui.py`: Main TUI app (~1082 lines)
- `chat_panel.py`: Standalone chat panel (193 lines) 
- `thinking_panel.py`: Thinking display panel (98 lines)
- `gptoss_tools.py`: Custom tool wrapper classes (280 lines)

## Problem Analysis

### Core Issue
The application needs TWO different API calls:
1. **Thinking Panel**: Uses `/api/generate` endpoint, returns `{"thinking": "...", "response": "..."}`
2. **Tool Calling**: Uses `/v1/chat/completions` endpoint with OpenAI SDK format

### Current State
- Thinking panel works perfectly with `/api/generate`
- Tool calling attempts break the thinking panel
- User frustrated by repeated failures to add functionality without breaking existing features

### Previous Failed Approaches
1. **Complex Harmony Integration**: Attempted to use openai-harmony package directly
2. **Async Implementation**: Tried async/await patterns that caused UI blocking
3. **Fallback Attempts**: Multiple reverts due to breaking thinking functionality

## Solution Strategy

### Approach: Dual Endpoint Strategy
1. **Preserve Thinking**: Keep using `/api/generate` for thinking panel
2. **Add Tools**: Use `/v1/chat/completions` for function calling when needed
3. **Coordination**: Make parallel calls or sequential calls to both endpoints

### Implementation Plan
1. **Detect Tool Needs**: Check if user message requires tools
2. **Dual API Calls**:
   - Call `/api/generate` to get thinking content
   - Call `/v1/chat/completions` with tools to get function calls
3. **Combine Results**: Show thinking in thinking panel, execute tools, show results in chat

### Key Requirements
- Use OpenAI SDK with `base_url="http://localhost:11434/v1"`
- Define tools in standard OpenAI function format
- Handle `response.choices[0].message.tool_calls` 
- Execute tool functions and return results
- Preserve existing thinking panel functionality

### Tool Schema
Based on existing tools, need functions for:
- `file_operations`: find, read, grep, search, analyze operations
- `file_writer`: create, edit, backup, templates operations

### Critical Implementation Notes
- **DO NOT** break existing thinking panel functionality
- **DO NOT** modify working `/api/generate` calls
- **ADD** tool calling as additional functionality
- **TEST** that both thinking and tool calling work together
- **PRESERVE** the working 2-panel UI layout

## Next Steps
1. Implement `_call_ollama_with_tools()` method using OpenAI SDK
2. Add tool detection logic to determine when to use tools
3. Create parallel calling strategy for thinking + tools
4. Test integration without breaking existing functionality
5. Handle tool execution and result display

## Success Criteria
- Thinking panel continues to work exactly as before
- Tool calling works for appropriate user queries
- AI can suggest and execute tool commands
- Results display properly in chat panel
- No breaking changes to existing UI or functionality