from kubernetes import client, config

# Load Kubernetes configuration from default location
config.load_kube_config()

# Create a Kubernetes client
v1 = client.CoreV1Api()
v1beta1 = client.ExtensionsV1beta1Api()

# Create the Nginx Deployment
nginx_deployment = {
    "apiVersion": "apps/v1",
    "kind": "Deployment",
    "metadata": {
        "name": "nginx-deployment",
        "labels": {
            "app": "nginx"
        }
    },
    "spec": {
        "replicas": 3,
        "selector": {
            "matchLabels": {
                "app": "nginx"
            }
        },
        "template": {
            "metadata": {
                "labels": {
                    "app": "nginx"
                }
            },
            "spec": {
                "containers": [
                    {
                        "name": "nginx",
                        "image": "nginx:latest",
                        "ports": [
                            {
                                "containerPort": 80
                            }
                        ]
                    }
                ]
            }
        }
    }
}

# Create the Nginx Service
nginx_service = {
    "apiVersion": "v1",
    "kind": "Service",
    "metadata": {
        "name": "nginx-service"
    },
    "spec": {
        "type": "NodePort",
        "ports": [
            {
                "port": 80,
                "targetPort": 80,
                "protocol": "TCP"
            }
        ],
        "selector": {
            "app": "nginx"
        }
    }
}

# Create the Nginx Deployment
v1beta1.create_namespaced_deployment(namespace="default", body=nginx_deployment)

# Create the Nginx Service
v1.create_namespaced_service(namespace="default", body=nginx_service)

# Define the ALB Ingress resource
alb_ingress = {
    "apiVersion": "extensions/v1beta1",
    "kind": "Ingress",
    "metadata": {
        "name": "nginx-ingress",
        "annotations": {
            "kubernetes.io/ingress.class": "alb",
            "alb.ingress.kubernetes.io/scheme": "internet-facing"
        }
    },
    "spec": {
        "rules": [
            {
                "http": {
                    "paths": [
                        {
                            "path": "/",
                            "backend": {
                                "serviceName": "nginx-service",
                                "servicePort": 80
                            }
                        }
                    ]
                }
            }
        ]
    }
}

# Create the ALB Ingress resource
v1beta1.create_namespaced_ingress(namespace="default", body=alb_ingress)
