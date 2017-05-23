"""
Role tests
"""

import json
import pytest
from testinfra.utils.ansible_runner import AnsibleRunner

testinfra_hosts = AnsibleRunner('.molecule/ansible_inventory').get_hosts('all')


def test_repository_file(host):
    """
    Test repository file permissions and content on Ubuntu distributions
    """

    if host.system_info.distribution != 'ubuntu':
        pytest.skip('Not apply to %s' % host.system_info.distribution)

    if 'mongodb-org' in host.check_output('cat /etc/hostname'):
        repo_file_name = '/etc/apt/sources.list.d/mongodb-org.list'
        expected_content = (
            'deb http://repo.mongodb.org/apt/{distribution} '
            '{release}/mongodb-org/3.4 multiverse'
        ).format(
            distribution=host.system_info.distribution,
            release=host.system_info.codename
        )
    else:
        repo_file_name = '/etc/apt/sources.list.d/mongodb-enterprise.list'
        expected_content = (
            'deb http://repo.mongodb.com/apt/{distribution} '
            '{release}/mongodb-enterprise/3.4 multiverse'
        ).format(
            distribution=host.system_info.distribution,
            release=host.system_info.codename
        )

    repo_file = host.file(repo_file_name)

    assert repo_file.exists
    assert repo_file.is_file
    assert repo_file.user == 'root'
    assert repo_file.group == 'root'
    assert repo_file.mode == 0o644
    assert repo_file.contains(expected_content)


def test_ubuntu_packages(host):
    """
    Test packages on Ubuntu distributions
    """

    if host.system_info.distribution != 'ubuntu':
        pytest.skip('Not apply to %s' % host.system_info.distribution)

    if 'mongodb-org' in host.check_output('cat /etc/hostname'):
        packages = [
            'mongodb-org',
            'mongodb-org-server',
            'mongodb-org-mongos',
            'mongodb-org-shell',
            'mongodb-org-tools',
        ]
    else:
        packages = [
            'mongodb-enterprise',
            'mongodb-enterprise-server',
            'mongodb-enterprise-mongos',
            'mongodb-enterprise-shell',
            'mongodb-enterprise-tools',
        ]

    for package in packages:
        assert host.package(package).is_installed


def test_pymongo_management(host):
    """
    Test "pymongo" installation with pip
    """

    assert 'version' in host.pip_package.get_packages().get('pymongo')


def test_default_instance_service(host):
    """
    Test default instance service disabled on Ubuntu distributions
    """

    if host.system_info.distribution != 'ubuntu':
        pytest.skip('Not apply to %s' % host.system_info.distribution)

    assert host.service('mongod').is_enabled is False

    if host.system_info.codename == 'trusty':
        # On my Trusty service test, return code is 0 when service stopped
        expected_output = 'mongod stop/waiting'
        assert expected_output in host.check_output('service mongod status')
    else:
        assert host.service('mongod').is_running is False


def test_configuration_directory(host):
    """
    Test configuration directory management
    """

    if host.system_info.distribution != 'ubuntu':
        pytest.skip('Not apply to %s' % host.system_info.distribution)

    config_dir = host.file('/etc/mongodb')
    assert config_dir.exists
    assert config_dir.is_directory
    assert config_dir.user == 'root'
    assert config_dir.group == 'mongodb'
    assert config_dir.mode == 0o750


def test_configuration_files(host):
    """
    Test configuration files management on Ubuntu distributions
    """

    if host.system_info.distribution != 'ubuntu':
        pytest.skip('Not apply to %s' % host.system_info.distribution)

    config_files = [
        {'path': '/etc/mongodb/mongod_27017.conf', 'user': 'mongodb'},
        {'path': '/etc/mongodb/mongod_27017.key', 'user': 'mongodb'},
        {'path': '/etc/mongodb/mongod_27018.conf', 'user': 'bar'},
        {'path': '/etc/mongodb/mongod_27018.key', 'user': 'bar'},
        {'path': '/etc/mongodb/mongos_27019.conf', 'user': 'foobar'},
        {'path': '/etc/mongodb/mongos_27019.key', 'user': 'foobar'},
    ]

    for current_file in config_files:
        config_file = host.file(current_file['path'])
        assert config_file.exists
        assert config_file.is_file
        assert config_file.user == current_file['user']
        assert config_file.group == current_file['user']
        assert config_file.mode == 0o400


