import tempfile
from suitcase.msgpack import Serializer
from bluesky import RunEngine
from bluesky.plans import count, scan
from ophyd.sim import img, det, motor

from databroker._drivers.msgpack import BlueskyMsgpackCatalog


def get_catalog():
    RE = RunEngine()

    directory = tempfile.TemporaryDirectory().name
    with Serializer(directory) as serializer:
        RE(scan([det], motor, -1, 1, 10), serializer)
    with Serializer(directory) as serializer:
        RE(scan([det], motor, -1, 1, 15), serializer)
    with Serializer(directory) as serializer:
        RE(count([img], 3), serializer)

    catalog = BlueskyMsgpackCatalog(f"{directory}/*.msgpack")
    return catalog