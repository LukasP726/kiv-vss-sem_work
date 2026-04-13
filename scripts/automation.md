# Automatizace experimentů (NetLogo)

Tento dokument popisuje, jak spouštět experimenty replikovatelně a bez ručního klikání.

## 1) Doporučený workflow

1. V každém modelu (`virus1`..`virus4`) vytvoř v BehaviorSpace experiment(y):
   - stejné názvy scénářů napříč modely (např. `baseline`, `ofat_transmission`, `combo_capacity_resources`)
   - repetitions = `10`
   - `run metrics every step` zapnout jen pokud opravdu potřebuješ časové řady
   - jinak sbírat jen finální metriky (rychlejší běh)
2. Spouštěj headless přes skript `scripts/run_behaviorspace.ps1` (Windows) nebo `scripts/run_behaviorspace.sh` (Linux/WSL).
3. Výstupy CSV agreguj skriptem `aggregate_results.py`.

## 2) Headless běh

Použij PowerShell skript:

```powershell
.\scripts\run_behaviorspace.ps1 `
  -NetLogoPath "C:\Program Files\NetLogo 7.0.0\NetLogo_Console.exe" `
  -ModelPath ".\examples\virus4.nlogox" `
  -ExperimentName "baseline_auto" `
  -OutputCsv ".\out\virus4_baseline.csv"
```

Linux/WSL:

```bash
./scripts/run_behaviorspace.sh \
  "/opt/NetLogo-7.0.3" \
  "./examples/virus4.nlogox" \
  "baseline_auto" \
  "./out/virus4_baseline.csv"
```

## 3) Agregace výsledků

```powershell
python .\scripts\aggregate_results.py `
  --input ".\out\virus4_baseline.csv" `
  --metrics "m_final_susceptible,m_final_exposed,m_final_infected,m_final_recovered,m_ever_infected,m_ticks,m_deaths,m_final_resources" `
  --output ".\out\virus4_baseline_summary.csv"
```

> Pozn.: V modelech jsou připravené reportery metrik se jmény `m_*`, aby byly výstupní sloupce konzistentní.

## 4) Hromadný běh všech baseline scénářů

Použij skript:

```powershell
.\scripts\run_all_baselines.ps1 `
  -NetLogoPath "C:\Program Files\NetLogo 7.0.3\NetLogo_Console.exe"
```

Linux/WSL:

```bash
./scripts/run_all_baselines.sh "/opt/NetLogo-7.0.3"
```

Ten vytvoří:
- raw CSV soubory v `.\out\`
- agregované summary CSV soubory v `.\out\`

## 5) Rozšířené experimenty (OFAT + kombinace)

PowerShell:

```powershell
.\scripts\run_extended_experiments.ps1 `
  -NetLogoPath "C:\Program Files\NetLogo 7.0.3\NetLogo_Console.exe"
```

Linux/WSL:

```bash
./scripts/run_extended_experiments.sh "/opt/NetLogo-7.0.3"
```

## 6) První spuštění v Linux/WSL

```bash
chmod +x scripts/run_behaviorspace.sh scripts/run_all_baselines.sh scripts/run_extended_experiments.sh
```

## 7) Jednopříkazové spuštění přes Makefile (Linux/WSL)

```bash
make baseline NETLOGO=/opt/NetLogo-7.0.3
make extended NETLOGO=/opt/NetLogo-7.0.3
# nebo oboje:
make all NETLOGO=/opt/NetLogo-7.0.3
```

## 8) Replikovatelnost pro kontrolu vyučujícího

- fixní sada scénářů a jejich názvů
- fixní počet opakování
- explicitně uvedené low/mid/high hodnoty parametrů
- export raw CSV + summary CSV
- uložit i použitou verzi NetLogo
