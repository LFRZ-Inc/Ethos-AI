# Oracle Cloud Setup for Ethos AI

## 🚀 Manual Setup Guide

### Step 1: Create Compartment
1. **Go to Oracle Cloud Console**
2. **Navigate to Identity → Compartments**
3. **Click "Create Compartment"**
4. **Fill in details:**
   - **Name**: `ethos-ai`
   - **Description**: `Compartment for Ethos AI backend and AI models`
5. **Click "Create Compartment"**
6. **Copy the Compartment OCID** (looks like `ocid1.compartment.oc1..aaaaaaaaxxxxxx`)

### Step 2: Create VCN (Virtual Cloud Network)
1. **Go to Networking → Virtual Cloud Networks**
2. **Click "Create VCN"**
3. **Fill in details:**
   - **Name**: `ethos-ai-vcn`
   - **Compartment**: Select your `ethos-ai` compartment
   - **CIDR Block**: `10.0.0.0/16`
   - **DNS Label**: `ethosai`
4. **Click "Create VCN"**

### Step 3: Create Internet Gateway
1. **In your VCN, go to "Internet Gateways"**
2. **Click "Create Internet Gateway"**
3. **Name**: `ethos-ai-igw`
4. **Click "Create Internet Gateway"**

### Step 4: Create Route Table
1. **In your VCN, go to "Route Tables"**
2. **Click "Create Route Table"**
3. **Name**: `ethos-ai-rt`
4. **Add Route Rule:**
   - **Target Type**: Internet Gateway
   - **Destination**: `0.0.0.0/0`
   - **Target**: Select your Internet Gateway
5. **Click "Create Route Table"**

### Step 5: Create Subnet
1. **In your VCN, go to "Subnets"**
2. **Click "Create Subnet"**
3. **Fill in details:**
   - **Name**: `ethos-ai-subnet`
   - **Subnet Type**: Regional
   - **CIDR Block**: `10.0.1.0/24`
   - **DNS Label**: `ethosai`
   - **Route Table**: Select your `ethos-ai-rt`
4. **Click "Create Subnet"**

### Step 6: Configure Security List
1. **In your VCN, go to "Security Lists"**
2. **Click on the default security list**
3. **Add Ingress Rules:**

#### SSH Access:
- **Source**: `0.0.0.0/0`
- **Protocol**: TCP
- **Port**: 22

#### HTTP Access:
- **Source**: `0.0.0.0/0`
- **Protocol**: TCP
- **Port**: 80

#### HTTPS Access:
- **Source**: `0.0.0.0/0`
- **Protocol**: TCP
- **Port**: 443

#### Ethos AI Backend:
- **Source**: `0.0.0.0/0`
- **Protocol**: TCP
- **Port**: 8000

### Step 7: Create VM Instance
1. **Go to Compute → Instances**
2. **Click "Create Instance"**
3. **Fill in details:**
   - **Name**: `ethos-ai-server`
   - **Compartment**: Select your `ethos-ai` compartment
   - **Placement**: Select any Availability Domain
   - **Image**: Canonical Ubuntu 22.04
   - **Shape**: VM.Standard.A1.Flex
   - **OCPUs**: 4
   - **Memory**: 24 GB
   - **Network**: Select your VCN and subnet
   - **SSH Key**: Add your public key:
   ```
   ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCmziutO5/FigF9LBXvjSqqzwRegmMJiQSYuQXEdjaSyHoPcrlqh++FKOd0S2r5eBfGQNdOwcgeGxuqJpH1IRE9oS/TQPkUMyGrXR25PqAdzh8LQoie0696HVp3gzrn59vUi7OzAg+rDhncSPPRhzzqHIHw9aIhHAFK/3mIUjWvOxAmYNWXph9mx/aD3LgrFOs1ONsceV7urqmv0k6eozgKMScKtYU/MxAVT7os/VsupyebfdfCrBlsKkRLjka6RAOLH/FNrBZvJR7jq5IWIjrBkIRck8meyZljtoLoGMwzDCFEEqxorZCb2BWzikbTr9q1OWqPJdjnrCwlwJcaLzqBnqI6QtZKL8M4/U/GIWg0gCUtA3m598G7vEIkMQFBAC4wgGNHxtB2ooUF/Nlbz1hKrQ/GFWZR4l7oe0LpizL636gYJJQ91TnFdjTkceWPM3PDFTOlKhX1veLw1Dh8XbiKf7y+Lsm4r4zZhteDiPfgBYHe1Ib4t9dMssp3gYdmYpX12FetJUnv6ZRNOvD9byRoJerNQ86GAVF0tGGqvOLkWNS9SUlmAS9L2CWaqDavem5S+z+svB3tQxu4NW0v5D3i41uQDf1N/RvrvHHGVHxDbMM6ab+XvMZo6Y+0ELJUskAYRuh/adChiFrPLwbicL00FBKcVODpB1rpe0nmvt0RDw== cooli@LuisAsusPC
   ```
4. **Click "Create Instance"**

### Step 8: Wait for VM to Start
1. **Wait for the VM status to show "Running"**
2. **Note the public IP address**

### Step 9: SSH into Your VM
```bash
ssh -i C:\Users\cooli\.ssh\oracle_cloud_key ubuntu@<YOUR_VM_PUBLIC_IP>
```

### Step 10: Install Ethos AI Backend
Once you're SSH'd into the VM, run these commands:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3 python3-pip python3-venv git curl

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Clone your Ethos AI repository
git clone https://github.com/LFRZ-Inc/Ethos-AI.git
cd Ethos-AI/backend

# Install Python dependencies
pip3 install -r requirements.txt

# Download AI models
ollama pull phi:latest
ollama pull llama2:latest
ollama pull sailor2:1b
ollama pull llama3.2:3b
ollama pull codellama:7b

# Start the backend
python3 client_storage_version.py
```

### Step 11: Update Frontend Configuration
Update your frontend to use the Oracle Cloud VM:

```typescript
// In frontend/src/config.ts
const getApiBaseUrl = () => {
  if (window.location.hostname.includes('vercel.app')) {
    return 'http://<YOUR_VM_PUBLIC_IP>:8000';
  }
  // ... rest of your config
};
```

## 🎉 Your Ethos AI is Now Running on Oracle Cloud!

**Benefits:**
- ✅ 24GB RAM (enough for all 5 AI models)
- ✅ 4 OCPUs (good performance)
- ✅ 100GB storage
- ✅ 24/7 availability
- ✅ Professional cloud infrastructure
- ✅ Free tier (forever free)

**Access your Ethos AI at:** `http://<YOUR_VM_PUBLIC_IP>:8000`
