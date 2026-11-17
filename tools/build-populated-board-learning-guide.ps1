<#
Build the illustrated Word/PDF guide from the companion Python content builder.
Requires Windows Microsoft Word. Creates its own invisible Word instance and
does not attach to or close the user's existing document sessions.
Run the Python builder first. No instrument access or firmware changes occur.
#>
[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$contentPath = Join-Path $repoRoot '.agent-scratch/populated-board-learning-guide/guide-content.json'
$outputBase = Join-Path $repoRoot 'docs/learning/populated-board-bench-checks-2026-11-16'
$content = Get-Content -LiteralPath $contentPath -Raw -Encoding utf8 | ConvertFrom-Json
$wordGuide = $null
$guideDocument = $null

function Convert-GuideColor([string]$hex) {
    $r = [Convert]::ToInt32($hex.Substring(0,2),16)
    $g = [Convert]::ToInt32($hex.Substring(2,2),16)
    $b = [Convert]::ToInt32($hex.Substring(4,2),16)
    return ($r + 256*$g + 65536*$b)
}

function Set-GuideParagraph($selection, $document, [int]$style = -1) {
    $selection.Style = $document.Styles.Item($style)
    $selection.Font.Name = 'Arial'
    $selection.Font.Color = 0
    $selection.Font.Bold = 0
    $selection.Font.Italic = 0
    $selection.Font.Size = 11
    $selection.ParagraphFormat.SpaceBefore = 0
    $selection.ParagraphFormat.SpaceAfter = 6
    $selection.ParagraphFormat.LineSpacingRule = 0
    $selection.ParagraphFormat.KeepWithNext = 0
    $selection.ParagraphFormat.KeepTogether = -1
    $selection.ParagraphFormat.Alignment = 0
}

try {
    $wordGuide = New-Object -ComObject Word.Application
    $wordGuide.Visible = $false
    $wordGuide.DisplayAlerts = 0
    $wordGuide.AutomationSecurity = 3
    $guideDocument = $wordGuide.Documents.Add()
    $section = $guideDocument.Sections.Item(1)
    $section.PageSetup.PageWidth = 612
    $section.PageSetup.PageHeight = 792
    $section.PageSetup.TopMargin = 43.2
    $section.PageSetup.BottomMargin = 43.2
    $section.PageSetup.LeftMargin = 46.8
    $section.PageSetup.RightMargin = 46.8
    $section.PageSetup.FooterDistance = 20
    foreach ($id in @(-1,-2,-3,-63,-35)) {
        $style = $guideDocument.Styles.Item($id)
        $style.Font.Name = 'Arial'
        $style.Font.Color = 0
        foreach ($border in $style.ParagraphFormat.Borders) { $border.LineStyle = 0 }
    }
    $guideDocument.Styles.Item(-1).Font.Size = 11
    $guideDocument.Styles.Item(-63).Font.Size = 25
    $guideDocument.Styles.Item(-63).Font.Bold = -1
    $guideDocument.Styles.Item(-2).Font.Size = 16
    $guideDocument.Styles.Item(-2).Font.Bold = -1
    $guideDocument.Styles.Item(-2).ParagraphFormat.KeepWithNext = -1
    $selection = $wordGuide.Selection
    $tableCount = 0
    $figureCount = 0
    for ($pageIndex=0; $pageIndex -lt $content.pages.Count; $pageIndex++) {
        if ($pageIndex -gt 0) { $selection.InsertBreak(7) }
        if ($pageIndex -eq 0) {
            Set-GuideParagraph $selection $guideDocument -63
            $selection.Font.Size = 25
            $selection.Font.Bold = -1
            $selection.TypeText($content.title)
            $selection.TypeParagraph()
            Set-GuideParagraph $selection $guideDocument
            $selection.Font.Size = 12
            $selection.TypeText($content.subtitle + ' | ' + $content.date)
            $selection.TypeParagraph()
        }
        Set-GuideParagraph $selection $guideDocument -2
        $selection.Font.Size = 16
        $selection.Font.Bold = -1
        $selection.ParagraphFormat.KeepWithNext = -1
        $selection.TypeText($content.pages[$pageIndex].title)
        $selection.TypeParagraph()
        foreach ($block in $content.pages[$pageIndex].blocks) {
            Set-GuideParagraph $selection $guideDocument
            switch ($block.type) {
                'paragraph' {
                    $selection.TypeText($block.text)
                    $selection.TypeParagraph()
                }
                'code' {
                    $selection.Font.Name = 'Consolas'
                    $selection.Font.Size = 9
                    $selection.TypeText($block.text.Replace("`n",[string][char]11))
                    $selection.TypeParagraph()
                }
                'link' {
                    $null = $guideDocument.Hyperlinks.Add($selection.Range,$block.url,$null,$null,$block.text)
                    $selection.SetRange($guideDocument.Content.End-1,$guideDocument.Content.End-1)
                    $selection.TypeParagraph()
                }
                'figure' {
                    $selection.ParagraphFormat.KeepWithNext = -1
                    $shape = $guideDocument.InlineShapes.AddPicture($block.path,$false,$true,$selection.Range)
                    $shape.LockAspectRatio = -1
                    $shape.Width = [single]($block.width_inches*72)
                    $shape.AlternativeText = $block.alt
                    $selection.SetRange($shape.Range.End,$shape.Range.End)
                    $selection.TypeParagraph()
                    Set-GuideParagraph $selection $guideDocument -35
                    $selection.Font.Size = 9.5
                    $selection.Font.Italic = -1
                    $selection.TypeText($block.caption)
                    $selection.TypeParagraph()
                    $figureCount++
                }
                'table' {
                    $rows = @($block.rows)
                    $columns = $block.headers.Count
                    $table = $guideDocument.Tables.Add($selection.Range,$rows.Count+1,$columns)
                    $table.AllowAutoFit = $false
                    $table.AutoFitBehavior(0)
                    $table.Rows.Alignment = 1
                    $table.Rows.AllowBreakAcrossPages = 0
                    $table.TopPadding = 3
                    $table.BottomPadding = 3
                    $table.LeftPadding = 5
                    $table.RightPadding = 5
                    $table.Range.Font.Name = 'Arial'
                    $table.Range.Font.Size = [single]$block.font_size
                    $table.Range.Font.Bold = 0
                    $table.Range.Font.Color = 0
                    $table.Range.ParagraphFormat.SpaceBefore = 0
                    $table.Range.ParagraphFormat.SpaceAfter = 0
                    $table.Range.ParagraphFormat.KeepWithNext = 0
                    $table.Range.ParagraphFormat.LineSpacingRule = 0
                    $table.Borders.Enable = 1
                    $table.Borders.InsideLineStyle = 1
                    $table.Borders.OutsideLineStyle = 1
                    $table.Borders.InsideLineWidth = 4
                    $table.Borders.OutsideLineWidth = 4
                    foreach ($border in $table.Borders) { $border.Color = Convert-GuideColor 'D9D9D9' }
                    for ($column=1; $column -le $columns; $column++) {
                        $table.Columns.Item($column).Width = [single]($block.widths[$column-1]*72)
                        $cell = $table.Cell(1,$column)
                        $cell.Range.Text = [string]$block.headers[$column-1]
                        $cell.Range.Font.Bold = -1
                        $cell.Range.Font.Color = 16777215
                        $cell.Shading.BackgroundPatternColor = Convert-GuideColor '203E50'
                        $cell.VerticalAlignment = 1
                    }
                    $table.Rows.Item(1).HeadingFormat = -1
                    $table.Rows.Item(1).Range.ParagraphFormat.KeepWithNext = -1
                    for ($row=0; $row -lt $rows.Count; $row++) {
                        for ($column=1; $column -le $columns; $column++) {
                            $cell = $table.Cell($row+2,$column)
                            $cell.Range.Text = [string]$rows[$row][$column-1]
                            $cell.VerticalAlignment = 1
                            $cell.Shading.BackgroundPatternColor = if ($row%2 -eq 0) {16777215} else {Convert-GuideColor 'F0F5F7'}
                            if ($column -eq 1 -and $columns -eq 4) { $cell.Range.ParagraphFormat.Alignment = 1 }
                        }
                    }
                    $selection.SetRange($table.Range.End,$table.Range.End)
                    $selection.TypeParagraph()
                    $tableCount++
                }
                default { throw ('Unknown content block ' + $block.type) }
            }
        }
    }
    $footer = $section.Footers.Item(1)
    $footer.Range.Text = 'Icom CTCSS board bench checks | 16 November 2026 | Page '
    $footer.Range.Font.Name = 'Arial'
    $footer.Range.Font.Size = 9
    $footer.Range.Font.Color = 0
    $footer.Range.ParagraphFormat.Alignment = 2
    $footerRange = $footer.Range.Duplicate
    $footerRange.End = $footerRange.End-1
    $footerRange.Collapse(0)
    $null = $guideDocument.Fields.Add($footerRange,33)
    $guideDocument.Repaginate()
    $null = $guideDocument.Fields.Update()
    $docxPath = $outputBase + '.docx'
    $pdfPath = $outputBase + '.pdf'
    $guideDocument.SaveAs2($docxPath,16)
    $guideDocument.ExportAsFixedFormat($pdfPath,17,$false,0,0,1,1,0,$true,$true,1,$true,$true,$false)
    $result = @{word_version=$wordGuide.Version; pages=$guideDocument.ComputeStatistics(2); tables=$tableCount; figures=$figureCount; docx=$docxPath; pdf=$pdfPath}
    $result | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $repoRoot '.agent-scratch/populated-board-learning-guide/native-word-render.json')
    $result | ConvertTo-Json
}
finally {
    if ($null -ne $guideDocument) { $guideDocument.Close(0); [System.Runtime.InteropServices.Marshal]::ReleaseComObject($guideDocument) | Out-Null }
    if ($null -ne $wordGuide) { $wordGuide.Quit(); [System.Runtime.InteropServices.Marshal]::ReleaseComObject($wordGuide) | Out-Null }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
