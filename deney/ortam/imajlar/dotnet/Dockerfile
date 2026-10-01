# pq-a09-env-dotnet:1.0 — .NET ortamı, Adım 9 görev 4a (derleme ön testi)
# Taban: Microsoft'un resmî kaydındaki (MCR) SDK imajı, özetle sabit. apt/apk KULLANILMAZ.
# Ubuntu 26.04 (resolute) OpenSSL 3.5.x getirir: .NET'in MLDsa'sı Linux'ta sistem OpenSSL 3.5+'e dayanır.
FROM mcr.microsoft.com/dotnet/sdk:10.0.401-resolute@sha256:d818bb3014d94172e93820d985130135870bd1760f02588a61263a85c966860e
LABEL pq.adim="a09" pq.gorev="4a" pq.imaj="pq-a09-env-dotnet:1.0"
# GİZLİLİK: .NET CLI telemetrisi KAPALI; ilk çalıştırma ve logo iletileri kapalı.
ENV DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1 DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1 \
    DOTNET_GENERATE_ASPNET_CERTIFICATE=false NUGET_XMLDOC_MODE=skip DOTNET_CLI_UI_LANGUAGE=en
COPY yetenek /opt/pq/yetenek
RUN set -eux; echo "SURUM dotnet-sdk $(dotnet --version)"; echo "SURUM sistem $(openssl version)"; \
    echo "SURUM $(grep PRETTY_NAME /etc/os-release)"; \
    cd /opt/pq/yetenek && dotnet run -c Release 2>&1 | sed 's/^/SURUM /'; rm -rf /opt/pq/yetenek/bin /opt/pq/yetenek/obj
