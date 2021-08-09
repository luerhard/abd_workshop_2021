def chunks(iterable, chunksize=2):
    """
    generator. chunks an iterable into chunks of size 'chunksize'.
    The last chunk contains the rest of the iterable any may
    be of len(chunk) < chunksize.

    Parameters
    ----------
    iterable:
        any iterable
    chunksize:
        size of the chunks.

    Returns:
    --------
        iterable of chunks.

    """
    iterable = iter(iterable)
    temp = [next(iterable)]

    for item in iterable:
        if len(temp) == chunksize:
            yield temp
            temp = []
        temp.append(item)
    if temp:
        yield temp

        
def flatten_list(li):
    if isinstance(li, list):
        return sum(map(flatten_list, li), [])
    return [li]
