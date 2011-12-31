from hashlib import md5

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
