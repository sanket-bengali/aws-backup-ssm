# AWS services backup using SSM (Systems Manager)

This is a sample solution including [SSM document](https://docs.aws.amazon.com/systems-manager/latest/userguide/automation-documents-reference-details.html?shortFooter=true) and Python scripts (that uses [AWS SDK for Python](https://aws.amazon.com/sdk-for-python/)) to take diffrent AWS services backup using [AWS SSM (Systems Manager)](https://docs.aws.amazon.com/systems-manager/latest/userguide/what-is-systems-manager.html) service.

More information on [AWS Systems Manager service](https://medium.com/@sanketbengali.23/aws-systems-manager-service-b023e95810d9)

## Note

In the sample scripts, below simple flow is executed :

1. Run pre-script (ex. "sudo service apache2 stop")

2. Take backup or restore

3. Run post-script (ex. "sudo service apache2 start", "sudo service apache2 status")

Pre and post scripts execution is done in 2 scenarios :

1. Locally on the EC2 instance : with [SSM agent](https://docs.aws.amazon.com/systems-manager/latest/userguide/ssm-agent.html) installed

   SSM agent is pre-installed on AWS AMIs, and needs to be installed on other AMIs (custom AMIs).

2. Remotely on the EC2 instance using Python library (like [subprocess](https://docs.python.org/2/library/subprocess.html)) : without SSM agent installed

   There can be a dedicated EC2 instance called [Bastian host](https://en.wikipedia.org/wiki/Bastion_host), which has SSM agent installed, and from that instance, commands/scripts can be executed on other instances using SSH Client.

## SSM document

The neo4j_db_backup.json SSM document executes the backup flow, where it takes Neo4j DB backup using [Neo4j's CLI](https://neo4j.com/docs/operations-manual/current/backup/performing/)
(ex. "sudo neo4j-admin backup --backup-dir={{ backupDir }} --name={{ backupName }}")
   
Note here the input params "badkupDir" (default : "/home/ubuntu/neo4j_backups") and "backupName" (default : "graph.db-backup")

## Python scripts

### Note

1. AWS operations are done using SDK : [boto3 client for Python](https://aws.amazon.com/sdk-for-python/)

2. Input parameters :

   In the sample scripts, several input params are provided as static values or hard-coded in the scripts.

   As an improvement, these values can be retrieved from different AWS resources using SDK/CLI or passed as inputs.

3. Python library :

   To execute Linux CLI on local or remote machines, Python's in-built library [subprocess](https://docs.python.org/2/library/subprocess.html) is used.

   Additionally, each Python script is individial, hence each has its own "execute_shell_commands" to execute SSH command locally or remotely.
 
4. Waiting for backup/restore operation completion :
    
   AWS SDK has in-built "wait" functions for many services (for ex. EC2 snapshot, DB snapshot etc.).

   For those services which don't have in-built "wait" functions (for ex. Backup job, Aurora DB cluster snapshot etc.), custom wait functions can be created by polling "describe_*" method of respective resource (for ex. describe_db_cluster_snapshots, describe_backup_job).

   In the Python scripts mentioned below, such polling functions are implemented. However, they are not accurate, they cover some success scenarios and may need improvement to cover negative scenarios.

### Sample scripts

1. ec2_volume_snapshot.py

   Takes EC2 snapshot, and waits for completion.
   
   Execution : python ec2_volume_snapshot.py <volume_id> <region_name>

2. pgsql_db_snapshot.py

   Takes RDS snapshot, and waits for completion.
   
   Execution : python pgsql_db_snapshot.py <ssh_key> <user_name> <host_ip> <db_instance_id>
  
3. pgsql_db_snapshot_aws_backup.py

   Starts a backup job, and waits for completion.
   
   Execution : python pgsql_db_snapshot_aws_backup.py <backup_vault_name> <resource_arn> <iam_role_arn> <region_name>

4. aurora_pgsql_cluster_snapshot.py

   Takes Aurora DB Cluster snapshot, and waits for completion.
   
   Execution : python aurora_pgsql_cluster_snapshot.py <ssh_key> <user_name> <host_ip> <db_cluster_id>
  
5. aurora_pgsql_cluster_snapshot_restore.py

   Restores Aurora DB Cluster snapshot, and waits for completion.
   
   Execution : python aurora_pgsql_cluster_snapshot_restore.py <ssh_key> <user_name> <host_ip> <db_cluster_snapshot_id> <db_subnet_group_name>

## License

The MIT License (MIT). Please see [License File](LICENSE) for more information.
