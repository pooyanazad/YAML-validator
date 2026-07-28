import os
import pytest
import tempfile
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent

@pytest.fixture
def clean_file():
    return str(FIXTURES_DIR / "test3_clean.yaml")

@pytest.fixture
def issues_file():
    return str(FIXTURES_DIR / "test1_issues.yaml")

@pytest.fixture
def security_file():
    return str(FIXTURES_DIR / "security_test1.yaml")

@pytest.fixture
def tmp_yaml():
    """Factory fixture to create temporary YAML files."""
    created_files = []
    
    def _make_yaml(content: str) -> str:
        f = tempfile.NamedTemporaryFile(suffix=".yaml", mode="w", delete=False)
        f.write(content)
        f.flush()
        f.close()
        created_files.append(f.name)
        return f.name
        
    yield _make_yaml
    
    for path in created_files:
        try:
            os.unlink(path)
        except OSError:
            pass
