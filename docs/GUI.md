# Custom chest GUIs (font backgrounds)

Font `stark:gui` (assets/stark/font/gui.json):

| char | what |
|---|---|
| `` | 6-row panel background (176 x 222) |
| `` | 3-row panel background (176 x 168) |
| `..` | negative space -1, -2, -4, -8, -16, -32, -64, -128 px |
| `..` | positive space +1 ... +128 px |

Inventory title component (6 rows):
`<font:stark:gui></font>` + normal title text
(= shift -8, background (advance 177), shift -169 back to x = 8).
Background colour must be white in the component (`color: white`) or the bitmap is tinted.

## Lift control panel (StarkElevator)

| char | what |
|---|---|
| `` | lift panel, 3-row chest (176 x 168) - own design: gold frame, hazard stripes, big UP / DOWN buttons, 5 floor lamps |

Title component: same as the 3-row panel, only `` instead of ``; the
title text is the current station (e.g. `▶ Starter Mine`) and is shown in the
dark display bar at the top.

Slot map (row * 9 + col):

| slots | content |
|---|---|
| 3, 4, 5 | **UP** button - item `minecraft:paper` with `item_model: "stark:blank"` (invisible), name "▲ Up", lore: next station above |
| 21, 22, 23 | **DOWN** button - same blank item, name "▼ Down", lore: next station below |
| 11 - 15 | floor lamps, top floor left: `stark:lamp_on` (cabin is here), `stark:lamp_off`, `stark:lamp_lock` (level too low), `stark:lamp_event` (closed / event only); name = station, lore = subtitle + level |
| all others | empty (the art is drawn there) |

The font `stark:gui` now also references `minecraft:default`, so title text
that inherits the font renders normally (before it showed empty boxes).
