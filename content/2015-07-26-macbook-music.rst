:title: Music playback on machines with tiny storage
:slug: macbook-music
:tags: music, mpd, osxmpdkeys, subsonic
:date: 2015-07-26 12:30:43

With the advent of solid state storage, the once massive drives of spinning rust that shipped in laptops got faster but tinier. While the advent of streaming services (Spotify, Google Music, Pandora, etc) solved this for most people, I'm a bit more traditional relying on my own library. I generally enjoy listening to music whilst working on the compute box, but I had three primary requirements:

#) Not iTunes (are there non-muggles who like iTunes?)
#) Leverages central storage for actual music data, as to not duplicate the data and save disk on workstation
#) Allow for media control keys on the macbook keyboard to continue working.

I wanted a solution for being on the local network and another when remote.

Local
=====

Wanting a light weight solution, I decided to fall back on `MPD <http://www.musicpd.org/>`_ controlled by `NCMPCPP <http://ncmpcpp.rybczak.net/>`_.  The MPD instance on the macbook will get the metadata from a MPD instance on the NAS, and plays the FLACs natively from the NFS store on the NAS.

Since the NAS has no soundcard, I configured the `null audio output <http://www.musicpd.org/doc/user/output_plugins.html>`_ and it just hangs out scanning for new media and presents the database to the network.

On the macbook I installed MPD via `brew <http://brew.sh/>`_ with the NFS option: ``brew install mpd --with-libnfs`` and configured MPD to act as a `satellite <http://www.musicpd.org/doc/user/advanced_config.html#satellite>`_ with the following configs:
::

	music_directory "nfs://nas.local/mnt/music/"
	database {
	    plugin "proxy"
	    host "nas.local"
	}

Now the local mpd/ncmpcpp plays all the flacs natively just fine from the NAS. But not having media keys were driving me crazy! When in doubt, just go to github and search for random projects to see if anyone already hacked something together. From there, I found `osxmpdkeys <https://github.com/pushrax/osxmpdkeys>`_. Once I pointed it to the local MPD instance, the media keys just magically started working! Simple service to capture keypress and send it to the daemon. Brilliant.

Remote
======

On the NAS I also run an instance of `Subsonic <http://www.subsonic.org/>`_ for use on my phone, and for playback when I'm out and about doing computing things. I used `Clementine <https://www.clementine-player.org/>`_, a thick client player, for a while for Subsonic playback but it was a little too heavy. Since I actually like the Subsonic web interface, all I had to do was launch `BeardedSpice <http://beardedspice.com/>`_ and now I had media keys.


TODO
====

If I end up doing more remote computing, I reckon I will set up `Mopidy <https://www.mopidy.com/>`_ with a subsonic backend to maintain a consistant interface for playback. Also, BeardedSpice seems like a pretty squared away project so I may try writing a MPD handler.
