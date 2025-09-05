# Mp4-To-Srt

A Python Programm That Converts Mp4 files to Srt files

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
$ python main.py "Bad Apple.mp4" 40
```

## What do The Arguments mean

| Argument        | Required | Description                                            |
|-----------------|----------|--------------------------------------------------------|
| `--msoffset`    | No       | After How many milliseconds should the animation start |
| `--idoffset`    | No       | At which subtitle id should it start                   |
| `--submsoffset` | No       | At which milisecond the subtitles start                |
| `file`          | Yes      | Your input mp4 file                                    |
| `collums`       | Yes      | How many characters Per Row                            |