# Automatizace experimentů

Adresář `scripts` obsahuje pomocné skripty pro hromadné spuštění připravených
BehaviorSpace experimentů v NetLogo a následnou agregaci jejich výstupů. Skripty
jsou určeny pro reprodukovatelné získání CSV souborů používaných ve výsledkové
části dokumentace.

## Přehled skriptů

- `run_behaviorspace.ps1` / `run_behaviorspace.sh` spustí jeden zadaný
  BehaviorSpace experiment v headless režimu NetLogo.
- `run_all_baselines.ps1` / `run_all_baselines.sh` spustí baseline scénáře pro
  modely `virus1` až `virus4`.
- `run_extended_experiments.ps1` / `run_extended_experiments.sh` spustí
  rozšířené OFAT a grid experimenty.
- `run_all_experiments.ps1` / `run_all_experiments.sh` spustí baseline i
  rozšířené experimenty v jednom kroku.
- `aggregate_results.py` agreguje raw CSV výstupy z BehaviorSpace do souhrnných
  tabulek.

Hromadné skripty volají `aggregate_results.py` automaticky, takže po jejich
dokončení vznikají jak raw CSV soubory, tak odpovídající `*_summary.csv`
soubory v adresáři `out`.

## Spuštění všech experimentů

Windows PowerShell:

```powershell
.\scripts\run_all_experiments.ps1 `
  -NetLogoPath "C:\Program Files\NetLogo 7.0.3\NetLogo_Console.exe"
```

Linux/WSL:

```bash
./scripts/run_all_experiments.sh "/opt/NetLogo-7.0.3"
```

Tento postup vytvoří kompletní sadu výstupů pro všechny baseline i rozšířené
experimenty.

## Samostatné spuštění baseline scénářů

Windows PowerShell:

```powershell
.\scripts\run_all_baselines.ps1 `
  -NetLogoPath "C:\Program Files\NetLogo 7.0.3\NetLogo_Console.exe"
```

Linux/WSL:

```bash
./scripts/run_all_baselines.sh "/opt/NetLogo-7.0.3"
```

Výstupem jsou soubory `out/virus*_baseline.csv` a
`out/virus*_baseline_summary.csv`.

## Samostatné spuštění rozšířených experimentů

Windows PowerShell:

```powershell
.\scripts\run_extended_experiments.ps1 `
  -NetLogoPath "C:\Program Files\NetLogo 7.0.3\NetLogo_Console.exe"
```

Linux/WSL:

```bash
./scripts/run_extended_experiments.sh "/opt/NetLogo-7.0.3"
```

Výstupem jsou raw CSV soubory a agregované summary tabulky pro citlivostní
experimenty:

- `virus1_ofat_transmission`
- `virus2_capacity_grid`
- `virus3_resources_grid`
- `virus4_strategy_grid`

## Ruční agregace

Ruční spuštění `aggregate_results.py` je potřeba pouze při samostatném exportu
nového BehaviorSpace experimentu mimo připravené hromadné skripty. Příklad:

```powershell
python .\scripts\aggregate_results.py `
  --input ".\out\virus4_baseline.csv" `
  --metrics "m_final_susceptible,m_final_exposed,m_final_infected,m_final_recovered,m_ever_infected,m_ticks,m_deaths,m_final_resources" `
  --output ".\out\virus4_baseline_summary.csv"
```

Argument `--group-by` se používá u experimentů s více konfiguracemi parametrů,
například podle `strategy-mode,high-risk-share,vaccination-rate`.

## Poznámka pro Linux/WSL

Pokud shell skripty nejsou spustitelné, nastaví se oprávnění příkazem:

```bash
chmod +x scripts/*.sh
```
