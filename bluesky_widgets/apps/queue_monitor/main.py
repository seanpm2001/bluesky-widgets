import argparse
import os

from bluesky_widgets.qt import gui_qt

from .viewer import Viewer
from .settings import SETTINGS


def main(argv=None):
    parser = argparse.ArgumentParser(description="BlueSky Queue Monitor")
    parser.add_argument(
        "--zmq-control-addr",
        default=None,
        help="Address of control socket of RE Manager. If the address "
        "is passed as a CLI parameter, it overrides the address specified with "
        "QSERVER_ZMQ_CONTROL_ADDRESS environment variable. Default address is "
        "used if the parameter or the environment variable are not specified.",
    )
    parser.add_argument(
        "--zmq-control",
        default=None,
        help="The parameter is deprecated and will be removed. Use --zmq-control-addr instead.",
    )
    parser.add_argument(
        "--zmq-info-addr",
        default=None,
        help="Address of PUB-SUB socket of RE Manager. If the address "
        "is passed as a CLI parameter, it overrides the address specified with "
        "QSERVER_ZMQ_INFO_ADDRESS environment variable. Default address is "
        "used if the parameter or the environment variable are not specified.",
    )
    parser.add_argument(
        "--zmq-publish",
        default=None,
        help="The parameter is deprecated and will be removed. Use --zmq-info-addr instead.",
    )
    args = parser.parse_args(argv)

    # The priority is first to check if an address is passed as a parameter and then
    #   check if the environment variables are set. Otherwise use the default local addresses.
    #   (The default addresses are typically used in demos.)
    zmq_control_addr = args.zmq_control_addr
    zmq_control_addr = zmq_control_addr or args.zmq_control
    if args.zmq_control is not None:
        print("The parameter --zmq-control is deprecated and will be removed. Use --zmq-control-addr instead.")
    zmq_control_addr = zmq_control_addr or os.environ.get("QSERVER_ZMQ_CONTROL_ADDRESS", None)

    zmq_info_addr = args.zmq_info_addr
    if args.zmq_publish is not None:
        print("The parameter --zmq-publish is deprecated and will be removed. Use --zmq-info-addr instead.")
    zmq_info_addr = zmq_info_addr or args.zmq_publish
    zmq_info_addr = zmq_info_addr or os.environ.get("QSERVER_ZMQ_INFO_ADDRESS", None)
    if "QSERVER_ZMQ_PUBLISH_ADDRESS" in os.environ:
        print("WARNING: Environment variable QSERVER_ZMQ_PUBLISH_ADDRESS is deprecated and will be removed.")
        print("    Use QSERVER_ZMQ_INFO_ADDRESS environment variable instead.")
    zmq_info_addr = zmq_info_addr or os.environ.get("QSERVER_ZMQ_PUBLISH_ADDRESS", None)
    SETTINGS.zmq_re_manager_control_addr = zmq_control_addr
    SETTINGS.zmq_re_manager_info_addr = zmq_info_addr

    with gui_qt("BlueSky Queue Monitor"):
        viewer = Viewer()  # noqa: 401


if __name__ == "__main__":
    main()