"""
Working with eks env.

"""
import datetime
import base64
from horey.aws_api.aws_api import AWSAPI
from horey.aws_api.aws_services_entities.iam_role import IamRole
from horey.aws_api.aws_services_entities.iam_policy import IamPolicy
from horey.aws_api.aws_services_entities.eks_cluster import EKSCluster


class K8S:
    """
    aws eks update-kubeconfig --region us-west-2 --name test-aws-example

    """

    TOKEN_EXPIRATION_MINS = 14
    TOKEN_PREFIX = "k8s-aws-v1."
    K8S_AWS_ID_HEADER = "x-k8s-aws-id"
    URL_TIMEOUT = 60

    def __init__(self):
        self.aws_api = AWSAPI()

    def provision_role(self, name):
        """
        Role Creation

        :param name:
        :return:
        """

        iam_role = IamRole({})
        iam_role.description = "alert_system lambda role"
        iam_role.name = name
        iam_role.max_session_duration = 12 * 60 * 60
        policy_src = """{
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "eks.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }"""
        iam_role.assume_role_policy_document = policy_src
        policy = IamPolicy({})
        policy.arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
        iam_role.policies.append(policy)
        self.aws_api.provision_iam_role(iam_role)
        return iam_role

    def get_cluster_login_credentials(self, cluster_name, region):
        """
        Find the cluster and retrieve the login credentials.

        :param cluster_name:
        :return:
        """
        token = self.get_token(cluster_name)

        cluster = EKSCluster({"name": cluster_name})
        cluster.region = region
        self.aws_api.eks_client.update_cluster_info(cluster)
        return cluster.endpoint, cluster.certificate_authority["data"], token

    @staticmethod
    def get_expiration_time():
        """
        Calculate token time.
        :return:
        """
        token_expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=K8S.TOKEN_EXPIRATION_MINS)
        return token_expiration.strftime("%Y-%m-%dT%H:%M:%SZ")

    def _get_presigned_url(self, k8s_aws_id):
        """
        Generate caller identity.

        :param k8s_aws_id:
        :return:
        """

        self._register_k8s_aws_id_handlers()
        return self.aws_api.sts_client.client.generate_presigned_url(
            "get_caller_identity",
            Params={self.K8S_AWS_ID_HEADER: k8s_aws_id},
            ExpiresIn=self.URL_TIMEOUT,
            HttpMethod="GET",
        )

    def get_token(self, cluster_name) -> dict:
        """
        Generate a presigned url token to pass to kubectl.
        Shamelessly stolen from here:
        https://github.com/peak-ai/eks-token/blob/main/eks_token/logics.py

        :param cluster_name:
        :return:
        """
        url = self._get_presigned_url(cluster_name)
        token = self.TOKEN_PREFIX + base64.urlsafe_b64encode(
            url.encode('utf-8')
        ).decode('utf-8').rstrip('=')
        return {
            "kind": "ExecCredential",
            "apiVersion": "client.authentication.k8s.io/v1alpha1",
            "spec": {},
            "status": {
                "expirationTimestamp": self.get_expiration_time(),
                "token": token
            }
        }

    def _register_k8s_aws_id_handlers(self):
        """
        Register callback functions

        :return:
        """

        self.aws_api.sts_client.client.meta.events.register(
            "provide-client-params.sts.GetCallerIdentity",
            self._retrieve_k8s_aws_id,
        )
        self.aws_api.sts_client.client.meta.events.register(
            "before-sign.sts.GetCallerIdentity",
            self._inject_k8s_aws_id_header,
        )

    def _retrieve_k8s_aws_id(self, params, context, **_):
        """
        Callback function.

        :param params:
        :param context:
        :param _:
        :return:
        """

        if self.K8S_AWS_ID_HEADER in params:
            context[self.K8S_AWS_ID_HEADER] = params.pop(self.K8S_AWS_ID_HEADER)

    def _inject_k8s_aws_id_header(self, request, **_):
        """
        Callback function.

        :param request:
        :param _:
        :return:
        """

        if self.K8S_AWS_ID_HEADER in request.context:
            request.headers[self.K8S_AWS_ID_HEADER] = request.context[self.K8S_AWS_ID_HEADER]
