"""
mediasync: Various utilities to query and synchronize media.

usage: python -m mediasync

Examples:
  List Winamp playlists: $ python -m mediasync listplaylists -s winamp
  List Winamp playlist files: $ python -m mediasync listplaylist -s winamp Cyberpunk
  Synchronize playlist files to a directory: $ python -m mediasync syncplaylist -s winamp Cyberpunk /tmp/play/
  Common usage: $ python -m mediasync syncplaylist -r -s winamp Latest /run/media/${USER}/USB128GB/music/001-Latest
"""

import io
import os
import sys
import glob
import time
import shutil
import inspect
import os.path
import pathlib
import argparse
import traceback
import subprocess
import xml.dom.minidom

VERSION = "0.0.1"

class DetailedErrorArgumentParser(argparse.ArgumentParser):
  def error(self, message):
    sys.stderr.write("Error: {}\n\n".format(message))
    self.print_help()
    sys.exit(1)

def add_remainder_arg(parser):
  parser.add_argument("args", help="Arguments for the data source", nargs=argparse.REMAINDER)

def add_basics_args(parser):
  parser.add_argument("-s", "--source", choices=["winamp"], help="Media source", required=True)
  parser.add_argument("--directory", default="~/.wine/drive_c/users/${USER}/Application Data/Winamp/", help="Data directory")
  parser.add_argument("--encoding", default="ISO-8859-1", help="Data encoding")
  parser.add_argument("--dataoffset", default=2, help="Data offset")
  parser.add_argument("--lineseparator", default="\n", help="Line separator")

def get_winamp_playlists_xml(options):
  playlists_xml_file = pathlib.Path(os.path.join(f"{os.path.expandvars(os.path.expanduser(options.directory))}", "Plugins/ml/playlists/playlists.xml")).read_text(encoding=options.encoding)
  playlists_xml_file = playlists_xml_file[options.dataoffset:]
  dom = xml.dom.minidom.parseString(playlists_xml_file)

  if options.debug:
    print(dom.toprettyxml())

  return dom

def get_winamp_playlist_files(options, playlist_name, playlists_dom):
  if playlist_name == "Winamp Playlist":
    return get_winamp_playlist_files_with_path(options, pathlib.Path(os.path.join(f"{os.path.expandvars(os.path.expanduser(options.directory))}", "winamp.m3u8")))

  for child in playlists_dom.documentElement.getElementsByTagName("playlist"):
    playlist = child.getAttribute("title")
    if options.playlist_name == playlist:
      return get_winamp_playlist_files_with_path(options, pathlib.Path(os.path.join(f"{os.path.expandvars(os.path.expanduser(options.directory))}", "Plugins/ml/playlists/", child.getAttribute("filename"))))

  return []

def get_winamp_playlist_files_with_path(options, playlist_path):
  if options.debug:
    print(f"Found playlist file {playlist_path}")
    
  playlist_file = playlist_path.read_text(encoding="UTF-8")

  if options.debug:
    print(playlist_file)

  result = []
  lines = playlist_file.split(options.lineseparator)
  for line in lines:
    line = line.strip()
    if len(line) > 0 and not line.startswith("#") and line.find("#EXTM3U") == -1:
      if line.startswith("Z:\\"):
        line = line[2:].replace("\\", "/")
      result += [line]

  return result

