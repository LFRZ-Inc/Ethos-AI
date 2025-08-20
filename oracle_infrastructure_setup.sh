#!/bin/bash
# Oracle Cloud Infrastructure Setup for Ethos AI
# Generated for your specific configuration

echo "🚀 Setting up Oracle Cloud infrastructure for Ethos AI..."

# Your Oracle Cloud details
TENANCY_OCID="ocid1.tenancy.oc1..aaaaaaaaarh4yq7yrr2fmxzlbsqioh2ask7pkudub2yy4kd2hj63gj7j2mvhq"
COMPARTMENT_OCID="ocid1.compartment.oc1..aaaaaaaackdia2a376x4br4x3p3mgfunjvtbs2ht67qncr4yx5s3lkroroxq"
REGION="us-chicago-1"
SSH_PUBLIC_KEY="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCmziutO5/FigF9LBXvjSqqzwRegmMJiQSYuQXEdjaSyHoPcrlqh++FKOd0S2r5eBfGQNdOwcgeGxuqJpH1IRE9oS/TQPkUMyGrXR25PqAdzh8LQoie0696HVp3gzrn59vUi7OzAg+rDhncSPPRhzzqHIHw9aIhHAFK/3mIUjWvOxAmYNWXph9mx/aD3LgrFOs1ONsceV7urqmv0k6eozgKMScKtYU/MxAVT7os/VsupyebfdfCrBlsKkRLjka6RAOLH/FNrBZvJR7jq5IWIjrBkIRck8meyZljtoLoGMwzDCFEEqxorZCb2BWzikbTr9q1OWqPJdjnrCwlwJcaLzqBnqI6QtZKL8M4/U/GIWg0gCUtA3m598G7vEIkMQFBAC4wgGNHxtB2ooUF/Nlbz1hKrQ/GFWZR4l7oe0LpizL636gYJJQ91TnFdjTkceWPM3PDFTOlKhX1veLw1Dh8XbiKf7y+Lsm4r4zZhteDiPfgBYHe1Ib4t9dMssp3gYdmYpX12FetJUnv6ZRNOvD9byRoJerNQ86GAVF0tGGqvOLkWNS9SUlmAS9L2CWaqDavem5S+z+svB3tQxu4NW0v5D3i41uQDf1N/RvrvHHGVHxDbMM6ab+XvMZo6Y+0ELJUskAYRuh/adChiFrPLwbicL00FBKcVODpB1rpe0nmvt0RDw== cooli@LuisAsusPC"

echo "📋 Using Compartment: $COMPARTMENT_OCID"
echo "📋 Using Region: $REGION"

# Step 1: Create VCN
echo "🚀 Creating VCN (Virtual Cloud Network)..."
VCN_RESPONSE=$(oci network vcn create \
    --compartment-id $COMPARTMENT_OCID \
    --display-name "ethos-ai-vcn" \
    --cidr-block "10.0.0.0/16" \
    --dns-label "ethosai" \
    --wait-for-state AVAILABLE)

VCN_ID=$(echo $VCN_RESPONSE | jq -r '.data.id')
echo "✅ VCN created successfully: $VCN_ID"

# Step 2: Create Internet Gateway
echo "🚀 Creating Internet Gateway..."
IGW_RESPONSE=$(oci network internet-gateway create \
    --compartment-id $COMPARTMENT_OCID \
    --vcn-id $VCN_ID \
    --display-name "ethos-ai-igw" \
    --wait-for-state AVAILABLE)

IGW_ID=$(echo $IGW_RESPONSE | jq -r '.data.id')
echo "✅ Internet Gateway created successfully: $IGW_ID"

# Step 3: Create Route Table
echo "🚀 Creating Route Table..."
ROUTE_TABLE_RESPONSE=$(oci network route-table create \
    --compartment-id $COMPARTMENT_OCID \
    --vcn-id $VCN_ID \
    --display-name "ethos-ai-rt" \
    --route-rules '[{"destination": "0.0.0.0/0", "destinationType": "CIDR_BLOCK", "networkEntityId": "'$IGW_ID'"}]' \
    --wait-for-state AVAILABLE)

ROUTE_TABLE_ID=$(echo $ROUTE_TABLE_RESPONSE | jq -r '.data.id')
echo "✅ Route Table created successfully: $ROUTE_TABLE_ID"

# Step 4: Get default security list
echo "🚀 Getting default security list..."
SECURITY_LIST_RESPONSE=$(oci network security-list list \
    --compartment-id $COMPARTMENT_OCID \
    --vcn-id $VCN_ID \
    --query "data[0]")

SECURITY_LIST_ID=$(echo $SECURITY_LIST_RESPONSE | jq -r '.id')
echo "✅ Using security list: $SECURITY_LIST_ID"

# Step 5: Create Subnet
echo "🚀 Creating Subnet..."
SUBNET_RESPONSE=$(oci network subnet create \
    --compartment-id $COMPARTMENT_OCID \
    --vcn-id $VCN_ID \
    --display-name "ethos-ai-subnet" \
    --dns-label "ethosai" \
    --cidr-block "10.0.1.0/24" \
    --security-list-ids "[$SECURITY_LIST_ID]" \
    --route-table-id $ROUTE_TABLE_ID \
    --wait-for-state AVAILABLE)

