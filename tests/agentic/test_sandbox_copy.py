def test_agentic_sandbox_copy_excludes_large_ignored_task_artifacts(repo):
    assert not list((repo / "contracts").rglob(".offline"))
    assert not (repo / ".ai/cache").exists()
