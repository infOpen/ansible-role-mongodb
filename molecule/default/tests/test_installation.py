"""
Role tests
"""

import json
import os
import pytest
from testinfra.utils.ansible_runner import AnsibleRunner

testinfra_hosts = AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_repository_file_debian_family(host):
    """
    Test repository file permissions and content on Ubuntu distributions
    """

    if host.system_info.distribution not in ['debian', 'ubuntu']:
        pytest.skip('Not apply to %s' % host.system_info.distribution)

    if host.system_info.distribution == 'debian':
        section_name = 'main'
    else:
        section_name = 'multiverse'

    if 'mongodb-org' in host.check_output('cat /etc/hostname'):
        repo_file_name = '/etc/apt/sources.list.d/mongodb-org.list'
        expected_content = (
            'deb https://repo.mongodb.org/apt/{distribution} '
            '{release}/mongodb-org/4.0 {section_name}'
        ).format(
            distribution=host.system_info.distribution,
            release=host.system_info.codename,
            section_name=section_name
        )
    else:
        repo_file_name = '/etc/apt/sources.list.d/mongodb-enterprise.list'
        expected_content = (
            'deb https://repo.mongodb.com/apt/{distribution} '
            '{release}/mongodb-enterprise/4.0 {section_name}'
        ).format(
            distribution=host.system_info.distribution,
            release=host.system_info.codename,
            section_name=section_name
        )

    repo_file = host.file(repo_file_name)

    assert repo_file.exists
    assert repo_file.is_file
    assert repo_file.user == 'root'
    assert repo_file.group == 'root'
    assert repo_file.mode == 0o644
    assert repo_file.contains(expected_content)


@pytest.mark.parametrize('pattern', [
    'mongodb-{}',
    'mongodb-{}-server',
    'mongodb-{}-mongos',
    'mongodb-{}-shell',
    'mongodb-{}-tools',
])
def test_packages(host, pattern):
    """
    Test packages
    """

    if 'mongodb-org' in host.check_output('cat /etc/hostname'):
        package_name = pattern.format('org')
    else:
        package_name = pattern.format('enterprise')

    assert host.package(package_name).is_installed


def test_pymongo_management(host):
    """
    Test "pymongo" installation with pip
    """

    assert 'version' in host.pip_package.get_packages().get('pymongo')


def test_default_instance_service(host):
    """
    Test default instance service disabled
    """

    assert host.service('mongod').is_enabled is False
    assert host.service('mongod').is_running is False


def test_configuration_directory(host):
    """
    Test configuration directory management
    """

    if host.system_info.distribution in ['debian', 'ubuntu']:
        mongodb_group = 'mongodb'
    else:
        mongodb_group = 'mongod'

    config_dir = host.file('/etc/mongodb')
    assert config_dir.exists
    assert config_dir.is_directory
    assert config_dir.user == 'root'
    assert config_dir.group == mongodb_group
    assert config_dir.mode == 0o750


@pytest.mark.parametrize('path,user', [
    ('/etc/mongodb/mongod_27017.conf', 'mongodb'),
    ('/etc/mongodb/mongod_27017.key', 'mongodb'),
    ('/etc/mongodb/mongod_27018.conf', 'bar'),
    ('/etc/mongodb/mongod_27018.key', 'bar'),
    ('/etc/mongodb/mongos_27019.conf', 'foobar'),
    ('/etc/mongodb/mongos_27019.key', 'foobar'),
])
def test_configuration_files(host, path, user):
    """
    Test configuration files management
    """

    if host.system_info.distribution in ['debian', 'ubuntu']:
        mongodb_user = 'mongodb'
    else:
        mongodb_user = 'mongod'

    if user != 'mongodb':
        mongodb_user = user

    config_file = host.file(path)
    assert config_file.exists
    assert config_file.is_file
    assert config_file.user == mongodb_user
    assert config_file.group == mongodb_user
    assert config_file.mode == 0o400


@pytest.mark.parametrize('user', [('bar'), ('foobar')])
def test_instance_users(host, user):
    """
    Test dedicated instance user
    """

    if host.system_info.distribution in ['debian', 'ubuntu']:
        mongodb_user = 'mongodb'
    else:
        mongodb_user = 'mongod'

    current_user = host.user(user)

    assert current_user.exists
    assert current_user.group == user
    assert mongodb_user in current_user.groups
    assert current_user.home == '/home/%s' % user
    assert current_user.shell == '/bin/false'


@pytest.mark.parametrize('path', ['/var/lib/mongodb/foo'])
def test_data_directories(host, path):
    """
    Test data directory management
    """

    if host.system_info.distribution in ['debian', 'ubuntu']:
        mongodb_user = 'mongodb'
    else:
        mongodb_user = 'mongod'

    data_directory = host.file(path)
    assert data_directory.exists
    assert data_directory.is_directory
    assert data_directory.user == mongodb_user
    assert data_directory.group == mongodb_user
    assert data_directory.mode == 0o750


@pytest.mark.parametrize('path', [
    ('/lib/systemd/system/mongod_27017.service'),
    ('/lib/systemd/system/mongod_27018.service'),
    ('/lib/systemd/system/mongos_27019.service')
])
def test_systemd_services_files(host, path):
    """
    Test systemd services files management
    """

    service_file = host.file(path)
    assert service_file.exists
    assert service_file.is_file
    assert service_file.user == 'root'


@pytest.mark.parametrize('service_name,enabled,running', [
    ('mongod_27017', True, True),
    ('mongod_27018', False, False),
    ('mongos_27019', True, True)
])
def test_systemd_instance_services(host, service_name, enabled, running):
    """
    Test instance systemd services
    """

    assert host.service(service_name).is_enabled is enabled
    assert host.service(service_name).is_running is running


def test_hugepage_service_file(host):
    """
    Test hugepage initd service file management
    """

    service_file = host.file('/etc/init.d/disable-transparent-hugepages')

    assert service_file.exists
    assert service_file.is_file
    assert service_file.user == 'root'


def test_hugepage_service_state(host):
    """
    Test hugepage initd service state
    """

    service = host.service('disable-transparent-hugepages')

    assert service.is_enabled
    assert service.is_running


@pytest.mark.parametrize('path', [
    ('/sys/kernel/mm/transparent_hugepage/enabled'),
    ('/sys/kernel/mm/transparent_hugepage/defrag'),
])
def test_hugepage_setting_value(host, path):
    """
    Test if kernel hugepage setting have recommended value
    """

    assert '[never]' in host.file(path).content_string


def test_logrotate_file(host):
    """
    Test logrotate configuration file
    """

    config_file = host.file('/etc/logrotate.d/mongodb')
    assert config_file.exists
    assert config_file.is_file
    assert config_file.user == 'root'


@pytest.mark.parametrize('user,database', [
    ('foo', 'admin'),
    ('foobar', 'foobar_db'),
])
def test_mongodb_users(host, user, database):
    """
    Test if MongoDB users created
    """

    test_host = 'localhost:27017'

    result = json.loads(host.check_output(
        "mongo {}/{} --quiet --eval 'printjson(db.getUsers())'".format(
            test_host, database)))
    assert result[0]['_id'] == "{}.{}".format(database, user)
    assert result[0]['db'] == database
    assert result[0]['user'] == user
