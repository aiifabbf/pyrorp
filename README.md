Pyrorp - Python Implementation for Remote Object Reference Protocol
=====

Transparent & symmetric RPC in few lines

Quick Start
=====

Start a daemon to keep and expose local object references.
```Python
import pyrorp
daemon = pyrorp.Daemon()
daemon.run()
```
This will start a daemon, @localhost:25565 by default.

To expose a local object, use: 
```Python
daemon.register(some_object, "name_to_expose")
```
`daemon` will add this object to `self.refs`, its reference table.

On the remote side, execute the following codes to get a reference to this daemon:
```Python
import pyrorp
daemon = pyrorp.refer()
```
Now you have got a reference to `daemon` object on the other side (For safety, you can't access everything of it, though,  e.g.`daemon.stop()` :) but if you really would like to, try [edit advanced options](https://github.com/aiifabbf/pyrorp/wiki/Edit-Daemon-Advanced-Options)

Finally,
```Python
some_object = daemon.some_object
```
to get specific reference to `some_object`.

RORP intends to be a symmetric & transparent protocol and tries to hide itself behind your codes. Due to this, Pyrorp implements `_RemoteObject` and everything you do to it will be applied to the real one on the other side. 

[Detailed Documentation](github.com/aiifabbf/pyrorp/wiki/RORP-Introduction)
