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
