FRC Queuing: Back-To-Back Match Finder
==========================

## Description
This program can be used to find and mark back-to-back matches in the qualification match schedule for a specific FRC event.

For queuing, it's important to track teams that have back-to-back matches to keep the match flow running smoothly, and to prevent teams from leaving the field if they are needed back in the match queue. Most events will keep at least 2 matches queued behind the match currently playing, and some will keep 3 matches if the distance to the pits is too far. An example of a qualification schedule is shown below:

| Match Number | Blue 1 | Blue 2 | Blue 3 | Red 1 | Red 2 | Red 3 |
|--------------|--------|--------|--------|-------|-------|-------|
|       1      |  2523  |  1519  |  2370  |  4048 |  __1100__ |  2262 |
|       2      |  2342  |  1277  |  501   |  3466 |  3780 |  126  |
|       3      |  5813  |  4987  |  5969  |  1350 |  3719 |  663  |
|       4      |  __1100__  |  190   |  3236  |  1740 |  6367 |  4041 |

In this schedule, team 1100 is in match 1 and match 4. In this case, when match 1 ends, match 4 will be brought up into queue, and so team 1100 will be queued again. We want to prevent them from leaving the field because they are needed right away in queue.

We also want to note that team 1100 has to switch alliance colors between matches 1 and 4 (Red to Blue). This is something we would want to notify them about, in case they need to switch bumpers.

This program pulls the match schedule from [The Blue Alliance](https://www.thebluealliance.com/) and generates an updated schedule that notes all the information to make queuing easier and eliminate the manual work of marking each back-to-back match.

## Build

This program requires:

* [Python 2.7](https://www.python.org/download/releases/2.7/)
* An internet connection

## Execution

#### Arguments

To generate the schedule, run the program as follows:
```
python frc_back_to_back_queuer.py -i <event ID> -o <output file> -m <match count>
```

The arguments are:

* `event ID` : The __Event Model__ *key* from [The Blue Alliance](https://www.thebluealliance.com/apidocs), in the form of `yyyy[EVENT_CODE]`. For example, `2017mawor` for the [2017 WPI District event](https://www.thebluealliance.com/event/2017mawor).
* `output file` : The file path to write the generated schedule, as a TSV file.
* `match count` : The number of matches to consider for "back-to-back". This is commonly __4__ matches for most events.

You can run `python frc_back_to_back_queuer.py -h` for further help.

#### Output

An example of the output is shown below:

| Match Number | Blue 1 | Blue 2 | Blue 3 | Red 1 | Red 2 | Red 3 |
|--------------|--------|--------|--------|-------|-------|-------|
|       1      |  2523  |  1519  |  2370  |  4048 |  __1100 (M4:B1:+3)__ |  2262 |
|       2      |  2342  |  1277  |  501   |  3466 |  3780 |  126  |
|       3      |  5813  |  4987  |  5969  |  1350 |  3719 |  663  |
|       4      |  1100  |  190   |  3236  |  1740 |  6367 |  4041 |

In this output, we have marked team 1100 in match 1 with additional information. The format of this information is as follows:

`<team number> (<match number>:<next alliance>:<matches out>)`

* `team number` : The FRC team number.
* `match number` : The match number for the associated back-to-back match, noted with __M__ and then the match number.
* `next alliance` : The next alliance color (__B__ or __R__) and driver station position (__1__, __2__, __3__).
* `matches out` : The number of matches until the back-to-back match from this current match.
