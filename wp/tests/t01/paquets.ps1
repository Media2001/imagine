# T03 presentation only. A packet error never mutates PHPUnit/tools/exit status.
function Get-T03PacketSummary {
    param([string]$Text)
    $e = [char]0x00e9
    $fallback = 'PAQUETS : 0 v{0}rifi{0}s, 1 {0}checs ; hors rejeu : aucun ; T-03 RUNNER_OUTPUT' -f $e
    try {
        $markers = @($Text -split "`n" | Where-Object { $_ -match '^T03_PACKETS ' })
        if ($markers.Count -ne 1) { throw 'MARKER' }
        $data = $markers[0].Substring(12) | ConvertFrom-Json
        if ((@($data.PSObject.Properties.Name | Sort-Object) -join ',') -ne 'excluded,failures,lots,verified') { throw 'SCHEMA' }
        if ($data.verified -isnot [int] -or $data.verified -lt 0 -or $data.verified -gt 10000 -or $data.lots -isnot [Array] -or $data.failures -isnot [Array] -or $data.excluded -isnot [Array]) { throw 'COUNTERS' }
        $lots = @($data.lots)
        if ($lots.Count -ne $data.verified -or @($lots | Select-Object -Unique).Count -ne $lots.Count) { throw 'COUNT' }
        foreach ($lot in $lots) { if ($lot -isnot [string] -or $lot -cnotmatch '^[A-Z]-[0-9]{2}$') { throw 'LOT' } }
        $reds = @($data.failures | ForEach-Object {
            if ((@($_.PSObject.Properties.Name | Sort-Object) -join ',') -ne 'control,lot' -or $_.lot -cnotmatch '^[A-Z]-[0-9]{2}$' -or $_.control -cnotmatch '^[A-Za-z][A-Za-z0-9_:.-]{0,159}$') { throw 'CONTROL' }
            $_.lot + ' ' + $_.control
        })
        if (@($data.failures.lot | Select-Object -Unique).Count -ne $reds.Count) { throw 'DUPLICATE_RED' }
        $reasons = @('declaration absente', 'journaux absents', 'Docker requis', 'reseau requis', 'ecriture depot requise', 'argument requis')
        $outside = @($data.excluded | ForEach-Object {
            if ((@($_.PSObject.Properties.Name | Sort-Object) -join ',') -ne 'lot,reason' -or $_.lot -cnotmatch '^[A-Z]-[0-9]{2}$' -or $reasons -cnotcontains $_.reason -or $lots -contains $_.lot) { throw 'OUTSIDE' }
            $_.lot + ' (' + $_.reason + ')'
        })
        if (@($data.excluded.lot | Select-Object -Unique).Count -ne $outside.Count) { throw 'DUPLICATE_OUTSIDE' }
        $textOutside = if ($outside.Count) { $outside -join ', ' } else { 'aucun' }
        $line = 'PAQUETS : {0} v{3}rifi{3}s, {1} {3}checs ; hors rejeu : {2}' -f $data.verified, $reds.Count, $textOutside, $e
        if ($reds.Count) { $line += ' ; ' + ($reds -join ', ') }
        return $line
    } catch { return $fallback }
}
