Use the "Wizard" button on a zippcube device to open the screen and take
measurements:

The operator does the following steps:
1. Places the product on the physical device.
2. Opens the wizard on the Odoo UI.
3. Selects the product to measure, the one placed in the device.
4. Clicks on the "Scan" button for the package chosen.
5. Press Refresh.
6. Press Save.

Then, the measures should be transferred to the product in Odoo.

*Note for developers:* Inside ```scripts/measurement.sh``` there is
an example of a petition made to the controller, to trigger the
measurement from a local instance while testing in local. To test in
local, follow the steps above but before pressing the button Refresh
execute that script to simulate the measurement.
