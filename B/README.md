How to test web application:

* Create an EC2 with the following requirements:
    * Choose a standard amazon linux AMI
    * Create a security group with entries for ports 22 and 80
    * Enable public ip

* Ssh to the machine and do the following:
    * Install pip,Flask,requests
    * Create the file app.py with the code
    * Run python3 app.py
    * In web browser access url: http://<ec2_public_ip>/metadata

Output of my test:

When accessing url: http://3.236.178.223/metadata

The following is printed:

{"ami-id":"ami-0fff1b9a61dec8a5f","ami-launch-index":"0","ami-manifest-path":"(unknown)","block-device-mapping/":"ami\nroot","events/":"maintenance/","hostname":"ip-172-31-1-79.ec2.internal","identity-credentials/":"ec2/","instance-action":"none","instance-id":"i-0293029d3f2abd532","instance-life-cycle":"on-demand","instance-type":"t2.micro","local-hostname":"ip-172-31-1-79.ec2.internal","local-ipv4":"172.31.1.79","mac":"02:77:00:37:20:93","metrics/":"vhostmd","network/":"interfaces/","placement/":"availability-zone\navailability-zone-id\nregion","profile":"default-hvm","public-hostname":"ec2-3-236-178-223.compute-1.amazonaws.com","public-ipv4":"3.236.178.223","public-keys/":"0=rotem","reservation-id":"r-02f481d2a644c39a7","security-groups":"launch-wizard-1","services/":"domain\npartition","system":"xen-on-nitro"}