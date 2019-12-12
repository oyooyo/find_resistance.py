# find_resistance.py

A command line tool for finding possibilities for creating a resistance close to a certain target value, by combining resistors.

Written in Python 3.

## Usage

```console
$ find_resistance.py -h
usage: find_resistance.py [-h] [--resistors RESISTORS] [--maximum MAXIMUM]
                          [--results RESULTS]
                          target_value

Find possibilities for creating a resistance close to a certain target value,
by combining resistors

positional arguments:
  target_value          The target resistance value

optional arguments:
  -h, --help            show this help message and exit
  --resistors RESISTORS, -r RESISTORS
                        The available resistor values, as a comma-separated
                        list, for example "100R,330,4k7,10k,1.0M" (Default:
                        All E6 series values)
  --maximum MAXIMUM, --max MAXIMUM, -m MAXIMUM
                        The maximum number of resistors to use. Increasing
                        this value exponentially increases computation time!
                        (Default: 2)
  --results RESULTS, -n RESULTS
                        The maximum number of results to output, or 0 for all
                        results. Results will be ordered by their deviation
                        from the target value (Default: 1)
```

## Examples

Find a resistance close to 50 ohms, using the E6 series resistors:
```console
$ find_resistance.py 50
50Ω (+0Ω/+0%): (100||100)Ω

─┬─[100Ω]──┬─
 └─[100Ω]──┘ 
```

Find a resistance close to 4850 ohms, using only resistors with 100, 300, 4700, 10000 or 1000000 ohms. Use at most 3 resistors, show the best 3 results:
```console
$ find_resistance.py 4.85k --resistors 100R,330,4k7,10k,1.0M --maximum 3 --results 3
4845.361Ω (-4.639Ω/-0.096%): (10000||(4700+4700))Ω

─┬─[10000Ω]──────────┬─
 └─[4700Ω]──[4700Ω]──┘ 
========================================
4865Ω (+15Ω/+0.309%): (4700+(330||330))Ω

─[4700Ω]──┬─[330Ω]──┬─
          └─[330Ω]──┘ 
========================================
4800Ω (-50Ω/-1.031%): (4700+100)Ω

─[4700Ω]──[100Ω]─
```
