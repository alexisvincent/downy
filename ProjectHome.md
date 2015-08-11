Downy is a robot that syncs between a Mercurial repository and a wave.

Right now it's just a proof of concept: it's just a WSGI server that hosts both a Mercurial repository and a robot that uses the Wave API. The goal is to have the robot update the wave with the contents of its repository and commit changes from the wave back into the repository.

The name "downy" refers to Markdown, because this robot was built with an eye towards being used to maintain a project wiki that lives in a Mercurial repository -- but that is a single, not the only, use case.