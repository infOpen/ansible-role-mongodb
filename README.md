# mongodb

[![Build Status](https://img.shields.io/travis/infOpen/ansible-role-mongodb/master.svg?label=travis_master)](https://travis-ci.org/infOpen/ansible-role-mongodb)
[![Build Status](https://img.shields.io/travis/infOpen/ansible-role-mongodb/develop.svg?label=travis_develop)](https://travis-ci.org/infOpen/ansible-role-mongodb)
[![Updates](https://pyup.io/repos/github/infOpen/ansible-role-mongodb/shield.svg)](https://pyup.io/repos/github/infOpen/ansible-role-mongodb/)
[![Python 3](https://pyup.io/repos/github/infOpen/ansible-role-mongodb/python-3-shield.svg)](https://pyup.io/repos/github/infOpen/ansible-role-mongodb/)
[![Ansible Role](https://img.shields.io/ansible/role/13906.svg)](https://galaxy.ansible.com/infOpen/mongodb/)

Install mongodb package.

## Requirements

This role requires Ansible 2.1 or higher,
and platform requirements are listed in the metadata file.

## Testing

This role use [Molecule](https://github.com/metacloud/molecule/) to run tests.

Locally, you can run tests on Docker (default driver) or Vagrant.
Travis run tests using Docker driver only.

Currently, tests are done on:
- Ubuntu Xenial

and use:
- Ansible 2.0.x
- Ansible 2.1.x
- Ansible 2.2.x
- Ansible 2.3.x

### Running tests

#### Using Docker driver

```
$ tox
```

#### Using Vagrant driver

```
$ MOLECULE_DRIVER=vagrant tox
```

## Role Variables

### Default role variables

``` yaml
# Choice your MongoDB edition
# Possible choices:
# * org (community)
# * enterprise
mongodb_edition: 'org'
mongodb_version: '3.2'


# MongoDB APT installation variables
mongodb_apt_keyserver: "{{ _mongodb_apt_keyserver | default ('') }}"
mongodb_apt_key: "{{ _mongodb_apt_key | default('') }}"
mongodb_apt_file_name: "mongodb-{{ mongodb_edition }}.list"
mongodb_apt_file_mode: '0644'
mongodb_apt_entries: "{{ _mongodb_apt_entries | default([]) }}"
mongodb_apt_update_cache: True
mongodb_apt_cache_valid_time: 3600
mongodb_apt_force: True


# Pymongo management
mongodb_os_packages_pymongo: "{{ _mongodb_os_packages_pymongo }}"
mongodb_pip_packages_pymongo:
  - name: 'pymongo'


# MongoDB packages
mongodb_packages_all: "{{ _mongodb_packages_all }}"
mongodb_packages_server: "{{ _mongodb_packages_server }}"
mongodb_packages_mongos: "{{ _mongodb_packages_mongos }}"
mongodb_packages_shell: "{{ _mongodb_packages_shell }}"
mongodb_packages_tools: "{{ _mongodb_packages_tools }}"


# Roles to install
mongodb_install_additional: True
mongodb_install_all: True
mongodb_install_server: True
mongodb_install_mongos: True
mongodb_install_shell: True
mongodb_install_tools: True


# Default instance management
mongodb_default_instance: "{{ _mongodb_default_instance }}"
mongodb_default_instance_disabled: True
mongodb_default_instance_removed: False


# Main user
mongodb_user: "{{ _mongodb_user }}"
mongodb_group: "{{ _mongodb_group }}"


# MongoDB databases users
mongodb_users: []


# Paths
mongodb_base_folders_paths:
  config: "{{ _mongodb_os_base_config_path }}/mongodb"
  data: "{{ _mongodb_os_base_data_path }}/mongodb"
  initd: "{{ _mongodb_os_base_initd_path }}"
  log: "{{ _mongodb_os_base_log_path }}/mongodb"
  logrotate: "{{ _mongodb_os_base_logrotate_path }}"
  upstart: "{{ _mongodb_os_base_upstart_path | default('') }}"
  run: "{{ _mongodb_os_base_run_path }}/mongodb"
  systemd_services: "{{ _mongodb_os_base_systemd_services_path | default('') }}"


# MongoDB configuration
mongodb_instances:
  - type: 'mongod'
    config: "{{ _mongodb_config_mongod }}"
    state: 'present'
    enabled: True


# Services management
mongodb_is_upstart_management: "{{ _mongodb_is_upstart_management | default(False) }}"
mongodb_is_systemd_management: "{{ _mongodb_is_systemd_management | default(False) }}"


# Manage hugepage settings to prevent MongoDB warnings
mongodb_manage_hugepage_settings: True


# Logrotate management
# Create option is manage inside template
mongodb_logrotate_options:
  - 'daily'
  - 'dateext'
  - 'dateformat _%Y-%m-%d'
  - 'rotate 31'
  - 'copytruncate'
  - 'compress'
  - 'delaycompress'
  - 'missingok'
```

## How ...

### Manage hugepage kernel settings with MongoDB recommendation

By default, this role manage these settings to set MongoDB recommendation:
* /sys/kernel/mm/transparent_hugepage/enable: never
* /sys/kernel/mm/transparent_hugepage/defrag: never

It's a new init.d service configured to start before MongoDB instances.

If you want to turn off this feature, just set mongodb_manage_hugepage_settings
to False.

### Manage "pymongo" install

By default, "pymongo" is installed by pip, to have a compatible version with
newest MongoDB packages.

> ***Warning***: This role not manage pip install, so you need to manage this !

Change nothing if you want this install method.

If you need os version, set "mongodb_install_pymongo_method" to "os" to use the
OS package instead.

### Manage databases users

You can defined users into "mongodb_users" variable.

Settings are the same than "mongodb_user" Ansible module.

### Install all packages

Only set ***mongodb_install_all*** to ***True***, and role will use meta package.
It is the default value without custom settings

### Only install some roles

1. Set ***mongodb_install_all*** to ***False***
2. Set needed roles to ***True*** and ***False*** to others for these items:
```yaml
mongodb_install_server: True
mongodb_install_mongos: True
mongodb_install_shell: True
mongodb_install_tools: True
```

## Dependencies

None

## Example Playbook

``` yaml
- hosts: servers
  roles:
    - { role: infOpen.mongodb }
```

## License

MIT

## Author Information

Alexandre Chaussier (for Infopen company)
- http://www.infopen.pro
- a.chaussier [at] infopen.pro
