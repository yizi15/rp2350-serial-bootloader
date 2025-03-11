$json_data = Get-Content  -Raw -Path ".vscode/settings.json" | ConvertFrom-Json
$OPENOCD_PATH = $ExecutionContext.InvokeCommand.ExpandString($json_data."cortex-debug.openocdPath")
echo $OPENOCD_PATH
$TCL_PATH = $OPENOCD_PATH -replace "src/openocd.exe","tcl"
$TCL_PATH="F:/PICO/pico-sdk/openocd-sdk-2.0.0/tcl"

echo $TCL_PATH
$target = "./build/bootloader.elf"
echo $target
$c_cmd = "program " + $target  + " verify reset exit"
& $OPENOCD_PATH -f interface/jlink.cfg -f "./this_ocd.cfg" -f target/rp2350.cfg -s $TCL_PATH  -c $c_cmd
