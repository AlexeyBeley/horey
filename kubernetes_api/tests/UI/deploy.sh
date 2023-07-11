#
#
#
#install:

kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml\

#Start:

kubectl proxy

#Open UI:

#http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/.

#https://github.com/kubernetes/dashboard/blob/master/docs/user/access-control/README.md#bearer-token


kubectl apply -f ./admin-user.yaml
kubectl apply -f ./cluster-role-binding.yaml


kubectl -n kubernetes-dashboard create token admin-user
