#!/usr/bin/env python3
"""Send an OpenIPA TextMessage and optionally wait for Ack."""

from __future__ import annotations

import argparse
import socket
import xml.etree.ElementTree as ET

from openipa import request_ack, send_xml_message


def build_text_message(message: str, to: str | None, from_: str | None, message_id: str | None) -> str:
    attrs = {}
    if message_id:
        attrs["Id"] = message_id
    if to:
        attrs["To"] = to
    if from_:
        attrs["From"] = from_

    root = ET.Element("TextMessage", attrs)
    root.text = message
    return ET.tostring(root, encoding="unicode")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", required=True, type=int)
    parser.add_argument("--to")
    parser.add_argument("--from", dest="from_")
    parser.add_argument("--id")
    parser.add_argument("--message", required=True)
    args = parser.parse_args()

    xml_text = build_text_message(args.message, args.to, args.from_, args.id)

    with socket.create_connection((args.host, args.port), timeout=8) as sock:
        if args.id:
            ack = request_ack(sock, xml_text)
            print("sent:")
            print(xml_text)
            print()
            print("ack:")
            print(ack.xml_text)
        else:
            send_xml_message(sock, xml_text)
            print("sent:")
            print(xml_text)


if __name__ == "__main__":
    main()
