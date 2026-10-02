# a10-jose-001:1 — System.IdentityModel.Tokens.Jwt 8.23.0 (packages.lock.json = experiment/environments/hedefler/JOSE-001/cikti; nuget.org, anonymous; telemetry off)
FROM pq-a09-env-dotnet:1.0
WORKDIR /opt/a/src
COPY Adaptor.csproj packages.lock.json ./
RUN dotnet restore --locked-mode
COPY Ortak.cs Adaptor.cs ./
RUN dotnet publish -c Release --no-restore -o /opt/a/bin  && echo "8.23.0" > /opt/a/HEDEF_SURUM  && sha256sum Ortak.cs Adaptor.cs | sha256sum | cut -d' ' -f1 > /opt/a/ADAPTOR_SHA256  && printf '#!/bin/sh\nexec dotnet /opt/a/bin/Adaptor.dll "$@"\n' > /usr/local/bin/adaptor && chmod +x /usr/local/bin/adaptor
ENV HEDEF_ID=JOSE-001 TARA_DERLEMELER=Microsoft.IdentityModel.Tokens,Microsoft.IdentityModel.JsonWebTokens,System.IdentityModel.Tokens.Jwt
