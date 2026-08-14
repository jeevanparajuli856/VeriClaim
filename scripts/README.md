# Agent control scripts

`agentctl.py` is the public interface. Other scripts are implementation details.

```bash
python scripts/agentctl.py --help
python scripts/agentctl.py bootstrap
python scripts/agentctl.py project validate
python scripts/agentctl.py task create AUTH-001 "User authentication"
python scripts/agentctl.py git prepare AUTH-001
python scripts/agentctl.py task advance AUTH-001
python scripts/agentctl.py task validate AUTH-001
python scripts/agentctl.py worktree create AUTH-001 backend
python scripts/agentctl.py worktree create AUTH-001 frontend
python scripts/agentctl.py scope check AUTH-001 backend
python scripts/agentctl.py verify AUTH-001
```

Normal lifecycle progression uses `task advance`; `task status --force` is reserved for recovery/administrative correction.
