<#
.SYNOPSIS
  Allineamento chiavi localizer <-> RESX per uno o piu' file Razor.

.DESCRIPTION
  Sola lettura. Per ogni .razor (e il suo .razor.cs, se esiste):
  - ricava i localizer iniettati (@inject IStringLocalizer<T> nome);
  - KO  chiave usata senza voce nel RESX (a runtime esce la chiave);
  - KO  chiave fantasma (spazi o accenti nella chiave);
  - KO  voce duplicata o senza <value> nel RESX;
  - KO  RESX atteso inesistente;
  - AVVISO voce RESX non usata (chiave morta);
  - AVVISO riga con lettere accentate fuori dai commenti (possibile stringa IT residua).
  Il RESX di pagina segue la convenzione Resources/<percorso>/<Nome>.it.resx;
  CommonLabels -> Resources/Resources.CommonLabels.it.resx.
  Exit code 1 se c'e' almeno un KO.

.PARAMETER Path
  File .razor o cartella (ricorsiva). Relativo alla cartella corrente, al progetto o alla radice del repo.

.PARAMETER Resx
  RESX di pagina esplicito, quando il localizer e' di un'altra classe (es. SinotticoTabella -> Sinottico).

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File .claude/skills/blazor-localization/scripts/verifica-chiavi.ps1 BlazorWCSWebUI/Components/Impostazioni/Autorizzazioni.razor
#>
param(
	[Parameter(Mandatory = $true, Position = 0)][string]$Path,
	[string]$Resx
)

$ErrorActionPreference = 'Stop'
# $PSScriptRoot non e' valorizzato nei default dei parametri su PS 5.1: calcolo nel corpo.
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..\..')).Path
$Progetto = Join-Path $Root 'BlazorWCSWebUI'
$ResxCommon = Join-Path $Progetto 'Resources\Resources.CommonLabels.it.resx'

function Resolve-Input([string]$p) {
	foreach ($base in @((Get-Location).Path, $Progetto, $Root)) {
		$c = if ([IO.Path]::IsPathRooted($p)) { $p } else { Join-Path $base $p }
		if (Test-Path $c) { return (Resolve-Path $c).Path }
	}
	throw "Percorso non trovato: $p"
}

function Get-ResxInfo([string]$file) {
	$info = @{ Keys = @{}; Dup = @(); Empty = @() }
	[xml]$x = Get-Content -LiteralPath $file -Raw -Encoding UTF8
	foreach ($d in $x.SelectNodes('/root/data')) {
		$n = $d.GetAttribute('name')
		if ($n -in 'Name1', 'Color1', 'Bitmap1', 'Icon1') { continue }
		if ($info.Keys.ContainsKey($n)) { $info.Dup += $n } else { $info.Keys[$n] = $true }
		$v = $d.SelectSingleNode('value')
		if ($null -eq $v -or [string]::IsNullOrWhiteSpace($v.InnerText)) { $info.Empty += $n }
	}
	return $info
}

$script:ko = 0
function Out-Esito([string]$livello, [string]$file, [string]$msg) {
	if ($livello -eq 'KO') { $script:ko++ }
	"{0} | {1} | {2}" -f $livello, $file, $msg
}

$target = Resolve-Input $Path
$files = if ((Get-Item $target).PSIsContainer) {
	Get-ChildItem $target -Recurse -Filter *.razor | Where-Object { $_.FullName -notmatch '\\(bin|obj)\\' } | ForEach-Object FullName
} else { @($target) }

$accenti = '[' + [char]0xC0 + '-' + [char]0xFF + ']'
foreach ($razor in $files) {
	$rel = $razor.Substring($Progetto.Length + 1)
	$sorgenti = @($razor) + @("$razor.cs" | Where-Object { Test-Path $_ })
	$testo = ($sorgenti | ForEach-Object { Get-Content -LiteralPath $_ -Raw -Encoding UTF8 }) -join "`n"

	# Localizer iniettati: nome variabile -> classe
	$inject = @{}
	foreach ($m in [regex]::Matches($testo, '@inject\s+(?:[\w.]+\.)?IStringLocalizer<\s*([\w.]+)\s*>\s+(\w+)')) {
		$inject[$m.Groups[2].Value] = ($m.Groups[1].Value -split '\.')[-1]
	}
	foreach ($m in [regex]::Matches($testo, '\[Inject\][^;]*?IStringLocalizer<\s*([\w.]+)\s*>\??\s+(\w+)')) {
		$inject[$m.Groups[2].Value] = ($m.Groups[1].Value -split '\.')[-1]
	}
	if ($inject.Count -eq 0) { Out-Esito 'AVVISO' $rel 'nessun IStringLocalizer iniettato'; continue }

	$nome = [IO.Path]::GetFileNameWithoutExtension($razor)
	foreach ($var in $inject.Keys) {
		$classe = $inject[$var]
		if ($classe -eq 'CommonLabels') { $file = $ResxCommon }
		elseif ($Resx) { $file = Resolve-Input $Resx }
		else {
			$file = Join-Path $Progetto ('Resources\' + $rel.Substring(0, $rel.Length - '.razor'.Length) + '.it.resx')
			if ($classe -ne $nome) { Out-Esito 'AVVISO' $rel "localizer '$var' e' di <$classe>, non <$nome>: passa -Resx col RESX giusto" }
		}
		$relResx = $file.Substring($Root.Length + 1)
		$usate = [regex]::Matches($testo, '\b' + [regex]::Escape($var) + '\["([^"]*)"') | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique

		foreach ($k in $usate) {
			if ($k -match '\s' -or $k -match $accenti) { Out-Esito 'KO' $rel "chiave fantasma $var[`"$k`"]" }
		}
		if (-not (Test-Path $file)) { Out-Esito 'KO' $rel "RESX inesistente: $relResx"; continue }

		$info = Get-ResxInfo $file
		foreach ($k in $usate) { if (-not $info.Keys.ContainsKey($k)) { Out-Esito 'KO' $rel "$var[`"$k`"] senza voce in $relResx" } }
		if ($classe -ne 'CommonLabels') {
			foreach ($k in $info.Dup) { Out-Esito 'KO' $relResx "voce duplicata: $k" }
			foreach ($k in $info.Empty) { Out-Esito 'KO' $relResx "voce senza valore: $k" }
			if (-not $Resx -or $files.Count -eq 1) {
				foreach ($k in ($info.Keys.Keys | Sort-Object)) { if ($k -notin $usate) { Out-Esito 'AVVISO' $relResx "voce non usata: $k" } }
			}
		}
	}

	# Righe con accenti fuori dai commenti: candidati a stringa IT residua
	$n = 0; $inCommento = $false
	foreach ($riga in (Get-Content -LiteralPath $razor -Encoding UTF8)) {
		$n++
		$t = $riga.Trim()
		if ($t -match '^(@\*|<!--|/\*)') { $inCommento = $true }
		$commento = $inCommento -or $t.StartsWith('//')
		if ($t -match '(\*@|-->|\*/)\s*$') { $inCommento = $false }
		if (-not $commento -and $t -match $accenti -and $t -notmatch '\["[^"]*"\]') { Out-Esito 'AVVISO' $rel "riga ${n}: possibile stringa IT -> $t" }
	}
}

"TOTALE | file {0} | KO {1}" -f $files.Count, $script:ko
if ($script:ko -gt 0) { exit 1 } else { exit 0 }
