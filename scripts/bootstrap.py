#!/usr/bin/env python3

def main():
    print("jee-agentic-dev bootstrap")
    print()
    print("For a brand-new project, do PROJECT INCEPTION first.")
    print("The orchestrator should create/update:")
    print("  - docs/PROJECT.md")
    print("  - docs/architecture/SYSTEM.md")
    print("  - .ai/project.json")
    print("  - a dependency-aware proposed backlog")
    print()
    print("Validate operational project configuration:")
    print("  python scripts/agentctl.py project validate")
    print()
    print("Only after .ai/project.json is INCEPTION_READY:")
    print('  python scripts/agentctl.py task create FOUNDATION-001 "First implementation task"')
    print("  python scripts/agentctl.py git prepare FOUNDATION-001")
    print("  python scripts/agentctl.py task advance FOUNDATION-001")


if __name__ == "__main__":
    main()
