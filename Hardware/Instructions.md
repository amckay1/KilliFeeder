# ft2kHardware

The hardware design files for the KilliFeeder system, including all Autocad files + stl files for 3D printing, Illustrator files for laser cutting, and Eagle files for hardware.

## Included files:
* FeederBOM.csv: list of components, estimated costs, and vendors used
* Print3D: files necessary to 3D print components with PLA
* LaserCut: files necessary to laser cut 0.066" thickness acrylic sheets
* PCB: Eagle files for PCB design

## Suggested approach to sourcing components:
* Order components in FeederBOM.csv from Digikey, Amazon, Grainger, and Aliexpress
* Order PCB from OSH Park by uploading WemoseD1_Feeder.brd Eagle file found in PCB directory
* Upon receipt of acrylic sheets, laser cut components using LaserCut.dxf file found in the LaserCut directory. This should cut a 1 foot by 1 foot sheet of acrylic at 0.066" thickness with two different diameters of food outlet (3 mm and 4 mm). The LaserCut.dxf and LaserCut.ai files are derived from the original LaserCut.dwg Autocad file and are customized to the laser cutter we used. You may need to rederive for your laser cutter, but this should only require changing line thickness and color (red signifies cuts and blue signifies engraving). 
* 3D Print PLA components found in Print3D/stl directory either by printing directly using 3D printer or ordering from online 3D printing service. Files are as follows: top.stl, bottom.stl, backstop.stl. Original autocad models in dwg format can be found in Print3D/Autocad_dwg, but you should only need the .stl files to print. All measurements are in mm.

## Suggested build process
* It is suggested that you assemble PCBs first as this is the rate limiting step for assembly.
* Assemble the PCBs using standard soldering iron and reworking station. The reworking station and solder paste is not necessary but greatly helps for some of the SMDs such as the ULN2003ADR IC.
* Solder the headers onto the Wemos D1 mini micro controller board.
* The battery holder needs to be soldered to the 2.54mm pitch JST male pin connectors and the photoresistors needs to be soldered to female jumper wires. The polarity matters for the battery holder but not the photoresistors.
* Hot glue the photoresistor onto the bottom 3D printed component to allow for visibility from the green LED above once assembled.
* Assemble the stepper motor, 3D printed parts, and acrylic parts separately with the nylon screws and hot glue the backstop 3D printed component to the large acrylic piece.
* When both the PBC and printed + laser cut parts are assembled into two assemblies, connect by placing the soldered LED into the top 3D printed units opening such that the photoresistor hot glued to the bottom 3D printed component can detect the light when illuminated.
* Hook up the photoresistor to the PCB, as well as the battery assembly.
* Flash WemosD1 Mini micro controller (explained more in the Software instructions) and add food into the hopper for calibration.