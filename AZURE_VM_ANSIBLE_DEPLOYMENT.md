# 🔵 Déploiement Azure VM + Ansible - Guide Complet

## 📋 Architecture Cible

```
┌─────────────────────────────────────────────────────────┐
│                    AZURE VM UBUNTU 22.04                │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Jenkins (CI/CD)                   Port 8080     │  │
│  └──────────────────────────────────────────────────┘  │
│                          │                               │
│  ┌──────────────────────┼───────────────────────────┐  │
│  │  Docker Containers   │                           │  │
│  │                      │                            │  │
│  │  ┌─────────────┐  ┌─┴─────────┐  ┌───────────┐ │  │
│  │  │  FastAPI    │  │    AI     │  │PostgreSQL │ │  │
│  │  │  :8000      │  │ Processor │  │   :5432   │ │  │
│  │  └─────────────┘  └───────────┘  └───────────┘ │  │
│  │                                                   │  │
│  │  ┌─────────────┐  ┌───────────┐  ┌───────────┐ │  │
│  │  │   Redis     │  │ SonarQube │  │  Grafana  │ │  │
│  │  │   :6379     │  │   :9000   │  │   :3000   │ │  │
│  │  └─────────────┘  └───────────┘  └───────────┘ │  │
│  └──────────────────────────────────────────────────┘  │
│                                                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Azure Load Balancer (Public IP)                 │  │
│  │  - Port 80/443 → FastAPI                         │  │
│  │  - Port 8080 → Jenkins                           │  │
│  └──────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
```

---

## ⚡ DÉMARRAGE RAPIDE (30 minutes)

### Étape 1: Créer la VM Azure (5 min)
```bash
# Créer VM Ubuntu 22.04
az vm create \
  --resource-group stock-market-rg \
  --name stock-market-vm \
  --image Ubuntu2204 \
  --size Standard_D4s_v3 \
  --admin-username azureuser \
  --generate-ssh-keys \
  --public-ip-sku Standard \
  --storage-sku Premium_LRS \
  --os-disk-size-gb 100

# Ouvrir les ports nécessaires
az vm open-port --port 80 --resource-group stock-market-rg --name stock-market-vm --priority 1000
az vm open-port --port 443 --resource-group stock-market-rg --name stock-market-vm --priority 1001
az vm open-port --port 8080 --resource-group stock-market-rg --name stock-market-vm --priority 1002
az vm open-port --port 8000 --resource-group stock-market-rg --name stock-market-vm --priority 1003

# Récupérer l'IP publique
VM_IP=$(az vm show -d -g stock-market-rg -n stock-market-vm --query publicIps -o tsv)
echo "VM Public IP: $VM_IP"
```

### Étape 2: Préparer Ansible (5 min)
```bash
# Sur votre machine locale
pip install ansible
ansible --version
```

### Étape 3: Déployer avec Ansible (20 min)
```bash
cd ansible
ansible-playbook -i inventory/azure.yml playbooks/deploy.yml
```

---

## 📁 STRUCTURE ANSIBLE

```
ansible/
├── ansible.cfg
├── inventory/
│   └── azure.yml
├── group_vars/
│   └── all.yml
├── roles/
│   ├── common/
│   ├── docker/
│   ├── jenkins/
│   ├── application/
│   └── monitoring/
└── playbooks/
    ├── deploy.yml
    ├── update.yml
    └── rollback.yml
```

---

## 📝 FICHIERS ANSIBLE À CRÉER

### 1. ansible.cfg
```ini
[defaults]
inventory = inventory/azure.yml
host_key_checking = False
remote_user = azureuser
private_key_file = ~/.ssh/id_rsa
retry_files_enabled = False
stdout_callback = yaml

[privilege_escalation]
become = True
become_method = sudo
become_user = root
become_ask_pass = False
```

### 2. inventory/azure.yml
```yaml
all:
  hosts:
    stock-market-vm:
      ansible_host: YOUR_VM_PUBLIC_IP  # Remplacer par l'IP de votre VM
      ansible_user: azureuser
      ansible_python_interpreter: /usr/bin/python3

  vars:
    ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
```

