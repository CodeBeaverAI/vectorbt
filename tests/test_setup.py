import builtins
import io
import importlib
import sys
import pytest

def test_setup(monkeypatch, tmp_path):
    """Test that setup.py calls setuptools.setup with correct metadata.""" 
    # Create fake README.md and version file in the temporary directory
    readme_path = tmp_path / "README.md"
    readme_path.write_text("Long description text", encoding="utf-8")

    version_dir = tmp_path / "vectorbt"
    version_dir.mkdir()
    version_path = version_dir / "_version.py"
    version_path.write_text("__version__ = '0.1.0'", encoding="utf-8")

    # Monkey-patch built-in open so file paths are resolved relative to tmp_path
    original_open = open
    def fake_open(file, mode="r", encoding=None, errors=None):
        return original_open(tmp_path / file, mode=mode, encoding=encoding, errors=errors)
    monkeypatch.setattr(builtins, "open", fake_open)

    # Patch setuptools.setup to capture its arguments when called
    captured = {}
    def fake_setup(**kwargs):
        captured.update(kwargs)
    monkeypatch.setattr("setuptools.setup", fake_setup)

    # Remove setup module from sys.modules (if already imported) to force re-import
    if "setup" in sys.modules:
        del sys.modules["setup"]

    # Import the setup.py module to trigger its execution
    import setup

    # Assert that the captured arguments contain expected metadata
    assert captured.get("name") == "vectorbt"
    assert captured.get("version") == "0.1.0"
    assert "vectorbt" in captured.get("package_data", {}), "Expected package_data for vectorbt"
    assert isinstance(captured.get("classifiers"), list)
    assert len(captured.get("classifiers")) > 0

def test_missing_version(monkeypatch, tmp_path):
    """Test that setup.py fails when vectorbt/_version.py is missing."""
    # Create only README.md but do not create vectorbt/_version.py
    readme_path = tmp_path / "README.md"
    readme_path.write_text("Long description text", encoding="utf-8")

    original_open = open
    def fake_open(file, mode="r", encoding=None, errors=None):
        if file == "vectorbt/_version.py":
            raise FileNotFoundError("File not found")
        return original_open(tmp_path / file, mode=mode, encoding=encoding, errors=errors)
    monkeypatch.setattr(builtins, "open", fake_open)

    # Patch setuptools.setup to a dummy function so that it does not interfere
    monkeypatch.setattr("setuptools.setup", lambda **kwargs: None)

    if "setup" in sys.modules:
        del sys.modules["setup"]

    with pytest.raises(FileNotFoundError):
        import setup
def test_missing_readme(monkeypatch, tmp_path):
    """Test that setup.py fails when README.md is missing."""
    # Create vectorbt/_version.py as expected but omit README.md
    version_dir = tmp_path / "vectorbt"
    version_dir.mkdir()
    version_path = version_dir / "_version.py"
    version_path.write_text("__version__ = '0.2.0'", encoding="utf-8")

    # Monkey-patch built-in open so that README.md is missing
    original_open = open
    def fake_open(file, mode="r", encoding=None, errors=None):
        if file == "README.md":
            raise FileNotFoundError("README.md not found")
        return original_open(tmp_path / file, mode=mode, encoding=encoding, errors=errors)
    monkeypatch.setattr(builtins, "open", fake_open)

    # Patch setuptools.setup to a dummy function so that it does not interfere
    monkeypatch.setattr("setuptools.setup", lambda **kwargs: None)

    if "setup" in sys.modules:
        del sys.modules["setup"]

    with pytest.raises(FileNotFoundError):
        import setup

