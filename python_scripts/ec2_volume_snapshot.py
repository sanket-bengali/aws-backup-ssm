import subprocess
import sys
import boto3

def execute_shell_commands(commands):
    MyOut = subprocess.Popen(commands,
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT)
    stdout,stderr = MyOut.communicate()
    
    #for command in commands:
    command_string = " ".join(commands)
    print("Command executed : %s" % command_string)
    if stdout is not None:
        stdout = stdout.decode("utf-8")
        print("Stdout :\n%s" % stdout)
    if stderr is not None:
        stderr = stderr.decode("utf-8")
        print("Stderr :\n%s" % stderr)

# Run pre-script
execute_shell_commands(['sudo', 'service', 'apache2', 'stop'])

volume_id = sys.argv[1]

region_name = sys.argv[2]

ec2 = boto3.resource('ec2', region_name=region_name)
volume = ec2.Volume(volume_id)
snapshot = volume.create_snapshot()
snapshot.wait_until_completed()

ec2_client = boto3.client('ec2', region_name=region_name)
snapshot_details = ec2_client.describe_snapshots(SnapshotIds=[snapshot.id])
print("Snapshot details :\n%s" % snapshot_details)

# Run post-script
execute_shell_commands(['sudo', 'service', 'apache2', 'start'])
execute_shell_commands(['sudo', 'service', 'apache2', 'status'])