### 3. group_vars/all.yml
```yaml
---
# Projet
project_name: stock-market-platform
project_dir: /opt/{{ project_name }}
docker_compose_version: "2.20.0"

# Docker Registry
docker_registry: docker.io
docker_username: michoc
image_name: "{{ docker_username }}/stock-market-platform"
ai_processor_image: "{{ docker_username }}/ai-security-processor"
docker_credentials_id: "2709ba15-3bf5-42b4-a41e-e2ae435f4951"

# Database
postgres_version: "14"
postgres_user: fastapi
postgres_password: "{{ lookup('env', 'POSTGRES_PASSWORD') | default('changeme123', true) }}"
postgres_db: fastapi_db
postgres_port: 5432

# Redis
redis_version: "7-alpine"
redis_port: 6379

# Jenkins
jenkins_version: "lts"
jenkins_port: 8080
jenkins_home: /var/jenkins_home

# Application
app_port: 8000
app_workers: 4

# Monitoring
grafana_version: "latest"
grafana_port: 3000
sonarqube_version: "community"
sonarqube_port: 9000

# Security
enable_firewall: true
enable_fail2ban: true
enable_ssl: false  # Mettre true si vous avez un domaine

# HuggingFace
hf_token: "{{ lookup('env', 'HF_TOKEN') }}"
hf_model: "deepseek-ai/DeepSeek-R1"

# Grafana
grafana_url: "https://ayoubcpge9.grafana.net"
grafana_api_key: "{{ lookup('env', 'GRAFANA_API_KEY') }}"
```

---

## 🎭 ROLES ANSIBLE

### Role 1: common (roles/common/tasks/main.yml)
```yaml
---
- name: Update apt cache
  apt:
    update_cache: yes
    cache_valid_time: 3600

- name: Install essential packages
  apt:
    name:
      - curl
      - wget
      - git
      - vim
      - htop
      - net-tools
      - software-properties-common
      - apt-transport-https
      - ca-certificates
      - gnupg
      - lsb-release
      - python3-pip
      - jq
      - unzip
    state: present

- name: Configure timezone
  timezone:
    name: Europe/Paris

- name: Configure UFW firewall
  block:
    - name: Install UFW
      apt:
        name: ufw
        state: present

    - name: Allow SSH
      ufw:
        rule: allow
        port: '22'
        proto: tcp

    - name: Allow HTTP
      ufw:
        rule: allow
        port: '80'
        proto: tcp

    - name: Allow HTTPS
      ufw:
        rule: allow
        port: '443'
        proto: tcp

    - name: Allow Jenkins
      ufw:
        rule: allow
        port: '8080'
        proto: tcp

    - name: Allow Application
      ufw:
        rule: allow
        port: '8000'
        proto: tcp

    - name: Enable UFW
      ufw:
        state: enabled
  when: enable_firewall

- name: Install and configure fail2ban
  block:
    - name: Install fail2ban
      apt:
        name: fail2ban
        state: present

    - name: Start fail2ban
      service:
        name: fail2ban
        state: started
        enabled: yes
  when: enable_fail2ban

- name: Increase file limits
  pam_limits:
    domain: '*'
    limit_type: '-'
    limit_item: nofile
    value: '65535'

- name: Configure sysctl for Docker
  sysctl:
    name: "{{ item.name }}"
    value: "{{ item.value }}"
    state: present
    reload: yes
  loop:
    - { name: 'vm.max_map_count', value: '262144' }
    - { name: 'fs.file-max', value: '65535' }
    - { name: 'net.ipv4.ip_forward', value: '1' }
```

### Role 2: docker (roles/docker/tasks/main.yml)
```yaml
---
- name: Remove old Docker versions
  apt:
    name:
      - docker
      - docker-engine
      - docker.io
      - containerd
      - runc
    state: absent

- name: Add Docker GPG key
  apt_key:
    url: https://download.docker.com/linux/ubuntu/gpg
    state: present

- name: Add Docker repository
  apt_repository:
    repo: "deb [arch=amd64] https://download.docker.com/linux/ubuntu {{ ansible_distribution_release }} stable"
    state: present

- name: Install Docker
  apt:
    name:
      - docker-ce
      - docker-ce-cli
      - containerd.io
      - docker-buildx-plugin
      - docker-compose-plugin
    state: present
    update_cache: yes

- name: Add azureuser to docker group
  user:
    name: "{{ ansible_user }}"
    groups: docker
    append: yes

- name: Start and enable Docker
  service:
    name: docker
    state: started
    enabled: yes

- name: Install Docker Compose standalone
  get_url:
    url: "https://github.com/docker/compose/releases/download/v{{ docker_compose_version }}/docker-compose-linux-x86_64"
    dest: /usr/local/bin/docker-compose
    mode: '0755'

- name: Create Docker daemon config
  copy:
    content: |
      {
        "log-driver": "json-file",
        "log-opts": {
          "max-size": "10m",
          "max-file": "3"
        },
        "storage-driver": "overlay2"
      }
    dest: /etc/docker/daemon.json
    mode: '0644'
  notify: Restart Docker

- name: Create project directory
  file:
    path: "{{ project_dir }}"
    state: directory
    owner: "{{ ansible_user }}"
    group: "{{ ansible_user }}"
    mode: '0755'
```