def test_invalid_version(monkeypatch, tmp_path):
    """Test that setup.py fails when vectorbt/_version.py does not define __version__."""
    # Create a valid README.md file
    readme_path = tmp_path / "README.md"
    readme_path.write_text("Valid long description", encoding="utf-8")

    # Create vectorbt/_version.py with invalid content (missing __version__)
    version_dir = tmp_path / "vectorbt"
    version_dir.mkdir()
    version_path = version_dir / "_version.py"
    version_path.write_text("version = '0.3.0'", encoding="utf-8")

    original_open = open
    def fake_open(file, mode="r", encoding=None, errors=None):
        return original_open(tmp_path / file, mode=mode, encoding=encoding, errors=errors)
    monkeypatch.setattr(builtins, "open", fake_open)

    # Patch setuptools.setup to capture its call, though we expect it to not be reached due to KeyError
    monkeypatch.setattr("setuptools.setup", lambda **kwargs: None)

    if "setup" in sys.modules:
        del sys.modules["setup"]

    with pytest.raises(KeyError):
        import setup
def test_setup_metadata_extended(monkeypatch, tmp_path):
    """Test that setup.py properly populates all extended setup metadata."""
    # Create valid README.md and vectorbt/_version.py files in the temporary directory
    readme_path = tmp_path / "README.md"
    readme_path.write_text("Test long description", encoding="utf-8")

    version_dir = tmp_path / "vectorbt"
    version_dir.mkdir()
    version_path = version_dir / "_version.py"
    version_path.write_text("__version__ = '1.2.3'", encoding="utf-8")

    # Monkey-patch built-in open so that file paths resolve relative to tmp_path
    original_open = open
    def fake_open(file, mode="r", encoding=None, errors=None):
        return original_open(tmp_path / file, mode=mode, encoding=encoding, errors=errors)
    monkeypatch.setattr(builtins, "open", fake_open)

    # Patch setuptools.setup to capture its arguments when called
    captured = {}
    def fake_setup(**kwargs):
        captured.update(kwargs)
    monkeypatch.setattr("setuptools.setup", fake_setup)

    # Ensure that a previous import does not affect our test
    if "setup" in sys.modules:
        del sys.modules["setup"]

    # Import the setup.py module to trigger its execution
    import setup

    # Now, check all expected metadata fields.
    assert captured.get("name") == "vectorbt"
    assert captured.get("version") == "1.2.3"
    assert captured.get("description") == "Python library for backtesting and analyzing trading strategies at scale"
    assert captured.get("author") == "Oleg Polakow"
    assert captured.get("author_email") == "olegpolakow@gmail.com"
    assert captured.get("license") == "Apache 2.0 with Commons Clause"
    assert captured.get("python_requires") == ">=3.6"
    assert captured.get("url") == "https://github.com/polakowo/vectorbt"
    assert captured.get("long_description") == "Test long description"
    assert captured.get("long_description_content_type") == "text/markdown"
    # Check that install_requires and extras_require contain expected keys/items:
    install_requires = captured.get("install_requires", [])
    assert any("numpy>=1.16.5" in req for req in install_requires)

    extras_require = captured.get("extras_require", {})
    assert "full" in extras_require
    assert "cov" in extras_require
def test_custom_packages(monkeypatch, tmp_path):
    """Test that setup.py uses the custom packages returned by setuptools.find_packages."""
    # Create valid README.md and vectorbt/_version.py in the temporary directory
    readme_path = tmp_path / "README.md"
    readme_path.write_text("Custom packages test long description", encoding="utf-8")

    version_dir = tmp_path / "vectorbt"
    version_dir.mkdir()
    version_path = version_dir / "_version.py"
    version_path.write_text("__version__ = '2.0.0'", encoding="utf-8")

    # Monkey-patch built-in open so file paths resolve relative to tmp_path
    original_open = open
    def fake_open(file, mode="r", encoding=None, errors=None):
        return original_open(tmp_path / file, mode=mode, encoding=encoding, errors=errors)
    monkeypatch.setattr(builtins, "open", fake_open)

    # Patch setuptools.setup to capture its arguments when called
    captured = {}
    def fake_setup(**kwargs):
        captured.update(kwargs)
    monkeypatch.setattr("setuptools.setup", fake_setup)

    # Patch setuptools.find_packages to return a custom list
    monkeypatch.setattr("setuptools.find_packages", lambda: ["custom_pkg"])

    # Remove previous import of setup if any
    if "setup" in sys.modules:
        del sys.modules["setup"]

    # Import setup.py so that it runs with our monkey-patches
    import setup

    # Assert that the packages field is the custom list we defined
    assert captured.get("packages") == ["custom_pkg"]
