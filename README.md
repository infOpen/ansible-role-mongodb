# mongodb

[![Build Status](https://travis-ci.org/infOpen/ansible-role-mongodb.svg?branch=master)](https://travis-ci.org/infOpen/ansible-role-mongodb)

Install mongodb package.

## Requirements

This role requires Ansible 2.1 or higher,
and platform requirements are listed in the metadata file.

## Testing

This role has some testing methods.

To use locally testing methods, you need to install Docker and/or Vagrant and Python requirements:

* Create and activate a virtualenv
* Install requirements

```
pip install -r requirements_dev.txt
```

### Automatically with Travis

Tests runs automatically on Travis on push, release, pr, ... using docker testing containers

### Locally with Docker

You can use Docker to run tests on ephemeral containers.

```
make test-docker
```

### Locally with Vagrant

You can use Vagrant to run tests on virtual machines.

```
make test-vagrant
```

## Role Variables

### Default role variables

``` yaml
# Choice your MongoDB edition
# Possible choices:
# * community
# * enterprise
mongodb_edition: 'community'
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


# MongoDB packages
mongodb_packages_all: "{{ _mongodb_packages_all }}"
mongodb_packages_server: "{{ _mongodb_packages_server }}"
mongodb_packages_mongos: "{{ _mongodb_packages_mongos }}"
mongodb_packages_shell: "{{ _mongodb_packages_shell }}"
mongodb_packages_tools: "{{ _mongodb_packages_tools }}"


# Roles to install
mongodb_install_all: True
mongodb_install_server: True
mongodb_install_mongos: True
mongodb_install_shell: True
mongodb_install_tools: True
```

## How ...

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

    - hosts: servers
      roles:
         - { role: infOpen.mongodb }

## License

MIT

## Author Information

Alexandre Chaussier (for Infopen company)
- http://www.infopen.pro
- a.chaussier [at] infopen.pro

