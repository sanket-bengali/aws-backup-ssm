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

db_cluster_id = sys.argv[4]

current_time = datetime.datetime.now()
time_string = current_time.strftime("%Y-%m-%d-%H-%M-%S")
db_cluster_snapshot_id = db_cluster_id + "-" + time_string
print("DB snapshot id : %s" % db_cluster_snapshot_id)

# Run pre-script
execute_shell_commands_remote(ssh_key, username, host_ip, "sudo service apache2 stop")

region_name = sys.argv[5]

client = boto3.client('rds', region_name=region_name)

response = client.create_db_cluster_snapshot(
    DBClusterSnapshotIdentifier=db_cluster_snapshot_id,
    DBClusterIdentifier=db_cluster_id)

snapshot_details = client.describe_db_cluster_snapshots(DBClusterSnapshotIdentifier=db_cluster_snapshot_id)
print("DB cluster snapshot details : %s" % str(snapshot_details))

status = ''
progress = 0
counter = 0
while (status != 'available' and progress != 100):
    
    snapshot_details = client.describe_db_cluster_snapshots(DBClusterSnapshotIdentifier=db_cluster_snapshot_id)
    status = snapshot_details['DBClusterSnapshots'][0]['Status']
    progress = snapshot_details['DBClusterSnapshots'][0]['PercentProgress']
    print("Counter : %s, Progress : %s%%, Status : %s" % ((counter+1), progress, status))

    if (status == 'available' and progress == 100):
        break;

    time.sleep(30)
    counter += 1
    if (counter == 10):
        print("DB cluster snapshot could not complete in 300 seconds.")

# Run post-script
execute_shell_commands_remote(ssh_key, username, host_ip, "sudo service apache2 start")
execute_shell_commands_remote(ssh_key, username, host_ip, "sudo service apache2 status")

