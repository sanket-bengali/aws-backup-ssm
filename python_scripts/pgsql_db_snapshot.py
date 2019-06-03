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

def create_db_snapshot (client, db_instance_id, db_instance_snapshot_id):

    response = client.create_db_snapshot(
        DBSnapshotIdentifier=db_instance_snapshot_id,
        DBInstanceIdentifier=db_instance_id)

    snapshot_details = client.describe_db_snapshots(DBSnapshotIdentifier=db_instance_snapshot_id)
    print("DB instance snapshot details : %s" % str(snapshot_details))

ssh_key = sys.argv[1]
username = sys.argv[2]
host_ip = sys.argv[3]

# Pre-script
execute_shell_commands_remote(ssh_key, username, host_ip, "sudo service apache2 stop")

# DB instance backup
db_instance_id = sys.argv[4]

current_time = datetime.datetime.now()
time_string = current_time.strftime("%Y-%m-%d-%H-%M-%S")
db_instance_snapshot_id = db_instance_id + "-" + time_string
print("DB instance snapshot id : %s" % db_instance_snapshot_id)

region_name = sys.argv[5]

client = boto3.client('rds', region_name=region_name)
create_db_snapshot(client, db_instance_id, db_instance_snapshot_id)

print("Waiting for DB snapshot to be available.......")
waiter_db_snapshot = client.get_waiter('db_snapshot_available')
# max number of tries as appropriate
waiter_db_snapshot.config.max_attempts = 10
# Add a 60 second delay between attempts
waiter_db_snapshot.config.delay = 60

# Wait for snapshot to be available
waiter_db_snapshot.wait(DBSnapshotIdentifier=db_instance_snapshot_id)

snapshot_details = client.describe_db_snapshots(DBSnapshotIdentifier=db_instance_snapshot_id)
status = snapshot_details['DBSnapshots'][0]['Status']
progress = snapshot_details['DBSnapshots'][0]['PercentProgress']
print("DB snapshot is available now.")
print("Progress : %s%%, Status : %s" % (progress, status))

# Post-script
execute_shell_commands_remote(ssh_key, username, host_ip, "sudo service apache2 start")
execute_shell_commands_remote(ssh_key, username, host_ip, "sudo service apache2 status")

