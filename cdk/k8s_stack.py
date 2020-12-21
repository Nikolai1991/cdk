from aws_cdk import (
    aws_eks as eks,
    aws_kms as kms,
    aws_ec2 as ec2,
    aws_iam as iam,
    core
)
from cdk_ec2_key_pair import KeyPair

class EKSStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str,
                 vpc, instance_type, managed_worker_nodes_nubmer,
                 cluster_name, unmanaged_worker_nodes_number, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        #Create key pair that will be used for the K8S worker nodes
        self.key = KeyPair(
            self,"EKSKey",
            name="kaltura",
            description="This is a Key Pair for EKS worker nodes"
        )
        #Create KMS key for secrets encryption
        self.kms_eks = kms.Key(
            self, 'kms_eks',
            alias = 'kms_eks',
        )
        #Get the IAM role which will be added to the aws_auth
        # masters_role = iam.Role.from_role_arn(
        #     self, 'MasterRole',
        #     role_arn = masters_role
        # )

        #Create EKS cluster with managed/unmanaged worker nodes
        self.eks_cluster = eks.Cluster(
            self, 'eks',
            cluster_name = cluster_name,
            version= eks.KubernetesVersion.V1_17,
            # masters_role = masters_role,
            default_capacity = managed_worker_nodes_nubmer,
            secrets_encryption_key = self.kms_eks,
            vpc = vpc
        )
        self.eks_role = self.eks_cluster.node.try_find_child('Role')
        self.eks_role.add_to_policy(
            statement = iam.PolicyStatement(actions = ["ec2:DescribeVpcs"], resources = ["*"])
        )
        if unmanaged_worker_nodes_number > 0:
            self.eks_cluster.add_auto_scaling_group_capacity(
                "EKSAutoScalingGroup",
                instance_type = ec2.InstanceType(instance_type),
                lifecycle=Ec2Spot
                desired_capacity = unmanaged_worker_nodes_number,
                key_name = self.key.name
            )
    # def deploy_tools(self,nginx_ingress=True,metrics_server=True):
    #     #Create Nginx Ingress Controller with internal NLB
    #     if nginx_ingress:
    #         self.eks_cluster.add_helm_chart(
    #             'NginxIngress',
    #             chart = 'nginx-ingress',
    #             repository = 'https://helm.nginx.com/stable',
    #             release = 'nginx-ingress',
    #             namespace = 'tools',
    #             values = {"controller":{"kind":"daemonset","ingressClass":"nginx","service":
    #                 {"annotations":{"service.beta.kubernetes.io/aws-load-balancer-type": "nlb",
    #                                 "service.beta.kubernetes.io/aws-load-balancer-internal": "true",
    #                                 "service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled": "true",
    #                                 "service.beta.kubernetes.io/aws-load-balancer-additional-resource-tags":"Name=nginx-ingress",
    #                                 }}}})
    #     #Install Metrics Server
    #     if metrics_server:
    #         self.eks_cluster.add_helm_chart(
    #             'MetricsServer',
    #             chart = 'metrics-server',
    #             repository = 'https://charts.helm.sh/stable',
    #             namespace = 'tools'
    #         )
