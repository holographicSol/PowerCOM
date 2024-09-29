"""
PowerCom. A COM port scanner (soon to be asynchronous and multi-processed) Written by Benjamin Jack Cullen

I need to read data from COM ports with as little configuration as possible for reusability across other projects and
so to avoid hardcoded COM ports, baud rates, etc. So this experimental.

Early stages. This can still be faster. Requires a modified aiomultiprocess to accept the multiproc_dict.

"""

import sys
import asyncio
import aioserial
import multiprocessing
import aiomultiprocess
import handler_chunk
import time

baud_rates = [
    115200
]


async def power_com(aioserial_instance: aioserial.AioSerial, tags: list):
    """ discover sentence tag(s) on a COM port and return discovered sentence(s).
    (can retrieve multiple differently tagged sentences per port) """
    results = []
    found_tags = []
    for i_try_to_get_a_good_read in range(0, 50):
        at_most_certain_size_of_bytes_read: bytes = await aioserial_instance.read_until_async(aioserial.LF, None)
        if at_most_certain_size_of_bytes_read:
            at_most_certain_size_of_bytes_read = at_most_certain_size_of_bytes_read.decode(encoding='utf-8')
            for tag in tags:
                if at_most_certain_size_of_bytes_read.startswith(tag):
                    if tag not in found_tags:
                        found_tags.append(tag)
                        if at_most_certain_size_of_bytes_read not in results:
                            results.append(at_most_certain_size_of_bytes_read)
    return results


async def power_com_entrypoint(chunks: list, **kwargs) -> list:
    """ pass a bag of tags to each instance of power_com """
    tags = kwargs.get('tags')
    # print('chunks:', chunks)
    try:
        return [await power_com(aioserial.AioSerial(port=item, baudrate=115200, timeout=1), tags=tags) for item in chunks]  # todo
    except Exception as e:  # handle me!
        pass


async def main(_chunks: list, _multiproc_dict: dict):
    """ create multiple processes in range of com ports """
    async with aiomultiprocess.Pool(processes=20, maxtasksperchild=-1, childconcurrency=-1, queuecount=-1) as pool:
        results = await pool.map(power_com_entrypoint, _chunks, _multiproc_dict)
    return results

if __name__ == '__main__':

    # used for compile time
    if sys.platform.startswith('win'):
        multiprocessing.freeze_support()

    # initial data (ideally passed in through somewhere)
    _com_min = 1
    _com_max = 20
    _tags = ['$SATCOM', '$GNGGA', '$SNS']
    _multiproc_dict = {'tags': _tags}

    # create simple data
    t0 = time.time()
    coms = []
    for i in range(_com_min, _com_max):
        coms.append('COM' + str(i))

    # chunk simple data
    _chunks = handler_chunk.chunk_data(data=coms, chunk_size=1)

    # let it rip!
    print('\nrunning processes:')
    _t_start = time.perf_counter()
    _results = asyncio.run(main(_chunks, _multiproc_dict))
    _t_completion = str(time.perf_counter() - _t_start)
    print('aiomultiprocess time taken:', _t_completion)

    # some post-processing
    print('\nresults:')
    _results[:] = [item for item in _results if item is not None]
    _results[:] = [item for sublist in _results for item in sublist if item is not None]
    for _ in _results:
        print(_results)
