#build ec2 for mermaid_cli host


#docker install, add current user to run, setup as system service to run 
#at start up 
sudo yum update -y
sudo yum install docker -y
sudo systemctl start docker
sudo systemctl enable docker.service
sudo systemctl enable containerd.service

#mermaid container
sudo docker pull minlag/mermaid-cli

#install git and setup the examples directory
sudo yum install git -y
git clone https://github.com/jackbrad/mmd_examples.git

#install pip, fastapi, uvicorn 
python3 -m ensurepip --upgrade
python3 -m pip install --upgrade pip

#create api
git clone https://github.com/jackbrad/fastaptest.git
cd /home/ec2-user/fastaptest
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn boto3
cp mermaid_cli.service /etc/systemd/system/

#nginx
sudo yum install git -y nginx
sudo systemctl enable --now nginx
sudo cp mermaid_cli.conf /etc/nginx/conf.d
sudo nginx -t
sudo service nginx restart

#uvicorn
sudo cp mermaid_cli.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start mermaid_cli
sudo systemctl status mermaid_cli
