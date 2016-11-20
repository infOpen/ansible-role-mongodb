"""
Role tests
"""
import pytest

# To run all the tests on given docker images:
pytestmark = pytest.mark.docker_images(
    'infopen/ubuntu-xenial-ssh-py27:0.2.0'
)


def test_community_repository_file(SystemInfo, File):
    """
    Test community repository file permissions
    """

    os_distribution = SystemInfo.distribution

    if os_distribution == 'ubuntu':
        repo_file_name = '/etc/apt/sources.list.d/mongodb-community.list'

    repo_file = File(repo_file_name)

    assert repo_file.exists
    assert repo_file.is_file
    assert repo_file.user == 'root'
    assert repo_file.group == 'root'
    assert repo_file.mode == 0o644


def test_ubuntu_community_repository_file_content(SystemInfo, File):
    """
    Test community repository file content on Ubuntu distributions
    """

    if (SystemInfo.distribution != 'ubuntu'):
        pytest.skip('Not apply to %s' % SystemInfo.distribution)

    repo_file = File('/etc/apt/sources.list.d/mongodb-community.list')

    expected_content = (
        'deb http://repo.mongodb.org/apt/{distribution} '
        '{release}/mongodb-org/3.2 multiverse'
    ).format(
        distribution=SystemInfo.distribution,
        release=SystemInfo.codename
    )

    assert repo_file.contains(expected_content)


def test_ubuntu_community_packages(SystemInfo, Package):
    """
    Test community packages on Ubuntu distributions
    """

    if (SystemInfo.distribution != 'ubuntu'):
        pytest.skip('Not apply to %s' % SystemInfo.distribution)

    packages = [
        'mongodb-org',
        'mongodb-org-server',
        'mongodb-org-mongos',
        'mongodb-org-shell',
        'mongodb-org-tools',
    ]

    for package in packages:
        assert Package(package).is_installed


def test_default_instance_service(Command, SystemInfo, Service):
    """
    Test default instance service disabled on Ubuntu distributions
    """

    if SystemInfo.distribution != 'ubuntu':
        pytest.skip('Not apply to %s' % SystemInfo.distribution)

    assert Service('mongod').is_enabled is False

    if SystemInfo.codename == 'trusty':
        # On my Trusty service test, return code is 0 when service stopped
        assert 'mongod stop/waiting' in Command('service mongod status').stdout
    else:
        assert Service('mongod').is_running is False


def test_configuration_directory(SystemInfo, File):
    """
    Test configuration directory management
    """

    if (SystemInfo.distribution != 'ubuntu'):
        pytest.skip('Not apply to %s' % SystemInfo.distribution)

    config_dir = File('/etc/mongodb')
    assert config_dir.exists
    assert config_dir.is_directory
    assert config_dir.user == 'root'
    assert config_dir.group == 'root'
    assert config_dir.mode == 0o750


def test_configuration_files(SystemInfo, File):
    """
    Test configuration files management
    """

    if (SystemInfo.distribution != 'ubuntu'):
        pytest.skip('Not apply to %s' % SystemInfo.distribution)

    config_files = [
        '/etc/mongodb/mongod_27017.conf',
        '/etc/mongodb/mongos_27018.conf'
    ]

    for current_file in config_files:
        config_file = File(current_file)
        assert config_file.exists
        assert config_file.is_file
        assert config_file.user == 'root'
        assert config_file.group == 'root'
        assert config_file.mode == 0o400


def test_instance_user(User):
    """
    Test dedicated instance user
    """

    user = User('bar')

    assert user.exists
    assert user.group == 'bar'
    assert 'mongodb' in user.groups
    assert user.home == '/home/bar'
    assert user.shell == '/bin/false'


def test_data_directories(SystemInfo, File):
    """
    Test data directory management
    """

    data_directories = [
        {'path': '/var/lib/mongodb/foo', 'user': 'mongodb'},
        {'path': '/var/lib/mongodb/bar', 'user': 'bar'},
    ]

    for current_directory in data_directories:
        data_directory = File(current_directory['path'])
        assert data_directory.exists
        assert data_directory.is_directory
        assert data_directory.user == current_directory['user']
        assert data_directory.group == current_directory['user']
        assert data_directory.mode == 0o750
