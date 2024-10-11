#!/bin/bash

sudo launchctl stop -w /System/Library/LaunchDaemons/ssh.plist
sudo launchctl start -w /System/Library/LaunchDaemons/ssh.plist

sudo launchctl stop com.openssh.sshd
sudo launchctl start com.openssh.sshd
