#!/usr/bin/env python3

import pulumi
import pulumi_fortios as forti
import yaml

addresses_file = 'firewall/addresses.yaml'
address_groups_file = 'firewall/address_groups.yaml'
rules_file = 'firewall/rules.yaml'
services_file = 'firewall/services.yaml'
service_groups_file = 'firewall/service_groups.yaml'

with open(addresses_file, 'r') as file:
    content_addresses = yaml.safe_load(file)

with open(address_groups_file, 'r') as file:
    content_address_groups = yaml.safe_load(file)

with open(rules_file, 'r') as file:
    content_rules = yaml.safe_load(file)

with open(services_file, 'r') as file:
    content_services = yaml.safe_load(file)

with open(service_groups_file, 'r') as file:
    content_service_groups = yaml.safe_load(file)

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
        comments=value['comments'],
        opts=pulumi.ResourceOptions(depends_on=address)
    )

for key, value in content_services.items():
    if value['type'] == 'TCP':
        serviced = forti.FirewallServiceCustom(
            key,
            app_service_type="disable",
            category="General",
            check_reset_range="default",
            color=0,
            helper="auto",
            iprange="0.0.0.0",
            name=key,
            protocol="TCP/UDP/SCTP",
            protocol_number=6,
            proxy="disable",
            tcp_halfclose_timer=0,
            tcp_halfopen_timer=0,
            tcp_portrange=value['port_range'],
            tcp_timewait_timer=0,
            udp_idle_timer=0,
            visibility=value['visibility'],
            )
    elif value['type'] == 'UDP':
        serviced = forti.FirewallServiceCustom(
            key,
            app_service_type="disable",
            category="General",
            check_reset_range="default",
            color=0,
            helper="auto",
            iprange="0.0.0.0",
            name=key,
            protocol="TCP/UDP/SCTP",
            protocol_number=6,
            proxy="disable",
            udp_halfclose_timer=0,
            udp_halfopen_timer=0,
            udp_portrange=value['port_range'],
            udp_timewait_timer=0,
            udp_idle_timer=0,
            visibility=value['visibility'],
            )
    elif value['type'] == 'SCTP':
        serviced = forti.FirewallServiceCustom(
            key,
            app_service_type="disable",
            category="General",
            check_reset_range="default",
            color=0,
            helper="auto",
            iprange="0.0.0.0",
            name=key,
            protocol="TCP/UDP/SCTP",
            protocol_number=6,
            proxy="disable",
            sctp_halfclose_timer=0,
            sctp_halfopen_timer=0,
            sctp_portrange=value['port_range'],
            sctp_timewait_timer=0,
            sctp_idle_timer=0,
            visibility=value['visibility'],
            )

for key, value in content_service_groups.items():
    members = []
    for service in value['members']:
        members.append(forti.FirewallServiceGroupMemberArgs(name=service))

    service_groups = forti.FirewallServiceGroup(
        resource_name=key,
        color=0,
        name=key,
        proxy="disable",
        members=members,
        opts=pulumi.ResourceOptions(depends_on=serviced)
    )
