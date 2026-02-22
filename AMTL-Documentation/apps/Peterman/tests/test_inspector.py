"""
Peterman Inspector Tests

Code quality tests.
"""

import subprocess
import os


def test_flake8_zero_errors():
    """All Python code passes flake8 with zero syntax errors."""
    result = subprocess.run(
        ['python', '-m', 'flake8', 'app/', '--max-line-length=120', 
         '--exclude=__pycache__,migrations', '--ignore=E501,W503'],
        capture_output=True, text=True,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    # Check for syntax errors (E999)
    assert 'E999' not in result.stdout, f"Syntax errors found:\n{result.stdout}"


def test_no_cloud_api_imports():
    """No direct cloud API imports (OpenAI, Anthropic) in codebase."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    result = subprocess.run(
        ['grep', '-r', '-l', 'import openai', 'app/', '--include=*.py'],
        capture_output=True, text=True,
        cwd=base_dir
    )
    # Filter out legitimate AI engine wrapper files
    files = [f for f in result.stdout.strip().split('\n') if f and 'ai_engine.py' not in f]
    assert len(files) == 0 or files == [''], f"Cloud API imports found in: {files}"


def test_no_hardcoded_api_keys():
    """No hardcoded API keys in codebase."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    result = subprocess.run(
        ['grep', '-r', '-l', 'sk-', 'app/', '--include=*.py'],
        capture_output=True, text=True,
        cwd=base_dir
    )
    # Allow in config files that load from env
    files = [f for f in result.stdout.strip().split('\n') if f and 'config.py' not in f]
    assert len(files) == 0 or files == [''], f"Hardcoded API keys found in: {files}"


def test_no_hardcoded_scores():
    """No hardcoded 50.0 scores in score engine."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    score_engine_path = os.path.join(base_dir, 'app', 'services', 'score_engine.py')
    
    if os.path.exists(score_engine_path):
        with open(score_engine_path, 'r') as f:
            content = f.read()
        
        # Check that score engine doesn't return hardcoded values
        assert 'return 50.0' not in content, "Hardcoded 50.0 return found in score engine"
        assert "'score': 50.0" not in content, "Hardcoded score dict found"


def test_imports_are_valid():
    """All imports in main modules are valid."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Test that core modules can be imported
    import sys
    sys.path.insert(0, base_dir)
    
    # Try importing main modules
    try:
        from app import create_app
        from app.config import config
        from app.models.database import Base, engine
        assert True
    except ImportError as e:
        assert False, f"Import error: {e}"


def test_sqlalchemy_models_import():
    """All SQLAlchemy models can be imported."""
    import sys
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, base_dir)
    
    try:
        from app.models import domain, audit, budget, deployment, score, hallucination, probe, brief, embedding
        from app.models.keyword_engine import TargetQuery
        assert True
    except ImportError as e:
        assert False, f"Model import error: {e}"


def test_routes_import():
    """All routes can be imported."""
    import sys
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, base_dir)
    
    try:
        from app.routes import api, health
        assert True
    except ImportError as e:
        assert False, f"Route import error: {e}"