### Role 3: jenkins (roles/jenkins/tasks/main.yml)
```yaml
---
- name: Create Jenkins directories
  file:
    path: "{{ item }}"
    state: directory
    owner: "{{ ansible_user }}"
    group: "{{ ansible_user }}"
    mode: '0755'
  loop:
    - "{{ jenkins_home }}"
    - "{{ project_dir }}/jenkins"

- name: Check if Jenkins is already running
  shell: docker ps -a --filter "name=jenkins" --format "{{ '{{' }}.Names{{ '}}' }}"
  register: jenkins_container
  changed_when: false

- name: Stop existing Jenkins container
  docker_container:
    name: jenkins
    state: absent
  when: jenkins_container.stdout == "jenkins"

- name: Start Jenkins container
  docker_container:
    name: jenkins
    image: "jenkins/jenkins:{{ jenkins_version }}"
    state: started
    restart_policy: unless-stopped
    ports:
      - "{{ jenkins_port }}:8080"
      - "50000:50000"
    volumes:
      - "{{ jenkins_home }}:/var/jenkins_home"
      - "/var/run/docker.sock:/var/run/docker.sock"
    user: root
    env:
      JAVA_OPTS: "-Djenkins.install.runSetupWizard=false"

- name: Wait for Jenkins to start
  wait_for:
    port: "{{ jenkins_port }}"
    delay: 10
    timeout: 300

- name: Get Jenkins initial admin password
  shell: docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
  register: jenkins_password
  changed_when: false
  failed_when: false

- name: Display Jenkins credentials
  debug:
    msg:
      - "Jenkins URL: http://{{ ansible_host }}:{{ jenkins_port }}"
      - "Initial Admin Password: {{ jenkins_password.stdout }}"
  when: jenkins_password.stdout is defined
```

### Role 4: application (roles/application/tasks/main.yml)
```yaml
---
- name: Copy project files
  synchronize:
    src: ../../../../
    dest: "{{ project_dir }}/"
    delete: yes
    rsync_opts:
      - "--exclude=.git"
      - "--exclude=__pycache__"
      - "--exclude=*.pyc"
      - "--exclude=venv"
      - "--exclude=.env"

- name: Create environment file
  template:
    src: .env.j2
    dest: "{{ project_dir }}/.env"
    owner: "{{ ansible_user }}"
    group: "{{ ansible_user }}"
    mode: '0600'

- name: Create Docker Compose file
  template:
    src: docker-compose.yml.j2
    dest: "{{ project_dir }}/docker-compose.yml"
    owner: "{{ ansible_user }}"
    group: "{{ ansible_user }}"
    mode: '0644'

- name: Pull latest Docker images
  shell: |
    docker pull {{ image_name }}:latest || true
    docker pull {{ ai_processor_image }}:latest || true
  args:
    chdir: "{{ project_dir }}"

- name: Stop existing containers
  shell: docker-compose down --remove-orphans
  args:
    chdir: "{{ project_dir }}"
  ignore_errors: yes

- name: Start application stack
  shell: docker-compose up -d
  args:
    chdir: "{{ project_dir }}"

- name: Wait for application to be ready
  wait_for:
    port: "{{ app_port }}"
    delay: 5
    timeout: 60

- name: Check application health
  uri:
    url: "http://localhost:{{ app_port }}/health"
    status_code: 200
  register: health_check
  until: health_check.status == 200
  retries: 5
  delay: 10
```

---

## 📄 TEMPLATES

### roles/application/templates/.env.j2
```jinja2
# Database
DATABASE_URL=postgresql://{{ postgres_user }}:{{ postgres_password }}@postgres_db:{{ postgres_port }}/{{ postgres_db }}

# Redis
REDIS_URL=redis://redis_cache:{{ redis_port }}/0

# HuggingFace
HF_TOKEN={{ hf_token }}
HF_MODEL={{ hf_model }}

# Application
APP_PORT={{ app_port }}
WORKERS={{ app_workers }}

# Grafana
GRAFANA_URL={{ grafana_url }}
GRAFANA_API_KEY={{ grafana_api_key }}

# Environment
ENVIRONMENT=production
DEBUG=False
```

