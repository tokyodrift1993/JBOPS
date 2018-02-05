'''
Share or unshare libraries.

optional arguments:
  -h, --help            show this help message and exit
  --share               To share libraries.
  --unshare             To unshare all libraries.
  --user  [ ...]        Space separated list of case sensitive names to process. Allowed names are:

                        (choices: All users names)
  --libraries  [ ...]
                        Space separated list of case sensitive names to process. Allowed names are:
                        (choices: All library names)
                        (default: All Libraries)

  --sync                Allow user to sync content
  --camera              Allow user to upload photos
  --channel             Allow user to utilize installed channels
  --movieRatings        Add rating restrictions to movie library types
  --movieLabels         Add label restrictions to movie library types
  --tvRatings           Add rating restrictions to show library types
  --tvLabels            Add label restrictions to show library types
  --musicLabels         Add label restrictions to music library types

Usage:

   plex_api_share.py --share --user USER --libraries Movies
       - Shared libraries: ['Movies'] with USER

   plex_api_share.py --share --allUsers --libraries Movies
       - Shared libraries: ['Movies'] with USER
       - Shared libraries: ['Movies'] with USER1 ...

   plex_api_share.py --share --user USER --libraries Movies "TV Shows"
       - Shared libraries: ['Movies', 'TV Shows'] with USER
          * Double Quote libraries with spaces

   plex_api_share.py --share -u USER --allLibraries
       - Shared all libraries with USER.

   plex_api_share.py --unshare -u USER
       - Unshared all libraries with USER.
       - USER is still exists as a Friend or Home User

   Excluding;
   
   --user becomes excluded if --allUsers is set
   plex_api_share.py --share --allUsers -u USER --libraries Movies
       - Shared libraries: ['Movies' ]with USER1.
       - Shared libraries: ['Movies'] with USER2 ... all users but USER

   --libraries becomes excluded if --allLibraries is set
   plex_api_share.py --share -u USER --allLibraries --libraries Movies
       - Shared [all libraries but Movies] with USER.

'''

from plexapi.server import PlexServer
import argparse
import requests

PLEX_URL = 'http://localhost:32400'
PLEX_TOKEN = 'xxxxxxx'

ratings_lst = ['G', 'PG', 'PG-13', 'R', 'NC-17', 'TV-G', 'TV-Y', 'TV-Y7', 'TV-14', 'TV-PG', 'TV-MA']

sess = requests.Session()
sess.verify = False
plex = PlexServer(PLEX_URL, PLEX_TOKEN, session=sess)


user_lst = [x.title for x in plex.myPlexAccount().users()]
sections_lst = [x.title for x in plex.library.sections()]


def share(user, sections, allowSync, camera, channels, filterMovies, filterTelevision, filterMusic):
    plex.myPlexAccount().updateFriend(user=user, server=plex, sections=sections, allowSync=allowSync,
                                      allowCameraUpload=camera, allowChannels=channels, filterMovies=filterMovies,
                                      filterTelevision=filterTelevision, filterMusic=filterMusic)
    print('Shared libraries: {libraries} with {user}.'.format(libraries=libraries, user=user))


def unshare(user, libraries):
    plex.myPlexAccount().updateFriend(user=user, server=plex, removeSections=True, sections=libraries)
    print('Unshared all libraries from {user}.'.format(user=user))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Share or unshare libraries.",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--share', default=False, action='store_true',
                        help='To share libraries.')
    parser.add_argument('--unshare', default=False, action='store_true',
                        help='To unshare all libraries.')
    parser.add_argument('--user', nargs='+', choices=user_lst, metavar='',
                        help='Space separated list of case sensitive names to process. Allowed names are: \n'
                             '(choices: %(choices)s)')
    parser.add_argument('--allUsers', default=False, action='store_true',
                        help='Select all users.')
    parser.add_argument('--libraries', nargs='+', default=False, choices=sections_lst, metavar='',
                        help='Space separated list of case sensitive names to process. Allowed names are: \n'
                             '(choices: %(choices)s')
    parser.add_argument('--allLibraries', default=False, action='store_true',
                        help='Select all users.')
    parser.add_argument('--sync', default=False, action='store_true',
                        help='Use to allow user to sync content.')
    parser.add_argument('--camera', default=False, action='store_true',
                        help='Use to allow user to upload photos.')
    parser.add_argument('--channels', default=False, action='store_true',
                        help='Use to allow user to utilize installed channels.')
    parser.add_argument('--movieRatings', nargs='+', choices=ratings_lst, metavar='',
                        help='Use to add rating restrictions to movie library types.')
    parser.add_argument('--movieLabels', nargs='+',
                        help='Use to add label restrictions for movie library types.')
    parser.add_argument('--tvRatings', nargs='+', choices=ratings_lst, metavar='',
                        help='Use to add rating restrictions for show library types.')
    parser.add_argument('--tvLabels', nargs='+',
                        help='Use to add label restrictions for show library types.')
    parser.add_argument('--musicLabels', nargs='+',
                        help='Use to add label restrictions for music library types.')


    opts = parser.parse_args()
    users = ''
    libraries = ''
    filterMovies = {}
    filterTelevision = {}
    filterMusic = {}

    # Setting additional share options
    if opts.movieLabels:
        filterMovies['label'] = opts.movieLabels
    if opts.movieRatings:
        filterMovies['contentRating'] = opts.movieRatings
    if opts.tvLabels:
        filterTelevision['label'] = opts.tvLabels
    if opts.tvRatings:
        filterTelevision['contentRating'] = opts.tvRatings
    if opts.musicLabels:
        filterMusic['label'] = opts.musicLabels

    # Defining users
    if opts.allUsers and not opts.user:
        users = user_lst
    elif not opts.allUsers and opts.user:
        users = opts.user
    elif opts.allUsers and opts.user:
        # If allUsers is used then any users listed will be excluded
        for user in opts.user:
            user_lst.remove(user)
            users = user_lst

    # Defining libraries
    if opts.allLibraries and not opts.libraries:
        libraries = sections_lst
    elif not opts.allLibraries and opts.libraries:
        libraries = opts.libraries
    elif opts.allLibraries and opts.libraries:
        # If allLibraries is used then any libraries listed will be excluded
        for library in opts.libraries:
            sections_lst.remove(library)
            libraries = sections_lst
    elif not all([opts.libraries, opts.allLibraries]):
        print('No libraries defined.')
        exit()

    # Share or Unshare
    for user in users:
        if opts.share and libraries:
            share(user, libraries, opts.sync, opts.camera, opts.channels, filterMovies, filterTelevision, filterMusic)
        elif opts.unshare:
            unshare(user, sections_lst)
        else:
            print('I don\'t know what you want.')
