# OpenIPA

OpenIPA is an open, IP-native protocol for alarm management and message delivery.
This repository turns the currently published material from `ipa.bxo.se` into a
more formal protocol specification, an XML schema, and runnable example code.

The current source of truth for protocol behavior in this repository is:

- [SPECIFICATION.md](./SPECIFICATION.md)
- [schemas/openipa-1.0.xsd](./schemas/openipa-1.0.xsd)

The repository intentionally stays close to the published website draft. Where
the site is underspecified, this repository calls that out explicitly instead of
inventing protocol behavior.

## Repository layout

- `SPECIFICATION.md`: protocol specification for OpenIPA 1.0 draft
- `schemas/openipa-1.0.xsd`: XML schema for the published message set
- `examples/python/openipa.py`: framing, parsing, and acknowledgement helpers
- `examples/python/send_text_message.py`: sender example
- `examples/python/ack_server.py`: receiver example
- `examples/messages/`: example XML payloads

## Protocol summary

- Transport: TCP with a fixed `PUT / IPA/1.0` request line
- Framing: mandatory `Content-Length` header followed by an empty line and an XML payload
- Encoding: UTF-8, with pure 7-bit ASCII as a compatible subset
- Messages: `Ack`, `Heartbeat`, `TextMessage`, and `Alarm`
- Acknowledgements: if a message includes `Id`, the receiver is expected to reply with `Ack`

## Status

This repository documents the current published draft. It is suitable for
implementation work, discussion, and further refinement, but it should still be
treated as a draft protocol rather than a finished standard.

## Quick start

Start a simple acknowledgement server:

```bash
python3 examples/python/ack_server.py --host 127.0.0.1 --port 5000
```

Send a text message:

```bash
python3 examples/python/send_text_message.py \
  --host 127.0.0.1 \
  --port 5000 \
  --to 123456 \
  --message "Text to display" \
  --id 100
```

## Source material

The protocol text in this repository was built from the published website
content in `https://github.com/bxosolutionsab/ipa.bxo.se`.
