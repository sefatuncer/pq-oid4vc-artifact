#!/usr/bin/env bash
# BİLGİ (derleme-sonuc.csv dışı): go-cose çerçeve HEAD commit'i (CERCEVE son_commit_sha) derlenebiliyor mu? İmza doğrulama YOK.
export MODUL=github.com/veraison/go-cose SURUM=dea543bf9b89b0cef461c0d194747c9ed5e6666c
exec bash /b/go.sh
