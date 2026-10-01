# a10-sdjwt-021:1 — WalletFramework.SdJwtVc 3.1.0 (packages.lock.json = deney/ortam/hedefler/SDJWT-021/cikti; nuget.org, anonim; telemetri kapalı)
FROM pq-a09-env-dotnet:1.0
WORKDIR /opt/a/src
COPY Adaptor.csproj packages.lock.json ./
RUN dotnet restore --locked-mode
COPY Ortak.cs Adaptor.cs ./
RUN dotnet publish -c Release --no-restore -o /opt/a/bin  && echo "3.1.0" > /opt/a/HEDEF_SURUM  && sha256sum Ortak.cs Adaptor.cs | sha256sum | cut -d' ' -f1 > /opt/a/ADAPTOR_SHA256  && printf '#!/bin/sh\nexec dotnet /opt/a/bin/Adaptor.dll "$@"\n' > /usr/local/bin/adaptor && chmod +x /usr/local/bin/adaptor
ENV HEDEF_ID=SDJWT-021 TARA_DERLEMELER=WalletFramework.SdJwtVc,WalletFramework.SdJwtLib,WalletFramework.Core,Microsoft.IdentityModel.Tokens,Microsoft.IdentityModel.JsonWebTokens
