# OpenIPA 1.0 Draft Specification

## 1. Status

This document specifies the current OpenIPA protocol draft using the content
published on `ipa.bxo.se` as its source. It organizes that material into a
single implementation-oriented specification.

This document does not define protocol behavior that is absent from the
published site. Where the source material is incomplete, this specification
marks the relevant behavior as unspecified.

## 2. Scope

OpenIPA is an IP-native protocol for alarm management and message delivery. It
is intended as a modern replacement for ESPA 4.4.4 while remaining practical to
implement in straightforward integrations.

This draft specifies:

- TCP-based framing
- XML message encoding
- The `Ack`, `Heartbeat`, `TextMessage`, and `Alarm` message families
- Timing constants
- Application result codes
- Published security notes

## 3. Terminology

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this
document are to be interpreted as normative requirements.

Sender:
A peer that transmits an OpenIPA-framed XML message.

Receiver:
A peer that accepts an OpenIPA-framed XML message.

Acknowledgement-requesting message:
A message that carries an `Id` attribute.

## 4. Transport

### 4.1 Transport binding

OpenIPA messages are carried over a TCP byte stream.

The protocol uses a framing format that resembles a minimal HTTP request, but
OpenIPA communication is asynchronous. A peer MUST NOT assume a strict
request-response pattern beyond the acknowledgement rules defined in this
document.

### 4.2 Frame format

Each message frame MUST contain:

1. A request line exactly equal to `PUT / IPA/1.0`
2. A `Content-Length` header
3. An empty line
4. An XML payload

The line separator on the wire SHOULD be CRLF (`\r\n`). Implementations MAY
accept LF-only framing when interoperating with peers that emit it, because the
published examples use LF-only formatting.

The `Content-Length` value MUST be the number of payload octets after UTF-8
encoding.

Example:

```text
PUT / IPA/1.0
Content-Length: 56

<TextMessage To="123456">Text to display</TextMessage>
```

The numeric value in examples is illustrative. Implementations MUST calculate
the byte length from the encoded payload.

### 4.3 Additional headers

`Content-Length` is mandatory.

Additional header fields MAY be included. Receivers MUST ignore unrecognized
header fields unless a future OpenIPA revision defines otherwise.

## 5. Encoding

The XML payload MUST be encoded as UTF-8.

Pure 7-bit ASCII is valid because it is a UTF-8-compatible subset.

## 6. Message model

### 6.1 Supported message families

This draft defines four top-level XML message elements:

- `Ack`
- `Heartbeat`
- `TextMessage`
- `Alarm`

Each frame MUST contain exactly one top-level message element.

### 6.2 Common acknowledgement trigger

If a message contains an `Id` attribute, the sender is requesting an
acknowledgement.

When a receiver accepts such a message, it SHOULD return an `Ack` message that:

- copies the same `Id`
- includes a `Result` code
- is sent within `T ACK`

### 6.3 Unsupported message types

Behavior for unknown top-level message elements is not fully described in the
published draft. A receiver SHOULD reject an unknown message with `Ack
Result="400"` when the incoming message included an `Id`.

## 7. Acknowledgements

### 7.1 Ack message

`Ack` acknowledges a previously received message.

Attributes:

- `Id` (required): the `Id` from the original message
- `Result` (required): the application result code

Element content:

- Optional plain text explanation, such as `OK` or `Not found`

Example:

```xml
<Ack Id="100" Result="200">OK</Ack>
```

### 7.2 Ack timing

If an acknowledgement is requested, the receiver SHOULD respond within `T ACK`,
whose maximum published value is 8 seconds.

### 7.3 Ack meaning

The published draft uses application result codes inspired by HTTP status
codes, but these codes are part of OpenIPA and MUST NOT be interpreted as HTTP
response semantics.

## 8. Heartbeat

`Heartbeat` is used for connection monitoring. Either side MAY send it.

Attributes:

- `Id` (optional): requests an acknowledgement when present
- `ClientId` (optional): identifies the client in multi-client deployments
- `Authentication` (optional): carries authentication data in the current draft

Examples:

```xml
<Heartbeat />
```

```xml
<Heartbeat Id="123" />
```

```xml
<Heartbeat Id="103" ClientId="012345" />
```

```xml
<Heartbeat Id="103" Authentication="dz80mi0pql+js9028jm8c89jv8" />
```

The format and verification procedure for `Authentication` are unspecified in
the published draft.

## 9. TextMessage

`TextMessage` requests delivery of a plain text message.

Attributes:

- `Id` (optional): requests an acknowledgement when present
- `To` (optional): recipient number or address
- `From` (optional): sender number or address

Element content:

- The text to deliver

Example:

```xml
<TextMessage To="123456">Text to display</TextMessage>
```

Multiline content is allowed:

```xml
<TextMessage To="someone@somewhere.com">Hello,
This is a text message.</TextMessage>
```

The exact character limits, delivery guarantees, and destination addressing
rules are unspecified in the published draft.

## 10. Alarm

`Alarm` carries alarm or event data.

Attributes:

- `Id` (optional): requests an acknowledgement when present

Child elements:

- `Source` (required)
- `Type` (required)
- `Location` (optional)

### 10.1 Source

`Source` identifies where the alarm originates.

The published draft allows two encodings:

- direct text content
- a structured set of child elements

Known structured child elements:

