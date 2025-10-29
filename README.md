# Mp4-To-Srv3

A Python program that converts Mp4 files to Srv3 files

## Installation

- Install Python 3: https://www.python.org/downloads
- Install requirements:
    ```shell
    $ pip install -r requirements.txt
    ```

## Example

```shell
$ python main.py "Bad Apple.mp4" --subfile "Bad Apple.srt" --rows 12 --layers 1 --targetsize 12
```

## Command line arguments

| Argument        | Required         | Description                       |
|-----------------|------------------|-----------------------------------|
| `file`          | Yes              | Input mp4/png file                |
| `--subfile`     | No               | Input srt file                    |
| `--msoffset`    | No (default: 0)  | Millisecond offset of input files |
| `--submsoffset` | No (default: 0)  | Millisecond offset of output file |
| `--rows`        | No (default: 12) | Number of characters per column   |
| `--layers`      | No (default: 1)  | Number of stacked frames          |
| `--targetsize`  | No (default: 12) | Target size in MB                 |