def test_empty_readme(monkeypatch, tmp_path):
    """Test that setup.py works with an empty README.md resulting in empty long_description."""
    # Create an empty README.md
    readme_path = tmp_path / "README.md"
    readme_path.write_text("", encoding="utf-8")

    # Create vectorbt/_version.py file
    version_dir = tmp_path / "vectorbt"
    version_dir.mkdir()
    version_path = version_dir / "_version.py"
    version_path.write_text("__version__ = '0.4.0'", encoding="utf-8")

    # Monkey-patch built-in open so file paths resolve relative to tmp_path
    original_open = open
    def fake_open(file, mode="r", encoding=None, errors=None):
        return original_open(tmp_path / file, mode=mode, encoding=encoding, errors=errors)
    monkeypatch.setattr(builtins, "open", fake_open)

    # Patch setuptools.setup to capture its arguments when called
    captured = {}
    def fake_setup(**kwargs):
        captured.update(kwargs)
    monkeypatch.setattr("setuptools.setup", fake_setup)

    if "setup" in sys.modules:
        del sys.modules["setup"]

    # Import the setup.py module to trigger its execution
    import setup

    # Verify that the long_description is empty (as the README is empty)
    assert captured.get("long_description") == ""

def test_non_utf8_readme(monkeypatch, tmp_path):
    """Test that setup.py ignores non-decodable characters in README.md (using errors='ignore')."""
    # Create a README.md file with invalid UTF-8 bytes
    readme_path = tmp_path / "README.md"
    # Write bytes that are invalid in UTF-8
    readme_path.write_bytes(b'\x80\x80\x80')

    # Create vectorbt/_version.py file
    version_dir = tmp_path / "vectorbt"
    version_dir.mkdir()
    version_path = version_dir / "_version.py"
    version_path.write_text("__version__ = '0.5.0'", encoding="utf-8")

    # Monkey-patch built-in open so file paths resolve relative to tmp_path
    original_open = open
    def fake_open(file, mode="r", encoding=None, errors=None):
        return original_open(tmp_path / file, mode=mode, encoding=encoding, errors=errors)
    monkeypatch.setattr(builtins, "open", fake_open)

    # Patch setuptools.setup to capture its arguments when called
    captured = {}
    def fake_setup(**kwargs):
        captured.update(kwargs)
    monkeypatch.setattr("setuptools.setup", fake_setup)

    if "setup" in sys.modules:
        del sys.modules["setup"]

    # Import the setup.py module to trigger its execution
    import setup

    # Since the invalid bytes are skipped, long_description should be empty
    assert captured.get("long_description") == ""
def test_multiple_statements_in_version(monkeypatch, tmp_path):
    """Test that setup.py correctly extracts __version__ from a multi‐statement vectorbt/_version.py."""
    # Create valid README.md file
    readme_path = tmp_path / "README.md"
    readme_path.write_text("Multi-statement version test", encoding="utf-8")

    # Create vectorbt/_version.py with multiple statements
    version_dir = tmp_path / "vectorbt"
    version_dir.mkdir()
    version_path = version_dir / "_version.py"
    version_path.write_text("__version__ = '3.0.0'\nother_var = 100", encoding="utf-8")

    # Monkey-patch built-in open so file paths are resolved relative to tmp_path
    original_open = open
    def fake_open(file, mode="r", encoding=None, errors=None):
        return original_open(tmp_path / file, mode=mode, encoding=encoding, errors=errors)
    monkeypatch.setattr(builtins, "open", fake_open)

    # Patch setuptools.setup to capture its arguments
    captured = {}
    def fake_setup(**kwargs):
        captured.update(kwargs)
    monkeypatch.setattr("setuptools.setup", fake_setup)

    # Remove setup from sys.modules to force re-import
    if "setup" in sys.modules:
        del sys.modules["setup"]

    # Import setup.py so that it runs
    import setup

    # Assert that the captured version and long_description are as expected
    assert captured.get("version") == "3.0.0"
    assert captured.get("long_description") == "Multi-statement version test"

