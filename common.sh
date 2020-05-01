#!/bin/sh
P="Latest"; F="001"; python -m mediasync syncplaylist -r -s winamp "${P}" "/run/media/${USER}/USB128GB/music/${F}-${P}"
P="Favorites"; F="002"; python -m mediasync syncplaylist -r -s winamp "${P}" "/run/media/${USER}/USB128GB/music/${F}-${P}"
