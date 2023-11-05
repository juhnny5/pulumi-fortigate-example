#!/usr/bin/env python3

import pulumi
import pulumi_fortios as forti
import yaml

addresses_file = 'firewall/addresses.yaml'
address_groups_file = 'firewall/address_groups.yaml'
rules_file = 'firewall/rules.yaml'

with open(addresses_file, 'r') as file:
    content_addresses = yaml.safe_load(file)

with open(address_groups_file, 'r') as file:
    content_address_groups = yaml.safe_load(file)

with open(rules_file, 'r') as file:
    content_rules = yaml.safe_load(file)

for key, value in content_addresses.items():
    address = forti.FirewallAddress(
        key+"-address",
        allow_routing="disable",
        associated_interface=value['interface'],
        end_ip=value['mask'],
        name=key,
        start_ip=value['ip'],
        subnet=f"{value['ip']} {value['mask']}",
        type="ipmask",
        visibility="enable",
    )

for key, value in content_address_groups.items():
    members = []
    for member in value['members']:
        members.append(forti.FirewallAddrgrp6MemberArgs(name=member))

    address = forti.FirewallAddrgrp(
        key+"-address-group",
        name=key,
        members=members,
        comment=value['comment'],
        opts=pulumi.ResourceOptions(depends_on=address) # Add depends_on to ensure addresses are created first
    )

for key, value in content_rules.items():
    srcintfs = []
    for srcintf in value['srcintfs']:
        srcintfs.append(forti.FirewallPolicySrcintfArgs(name=srcintf))

    srcaddrs = []
    for srcaddr in value['srcaddrs']:
        srcaddrs.append(forti.FirewallPolicySrcaddrArgs(name=srcaddr))

    dstintfs = []
    for dstintf in value['dstintfs']:
        dstintfs.append(forti.FirewallPolicyDstintfArgs(name=dstintf))

    dstaddrs = []
    for dstaddr in value['dstaddrs']:
        dstaddrs.append(forti.FirewallPolicyDstaddrArgs(name=dstaddr))

    services = []
    for service in value['services']:
        services.append(forti.FirewallPolicyServiceArgs(name=service))

    rule = forti.FirewallPolicy(
        key,
        action=value['action'],
        srcintfs=srcintfs,
        srcaddrs=srcaddrs,
        dstintfs=dstintfs,
        dstaddrs=dstaddrs,
        services=services,
        schedule="always",
        logtraffic=value['logtraffic'],
        opts=pulumi.ResourceOptions(depends_on=address),
        comments=value['comments']
    )
