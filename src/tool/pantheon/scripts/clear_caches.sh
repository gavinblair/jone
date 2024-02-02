#!/bin/bash

# Assign command line parameters to variables
site_name=$1
env=$2

# Use variables in the terminus command
terminus env:clear-cache $site_name.$env

# Use variables in the say command
echo "Caches cleared for $env.$site_name"