# Oracle Cloud Setup Script for Ethos AI
# This script will create the necessary infrastructure for hosting Ethos AI backend

param(
    [Parameter(Mandatory=$true)]
    [string]$TenancyOCID,
    
    [Parameter(Mandatory=$true)]
    [string]$UserOCID,
    
    [Parameter(Mandatory=$true)]
    [string]$CompartmentOCID,
    
    [Parameter(Mandatory=$true)]
    [string]$Region = "us-chicago-1",
    
    [Parameter(Mandatory=$true)]
    [string]$SSHPublicKey
)

Write-Host "🚀 Setting up Oracle Cloud infrastructure for Ethos AI..." -ForegroundColor Green

# Create configuration directory
$ConfigDir = "$env:USERPROFILE\.oci"
if (!(Test-Path $ConfigDir)) {
    New-Item -ItemType Directory -Path $ConfigDir -Force
}

# Create OCI config file
$ConfigContent = @"
[DEFAULT]
user=$UserOCID
fingerprint=YOUR_FINGERPRINT_HERE
key_file=$ConfigDir\oci_api_key.pem
tenancy=$TenancyOCID
region=$Region
"@

$ConfigContent | Out-File -FilePath "$ConfigDir\config" -Encoding UTF8

Write-Host "✅ Created OCI config file at $ConfigDir\config" -ForegroundColor Green

# Create infrastructure setup script
$InfraScript = @"
#!/bin/bash
# Oracle Cloud Infrastructure Setup for Ethos AI

# Variables
TENANCY_OCID="$TenancyOCID"
COMPARTMENT_OCID="$CompartmentOCID"
REGION="$Region"
SSH_PUBLIC_KEY="$SSHPublicKey"

echo "🚀 Creating VCN (Virtual Cloud Network)..."
oci network vcn create \
    --compartment-id \$COMPARTMENT_OCID \
    --display-name "ethos-ai-vcn" \
    --cidr-block "10.0.0.0/16" \
    --dns-label "ethosai"

echo "✅ VCN created successfully"

echo "🚀 Creating Internet Gateway..."
oci network internet-gateway create \
    --compartment-id \$COMPARTMENT_OCID \
    --vcn-id \$(oci network vcn list --compartment-id \$COMPARTMENT_OCID --query "data[0].id" --raw-output) \
    --display-name "ethos-ai-igw"

echo "✅ Internet Gateway created successfully"

echo "🚀 Creating Route Table..."
VCN_ID=\$(oci network vcn list --compartment-id \$COMPARTMENT_OCID --query "data[0].id" --raw-output)
IGW_ID=\$(oci network internet-gateway list --compartment-id \$COMPARTMENT_OCID --vcn-id \$VCN_ID --query "data[0].id" --raw-output)

oci network route-table create \
    --compartment-id \$COMPARTMENT_OCID \
    --vcn-id \$VCN_ID \
    --display-name "ethos-ai-rt" \
    --route-rules '[{"destination": "0.0.0.0/0", "destinationType": "CIDR_BLOCK", "networkEntityId": "'\$IGW_ID'"}]'

echo "✅ Route Table created successfully"

echo "🚀 Creating Subnet..."
oci network subnet create \
    --compartment-id \$COMPARTMENT_OCID \
    --vcn-id \$VCN_ID \
    --display-name "ethos-ai-subnet" \
    --dns-label "ethosai" \
    --cidr-block "10.0.1.0/24" \
    --security-list-ids '["'$(oci network security-list list --compartment-id \$COMPARTMENT_OCID --vcn-id \$VCN_ID --query "data[0].id" --raw-output)'"]'

echo "✅ Subnet created successfully"

echo "🚀 Creating Security List rules..."
SECURITY_LIST_ID=\$(oci network security-list list --compartment-id \$COMPARTMENT_OCID --vcn-id \$VCN_ID --query "data[0].id" --raw-output)

# Allow SSH
oci network security-list update \
    --security-list-id \$SECURITY_LIST_ID \
    --ingress-security-rules '[{"source": "0.0.0.0/0", "protocol": "6", "tcpOptions": {"destinationPortRange": {"min": 22, "max": 22}}}]'

# Allow HTTP
oci network security-list update \
    --security-list-id \$SECURITY_LIST_ID \
    --ingress-security-rules '[{"source": "0.0.0.0/0", "protocol": "6", "tcpOptions": {"destinationPortRange": {"min": 80, "max": 80}}}]'

# Allow HTTPS
oci network security-list update \
    --security-list-id \$SECURITY_LIST_ID \
    --ingress-security-rules '[{"source": "0.0.0.0/0", "protocol": "6", "tcpOptions": {"destinationPortRange": {"min": 443, "max": 443}}}]'

# Allow custom port for Ethos AI
oci network security-list update \
    --security-list-id \$SECURITY_LIST_ID \
    --ingress-security-rules '[{"source": "0.0.0.0/0", "protocol": "6", "tcpOptions": {"destinationPortRange": {"min": 8000, "max": 8000}}}]'

echo "✅ Security List rules created successfully"

echo "🚀 Creating VM Instance..."
SUBNET_ID=\$(oci network subnet list --compartment-id \$COMPARTMENT_OCID --vcn-id \$VCN_ID --query "data[0].id" --raw-output)

oci compute instance launch \
    --compartment-id \$COMPARTMENT_OCID \
    --display-name "ethos-ai-server" \
    --availability-domain \$(oci iam availability-domain list --query "data[0].name" --raw-output) \
    --subnet-id \$SUBNET_ID \
    --image-id \$(oci compute image list --compartment-id \$COMPARTMENT_OCID --operating-system "Canonical Ubuntu" --operating-system-version "22.04" --query "data[0].id" --raw-output) \
    --shape "VM.Standard.A1.Flex" \
    --shape-config '{"ocpus": 4, "memoryInGBs": 24}' \
    --ssh-authorized-keys-file <(echo "\$SSH_PUBLIC_KEY") \
    --boot-volume-size-in-gbs 100

echo "✅ VM Instance created successfully"

echo "🎉 Oracle Cloud infrastructure setup complete!"
echo "📋 Next steps:"
echo "1. Wait for the VM to be running (check Oracle Cloud Console)"
echo "2. Get the public IP address of your VM"
echo "3. SSH into the VM: ssh -i ~/.ssh/oracle_cloud_key ubuntu@<PUBLIC_IP>"
echo "4. Install Ethos AI backend on the VM"
"@

$InfraScript | Out-File -FilePath "oracle_infrastructure_setup.sh" -Encoding UTF8

Write-Host "✅ Created infrastructure setup script: oracle_infrastructure_setup.sh" -ForegroundColor Green

Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Create a compartment named 'ethos-ai' in Oracle Cloud Console" -ForegroundColor White
Write-Host "2. Get the Compartment OCID" -ForegroundColor White
Write-Host "3. Run this script with your compartment OCID" -ForegroundColor White
Write-Host "4. Execute the generated oracle_infrastructure_setup.sh script" -ForegroundColor White

Write-Host "🔑 Your SSH Public Key:" -ForegroundColor Cyan
Write-Host $SSHPublicKey -ForegroundColor White
