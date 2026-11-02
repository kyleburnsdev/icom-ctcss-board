param([string]$Compiler = 'clang++')
$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
function Test-NativeFirmware([string]$Name, [string[]]$Sources, [string[]]$Includes, [string[]]$Definitions = @()) {
    $out = ".agent-scratch/firmware/$Name.exe"
    if ((Split-Path $Compiler -Leaf) -in @('cl', 'cl.exe')) {
        $flags = @('/nologo','/EHsc','/W4','/WX','/Fo.agent-scratch/firmware/',"/Fe$out")
        $flags += $Includes | ForEach-Object { "/I$_" }
        $flags += $Definitions | ForEach-Object { "/D$_" }
    } else {
        $flags = @('-std=c++11','-Wall','-Wextra','-Werror','-x','c++','-o',$out)
        $flags += $Includes | ForEach-Object { "-I$_" }
        $flags += $Definitions | ForEach-Object { "-D$_" }
    }
    & $Compiler @flags @Sources
    if ($LASTEXITCODE) { throw "$Name compilation failed" }
    & "./$out"
    if ($LASTEXITCODE) { throw "$Name failed" }
}
Push-Location $repo
try {
    New-Item -ItemType Directory -Force .agent-scratch/firmware | Out-Null
    Test-NativeFirmware control_test @('firmware/tests/control_test.cpp','firmware/icom_ctcss/control.cpp','firmware/icom_ctcss/journal.cpp') @('firmware/icom_ctcss')
    Test-NativeFirmware capture_test @('firmware/tests/capture_test.cpp','firmware/icom_ctcss/control.cpp','firmware/radio_standin/Core/Src/pwm_capture.c') @('firmware/icom_ctcss','firmware/radio_standin/Core/Inc')
    Test-NativeFirmware display_test @('firmware/tests/display_test.cpp','firmware/icom_ctcss/display.cpp','firmware/icom_ctcss/control.cpp') @('firmware/tests/fakes','firmware/icom_ctcss') @('CTCSS_LCD_ADDRESS=0x27')
}
finally { Pop-Location }
