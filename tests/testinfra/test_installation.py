"""
Role tests
"""
import pytest

# To run all the tests on given docker images:
pytestmark = pytest.mark.docker_images(
    'infopen/ubuntu-trusty-ssh:0.1.0',
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
