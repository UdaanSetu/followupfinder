#!/bin/bash
git remote set-url origin https://github.com/UdaanSetu/followupfinder.git
git config credential.helper ""
git -c http.extraHeader="Authorization: Basic $(echo -n 'UdaanSetu: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' | base64 | tr -d '\n')" push origin feature/backend
