# mediasync

Command line tool for various media synchronization utilities.

usage:

    python -m mediasync -h

## Examples

1. List Winamp playlists:

        $ python -m mediasync listplaylists -s winamp

1. List Winamp playlist files: 

        $ python -m mediasync listplaylist -s winamp Cyberpunk

1. Synchronize playlist files to a directory: 

        $ python -m mediasync syncplaylist -s winamp Cyberpunk /tmp/play/

1. Common usage: 

        $ python -m mediasync syncplaylist -r -s winamp Latest /run/media/${USER}/USB128GB/music/001-Latest

