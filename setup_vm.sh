#!/bin/bash
#
# Script d'installation des prérequis sur la VM de déploiement
# Ubuntu 24.04 LTS
#

set -e  # Arrêter en cas d'erreur

echo "=============================================="
echo "  Installation des outils de déploiement"
echo "  Bot Traducteur - VM de déploiement"
echo "=============================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Fonction pour afficher les étapes
step() {
    echo -e "${BLUE}[ÉTAPE]${NC} $1"
}

success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

error() {
    echo -e "${RED}[ERREUR]${NC} $1"
}

# Vérification root
if [[ $EUID -ne 0 ]]; then
   error "Ce script doit être exécuté en tant que root (sudo)"
   exit 1
fi

USER_HOME=$(eval echo ~${SUDO_USER})
INSTALL_USER=${SUDO_USER:-$USER}

echo "Installation pour l'utilisateur: $INSTALL_USER"
echo "Répertoire utilisateur: $USER_HOME"
echo ""

# ============================================
# 1. Mise à jour du système
# ============================================
step "Mise à jour du système"
apt-get update -qq
apt-get upgrade -y -qq
success "Système mis à jour"
echo ""

# ============================================
# 2. Installation des dépendances de base
# ============================================
step "Installation des dépendances de base"
apt-get install -y -qq \
    curl \
    wget \
    gnupg \
    lsb-release \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    unzip \
    jq \
    zip \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    python3-pip \
    python3-venv

success "Dépendances de base installées"
echo ""

# ============================================
# 3. Installation Azure Functions Core Tools
# ============================================
step "Installation Azure Functions Core Tools v4"

# Ajouter le repository Microsoft
wget -q https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/packages-microsoft-prod.deb
dpkg -i packages-microsoft-prod.deb
rm packages-microsoft-prod.deb

apt-get update -qq
apt-get install -y -qq azure-functions-core-tools-4

# Vérification
if command -v func &> /dev/null; then
    FUNC_VERSION=$(func --version)
    success "Azure Functions Core Tools installé: $FUNC_VERSION"
else
    error "Échec de l'installation d'Azure Functions Core Tools"
    exit 1
fi
echo ""

# ============================================
# 4. Installation Power Platform CLI
# ============================================
step "Installation Power Platform CLI"

# Power Platform CLI nécessite .NET
apt-get install -y -qq dotnet-sdk-8.0

# Installer Power Platform CLI via dotnet tool
su - $INSTALL_USER -c "dotnet tool install --global Microsoft.PowerApps.CLI.Tool"

# Ajouter au PATH si pas déjà fait
PAC_PATH="$USER_HOME/.dotnet/tools"
if ! grep -q "$PAC_PATH" "$USER_HOME/.bashrc"; then
    echo 'export PATH="$PATH:$HOME/.dotnet/tools"' >> "$USER_HOME/.bashrc"
fi

# Vérification
if su - $INSTALL_USER -c "command -v pac" &> /dev/null; then
    PAC_VERSION=$(su - $INSTALL_USER -c "pac --version" | head -1)
    success "Power Platform CLI installé: $PAC_VERSION"
else
    error "Échec de l'installation de Power Platform CLI"
    error "Vous devrez peut-être recharger votre shell: source ~/.bashrc"
fi
echo ""

# ============================================
# 5. Vérification Python et pip
# ============================================
step "Vérification Python et pip"
PYTHON_VERSION=$(python3 --version)
PIP_VERSION=$(pip3 --version)
success "Python: $PYTHON_VERSION"
success "Pip: $PIP_VERSION"
echo ""

# ============================================
# 6. Création de l'alias python
# ============================================
step "Configuration de l'alias python"
if ! grep -q "alias python='python3'" "$USER_HOME/.bashrc"; then
    echo "alias python='python3'" >> "$USER_HOME/.bashrc"
    success "Alias python='python3' ajouté"
else
    success "Alias python déjà configuré"
fi
echo ""

# ============================================
# 7. Installation des dépendances Python globales
# ============================================
step "Installation des outils Python"
pip3 install --upgrade pip
pip3 install --upgrade setuptools wheel
success "Outils Python installés"
echo ""

# ============================================
# 8. Vérification finale
# ============================================
echo ""
echo "=============================================="
echo "  VÉRIFICATION FINALE"
echo "=============================================="
echo ""

echo "✓ Système d'exploitation: $(lsb_release -ds)"
echo "✓ Python: $(python3 --version)"
echo "✓ Git: $(git --version)"
echo "✓ Azure CLI: $(az --version | head -1 | awk '{print $2}')"
echo "✓ Azure Functions Core Tools: $(func --version)"
echo "✓ .NET SDK: $(dotnet --version)"
echo "✓ Power Platform CLI: $(su - $INSTALL_USER -c 'pac --version 2>/dev/null | head -1' || echo 'Instalé (rechargez le shell)')"

echo ""
echo "=============================================="
echo -e "${GREEN}  Installation terminée avec succès !${NC}"
echo "=============================================="
echo ""
echo "IMPORTANT:"
echo "1. Rechargez votre shell pour activer les nouveaux outils:"
echo "   source ~/.bashrc"
echo ""
echo "2. Connectez-vous à Azure:"
echo "   az login"
echo ""
echo "3. Vous pouvez maintenant utiliser le script de déploiement:"
echo "   python3 deploy_client.py"
echo ""