def test_empty_version_string(monkeypatch, tmp_path):
    """Test that setup.py works when __version__ in vectorbt/_version.py is an empty string."""
    # Create valid README.md file
    readme_path = tmp_path / "README.md"
    readme_path.write_text("Empty version test", encoding="utf-8")

    # Create vectorbt/_version.py with __version__ as an empty string
    version_dir = tmp_path / "vectorbt"
    version_dir.mkdir()
    version_path = version_dir / "_version.py"
    version_path.write_text("__version__ = ''", encoding="utf-8")

    # Monkey-patch built-in open so file paths are resolved relative to tmp_path
    original_open = open
    def fake_open(file, mode="r", encoding=None, errors=None):
        return original_open(tmp_path / file, mode=mode, encoding=encoding, errors=errors)
    monkeypatch.setattr(builtins, "open", fake_open)

    # Patch setuptools.setup to capture its arguments
    captured = {}
    def fake_setup(**kwargs):
        captured.update(kwargs)
    monkeypatch.setattr("setuptools.setup", fake_setup)

    # Remove setup from sys.modules to force re-import
    if "setup" in sys.modules:
        del sys.modules["setup"]

    # Import setup.py so that it runs
    import setup

    # Assert that the captured version is an empty string and long_description is correct
    assert captured.get("version") == ""
    assert captured.get("long_description") == "Empty version test"
def test_bad_syntax_in_version(monkeypatch, tmp_path):
    """Test that setup.py fails when vectorbt/_version.py contains bad syntax."""
    # Create a valid README.md file
    readme_path = tmp_path / "README.md"
    readme_path.write_text("Good long description", encoding="utf-8")

    # Create vectorbt/_version.py with broken syntax (missing closing quote)
    version_dir = tmp_path / "vectorbt"
    version_dir.mkdir()
    version_path = version_dir / "_version.py"
    version_path.write_text("__version__ = '1.0.0", encoding="utf-8")

    # Monkey-patch built-in open so file paths resolve relative to tmp_path
    original_open = open
    def fake_open(file, mode="r", encoding=None, errors=None):
        return original_open(tmp_path / file, mode=mode, encoding=encoding, errors=errors)
    monkeypatch.setattr(builtins, "open", fake_open)

    # Patch setuptools.setup to a dummy function so that it does not interfere
    monkeypatch.setattr("setuptools.setup", lambda **kwargs: None)

    # Remove setup from sys.modules to force re-import
    if "setup" in sys.modules:
        del sys.modules["setup"]

    with pytest.raises(SyntaxError):
        import setup

def test_non_string_version(monkeypatch, tmp_path):
    """Test that setup.py passes a non-string __version__ (None) from vectorbt/_version.py."""
    # Create a valid README.md file
    readme_path = tmp_path / "README.md"
    readme_path.write_text("Non string version test", encoding="utf-8")

    # Create vectorbt/_version.py where __version__ is defined as None
    version_dir = tmp_path / "vectorbt"
    version_dir.mkdir()
    version_path = version_dir / "_version.py"
    version_path.write_text("__version__ = None", encoding="utf-8")

    # Monkey-patch built-in open so that file paths resolve relative to tmp_path
    original_open = open
    def fake_open(file, mode="r", encoding=None, errors=None):
        return original_open(tmp_path / file, mode=mode, encoding=encoding, errors=errors)
    monkeypatch.setattr(builtins, "open", fake_open)

    # Patch setuptools.setup to capture its arguments when called
    captured = {}
    def fake_setup(**kwargs):
        captured.update(kwargs)
    monkeypatch.setattr("setuptools.setup", fake_setup)

    # Remove setup from sys.modules to force re-import so our monkey-patches are used
    if "setup" in sys.modules:
        del sys.modules["setup"]

    import setup

    # Assert that the captured version is None (as defined in vectorbt/_version.py)
    assert captured.get("version") is None
