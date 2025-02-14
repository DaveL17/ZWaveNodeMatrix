### v2024.1.0
- 
 
### v2023.1.0
- Minor UI enhancements.
- Minor Wiki enhancements.

### v2023.1.0
- Adds `X (filled)` to Node Marker styles.
- Adds "About Matplotlib" to plugin menu.
- Fixes bug where charts wouldn't generate in Matplotlib 3.8 (shipping with Indigo 2023.2). Should still work for prior
  versions of Matplotlib.
- Code refinements.
- Moves Node Markers XML to template file.

### v2022.0.5
- Updates plugin API to `3.2`.
- Code refinement.

### v2022.0.4
- Adds foundation for API `3.1`.
- Fixes bug where plugin searches for Z-Wave devices.

### v2022.0.3
- Adds `_to_do_list.md` and changes changelog to markdown.
- Moves plugin environment logging to plugin menu item (log only on request).

### v2022.0.2
- Sync

### v2022.0.1
- Fixes bug where dummy testing data can override real data.

### v2022.0.1
- Updates plugin for Indigo 2022.1 and Python 3.
- Fixes bug where chart height and width settings were reversed.
- Improves dummy device data (for testing).
- Adds tight_layout (reduces empty space around chart).
- Adds new marker styles.
- Standardizes Indigo method implementation.

### v1.0.15
- Fixes broken link to readme logo.
- Fixes broken symlinks.

### v1.0.14
- Better integration of DLFramework.

### v1.0.13
- Code refinements.

### v1.0.12
- Removes all references to legacy version checking.

### v1.0.11
- Fixes bug where plugin would error out when no Z-Wave devices present.

### v1.0.10
- Adds asterisk to plugin configuration dialog dropdown menus to indicate default setting.

### v1.0.09
- Synchronizes version numbers.

### v1.0.08
- Fixes bug for horizontal line marker style.

### v1.0.07
- Increments version number.

### v1.0.06
- Ensures that the plugin is compatible with the Indigo server version.
- Standardizes Support URL behavior across all plugin functions.

### v1.0.05
- Synchronize self.pluginPrefs in closedPrefsConfigUi().

### v1.0.04
- Updates default image save location to the current install path.
- Updates kDefaultPluginPrefs

### v1.0.03
- Removes plugin update checker.

### v1.0.02
- Changes Python lists to tuples where possible to improve performance.

### v1.0.01
- Takes plugin out of beta.
- Fixes bug where change in debug level required a plugin restart to take effect.
- Code refinements.

### v0.3.01
- Fixes bug in listing of nodes for combination devices (multiple devices that use the same address).
- Fixes bug where font setting only affected the chart's title.
- Refactors code to establish device plotting properties.
- Increments Indigo Server API requirement to `2.0`

### v0.2.9
- Refactors plugin method names to PEP 8.

### v0.2.8
- Fixes bug in naming of PluginConfig.xml (which caused problems on systems set up as case-sensitive).

### v0.2.7
- Updates plugin update checker to use curl to overcome outdated security of Apple's Python install.

### v0.2.6
- IPS configuration

### v0.2.5
- Standardizes file framework.

### v0.2.4
- Plot legend made dynamic (only selected options will be reflected).
- Legend entries more closely mirror plot.
- Order of legend redone to put plot elements and axis elements together.
- Stylistic changes to Indigo Plugin Update Checker module.
