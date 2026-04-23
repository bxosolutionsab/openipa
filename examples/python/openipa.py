#!/usr/bin/env python3
"""Minimal OpenIPA framing and parsing helpers."""

from __future__ import annotations

from dataclasses import dataclass
import socket
from typing import Dict, Optional
import xml.etree.ElementTree as ET

REQUEST_LINE = "PUT / IPA/1.0"
DEFAULT_TIMEOUT_SECONDS = 8.0
RESULT_TEXT = {
    200: "OK",
    202: "Accepted",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    500: "Internal Server Error",
    503: "Service Unavailable",
}


@dataclass
class OpenIPAMessage:
    headers: Dict[str, str]
    payload_bytes: bytes
    xml_text: str
    xml_root: ET.Element


def build_frame(xml_text: str) -> bytes:
    payload = xml_text.encode("utf-8")
    header = (
        f"{REQUEST_LINE}\r\n"
        f"Content-Length: {len(payload)}\r\n"
        "\r\n"
    )
    return header.encode("ascii") + payload


def build_ack(message_id: str, result: int = 200, text: Optional[str] = None) -> str:
    if text is None:
        text = RESULT_TEXT.get(result, "")
    ack = ET.Element("Ack", {"Id": str(message_id), "Result": str(result)})
    ack.text = text
    return ET.tostring(ack, encoding="unicode")


def recv_framed_message(sock: socket.socket) -> OpenIPAMessage:
    header_bytes = _recv_until_header_end(sock)
    header_text = header_bytes.decode("ascii")
    lines = header_text.replace("\r\n", "\n").split("\n")

    if not lines or lines[0] != REQUEST_LINE:
        raise ValueError(f"unexpected request line: {lines[0] if lines else '<missing>'}")

    headers: Dict[str, str] = {}
    for line in lines[1:]:
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"malformed header line: {line}")
        name, value = line.split(":", 1)
        headers[name.strip()] = value.strip()

    if "Content-Length" not in headers:
        raise ValueError("missing Content-Length header")

    content_length = int(headers["Content-Length"])
    payload = _recv_exact(sock, content_length)
    xml_text = payload.decode("utf-8")
    xml_root = ET.fromstring(xml_text)
    return OpenIPAMessage(headers=headers, payload_bytes=payload, xml_text=xml_text, xml_root=xml_root)


def send_xml_message(sock: socket.socket, xml_text: str) -> None:
    sock.sendall(build_frame(xml_text))


def request_ack(sock: socket.socket, xml_text: str, timeout: float = DEFAULT_TIMEOUT_SECONDS) -> OpenIPAMessage:
    previous_timeout = sock.gettimeout()
    try:
        sock.settimeout(timeout)
        send_xml_message(sock, xml_text)
        return recv_framed_message(sock)
    finally:
        sock.settimeout(previous_timeout)


def _recv_until_header_end(sock: socket.socket) -> bytes:
    buffer = bytearray()
    while True:
        chunk = sock.recv(1)
        if not chunk:
            raise ConnectionError("connection closed while reading headers")
        buffer.extend(chunk)
        if buffer.endswith(b"\r\n\r\n") or buffer.endswith(b"\n\n"):
            return bytes(buffer)


def _recv_exact(sock: socket.socket, size: int) -> bytes:
    buffer = bytearray()
    while len(buffer) < size:
        chunk = sock.recv(size - len(buffer))
        if not chunk:
            raise ConnectionError("connection closed while reading payload")
        buffer.extend(chunk)
    return bytes(buffer)
