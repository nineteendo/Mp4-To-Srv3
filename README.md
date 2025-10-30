# Mp4-To-Srv3

A Python program that converts Mp4 files to Srv3 files

## Installation

- Install Python 3: https://www.python.org/downloads
- Install `mp4_to_srv3` command:
    ```shell
    $ pip install .
    ```

## Example

```shell
$ mp4_to_srv3 input/video.mp4 --subfile input/captions.srt --dir output --rows 12 --layers 1 --targetsize 12
```

## Command line arguments

| Argument        | Required          | Description                       |
|-----------------|-------------------|-----------------------------------|
| `file`          | Yes               | Input mp4/png file                |
| `--subfile`     | No                | Input srt file                    |
| `--dir`         | No (default: '.') | Output folder                     |
| `--msoffset`    | No (default: 0)   | Millisecond offset of input files |
| `--submsoffset` | No (default: 0)   | Millisecond offset of output file |
| `--rows`        | No (default: 12)  | Number of characters per column   |
| `--layers`      | No (default: 1)   | Number of stacked frames          |
| `--targetsize`  | No (default: 12)  | Target size in MB                 |
