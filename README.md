# Mp4-To-Srv3

A Python Programm That Converts Mp4 files to Srv3 files

## Requirements

python3, opencv and numpy

## How to install

[Python](https://www.python.org/downloads/)

if you have python setup do

```shell
$ pip install -r requirements.txt
```

## Example

```shell
$ python main.py "Bad Apple.mp4" 12 --subfile "Bad Apple.srt"
```

## What do The Arguments mean

| Argument        | Required | Description                                            |
|-----------------|----------|--------------------------------------------------------|
| `--msoffset`    | No       | After how many milliseconds should the animation start |
| `--subfile`     | No       | Your input subtitle file                               |
| `--submsoffset` | No       | At which milisecond the subtitles start                |
| `file`          | Yes      | Your input mp4 file                                    |
| `rows`          | Yes      | How many characters Per Column                         |