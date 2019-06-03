import subprocess
import sys
import datetime
import time
import boto3

def execute_shell_commands_remote(key, username, host_ip, command):
    ssh = subprocess.Popen(["ssh", "-i", key, "%s@%s" % (username, host_ip), command],
	    shell=False,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            universal_newlines=True)

    print("Command executed : %s" % command)
    
    result = ssh.stdout.readlines()
    result_string = "".join(result)
    print("Stdout :\n%s" % result_string)

    error = ssh.stderr.readlines()
    if error != []:
        error_string = "".join(error)
        print("Stderr :\n%s" % error_string)

ssh_key = sys.argv[1]
username = sys.argv[2]
host_ip = sys.argv[3]

db_cluster_snapshot_id = sys.argv[4]
db_cluster_id = db_cluster_snapshot_id + "-" + "restored"

# Run pre-script
execute_shell_commands_remote(ssh_key, username, host_ip, "sudo service apache2 stop")

region_name = sys.argv[5]

client = boto3.client('rds', region_name=region_name)

db_subnet_group_name = sys.argv[6]

response = client.restore_db_cluster_from_snapshot(
    SnapshotIdentifier=db_cluster_snapshot_id,
    DBClusterIdentifier=db_cluster_id,
    Engine='aurora-postgresql',
    DBSubnetGroupName=db_subnet_group_name)

db_cluster_details = client.describe_db_clusters(DBClusterIdentifier=db_cluster_id)
print("DB cluster snapshot restore details : %s" % str(db_cluster_details))

status = ''
progress = 0
counter = 0
while (status != 'available'):
    
    db_cluster_details = client.describe_db_clusters(DBClusterIdentifier=db_cluster_id)
    status = db_cluster_details['DBClusters'][0]['Status']
    print("Counter : %s, Status : %s" % ((counter+1), status))

    if (status == 'available'):
        break;

    time.sleep(30)
    counter += 1
    if (counter == 10):
        print("DB cluster could not be restored in 300 seconds.")
        break

# Run post-script
execute_shell_commands_remote(ssh_key, username, host_ip, "sudo service apache2 start")
execute_shell_commands_remote(ssh_key, username, host_ip, "sudo service apache2 status")
