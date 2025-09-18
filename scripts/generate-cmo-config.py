#!/usr/bin/env python

import copy
import oyaml as yaml
import os

input_file_path = os.path.join("resources", "cluster-monitoring-config", "config.yaml")
output_file_path_non_uwm = os.path.join("deploy", "cluster-monitoring-config-non-uwm", "50-GENERATED-cluster-monitoring-config.yaml")
output_file_path_non_uwm_4_5 = os.path.join("deploy", "cluster-monitoring-config-non-uwm", "clusters-v4.5", "50-GENERATED-cluster-monitoring-config.yaml")
output_file_path_non_uwm_pre_411 = os.path.join("deploy", "cluster-monitoring-config-non-uwm", "pre-4.11", "50-GENERATED-cluster-monitoring-config.yaml")
output_file_path_non_uwm_411_416 = os.path.join("deploy", "cluster-monitoring-config-non-uwm", "4.11-4.16", "50-GENERATED-cluster-monitoring-config.yaml")
output_file_path_uwm = os.path.join("deploy", "cluster-monitoring-config", "50-GENERATED-cluster-monitoring-config.yaml")
output_file_path_uwm_pre_411 = os.path.join("deploy", "cluster-monitoring-config", "pre-4.11", "50-GENERATED-cluster-monitoring-config.yaml")
output_file_path_uwm_411_416 = os.path.join("deploy", "cluster-monitoring-config", "4.11-4.16", "50-GENERATED-cluster-monitoring-config.yaml")
output_file_path_fr = os.path.join("deploy", "osd-fedramp-cluster-monitoring-config", "50-GENERATED-cluster-monitoring-config.yaml")
output_mc_file_path_non_uwm = os.path.join("deploy", "cluster-monitoring-config-non-uwm", "management-clusters", "50-GENERATED-cluster-monitoring-config.yaml")
output_mc_file_path_uwm = os.path.join("deploy", "cluster-monitoring-config", "management-clusters", "50-GENERATED-cluster-monitoring-config.yaml")

def str_presenter(dumper, data):
  if len(data.splitlines()) > 1:  # check for multiline string
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
  return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(str, str_presenter)

def dump_configmap(input_path, configmap_path, enableUserWorkload,
                   disableremoteWrite, retentionTime = "11d",
                   enableGrafana = False,
                   keepPrometheusAdapter = False):
    with open(input_path,'r') as input_file:
        config = yaml.safe_load(input_file)
        config["enableUserWorkload"] = enableUserWorkload
        config["prometheusK8s"]["retention"] = retentionTime
        if disableremoteWrite:
            del config['prometheusK8s']['remoteWrite']

        if enableGrafana:
            # Grafana config was removed in 4.11, pre-4.11, put it back
            config["grafana"] = copy.deepcopy(config["prometheusOperator"])

        if not keepPrometheusAdapter:
            del config['k8sPrometheusAdapter']

        cmo_config = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "cluster-monitoring-config" ,
                "namespace": "openshift-monitoring"
            },
            "data": {
                "config.yaml": yaml.dump(config)
            }
        }


        with open(configmap_path, 'w') as outfile:
            yaml.dump(cmo_config, outfile)

dump_configmap(input_file_path, output_file_path_uwm, True, False)
dump_configmap(input_file_path, output_file_path_uwm_pre_411, True, False, "7d", True, True)
dump_configmap(input_file_path, output_file_path_uwm_411_416, True, False, "7d", True, True)
dump_configmap(input_file_path, output_file_path_non_uwm, False, False)
dump_configmap(input_file_path, output_file_path_non_uwm_4_5, False, False, "11d", True, True)
dump_configmap(input_file_path, output_file_path_non_uwm_pre_411, False, False, "7d", True, True)
dump_configmap(input_file_path, output_file_path_non_uwm_411_416, False, False, "7d", True, True)
dump_configmap(input_file_path, output_file_path_fr, True, True)
dump_configmap(input_file_path, output_mc_file_path_uwm, True, False, "7d")
dump_configmap(input_file_path, output_mc_file_path_non_uwm, False, False, "7d")
