from typing import Dict, Any
import re

# Tool registry to hold node functions
TOOL_REGISTRY = {}

def register_tool(name: str):
    """Decorator to register tools by name"""
    def decorator(func):
        TOOL_REGISTRY[name] = func
        return func
    return decorator


# -------------------------------------------------------------------
#  TOOL 1: extract_functions
#  Extracts function definitions from source code
# -------------------------------------------------------------------
@register_tool("extract_functions")
def extract_functions(code: str, state: Dict[str, Any]) -> Dict[str, Any]:
    functions = re.findall(r"def\\s+([a-zA-Z_][a-zA-Z_0-9]*)", code or "")
    return {
        "functions": functions,
        "num_functions": len(functions)
    }


# -------------------------------------------------------------------
#  TOOL 2: check_complexity
#  Assigns a simple "complexity score" per function
# -------------------------------------------------------------------
@register_tool("check_complexity")
def check_complexity(state: Dict[str, Any]) -> Dict[str, Any]:
    funcs = state.get("functions", [])
    complexities = {f: len(f) + 1 for f in funcs}
    avg = sum(complexities.values()) / max(1, len(funcs))
    return {
        "complexities": complexities,
        "avg_complexity": avg
    }


# -------------------------------------------------------------------
#  TOOL 3: detect_issues
#  Simple static code checks: TODOs, tabs, and long lines
# -------------------------------------------------------------------
@register_tool("detect_issues")
def detect_issues(code: str, state: Dict[str, Any]) -> Dict[str, Any]:
    issues = []

    if "TODO" in (code or ""):
        issues.append("Contains TODO comments")

    if "\\t" in (code or ""):
        issues.append("Tabs found (use spaces!)")

    lines = (code or "").splitlines()
    long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 120]
    if long_lines:
        issues.append(f"Long lines at: {long_lines}")

    return {
        "issues": issues,
        "num_issues": len(issues)
    }


# -------------------------------------------------------------------
#  TOOL 4: suggest_improvements
#  Gives suggestions based on number of issues and complexity level
# -------------------------------------------------------------------
@register_tool("suggest_improvements")
def suggest_improvements(state: Dict[str, Any]) -> Dict[str, Any]:
    suggestions = []

    if state.get("num_issues", 0) > 0:
        suggestions.append("Fix code issues")

    if state.get("avg_complexity", 0) > 8:
        suggestions.append("Refactor complex functions")

    quality_score = max(
        0,
        100 - 10 * state.get("num_issues", 0) - int(state.get("avg_complexity", 0))
    )

    return {
        "suggestions": suggestions,
        "quality_score": quality_score
    }


# -------------------------------------------------------------------
#  TOOL 5: noop (does nothing — for end nodes)
# -------------------------------------------------------------------
@register_tool("noop")
def noop(state: Dict[str, Any]) -> Dict[str, Any]:
    return {}
