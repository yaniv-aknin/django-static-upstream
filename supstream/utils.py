import os
import uuid
import logging
from hashlib import md5
from subprocess import Popen, PIPE

logger = logging.getLogger(__name__)
logger.error('foo!')

# ideas for optimizing this abound, but for now it's Good Enough
def file_digest(filename, return_contents=False):
    contents = []
    context = md5()
    with open(filename, 'rb') as handle:
        for block in iter(lambda: handle.read(128*context.block_size), ''):
            context.update(block)
            if return_contents:
                contents.append(block)
    return context.hexdigest(), "".join(contents)

def find_upwards(filename, cwd=None):
    cwd = cwd or os.getcwd()
    while True:
        if os.path.exists(os.path.join(cwd, filename)):
            return os.path.abspath(cwd)
        if os.path.abspath(cwd) == '/':
            raise EnvironmentError("unable to find %s" % (filename,))
        cwd = os.path.join(cwd, os.pardir)

class AutomagicalReleaseIDError(Exception):
    pass

def automagical_release_id(path):
    def git_handler(path):
        gitdir = find_upwards('.git', path)
        with open('/dev/null', 'w') as devnull:
            process = Popen('git rev-parse HEAD ; git diff', cwd=gitdir, shell=True,
                            stdout=PIPE, stderr=PIPE, stdin=devnull)
            stdout, stderr = process.communicate()
            rev_parse, diff = stdout.split('\n', 1)
            if process.returncode != 0:
                raise AutomagicalReleaseIDError('git handler received nonzero exit; stderr=%r' % (stderr,))
            return 'GIT-%s-%s' % (rev_parse, md5(diff).hexdigest())

    for scm_handler in (git_handler,):
        try:
            return scm_handler(path)
        except EnvironmentError:
            pass
    else:
        # fallback to random release id; this will force rehashing of served statics every time you reload code
        logger.warn('falling back to random release id; provide RELEASE_ID in settings to avoid this')
        return 'UUID-' + uuid.uuid4().hex