def test_instance_users(host):
    """
    Test dedicated instance user
    """

    users = ['bar', 'foobar']

    for user in users:
        current_user = host.user(user)

        assert current_user.exists
        assert current_user.group == user
        assert 'mongodb' in current_user.groups
        assert current_user.home == '/home/%s' % user
        assert current_user.shell == '/bin/false'


def test_data_directories(host):
    """
    Test data directory management
    """

    data_directories = [
        {'path': '/var/lib/mongodb/foo', 'user': 'mongodb'},
    ]

    for current_directory in data_directories:
        data_directory = host.file(current_directory['path'])
        assert data_directory.exists
        assert data_directory.is_directory
        assert data_directory.user == current_directory['user']
        assert data_directory.group == current_directory['user']
        assert data_directory.mode == 0o750


def test_upstart_init_files(host):
    """
    Test upstart init files management
    """

    if host.system_info.codename != 'trusty':
        pytest.skip('Not apply to %s' % host.system_info.codename)

    upstart_files = [
        '/etc/init/mongod_27017.conf',
        '/etc/init/mongod_27018.conf',
        '/etc/init/mongos_27019.conf'
    ]

    for current_file in upstart_files:
        upstart_file = host.file(current_file)
        assert upstart_file.exists
        assert upstart_file.is_file
        assert upstart_file.user == 'root'


def test_upstart_instance_services(host):
    """
    Test instance upstart services on Ubuntu Trusty
    """

    if host.system_info.codename != 'trusty':
        pytest.skip('Not apply to %s' % host.system_info.codename)

    services = [
        {'name': 'mongod_27017', 'enabled': True, 'running': True},
        {'name': 'mongod_27018', 'enabled': False, 'running': False},
        {'name': 'mongos_27019', 'enabled': True, 'running': True},
    ]

    for service in services:
        assert host.service(service['name']).is_enabled is service['enabled']
        if service['running']:
            assert '%s start/running' % service['name'] in \
                host.check_output('service %s status' % service['name'])
        else:
            assert '%s stop/waiting' % service['name'] in \
                host.check_output('service %s status' % service['name'])


def test_systemd_services_files(host):
    """
    Test systemd services files management
    """

    if host.system_info.codename != 'xenial':
        pytest.skip('Not apply to %s' % host.system_info.codename)

    services_files = [
        '/lib/systemd/system/mongod_27017.service',
        '/lib/systemd/system/mongod_27018.service',
        '/lib/systemd/system/mongos_27019.service'
    ]

    for current_file in services_files:
        service_file = host.file(current_file)
        assert service_file.exists
        assert service_file.is_file
        assert service_file.user == 'root'


def test_systemd_instance_services(host):
    """
    Test instance systemd services on Ubuntu Xenial
    """

    if host.system_info.codename != 'xenial':
        pytest.skip('Not apply to %s' % host.system_info.codename)

    services = [
        {'name': 'mongod_27017', 'enabled': True, 'running': True},
        {'name': 'mongod_27018', 'enabled': False, 'running': False},
        {'name': 'mongos_27019', 'enabled': True, 'running': True},
    ]

    for service in services:
        assert host.service(service['name']).is_enabled is service['enabled']
        assert host.service(service['name']).is_running is service['running']


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


def test_hugepage_setting_value(host):
    """
    Test if kernel hugepage setting have recommended value
    """

    if host.system_info.distribution != 'ubuntu':
        pytest.skip('Not apply to %s' % host.system_info.distribution)

    setting_paths = [
        '/sys/kernel/mm/transparent_hugepage/enabled',
        '/sys/kernel/mm/transparent_hugepage/defrag',
    ]

    for setting_path in setting_paths:
        assert '[never]' in host.file(setting_path).content_string


def test_logrotate_file(host):
    """
    Test logrotate configuration file
    """

    config_file = host.file('/etc/logrotate.d/mongodb')
    assert config_file.exists
    assert config_file.is_file
    assert config_file.user == 'root'


def test_mongodb_users(host):
    """
    Test if MongoDB users created
    """

    users = [
        {'name': 'foo', 'database': 'admin'},
        {'name': 'foobar', 'database': 'foobar_db'},
    ]

    test_host = 'localhost:27017'

    for user in users:
        result = json.loads(host.check_output(
            "mongo {}/{} --quiet --eval 'printjson(db.getUsers())'".format(
                test_host, user['database'])))
        assert result[0]['_id'] == "{}.{}".format(
            user['database'], user['name'])
        assert result[0]['db'] == user['database']
        assert result[0]['user'] == user['name']