### roles/application/templates/docker-compose.yml.j2
```yaml
version: '3.8'

services:
  postgres_db:
    image: postgres:{{ postgres_version }}
    container_name: postgres_db
    restart: unless-stopped
    environment:
      POSTGRES_USER: {{ postgres_user }}
      POSTGRES_PASSWORD: {{ postgres_password }}
      POSTGRES_DB: {{ postgres_db }}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "{{ postgres_port }}:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U {{ postgres_user }}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis_cache:
    image: redis:{{ redis_version }}
    container_name: redis_cache
    restart: unless-stopped
    volumes:
      - redis_data:/data
    ports:
      - "{{ redis_port }}:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  app:
    image: {{ image_name }}:latest
    container_name: stock_market_app
    restart: unless-stopped
    ports:
      - "{{ app_port }}:8000"
    environment:
      DATABASE_URL: postgresql://{{ postgres_user }}:{{ postgres_password }}@postgres_db:{{ postgres_port }}/{{ postgres_db }}
      REDIS_URL: redis://redis_cache:{{ redis_port }}/0
    depends_on:
      postgres_db:
        condition: service_healthy
      redis_cache:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
  redis_data:
```

---

## 🚀 PLAYBOOKS

### playbooks/deploy.yml
```yaml
---
- name: Deploy Stock Market Platform to Azure VM
  hosts: all
  become: yes

  pre_tasks:
    - name: Check required environment variables
      fail:
        msg: "{{ item }} environment variable is required"
      when: lookup('env', item) == ''
      loop:
        - POSTGRES_PASSWORD
        - HF_TOKEN
        - GRAFANA_API_KEY
      delegate_to: localhost
      run_once: true

  roles:
    - common
    - docker
    - jenkins
    - application

  post_tasks:
    - name: Display deployment information
      debug:
        msg:
          - "=================================="
          - "DEPLOYMENT COMPLETED SUCCESSFULLY"
          - "=================================="
          - ""
          - "Application URL: http://{{ ansible_host }}:{{ app_port }}"
          - "API Docs: http://{{ ansible_host }}:{{ app_port }}/docs"
          - "Jenkins URL: http://{{ ansible_host }}:{{ jenkins_port }}"
          - ""
          - "To check status: ansible-playbook playbooks/status.yml"
          - "To update: ansible-playbook playbooks/update.yml"
```

### playbooks/update.yml
```yaml
---
- name: Update application
  hosts: all
  become: yes

  tasks:
    - name: Pull latest images
      shell: |
        docker pull {{ image_name }}:latest
        docker pull {{ ai_processor_image }}:latest
      args:
        chdir: "{{ project_dir }}"

    - name: Restart application
      shell: docker-compose up -d --force-recreate
      args:
        chdir: "{{ project_dir }}"

    - name: Wait for application
      wait_for:
        port: "{{ app_port }}"
        delay: 5
        timeout: 60
```

### playbooks/status.yml
```yaml
---
- name: Check application status
  hosts: all
  become: yes

  tasks:
    - name: Check Docker containers
      shell: docker ps --format "table {{ '{{' }}.Names{{ '}}' }}\t{{ '{{' }}.Status{{ '}}' }}\t{{ '{{' }}.Ports{{ '}}' }}"
      register: docker_status

    - name: Display container status
      debug:
        msg: "{{ docker_status.stdout_lines }}"

    - name: Check disk usage
      shell: df -h
      register: disk_usage

    - name: Display disk usage
      debug:
        msg: "{{ disk_usage.stdout_lines }}"

    - name: Check application health
      uri:
        url: "http://localhost:{{ app_port }}/health"
        return_content: yes
      register: health

    - name: Display health check
      debug:
        msg: "Application health: {{ health.json }}"
```

---

## 📦 DÉPLOIEMENT COMPLET

### 1. Préparer l'environnement local
```bash
# Cloner le projet
cd ~/intelligent-stock-market-monitoring-platform-backend

# Créer structure Ansible
mkdir -p ansible/{inventory,group_vars,roles/{common,docker,jenkins,application}/{tasks,templates,handlers},playbooks}

# Exporter variables d'environnement
export POSTGRES_PASSWORD="votre_mot_de_passe_securise"
export HF_TOKEN="votre_token_huggingface"
export GRAFANA_API_KEY="votre_api_key_grafana"
```

