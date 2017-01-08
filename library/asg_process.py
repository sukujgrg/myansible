#!/usr/bin/env python

DOCUMENTATION = '''
module: ec2 autoscaling process
version_added: "1.0"
short_description: Manager EC2 autoscaling process
description:
     - Suspend/Resume EC2 autoscaling process
options:
  ags_name:
    description:
      - the name of the autoscaling group
    required: true
  processes:
    description:
      - all valid asg processes as list
    required: true
  state:
      description:
        - suspend and resume will do the obvious action on the given processes
      required: true
      choices: ['suspend', 'resume']
requirements: [ "boto3" ]
author: Suku John George
'''

EXAMPLES = '''
# check auto-assign public ip attribute and turn-on if it is off
- asg_process:
    region: ap-southeast-2
    state: resume
    asg_name: testing_resume
    processes:
      - Launch
      - Terminate
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

def asg_proc(region, asg_name, processes, state):
    result = namedtuple('result', ('success', 'changed', 'message'))
    try:
        client = boto3.client('autoscaling', region_name=region)
        if state == 'resume':
            client.resume_processes(AutoScalingGroupName=asg_name, ScalingProcesses=processes)
            msg = 'resumed {0}'.format(', '.join(processes))
        elif state == 'suspend':
            client.suspend_processes(AutoScalingGroupName=asg_name, ScalingProcesses=processes)
            msg = 'suspended {0}'.format(', '.join(processes))
        return result(success=True, changed=True, message={'ASG Processes': msg})
    except Exception as e:
        return result(success=False, changed=False, message={'ASG Processes': e})


def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update({
        'processes': {'type': 'list', 'required': True},
        'asg_name': {'type': 'str', 'required': True},
        'state': {'type': 'str', 'choices': ('resume', 'suspend'), 'required': True},
    })
    module = AnsibleModule(argument_spec=argument_spec)

    if not HAS_BOTO3:
        module.fail_json(msg='boto3 is required for this module')

    region = module.params['region']
    asg_name = module.params['asg_name']
    processes = module.params['processes']
    state = module.params['state']

    is_success, has_changed, msg = asg_proc(region, asg_name, processes, state)
    if is_success:
        module.exit_json(changed=has_changed, meta=msg)
    else:
        module.fail_json(msg=msg)

if __name__ == '__main__':
    main()
