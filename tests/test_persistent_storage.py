import os
import shutil
import tempfile

from persistent_data_manager import PersistentDataManager


def test_persistent_manager_uses_override(tmp_path, monkeypatch):
    # Simulate Render environment
    monkeypatch.setenv('RENDER', 'true')
    # Provide an override directory
    custom_dir = tmp_path / "render_data"
    monkeypatch.setenv('RENDER_PERSISTENT_DIR', str(custom_dir))

    # Ensure dir does not exist before init
    assert not custom_dir.exists()

    manager = PersistentDataManager()
    db_path = manager.get_database_path()

    # The DB path should be under the override directory
    assert str(custom_dir) in db_path
    assert custom_dir.exists()
    # Backup dir should have been created
    backup_dir = os.environ.get('BACKUP_DIR')
    assert backup_dir is not None
    assert os.path.isdir(backup_dir)

    # Clean up
    shutil.rmtree(str(custom_dir))
