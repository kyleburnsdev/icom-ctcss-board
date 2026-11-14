param(
    [ValidateSet('All', 'ProMicro', 'Standin')][string]$Target = 'All',
    [switch]$Bench,
    [string]$ArduinoCli = 'arduino-cli',
    [string]$CMake = 'cmake',
    [string]$LcdAddress = '0',
    [switch]$GroveV4,
    [ValidateSet('Debug','Release')][string]$Configuration = 'Release'
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
Push-Location $repo
try {
    if ($Target -in @('All','ProMicro')) {
        $variant = if ($Bench) { 'bench' } else { 'production' }
        $benchValue = if ($Bench) { 1 } else { 0 }
        $groveValue = if ($GroveV4) { 1 } else { 0 }
        if ($GroveV4) { $LcdAddress = '0x3e' }
        if ($LcdAddress -notmatch '^(0|0x[0-7][0-9a-fA-F])$') { throw 'LCD address must be 0 or a 7-bit hex address' }
        $displaySuffix = if ($LcdAddress -eq '0') { '' } else { "-lcd$LcdAddress" }
        if ($GroveV4) { $displaySuffix += '-grove-v4' }
        & $ArduinoCli compile --fqbn 'SparkFun:avr:promicro:cpu=16MHzatmega32U4' --warnings all `
            --build-path ".agent-scratch/firmware/avr-$variant$displaySuffix" `
            --build-property "compiler.cpp.extra_flags=-DCTCSS_BENCH=$benchValue -DCTCSS_LCD_ADDRESS=$LcdAddress -DCTCSS_LCD_GROVE_V4=$groveValue" `
            firmware/icom_ctcss
        if ($LASTEXITCODE) { throw 'Pro Micro build failed' }
    }
    if ($Target -in @('All','Standin')) {
        $out = ".agent-scratch/firmware/standin-$Configuration"
        & $CMake -S firmware/radio_standin -B $out -G Ninja `
            "-DCMAKE_BUILD_TYPE=$Configuration" `
            '-DCMAKE_TOOLCHAIN_FILE=cmake/gcc-arm-none-eabi.cmake'
        if ($LASTEXITCODE) { throw 'NUCLEO configuration failed' }
        & $CMake --build $out
        if ($LASTEXITCODE) { throw 'NUCLEO build failed' }
    }
} finally { Pop-Location }
