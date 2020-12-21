#!/usr/bin/env python3
from aws_cdk import core
import aws_cdk.aws_ec2 as ec2
from eks_and_vpc.k8s_stack import EKSStack
from eks_and_vpc.vpc_stack import VpcStack
from globals import *

environment = config["global"]["environment"]
account_id = config["global"]["account_id"]
region = config["global"]["region"]
env = {'account': account_id , 'region': region}
app = core.App()

# Create VPC
vpc_stack = VpcStack(app, environment + "-vpc",
                     cidr_block=config["vpc"]["cidr_block"],
                     env = env)
vpc_stack.add_subnet_configuration(
    subnet_type=ec2.SubnetType.PUBLIC,
    name="Public",
    cidr_mask=24)

vpc_stack.add_subnet_configuration(
    subnet_type=ec2.SubnetType.PRIVATE,
    name="PRIVATE",
    cidr_mask=24)
vpc_stack.create_vpc()

eks_stack = EKSStack(app, environment + "-eks",
                     vpc = vpc_stack.vpc,
                     cluster_name = config["eks"]["cluster_name"],
                     # masters_role = config["eks"]["masters_role"],
                     managed_worker_nodes_nubmer = config["eks"]["managed_worker_nodes_nubmer"],
                     unmanaged_worker_nodes_number = config["eks"]["unmanaged_worker_nodes_number"],
                     spot_price = config["eks"]["spot_price"],
                     key_pair = config["eks"]["key_pair"],
                     instance_type = config["eks"]["instance_type"],
                     env = env)
# eks_stack.deploy_tools(nginx_ingress=True, metrics_server=False)
eks_stack.add_dependency(vpc_stack)

app.synth()


