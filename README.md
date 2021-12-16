# mediasync

Command line tool for various media synchronization utilities.

usage:

    python -m mediasync -h

## Examples

1. List Winamp playlists:

        $ python -m mediasync listplaylists -s winamp
        $ python -m mediasync listplaylists -s directory --directory /work/music/playlists/

1. List Winamp playlist files: 

        $ python -m mediasync listplaylist -s winamp Cyberpunk

1. Synchronize playlist files to a directory: 

        $ python -m mediasync syncplaylist -s winamp Cyberpunk /tmp/play/

1. Common usage: 

	$ P="Latest"; F="001"; python -m mediasync syncplaylist -r -s winamp "${P}" "/run/media/${USER}/USB128GB/music/${F}-${P}"
	$ P="Favorites"; F="002"; python -m mediasync syncplaylist -r -s winamp "${P}" "/run/media/${USER}/USB128GB/music/${F}-${P}"
	$ P="Favorites"; python -m mediasync syncplaylist -r -s winamp "${P}" /run/media/${USER}/*/

        $ python -m mediasync syncplaylist -r -s directory /work/music/playlists/Bballfun.m3u /run/media/kevin/7BEE-1708/
