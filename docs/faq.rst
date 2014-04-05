Common questions
================

Tech questions
--------------

Why aren't you using salts? Salts make everything more secure!
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Though this might be technically right, in our current use case
we are using the hash for lookup and confirmation. If we used a
salt to generate them then people wouldn't be able to generate
them anylonger on their own unless you'd make them either server-
wide or generally distribute them, in any case rendering it kinda
useless.

It would be as if you'd put a salt into a hash of a file. Either
you redistribute it, too, or now one will be able to confirm it.

If you aren't storing my data, how is Mario (the frontend) able to show it? 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Mario_ indeed knows about this information but the It-se.me
API-Server doesn't. Mario stores it on your System via LocalStorage
for convienience. 




API questions
-------------

Is there a reference implementation?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Yes. The `frontend`_ itself uses the same API (and nothing else). Please
look at the `Mario Source code`_ for a complete registration flow
implementation. A second also contact-flow-complete version is in the
works for SecureChat_.


I found a bug in the API, where can I report it?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Please do report them on our `Github Issue Tracker`_.


.. _Github Issue Tracker: yoloyolo