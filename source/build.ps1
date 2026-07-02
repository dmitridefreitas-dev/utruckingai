# Rebuilds ALL shareable PDFs (into the parent folder) from the source files here.
# Usage:  powershell -ExecutionPolicy Bypass -File source\build.ps1
$ErrorActionPreference = "Continue"
$src = Split-Path -Parent $MyInvocation.MyCommand.Definition
$out = Split-Path -Parent $src
Write-Output "source: $src"
Write-Output "output: $out"

$browser = @(
  "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
  "C:\Program Files\Microsoft\Edge\Application\msedge.exe",
  "C:\Program Files\Google\Chrome\Application\chrome.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1
$dot = @("C:\Program Files\Graphviz\bin\dot.exe","C:\Program Files (x86)\Graphviz\bin\dot.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $browser) { Write-Output "No Edge/Chrome found."; exit 1 }

function To-Pdf($html, $pdf) {
  $url = "file:///" + ($html -replace '\\','/')
  & $browser --headless=new --disable-gpu --no-pdf-header-footer --virtual-time-budget=6000 --print-to-pdf="$pdf" $url 2>$null | Out-Null
  if (Test-Path $pdf) { Write-Output ("  OK  {0}" -f (Split-Path $pdf -Leaf)) } else { Write-Output ("  FAIL {0}" -f (Split-Path $pdf -Leaf)) }
}

python -m pip install --user --quiet markdown pypdf 2>$null

# 1) Flow maps: PDF to output, PNG stays in source (the deck embeds the journey PNG)
if ($dot) {
  & $dot -Tpdf "$src\utrucking_call_journey.dot" -o "$out\UTrucking_Call_Journey.pdf"
  & $dot -Tpng "-Gdpi=150" "$src\utrucking_call_journey.dot" -o "$src\UTrucking_Call_Journey.png"
  & $dot -Tpdf "$src\utrucking_agent_flow.dot" -o "$out\UTrucking_Voice_Agent_Flow.pdf"
  & $dot -Tpng "-Gdpi=150" "$src\utrucking_agent_flow.dot" -o "$src\UTrucking_Voice_Agent_Flow.png"
  Write-Output "  OK  flow maps"
} else { Write-Output "  (Graphviz not found - skipping flow-map rebuild)" }

# 2) Markdown docs -> PDF
$docs = [ordered]@{ "PLAN.md"="UTrucking Plan & Roadmap"; "CONNECTIONS.md"="UTrucking Connections"; "TEST_LOG.md"="UTrucking QA & Test Log" }
foreach ($md in $docs.Keys) {
  if (-not (Test-Path "$src\$md")) { continue }
  $tmp = "$src\_tmp.html"
  python "$src\md2html.py" "$src\$md" $tmp $docs[$md] | Out-Null
  To-Pdf $tmp ("$out\" + ($md -replace '\.md$','.pdf'))
  Remove-Item $tmp -ErrorAction SilentlyContinue
}

# 3) Executive deck -> PDF
if (Test-Path "$src\UTrucking_Executive_Deck.html") { To-Pdf "$src\UTrucking_Executive_Deck.html" "$out\UTrucking_Executive_Deck.pdf" }

# 3.5) Data & Revenue audit -> PDF (charts embedded from source/analytics/metrics.json)
if (Test-Path "$src\analytics\build_audit.py") {
  python "$src\analytics\build_audit.py" "$src\analytics\metrics.json" "$src\analytics\_audit.html" | Out-Null
  To-Pdf "$src\analytics\_audit.html" "$out\UTrucking_Data_Audit.pdf"
  Remove-Item "$src\analytics\_audit.html" -ErrorAction SilentlyContinue
}

# 4) Combined master report with Contents page + bookmarks
python "$src\gen_toc.py" "$out" "$src"
if (Test-Path "$src\_toc.html") {
  To-Pdf "$src\_toc.html" "$src\_toc.pdf"
  python "$src\merge_pdfs.py" "$out" "$src"
  Remove-Item "$src\_toc.html","$src\_toc.pdf","$src\_manifest.json" -ErrorAction SilentlyContinue
}
Write-Output "Done. -> $out\UTrucking_AI_Assistant_Full_Report.pdf"
