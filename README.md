# Flagdays_DK

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

Sensor with official flagdays in Denmark, with a option to add your own (birthdays etc.)

## Credits
Data is from [Justitsministeriet](https://www.justitsministeriet.dk/temaer/flagning/flagdage/).

Sunrises and sunsets in the future is provided by [Sunrise-Sunset](https://sunrise-sunset.org/api) API.

For installation instructions [see this guide](https://hacs.xyz/docs/faq/custom_repositories).
## Quick start
Add the following to your configuration.yaml
```yaml
flagdays_dk:
  flags:
    # Flags we own and want to use
    - grønland
    - færø
    - pride
  events:
    # List of custom events
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
| attribution                | Created by J-Lindvig                      | Name of the creator                |
| date_str                   | 5. februar                                | Nice TTS date of the event         |
| date                       | 5-2-2022                                  | Date of the event                  |
| flag_up_time               | 08:42                                     | Time to hoist the flag             |
| flag_down_time             | 16:02                                     | Time to pulle the flag             |
| timestamp                  | 1644046920                                | Timestamp of the event             |
| days_to_event              | 13                                        | Days to the event                  |
| event_name                 | Hendes Kongelige Højhed Kronprinsesse...  | Name of the event                  |
| half_mast                  | false                                     | Flag at half mast?                 |
| half_mast_all_day          | false                                     | Falg at half mast all day?         |
| flag                       | Dannebrog                                 | Name of flag to use                |
