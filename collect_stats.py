#!/usr/bin/env python3

import csv
import datetime
import dateutil.parser
import os
import re
import requests
import subprocess
import sys
import typing

TOKEN = os.environ.get("ACCESS_TOKEN", "")
EXTENSIONS = (".cpp", ".java", ".py")
DATA_FILEPATH = os.path.join(sys.path[0], "data.csv")
README_FILEPATH = os.path.join(sys.path[0], "README.md")


def get_latest_commit() -> typing.Tuple[str, typing.List]:
  url = "https://api.github.com/repos/arkn98/cp-everyday/commits/master"
  headers = {"Authorization": "token " + TOKEN}
  response = requests.get(url, headers=headers)
  if not response.ok:
    response.raise_for_status()

  # get commit date
  body = response.json()
  commit_date_str = body["commit"]["committer"]["date"]
  commit_date = dateutil.parser.isoparse(commit_date_str).date()

  # get the count of files added
  added_files = []
  for f in body["files"]:
    if f["status"] == "added" and f["filename"].lower().endswith(EXTENSIONS):
      added_files.append(f["filename"])

  return commit_date, added_files


def update_stats(data: typing.Tuple[str, typing.List]):
  commit_date, added_files = data

  # get date string
  date = commit_date.strftime("%d/%m")

  # read existing data
  to_write = []
  with open(DATA_FILEPATH) as f:
    reader = csv.reader(f, delimiter=" ")
    to_write = [tuple(row) for row in reader]
  del to_write[-1]

  # store only 12 entries
  if len(to_write) >= 11:
    del to_write[:1]
  to_write.append((date, len(added_files)))
  # gnuplot wont show the point of the most recent date on the plot,
  # so we add another dummy entry
  next_day = commit_date + datetime.timedelta(days=1)
  to_write.append((next_day.strftime("%d/%m"), 0))

  # update contents
  with open(DATA_FILEPATH, "w") as f:
    writer = csv.writer(f, delimiter=" ")
    for row in to_write:
      writer.writerow(row)


def plot() -> str:
  fig = subprocess.check_output(["gnuplot", "plot"]).decode("utf-8")
  fig = "```\n{}```".format(fig)
  return fig


# copied from https://github.com/simonw/simonw/blob/main/build_readme.py
def replace_chunk(content, marker, chunk, inline=False) -> str:
  r = re.compile(
    r"<!\-\- {} start \-\->.*<!\-\- {} end \-\->".format(marker, marker),
    re.DOTALL,
  )
  if not inline:
    chunk = "\n{}\n".format(chunk)
  chunk = "<!-- {} start -->{}<!-- {} end -->".format(marker, chunk, marker)
  return r.sub(chunk, content)


def update_readme(fig):
  with open(README_FILEPATH, "r+") as f:
    readme_contents = f.read()
    f.seek(0)
    to_write = replace_chunk(readme_contents, "cp-progress", fig)
    f.write(to_write)


def main():
  try:
    data = get_latest_commit()
    update_stats(data)
    fig = plot()
    update_readme(fig)
  except requests.HTTPError as e:
    print("request to GitHub API failed: " + str(e))
  except Exception as e:
    print("something went wrong: " + str(e))


if __name__ == "__main__":
  main()
