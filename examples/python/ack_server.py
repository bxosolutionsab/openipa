#!/usr/bin/env python3
"""Receive OpenIPA messages and return Ack when Id is present."""

from __future__ import annotations

import argparse
import socket

from openipa import build_ack, recv_framed_message, send_xml_message


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=5000, type=int)
    args = parser.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((args.host, args.port))
        server.listen()
        print(f"listening on {args.host}:{args.port}")

        while True:
            conn, addr = server.accept()
            with conn:
                print(f"connection from {addr[0]}:{addr[1]}")
                try:
                    message = recv_framed_message(conn)
                    print("received:")
                    print(message.xml_text)

                    message_id = message.xml_root.attrib.get("Id")
                    if message_id:
                        ack_xml = build_ack(message_id, 200)
                        send_xml_message(conn, ack_xml)
                        print("sent ack:")
                        print(ack_xml)
                except Exception as exc:  # noqa: BLE001
                    print(f"error: {exc}")


if __name__ == "__main__":
    main()
