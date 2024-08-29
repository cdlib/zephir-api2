import os
import shutil

import pytest
from app import create_app


@pytest.fixture
def td_tmpdir(request, tmpdir):
    """Copy test data into the temporary directory for tests, if available.

    Note:
        1) Test data is located by convention. Create a directory with the same name as
        the test file (test-file: test_mymodule.py, test-data: test_mymodule/* ) if it exists.

    Args:
        request: Fixture with test case filename, used to find test data.
        tmpdir: Fixture for test case temporary directory generated by pytest.

    Returns:
        Filepath of the test data subdirectory within the temporary directory,
        or the temporary directory itself if the test data directory does not exist.

    """
    # Determine the name of the directory based on the test file name
    td_dirname = os.path.splitext(os.path.basename(request.fspath))[0]
    # Construct the expected path to the test data directory
    td_path = os.path.join(os.path.dirname(request.fspath), td_dirname)
    # Define the target path within the temporary directory
    tmp_td_path = os.path.join(tmpdir, td_dirname)

    try:
        # Attempt to copy the test data directory into the temporary directory
        shutil.copytree(td_path, tmp_td_path)
        # If successful, return the path to the copied test data
        return tmp_td_path
    except FileNotFoundError:
        # If the test data directory does not exist, return the path to the temporary directory
        return tmpdir


@pytest.fixture
def app(td_tmpdir):


    class TestConfig:
        TESTING = True
        LOG_LEVEL = "DEBUG"
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{td_tmpdir}/db.sqlite'
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        
        
    app = create_app(TestConfig)
    yield app


@pytest.fixture
def client(app):
    return app.test_client()