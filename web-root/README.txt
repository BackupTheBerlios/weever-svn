THIS SOFTWARE IS UNDER MIT LICENSE.
(C) 2004 Valentino Volonghi, Andrea Peltrin

Read LICENSE file for more informations

REQUIREMENTS:

Weever should run on FreeBSD, Linux and Win32 without any problems (at
least I've tried on these platforms and it worked). You should just
download and install:

* PostgreSQL 7.4 and above:
    win32: Use version 8.0-beta1 and above
    both win32 and *nix version available here: http://www.postgresql.org

* Psycopg2:
    win32:  http://www.stickpeople.com/projects/python/psycopg/index.html
    *nix: http://www.initd.org or look for psycopg package in your distribution
    source: http://initd.org/pub/software/psycopg/ALPHA/psycopg-1.99.10.tar.gz

* Twisted (svn: svn://svn.twistedmatrix.com/svn/Twisted/trunk) 

* Nevow (svn: svn://divmod.org/svn/Nevow/trunk)

* ZopeInterface-3.0b1 and above:
    Available from: http://www.zope.org/Products/ZopeInterface/
    ZopeInterface from Zope3 SVN works well too.


NOTES:
Since Weever is currently under heavy development, you will need to get the 
very latest versions (from SVN) of both Twisted (required) and Nevow (required).
An additional dependency required by Twisted is ZopeInterface which can be downloaded from:
http://www.zope.org/Products/ZopeInterface/

I've tested it with psycopg2, but since I'm not using any special features provided with 
psycopg2 it should work with psycopg1 too.
