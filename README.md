# Music Metadata Cleaner

Once upon a time, my wife had an MP3 player which sucked: it could play a folder of music, but knew nothing about metadata, so played everything only in strict alphabetical order according to the file name. Accordingly, for several years, my wife compulsively renamed her music such that the filenames put the albums in order. All unknowing, the tool she used to do this also modified the song metadata, putting the number in front of every title.

Now, all our combined music is in a NAS box together, and several hundred songs have ugly numbers ahead of their names. This irritates me, so I wrote this script to fix it.

This script is unlikely to precisely fit the use case of anyone other than ourselves, but in case it does, feel free. Be aware that this will edit your files, so if you don't trust it, be sure to make backups first. Use the `--dry-run` feature.