def main():
  try:
    args = sys.argv[1:]
    parser = DetailedErrorArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-v", "--version", action="version", version="mediasync {}".format(VERSION))
    parser.add_argument("-d", "--debug", action="store_true", help="Debug", default=False)
    subparsers = parser.add_subparsers(title="action", help="Run `action -h` for additional help", dest="action", required=True)

    #subparser = subparsers.add_parser("test", help="Test")
    #add_remainder_arg(subparser)

    subparser = subparsers.add_parser("listplaylists", help="List media")
    add_basics_args(subparser)

    subparser = subparsers.add_parser("listplaylist", help="List playlist items")
    add_basics_args(subparser)
    subparser.add_argument("playlist_name", help="Playlist name")

    subparser = subparsers.add_parser("syncplaylist", help="Synchronize playlist items")
    add_basics_args(subparser)
    subparser.add_argument("-r", "--rmdir", action="store_true", help="Remove existing directory", default=False)
    subparser.add_argument("-n", "--useplaylistnamedir", action="store_true", help="Use the playlist name as a destination subdirectory", default=False)
    subparser.add_argument("-q", "--nosync", action="store_true", help="Do not perform sync on Linux", default=False)
    subparser.add_argument("playlist_name", help="Playlist name")
    subparser.add_argument("destination", help="Destination directory")

    options = parser.parse_args(args)

    if options.action == "listplaylists":
      if options.source == "winamp":
        dom = get_winamp_playlists_xml(options)
        print("Winamp Playlist")
        for child in dom.documentElement.getElementsByTagName("playlist"):
          playlist = child.getAttribute("title")
          print(playlist)
      else:
        raise NotImplementedError()

    elif options.action == "listplaylist":
      if options.source == "winamp":
        dom = get_winamp_playlists_xml(options)

        files = get_winamp_playlist_files(options, options.playlist_name, dom)
        if len(files) > 0:
          for file in files:
            print(file)
        else:
          print("Error: playlist not found")
      else:
        raise NotImplementedError()

    elif options.action == "syncplaylist":

      destination = pathlib.Path(options.destination)

      if options.useplaylistnamedir:
        destination = destination.joinpath(options.playlist_name)

      if options.rmdir and destination.exists():
        #shutil.rmtree(destination)

        for destination_path in glob.glob(f"{destination}/*"):
          if os.path.isdir(destination_path):
            shutil.rmtree(destination)
          else:
            os.remove(destination_path)

        print(f"Recursively deleted {destination}")
      
      if not destination.exists():
        destination.mkdir(parents=True)

      if options.source == "winamp":
        dom = get_winamp_playlists_xml(options)

        files = get_winamp_playlist_files(options, options.playlist_name, dom)
        if len(files) > 0:

          print(f"Copying {len(files)} files to {destination}...")

          i = 1
          copied = 0

          copied_files = []

          for file in files:
            filepath = pathlib.Path(file)

            number_width = 9

            if len(files) < 10:
              number_width = 1
            elif len(files) < 100:
              number_width = 2
            elif len(files) < 1000:
              number_width = 3
            elif len(files) < 10000:
              number_width = 4
            elif len(files) < 100000:
              number_width = 5

            format_string = "{0:0" + str(number_width) + "}"
            destination_name = format_string.format(i)
            destination_name += " - "
            destination_name += filepath.name
            destination_path = destination.joinpath(destination_name)

            print(f"[{i}/{len(files)}] Copying {file} to {destination_path}")

            i += 1

            if filepath.exists():
              shutil.copyfile(file, destination_path)
              copied += 1

              copied_files.append(destination_path)
            else:
              print(f"Warning: File not found: {filepath}")
          
          # Now touch in reverse order so that the first file is newest
          i = 1
          for file in reversed(copied_files):
            print(f"[{i}/{len(copied_files)}] Touching {file}")
            pathlib.Path(file).touch()
            time.sleep(1)
            i += 1

          print(f"Finished touching files")

          if sys.platform != "win32" and not options.nosync:
            print("Performing sync...")
            completed_process = subprocess.run("sudo sync", shell=True, check=True, capture_output=True)
            if completed_process.stdout is not None and len(completed_process.stdout) > 0:
              print(f"stdout: {completed_process.stdout}")
            if completed_process.stderr is not None and len(completed_process.stderr) > 0:
              print(f"stderr: {completed_process.stderr}")

          print(f"Copied {copied} files to {destination}")
        else:
          print("Error: playlist not found")
      else:
        raise NotImplementedError()

    else:
      raise NotImplementedError()

  except:
    e = sys.exc_info()[0]
    if e != SystemExit:
      traceback.print_exc()