- `Client`
- `Department`
- `Building`
- `Ward`
- `Section`
- `Room`
- `Detector`
- `Transmitter`
- `Phone`
- `Address`

Examples:

```xml
<Source>219</Source>
```

```xml
<Source>
    <Client>10026</Client>
    <Building>B</Building>
    <Ward>2</Ward>
    <Room>219</Room>
</Source>
```

### 10.2 Type

`Type` identifies the alarm type through its text content.

Attributes:

- `Qualifier` (optional): examples include `New`, `Updated`, and `Reset`
- `Severity` (optional): integer from 0 to 100, where 100 is most severe

Example:

```xml
<Type Qualifier="New" Severity="100">FIRE</Type>
```

### 10.3 Location

`Location` is optional and may describe alarm position through one of the
published location forms:

- `CellInfo`
- `BeaconId`
- `Gps`

#### 10.3.1 CellInfo

Known child elements:

- `MCC` (required): mobile country code, 3 digits
- `MNC` (required): mobile network code
- `LAC` (required): location area code in decimal
- `CI` (required): cell identifier in decimal
- `TA` (optional): timing advance

Example:

```xml
<Location>
    <CellInfo>
        <MCC>240</MCC>
        <MNC>10</MNC>
        <LAC>57005</LAC>
        <CI>48879</CI>
    </CellInfo>
</Location>
```

#### 10.3.2 BeaconId

Example:

```xml
<Location><BeaconId>100</BeaconId></Location>
```

#### 10.3.3 Gps

Known child elements:

- `Longitude`
- `Latitude`
- `Altitude`
- `Direction`
- `Speed`
- `TimeStamp`
- `HorizontalAccuracy`
- `VerticalAccuracy`
- `DirectionAccuracy`
- `SpeedAccuracy`

The site describes only `Longitude`, `Latitude`, and `Altitude` in detail. The
remaining fields are published but otherwise unspecified.

Example:

```xml
<Location>
    <Gps>
        <Longitude>17.87930</Longitude>
        <Latitude>59.41310</Latitude>
        <Altitude>57</Altitude>
    </Gps>
</Location>
```

### 10.4 Alarm examples

Simple:

```xml
<Alarm><Source>209</Source><Type>FIRE</Type></Alarm>
```

Detailed:

```xml
<Alarm Id="101">
    <Source>
        <Section>5</Section>
        <Room>50</Room>
    </Source>
    <Type Qualifier="New" Severity="100">FIRE</Type>
    <Location>
        <Gps>
            <Longitude>17.87930</Longitude>
            <Latitude>59.41310</Latitude>
            <Altitude>57</Altitude>
        </Gps>
    </Location>
</Alarm>
```

## 11. Result codes

OpenIPA `Ack` messages use the following published result codes:

| Code | Default text | Meaning |
| --- | --- | --- |
| `200` | `OK` | Message was accepted or delivered and acknowledged by the final destination. |
| `202` | `Accepted` | Message was accepted and queued, but not yet delivered. |
| `400` | `Bad Request` | The datagram was malformed. |
| `401` | `Unauthorized` | Identification or authorization is required. |
| `403` | `Forbidden` | The client lacks sufficient privileges for the requested action. |
| `404` | `Not Found` | The destination was not found. |
| `500` | `Internal Server Error` | The server failed while handling the message. |
| `503` | `Service Unavailable` | The server or an external dependency is temporarily unavailable. |

Receivers MAY include a short explanatory text body in the `Ack`.

## 12. Timing constants

The published draft defines the following timing constants:

| Symbol | Description | Min | Max |
| --- | --- | --- | --- |
| `T ACK` | Time between a message and its acknowledgement | - | 8 s |
| `T HB` | Heartbeat interval | 10 s | - |
| `T MHB` | Delay after a missed heartbeat before trying a new connection | 10 s | 60 s |
| `T ALIVE` | Maximum idle time before a connection is considered stale | 120 s | 600 s |

The site does not define retry counts, backoff strategy, or connection ownership
rules beyond these values.

## 13. Security considerations

The published material does not define a full mandatory security profile. It
does, however, describe three security-related concerns:

### 13.1 Identification

When multiple clients connect to one server, the client MAY need to identify
itself, for example through `ClientId` on `Heartbeat`.

### 13.2 Authentication

The draft sketches authentication as message-carried data, for example through
the `Authentication` attribute on `Heartbeat`.

The encoding, algorithm, secret handling, and replay protections are
unspecified.

### 13.3 Encryption

The published material states that authentication is of limited value without
transport encryption and recommends TLS for the TCP connection.

Implementations SHOULD use TLS in production deployments.

## 14. Error handling

When a received frame is malformed, a receiver SHOULD:

- reject the message locally
- close the connection if the framing can no longer be trusted
- return `Ack Result="400"` only when a valid message `Id` can still be
  determined safely

The published site does not define a richer error recovery model.

## 15. XML schema

The XML schema in `schemas/openipa-1.0.xsd` captures the currently published
message set and field names.

Because the source material is still a draft, the schema favors interoperability
with the published examples over aggressive restriction of underspecified
fields.

## 16. Implementation guidance

Implementations should take particular care with:

- computing `Content-Length` from UTF-8 bytes, not from characters
- treating `Id` as the acknowledgement trigger
- using the XML element names directly in logs and diagnostics
- keeping unsupported or unspecified fields tolerant unless stricter behavior is
  agreed in a future revision
