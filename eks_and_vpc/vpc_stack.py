from aws_cdk import core
import aws_cdk.aws_ec2 as ec2

class VpcStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, cidr_block, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self.vpc = None
        self.cidr_block = cidr_block
        self.subnet_configuration = None

    def add_subnet_configuration(self, subnet_type, name: str, cidr_mask: int):
        if not self.subnet_configuration:
            self.subnet_configuration = []
        self.subnet_configuration.append(ec2.SubnetConfiguration(
            subnet_type=subnet_type,
            name=name,
            cidr_mask=cidr_mask
        ))

    def create_vpc(self, max_azs=4, nat_gateways=1):
        # Create VPC with private and public subnets
        if self.subnet_configuration:
            self.vpc = ec2.Vpc(
                self, "VPC",
                max_azs=max_azs,
                cidr=self.cidr_block,
                subnet_configuration=self.subnet_configuration,
                nat_gateways=nat_gateways,
            )
            core.CfnOutput(self, "Output",
                           value=self.vpc.vpc_id)
        else:
            raise ValueError("subnet_configuration should be set using add_subnet_configuration")
