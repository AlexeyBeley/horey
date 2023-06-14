#FROM HERE:  https://docs.aws.amazon.com/eks/latest/userguide/aws-load-balancer-controller.html

oidc_id=$(aws eks describe-cluster --name test-aws-example --region us-west-2 --query "cluster.identity.oidc.issuer" --output text | cut -d '/' -f 5)

aws iam list-open-id-connect-providers | grep $oidc_id | cut -d "/" -f4


cat >load-balancer-role-trust-policy.json <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::12345678910:oidc-provider/oidc.eks.us-west-2.amazonaws.com/id/954DE8583F4848A01632BDC97CB93FB5"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "oidc.eks.us-west-2.amazonaws.com/id/954DE8583F4848A01632BDC97CB93FB5:aud": "sts.amazonaws.com",
                    "oidc.eks.us-west-2.amazonaws.com/id/954DE8583F4848A01632BDC97CB93FB5:sub": "system:serviceaccount:kube-system:aws-load-balancer-controller"
                }
            }
        }
    ]
}
EOF

aws iam attach-role-policy \
  --policy-arn arn:aws:iam::12345678910:policy/AWSLoadBalancerControllerIAMPolicy \
  --role-name AmazonEKSLoadBalancerControllerRole
  

cat >aws-load-balancer-controller-service-account.yaml <<EOF
apiVersion: v1
kind: ServiceAccount
metadata:
  labels:
    app.kubernetes.io/component: controller
    app.kubernetes.io/name: aws-load-balancer-controller
  name: aws-load-balancer-controller
  namespace: kube-system
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::12345678910:role/AmazonEKSLoadBalancerControllerRole
EOF


kubectl apply -f aws-load-balancer-controller-service-account.yaml


kubectl apply \
    --validate=false \
    -f https://github.com/jetstack/cert-manager/releases/download/v1.5.4/cert-manager.yamlO


curl -Lo v2_4_7_full.yaml https://github.com/kubernetes-sigs/aws-load-balancer-controller/releases/download/v2.4.7/v2_4_7_full.yaml

sed -i.bak -e 's|your-cluster-name|test-aws-example|' ./v2_4_7_full.yaml
# security feature
#https://aws.github.io/aws-eks-best-practices/security/docs/iam/#restrict-access-to-the-instance-profile-assigned-to-the-worker-node