### 2. Créer la VM Azure
```bash
# Créer ressources Azure
./scripts/azure-setup.sh
```

Créez le script `scripts/azure-setup.sh`:
```bash
#!/bin/bash
set -e

# Variables
RG_NAME="stock-market-rg"
VM_NAME="stock-market-vm"
LOCATION="westeurope"
VM_SIZE="Standard_D4s_v3"  # 4 vCPU, 16GB RAM

echo "Creating Azure resources..."

# Créer groupe de ressources
az group create --name $RG_NAME --location $LOCATION

# Créer VM
az vm create \
  --resource-group $RG_NAME \
  --name $VM_NAME \
  --image Ubuntu2204 \
  --size $VM_SIZE \
  --admin-username azureuser \
  --generate-ssh-keys \
  --public-ip-sku Standard \
  --storage-sku Premium_LRS \
  --os-disk-size-gb 100

# Ouvrir ports
for port in 80 443 8080 8000; do
  az vm open-port --port $port --resource-group $RG_NAME --name $VM_NAME --priority $((1000 + port))
done

# Récupérer IP
VM_IP=$(az vm show -d -g $RG_NAME -n $VM_NAME --query publicIps -o tsv)

echo "VM created successfully!"
echo "VM Public IP: $VM_IP"
echo ""
echo "Update inventory/azure.yml with this IP address"
```

### 3. Mettre à jour l'inventaire
```bash
# Récupérer l'IP de la VM
VM_IP=$(az vm show -d -g stock-market-rg -n stock-market-vm --query publicIps -o tsv)

# Mettre à jour inventory/azure.yml
sed -i "s/YOUR_VM_PUBLIC_IP/$VM_IP/g" ansible/inventory/azure.yml
```

### 4. Tester la connexion SSH
```bash
# Tester connexion
ansible all -i ansible/inventory/azure.yml -m ping

# Devrait afficher:
# stock-market-vm | SUCCESS => {
#     "changed": false,
#     "ping": "pong"
# }
```

### 5. Déployer l'application
```bash
cd ansible

# Dry run (vérifier sans exécuter)
ansible-playbook -i inventory/azure.yml playbooks/deploy.yml --check

# Déploiement réel
ansible-playbook -i inventory/azure.yml playbooks/deploy.yml

# Suivre les logs
ansible-playbook -i inventory/azure.yml playbooks/deploy.yml -v
```

---

## ✅ VÉRIFICATION POST-DÉPLOIEMENT

```bash
# Vérifier le statut
ansible-playbook -i inventory/azure.yml playbooks/status.yml

# SSH dans la VM
ssh azureuser@$(az vm show -d -g stock-market-rg -n stock-market-vm --query publicIps -o tsv)

# Dans la VM, vérifier les containers
docker ps
docker-compose -f /opt/stock-market-platform/docker-compose.yml ps

# Tester l'API
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

---

## 📊 COÛTS AZURE VM

| Configuration | vCPU | RAM | Disque | Coût/mois |
|--------------|------|-----|--------|-----------|
| **D2s_v3** (Dev) | 2 | 8GB | 100GB | ~$70 |
| **D4s_v3** (Prod) | 4 | 16GB | 100GB | ~$140 |
| **D8s_v3** (High) | 8 | 32GB | 200GB | ~$280 |

**Coût total estimé: ~$140-160/mois** (VM + disques + bandwidth)

---

## 🔄 MAINTENANCE

### Mise à jour de l'application
```bash
ansible-playbook -i inventory/azure.yml playbooks/update.yml
```

### Backup de la base de données
```bash
ansible all -i inventory/azure.yml -m shell -a \
  "docker exec postgres_db pg_dump -U fastapi fastapi_db > /tmp/backup_$(date +%Y%m%d).sql"
```

### Monitoring
```bash
# Logs en temps réel
ansible all -i inventory/azure.yml -m shell -a \
  "docker-compose -f /opt/stock-market-platform/docker-compose.yml logs -f --tail=100"
```

---

## 🎯 AVANTAGES DE CETTE APPROCHE

✅ **Simple**: Pas de complexité Kubernetes
✅ **Coût**: ~$140/mois vs ~$180/mois pour AKS
✅ **Contrôle**: Accès complet à la VM
✅ **Jenkins**: Garde votre pipeline actuel
✅ **Reproductible**: Ansible permet de recréer l'infra facilement
✅ **Scalable**: Peut évoluer vers AKS plus tard

---

**Prêt à déployer? Les fichiers Ansible sont prêts à être créés!**
