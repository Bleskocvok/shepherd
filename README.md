# Shepherd
Discord BOT for scheduling exercise.

## How to run

First clone the repository.

```bash
git clone --recurse-submodules https://github.com/Bleskocvok/shepherd.git
```

Then you can either run manually or using docker.

- Run manually

  ```bash
  python3 run.py
  ```

- Using Docker
  ```bash
  docker build -t shepherd . # builds it
  docker run --rm shepherd   # runs it
  ```

## Usage

`!help`
`!schedule XX:XX`
`!cancel`
`!status`
`!did N`
`!stats`
`!buff`
`!stats NAME`
`!allstats`
