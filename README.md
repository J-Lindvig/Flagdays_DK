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
+ ~~time_offset~~ is now **offset** (Again). Default is 10 minutes
+ ~~hide_past~~ is removed.
+ ~~flags~~ is removed. We are now using **include** and **exclude**.

For installation instructions [see this guide](https://hacs.xyz/docs/faq/custom_repositories).
## Quick start
Add the following to your configuration.yaml
```yaml
flagdays_dk:
  # Optional entries
  
  # Time in minutes before flag up/down times, used for triggers fx. automation, Default is 10
  offset: 5

  # Include and Exclude options
  include:
    - Erfalasorput    # Either name of a special (commonwealth) flag
    - Færøerne        # or a string with a part of the flagdays name

  # Strings to be present in the flagdays name and which should be excluded
  exclude:
    - Kongelig
    - Udsendte

  # List of private flagdays
  flagdays:
    # Sensor with a datetime attribute named **date**
    - sensor.birthday_hjaltes_fodselsdag

    # Group of sensors with a datetime attribute named **date**
    - group.birthdays

    # Manual entry with a custom flag, calculation of age (year stated in date) and a high priority (0 = highest)
    - name: Jolly Roger Memorial Day
      flag: Jolly Roger
      date: 10-06-1975
      priority: 2

    # Manual entry with a prolonged event (**date_end**) and custom flag
    - name: Copenhagen Pride Month
      flag: Pride
      date: 01-08
      date_end: 31-08

    # Manual entry with calculation of age (year stated in date)
    - name: Tim Berners Lee Birthday
      date: 08-06-1955

    # Manual entry with calculation of age (year stated in date)
    - name: Ada Lovelace Birthday
      date: 10-12-1815
```
## State and attributes
State is the number of days to the event.
![image](https://user-images.githubusercontent.com/54498188/212568684-7572c620-a79e-4b3a-a61b-5148eb03d5be.png)
Friendly name is the name of the next flagday.


### Attributes

| Attribute name             | Description                        |
|----------------------------|------------------------------------|
| name                       | Name of the flagday                |
| flag                       | Name of flag to use                |
| years                      | Age to come, if calculated         |
| flag_up_time               | Time to hoist the flag             |
| flag_down_time             | Time to pull the flag              |
| flag_up_time_trigger       | Trigger to use for flag up         |
| flag_down_time_trigger     | Trigger to use for flag down       |
| half_mast                  | True/False/Time for full mast      |
| future_flagdays            | List of flagdays in the future     |
| attribution                | Name of the creator                |
