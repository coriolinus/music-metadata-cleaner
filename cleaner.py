#!/usr/bin/env python3
from functools import partial
from pathlib import Path
import re

import mutagen
import toml


def get_settings():
    with open('settings.toml', 'r') as settings_file:
        settings = toml.loads(settings_file.read())
    settings['media_extensions'] = set(settings['media_extensions'])
    settings['cleanup_regexes'] = [re.compile(rx) for rx in settings['cleanup_regexes']]
    return settings


def clean_unicode_for_print(s):
    "Clean up unicode which doesn't print on Windows"
    try:
        return str(s).encode('cp437', 'namereplace').decode('cp437')
    except UnicodeDecodeError:
        return str(s).encode('cp437', 'replace').decode('cp437')


def iter_media(root, media_extensions):
    root_path = Path(root).resolve()
    if not root_path.exists():
        raise ValueError("Couldn't locate {}".format(root))
    if not root_path.is_dir():
        raise ValueError("'{}' is not a directory".format(root))
    root = root_path

    for child in root.iterdir():
        if child.is_dir():
            yield from iter_media(root / child, media_extensions)
        elif child.is_file() and child.suffix in media_extensions:
            yield child


def handle_media(media_path, regexes, verbose, dry_run):
    if verbose:
        print("{}: ".format(clean_unicode_for_print(media_path)))
    try:
        media = mutagen.File(media_path, easy=True)
    except mutagen.MutagenError:
        return False  # can't load it? skip it
    if not media:
        return False
    try:
        # title field (often TIT2) not found
        # we can't read the metadata
        title = media['title'][0]
    except KeyError:
        return False
    for regex in regexes:
        try:
            rm = regex.match(title)
        except KeyError:
            continue
        if not rm:
            continue
        old_title = rm.group(0)
        new_title = rm.group('keep')
        if not verbose:
            print("{}: ".format(clean_unicode_for_print(media_path)))
        print(clean_unicode_for_print("\t{} => {}".format(old_title, new_title)))
        if not dry_run:
            media['title'] = new_title
            media.save()
        return True
    return False


def run(path_generator, media_handler):
    """
    Takes two functions: path_generator and media_handler.
    `path_generator` is expected to take no arguments and yield some number of paths.
    `media_handler` is expected to take one argument, the path to some piece of media.

    Users are expected to prepare these functions from `iter_media` and `handle_media`
    respectively using `functools.partial`.
    """
    modifications = 0
    for media_path in path_generator():
        if media_handler(str(media_path)):
            modifications += 1
    print("{} media entries modified".format(modifications))


if __name__ == '__main__':
    import argparse

    settings = get_settings()

    parser = argparse.ArgumentParser("Clean up id3 tags")

    parser.add_argument('-p', '--path', default=settings['default_path'],
                        help="Path to search for files to adjust. Default: '{}'".format(settings['default_path']))
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Name every file operated on')
    parser.add_argument('-d', '--dry-run', action='store_true',
                        help="Don't modify any files, just name those which would be acted on")

    args = parser.parse_args()

    run(
        partial(iter_media, args.path, settings['media_extensions']),
        partial(handle_media, regexes=settings['cleanup_regexes'],
                verbose=args.verbose, dry_run=args.dry_run),
    )
