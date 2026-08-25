import struct

"""

Para enviar los ficheros, los protocolos van a usar frames de las siguientes
características:
- Un campo booleano "is_last" de 8 bits en el header indica que no quedan más
  datos por transmitir
- Los datos se envían en chunks de un tamaño máximo (por defecto, 256 bytes)
- Un campo entero "length" de 16 bits indica la longitud en bytes de los datos
  contenidos en el frame
- Si la longitud de los datos es menor al máximo permitido, el protocolo agrega
  bytes nulos a la derecha como relleno. Esto hace que se pierda eficiencia del
  frame, pero permite tener frames de largo fijo. De esta forma la
  implementación del protocolo queda menos complicada.
- Algunos protocolos extienden el header agregándole campos extra, y crean un
  frame con otro formato para representar un acknowledgement

El formato del header básico representado en bits es el siguiente:

 0                   1                   2
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|    is_last    |             length            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

Veamos un ejemplo. Si el tamaño máximo de un chunk fuera de 5 bytes y
quisiéramos enviar el mensaje "hola mundo!!!" tendríamos que separarlo en tres
frames diferentes de longitud fija 64 bits con los siguientes contenidos:

 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  is_last=0    |        length=5               |      h        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       o       |       l       |       a       |   (espacio)   |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  is_last=0    |        length=5               |      m        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       u       |       n       |       d       |      o        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  is_last=1    |        length=3               |      !        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       !       |       !       |0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0|
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

"""

CHUNK_SIZE = 256

def pad_to_chunk_size(data):
    """Cuando un chunk no tiene longitud máxima, le agrega bytes nulos al
    final. El campo length de los paquetes se encarga de ignorar estos
    bytes nulos al momento de decodificar los datos del frame."""
    return data.ljust(CHUNK_SIZE, b'\x00')

# El protocolo dumb solamente envía frames de datos en una única dirección,
# usando el formato de header básico

DUMB_DATA_HEADER_SIZE = 3
DUMB_DATA_FRAME_SIZE = DUMB_DATA_HEADER_SIZE + CHUNK_SIZE

def encode_dumb_data_frame(is_last, data):
    return struct.pack('!bh', bool(is_last), len(data)) + pad_to_chunk_size(data)

def decode_dumb_data_frame(frame):
    (is_last, length) = struct.unpack('!bh', frame[:DUMB_DATA_HEADER_SIZE])
    assert is_last in (0, 1)
    padded_data = frame[DUMB_DATA_HEADER_SIZE:]
    data = padded_data[:length]
    return bool(is_last), data

# Stop and wait usa (por ahora) frames con el formato de header básico.
# Para el acknowledge manda un único frame de 8 bits, cuyo contenido es
# indiferente

STOPANDWAIT_DATA_HEADER_SIZE = 3
STOPANDWAIT_DATA_FRAME_SIZE = STOPANDWAIT_DATA_HEADER_SIZE + CHUNK_SIZE
STOPANDWAIT_ACK_FRAME_SIZE = 1

def encode_stopandwait_data_frame(is_last, data):
    return struct.pack('!bh', bool(is_last), len(data)) + pad_to_chunk_size(data)

def decode_stopandwait_data_frame(frame):
    (is_last, length) = struct.unpack('!bh', frame[:STOPANDWAIT_DATA_HEADER_SIZE])
    assert is_last in (0, 1)
    padded_data = frame[STOPANDWAIT_DATA_HEADER_SIZE:]
    data = padded_data[:length]
    return bool(is_last), data

def encode_stopandwait_ack_frame():
    return b'x'

def decode_stopandwait_ack_frame(frame):
    # No es necesario decodificarlo (por ahora)
    raise NotImplementedError()

# Sliding window extiende el formato de frame básico. Agrega un entero de 32
# bits indicando el número de secuencia del frame transmitido.
# El receptor del fichero responde con enteros de 32 bits representando el
# número de secuencia al que se le quiere hacer acknowledge

SLIDINGWINDOW_DATA_HEADER_SIZE = 3 + 4
SLIDINGWINDOW_DATA_FRAME_SIZE = SLIDINGWINDOW_DATA_HEADER_SIZE + CHUNK_SIZE
SLIDINGWINDOW_ACK_FRAME_SIZE = 4

def encode_slidingwindow_data_frame(is_last, sequence_number, data):
    return struct.pack('!bhl', bool(is_last), len(data), sequence_number) + pad_to_chunk_size(data)

def decode_slidingwindow_data_frame(frame):
    (is_last, length, sequence_number) = struct.unpack('!bhl', frame[:SLIDINGWINDOW_DATA_HEADER_SIZE])
    assert is_last in (0, 1)
    padded_data = frame[SLIDINGWINDOW_DATA_HEADER_SIZE:]
    data = padded_data[:length]
    return bool(is_last), sequence_number, data

def encode_slidingwindow_ack_frame(sequence_number):
    return struct.pack('!l', sequence_number)

def decode_slidingwindow_ack_frame(frame):
    return struct.unpack('!l', frame)

def split_file_in_chunks(filepath):
    chunks = []
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            chunks.append(chunk)
    return chunks
