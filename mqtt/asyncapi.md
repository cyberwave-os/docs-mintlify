# Cyberwave MQTT API 1.0.0 documentation

* Specification ID: `urn:com:cyberwave:mqtt:api`
* License: [Proprietary](https://cyberwave.com/license)
* Default content type: [application/json](https://www.iana.org/assignments/media-types/application/json)
* Support: [Cyberwave API Support](https://cyberwave.com/support)
* Email support: [support@cyberwave.com](mailto:support@cyberwave.com)

MQTT API for Cyberwave platform
##### Specification tags

| Name | Description | Documentation |
|---|---|---|
| articulation | Articulation related operations | - |
| health | Health related operations | - |
| joint | Joint related operations | - |
| monitoring | Monitoring related operations | - |
| position | Position related operations | - |
| robot | Robot related operations | - |
| rotation | Rotation related operations | - |
| scale | Scale related operations | - |
| streaming | Streaming related operations | - |
| transform | Transform related operations | - |
| twin | Twin related operations | - |
| video | Video related operations | - |
| webrtc | Webrtc related operations | - |


## Table of Contents

* [Servers](#servers)
  * [production](#production-server)
* [Operations](#operations)
  * [SUB cyberwave.twin.{twin_uuid}.webrtc-offer](#sub-cyberwavetwintwin_uuidwebrtc-offer-operation)
  * [SUB cyberwave.joint.{asset_uuid}.update](#sub-cyberwavejointasset_uuidupdate-operation)
  * [SUB cyberwave.ping.{resource_uuid}.request](#sub-cyberwavepingresource_uuidrequest-operation)
  * [PUB cyberwave.pong.{resource_uuid}.response](#pub-cyberwavepongresource_uuidresponse-operation)
  * [SUB cyberwave.twin.{twin_uuid}.position](#sub-cyberwavetwintwin_uuidposition-operation)
  * [SUB cyberwave.twin.{twin_uuid}.rotation](#sub-cyberwavetwintwin_uuidrotation-operation)
  * [SUB cyberwave.twin.{twin_uuid}.scale](#sub-cyberwavetwintwin_uuidscale-operation)

## Servers

### `production` Server

* URL: `mqtt://host.docker.internal:1883`
* Protocol: `mqtt`

Production MQTT broker


## Operations

### SUB `cyberwave.twin.{twin_uuid}.webrtc-offer` Operation

* Operation ID: `subscribe_cyberwave_twin_twin_uuid_webrtc-offer`

Processes WebRTC SDP offers from edge devices or frontend clients to establish real-time video streaming connections

#### Parameters

| Name | Type | Description | Value | Constraints | Notes |
|---|---|---|---|---|---|
| twin_uuid | string | The twin uuid | - | - | **required** |


#### Message Handle WebRTC Offer `Handle WebRTC Offer`

*Processes WebRTC SDP offers from edge devices or frontend clients to establish real-time video streaming connections*

* Message ID: `cyberwave_twin_twin_uuid_webrtc-offer_subscribe_message`
* Content type: [application/json](https://www.iana.org/assignments/media-types/application/json)

##### Payload

| Name | Type | Description | Value | Constraints | Notes |
|---|---|---|---|---|---|
| (root) | object | Payload for WebRTC offer messages. | examples (`{"sdp":"v=0...","sender":"edge","target":"backend","timestamp":1700000000,"type":"offer"}`) | - | **additional properties are allowed** |
| type | string | Message type | default (`"offer"`), const (`"offer"`) | - | - |
| sdp | string | Session Description Protocol offer | - | - | **required** |
| target | string | Target of the WebRTC connection | allowed (`"backend"`, `"frontend"`, `"edge"`) | - | **required** |
| sender | string | Sender of the WebRTC offer | allowed (`"backend"`, `"frontend"`, `"edge"`) | - | **required** |
| frontend_type | string | Type of frontend stream (rgb, depth, etc.) | - | - | - |
| color_track_id | string | ID of the color/RGB track | - | - | - |
| depth_track_id | string | ID of the depth track | - | - | - |
| timestamp | number | Unix timestamp | - | - | **required** |

> Examples of payload

```json
{
  "sdp": "v=0...",
  "sender": "edge",
  "target": "backend",
  "timestamp": 1700000000,
  "type": "offer"
}
```


##### Message tags

| Name | Description | Documentation |
|---|---|---|
| webrtc | - | - |
| video | - | - |
| streaming | - | - |


### SUB `cyberwave.joint.{asset_uuid}.update` Operation

* Operation ID: `subscribe_cyberwave_joint_asset_uuid_update`

Updates the state (position, velocity, effort) of a robot joint

#### Parameters

| Name | Type | Description | Value | Constraints | Notes |
|---|---|---|---|---|---|
| asset_uuid | string | The asset uuid | - | - | **required** |


#### Message Update Joint State `Update Joint State`

*Updates the state (position, velocity, effort) of a robot joint*

* Message ID: `cyberwave_joint_asset_uuid_update_subscribe_message`
* Content type: [application/json](https://www.iana.org/assignments/media-types/application/json)

##### Payload

| Name | Type | Description | Value | Constraints | Notes |
|---|---|---|---|---|---|
| (root) | object | Payload for joint state updates. | examples (`{"joint_name":"shoulder_pan_joint","joint_state":{"effort":0,"position":1.57,"velocity":0},"timestamp":1700000000}`) | - | **additional properties are allowed** |
| joint_name | string | Name of the joint being updated | - | - | **required** |
| joint_state | object | State of a single joint. | - | - | **required**, **additional properties are allowed** |
| joint_state.position | number | Joint position in radians or meters | - | - | - |
| joint_state.velocity | number | Joint velocity | - | - | - |
| joint_state.effort | number | Joint effort/torque | - | - | - |
| timestamp | number | Unix timestamp | - | - | - |

> Examples of payload

```json
{
  "joint_name": "shoulder_pan_joint",
  "joint_state": {
    "effort": 0,
    "position": 1.57,
    "velocity": 0
  },
  "timestamp": 1700000000
}
```


##### Message tags

| Name | Description | Documentation |
|---|---|---|
| joint | - | - |
| robot | - | - |
| articulation | - | - |


### SUB `cyberwave.ping.{resource_uuid}.request` Operation

* Operation ID: `subscribe_cyberwave_ping_resource_uuid_request`

Responds to health check ping messages with a pong response

#### Parameters

| Name | Type | Description | Value | Constraints | Notes |
|---|---|---|---|---|---|
| resource_uuid | string | The resource uuid | - | - | **required** |


#### Message Handle Ping Request `Handle Ping Request`

*Responds to health check ping messages with a pong response*

* Message ID: `cyberwave_ping_resource_uuid_request_subscribe_message`
* Content type: [application/json](https://www.iana.org/assignments/media-types/application/json)

##### Payload

| Name | Type | Description | Value | Constraints | Notes |
|---|---|---|---|---|---|
| (root) | object | Payload for ping health check messages. | examples (`{"timestamp":1700000000,"type":"ping"}`) | - | **additional properties are allowed** |
| type | string | Message type | default (`"ping"`), const (`"ping"`) | - | - |
| timestamp | number | Unix timestamp | - | - | **required** |

> Examples of payload

```json
{
  "timestamp": 1700000000,
  "type": "ping"
}
```


##### Message tags

| Name | Description | Documentation |
|---|---|---|
| health | - | - |
| monitoring | - | - |


### PUB `cyberwave.pong.{resource_uuid}.response` Operation

* Operation ID: `publish_cyberwave_pong_resource_uuid_response`

Sends a pong response to confirm system health

#### Parameters

| Name | Type | Description | Value | Constraints | Notes |
|---|---|---|---|---|---|
| resource_uuid | string | The resource uuid | - | - | **required** |


#### Message Send Pong Response `Send Pong Response`

*Sends a pong response to confirm system health*

* Message ID: `cyberwave_pong_resource_uuid_response_publish_message`
* Content type: [application/json](https://www.iana.org/assignments/media-types/application/json)

##### Payload

| Name | Type | Description | Value | Constraints | Notes |
|---|---|---|---|---|---|
| (root) | object | Payload for pong health check responses. | examples (`{"timestamp":1700000000,"type":"pong"}`) | - | **additional properties are allowed** |
| type | string | Message type | default (`"pong"`), const (`"pong"`) | - | - |
| timestamp | number | Unix timestamp | - | - | **required** |

> Examples of payload

```json
{
  "timestamp": 1700000000,
  "type": "pong"
}
```


##### Message tags

| Name | Description | Documentation |
|---|---|---|
| health | - | - |
| monitoring | - | - |


### SUB `cyberwave.twin.{twin_uuid}.position` Operation

* Operation ID: `subscribe_cyberwave_twin_twin_uuid_position`

Updates the 3D position coordinates of a digital twin in the environment

#### Parameters

| Name | Type | Description | Value | Constraints | Notes |
|---|---|---|---|---|---|
| twin_uuid | string | The twin uuid | - | - | **required** |


#### Message Update Twin Position `Update Twin Position`

*Updates the 3D position coordinates of a digital twin in the environment*

* Message ID: `cyberwave_twin_twin_uuid_position_subscribe_message`
* Content type: [application/json](https://www.iana.org/assignments/media-types/application/json)

##### Payload

| Name | Type | Description | Value | Constraints | Notes |
|---|---|---|---|---|---|
| (root) | object | Payload for updating twin position. | examples (`{"position":{"x":1,"y":2,"z":3},"timestamp":1700000000}`) | - | **additional properties are allowed** |
| position | object | 3D vector representation. | - | - | **required**, **additional properties are allowed** |
| position.x | number | X coordinate | - | - | **required** |
| position.y | number | Y coordinate | - | - | **required** |
| position.z | number | Z coordinate | - | - | **required** |
| timestamp | number | Unix timestamp of the update | - | - | - |

> Examples of payload

```json
{
  "position": {
    "x": 1,
    "y": 2,
    "z": 3
  },
  "timestamp": 1700000000
}
```


##### Message tags

| Name | Description | Documentation |
|---|---|---|
| twin | - | - |
| position | - | - |
| transform | - | - |


### SUB `cyberwave.twin.{twin_uuid}.rotation` Operation

* Operation ID: `subscribe_cyberwave_twin_twin_uuid_rotation`

Updates the rotation quaternion of a digital twin in the environment

#### Parameters

| Name | Type | Description | Value | Constraints | Notes |
|---|---|---|---|---|---|
| twin_uuid | string | The twin uuid | - | - | **required** |


#### Message Update Twin Rotation `Update Twin Rotation`

*Updates the rotation quaternion of a digital twin in the environment*

* Message ID: `cyberwave_twin_twin_uuid_rotation_subscribe_message`
* Content type: [application/json](https://www.iana.org/assignments/media-types/application/json)

##### Payload

| Name | Type | Description | Value | Constraints | Notes |
|---|---|---|---|---|---|
| (root) | object | Payload for updating twin rotation. | examples (`{"rotation":{"w":1,"x":0,"y":0,"z":0},"timestamp":1700000000}`) | - | **additional properties are allowed** |
| rotation | object | Quaternion representation for rotation. | - | - | **required**, **additional properties are allowed** |
| rotation.w | number | W component (real part) | default (`1`) | - | - |
| rotation.x | number | X component | - | - | - |
| rotation.y | number | Y component | - | - | - |
| rotation.z | number | Z component | - | - | - |
| timestamp | number | Unix timestamp of the update | - | - | - |

> Examples of payload

```json
{
  "rotation": {
    "w": 1,
    "x": 0,
    "y": 0,
    "z": 0
  },
  "timestamp": 1700000000
}
```


##### Message tags

| Name | Description | Documentation |
|---|---|---|
| twin | - | - |
| rotation | - | - |
| transform | - | - |


### SUB `cyberwave.twin.{twin_uuid}.scale` Operation

* Operation ID: `subscribe_cyberwave_twin_twin_uuid_scale`

Updates the 3D scale factors of a digital twin in the environment

#### Parameters

| Name | Type | Description | Value | Constraints | Notes |
|---|---|---|---|---|---|
| twin_uuid | string | The twin uuid | - | - | **required** |


#### Message Update Twin Scale `Update Twin Scale`

*Updates the 3D scale factors of a digital twin in the environment*

* Message ID: `cyberwave_twin_twin_uuid_scale_subscribe_message`
* Content type: [application/json](https://www.iana.org/assignments/media-types/application/json)

##### Payload

| Name | Type | Description | Value | Constraints | Notes |
|---|---|---|---|---|---|
| (root) | object | Payload for updating twin scale. | examples (`{"scale":{"x":1,"y":1,"z":1},"timestamp":1700000000}`) | - | **additional properties are allowed** |
| scale | object | 3D vector representation. | - | - | **required**, **additional properties are allowed** |
| scale.x | number | X coordinate | - | - | **required** |
| scale.y | number | Y coordinate | - | - | **required** |
| scale.z | number | Z coordinate | - | - | **required** |
| timestamp | number | Unix timestamp of the update | - | - | - |

> Examples of payload

```json
{
  "scale": {
    "x": 1,
    "y": 1,
    "z": 1
  },
  "timestamp": 1700000000
}
```


##### Message tags

| Name | Description | Documentation |
|---|---|---|
| twin | - | - |
| scale | - | - |
| transform | - | - |


