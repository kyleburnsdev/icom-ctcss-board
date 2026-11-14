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
        # The host sketch model uses STL containers; Windows' current STL needs
        # C++14. This does not change the Arduino compiler/language settings.
        $flags = @('-std=c++14','-Wall','-Wextra','-Werror','-x','c++','-o',$out)
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
    Test-NativeFirmware tone_test @('firmware/tests/tone_test.cpp','firmware/icom_ctcss/tone.cpp') @('firmware/tests/tone_fakes','firmware/icom_ctcss')
    Test-NativeFirmware display_test @('firmware/tests/display_test.cpp','firmware/icom_ctcss/display.cpp','firmware/icom_ctcss/control.cpp') @('firmware/tests/fakes','firmware/icom_ctcss') @('CTCSS_LCD_ADDRESS=0x27')
    Test-NativeFirmware sketch_test @('firmware/tests/sketch_test.cpp','firmware/icom_ctcss/control.cpp','firmware/icom_ctcss/journal.cpp','firmware/icom_ctcss/storage.cpp','firmware/icom_ctcss/tone.cpp','firmware/icom_ctcss/display.cpp') @('firmware/tests/sketch_fakes','firmware/tests/tone_fakes','firmware/tests/fakes','firmware/icom_ctcss') @('CTCSS_BENCH=1','CTCSS_LCD_ADDRESS=0x27')
    foreach ($scenario in @('held','bypass','held-bypass','wrap','no-lcd','standalone','write-fault')) {
        & './.agent-scratch/firmware/sketch_test.exe' $scenario
        if ($LASTEXITCODE) { throw "Sketch integration scenario $scenario failed" }
    }
    Test-NativeFirmware sketch_no_lcd_test @('firmware/tests/sketch_test.cpp','firmware/icom_ctcss/control.cpp','firmware/icom_ctcss/journal.cpp','firmware/icom_ctcss/storage.cpp','firmware/icom_ctcss/tone.cpp','firmware/icom_ctcss/display.cpp') @('firmware/tests/sketch_fakes','firmware/tests/tone_fakes','firmware/tests/fakes','firmware/icom_ctcss') @('CTCSS_BENCH=1','CTCSS_LCD_ADDRESS=0')
    Test-NativeFirmware display_grove_test @('firmware/tests/display_test.cpp','firmware/icom_ctcss/display.cpp','firmware/icom_ctcss/control.cpp') @('firmware/tests/fakes','firmware/icom_ctcss') @('CTCSS_LCD_ADDRESS=0x3e','CTCSS_LCD_GROVE_V4=1')
    Test-NativeFirmware sketch_grove_test @('firmware/tests/sketch_test.cpp','firmware/icom_ctcss/control.cpp','firmware/icom_ctcss/journal.cpp','firmware/icom_ctcss/storage.cpp','firmware/icom_ctcss/tone.cpp','firmware/icom_ctcss/display.cpp') @('firmware/tests/sketch_fakes','firmware/tests/tone_fakes','firmware/tests/fakes','firmware/icom_ctcss') @('CTCSS_BENCH=1','CTCSS_LCD_ADDRESS=0x3e','CTCSS_LCD_GROVE_V4=1')
    foreach ($scenario in @('held','bypass','held-bypass','wrap','no-lcd','standalone','write-fault')) {
        & './.agent-scratch/firmware/sketch_grove_test.exe' $scenario
        if ($LASTEXITCODE) { throw "Grove sketch integration scenario $scenario failed" }
    }
}
finally { Pop-Location }
