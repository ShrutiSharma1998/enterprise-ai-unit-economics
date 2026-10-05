# SPDX-License-Identifier: Apache-2.0
# Recalculate a workbook with the installed Excel so formula results are cached in the file.
param([Parameter(Mandatory=$true)][string]$Path)
$full = (Resolve-Path $Path).Path
$xl = New-Object -ComObject Excel.Application
$xl.Visible = $false
$xl.DisplayAlerts = $false
try {
    $wb = $xl.Workbooks.Open($full)
    $xl.CalculateFull()
    $wb.Save()
    $wb.Close($false)
    "recalculated: $full"
} finally {
    $xl.Quit()
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl)
}
