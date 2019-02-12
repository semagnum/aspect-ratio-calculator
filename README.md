# Aspect Ratio Calculator

There are two places that this addon is used: in the scene properties, and the compositing node tree.

## Render Settings

You'll find the panel at the bottom of the output settings of the properties panel.  Each of the buttons generates the correct resolution based on the selected aspect ratio and the width of your current render resolution setting.

## Compositor Node Tree

On the left shelf of the compositing window (if it's not visible, press "t" with your cursor over the window), find the "Aspect Ratio" category.  There are a few presets, along with a custom aspect ratio generator.  By clicking any of the buttons, a few nodes will be added before the composite.  And if you change your mind and select a different ratio, it'll simply update the compositor - nothing will be re-added.

## How to Use
You can either using the preset aspect ratios, or enter the aspect ratio in decimal form in the "Custom Aspect Ratio" field.  If you don't know the decimal form but have the proportions ("1.85 : 1," for example), enter the width proportion divided by the height proportion, and let Blender calculate it for you (for the previous example, you'd type in "1.85 / 1")!

For the most accuracy with the custom aspect ratio, ensure that your number has at least 4 significant figures.  This will ensure the accuracy of the resolution size.  Otherwise, it may be a little off.
