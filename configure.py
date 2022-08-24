import os, sys, yaml, json, shutil, subprocess
from read_yaml import read

class configure:
    def __init__(self, value_yaml_file, logging):
        self.logging = logging
        self.file_home_dir = os.path.dirname(os.path.realpath(__file__))
        self.file = read(value_yaml_file, logging)
        self.config = self.file.get_config()
    
    def run_cmd(self, cmd, custom_error_output="task failed"):
        process = subprocess.run(['/bin/bash', '-c', cmd], stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        if(process.returncode != 0):
            self.logging.error(cmd+"\n"+process.stdout.decode('utf-8')+"\n")
            self.logging.error("Task exit with status: "+str(process.returncode))
            print("ERROR "+custom_error_output+". Please check logs for details.")
            exit(process.returncode)
        else:
            self.logging.debug(process.stdout.decode('utf-8')+"\n")
        return str(process.stdout.decode('utf-8'))
        
    def configure_labels(self):
        self.logging.info("Adding SS8 labels")
        for node_dict in self.config["nodes"]:
            self.logging.debug("Node name: "+str(list(node_dict.keys())))
            for node in node_dict.keys():
                for item in  node_dict[node].keys():
                    if (item == "labels"):
                        self.logging.debug("- Labels: "+str(node_dict[node].values()))
                        for label in node_dict[node][item]:
                            cmd = "kubectl label node --overwrite " + node +" "+ label +"="+ node_dict[node][item][label]
                            self.logging.debug("- CMD: "+cmd)
                            self.run_cmd(cmd, custom_error_output="Adding "+item+" "+label+" to node "+node+" failed")
                    else:
                        print("ERROR "+str(item)+" is not supported, skipping")
    
    def configure_resource_quota(self):
        self.logging.info("Applying SS8 resource quotas")
        # load resource template
        try:
            with open(self.file_home_dir+"/templates/resourcequota.yaml", 'r') as file:
                template = yaml.safe_load(file)
        except:
            self.logging.error("ERROR was not able to read template:"+self.file_home_dir+"/templates/resourcequota.yaml")
            exit(1)
            
        # remove old file create from template if they exist
        if os.path.exists(self.file_home_dir+"/yamls/") and os.path.isdir(self.file_home_dir+"/yamls/"):
            shutil.rmtree(self.file_home_dir+"/yamls/")
        os.makedirs(self.file_home_dir+"/yamls/")
        
        # generating resources quota yaml for each namespace
        self.logging.debug(("Original: "+str(template)))
#        print(("Original: "+str(template)))
#        print(self.config)
        for quota_dict in self.config["resourceQuota"]:
            #self.logging.info("Creating resource quota for namespace: "+str(list(quota_dict.keys())[0]))
            #print(namespace)
#            print(self.namespace_exist)
            for namespace in quota_dict.keys():
                cmd = [self.file_home_dir+"/check_namespace.sh", namespace]
                subprocess.run(cmd)
 #               if (not self.namespace_exist(namespace)):
 #                   self.create_namespace(namespace)
                self.logging.info("Creating resource quota for namespace: "+namespace)
                template["metadata"]["name"]="ss8-"+namespace+"-resourcequota"
                template["metadata"]["namespace"]=namespace
                template["spec"]=quota_dict[namespace]
                self.logging.debug(("ss8-"+namespace+"-resourcequota.yaml: \n"+yaml.dump(template)))
                with open(self.file_home_dir+"/yamls/ss8-"+namespace+"-resourcequota.yaml", "w") as write:
                    write.write(yaml.dump(template))
                #cmd = "kubectl apply -f "+ self.file_home_dir + "/yamls/ss8-" + namespace + "-resourcequota.yaml"
                subprocess.run(["kubectl apply -f "+ self.file_home_dir + "/yamls/ss8-" + namespace + "-resourcequota.yaml"], shell=True)
   #             self.run_cmd(cmd)
            
            
    