SUBNET_ID=$(echo $SUBNET_RESPONSE | jq -r '.data.id')
echo "✅ Subnet created successfully: $SUBNET_ID"

# Step 6: Configure Security List Rules
echo "🚀 Configuring Security List Rules..."

# Allow SSH (Port 22)
echo "  🔓 Adding SSH rule (port 22)..."
oci network security-list update \
    --security-list-id $SECURITY_LIST_ID \
    --ingress-security-rules '[{"source": "0.0.0.0/0", "protocol": "6", "tcpOptions": {"destinationPortRange": {"min": 22, "max": 22}}}]'

# Allow HTTP (Port 80)
echo "  🔓 Adding HTTP rule (port 80)..."
oci network security-list update \
    --security-list-id $SECURITY_LIST_ID \
    --ingress-security-rules '[{"source": "0.0.0.0/0", "protocol": "6", "tcpOptions": {"destinationPortRange": {"min": 80, "max": 80}}}]'

# Allow HTTPS (Port 443)
echo "  🔓 Adding HTTPS rule (port 443)..."
oci network security-list update \
    --security-list-id $SECURITY_LIST_ID \
    --ingress-security-rules '[{"source": "0.0.0.0/0", "protocol": "6", "tcpOptions": {"destinationPortRange": {"min": 443, "max": 443}}}]'

# Allow Ethos AI Backend (Port 8000)
echo "  🔓 Adding Ethos AI backend rule (port 8000)..."
oci network security-list update \
    --security-list-id $SECURITY_LIST_ID \
    --ingress-security-rules '[{"source": "0.0.0.0/0", "protocol": "6", "tcpOptions": {"destinationPortRange": {"min": 8000, "max": 8000}}}]'

echo "✅ Security List rules configured successfully"

# Step 7: Get Ubuntu 22.04 image
echo "🚀 Getting Ubuntu 22.04 image..."
IMAGE_RESPONSE=$(oci compute image list \
    --compartment-id $COMPARTMENT_OCID \
    --operating-system "Canonical Ubuntu" \
    --operating-system-version "22.04" \
    --query "data[0]")

IMAGE_ID=$(echo $IMAGE_RESPONSE | jq -r '.id')
echo "✅ Using Ubuntu 22.04 image: $IMAGE_ID"

# Step 8: Get Availability Domain
echo "🚀 Getting Availability Domain..."
AD_RESPONSE=$(oci iam availability-domain list \
    --query "data[0]")

AD_NAME=$(echo $AD_RESPONSE | jq -r '.name')
echo "✅ Using Availability Domain: $AD_NAME"

# Step 9: Create VM Instance
echo "🚀 Creating VM Instance..."
echo "  📋 Instance details:"
echo "  - Name: ethos-ai-server"
echo "  - Shape: VM.Standard.A1.Flex"
echo "  - OCPUs: 4"
echo "  - Memory: 24 GB"
echo "  - Boot Volume: 100 GB"

# Create SSH key file
echo "$SSH_PUBLIC_KEY" > /tmp/ssh_key.pub

VM_RESPONSE=$(oci compute instance launch \
    --compartment-id $COMPARTMENT_OCID \
    --display-name "ethos-ai-server" \
    --availability-domain $AD_NAME \
    --subnet-id $SUBNET_ID \
    --image-id $IMAGE_ID \
    --shape "VM.Standard.A1.Flex" \
    --shape-config '{"ocpus": 4, "memoryInGBs": 24}' \
    --ssh-authorized-keys-file /tmp/ssh_key.pub \
    --boot-volume-size-in-gbs 100 \
    --wait-for-state RUNNING)

VM_ID=$(echo $VM_RESPONSE | jq -r '.data.id')
echo "✅ VM Instance created successfully: $VM_ID"

# Get public IP
echo "🚀 Getting public IP address..."
PUBLIC_IP=$(oci compute instance list-vnics \
    --instance-id $VM_ID \
    --query "data[0].public-ip" \
    --raw-output)

echo "🎉 Oracle Cloud infrastructure setup complete!"
echo ""
echo "📋 Your Ethos AI Server Details:"
echo "  - Instance ID: $VM_ID"
echo "  - Public IP: $PUBLIC_IP"
echo "  - SSH Command: ssh -i ~/.ssh/oracle_cloud_key ubuntu@$PUBLIC_IP"
echo ""
echo "🔗 Access your Ethos AI at: http://$PUBLIC_IP:8000"
echo ""
echo "📋 Next steps:"
echo "1. SSH into your VM: ssh -i ~/.ssh/oracle_cloud_key ubuntu@$PUBLIC_IP"
echo "2. Install Ethos AI backend (see ORACLE_CLOUD_SETUP.md)"
echo "3. Update your frontend configuration to use $PUBLIC_IP"