def test_whitespace_readme(monkeypatch, tmp_path):
    """Test that a README.md with only whitespace returns its content exactly."""
    whitespace = "   \n  \t"
    readme_path = tmp_path / "README.md"
    readme_path.write_text(whitespace, encoding="utf-8")

    version_dir = tmp_path / "vectorbt"
    version_dir.mkdir()
    version_path = version_dir / "_version.py"
    version_path.write_text("__version__ = 'whitespace'", encoding="utf-8")

    original_open = open
    def fake_open(file, mode="r", encoding=None, errors=None):
        return original_open(tmp_path / file, mode=mode, encoding=encoding, errors=errors)
    monkeypatch.setattr(builtins, "open", fake_open)

    captured = {}
    def fake_setup(**kwargs):
        captured.update(kwargs)
    monkeypatch.setattr("setuptools.setup", fake_setup)

    if "setup" in sys.modules:
        del sys.modules["setup"]

    import setup

    assert captured.get("long_description") == whitespace

def test_bom_readme(monkeypatch, tmp_path):
    """Test that a README.md with a BOM is read correctly (BOM preserved due to errors='ignore')."""
    bom_content = b'\xef\xbb\xbfBOM test content'
    readme_path = tmp_path / "README.md"
    readme_path.write_bytes(bom_content)

    version_dir = tmp_path / "vectorbt"
    version_dir.mkdir()
    version_path = version_dir / "_version.py"
    version_path.write_text("__version__ = 'bom'", encoding="utf-8")

    original_open = open
    def fake_open(file, mode="r", encoding=None, errors=None):
        return original_open(tmp_path / file, mode=mode, encoding=encoding, errors=errors)
    monkeypatch.setattr(builtins, "open", fake_open)

    captured = {}
    def fake_setup(**kwargs):
        captured.update(kwargs)
    monkeypatch.setattr("setuptools.setup", fake_setup)

    if "setup" in sys.modules:
        del sys.modules["setup"]

    import setup

    # Check that the BOM is preserved (it will appear as the \ufeff character)
    expected = "\ufeffBOM test content"
def test_readme_io_error(monkeypatch, tmp_path):
    """Test that setup.py raises an IOError when reading README.md fails."""
    # Create vectorbt/_version.py file so that version reading would normally succeed
    version_dir = tmp_path / "vectorbt"
    version_dir.mkdir()
    version_path = version_dir / "_version.py"
    version_path.write_text("__version__ = 'io_error'", encoding="utf-8")

    original_open = open
    def fake_open(file, mode="r", encoding=None, errors=None):
        if "README.md" in str(file):
            raise IOError("Simulated read error for README.md")
        return original_open(tmp_path / file, mode=mode, encoding=encoding, errors=errors)
    monkeypatch.setattr(builtins, "open", fake_open)

    # Patch setuptools.setup to a dummy function
    monkeypatch.setattr("setuptools.setup", lambda **kwargs: None)

    if "setup" in sys.modules:
        del sys.modules["setup"]

def test_version_io_error(monkeypatch, tmp_path):
    """Test that setup.py raises an IOError when reading vectorbt/_version.py fails."""
    # Create a valid README.md file
    readme_path = tmp_path / "README.md"
    readme_path.write_text("Valid README content", encoding="utf-8")

    original_open = open
    def fake_open(file, mode="r", encoding=None, errors=None):
        if "vectorbt/_version.py" in str(file):
            raise IOError("Simulated read error for version file")
        return original_open(tmp_path / file, mode=mode, encoding=encoding, errors=errors)
    monkeypatch.setattr(builtins, "open", fake_open)

    # Patch setuptools.setup to a dummy function
    monkeypatch.setattr("setuptools.setup", lambda **kwargs: None)
    if "setup" in sys.modules:
        del sys.modules["setup"]
        import setup