#/usr/bin/python

import re
from pathlib import Path

from ansible.module_utils.basic import AnsibleModule

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        asadmin = dict(type='str', required=True),
        return_version = dict(type='bool', default=False)
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    result = {
        'is_running': False,
        'version': None,
        'applications': None
    }

    asadmin = module.params['asadmin']

    # Check that payara_dir is valid:
    asadmin = Path(asadmin)
    if not asadmin.is_file():
        module.fail_json(msg='Could not find asadmin at %s' % asadmin)

    # Call `asadmin list-applications` to:
    #  - Check whether the domain is running
    #  - Get the list of deployed applications
    (rc, stdout, stderr) = module.run_command([asadmin, '--terse', 'list-applications'])
    if rc == 0:
        result['is_running'] = True
        result['applications'] = re.findall(r'^[^ ]+', stdout, flags=re.MULTILINE)

    # Call `asadmin version` to get the Payara version
    if module.params['return_version']:
        (rc, stdout, stderr) = module.run_command([asadmin, '--terse', 'version'])
        if rc == 0:
            result['version'] = re.match(r'^Payara Server +([^ ]+)', stdout, flags=re.MULTILINE)[1]

    return module.exit_json(changed=False, **result)


def main():
    run_module()


if __name__ == '__main__':
    main()
