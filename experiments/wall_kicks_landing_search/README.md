# Wall Kicks Will Work: landing-recovery search

This intermediate search layered 86 mutations on the first VI 538 seed:
jump-kick shifts, button-transition shifts, held inputs, final counter-steering,
launch-stick variants, shortened edit windows, and earlier-kick variants of the
other successful seeds.

No candidate combined an earlier star touch with an exit before baseline VI
546. Forty-one retained the VI 538 touch but exited at VI 548; thirteen tied the
baseline exit without an earlier touch; thirty-two missed the star. The one
initial emulator timeout was retried and classified.

The negative result led to the wider analog grid, which found several distinct
collision branches that touch at VI 538 and exit at VI 546. See the
[successful refined search](../wall_kicks_touch_search/README.md).

Reproduce:

```powershell
python tools\research\wkw_landing_search.py
python tools\research\wkw_landing_search.py --retry-errors
```
