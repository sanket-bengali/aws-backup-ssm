import subprocess
import time
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

# Run post-script
execute_shell_commands(['sudo', 'service', 'httpd', 'stop'])

backup_vault_name = sys.argv[1]
resource_arn = sys.argv[2]
iam_role_arn = sys.argv[3]
region_name = sys.argv[4]

backup_client = boto3.client('backup', region_name=region_name)
backup = backup_client.start_backup_job(BackupVaultName=backup_vault_name, ResourceArn=resource_arn, IamRoleArn=iam_role_arn)
backup_job_id = backup['BackupJobId']

print("Backup job id : %s" % backup_job_id)

backup_job_details = backup_client.describe_backup_job(BackupJobId=backup_job_id)
print("Backup Job details :\n%s" % str(backup_job_details))

state = ''
counter = 0
while (state != 'COMPLETED'):

    backup_job_details = backup_client.describe_backup_job(BackupJobId=backup_job_id)
    state = backup_job_details['State']
    print("Counter : %s, Status : %s" % ((counter+1), state))

    if (state == 'COMPLETED'):
        break;

    time.sleep(30)
    counter += 1
    if (counter == 20):
        print("DB backup could not complete in 600 seconds.")
        break

# Run post-script
execute_shell_commands(['sudo', 'service', 'httpd', 'start'])
execute_shell_commands(['sudo', 'service', 'httpd', 'status'])
