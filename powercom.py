"""
COM Scan. A COM port scanner (soon to be asynchronous and multi-processed) Written by Benjamin Jack Cullen

I need to read data from COM ports with as little configuration as possible for reusability across other projects and
so to avoid hardcoded COM ports, baud rates.

Early stages. This working solution will have to be asynchronous and multi-processed for performance reasons.

"""

import os
import serial

baud_rates = [
    115200
]
matrix = []


def load_matrix(file: str) -> bool:
    """ load configuration data. {'tag': '$a_tag', 'descriptor': 'element', etc} """
    global matrix
    if os.path.exists(file):
        matrix_str = ''
        with open(file, 'r') as fo:
            for line in fo:
                line = line.strip()
                if not line.startswith('#'):
                    matrix_str = matrix_str + line
        fo.close()
        if matrix_str:
            matrix = eval(f"[{matrix_str}]")
            return True


def power_com(tags: list) -> list:
    """ requires zero configuration, we just need a known tag. should be async. """
    data = []
    has_data = []

    # iterate through tags
    for tag in tags:

        # iterate through com
        for i_com in range(0, 256):

            # iterate through baud rates
            for baud_rate in baud_rates:

                try:
                    print('scanning:', 'tag:', tag, 'COM'+str(i_com), ' with baud rate', baud_rate)
                    connection = serial.Serial('COM'+str(i_com), baud_rate)

                    # try to get a good read
                    for i_listen in range(0, 50):
                        incoming_data = connection.readline()
                        if incoming_data:
                            try:
                                tmp_data = incoming_data.decode('utf-8').strip()
                                if tmp_data.startswith(tag) and tag not in has_data:

                                    # add checksum validation
                                    has_data.append(tag)
                                    data.append(tmp_data)

                                    # stop scanning current port
                                    break

                            except Exception as e:  # handle me
                                pass
                except Exception as e:  # handle me
                    pass
    if data:
        return data


# example module use (tags will be loaded from matrix but are currently hardcoded)
results = power_com(tags=['$SATCOM', '$GNGGA', '$SNS'])
if results:
    for _ in results:
        print(_)
