#!/bin/bash
# Automatic update of chwd local repository

set -e

REPO_PATH="/var/lib/meowrch/cachyos-local"
REPO_NAME="meowrch-cachyos-local"
CACHYOS_REPO_URL="https://mirror.cachyos.org/repo/x86_64/cachyos"

# Check root privileges
if [ "$EUID" -ne 0 ]; then
    echo "Error: root privileges required"
    echo "Run: sudo $0"
    exit 1
fi

echo "=== Updating chwd local repository ==="
echo "Date: $(date)"
echo ""

cd "$REPO_PATH" || exit 1

# Get current version
CURRENT_VERSION=$(pacman -Q chwd 2>/dev/null | awk '{print $2}' || echo "not installed")
echo "Current installed version: $CURRENT_VERSION"

# Search for package in CachyOS repository
echo "Searching for package in CachyOS repository..."
PACKAGE_FILE=$(curl -s "$CACHYOS_REPO_URL/" | grep -oP 'chwd-[\d\.\-a-zA-Z_]+\.pkg\.tar\.zst(?!\.sig)' | head -n1)

if [ -z "$PACKAGE_FILE" ]; then
    echo "Error: package not found in repository"
    exit 1
fi

echo "Found package: $PACKAGE_FILE"

# Extract version from filename
NEW_VERSION=$(echo "$PACKAGE_FILE" | grep -oP 'chwd-\K[\d\.\-]+(?=-)')
echo "Version in repository: $NEW_VERSION"

# Check if update is needed
if [ -f "$PACKAGE_FILE" ]; then
    echo ""
    echo "Package $PACKAGE_FILE already exists in local repository"
    echo "Local repository is up to date"
    exit 0
fi

echo ""
echo "Updating local repository..."

# Remove old packages
echo "Removing old versions..."
rm -f chwd-*.pkg.tar.zst
rm -f "$REPO_NAME".db*
rm -f "$REPO_NAME".files*

# Download new package
echo "Downloading $PACKAGE_FILE..."
curl -L -# -o "$PACKAGE_FILE" "$CACHYOS_REPO_URL/$PACKAGE_FILE"

if [ ! -f "$PACKAGE_FILE" ]; then
    echo "Error: file was not downloaded"
    exit 1
fi

echo "Package downloaded: $(ls -lh "$PACKAGE_FILE" | awk '{print $5}')"

# Recreate repository database
echo ""
echo "Creating repository database..."
repo-add "$REPO_NAME.db.tar.zst" *.pkg.tar.zst

if [ ! -f "$REPO_NAME.db.tar.zst" ]; then
    echo "Error: database not created"
    exit 1
fi

echo ""
echo "=== Local repository successfully updated ==="
echo ""
echo "Available version: $NEW_VERSION"
echo ""
echo "To update the package run:"
echo "  sudo pacman -Syu"
echo "or:"
echo "  sudo pacman -Sy chwd"
