#!/usr/bin/env python

# a custom ansible module for updating the ec2 subnet "Auto Assign Public IP" attribute

DOCUMENTATION = '''
module: update_subnet_attribute
version_added: "1.0"
short_description: Modify Auto-Assign Public IP
description:
     - Modifies auto-assign public IP attribute of a subnet
options:
  subnet:
    description:
      - the ID of the sbunet.
    required: true
  region:
    description:
      - aws region
    required: true
  state:
      description:
        - absent will turn-off auto-assign public ip and present will do opposite
      required: true
      choices: ['present', 'absent']
requirements: [ "boto3" ]
author: Suku John George
'''

EXAMPLES = '''
# check auto-assign public ip attribute and turn-on if it is off
- update_subnet_attribute:
    subnet: subnet-xxxxxx
    region: ap-southeast-2
    state: present
'''

from collections import namedtuple
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.ec2 import ec2_argument_spec
try:
    import boto3
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False
    if __name__ == '__main__':
        raise

def update_subnet_attr(region, subnet_id, state):
    update_result = namedtuple('update_result', ('success', 'changed', 'message'))
    try:
        ec2 = boto3.resource('ec2', region_name=region)
        subnet = ec2.Subnet(subnet_id)
        changed = False
        if subnet.map_public_ip_on_launch != state:
            subnet.meta.client.modify_subnet_attribute(
                SubnetId=subnet_id,
                MapPublicIpOnLaunch={"Value": state},
            )
            changed = True
        return update_result(success=True, changed=changed, message={'MapPublicIpOnLaunch': state})
    except Exception as e:
        return update_result(success=False, changed=False, message={'Failed': e})

def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update({
        'subnet': {'type': 'str', 'required': True},
        'state': {'type': 'str', 'choices': ('present', 'absent'), 'default': 'present'},
    })
    module = AnsibleModule(argument_spec=argument_spec)

    if not HAS_BOTO3:
        module.fail_json(msg='boto3 is required for this module')

    region = module.params['region']
    subnet_id = module.params['subnet']
    state = module.params['state'] == 'present'

    is_success, has_changed, msg = update_subnet_attr(region, subnet_id, state)
    if is_success:
        module.exit_json(changed=has_changed, meta=msg)
    else:
        module.fail_json(msg=msg)

if __name__ == '__main__':
    main()
