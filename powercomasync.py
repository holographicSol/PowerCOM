"""
COM Scan. A COM port scanner (soon to be asynchronous and multi-processed) Written by Benjamin Jack Cullen

I need to read data from COM ports with as little configuration as possible for reusability across other projects and
so to avoid hardcoded COM ports, baud rates.

Early stages. This can still be faster.

"""

import sys
import serial
import asyncio
import aioserial
import multiprocessing
import aiomultiprocess
import handler_chunk
import time

baud_rates = [
    115200
]


async def read_and_print(aioserial_instance: aioserial.AioSerial, tags: list):
    results = []
    found_tags = []
    for i in range(0, 10):
        at_most_certain_size_of_bytes_read: bytes = await aioserial_instance.read_until_async(aioserial.LF, None)
        if at_most_certain_size_of_bytes_read:
            at_most_certain_size_of_bytes_read = at_most_certain_size_of_bytes_read.decode(encoding='utf-8')
            for tag in tags:
                if at_most_certain_size_of_bytes_read.startswith(tag):
                    if tag not in found_tags:
                        found_tags.append(tag)
                        if at_most_certain_size_of_bytes_read not in results:
                            results.append(at_most_certain_size_of_bytes_read)
    if results:
        return results


async def power_com(item: str, **kwargs):
    # print('\nscanning comport:', item, '(for tags:', kwargs.values(), ')')
    results = []
    tags = kwargs.get('tags')
    try:
        results = await read_and_print(aioserial.AioSerial(port=item, baudrate=115200), tags=tags)
    except Exception as e:
        pass
    if results:
        return results


async def power_scan_entry_point(chunks: list, **kwargs) -> list:
    return [await power_com(item, **kwargs) for item in chunks]


async def main(_chunks: list, _multiproc_dict: dict):
    async with aiomultiprocess.Pool() as pool:
        results = await pool.map(power_scan_entry_point, _chunks, _multiproc_dict)
    return results

if __name__ == '__main__':

    # used for compile time
    if sys.platform.startswith('win'):
        multiprocessing.freeze_support()

    # chunk data
    t0 = time.time()
    coms = []
    for i in range(1, 255):
        coms.append('COM' + str(i))
    _chunks = handler_chunk.chunk_data(data=coms, chunk_size=1)
    print('\nchunks:', _chunks)
    print('chunk time:', time.time()-t0)

    _tags = ['$SATCOM', '$GNGGA', '$SNS']
    _multiproc_dict = {'tags': _tags}

    print('\nrunning processes:')
    _t_start = time.perf_counter()
    _results = asyncio.run(main(_chunks, _multiproc_dict))
    _t_completion = str(time.perf_counter() - _t_start)
    print('aiomultiprocess time taken:', _t_completion)

    print('\nresults:')
    _results[:] = [item for sublist in _results for item in sublist if item is not None]
    for _ in _results:
        print(_results)
