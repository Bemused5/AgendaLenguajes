# syntax=docker/dockerfile:1

################################################################################
# 1) STAGE «builder»: instalamos Wine (multi-arch desde los repos oficiales),
#    Python para Windows dentro de Wine, y PyInstaller
################################################################################
FROM ubuntu:22.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive
ENV WINEPREFIX=/wine

# 1.1) Habilitamos i386 y multiverse/universe para poder instalar Wine
RUN dpkg --add-architecture i386 \
 && apt-get update \
 && apt-get install -y --no-install-recommends \
      software-properties-common \
 && add-apt-repository universe \
 && add-apt-repository multiverse \
 && apt-get update

# 1.2) Instalamos Wine meta-paquete (trae wine64 + wine32 + wineboot), plus utilidades
RUN apt-get install -y --no-install-recommends \
      wine \
      wget \
      curl \
      ca-certificates \
      cabextract \
      python3 \
      python3-pip \
      build-essential \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /src

# 1.3) Instalamos un Python real de Windows dentro de Wine para que PyInstaller funcione
RUN wget https://www.python.org/ftp/python/3.10.9/python-3.10.9-amd64.exe -O python-win.exe \
 && wine python-win.exe /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1 \
 && rm python-win.exe

# 1.4) Copiamos requirements.txt e instalamos las dependencias Windows via wine-pip
COPY requirements.txt .
RUN wine pip install --upgrade pip \
 && wine pip install --no-cache-dir -r requirements.txt pyinstaller

# 1.5) Copiamos el resto del código y generamos el .exe
COPY . .
RUN wine pyinstaller --name myapp --onefile --windowed main.py


################################################################################
# 2) STAGE «export»: extraemos el exe final
################################################################################
FROM scratch AS export
COPY --from=builder /src/dist/myapp.exe /myapp.exe
ENTRYPOINT ["/myapp.exe"]
