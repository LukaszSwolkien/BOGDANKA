#!/usr/bin/env python3
"""
Generate detailed markdown report from test results YAML.
"""

import sys
import yaml
from datetime import datetime
from pathlib import Path


def generate_markdown_report(results_file: Path) -> str:
    """Generate markdown report from test results YAML."""
    
    with results_file.open("r") as f:
        data = yaml.safe_load(f)
    
    lines = []
    
    # Header
    lines.append("# Test Suite Report - BOGDANKA Simulation")
    lines.append("")
    lines.append(f"**Generated:** {datetime.fromisoformat(data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    # Executive Summary
    lines.append("## Executive Summary")
    lines.append("")
    
    passed = data['passed']
    failed = data['failed']
    errors = data['errors']
    total = data['total_tests']
    success_rate = (passed / total * 100) if total > 0 else 0
    
    lines.append(f"- **Total Tests:** {total}")
    lines.append(f"- **✅ Passed:** {passed}")
    lines.append(f"- **❌ Failed:** {failed}")
    lines.append(f"- **⚠️ Errors:** {errors}")
    lines.append(f"- **Success Rate:** {success_rate:.1f}%")
    lines.append("")
    
    # Overall Status
    if passed == total:
        lines.append("🎉 **All tests passed!** The algorithms are ready for PLC implementation.")
    elif success_rate >= 80:
        lines.append("⚠️ **Most tests passed**, but some issues need attention before PLC implementation.")
    else:
        lines.append("❌ **Critical issues detected.** Algorithms need review before PLC implementation.")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Test Results by Priority
    lines.append("## Test Results")
    lines.append("")
    
    # Group by priority
    high_priority = [r for r in data['results'] if r['priority'] == 'HIGH']
    medium_priority = [r for r in data['results'] if r['priority'] == 'MEDIUM']
    
    for priority_name, priority_results in [("High Priority", high_priority), ("Medium Priority", medium_priority)]:
        if not priority_results:
            continue
        
        lines.append(f"### {priority_name}")
        lines.append("")
        
        for result in priority_results:
            status_symbol = "✅" if result['status'] == "PASSED" else "❌" if result['status'] == "FAILED" else "⚠️"
            
            lines.append(f"#### {status_symbol} {result['profile_name']}")
            lines.append("")
            lines.append(f"**Description:** {result['description']}")
            lines.append("")
            lines.append(f"**Status:** {result['status']}")
            lines.append(f"**Duration:** {result['duration_s']:.1f}s")
            lines.append("")
            
            if result['status'] == "ERROR":
                lines.append(f"**Error:** {result['error_message']}")
                lines.append("")
            
            elif result['status'] in ["PASSED", "FAILED"]:
                # Show validation results
                lines.append("**Validation Results:**")
                lines.append("")
                lines.append("| Metric | Expected | Actual | Status | Notes |")
                lines.append("|--------|----------|--------|--------|-------|")
                
                for v in result['validation_results']:
                    status_icon = "✅" if v['passed'] else "❌"
                    expected_str = _format_expected(v['expected'])
                    actual_str = _format_actual(v['actual'])
                    message = v['message'].replace('|', '\\|')  # Escape pipes for markdown
                    
                    lines.append(f"| {v['metric']} | {expected_str} | {actual_str} | {status_icon} | {message} |")
                
                lines.append("")
                
                # Show key metrics
                if result['actual_metrics']:
                    lines.append("<details>")
                    lines.append("<summary><strong>Detailed Metrics</strong></summary>")
                    lines.append("")
                    lines.append("```yaml")
                    lines.append(yaml.dump(result['actual_metrics'], indent=2, default_flow_style=False))
                    lines.append("```")
                    lines.append("")
                    lines.append("</details>")
                    lines.append("")
            
            lines.append("---")
            lines.append("")
    
    # Recommendations
    lines.append("## Recommendations")
    lines.append("")
    
    failed_results = [r for r in data['results'] if r['status'] == 'FAILED']
    error_results = [r for r in data['results'] if r['status'] == 'ERROR']
    
    if not failed_results and not error_results:
        lines.append("✅ **No issues detected.** Algorithms are ready for PLC implementation.")
        lines.append("")
        lines.append("**Next Steps:**")
        lines.append("1. Review pseudocode in `src/algo_pseudokod.md`")
        lines.append("2. Begin PLC implementation")
        lines.append("3. Measure real equipment timing parameters during commissioning")
    else:
        lines.append("### Issues to Address:")
        lines.append("")
        
        for result in failed_results + error_results:
            lines.append(f"- **{result['profile_name']}**:")
            
            if result['status'] == 'ERROR':
                lines.append(f"  - Error: {result['error_message']}")
            else:
                failed_validations = [v for v in result['validation_results'] if not v['passed']]
                for v in failed_validations[:3]:  # Show top 3
                    lines.append(f"  - {v['metric']}: {v['message']}")
            
            lines.append("")
    
    lines.append("---")
    lines.append("")
    
    # Footer
    lines.append("## Test Configuration")
    lines.append("")
    lines.append("- **Test Profiles:** `src/simulation/test_profiles.json`")
    lines.append("- **Pseudocode:** `src/algo_pseudokod.md`")
    lines.append("- **Documentation:** `src/simulation/PODSUMOWANIE_PLAN_SYMULACJI.md`")
    lines.append("")
    
    return "\n".join(lines)


def _format_expected(expected: any) -> str:
    """Format expected value for markdown table."""
    if isinstance(expected, dict):
        parts = []
        if "min" in expected:
            parts.append(f"≥{expected['min']}")
        if "max" in expected:
            parts.append(f"≤{expected['max']}")
        if "target" in expected:
            parts.append(f"(~{expected['target']})")
        return " ".join(parts)
    elif isinstance(expected, list):
        return ", ".join(str(x) for x in expected)
    elif expected is None:
        return "N/A"
    else:
        return str(expected)


def _format_actual(actual: any) -> str:
    """Format actual value for markdown table."""
    if actual is None:
        return "N/A"
    elif isinstance(actual, float):
        return f"{actual:.2f}"
    elif isinstance(actual, list):
        if len(actual) > 3:
            return f"[{len(actual)} values]"
        return ", ".join(str(x) for x in actual)
    else:
        return str(actual)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python generate_report.py <results_json_file>")
        sys.exit(1)
    
    results_file = Path(sys.argv[1])
    
    if not results_file.exists():
        print(f"Error: Results file not found: {results_file}")
        sys.exit(1)
    
    # Generate markdown report
    markdown = generate_markdown_report(results_file)
    
    # Save to file
    output_file = results_file.parent / f"{results_file.stem}_report.md"
    with output_file.open("w") as f:
        f.write(markdown)
    
    print(f"Report generated: {output_file}")
    
    # Also print to stdout
    print("\n" + markdown)


if __name__ == "__main__":
    main()

