[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/J-Lindvig/Flagdays_DK)
![GitHub all releases](https://img.shields.io/github/downloads/J-Lindvig/Flagdays_DK/total)
![GitHub last commit](https://img.shields.io/github/last-commit/J-Lindvig/Flagdays_DK)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/J-Lindvig/Flagdays_DK)
[![Buy me a coffee](https://img.shields.io/static/v1.svg?label=Buy%20me%20a%20coffee&message=🥨&color=black&logo=buy%20me%20a%20coffee&logoColor=white&labelColor=6f4e37)](https://www.buymeacoffee.com/apptoo)

# Flagdays_DK

Sensor with official flagdays in Denmark, with a option to add your own (birthdays etc.)

## BREAKING CHANGES
The integration has been rewritten and have received some TLC and improvements.
+ ~~offset~~ is now **time_offset**
+ flags, no change
+ ~~events~~ is now **flagdays** and the flagdays listed is now:
  + **name**, the name of the flagday
  + **flag**, the flag to use
  + **date**, the date of the flagday in either "dd-mm" or "dd-mm-yyyy". If year is stated, the years between current year and flagday will be calculated and appended to the name
  + **date_end (new feature)**, the date to end the period of prolonged flagday, fx. Pride Month.

## Credits
Data is from [Justitsministeriet](https://www.justitsministeriet.dk/temaer/flagning/flagdage/).

Sunrises and sunsets in the future is provided by [Sunrise-Sunset](https://sunrise-sunset.org/api) API.

For installation instructions [see this guide](https://hacs.xyz/docs/faq/custom_repositories).
## Quick start
Add the following to your configuration.yaml
```yaml
flagdays_dk:
  # Optional entries
  time_offset: 30
  flags:
    - erfalasorput
    - merkið
  flagdays:
    - name: Jolly Roger Memorial Day
      flag: Jolly Roger
      date: 10-06-1975

    - name: Copenhagen Pride Month
      flag: Pride
      date: 01-08
      date_end: 31-08

    - name: Tim Berners Lee Birthday
      date: 08-06-1955

    - name: Ada Lovelace Birthday
      date: 10-12-1815
```
## State and attributes
State is the number of days to the event
![image](https://user-images.githubusercontent.com/54498188/174452882-4031e5c9-3f10-4fd1-9bf5-319d6a3e48b2.png)

### Attributes

| Attribute name             | Description                        |
|----------------------------|------------------------------------|
| name                       | Name of the flagday                |
| flag                       | Name of flag to use                |
| instructions               | List of instuctions                |
| flag_up_time               | Time to hoist the flag             |
| flag_down_time             | Time to pull the flag              |
| flag_up_time_trigger       | Trigger to use for flag up         |
| flag_down_time_trigger     | Trigger to use for flag down       |
| future_flagdays            | List of flagdays in the future     |
| attribution                | Name of the creator                |
