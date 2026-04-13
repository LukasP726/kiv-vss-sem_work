# KIV VSS Semester Work

Repo obsahuje NetLogo modely (`examples/virus1..4.nlogox`) a skripty pro automatizované BehaviorSpace experimenty.

## Možnosti spuštění skriptů (testů)

1. Lokální spuštění skriptů ze složky `scripts` (`.ps1` na Windows, `.sh` na Linuxu) při lokálně nainstalovaném NetLogo `7.0.3`; na Linuxu je k dispozici zjednodušené spuštění přes `Makefile`.
2. Spuštění experimentů v Docker kontejneru bez lokální instalace NetLogo/Java/Python; požadován je Docker.

## Možnosti spuštění jednotlivých simulací (GUI)

1. Lokální spuštění NetLogo GUI na vlastním stroji s nainstalovaným NetLogo `7.0.3`.
2. Spuštění NetLogo GUI z Docker kontejneru na Linuxu s X11 forwardingem.
(Na Windows (včetně WSL) není spuštění NetLogo GUI z Docker kontejneru podporováno.)

## Požadavky

### Lokální běh

- NetLogo `7.0.3` (stažené lokálně)
- Java/JDK (na Linuxu doporučeně nainstalované; kontrola přes `java --version`)
- Python 3 (kvůli `scripts/aggregate_results.py`)
- Linux: spustitelné shell skripty (`chmod +x scripts/*.sh`)

### Běh přes Docker

- Docker Engine / Docker Desktop

## Rychlé spuštění přes Makefile (Linux)

Nastavení cesty k NetLogo přes proměnnou `NETLOGO`:

```bash
make baseline NETLOGO="/path/to/NetLogo-7.0.3"
make extended NETLOGO="/path/to/NetLogo-7.0.3"
make all NETLOGO="/path/to/NetLogo-7.0.3"
```

Bez předání `NETLOGO` se použije výchozí hodnota z `Makefile` (`/opt/NetLogo-7.0.3`), která na konkrétním systému nemusí existovat.

## Známý problém na Linuxu (`Could not find or load main class []`)

U některých distribucí/archivů NetLogo může být v `netlogo-headless.sh` chybně vložený token `[]` v `JVM_OPTS`, což rozbije start headless režimu.

Projev v logu:

```text
Error: Could not find or load main class []
Caused by: java.lang.ClassNotFoundException: []
```

Rychlá oprava:

```bash
sed -i "s/ \[\])/)/" "/path/to/NetLogo-7.0.3/netlogo-headless.sh"
```

Následné ověření:

```bash
"/path/to/NetLogo-7.0.3/netlogo-headless.sh" --help
```

## Spuštění přes Docker (bez lokální instalace NetLogo/Java)

Sestavení image:

```bash
docker build -t kiv-vss-sem .
```

Spuštění baseline experimentů:

```bash
docker run --rm -v "$(pwd):/workspace" kiv-vss-sem make baseline
```

Alternativa pouze pro export výstupů (bez mountu celého projektu):

```bash
docker run --rm -v "$(pwd)/out:/workspace/out" kiv-vss-sem make baseline
```

Spuštění rozšířených experimentů:

```bash
docker run --rm -v "$(pwd):/workspace" kiv-vss-sem make extended
```

Spuštění všech experimentů:

```bash
docker run --rm -v "$(pwd):/workspace" kiv-vss-sem make all
```

Image deklaruje volume `"/workspace/out"`. Výstupy je vhodné mapovat na host (`-v "$(pwd)/out:/workspace/out"`), případně mapovat celý projekt (`-v "$(pwd):/workspace"`).

Interaktivní shell v image:

```bash
docker run --rm -it kiv-vss-sem /bin/bash
```

Image obsahuje kopii projektu z času buildu (`COPY . /workspace`).
Pro práci s aktuálním lokálním stavem repozitáře je vhodné použít bind mount:

```bash
docker run --rm -it -v "$(pwd):/workspace" kiv-vss-sem /bin/bash
```

## Spuštění NetLogo GUI v Dockeru (Linux/X11)

NetLogo GUI (`NetLogo_Console`) vyžaduje X11 display z host systému. Tato varianta je určena pro Linux a není podporována na Windows ani ve WSL.

Povolení lokálního přístupu na X server:

```bash
xhost +local:docker
```

Spuštění GUI aplikace z kontejneru:

```bash
docker run --rm -it \
  -e DISPLAY="$DISPLAY" \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v "$HOME/.Xauthority:/root/.Xauthority:ro" \
  -v "$(pwd):/workspace" \
  kiv-vss-sem /opt/NetLogo-7.0.3/NetLogo_Console
```

Po ukončení je možné oprávnění zase odebrat:

```bash
xhost -local:docker
```

Bez mapování `DISPLAY` a `/tmp/.X11-unix` dojde k chybě `java.awt.HeadlessException`.

## Další dokumentace

- Detailní workflow a příklady příkazů jsou v `scripts/automation.md`.
