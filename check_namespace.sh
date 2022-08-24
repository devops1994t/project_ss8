#!/bin/bash
echo "Checking if namespace "$1" available in Kubernetes Cluster" >> namespacelog
echo "$1"
namespace="$1"
if [ -n "$1" ];then
kubectl get namespaces | grep "$namespace"
##########
if [ $? -eq 0 ];then
  echo "Namespace "$namespace" exists in Kubernetes Cluster" >> namespacelog
  exit
elif [ $? -ne 0 ];then
  kubectl create namespace "$namespace"
else 
  echo "Issues with checking namespace availability" >> namespacelog
fi
#########
else
echo "namespace name is not available, exit"
exit
fi







