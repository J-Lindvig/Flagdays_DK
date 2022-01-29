[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/J-Lindvig/Flagdays_DK?style=for-the-badge)
![GitHub all releases](https://img.shields.io/github/downloads/J-Lindvig/Flagdays_DK/total?style=for-the-badge)
![GitHub last commit](https://img.shields.io/github/last-commit/J-Lindvig/Flagdays_DK?style=for-the-badge)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/J-Lindvig/Flagdays_DK?style=for-the-badge)

# Flagdays_DK

Sensor with official flagdays in Denmark, with a option to add your own (birthdays etc.)

## Credits
Data is from [Justitsministeriet](https://www.justitsministeriet.dk/temaer/flagning/flagdage/).

Sunrises and sunsets in the future is provided by [Sunrise-Sunset](https://sunrise-sunset.org/api) API.

For installation instructions [see this guide](https://hacs.xyz/docs/faq/custom_repositories).
## Quick start
Add the following to your configuration.yaml
```yaml
flagdays_dk:
  # Optional entries
  
  # Create attributes with specified offset in minutes
  # These are to be used as triggers in automatiions
  offset: 10
  
  # List of flags that we own and wish to use
  flags:
    - grønland
    - færø
    - pride
    - Jolly Roger

  # List of custom events
  # Required: name and date
  # Optional: flag
  events:
    - name: Jolly Roger Memorial Day
      date: 01-01-2022
      flag: Jolly Roger
    - name: Copenhagen Pride
      date: 01-08-2004
    - name: Tim Berners Lee Birthday
      date: 08-06-1955
    - name: Ada Lovelace Birthday
      date: 10-12-1815
```
## State and attributes
State is the number of days to the event
![Screenshot](https://github.com/J-Lindvig/Flagdays_DK/blob/main/images/screenshot.png)
### Attributes

| Attribute name             | Example value                             | Description                        |
|----------------------------|-------------------------------------------|------------------------------------|
| event_name                 | Hendes Kongelige Højhed Kronprinsesse...  | Name of the event                  |
| date_str                   | 5. februar                                | Nice TTS date of the event         |
| date                       | 5-2-2022                                  | Date of the event                  |
| flag                       | Dannebrog                                 | Name of flag to use                |
| flag_up_time               | 08:42                                     | Time to hoist the flag             |
| flag_down_time             | 16:02                                     | Time to pull the flag              |
| flag_up_time_trigger       | 08:32                                     | Trigger to use for flag up         |
| flag_down_time_trigger     | 15:22                                     | Trigger to use for flag down       |
| timestamp                  | 1644046920                                | Timestamp of the event             |
| days_to_event              | 13                                        | Days to the event                  |
| half_mast                  | false                                     | Flag at half mast?                 |
| half_mast_all_day          | false                                     | Flag at half mast all day?         |
| up_at_night                | false                                     | Flag allowed to be up at night?    |
| attribution                | Created by J-Lindvig                      | Name of the creator                |
