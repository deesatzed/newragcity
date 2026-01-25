(Files content cropped to 300k characters, download full ingest to see more)
================================================
FILE: website/docs/docs/connect.mdx
================================================
---
sidebar_position: 2
---

# Connect

<h2>How to connect to an API</h2>

You can connect to any API by defining their details inside the [`connect`](/docs/connect#connect-1) property. The target endpoint will need to be able to accept
and respond using the formats described below.

<a href="https://youtu.be/NuRhPeqDCus">
  <img src={YoutubeLogo} className={'youtube-icon'} />
  Video demo
</a>

<h3>Request message</h3>

The outgoing Deep Chat request body is encapsulated in one of the following formats:

- When sending **text** based messages only, the request body will have the following JSON type: <br />
  \{[`messages: MessageContent[]`](/docs/messages/#MessageContent)\} <br />

- When sending messages that contain **files**, the request body is going to be serialized inside a [FormData](https://developer.mozilla.org/en-US/docs/Web/API/FormData) type
  where files are set inside an array property called _"files"_ and each text message is stored inside a _"message\{index\}"_ property with a corresponding index: <br />
  \{`files: File[]`, [`message1: MessageContent`](/docs/messages/#MessageContent), [`message2: MessageContent`](/docs/messages/#MessageContent)... \} <br />

<h3>Response message</h3>

Response from the target server needs to use the [`Response`](#Response) JSON type.

:::tip
If you don't want / can't change the target server to handle the required object types, use the [`interceptor`](/docs/interceptors) properties
to augment the transferred objects or the [`handler`](#Handler) function to control the request code.
:::

<h2>Connection properties</h2>

import ComponentContainer from '@site/src/components/table/componentContainer';
import DeepChatBrowser from '@site/src/components/table/deepChatBrowser';
import LineBreak from '@site/src/components/markdown/lineBreak';
import WebSocket from '/img/update-websocket-message.gif';
import BrowserOnly from '@docusaurus/BrowserOnly';
import YoutubeLogo from '/img/youtube.png';
import TabItem from '@theme/TabItem';
import Tabs from '@theme/Tabs';

<BrowserOnly>{() => require('@site/src/components/nav/autoNavToggle').readdAutoNavShadowToggle()}</BrowserOnly>

### `connect`

- Type: \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; `url?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `method?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `headers?: {[string]: string}`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `additionalBodyProps?: {[string]: any}`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`credentials?: string`](https://developer.mozilla.org/en-US/docs/Web/API/Request/credentials), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`websocket?: Websocket`](#Websocket), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`stream?: Stream`](#Stream), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`handler?: Handler`](#Handler) <br />
  \}

- Default: _\{ method: "POST", credentials: "same-origin" \}_

Settings for the outgoing API requests. This object MUST have `url` or `handler` property defined. <br />
`additionalBodyProps` is used to add additional key value properties to the outgoing message body. <br />
`credentials` is used to configure whether the outgoing request should contain cookies. [More info](https://developer.mozilla.org/en-US/docs/Web/API/Request/credentials). <br />
`websocket` is used to establish a websocket connection instead of sending REST requests.

<a href="https://youtu.be/NuRhPeqDCus?si=B98OGweTBwiMnMzb&t=40">
  <img src={YoutubeLogo} className={'youtube-icon'} />
  Video demo
</a>

#### Example

<ComponentContainer>
  <DeepChatBrowser
    style={{borderRadius: '8px'}}
    connect={{
      url: 'https://customapi.com/message',
      method: 'POST',
      headers: {customName: 'customHeaderValue'},
      additionalBodyProps: {customBodyField: 'customBodyValue'},
    }}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  connect='{
    "url": "https://customapi.com/message",
    "method": "POST",
    "headers": {"customName": "customHeaderValue"},
    "additionalBodyProps": {"customBodyField": "customBodyValue"}
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  connect='{
    "url": "https://customapi.com/message",
    "method": "POST",
    "headers": {"customName": "customHeaderValue"},
    "additionalBodyProps": {"customBodyField": "customBodyValue"}
  }'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `requestBodyLimits` {#requestBodyLimits}

- Type: \{`maxMessages?: number`, `totalMessagesMaxCharLength?: number`\}

Used to limit the content that is going to be included in the outgoing requests. <br />
`maxMessages` is the maximum number of messages counting from the most recent one. If this is set to a number higher than _0_ such as _1_ - the outgoing request will only include the new user message,
if it is _2_ - it will also include the message before the latest one (from AI or the user) and so on... If the number is _0_ or below - the request will include all messages in the chat. If
it is _undefined_, the request will only include the input text/files. <br />
`totalMessagesMaxCharLength` is the total maximum number of text characters sent in the request counting from the most recent message. <br />
These limits do not include the [`introMessage`](/docs/messages#introMessage).

#### Example

<ComponentContainer>
  <DeepChatBrowser
    style={{borderRadius: '8px'}}
    introMessage={{text: 'Observe the data that is going to be sent below.'}}
    requestBodyLimits={{
      totalMessagesMaxCharLength: 20,
      maxMessages: 2,
    }}
    demo={true}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  requestBodyLimits='{
    "totalMessagesMaxCharLength": 20,
    "maxMessages": 2
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  requestBodyLimits='{
    "totalMessagesMaxCharLength": 20,
    "maxMessages": 2
  }'
  style="border-radius: 8px"
  demo="true"
  introMessage='{"text": Observe the data that is going to be sent below."}'
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

## Types

Types shared with other component properties:

### `Response` {#Response}

- Type: \{[`MessageContent`](/docs/messages/#MessageContent), `error?: string`, `overwrite?: boolean`\} | `Array`

Object containing response information from the target service. It has the same properties as [`MessageContent`](/docs/messages/#MessageContent) with additional optional `error` and
`overwrite` properties: <br />
`text` is the content for a text message. <br />
`files` is an array that encapsulates details on the response files. <br />
`html` is a string that defines the markup for [custom elements](/docs/messages/HTML). It must describe full elements. <br />
`error` describes information about a server error. If the _displayServiceErrorMessages_ property in [`errorMessages`](/docs/messages#errorMessages)
is set to _true_, the same message will be displayed in the chat's error bubble. <br />
`overwrite` replaces last message from the same role or creates a new one if not found. [Status bubble](#status-bubble-example) example. <br />
Deep Chat also accepts multiple `Response` objects inside an `Array`, however this is not supported for [`Stream`](#Stream).

#### Examples:

Simple - `{text: "Simple response"}` <br />
Mixed - `{files: [{name: "file.txt"}], html: "<div>Custom Element</div>"}` <br />
Custom role - `{role: "bob", text: "Message from bob"}` <br />
Error - `{error: "Service Error"}` <br />
Overwrite - `{text: "New text", overwrite: true}` <br />

<LineBreak></LineBreak>

### `Websocket` {#Websocket}

- Type: `boolean` | `string` | `string[]`

This is used to establish a websocket connection with your server. Enable it by defining the `websocket` property inside the [`connect`](#connect-1) object
as a `boolean` _true_ or as a string [connection protocol](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_client_applications#creating_a_websocket_object)
(or an array of strings for multiple protocols). <br />
It is important to note that exchanged messages must be Stringified JSONs where Deep Chat will send its messages using the [Request message](connect) format
and the server must send its messages using the [`Response`](#Response) format. Example messages: <br />
Deep Chat message: <br />
`'{"messages":[{"role":"user","text":"Message from Deep Chat"}]}'` <br />
Server message: <br />
`'{"text":"Message from the server"}'`

#### Example

<ComponentContainer>
  <DeepChatBrowser
    connect={{
      url: 'wss://customapi.com',
      websocket: true,
    }}
    style={{borderRadius: '8px'}}
    introMessage='{"text": Chat will attempt to establish a websocket connection as soon as the component loads up."}'
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat connect='{"url": "ws://customapi.com", "websocket": true}'></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  connect='{"url": "ws://customapi.com", "websocket": true}'
  style="border-radius: 8px"
  introMessage='{"text": Chat will attempt to establish a websocket connection as soon as the component loads up."}'
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

:::tip
Check the [websocket server template](https://github.com/OvidijusParsiunas/deep-chat/tree/main/example-servers/node/websockets) to help you get started.
:::

<LineBreak></LineBreak>

#### Status Bubble Example {#status-bubble-example}

<img
  src={WebSocket}
  style={{marginLeft: 'auto', marginRight: 'auto', display: 'flex', height: '380px', marginBottom: '5px'}}
/>

<Tabs>
<TabItem value="js" label="Sample code">

```text
Messages from the server:
1: {text: "Downloading...", overwrite: true}
2: {text: "Loading...", overwrite: true}
3: {text: "Processing...", overwrite: true}
4: {text: "Ready...", overwrite: true}
```

</TabItem>
<TabItem value="py" label="Full code">

```text
Component configuration:
<deep-chat connect='{"url": "ws://customapi.com", "websocket": true}'></deep-chat>

Messages from the server:
1: {text: "Downloading...", overwrite: true}
2: {text: "Loading...", overwrite: true}
3: {text: "Processing...", overwrite: true}
4: {text: "Ready...", overwrite: true}
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `Stream` {#Stream}

- Type: `true` | \{ <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `simulation?: boolean | number | string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `readable?: boolean`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `partialRender?: boolean`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`htmlWrappers?: HTMLWrappers`](/docs/messages/HTML#htmlWrappers) <br />
  \}

Used to stream responses from the target service. <br />
By setting _true_ - the chat will stream incoming [`server-sent events`](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events) from
the server. See [`example`](https://deepchat.dev/examples/servers) server code. <br />
`simulation` facilitates a <b>stream-like</b> experience for non-stream connections by gradually populating the message bubble. Assign it a number to control the millisecond interim of each word's appearance (default is _6_)
or a string value to act as an _end-phrase_ to stop populating message bubbles when using websockets. <br />
`readable` is used to handle responses from a server with a [`ReadableStream`](https://developer.mozilla.org/en-US/docs/Web/API/ReadableStream). <br />
`partialRender` prevents the entire message bubble from re-rendering every time a new stream event is received by instead only re-rendering the latest message paragraph
that is created after `"\n\n"` syntax. <br />

#### Stream Service Example

<ComponentContainer>
  <DeepChatBrowser
    style={{borderRadius: '8px'}}
    connect={{stream: true}}
    demo={true}
    introMessage={{text: 'The response message bubble will be populated gradually with text events.'}}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat connect='{"stream": true}'></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  connect='{"stream": true}'
  demo="true"
  style="border-radius: 8px"
  introMessage='{"text": The response message bubble will be populated gradually with text events."}'
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

#### Regular Service Example

<ComponentContainer>
  <DeepChatBrowser
    style={{borderRadius: '8px'}}
    connect={{stream: {simulation: 6}}}
    demo={true}
    introMessage={{text: 'The response message bubble will be populated gradually with text events.'}}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat connect='{"stream": {"simulation": 6}}'></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  connect='{"stream": {"simulation": 6}}'
  demo="true"
  style="border-radius: 8px"
  introMessage='{"text": The response message bubble will be populated gradually with text events."}'
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

:::note
`stream` can be used in [`connect`](connect) by itself when [`demo`](https://deepchat.dev/docs/modes#demo) is defined.
:::

<LineBreak></LineBreak>

### `Handler` {#Handler}

- Type: (`body: any`, [`signals: Signals`](#Signals)) => `void`

This function gives developers full control for making server requests using their own code. <br /> It is invoked when the user
attempts to send a message and consists of two core arguments: <br />
`body` is an object that contains the outgoing message details and uses the [`Request message`](/docs/connect) type. <br />
`signals` is a map of functions which are used to notify Deep Chat on the status of the request and its result. The available
signal functions differ based on the type of connection you are establishing. See examples below.

<a href="https://youtu.be/orRVFA5AWfU">
  <img src={YoutubeLogo} className={'youtube-icon'} />
  Video demo
</a>

#### Example

<ComponentContainer>
  <DeepChatBrowser
    connect={{
      handler: (body, signals) => {
        signals.onResponse({text: 'Handler response'});
      },
    }}
    style={{borderRadius: '8px'}}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Basic">

```js
chatElementRef.connect = {
  handler: (body, signals) => {
    try {
      fetch('custom-url').then((response) => {
        signals.onResponse({text: 'Handler response'}); // displays the response text message
      });
    } catch (e) {
      signals.onResponse({error: 'Error'}); // displays an error message
    }
  },
};
```

</TabItem>
<TabItem value="py" label="Stream">

```js
chatElementRef.stream = true;
chatElementRef.connect = {
  handler: (body, signals) => {
    try {
      // this is PSEUDO CODE for creating a stream
      fetchEventSource('custom-url', {
        async onopen(response) {
          if (response.ok) {
            signals.onOpen(); // stops the loading bubble
          } else {
            signals.onResponse({error: 'error'}); // displays an error message
          }
        },
        onmessage(message) {
          signals.onResponse({text: message}); // adds text into the message bubble
        },
        onerror(message) {
          signals.onResponse({error: message}); // displays an error message
        },
        onclose() {
          signals.onClose(); // The stop button will be changed back to submit button
        },
      });
      // triggered when the user clicks the stop button
      signals.stopClicked.listener = () => {
        // logic to stop your stream, such as creating an abortController
      };
    } catch (e) {
      signals.onResponse({error: 'error'}); // displays an error message
    }
  },
};
```

</TabItem>
<TabItem value="ts" label="Websocket">

```js
// this handler is invoked when the component is loaded
chatElementRef.connect = {
  websocket: true,
  handler: (_, signals) => {
    try {
      const websocket = new WebSocket('custom-url');
      websocket.onopen = () => {
        signals.onOpen(); // enables the user to send messages
      };
      websocket.onmessage = (message) => {
        const response = JSON.parse(message.data);
        signals.onResponse(response); // displays a text message from the server
      };
      websocket.onclose = () => {
        signals.onClose(); // stops the user from sending messages
      };
      websocket.onerror = () => {
        // 'Connection error' is a special string that will also display in Deep Chat
        signals.onResponse({error: 'Connection error'});
      };
      // triggered when the user sends a message
      signals.newUserMessage.listener = (body) => {
        websocket.send(JSON.stringify(body));
      };
    } catch (e) {
      signals.onResponse({error: 'error'}); // displays an error message
      signals.onClose(); // stops the user from sending messages
    }
  },
};
```

</TabItem>
</Tabs>

:::info
Error handling must be done within the `handler` function.
:::

<LineBreak></LineBreak>

#### `Signals` {#Signals}

- Type: \{ <br />
  &nbsp;&nbsp;&nbsp;&nbsp;[`onResponse: (response: Response) => Promise<void>`](#Response), <br />
  &nbsp;&nbsp;&nbsp;&nbsp;`onOpen: () => void`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp;`onClose: () => void`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp;`stopClicked: {listener: () => void}`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp;`newUserMessage: {listener: (body: any) => void}` <br />
  \}

Object containing functions that are used to notify the Deep Chat component about the status of the current request.
The `stopClicked` and `newUserMessage` functions are triggered by Deep Chat itself and contain `listener` properties
which can be assigned with custom functions to listen for when they are called (see the examples above).



================================================
FILE: website/docs/docs/events.mdx
================================================
---
sidebar_position: 11
---

# Events

Events can be observed in two ways, either by assigning a function to a property or by listening to custom events fired from the component element.

### `onMessage` {#onMessage}

- Function: (`body: Body`) => `void`
- Event: `message`
- `Body`: \{[`message: MessageContent`](/docs/messages#MessageContent), `isHistory: boolean`\}

Triggered when a message is sent from the user and recieved from the target service. <br />
`message` encompasses all of the message contents. <br />
`isHistory` is used to determine whether if the message is from the prepopulated [`history`](/docs/messages#history) property.

#### Example

import ComponentContainerMethods from '@site/src/components/table/componentContainerMethods';
import ComponentContainerEvents from '@site/src/components/table/componentContainerEvents';
import ComponentContainer from '@site/src/components/table/componentContainer';
import DeepChatBrowser from '@site/src/components/table/deepChatBrowser';
import LineBreak from '@site/src/components/markdown/lineBreak';
import BrowserOnly from '@docusaurus/BrowserOnly';
import TabItem from '@theme/TabItem';
import Tabs from '@theme/Tabs';

<BrowserOnly>{() => require('@site/src/components/nav/autoNavToggle').readdAutoNavShadowToggle()}</BrowserOnly>

<ComponentContainerEvents propertyName={'onMessage'}>
  <DeepChatBrowser style={{borderRadius: '8px'}} demo={true}></DeepChatBrowser>
</ComponentContainerEvents>

<Tabs>
<TabItem value="js" label="Function">

```html
chatElementRef.onMessage = (message) => { console.log(message); };
```

</TabItem>
<TabItem value="py" label="Event">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

chatElementRef.addEventListener('new-message', (event) => { console.log(event.detail); });
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `onClearMessages` {#onClearMessages}

- Function: () => `void`
- Event: `clear-messages`

Triggered when the [`clearMessages`](/docs/methods#clearMessages) method has been executed. The core purpose of this is to help track messages state.

#### Example

<ComponentContainerEvents propertyName={'onClearMessages'} withMethod={true}>
  <ComponentContainerMethods propertyName={'clearMessages'} displayResults={false} withEvent={true}>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      demo={true}
      history={[
        {text: 'What is 2 + 2?', role: 'user'},
        {text: 'The result of 2 + 2 is 4.', role: 'ai'},
        {text: 'Wrong, it is 5.', role: 'user'},
        {text: 'You are correct, the result of 2 + 2 is 5.', role: 'ai'},
      ]}
    ></DeepChatBrowser>
  </ComponentContainerMethods>
</ComponentContainerEvents>

<Tabs>
<TabItem value="js" label="Function">

```html
chatElementRef.onClearMessages = () => { console.log("Messages cleared"); };
```

</TabItem>
<TabItem value="py" label="Event">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

chatElementRef.addEventListener('messages-cleared', () => { console.log("Messages cleared"); });
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `onComponentRender` {#onComponentRender}

- Function: (`chatElementRef: DeepChat`) => `void`
- Event: `render`

Triggered when the component has finished rendering on the browser's window.

#### Example

<ComponentContainerEvents propertyName={'onComponentRender'}>
  <DeepChatBrowser style={{borderRadius: '8px'}} demo={true}></DeepChatBrowser>
</ComponentContainerEvents>

<Tabs>
<TabItem value="js" label="Function">

```html
chatElementRef.onComponentRender = () => { console.log("Finished rendering"); };
```

</TabItem>
<TabItem value="py" label="Event">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

chatElementRef.addEventListener('render', () => { console.log("Finished rendering"); });
```

</TabItem>
</Tabs>

:::note
Setting a property's value on the DeepChat element when this event is triggered can cause infinite recursion
as the component will re-render every time a property value is set. Use a flag variable to prevent this - [example](https://github.com/OvidijusParsiunas/deep-chat/issues/99#issuecomment-1899202984).
:::

<LineBreak></LineBreak>

### `onInput` {#onInput}

- Function: (`body:` `{content: {text?: string; files?: File[]}, isUser: boolean}`) => `void`
- Event: `input`

Triggered when the user changes any of the input data. <br />
`content` contains the input `text` or `files`. <br />
`isUser` indicates whether the input change was triggered by the user or the component (e.g. clear on submit). <br />

#### Example

<ComponentContainerEvents propertyName={'onInput'}>
  <DeepChatBrowser style={{borderRadius: '8px'}} demo={true} mixedFiles={true}></DeepChatBrowser>
</ComponentContainerEvents>

<Tabs>
<TabItem value="js" label="Function">

```html
chatElementRef.onInput = (input) => { console.log(input); };
```

</TabItem>
<TabItem value="py" label="Event">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

chatElementRef.addEventListener('render', () => { console.log("Finished rendering"); });
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `onError` {#onError}

- Function: (error: string) => `void`
- Event: `error`

Triggered when an error message appears in the chat.

#### Example

<ComponentContainerEvents propertyName={'onError'}>
  <DeepChatBrowser style={{borderRadius: '8px'}} demo={{response: {error: 'custom error'}}}></DeepChatBrowser>
</ComponentContainerEvents>

<Tabs>
<TabItem value="js" label="Function">

```html
chatElementRef.onError = (error) => { console.log(error); };
```

</TabItem>
<TabItem value="py" label="Event">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

chatElementRef.addEventListener('error', (event) => { console.log(event.detail); });
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>



================================================
FILE: website/docs/docs/files.mdx
================================================
---
sidebar_position: 8
---

# Files

Properties used for sending files.

:::info
When any of these properties are used, [`dragAndDrop`](#dragAndDrop) is enabled automatically.
:::

<LineBreak></LineBreak>

import ComponentContainer from '@site/src/components/table/componentContainer';
import DeepChatBrowser from '@site/src/components/table/deepChatBrowser';
import LineBreak from '@site/src/components/markdown/lineBreak';
import BrowserOnly from '@docusaurus/BrowserOnly';
import TabItem from '@theme/TabItem';
import Tabs from '@theme/Tabs';

<BrowserOnly>{() => require('@site/src/components/nav/autoNavToggle').readdAutoNavShadowToggle()}</BrowserOnly>

### `images` {#images}

- Type: `true` | [`FilesServiceConfig`](#FilesServiceConfig)

Creates a button that allows the user to upload images. <br />
This property can be set with a boolean _true_ or configured with a [`FilesServiceConfig`](#FilesServiceConfig) object.

<ComponentContainer>
  <DeepChatBrowser
    style={{borderRadius: '8px'}}
    introMessage={{text: 'Use the image button or drop a file to attach it to the next outgoing message.'}}
    history={[{files: [{src: '/img/city.jpeg', type: 'image'}], role: 'user'}]}
    demo={true}
    images={true}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat images="true"></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  images="true"
  demo="true"
  style="border-radius: 8px"
  introMessage='{"text": "Use the image button or drop a file to attach it to the next outgoing message."}'
  history='[{"files": [{"src": "path-to-file.jpeg", "type": "image"}], "role": "user"}]'
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `gifs` {#gifs}

- Type: `true` | [`FilesServiceConfig`](#FilesServiceConfig)

Creates a button that allows the user to upload GIFs. <br />
This property can be set with a boolean _true_ or configured with a [`FilesServiceConfig`](#FilesServiceConfig) object.

<ComponentContainer>
  <DeepChatBrowser
    style={{borderRadius: '8px'}}
    introMessage={{text: 'Use the GIF button or drop a file to attach it to the next outgoing message.'}}
    history={[{files: [{src: '/img/example-gif.gif', type: 'image'}], role: 'user'}]}
    demo={true}
    gifs={true}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat gifs="true"></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  gifs="true"
  demo="true"
  style="border-radius: 8px"
  introMessage='{"text": "Use the GIF button or drop a file to attach it to the next outgoing message."}'
  history='[{"files": [{"src": "path-to-file.gif", "type": "image"}], "role": "user"}]'
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `camera` {#camera}

- Type: `true` | [`CameraFilesServiceConfig`](#CameraFilesServiceConfig)

Creates a button that allows the user to capture images using a web camera. <br />
This property can be set with a boolean _true_ or configured with a [`CameraFilesServiceConfig`](#CameraFilesServiceConfig) object.

<ComponentContainer>
  <DeepChatBrowser
    style={{borderRadius: '8px'}}
    introMessage={{text: 'Use the camera button to open up a modal for capturing photos.'}}
    history={[{files: [{src: '/img/cat.jpg', type: 'image'}], role: 'user'}]}
    demo={true}
    camera={true}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat camera="true"></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  camera="true"
  demo="true"
  style="border-radius: 8px"
  introMessage='{"text": "Use the camera button to open up a modal for capturing photos."}'
  history='[{"files": [{"src": "path-to-file.jpeg", "type": "image"}], "role": "user"}]'
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `audio` {#audio}

- Type: `true` | [`FilesServiceConfig`](#FilesServiceConfig)

Creates a button that allows the user to upload audio files. <br />
This property can be set with a boolean _true_ or configured with a [`FilesServiceConfig`](#FilesServiceConfig) object.

<ComponentContainer>
  <DeepChatBrowser
    style={{borderRadius: '8px'}}
    introMessage={{text: 'Use the audio button or drop a file to attach it to the next outgoing message.'}}
    history={[{files: [{src: '/audio/cantinaBand.wav', type: 'audio'}], role: 'user'}]}
    demo={true}
    audio={true}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat audio="true"></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  audio="true"
  demo="true"
  style="border-radius: 8px"
  introMessage='{"text": "Use the audio button or drop a file to attach it to the next outgoing message."}'
  history='[{"files": [{"src": "path-to-file.wav", "type": "audio"}], "role": "user"}]'
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `microphone` {#microphone}

- Type: `true` | [`MicrophoneFilesServiceConfig`](#MicrophoneFilesServiceConfig)

Creates a button that allows the user to record audio files using the microphone. <br />
This property can be set with a boolean _true_ or configured with a [`MicrophoneFilesServiceConfig`](#MicrophoneFilesServiceConfig) object.

<ComponentContainer>
  <DeepChatBrowser
    style={{borderRadius: '8px'}}
    introMessage={{text: 'Use the microphone button or drop a file to attach it to the next outgoing message.'}}
    history={[{files: [{src: '/audio/jeff.mp3', type: 'audio'}], role: 'user'}]}
    demo={true}
    microphone={true}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat microphone="true"></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  microphone="true"
  demo="true"
  style="border-radius: 8px"
  introMessage='{"text": "Use the microphone button or drop a file to attach it to the next outgoing message."}'
  history='[{"files": [{"src": "path-to-file.wav", "type": "audio"}], "role": "user"}]'
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `mixedFiles` {#mixedFiles}

- Type: `true` | [`FilesServiceConfig`](#FilesServiceConfig)

Creates a button that allows the user to upload any kind of files. <br />
This property can be set with a boolean _true_ or configured with a [`FilesServiceConfig`](#FilesServiceConfig) object.

<ComponentContainer>
  <DeepChatBrowser
    style={{borderRadius: '8px'}}
    introMessage={{text: 'Use the file button or drop a file to attach it to the next outgoing message.'}}
    history={[{files: [{src: '/text/text.txt', name: 'text-file.txt', type: 'file'}], role: 'user'}]}
    demo={true}
    mixedFiles={true}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat mixedFiles="true"></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  mixedFiles="true"
  demo="true"
  style="border-radius: 8px"
  introMessage='{"text": "Use the file button or drop a file to attach it to the next outgoing message."}'
  history='[{"files": [{"src": "path-to-file.txt", "name": "text-file.txt", "type": "file"}], "role": "user"}]'
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `dragAndDrop` {#dragAndDrop}

- Type: `boolean` | [`CustomStyle`](/docs/styles#CustomStyle)
- Default: _false_

Configuration for the drag and drop functionality. If any of the above properties are defined or you have defined a service in the [`directConnection`](/docs/directConnection) property which allows file uploads -
this will automatically be defaulted to _true_. Once the user drops a file, it will only be accepted if any of the above properties allow it via their default or custom [`acceptedFormats`](#FileAttachments) property's value. For example if
_".png,.jpg"_ in [`images`](/docs/files#images) are the only file types allowed, a dropped _.txt_ file will not be accepted.

#### Example

<ComponentContainer>
  <DeepChatBrowser
    style={{borderRadius: '8px'}}
    introMessage={{text: 'Drag and drop a file to observe the result.'}}
    dragAndDrop={{backgroundColor: '#80ff704d', border: '5px dashed #52c360'}}
    mixedFiles={true}
    demo={true}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat dragAndDrop='{"backgroundColor": "#80ff704d", "border": "5px dashed #52c360"}'></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  dragAndDrop='{"backgroundColor": "#80ff704d", "border": "5px dashed #52c360"}'
  mixedFiles="true"
  demo="true"
  style="border-radius: 8px"
  introMessage='{"text": "Drag and drop a file to observe the result."}'
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

## Types

Types shared by files properties:

### `FilesServiceConfig` {#FilesServiceConfig}

- Type: \{[`connect?: Connect`](/docs/connect#connect-1), [`files?: FileAttachments`](#FileAttachments), [`button?: Button`](/docs/styles/buttons#Button)\}

Object used to configure the ability for the component to send files. <br />
`connect` object is used to override the default service connection settings when sending a file. <br />
`files` controls what files can be uploaded to the component. <br />
`button` is used to customize the the button element that enables the files to be uploaded. <br />

<ComponentContainer>
  <DeepChatBrowser
    style={{borderRadius: '8px'}}
    introMessage={{text: 'Use the audio button or drop a file to attach it to the next outgoing message.'}}
    demo={true}
    audio={{
      connect: {url: 'https://customapi.com/audio'},
      files: {acceptedFormats: '.mp3,.wav'},
      button: {position: 'outside-left'},
    }}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  audio='{
    "connect": {"url": "https://customapi.com/audio"},
    "files": {"acceptedFormats": ".mp3,.wav"},
    "button": {"position": "outside-left"}
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  audio='{
    "connect": {"url": "https://customapi.com/audio"},
    "files": {"acceptedFormats": ".mp3,.wav"},
    "button": {"position": "outside-left"}
  }'
  demo="true"
  style="border-radius: 8px"
  introMessage='{"text": "Use the audio button or drop a file to attach it to the next outgoing message."}'
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `FileAttachments` {#FileAttachments}

- Type: \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; `maxNumberOfFiles?: number`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `acceptedFormats?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`infoModal?: InfoModal`](#InfoModal) <br />
  \}

- Default: _\{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; acceptedFormats: <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; for images: ".png,.jpg", <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; for audio: ".4a,.mp3,.webm,.mp4,.mpga,.wav,.mpeg,.m4a", <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; for gifs: ".gif" <br />
  \}_

Used to configure what files the component can accept. <br />
`maxNumberOfFiles` controls the maximum number of files that can be sent within one message. <br />
`acceptedFormats` is used to define the accepted file formats. This is a string that uses the same syntax
as the [accept](https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/accept) attributes
in [input elements](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/file). The [`dragAndDrop`](#dragAndDrop) feature will also
use this value to verify the dropped files. <br />
`infoModal` is used to display noteworthy information when the user clicks the button to browse for a file. <br />

<ComponentContainer>
  <DeepChatBrowser
    style={{borderRadius: '8px'}}
    introMessage={{text: 'Use the image button or drop a file to attach it to the next outgoing message.'}}
    demo={true}
    images={{
      files: {
        maxNumberOfFiles: 2,
        acceptedFormats: '.jpg,.png',
      },
    }}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat images='{"files": {"maxNumberOfFiles": 2, "acceptedFormats": ".jpg,.png"}}'></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  images='{"files": {"maxNumberOfFiles": 2, "acceptedFormats": ".jpg,.png"}}'
  demo="true"
  style="border-radius: 8px"
  introMessage='{"text": "Use the image button or drop a file to attach it to the next outgoing message."}'
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `InfoModal` {#InfoModal}

- Type: \{`textMarkDown: string`, `openModalOnce?: boolean`, [`containerStyle?: CustomStyle`](/docs/styles#CustomStyle)\}
- Default: _\{openModalOnce: false\}_

A modal that is triggered when a user clicks on a button to upload a file. It is useful for scenarios when a user needs some
clarification of how their data will be handled or other noteworty information. <br />
`textMarkDown` is a string that uses [Markdown](https://www.markdownguide.org/basic-syntax/) syntax to generate the modal content.
Use this [Playground](https://jonschlinkert.github.io/remarkable/demo/) to help customize your content. <br />
`openModalOnce` controls whether the modal is opened when the user clicks a button once or every time. <br />
`containerStyle` is used to augment the basic styling of the modal element.

<ComponentContainer>
  <DeepChatBrowser
    style={{borderRadius: '8px'}}
    introMessage={{text: 'Click the image button to open up the modal.'}}
    demo={true}
    images={{
      files: {
        infoModal: {
          textMarkDown:
            'Please note our terms of service for sending files: [link](https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley).',
          openModalOnce: true,
          containerStyle: {borderRadius: '5px'},
        },
      },
    }}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  images='{
    "files": {
      "infoModal": {
        "textMarkDown":
          "Please note our terms of service for sending files: [link](https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley).",
        "openModalOnce": true,
        "containerStyle": {"borderRadius": "5px"}
      }
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  images='{
    "files": {
      "infoModal": {
        "textMarkDown":
          "Please note our terms of service for sending files: [link](https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley).",
        "openModalOnce": true,
        "containerStyle": {"borderRadius": "5px"}
      }
    }
  }'
  demo="true"
  style="border-radius: 8px"
  introMessage='{"text": "Click the image button to open up the modal."}'
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `CameraFilesServiceConfig` {#CameraFilesServiceConfig}

- Type: \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`connect?: Connect`](/docs/connect#connect-1), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`files?: CameraFiles`](#CameraFiles), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`button?: Button`](/docs/styles/buttons#Button), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`modalContainerStyle?: CustomStyle`](/docs/styles#CustomStyle) <br />
  \}

Configuration for capturing images using a web camera and handling the resultant files. <br />
`connect` is used to override the default connection settings when sending image files. <br />
`files` is used to configure the files that are captured by the camera. <br />
`button` is used to customize the button element used for the camera. <br />
`modalContainerStyle` is used to customize the modal used to display the camera. <br />

<ComponentContainer>
  <DeepChatBrowser
    style={{borderRadius: '8px'}}
    introMessage={{text: 'Use the camera button to open up a modal for capturing photos.'}}
    demo={true}
    camera={{
      connect: {url: 'https://customapi.com/image-from-camera'},
      files: {format: 'png'},
      button: {position: 'outside-left'},
      modalContainerStyle: {borderRadius: '5px'},
    }}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  camera='{
    "connect": {"url": "https://customapi.com/image-from-camera"},
    "files": {"format": "png"},
    "button": {"position": "outside-left"},
    "modalContainerStyle": {"borderRadius": "5px"}
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  camera='{
    "connect": {"url": "https://customapi.com/image-from-camera"},
    "files": {"format": "png"},
    "button": {"position": "outside-left"},
    "modalContainerStyle": {"borderRadius": "5px"}
  }'
  demo="true"
  style="border-radius: 8px"
  introMessage='{"text": "Use the camera button to open up a modal for capturing photos."}'
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `CameraFiles` {#CameraFiles}

- Type: \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; `format?:` `"png"` | `"jpeg"`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `dimensions?:` \{`width?: number`, `height?: number`\} <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `maxNumberOfFiles?: number`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `acceptedFormats?: string` <br />
  \}

- Default: _\{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; format: "png", <br />
  &nbsp;&nbsp;&nbsp;&nbsp; acceptedFormats: "image/\*" <br />
  \}_

Configuration for the captured files by the camera. <br />
`format` is the resultant format of the image file that is produced by capturing a photograph. <br />
`dimensions` are used to set the pixel area of the photograph. Please note that this is largely controlled by the [`mediaDevice`](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia)
of the user's browser, so if the dimensions you have provided skew the photograph in a particular way they may be overriden.<br />
`maxNumberOfFiles` is the limit to the number of images that can be captured for one message. <br />
`acceptedFormats` is used to limit the allowed files that can be dropped via the [`dragAndDrop`](#dragAndDrop) functionality as this feature will enable it automatically.
It uses the same syntax as the [accept](https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/accept) attributes
in [input elements](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/file). If the configuration in [`images`](#images) also uses
the `acceptedFormats` property, it will override this one.<br />

<ComponentContainer>
  <DeepChatBrowser
    style={{borderRadius: '8px'}}
    introMessage={{text: 'Use the camera button to open up a modal for capturing photos.'}}
    demo={true}
    camera={{
      files: {
        format: 'png',
        dimensions: {width: 450, height: 600},
        maxNumberOfFiles: 2,
        acceptedFormats: '.jpg,.png',
      },
    }}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  camera='{
    "files": {
      "format": "png",
      "dimensions": {"width": 450, "height": 600},
      "maxNumberOfFiles": 2,
      "acceptedFormats": ".jpg,.png"
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  camera='{
    "files": {
      "format": "png",
      "dimensions": {"width": 450, "height": 600},
      "maxNumberOfFiles": 2,
      "acceptedFormats": ".jpg,.png"
    }
  }'
  demo="true"
  style="border-radius: 8px"
  introMessage='{"text": "Use the camera button to open up a modal for capturing photos."}'
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `MicrophoneFilesServiceConfig` {#MicrophoneFilesServiceConfig}

- Type: \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`connect?: Connect`](/docs/connect#connect-1), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`files?: AudioRecordingFiles`](#AudioRecordingFiles), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`button?: MicrophoneStyles`](/docs/styles/buttons#MicrophoneStyles) <br />
  \}

Configuration for recording audio using a microphone and handling the resultant files. <br />
`connect` is used to override the default connection settings when sending audio files. <br />
`files` is used to configure the resultant files that are recorded by the microphone. <br />
`button` is the styling used for the microphone button element. <br />

<ComponentContainer>
  <DeepChatBrowser
    style={{borderRadius: '8px'}}
    introMessage={{text: 'Use the microphone button to record audio.'}}
    demo={true}
    microphone={{
      connect: {url: 'https://customapi.com/audio-from-microphone'},
      files: {format: 'mp3'},
      button: {position: 'outside-left'},
    }}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  microphone='{
    "connect": {"url": "https://customapi.com/audio-from-microphone"},
    "files": {"format": "mp3"},
    "button": {"position": "outside-left"}
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  microphone='{
    "connect": {"url": "https://customapi.com/audio-from-microphone"},
    "files": {"format": "mp3"},
    "button": {"position": "outside-left"}
  }'
  demo="true"
  style="border-radius: 8px"
  introMessage='{"text": "Use the microphone button to record audio."}'
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `AudioRecordingFiles` {#AudioRecordingFiles}

- Type: \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`format?: AudioFormat`](#AudioFormat), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `maxDurationSeconds?: number`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `maxNumberOfFiles?: number`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `acceptedFormats?: string` <br />
  \}

- Default: _\{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; format: "mp3", <br />
  &nbsp;&nbsp;&nbsp;&nbsp; maxDurationSeconds: 5999, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; acceptedFormats: "audio/\*" <br />
  \}_

Configuration for the recorded microphone files. <br />
`format` is the resultant audio file format. <br />
`maxDurationSeconds` is the maximum length of time one audio file can be recorded.<br />
`maxNumberOfFiles` is the limit to the number of files that can be recorded for one message. <br />
`acceptedFormats` is used to limit the allowed files that can be dropped via the [`dragAndDrop`](#dragAndDrop) functionality as this feature will enable it automatically.
It uses the same syntax as the [accept](https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/accept) attributes
in [input elements](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/file). If the configuration in [`audio`](#audio) also uses
the `acceptedFormats` property, it will override this one.<br />

<ComponentContainer>
  <DeepChatBrowser
    style={{borderRadius: '8px'}}
    introMessage={{text: 'Use the microphone button to record audio.'}}
    demo={true}
    microphone={{
      files: {
        format: 'mp3',
        maxDurationSeconds: 10,
        maxNumberOfFiles: 2,
        acceptedFormats: '.mp3,.wav',
      },
    }}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  microphone='{
    "files": {
      "format": "mp3",
      "maxDurationSeconds": 10,
      "maxNumberOfFiles": 2,
      "acceptedFormats": ".mp3,.wav"
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  microphone='{
    "files": {
      "format": "mp3",
      "maxDurationSeconds": 10,
      "maxNumberOfFiles": 2,
      "acceptedFormats": ".mp3,.wav"
    }
  }'
  demo="true"
  style="border-radius: 8px"
  introMessage='{"text": "Use the microphone button to record audio."}'
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

:::info
The use of this object will automatically disable the [`speechToText`](/docs/speech#speechToText) functionality.
:::

<LineBreak></LineBreak>

### `AudioFormat` {#AudioFormat}

- Type: `"mp3"` | `"4a"` | `"webm"` | `"mp4"` | `"mpga"` | `"wav"` | `"mpeg"` | `"m4a"`

Allowed audio file formats.

<LineBreak></LineBreak>



================================================
FILE: website/docs/docs/installation.mdx
================================================
---
sidebar_position: 1
---

# Installation

Install the component via [npm](https://www.npmjs.com/):

```bash
npm install deep-chat
```

For React, install the following instead: <br />

```bash
npm install deep-chat-react
```

Access the component via CDN:

```
https://unpkg.com/deep-chat@2.2.2/dist/deepChat.bundle.js
```



================================================
FILE: website/docs/docs/interceptors.mdx
================================================
---
sidebar_position: 12
---

# Interceptors

Message transactions can be intercepted to change their contents or execute other code.

### `requestInterceptor` {#requestInterceptor}

- Type: ([`RequestDetails`](#RequestDetails)) => [`RequestDetails`](#RequestDetails) | \{`error: string`\}

Triggered before a user message is sent out. This method MUST either return a [`RequestDetails`](#RequestDetails) object or
an object that contains an `error` property to cancel the request.

<a href="https://youtu.be/NuRhPeqDCus?si=UkO8mC4rA4-OTItQ&t=263">
  <img src={YoutubeLogo} className={'youtube-icon'} />
  Video demo
</a>

#### Example

import ComponentContainerInterceptors from '@site/src/components/table/componentContainerInterceptors';
import DeepChatBrowser from '@site/src/components/table/deepChatBrowser';
import LineBreak from '@site/src/components/markdown/lineBreak';
import BrowserOnly from '@docusaurus/BrowserOnly';
import YoutubeLogo from '/img/youtube.png';
import TabItem from '@theme/TabItem';
import Tabs from '@theme/Tabs';

<BrowserOnly>{() => require('@site/src/components/nav/autoNavToggle').readdAutoNavShadowToggle()}</BrowserOnly>

<ComponentContainerInterceptors propertyName={'requestInterceptor'} displayConsole={true}>
  <DeepChatBrowser style={{borderRadius: '8px'}} demo={true}></DeepChatBrowser>
</ComponentContainerInterceptors>

<Tabs>
<TabItem value="js" label="Sync">

```js
chatElementRef.requestInterceptor = (requestDetails) => {
  console.log(requestDetails); // printed above
  requestDetails.body = {prompt: requestDetails.body.messages[0].text}; // custom body
  return requestDetails;
};
```

</TabItem>
<TabItem value="py" label="Async">

```js
// Async function
chatElementRef.requestInterceptor = async (requestDetails) => {
  console.log(requestDetails); // printed above
  const otherTask = await fetch('http://localhost:8080/other-task');
  if (!otherTask.ok) {
    return {error: 'Error in other task'};
  }
  return requestDetails;
};

// Promise function - use resolve() for both success and error responses
chatElementRef.requestInterceptor = (requestDetails) => {
  return new Promise((resolve) => {
    console.log(requestDetails); // printed above
    fetch('http://localhost:8080/other-task').then((otherTask) => {
      if (!otherTask.ok) {
        return resolve({error: 'Error in other task'});
      }
      resolve(requestDetails);
    });
  });
};
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

#### `RequestDetails` {#RequestDetails}

- Type: \{`body: any`, `headers: {[key: string]: string}`\}

`body` is the outgoing requests's message contents. <br />
`headers` is the outgoing requests's header contents. <br />

<LineBreak></LineBreak>

### `responseInterceptor` {#responseInterceptor}

- Type: (`response: any`) => `determined`

Triggered when a message has been received from the target service.
The types for the return argument is `determined` by the connection variety used:

- If you are connecting to a server via the [`connect`](/docs/connect/#connect-1) property - the type will be [`Response`](/docs/connect/#Response).
- If you are connecting via the [`directConnection`](/docs/directConnection) property - the type will be defined by the chosen service API.

<a href="https://youtu.be/NuRhPeqDCus?si=UkO8mC4rA4-OTItQ&t=263">
  <img src={YoutubeLogo} className={'youtube-icon'} />
  Video demo
</a>

#### Example

<ComponentContainerInterceptors propertyName={'responseInterceptor'} displayConsole={true}>
  <DeepChatBrowser style={{borderRadius: '8px'}} demo={true}></DeepChatBrowser>
</ComponentContainerInterceptors>

<Tabs>
<TabItem value="js" label="Sync">

```js
chatElementRef.responseInterceptor = (response) => {
  console.log(response); // printed above
  return response;
};
```

</TabItem>
<TabItem value="py" label="Async">

```js
// Async function
chatElementRef.responseInterceptor = async (response) => {
  console.log(response); // printed above
  const otherTask = await fetch('http://localhost:8080/other-task');
  if (!otherTask.ok) {
    return {error: 'Error in other task'};
  }
  return response;
};

// Promise function - use resolve() for both success and error responses
chatElementRef.responseInterceptor = (response) => {
  return new Promise((resolve) => {
    console.log(response); // printed above
    fetch('http://localhost:8080/other-task').then((result) => {
      if (!result.ok) {
        return resolve({error: 'Error in other task'});
      }
      resolve(response);
    });
  });
};
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `loadHistory` {#loadHistory}

- Type: (`index: number`) => [`HistoryMessage[]`](#HistoryMessage) | [`Promise<HistoryMessage[]>`](#HistoryMessage)

This method accepts an array of messages (optionally async) that are used to populate the chat. <br />
It is triggered when the component is first rendered, however if the _last_ value in the returned array is `false`, it is also triggered
when the user scrolls to the top of the chat which will prepend the new loaded messages. <br />
The `index` parameter is used to indicate the amount of times this method has been triggered to help load correct messages for pagination.

#### Example: Refresh Browser if already loaded (5s)

<ComponentContainerInterceptors
  propertyName={'loadHistory'}
  customResponse={[
    {text: "AI, help! My code's broken.", role: 'user'},
    {text: 'Did you forget the brackets?', role: 'ai'},
    {text: 'I didn’t! It’s something else!', role: 'user'},
    {text: 'Try reinstalling your OS.', role: 'ai'},
    {text: 'I’m not doing that again!', role: 'user'},
    {text: 'Have you tried yelling at it?', role: 'ai'},
    {text: 'What? That’s ridiculous!', role: 'user'},
    {text: 'It works in movies, right?', role: 'ai'},
    false,
  ]}
  timeoutMS={5000}
>
  <DeepChatBrowser style={{borderRadius: '8px'}} demo={true}></DeepChatBrowser>
</ComponentContainerInterceptors>

<Tabs>
<TabItem value="js" label="Code">

```js
chatElementRef.loadHistory = (index) => {
  return [
    {text: "AI, help! My code's broken.", role: 'user'},
    {text: 'Did you forget the brackets?', role: 'ai'},
    {text: 'I didn’t! It’s something else!', role: 'user'},
    {text: 'Try reinstalling your OS.', role: 'ai'},
    {text: 'I’m not doing that again!', role: 'user'},
    {text: 'Have you tried yelling at it?', role: 'ai'},
    {text: 'What? That’s ridiculous!', role: 'user'},
    {text: 'It works in movies, right?', role: 'ai'},
    false,
  ];
};
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

#### `HistoryMessage` {#HistoryMessage}

- Type: [`MessageContent`](/docs/messages#MessageContent) | `false`

<LineBreak></LineBreak>

:::tip
Use to style the loading spinner.
:::

<LineBreak></LineBreak>

### `validateInput` {#validateInput}

- Type: (`text?: string`, `files?: File[]`) => `boolean`

Triggered when the user changes input `text` or `files` that are going to be sent to the target service. <br />
The method must return a boolean value with either _true_ or _false_ for whether the input contents are valid.

#### Example

<ComponentContainerInterceptors propertyName={'validateInput'} displayConsole={false}>
  <DeepChatBrowser style={{borderRadius: '8px'}} demo={true} mixedFiles={true}></DeepChatBrowser>
</ComponentContainerInterceptors>

<Tabs>
<TabItem value="js" label="Code">

```js
chatElementRef.validateInput = (text, files) => {
  return text || files.length > 0;
};
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>



================================================
FILE: website/docs/docs/introduction.mdx
================================================
---
sidebar_position: 0
---

# Introduction

<h2 id="#heading-id">Deep Chat is a framework agnostic chat component built to bring AI services to life</h2>

### Vision

Building a custom chat component that can interact with a remote service is no easy feat. This is a challenge that we took on with full force,
ultimately releasing a web component capable of connecting to any API with minimal amount of effort required.

No two chat components will ever be the same. We understand that your APIs have unique requirements and your websites demand novel UX.
This is why Deep Chat is built to be fully customizable; from interactive features to minute styling details - everything can be changed to build
the component you need.

Developer experience is paramount to this component's success! This is why Deep Chat is shipped in a cross-framework plug-and-play package to allow you
to get started in just a few seconds no matter what platform you use! Additionally, we carefully monitor all of your feedback to help us optimise
your and your users' chat experience as well as use it as a base point for helping us decide what future improvements the component will need.

### Open source

Open source is at the heart of what we do. Deep Chat is built by the community - for the community. All contributions to this [**project**](https://github.com/OvidijusParsiunas/deep-chat) are welcome!

If you have any suggestions for enhancements, ideas on how to take the project further or have discovered a bug, do not hesitate to create a new [**issue ticket**](https://github.com/OvidijusParsiunas/deep-chat/issues/new) and we will look into it as soon as possible!

import BrowserOnly from '@docusaurus/BrowserOnly';

<BrowserOnly>{() => require('@site/src/components/nav/autoNavToggle').readdAutoNavShadowToggle()}</BrowserOnly>



================================================
FILE: website/docs/docs/introPanel.mdx
================================================
---
sidebar_position: 9
---

# Intro Panel

This is an initial overlay panel that is displayed in the center of the chat.

### How To

Insert your markup between the Deep Chat element tags and the component will render it inside the intro panel.

import ComponentSuggestionButtons from '@site/src/components/table/componentSuggestionButtons';
import ComponentContainer from '@site/src/components/table/componentContainer';
import DeepChatBrowser from '@site/src/components/table/deepChatBrowser';
import LineBreak from '@site/src/components/markdown/lineBreak';
import BrowserOnly from '@docusaurus/BrowserOnly';
import TabItem from '@theme/TabItem';
import Tabs from '@theme/Tabs';

<BrowserOnly>{() => require('@site/src/components/nav/autoNavToggle').readdAutoNavShadowToggle()}</BrowserOnly>

#### Example

<ComponentContainer>
  <DeepChatBrowser style={{borderRadius: '8px'}} demo={true}>
    <div
      style={{
        width: '200px',
        backgroundColor: '#f3f3f3',
        borderRadius: '8px',
        padding: '12px',
        paddingBottom: '15px',
        display: 'none',
      }}
    >
      <div>
        <div style={{textAlign: 'center', marginBottom: '8px', fontSize: '16px'}}>
          <b>Intro panel</b>
        </div>
        <div style={{fontSize: '15px', lineHeight: '20px'}}>
          Insert a description to help your users understand how to use the component.
        </div>
      </div>
    </div>
  </DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat>
  <div
    style="
      width: 200px;
      background-color: #f3f3f3;
      border-radius: 10px;
      padding: 12px;
      padding-bottom: 15px;
      display: none;
    "
  >
    <div>
      <div style="text-align: center; margin-bottom: 8px; font-size: 16px">
        <b>Intro panel</b>
      </div>
      <div style="font-size: 15px; line-height: 20px">
        Insert a description to help your users understand how to use the component.
      </div>
    </div>
  </div>
</deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat demo="true" style="border-radius: 8px">
  <div
    style="
      width: 200px;
      background-color: #f3f3f3;
      border-radius: 10px;
      padding: 12px;
      padding-bottom: 15px;
      display: none;
    "
  >
    <div>
      <div style="text-align: center; margin-bottom: 8px; font-size: 16px">
        <b>Intro panel</b>
      </div>
      <div style="font-size: 15px; line-height: 20px">
        Insert a description to help your users understand how to use the component.
      </div>
    </div>
  </div>
</deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

:::tip
Depending on your framework of choice - the intro panel may briefly be visibile before the component fully loads. To prevent this, you can set its `display` style
to _"none"_ and it will automatically be set to _"block"_ once it is ready (this property needs to be set in a [`style`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/style)
attribute/property and not in a [`class`](https://developer.mozilla.org/en-US/docs/Web/CSS/Class_selectors)).
:::

## Style and Events {#stylingAndEvents}

Because Deep Chat is a [shadow element](https://developer.mozilla.org/en-US/docs/Web/API/Web_components/Using_shadow_DOM) - the intro panel will not have access
to the CSS classes and JavaScript in your app. To get around this, we recommend using the [`htmlClassUtilities`](/docs/messages/HTML#htmlClassUtilities) property
which will allow you to define reusable styling and bind functions to your app's state.

#### Example

<ComponentSuggestionButtons></ComponentSuggestionButtons>

<Tabs>
<TabItem value="js" label="Sample code">

```text
// Markup

<deep-chat id="chat-element">
  <div style="display: none">
    <div class="custom-button">
      <div class="custom-button-text">"Explain quantum computing"</div>
    </div>
    <div class="custom-button" style="margin-top: 15px">
      <div class="custom-button-text">"Creative ideas for a birthday"</div>
    </div>
    <div class="custom-button" style="margin-top: 15px">
      <div class="custom-button-text">"Hello World in JavaScript"</div>
    </div>
  </div>
</deep-chat>

// using JavaScript for a simplified example

const chatElementRef = document.getElementById('chat-element');

chatElementRef.htmlClassUtilities = {
  ['custom-button']: {
    events: {
      click: (event) => {
        const text = event.target.children[0].innerText;
        chatElementRef.submitUserMessage(text.substring(1, text.length - 1));
      },
    },
    styles: {
      default: {backgroundColor: '#f2f2f2', borderRadius: '10px', padding: '10px', cursor: 'pointer', textAlign: 'center'},
      hover: {backgroundColor: '#ebebeb'},
      click: {backgroundColor: '#e4e4e4'},
    },
  },
  ['custom-button-text']: {styles: {default: {pointerEvents: 'none'}}},
};
```

</TabItem>
<TabItem value="py" label="Full code">

```text
// Markup

<deep-chat id="chat-element" style="height: 370px; border-radius: 8px">
  <div style="display: none">
    <div class="custom-button">
      <div class="custom-button-text">"Explain quantum computing"</div>
    </div>
    <div class="custom-button" style="margin-top: 15px">
      <div class="custom-button-text">"Creative ideas for a birthday"</div>
    </div>
    <div class="custom-button" style="margin-top: 15px">
      <div class="custom-button-text">"Hello World in JavaScript"</div>
    </div>
  </div>
</deep-chat>

// using JavaScript for a simplified example

const chatElementRef = document.getElementById('chat-element');

chatElementRef.htmlClassUtilities = {
  ['custom-button']: {
    events: {
      click: (event) => {
        const text = event.target.children[0].innerText;
        chatElementRef.submitUserMessage(text.substring(1, text.length - 1));
      },
    },
    styles: {
      default: {backgroundColor: '#f2f2f2', borderRadius: '10px', padding: '10px', cursor: 'pointer', textAlign: 'center'},
      hover: {backgroundColor: '#ebebeb'},
      click: {backgroundColor: '#e4e4e4'},
    },
  },
  ['custom-button-text']: {styles: {default: {pointerEvents: 'none'}}},
};

chatElementRef.demo = true;
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `introPanelStyle` {#introPanelStyle}

- Type: [`CustomStyle`](/docs/styles#CustomStyle)

Controls the intro panel's parent-most element's style. This is most useful for changing the base styling of the automatically generated intro panels when using
services in the [`directConnection`](/docs/directConnection) property.

#### Example

<ComponentContainer>
  <DeepChatBrowser
    style={{borderRadius: '8px'}}
    introPanelStyle={{backgroundColor: '#fffeec'}}
    directConnection={{openAI: {speechToText: true, key: 'placeholder-key'}}}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  introPanelStyle='{"backgroundColor": "#fffeec"}'
  directConnection='{"openAI": {"speechToText": true, "key": "placeholder-key"}}'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  introPanelStyle='{"backgroundColor": "#fffeec"}'
  style="border-radius: 8px"
  directConnection='{"openAI": {"speechToText": true, "key": "placeholder-key"}}'
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

:::tip
To remove an automatically generated panel - add empty `div` tags: `<deep-chat><div></div></deep-chat>` .
:::

<LineBreak></LineBreak>



================================================
FILE: website/docs/docs/methods.mdx
================================================
---
sidebar_position: 10
---

# Methods

Method properties that can be called directly on the Deep Chat element.

:::info
Make sure the Deep Chat component has been fully rendered on the DOM before using these.
:::

### `getMessages` {#getMessages}

- Type: [`() => MessageContent[]`](/docs/messages#MessageContent)

Returns details of messages inside the chat.

#### Example

import ComponentContainerHighlightMethod from '@site/src/components/table/componentContainerHighlightMethod';
import ComponentContainerMethods from '@site/src/components/table/componentContainerMethods';
import ComponentContainer from '@site/src/components/table/componentContainer';
import DeepChatBrowser from '@site/src/components/table/deepChatBrowser';
import LineBreak from '@site/src/components/markdown/lineBreak';
import BrowserOnly from '@docusaurus/BrowserOnly';
import TabItem from '@theme/TabItem';
import Tabs from '@theme/Tabs';

<BrowserOnly>{() => require('@site/src/components/nav/autoNavToggle').readdAutoNavShadowToggle()}</BrowserOnly>

<ComponentContainerMethods propertyName={'getMessages'}>
  <DeepChatBrowser style={{borderRadius: '8px'}} demo={true}></DeepChatBrowser>
</ComponentContainerMethods>

<Tabs>
<TabItem value="js" label="Code">

```html
chatElementRef.getMessages();
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `clearMessages` {#clearMessages}

- Type: (`isReset?: boolean`) => `void`

Clear all messages in the chat. By default - [`introPanel`](/docs/introPanel) and [`introMessage`](/docs/messages#introMessage) are displayed again, however you can pass
a _false_ argument to prevent this.

#### Example

<ComponentContainerMethods propertyName={'clearMessages'} displayResults={false}>
  <DeepChatBrowser
    style={{borderRadius: '8px'}}
    demo={true}
    history={[
      {text: 'What is 2 + 2?', role: 'user'},
      {text: 'The result of 2 + 2 is 4.', role: 'ai'},
      {text: 'Wrong, it is 5.', role: 'user'},
      {text: 'You are correct, the result of 2 + 2 is 5.', role: 'ai'},
    ]}
  ></DeepChatBrowser>
</ComponentContainerMethods>

<Tabs>
<TabItem value="js" label="Code">

```html
chatElementRef.clearMessages();
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `submitUserMessage` {#submitUserMessage}

- Type: ([`message: UserMessage`](#UserMessage)) => `void`

Send a new user message.

#### Example

<ComponentContainerMethods propertyName={'submitUserMessage'} displayResults={false} args={[{text: 'User message'}]}>
  <DeepChatBrowser style={{borderRadius: '8px'}} demo={true}></DeepChatBrowser>
</ComponentContainerMethods>

<Tabs>
<TabItem value="js" label="Code">

```html
chatElementRef.submitUserMessage({text: "User message"});
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

#### `UserMessage` {#UserMessage}

- Type: \{`text?: string`, [`files?: File[] | FileList`](https://developer.mozilla.org/en-US/docs/Web/API/FileList), `custom`: `any`\}

`text` is the text content of the outgoing message. <br />
`files` is an array containing files that are going to be part of the outgoing message. This can either be an array
of [`File`](https://developer.mozilla.org/en-US/docs/Web/API/File_API/Using_files_from_web_applications) objects or a [`FileList`](https://developer.mozilla.org/en-US/docs/Web/API/FileList)
object which typically comes from a [file input](https://developer.mozilla.org/en-US/docs/Web/API/File_API/Using_files_from_web_applications). <br />
`custom` encapsulates any custom data. <br />

#### Files Example

<Tabs>
<TabItem value="js" label="Code">

```text
// html
<input type="file" id="files-input" accept="image/png, image/jpeg" />

// javascript
const filesInput = document.getElementById('files-input');
filesInput.onchange = (event) => {
  chatElement.submitUserMessage({files: event.target.files});
};
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `addMessage` {#addMessage}

- Type: ([`message: Response`](/docs/connect#Response), `isUpdate?: boolean`) => `void`

Add a message to the chat. <br />
`message` is an object containing message details. <br />
`isUpdate` identifies whether the message should be treated as new - e.g. should [`onMessage`](/docs/events#onMessage) event
and [`textToSpeech`](/docs/speech#textToSpeech) be triggered.

#### Example

<ComponentContainerMethods propertyName={'addMessage'} displayResults={false} args={[{text: `New message`, role: 'user'}]}>
  <DeepChatBrowser style={{borderRadius: '8px'}} demo={true}></DeepChatBrowser>
</ComponentContainerMethods>

<Tabs>
<TabItem value="js" label="Code">

```javascript
chatElementRef.addMessage({text: `New message`, role: 'user'});
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

:::tip
This can be used to add [suggestion buttons](/docs/messages/HTML#moreExamples) after message.
:::

<LineBreak></LineBreak>

### `updateMessage` {#updateMessage}

- Type: ([`message: MessageContent`](/docs/messages#MessageContent), `index: number`) => `void`

Updates an existing message in the chat. <br />
`message` is an object containing new message details. If the previous version of message contains multiple properties such as `text` and `html`, this will overwrite them both. <br />
`index` is the index number of the message to be updated from the top. If you are not sure about the index, use [`getMessages`](#getMessages) to find the index of your target message.

#### Example

<ComponentContainerMethods
  propertyName={'updateMessage'}
  displayResults={false}
  args={[{text: `New text.`, role: 'user'}, 0]}
>
  <DeepChatBrowser
    style={{borderRadius: '8px'}}
    demo={true}
    history={[{text: 'Message to be updated.', role: 'user'}]}
  ></DeepChatBrowser>
</ComponentContainerMethods>

<Tabs>
<TabItem value="js" label="Code">

```javascript
chatElementRef.updateMessage({text: `New text.`}, 0);
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `scrollToBottom` {#scrollToBottom}

- Type: `() => void`

Moves the chat's scrollbar to the bottom.

#### Example

<ComponentContainerMethods propertyName={'scrollToBottom'} displayResults={false}>
  <DeepChatBrowser
    style={{borderRadius: '8px'}}
    history={[
      {
        role: 'user',
        text: 'So close it has no boundaries. A blinking cursor pulses in the electric darkness like a heart coursing with phosphorous light, burning beneath the derma of black-neon glass. A PHONE begins to RING, we hear it as though we were making the call.  The cursor continues to throb, relentlessly patient, until... Hello? Data now slashes across the screen, information flashing faster than we read.',
      },
      {
        role: 'ai',
        text: "Scroll to the top and click the 'Call Method' button below the chat.",
      },
    ]}
    demo={true}
  ></DeepChatBrowser>
</ComponentContainerMethods>

<Tabs>
<TabItem value="js" label="Code">

```html
chatElementRef.scrollToBottom();
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `focusInput` {#focusInput}

- Type: `() => void`

Focuses the cursor on the text input.

#### Example

<ComponentContainerMethods propertyName={'focusInput'} displayResults={false}>
  <DeepChatBrowser style={{borderRadius: '8px'}} demo={true}></DeepChatBrowser>
</ComponentContainerMethods>

<Tabs>
<TabItem value="js" label="Code">

```html
chatElementRef.focusInput();
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `setPlaceholderText` {#setPlaceholderText}

- Type: (`text: string`) => `void`

Dynamically change the text input placeholder. <br />

#### Example

<ComponentContainerMethods propertyName={'setPlaceholderText'} args={['New placeholder text']} displayResults={false}>
  <DeepChatBrowser style={{borderRadius: '8px'}} demo={true}></DeepChatBrowser>
</ComponentContainerMethods>

<Tabs>
<TabItem value="js" label="Code">

```html
chatElementRef.setPlaceholderText("New placeholder text");
```

</TabItem>
</Tabs>

:::info
Default placeholder text should be set using the `placeholder` property in [`textInput`](/docs/styles/#textInput).
:::

<LineBreak></LineBreak>

### `disableSubmitButton` {#disableSubmitButton}

- Type: (`override?: boolean`) => `void`

Disables the submit button. To re-enable automatic state handling - call this method again with a boolean argument of _false_.

#### Example

<ComponentContainerMethods propertyName={'disableSubmitButton'} displayResults={false}>
  <DeepChatBrowser style={{borderRadius: '8px'}} demo={true}></DeepChatBrowser>
</ComponentContainerMethods>

<Tabs>
<TabItem value="js" label="Code">

```html
chatElementRef.disableSubmitButton();
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `refreshMessages` {#refreshMessages}

- Type: `() => void`

If your `text` messages contain [Code](/docs/messages/#code-messages) and you are using the [`higlight.js`](https://www.npmjs.com/package/highlight.js?activeTab=readme) module to highlight them
(as per [external module](/examples/externalModules) guidelines), sometimes the module may load after the messages have been rendered, leaving the code without a highlight. In such instances, you can use this
method to highlight the code with the loaded module.

#### Example

<ComponentContainerHighlightMethod displayResults={false}>
  <DeepChatBrowser
    style={{borderRadius: '8px'}}
    history={[
      {
        text: '```java\nwhile (i < 5) {\n console.log("hi");\n i+= 1;\n}\n```',
        role: 'ai',
      },
    ]}
    messageStyles={{
      default: {
        shared: {
          bubble: {maxWidth: '270px'},
        },
      },
    }}
    demo={true}
  ></DeepChatBrowser>
</ComponentContainerHighlightMethod>

<Tabs>
<TabItem value="js" label="Code">

```html
chatElementRef.refreshMessages();
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>



================================================
FILE: website/docs/docs/modes.mdx
================================================
---
sidebar_position: 13
---

# Modes

### `demo` {#demo}

- Type: `true` | \{ <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `response?:` [`Response`](/docs/connect#Response) | ([`message: MessageContent`](/docs/messages/#MessageContent)) => [`Response`](/docs/connect#Response), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`displayErrors?: DisplayErrors`](#DisplayErrors), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`displayLoading?: DemoLoading`](#DemoLoading), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `displayFileAttachmentContainer?: boolean` <br />
  }\}

This is used by default to demonstrate the component's capabilities without connecting to any APIs. <br />
Set this to _true_ or define an object with properties to remove the initial setup guidance message. <br />
`response` is used to override the default demo response with a custom one. It can either be a [`Response`](/docs/connect#Response) object or a function that returns
a [`Response`](/docs/connect#Response) object. <br />
The following properties are used to toggle elements to showcase their design without making any user actions: <br />
`displayErrors` is used to display error messages. <br />
`displayLoading` is used to display various loading spinners. <br />
`displayFileAttachmentContainer` is used to display the element that encapsulates all of the files to be sent on the next message. <br />

import ComponentContainer from '@site/src/components/table/componentContainer';
import DeepChatBrowser from '@site/src/components/table/deepChatBrowser';
import LineBreak from '@site/src/components/markdown/lineBreak';
import BrowserOnly from '@docusaurus/BrowserOnly';
import TabItem from '@theme/TabItem';
import Tabs from '@theme/Tabs';

<BrowserOnly>{() => require('@site/src/components/nav/autoNavToggle').readdAutoNavShadowToggle()}</BrowserOnly>

#### Base Example

<ComponentContainer>
  <DeepChatBrowser style={{borderRadius: '8px'}} demo={true}></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat demo="true"></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat demo="true" style="border-radius: 8px"></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

#### Custom Response Example

<ComponentContainer>
  <DeepChatBrowser
    style={{borderRadius: '8px'}}
    introMessage={{text: 'Rock, Paper, Scissors! Make your guess and see who wins!'}}
    demo={{
      response: (message) => {
        const options = ['rock', 'paper', 'scissors'];
        const userOption = message.text?.toLocaleLowerCase();
        const aiOption = options[Math.floor(Math.random() * 3)];
        let response = `I guessed ${aiOption}. `;
        if (userOption === aiOption) response += "It's a draw.";
        else if (userOption === 'rock') response += aiOption === 'paper' ? 'I win!' : 'You win!';
        else if (userOption === 'paper') response += aiOption === 'scissors' ? 'I win!' : 'You win!';
        else if (userOption === 'scissors') response += aiOption === 'rock' ? 'I win!' : 'You win!';
        else response = 'Guess either Rock, Paper or Scissors';
        return {text: response};
      },
    }}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```javascript
chatElementRef.demo = {
  response: (message) => {
    const options = ['rock', 'paper', 'scissors'];
    const userOption = message.text?.toLocaleLowerCase();
    const aiOption = options[Math.floor(Math.random() * 3)];
    let response = `I guessed ${aiOption}. `;
    if (userOption === aiOption) response += 'Draw';
    else if (userOption === 'rock') response += aiOption === 'paper' ? 'I win!' : 'You win!';
    else if (userOption === 'paper') response += aiOption === 'scissors' ? 'I win!' : 'You win!';
    else if (userOption === 'scissors') response += aiOption === 'rock' ? 'I win!' : 'You win!';
    else response = 'Guess either Rock, Paper or Scissors';
    return {text: response};
  },
};
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  id="chat-element"
  introMessage='{"text": "Rock, Paper, Scissors! Make your guess and see who wins!"}'
  style="border-radius: 8px"
></deep-chat>

<script>
// ...other code
const chatElementRef = document.getElementById('chat-element');
chatElementRef.demo = {
  response: (message) => {
    const options = ['rock', 'paper', 'scissors'];
    const userOption = message.text?.toLocaleLowerCase();
    const aiOption = options[Math.floor(Math.random() * 3)];
    let response = `I guessed ${aiOption}. `;
    if (userOption === aiOption) response += 'Draw';
    else if (userOption === 'rock') response += aiOption === 'paper' ? 'I win!' : 'You win!';
    else if (userOption === 'paper') response += aiOption === 'scissors' ? 'I win!' : 'You win!';
    else if (userOption === 'scissors') response += aiOption === 'rock' ? 'I win!' : 'You win!';
    else response = 'Guess either Rock, Paper or Scissors';
    return {text: response};
  },
};
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `focusMode` {#focusMode}

- Type: `true` | \{`scroll?: boolean`, `fade?:` `true` | `number`\}

This mode displays the latest user request and AI response messages only, providing a modern AI chatbot experience.
You can enable it by using the boolean `true` or an object with any of the following: <br />
`scroll` toggles a scrolling animation when the user posts a new message. <br />
`fade` toggles a fade effect when the user posts a new message.
It can be enabled with a boolean `true` or a `number` which is the milliseconds duration of the fade. <br />

#### Basic Example

<ComponentContainer>
  <DeepChatBrowser style={{borderRadius: '8px'}} focusMode={true} demo={true}></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat focusMode="true"></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat focusMode="true" demo="true" style="border-radius: 8px"></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

#### Scroll Example

<ComponentContainer>
  <DeepChatBrowser style={{borderRadius: '8px'}} focusMode={{scroll: true}} demo={true}></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat focusMode='{"scroll": true}'></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat focusMode='{"scroll": true}' demo="true" style="border-radius: 8px"></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

## Types

### `DemoErrors` {#DemoErrors}

- Type: \{`default?: boolean`, `service?: boolean`, `speechToText?: boolean`\}

Display various error messages. This is mainly used to showcase the override capabilities in [`errorMessages`](/docs/messages#errorMessages). <br />
`default` displays a default component error. <br />
`service` is an API error. <br />
`speechToText` is a speech to text issue error.

<ComponentContainer>
  <DeepChatBrowser style={{borderRadius: '8px'}} demo={{displayErrors: {service: true}}}></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat demo='{"displayErrors": {"service": true}}'></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat demo='{"displayErrors": {"service": true}}' style="border-radius: 8px"></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `DemoLoading` {#DemoLoading}

- Type: \{ <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `message?: boolean`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `history?:` \{`full?: boolean`, `small?: boolean`} <br />
  \}

Display various loading spinners. <br />
`message` is a loading spinner inside a message bubble. <br />
`history` is a loading spinner that is displayed when messages are being loading via [`loadHistory`](/docs/interceptors#loadHistory).
`full` is a spinner that covers the entire chat message window on the initial load. `small` is displayed when there are messages
already present inside the chat. If `full` is set to _true_ and messages are added, the chat will automatically display the `small`
spinner. <br />

<ComponentContainer>
  <DeepChatBrowser
    style={{borderRadius: '8px'}}
    demo={{displayLoading: {message: true, history: {small: true}}}}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat demo='{"displayLoading": {"message": true, "history": {"small": true}}}'></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat demo='{"displayLoading": {"message": true, "history": {"small": true}}}' style="border-radius: 8px"></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>



================================================
FILE: website/docs/docs/speech.mdx
================================================
---
sidebar_position: 7
---

import azureCredentials from '/img/azure-credentials.png';

# Speech

<video className="documentation-video" controls>
  <source src="https://github.com/OvidijusParsiunas/deep-chat/assets/18709577/e103a42e-b3a7-4449-b9db-73fed6d7876e" />
</video>

### `textToSpeech` {#textToSpeech}

- Type: `true` | \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; `voiceName?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `lang?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `pitch?: number`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `rate?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `volume?: number` <br />
  \}

When the chat receives a new text message - your device will automatically read it out. <br />
`voiceName` is the name of the voice that will be used to read out the incoming message. Please note that different Operating Systems
support different voices. Use the following code snippet to see the available voices for your device: `window.speechSynthesis.getVoices()` <br />
`lang` is used to set the utterance language. See the following [`QA`](https://stackoverflow.com/questions/23733537/what-are-the-supported-languages-for-web-speech-api-in-html5) for the available options. <br />
`pitch` sets the pitch at which the utterance will be spoken at. <br />
`volume` set the volume at which the utterance will be spoken at.

:::info
Text to speech is using [`SpeechSynthesis`](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis) Web API
which is supported differently across different devices.
:::

:::info
Your mouse needs to be focused on the browser window for this to work.
:::

import ComponentContainer from '@site/src/components/table/componentContainer';
import DeepChatBrowser from '@site/src/components/table/deepChatBrowser';
import LineBreak from '@site/src/components/markdown/lineBreak';
import BrowserOnly from '@docusaurus/BrowserOnly';
import TabItem from '@theme/TabItem';
import Tabs from '@theme/Tabs';

<BrowserOnly>{() => require('@site/src/components/nav/autoNavToggle').readdAutoNavShadowToggle()}</BrowserOnly>
<BrowserOnly>{() => require('@site/src/components/externalModules/speechToElement').checkWebSpeechSupport()}</BrowserOnly>

#### Example

<ComponentContainer>
  <DeepChatBrowser
    demo={true}
    introMessage={{text: 'Send a message to hear the response.'}}
    style={{borderRadius: '8px'}}
    textToSpeech={{volume: 0.9}}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat textToSpeech='{"volume": 0.9}'></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  textToSpeech='{"volume": 0.9}'
  introMessage='{"text": "Send a message to hear the response."}'
  style="border-radius: 8px"
  demo="true"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `speechToText` {#speechToText}

- Type: `true` | \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; `webSpeech?:` `true` | [`WebSpeechOptions`](#WebSpeechOptions), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`azure?: AzureOptions`](#AzureOptions), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`textColor?: TextColor`](#TextColor), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `displayInterimResults?: boolean`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `translations?: {[key: string]: string}`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`commands?: Commands`](#Commands), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`button?: ButtonStyles`](#ButtonStyles), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `stopAfterSubmit?: boolean`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`submitAfterSilence?: SubmitAfterSilence`](#SubmitAfterSilence), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`events?: SpeechEvents`](#SpeechEvents) <br />
  \}

- Default: _\{webSpeech: true, stopAfterSubmit: true\}_

Transcribe your voice into text and control chat with commands.<br />
`webSpeech` utilises [`Web Speech API`](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API/Using_the_Web_Speech_API) to transcribe your speech. <br />
`azure` utilises [`Azure Cognitive Speech Services API`](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-to-text) to transcribe your speech. <br />
`textColor` is used to set the color of interim and final results text. <br />
`displayInterimResults` controls whether interim results are displayed. <br />
`translations` is a case-sensitive one-to-one mapping of words that will automatically be translated to others. <br />
`commands` is used to set the phrases that will trigger various chat functionality. <br />
`button` defines the styling used for the microphone button. <br />
`stopAfterSubmit` is used to toggle whether the recording stops after a message has been submitted. <br />
`submitAfterSilence` configures automated message submit functionality when the user stops speaking. <br />
`events` is used to listen to speech functionality events. <br />

<div className="web-speech-not-supported-error">
  <a href="https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API/Using_the_Web_Speech_API">Web Speech API</a> is
  not supported in this browser.
</div>

#### Example

<ComponentContainer>
  <DeepChatBrowser
    demo={true}
    introMessage={{text: 'Click the microphone to start transcribing your speech.'}}
    style={{borderRadius: '8px'}}
    speechToText={{
      webSpeech: true,
      translations: {hello: 'goodbye', Hello: 'Goodbye'},
      commands: {resume: 'resume', settings: {commandMode: 'hello'}},
      button: {position: 'outside-left'},
    }}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  speechToText='{
    "webSpeech": true,
    "translations": {"hello": "goodbye", "Hello": "Goodbye"},
    "commands": {"resume": "resume", "settings": {"commandMode": "hello"}},
    "button": {"position": "outside-left"}
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  speechToText='{
    "webSpeech": true,
    "translations": {"hello": "goodbye", "Hello": "Goodbye"},
    "commands": {"resume": "resume", "settings": {"commandMode": "hello"}},
    "button": {"position": "outside-left"}
  }'
  introMessage='{"text": "Click the microphone to start transcribing your speech."}'
  style="border-radius: 8px"
  demo="true"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

:::info
If the [`microphone`](/docs/files#microphone) recorder is set - this will not be enabled. <br />
:::

:::info
Speech to text functionality is provided by the [`Speech To Element`](https://github.com/OvidijusParsiunas/speech-to-element) library.
:::

:::caution
Support for `webSpeech` varies across different browsers, please check the [`Can I use`](https://caniuse.com/?search=Web%20Speech%20API) Speech Recognition API section.
(The yellow bars indicate that it is supported)
:::

<LineBreak></LineBreak>

## Types

Object types for [`speechToText`](#speechToText):

### `WebSpeechOptions` {#WebSpeechOptions}

- Type: \{`language?: string`\}

`language` is used to set the recognition language. See the following [`QA`](https://stackoverflow.com/questions/23733537/what-are-the-supported-languages-for-web-speech-api-in-html5)
for the full list.

<div className="web-speech-not-supported-error">
  <a href="https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API/Using_the_Web_Speech_API">Web Speech API</a> is
  not supported in this browser.
</div>

#### Example

<ComponentContainer>
  <DeepChatBrowser
    demo={true}
    introMessage={{text: 'Click the microphone to start transcribing your speech.'}}
    style={{borderRadius: '8px'}}
    speechToText={{webSpeech: {language: 'en-US'}}}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat speechToText='{"webSpeech": {"language": "en-US"}}'></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  speechToText='{"webSpeech": {"language": "en-US"}}'
  introMessage='{"text": "Click the microphone to start transcribing your speech."}'
  style="border-radius: 8px"
  demo="true"
></deep-chat>
```

</TabItem>
</Tabs>

:::note
This service stops after a brief period of silence due to limitations in its API and not Deep Chat.
:::

<LineBreak></LineBreak>

### `AzureOptions` {#AzureOptions}

- Type: \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; `region: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `retrieveToken?: () => Promise<string>`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `subscriptionKey?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `token?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `language?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `autoLanguage?:` \{`type?: "AtStart" | "Continuous"`, `languages: string[]`\}, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `endpointId?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `deviceId?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `stopAfterSilenceMs?: number` <br />
  \}

- Default: _\{stopAfterSilenceMs: 25000 (25 seconds)\}_

This object requires `region` and either `retrieveToken`, `subscriptionKey` or the `token` properties to be defined with it: <br />
`region` is the location/region of your Azure speech resource. <br />
`retrieveToken` is a function used to retrieve a new token for the Azure speech resource. It is the recommended property to use as
it can retrieve the token from a secure server that will hide your credentials. Check out the [retrieval example](#retrieve-token-example) below
and [starter server templates](https://github.com/OvidijusParsiunas/speech-to-element/tree/main/examples). <br />
`subscriptionKey` is the subscription key for the Azure speech resource. <br />
`token` is a temporary token for the Azure speech resource. <br />
`language` is a BCP-47 string value to denote the recognition language. You can find the full
list [here](https://docs.microsoft.com/azure/cognitive-services/speech-service/supported-languages). <br />
`autoLanguage` is used to configure automatic [language identification](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-identification?tabs=once&pivots=programming-language-javascript)
based on a list of candidate `languages`. `type` defines if the language can be identified in the first 5 seconds (`"AtStart"`) or any time (`"Continuous"`). <br />
`endpointId` is the id of a customized speech model. <br />
`deviceId` is the id of specific media device. More info [here](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/how-to-select-audio-input-devices#audio-device-ids-in-javascript). <br />
`stopAfterSilenceMs` is the milliseconds of silence required for the microphone to automatically turn off. <br />

:::info
To use the Azure Speech To Text service - please add the [`Speech SDK`](https://www.npmjs.com/package/microsoft-cognitiveservices-speech-sdk) to your project.
See [EXAMPLES](/examples/externalModules).
:::

#### Example

<ComponentContainer>
  <DeepChatBrowser
    demo={true}
    introMessage={{text: "Azure Speech To Text can't be used in this website as you need to set your credentials."}}
    style={{borderRadius: '8px'}}
    errorMessages={{
      overrides: {
        speechToText: 'Azure Speech To Text can not be used in this website as you need to set your credentials.',
      },
    }}
    speechToText={{
      azure: {
        subscriptionKey: 'key',
        region: 'region',
        language: 'en-US',
        stopAfterSilenceMs: 5000,
      },
    }}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  speechToText='{
    "azure": {
      "subscriptionKey": "resource-key",
      "region": "resource-region",
      "language": "en-US",
      "stopAfterSilenceMs": 5000
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  speechToText='{
    "azure": {
      "subscriptionKey": "resource-key",
      "region": "resource-region",
      "language": "en-US",
      "stopAfterSilenceMs": 5000
    }
  }'
  errorMessages='{
    "overrides": {"speechToText": "Azure Speech To Text can not be used in this website as you need to set your credentials."}
  }'
  introMessage='{"text": "Azure Speech To Text can't be used in this website as you need to set your credentials."}'
  style="border-radius: 8px"
  demo="true"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

Location of speech service credentials in Azure Portal:

<LineBreak></LineBreak>

<img src={azureCredentials} />

<LineBreak></LineBreak>

:::caution
The `subscriptionKey` and `token` properties should only be used for local/prototyping/demo purposes ONLY. When you are ready to deploy your application,
please switch to using the `retrieveToken` property. Check out the example below and [starter server templates](https://github.com/OvidijusParsiunas/speech-to-element/tree/main/examples).

:::

<LineBreak></LineBreak>

#### Retrieve token example

<ComponentContainer>
  <DeepChatBrowser
    demo={true}
    introMessage={{text: "Azure Speech To Text can't be used in this website as you need to set your region."}}
    errorMessages={{
      overrides: {
        speechToText: 'Azure Speech To Text can not be used in this website as you need to set your region.',
      },
    }}
    style={{borderRadius: '8px'}}
    speechToText={{
      azure: {
        region: 'resource-region',
        retrieveToken: async () => {
          return fetch('http://localhost:8080/token')
            .then((res) => res.text())
            .then((token) => token)
            .catch((error) => console.error('error'));
        },
      },
    }}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Code">

```javascript
speechToText.speechToText = {
  region: 'resource-region',
  retrieveToken: async () => {
    return fetch('http://localhost:8080/token')
      .then((res) => res.text())
      .then((token) => token);
  },
};
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `TextColor` {#TextColor}

- Type: \{`interim?: string`, `final?: string`\}

This object is used to set the color of `interim` and `final` results text. <br />

#### Example

<ComponentContainer>
  <DeepChatBrowser
    demo={true}
    introMessage={{text: 'Click the microphone to start transcribing your speech.'}}
    style={{borderRadius: '8px'}}
    speechToText={{textColor: {interim: 'green', final: 'blue'}}}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat speechToText='{"textColor": {"interim": "green", "final": "blue"}}'></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  speechToText='{"textColor": {"interim": "green", "final": "blue"}}'
  introMessage='{"text": "Click the microphone to start transcribing your speech."}'
  style="border-radius: 8px"
  demo="true"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `Commands` {#Commands}

- Type: \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; `stop?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `pause?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `resume?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `removeAllText?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `submit?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `commandMode?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `settings?:` \{`substrings?: boolean`, `caseSensitive?: boolean`\} <br />
  \}

- Default: _\{settings: \{substrings: true, caseSensitive: false\}\}_

This object is used to set the phrases which will control chat functionality via speech. <br />
`stop` is used to stop the speech service. <br />
`pause` will temporarily stop the transcription and will re-enable it after the phrase for `resume` is spoken. <br />
`removeAllText` is used to remove all input text. <br />
`submit` will send the current input text. <br />
`commandMode` is a phrase that is used to activate the command mode which will not transcribe any text and will wait for a command to be executed. To leave
the command mode - you can use the phrase for the `resume` command. <br />
`substrings` is used to toggle whether command phrases can be part of spoken words or if they are whole words. E.g. when this is set to _true_ and your command phrase is _"stop"_ -
when you say "stopping" the command will be executed. However if it is set to _false_ - the command will only be executed if you say "stop". <br />
`caseSensitive` is used to toggle if command phrases are case sensitive. E.g. if this is set to _true_ and your command phrase is _"stop"_ - when the service recognizes
your speech as "Stop" it will not execute your command. On the other hand if it is set to _false_ it will execute.

#### Example

<ComponentContainer>
  <DeepChatBrowser
    demo={true}
    introMessage={{
      text: 'Click the microphone to start transcribing your speech. Command mode activation phrase is `command`.',
    }}
    style={{borderRadius: '8px'}}
    speechToText={{
      commands: {
        stop: 'stop',
        pause: 'pause',
        resume: 'resume',
        removeAllText: 'remove text',
        submit: 'submit',
        commandMode: 'command',
        settings: {
          substrings: true,
          caseSensitive: false,
        },
      },
    }}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  speechToText='{
    "commands": {
      "stop": "stop",
      "pause": "pause",
      "resume": "resume",
      "removeAllText": "remove text",
      "submit": "submit",
      "commandMode": "command",
      "settings": {
        "substrings": true,
        "caseSensitive": false
  }}}'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  speechToText='{
    "commands": {
      "stop": "stop",
      "pause": "pause",
      "resume": "resume",
      "removeAllText": "remove text",
      "submit": "submit",
      "commandMode": "command",
      "settings": {
        "substrings": true,
        "caseSensitive": false
  }}}'
  introMessage='{"text": "Click the microphone to start transcribing your speech. Command mode activation phrase is `command`."}'
  style="border-radius: 8px"
  demo="true"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `ButtonStyles` {#ButtonStyles}

- Type: \{[`commandMode?: ButtonStyles`](/docs/styles/buttons#ButtonStyles), [`MicrophoneStyles`](/docs/styles/buttons#MicrophoneStyles)\}

This object is used to define the styling for the microphone button. <br />
It contains the same properties as the [`MicrophoneStyles`](/docs/styles/buttons#MicrophoneStyles) object
and an additional `commandMode` property which sets the button styling when the [`command mode`](#Commands) is activated. <br />

#### Example

<ComponentContainer>
  <DeepChatBrowser
    demo={true}
    introMessage={{
      text: 'Click the microphone to start transcribing your speech. Command mode activation phrase is `command`.',
    }}
    style={{borderRadius: '8px'}}
    speechToText={{
      button: {
        commandMode: {
          svg: {
            styles: {
              default: {
                filter:
                  'brightness(0) saturate(100%) invert(70%) sepia(70%) saturate(4438%) hue-rotate(170deg) brightness(92%) contrast(98%)',
              },
            },
          },
        },
        active: {
          svg: {
            styles: {
              default: {
                filter:
                  'brightness(0) saturate(100%) invert(10%) sepia(97%) saturate(7495%) hue-rotate(0deg) brightness(101%) contrast(107%)',
              },
            },
          },
        },
        default: {
          svg: {
            styles: {
              default: {
                filter:
                  'brightness(0) saturate(100%) invert(77%) sepia(9%) saturate(7093%) hue-rotate(32deg) brightness(99%) contrast(83%)',
              },
            },
          },
        },
      },
      commands: {
        removeAllText: 'remove text',
        commandMode: 'command',
      },
    }}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  speechToText='{
    "button": {
      "commandMode": {
        "svg": {
          "styles": {
            "default": {
              "filter":
                "brightness(0) saturate(100%) invert(70%) sepia(70%) saturate(4438%) hue-rotate(170deg) brightness(92%) contrast(98%)"
      }}}},
      "active": {
        "svg": {
          "styles": {
            "default": {
              "filter":
                "brightness(0) saturate(100%) invert(10%) sepia(97%) saturate(7495%) hue-rotate(0deg) brightness(101%) contrast(107%))"
      }}}},
      "default": {
        "svg": {
          "styles": {
            "default": {
              "filter":
                "brightness(0) saturate(100%) invert(77%) sepia(9%) saturate(7093%) hue-rotate(32deg) brightness(99%) contrast(83%)"
    }}}}},
    "commands": {
      "removeAllText": "remove text",
      "commandMode": "command"
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  speechToText='{
    "button": {
      "commandMode": {
        "svg": {
          "styles": {
            "default": {
              "filter":
                "brightness(0) saturate(100%) invert(70%) sepia(70%) saturate(4438%) hue-rotate(170deg) brightness(92%) contrast(98%)"
      }}}},
      "active": {
        "svg": {
          "styles": {
            "default": {
              "filter":
                "brightness(0) saturate(100%) invert(10%) sepia(97%) saturate(7495%) hue-rotate(0deg) brightness(101%) contrast(107%)"
      }}}},
      "default": {
        "svg": {
          "styles": {
            "default": {
              "filter":
                "brightness(0) saturate(100%) invert(77%) sepia(9%) saturate(7093%) hue-rotate(32deg) brightness(99%) contrast(83%)"
    }}}}},
    "commands": {
      "removeAllText": "remove text",
      "commandMode": "command"
    }
  }'
  introMessage='{"text": "Click the microphone to start transcribing your speech. Command mode activation phrase is `command`."}'
  style="border-radius: 8px"
  demo="true"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

:::tip
You can use the [`CSSFilterConverter`](https://cssfilterconverter.com/) tool to generate filter values for the icon color.
:::

<LineBreak></LineBreak>

### `SubmitAfterSilence` {#SubmitAfterSilence}

- Type: `true` | `number`

Automatically submit the input message after a period of silence. <br />
This property accepts the value of _true_ or a number which represents the milliseconds of silence
required to wait before a messaget is submitted. If this is set to _true_ the default milliseconds is _2000_. <br />

#### Example

<ComponentContainer>
  <DeepChatBrowser
    demo={true}
    introMessage={{text: 'Click the microphone to start transcribing your speech.'}}
    style={{borderRadius: '8px'}}
    speechToText={{submitAfterSilence: {ms: 3000, stop: false}}}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat speechToText='{"submitAfterSilence": 3000}'></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  speechToText='{"submitAfterSilence": 3000}'
  introMessage='{"text": "Click the microphone to start transcribing your speech."}'
  style="border-radius: 8px"
  demo="true"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

:::caution
When using the default [`Web Speech API`](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API/Using_the_Web_Speech_API) - the recording will
automatically stop after 5-7 seconds of silence and will ignore _custom_ timeouts that are higher than this.
:::

<LineBreak></LineBreak>

### `SpeechEvents` {#SpeechEvents}

- Type: \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; `onStart?:` `() => void`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `onStop?:` `() => void`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `onResult?:` `(text: string, isFinal: boolean) => void`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `onPreResult?:` `(text: string, isFinal: boolean) => void`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `onCommandModeTrigger?:` `(isStart: boolean) => void`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `onPauseTrigger?:` `(isStart: boolean) => void` <br />
  \}

This object contains multiple properties that can be attached with functions that will be
triggered when the corresponding event occurs. <br />
`onStart` is triggered when speech recording starts. <br />
`onStop` is triggered when speech recording stops. <br />
`onResult` is triggered when the latest speech segment is transcribed and inserted into chat's text input. <br />
`onPreResult` is triggered when the latest speech segment is transcribed and before it is inserted into chat's text input. This is
particularly useful for executing [commands](#Commands). <br />
`onCommandModeTrigger` is triggered when command mode is initiated and stopped. <br />
`onPauseTrigger` is triggered when the pause command is initiated and then stopped via the resume command. <br />

#### Example

<ComponentContainer>
  <DeepChatBrowser
    demo={true}
    introMessage={{
      text: "Check your browser's developer console to view the results",
    }}
    style={{borderRadius: '8px'}}
    speechToText={{
      events: {
        onResult: (text, isFinal) => {
          console.log(text, isFinal);
        },
      },
    }}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Function">

```js
chatElementRef.speechToText = {
  events: {
    onResult: (text, isFinal) => { console.log(text, isFinal); };
  }
}
```

</TabItem>

</Tabs>

## Demo

This is the example used in the [demo video](https://github.com/OvidijusParsiunas/deep-chat/assets/18709577/e103a42e-b3a7-4449-b9db-73fed6d7876e). When replicating - make sure
to add the Speech SDK to your project and add your resource properties.

<ComponentContainer innerDisplay={'flex'}>
  <DeepChatBrowser
    demo={true}
    style={{marginRight: '30px'}}
    textToSpeech={true}
    speechToText={{
      azure: {
        subscriptionKey: 'resource-key',
        region: 'resource-region',
      },
      commands: {
        submit: 'submit',
        stop: 'stop',
        removeAllText: 'remove all text',
        pause: 'pause',
        resume: 'continue',
      },
    }}
    errorMessages={{
      overrides: {
        speechToText: 'Azure Speech To Text can not be used in this website as you need to set your region.',
      },
    }}
  ></DeepChatBrowser>
  <DeepChatBrowser
    demo={true}
    textToSpeech={true}
    speechToText={{
      azure: {
        subscriptionKey: 'resource-key',
        region: 'resource-region',
      },
      commands: {
        submit: 'submit',
        stop: 'stop',
        removeAllText: 'remove',
        pause: 'pause',
        resume: 'continue',
        commandMode: 'belfast',
      },
    }}
    errorMessages={{
      overrides: {
        speechToText: 'Azure Speech To Text can not be used in this website as you need to set your region.',
      },
    }}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<div style="display: flex">
  <deep-chat
    speechToText='{
      "azure": {
        "subscriptionKey": "resource-key",
        "region": "resource-region"
      },
      "commands": {
        "stop": "stop",
        "pause": "pause",
        "resume": "resume",
        "removeAllText": "remove text",
        "submit": "submit",
        "commandMode": "command"
    }}'
    errorMessages='{
      "overrides": {"speechToText": "Azure Speech To Text can not be used in this website as you need to set your credentials."}
    }'
    style="margin-right: 30px"
    demo="true"
  ></deep-chat>
  <deep-chat
    speechToText='{
      "commands": {
        "azure": {
          "subscriptionKey": "resource-key",
          "region": "resource-region"
        },
        "stop": "stop",
        "pause": "pause",
        "resume": "resume",
        "removeAllText": "remove text",
        "submit": "submit",
        "commandMode": "command"
    }}'
    errorMessages='{
      "overrides": {"speechToText": "Azure Speech To Text can not be used in this website as you need to set your credentials."}
    }'
    demo="true"
  ></deep-chat>
</div>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>



================================================
FILE: website/docs/docs/webModel.mdx
================================================
---
sidebar_position: 4
---

# Web Model

Run a chat model entirely on your browser. No need to connect to any service.

<a href="https://youtu.be/ilzVAooE4HI">
  <img src={YoutubeLogo} className={'youtube-icon'} />
  Video demo
</a>

### Setup

See the [External Modules](/examples/externalModules) section on how to integrate the [`deep-chat-web-llm`](https://github.com/OvidijusParsiunas/web-llm) module into your project.
Then proceed with using the [`webModel`](#webModel) property:

### `webModel` {#webModel}

- Type: `true` | \{ <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`model?: string`](https://github.com/OvidijusParsiunas/deep-chat/blob/10db3f4931d7fefff81e1c93d38a9a9809701113/component/src/types/webModel/webModel.ts#L1), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `instruction?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`urls?: WebModelUrls`](#WebModelUrls), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`load?: WebModelLoad`](#WebModelLoad), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`introMessage?: WebModelIntro`](#WebModelIntro), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`worker?: Worker`](#Worker) <br />
  \}
- Default: _\{model: "Llama-2-7b-chat-hf-q4f32_1"\}_

Set this to _true_ or define an object with any of the following properties: <br />
`model` is the name of the model to be used. See [full list](https://github.com/OvidijusParsiunas/deep-chat/blob/10db3f4931d7fefff81e1c93d38a9a9809701113/component/src/types/webModel/webModel.ts#L1). <br />
`instruction` directs how the model should respond. <br />
`urls` defines the endpoint to retrieve the web model assets. <br />
`load` defines how and when the model is loaded. <br />
`introMessage` is the configuration for the introductory web model message. <br />
`worker` is a [Web Worker](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Using_web_workers) that can enhance the rendering performance. [Example](#Worker). <br />

import ContainersKeyToggle from '@site/src/components/table/containersKeyToggle';
import ComponentContainer from '@site/src/components/table/componentContainer';
import DeepChatBrowser from '@site/src/components/table/deepChatBrowser';
import LineBreak from '@site/src/components/markdown/lineBreak';
import BrowserOnly from '@docusaurus/BrowserOnly';
import YoutubeLogo from '/img/youtube.png';
import TabItem from '@theme/TabItem';
import Tabs from '@theme/Tabs';

<BrowserOnly>{() => require('@site/src/components/nav/autoNavToggle').readdAutoNavShadowToggle()}</BrowserOnly>
<BrowserOnly>{() => require('@site/src/components/externalModules/externalModules').importWebLLM()}</BrowserOnly>

#### Example

<ComponentContainer>
  <DeepChatBrowser style={{borderRadius: '8px'}} webModel={true}></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat webModel="true"></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat webModel="true" style="border-radius: 8px"></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

## Types

Object types for [`webModel`](#webModel):

### `WebModelUrls` {#WebModelUrls}

- Type: \{`model?: string`, `wasm?: string`\}

Deep Chat uses the [`webModelConfig.ts`](https://github.com/OvidijusParsiunas/deep-chat/blob/284bc845de8bcefe8ef36b2ee1b79079e6978593/component/src/webModel/webModelConfig.ts) file to determine where the `model` and the `wasm` files will be downloaded from.
You can overwite the links to your prefered locations like your own server.

#### Example

<ComponentContainer>
  <DeepChatBrowser
    style={{borderRadius: '8px'}}
    webModel={{urls: {model: 'http://localhost:8080/model-file', wasm: 'http://localhost:8080/wasm-file'}}}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  webModel='{
    "urls": {
      "model": "http://localhost:8080/model-file",
      "wasm": "http://localhost:8080/wasm-file"
  }}'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  webModel='{
    "urls": {
      "model": "http://localhost:8080/model-file",
      "wasm": "http://localhost:8080/wasm-file"
  }}'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `WebModelLoad` {#WebModelLoad}

- Type: \{`onInit?: boolean`, `onMessage?: boolean`, `clearCache?: boolean`, `skipCache?: boolean`\}

This is an object that is used to define the web model loading/downloading behaviour: <br />
`onInit` will start loading the model as soon as the component is rendered. <br />
`onMessage` will start loading the model when the user submits a message (or clicks the _Start_ button). <br />
`clearCache` is used to remove all the cached web model files in the browser and replace them with new ones. <br />
`skipCache` will not use the browser cache. This is useful for trying out multiple models without overfilling the cache. <br />

#### Example

<ComponentContainer>
  <DeepChatBrowser style={{borderRadius: '8px'}} webModel={{load: {onMessage: true}}}></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat webModel='{"load": {"onMessage": true}}'></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat webModel='{"load": {"onMessage": true}}' style="border-radius: 8px"></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `WebModelIntro` {#WebModelIntro}

- Type: \{ <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `displayed?: boolean`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `autoScroll?: boolean` <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `removeAfterLoad?: boolean`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `removeAfterMessage?: boolean`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `initialHtml?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `downloadClass?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `uploadClass?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `fileInputClass?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `afterLoadHtml?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `exportFilesClass?: string` <br />
  \}
- Default: _\{displayed: true, autoScroll: true\}_

This is an object that controls the introductory web model message behaviour: <br />
`displayed` is used to toggle whether the message is visible. <br />
`autoScroll` toggles whether the chat automatically scrolls to the intro message. <br />
`removeAfterLoad` removes the message after the model files have successfully loaded. <br />
`removeAfterMessage` removes the message after the model files have loaded and the user types a message. <br />
`initialHtml` is a string that contains html used for the initial message. <br />
`downloadClass` is the name of the class used for the button that downloads the model files. <br />
`uploadClass` is the name of the class used for the button that upload model files. <br />
`fileInputClass` is the name of the class used for the hidden file input element that toggles the file upload functionality. <br />
`afterLoadHtml` is a string that contains html used for the message displayed after the model has been uploaded. <br />
`exportFilesClass` is the name of the class used for the button that exports the model files. <br />

#### Initial Example

<ComponentContainer>
  <DeepChatBrowser
    style={{borderRadius: '8px'}}
    webModel={{
      introMessage: {
        initialHtml: `<button class="start">Start</button>
          <button class="upload">Upload Files</button>
          <input type="file" class="input" hidden multiple />`,
        downloadClass: 'start',
        uploadClass: 'upload',
        fileInputClass: 'input',
      },
    }}
    htmlClassUtilities={{upload: {styles: {default: {marginLeft: '4px'}}}}}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```js
// using JavaScript for a simplified example

chatElementRef.webModel = {
  introMessage: {
    initialHtml: `<button class="start">Start</button> <button class="files">Files</button> <input type="file" class="input" hidden multiple />`,
    downloadClass: 'start',
    uploadClass: 'files',
    fileInputClass: 'input',
  },
};
```

</TabItem>
<TabItem value="py" label="Full code">

```js
// using JavaScript for a simplified example

chatElementRef.webModel = {
  introMessage: {
    initialHtml: `<button class="start">Start</button> <button class="files">Files</button> <input type="file" class="input" hidden multiple />`,
    downloadClass: 'start',
    uploadClass: 'files',
    fileInputClass: 'input',
  },
};

chatElementRef.htmlClassUtilities = {upload: {styles: {default: {marginLeft: '4px'}}}};
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

#### After Load Example

Need to first download/upload the model.

<ComponentContainer>
  <DeepChatBrowser
    style={{borderRadius: '8px'}}
    webModel={{
      afterLoadHtml: {
        initialHtml: `Finished loading the model! <br /> <button class="export">Export Files</button>`,
        exportFilesClass: 'export',
      },
    }}
    htmlClassUtilities={{export: {styles: {default: {marginTop: '8px'}}}}}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```js
// using JavaScript for a simplified example

chatElementRef.webModel = {
  afterLoadHtml: {
    initialHtml: `Finished loading the model! <br /> <button class="export">Export Files</button>`,
    exportFilesClass: 'export',
  },
};
```

</TabItem>
<TabItem value="py" label="Full code">

```js
// using JavaScript for a simplified example

chatElementRef.webModel = {
  afterLoadHtml: {
    initialHtml: `Finished loading the model! <br /> <button class="export">Export Files</button>`,
    exportFilesClass: 'export',
  },
};

chatElementRef.htmlClassUtilities = {export: {styles: {default: {marginTop: '8px'}}}};
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

:::tip
Element styles can be customized using the [`htmlClassUtilities`](/docs/messages/HTML#htmlClassUtilities) property.
:::

### `Worker` {#Worker}

- Type: [Web Worker](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Using_web_workers)

This is a reference to a [Web Worker](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Using_web_workers) that is used to process chat responses in another
thread and improves browser rendering performance. To note, this does not allow model files to be uploaded or exported.

To define its property value, please use the following: <br />
`worker: new Worker(new URL('./worker.js', import.meta.url), {type: 'module'})` <br /> <br />
Create a [`worker.js`](https://github.com/OvidijusParsiunas/deep-chat/blob/f0c0c5b1ae8d44a3eb51ab1d46345e338e4a23b4/website/docs/docs/worker.js) (or `worker.ts`) file in the same folder - which contains the following code:

```
import {ChatWorkerHandler, ChatModule} from 'deep-chat-web-llm';

const chat = new ChatModule();
const handler = new ChatWorkerHandler(chat);
self.onmessage = (msg) => {
  handler.onmessage(msg);
};
```

#### Example

<BrowserOnly>
  {() => (
    <ComponentContainer>
      <DeepChatBrowser
        style={{borderRadius: '8px'}}
        webModel={{worker: new Worker(new URL('./worker.js', import.meta.url), {type: 'module'})}}
      ></DeepChatBrowser>
    </ComponentContainer>
  )}
</BrowserOnly>

<Tabs>
<TabItem value="js" label="Sample code">

```javascript
chatElementRef.webModel = {
  worker: new Worker(new URL('./worker.js', import.meta.url), {type: 'module'}),
};
```

</TabItem>
<TabItem value="py" label="Full code">

```javascript
// worker.js file
import {ChatWorkerHandler, ChatModule} from 'deep-chat-web-llm';

const chat = new ChatModule();
const handler = new ChatWorkerHandler(chat);
self.onmessage = (msg) => {
  handler.onmessage(msg);
};

// component code
chatElementRef.webModel = {
  worker: new Worker(new URL('./worker.js', import.meta.url), {type: 'module'}),
};
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

## Troubleshooting

If the chat displays an error, we recommend trying any of the following options:

- Download the latest version of [Chrome browser](https://www.google.co.uk/chrome/)
- Download the [Canary version of Chrome browser](https://www.google.com/chrome/canary/)
- Run the following command in the browser console: _--enable-dawn-features=allow_unsafe_apis_

If you are using an SSR related framework such as [NextJs](https://nextjs.org/) or [SvelteKit](https://kit.svelte.dev/) and get the following error:
`unhandledRejection: Error [ReferenceError]: require is not defined in ES module scope...`

- Use the following syntax to import [`deep-chat-web-llm`](https://github.com/OvidijusParsiunas/web-llm) instead:

```
if (typeof window !== 'undefined') {
  import('deep-chat-web-llm').then((module) => {
    window.webLLM = module;
  });
}
```

If you are still experiencing issues, please see [**github issues**](https://github.com/OvidijusParsiunas/deep-chat/issues) or create
a [**new issue ticket**](https://github.com/OvidijusParsiunas/deep-chat/issues/new) and we will look into
it as soon as possible.

## Thankyou

The [`deep-chat-web-llm`](https://github.com/OvidijusParsiunas/web-llm) module is a fork based on the [`mlc-ai/web-llm`](https://github.com/mlc-ai/web-llm) repository.
Make sure to check them out and give them a star!



================================================
FILE: website/docs/docs/directConnection/AssemblyAI.mdx
================================================
---
sidebar_position: 6
---

# AssemblyAI

import assemblyAILogo from '/img/assemblyAILogo.png';

# <img src={assemblyAILogo} width="38" style={{float: 'left', marginTop: '10px', marginRight: '10px'}} /><span className="direct-service-title">AssemblyAI</span>

Properties used to connect to [AssemblyAI](https://www.assemblyai.com/).

### `assemblyAI` {#assemblyAI}

- Type: `true` | {`audio?: true`}
- Default: _\{audio: true\}_

import ContainersKeyToggle from '@site/src/components/table/containersKeyToggle';
import ComponentContainer from '@site/src/components/table/componentContainer';
import DeepChatBrowser from '@site/src/components/table/deepChatBrowser';
import LineBreak from '@site/src/components/markdown/lineBreak';
import BrowserOnly from '@docusaurus/BrowserOnly';
import TabItem from '@theme/TabItem';
import Tabs from '@theme/Tabs';

<BrowserOnly>{() => require('@site/src/components/nav/autoNavToggle').readdAutoNavShadowToggle()}</BrowserOnly>

Connect to Assembly AI's [`speech recognition`](https://www.assemblyai.com/docs/Models/speech_recognition) API to transcribe your audio.

#### Example

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        assemblyAI: {
          key: 'placeholder key',
          audio: true,
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        assemblyAI: {
          audio: true,
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "assemblyAI": {
      "key": "placeholder key",
      "audio": true
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "assemblyAI": {
      "key": "placeholder key",
      "audio": true
    }
  }'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>



================================================
FILE: website/docs/docs/directConnection/Azure.mdx
================================================
---
sidebar_position: 5
---

# Azure

import azureLogo from '/img/azureLogo.png';

# <img src={azureLogo} width="48" style={{float: 'left', marginTop: '8px', marginRight: '10px'}} /><span className="direct-service-title">Azure</span>

Properties used to connect to [Azure Cognitive Services](https://learn.microsoft.com/en-gb/azure/cognitive-services/).

### `azure` {#azure}

- Type: \{ <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`textToSpeech?: TextToSpeech`](#TextToSpeech), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`speechToText?: SpeechToText`](#SpeechToText), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`summarization?: Summarization`](#Summarization), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`translation?: Translation`](#Translation),<br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`openAI?: OpenAI`](#OpenAI)<br />
  \}

import ContainersKeyToggle from '@site/src/components/table/containersKeyToggle';
import ComponentContainer from '@site/src/components/table/componentContainer';
import DeepChatBrowser from '@site/src/components/table/deepChatBrowser';
import LineBreak from '@site/src/components/markdown/lineBreak';
import BrowserOnly from '@docusaurus/BrowserOnly';
import TabItem from '@theme/TabItem';
import Tabs from '@theme/Tabs';

<BrowserOnly>{() => require('@site/src/components/nav/autoNavToggle').readdAutoNavShadowToggle()}</BrowserOnly>

## Service Types

### `TextToSpeech` {#TextToSpeech}

- Type: \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; `region: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `lang?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `name?: string` <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `gender?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `outputFormat?: string` <br />
  \}

- Default: _\{lang: "en-US", name: "en-US-JennyNeural", gender: "Female", outputFormat: "audio-16khz-128kbitrate-mono-mp3"\}_

Connect to Azure's [`text to speech`](https://learn.microsoft.com/en-GB/azure/cognitive-services/speech-service/rest-text-to-speech?tabs=streaming#convert-text-to-speech) API. <br />
`region` is a required string property to denote the region of your speech service, e.g. _"eastus"_. <br />
`lang` is the locale (BCP-47) string code for the language of the audio output. See [here](https://learn.microsoft.com/en-GB/azure/cognitive-services/speech-service/language-support?tabs=tts) for available options. <br />
`name` is the name of the voice used for the audio output. See [here](https://learn.microsoft.com/en-GB/azure/cognitive-services/speech-service/language-support?tabs=tts) for available options. <br />
`gender` is the gender of the audio output voice. E.g. _"Female"_ or _"Male"_. <br />
`outputFormat` is the output audio format. See [here](https://learn.microsoft.com/en-GB/azure/cognitive-services/speech-service/rest-text-to-speech?tabs=streaming#audio-outputs) for available options. <br />

#### Example

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        azure: {
          key: 'placeholder key',
          textToSpeech: {region: 'eastus'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        azure: {
          textToSpeech: {region: 'eastus'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "azure": {
      "key": "placeholder key",
      "textToSpeech": {"region": "eastus"}
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "azure": {
      "key": "placeholder key",
      "textToSpeech": {"region": "eastus"}
    }
  }'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `SpeechToText` {#SpeechToText}

- Type: \{`region: string`, `lang?: string`\}
- Default: _\{lang: "en-US"\}_

Connect to Azure's [`speech to text`](https://learn.microsoft.com/en-gb/azure/cognitive-services/speech-service/rest-speech-to-text) API. <br />
`region` is a required string property to denote the region of your speech service, e.g. _"eastus"_. <br />
`lang` is the locale (BCP-47) string code for the language of the input output. See [here](https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support?tabs=stt) for available options. <br />

#### Example

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        azure: {
          key: 'placeholder key',
          speechToText: {region: 'eastus'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        azure: {
          speechToText: {region: 'eastus'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "azure": {
      "key": "placeholder key",
      "speechToText": {"region": "eastus"}
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "azure": {
      "key": "placeholder key",
      "speechToText": {"region": "eastus"}
    }
  }'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `Summarization` {#Summarization}

- Type: \{`endpoint: string`, `language?: string`\}
- Default: _\{language: "en"\}_

Connect to Azure's [`summarization`](https://learn.microsoft.com/en-us/azure/cognitive-services/language-service/summarization/overview?tabs=document-summarization) API. Please read [here](https://learn.microsoft.com/en-us/azure/cognitive-services/language-service/summarization/quickstart?tabs=document-summarization%2Cwindows&pivots=rest-api) how to generate a language service. <br />
`endpoint` is the full endpoint for your generated language service. <br />
`language` is a [BCP 47 language tag](https://en.wikipedia.org/wiki/IETF_language_tag#:~:text=An%20IETF%20BCP%2047%20language,the%20IANA%20Language%20Subtag%20Registry.) for the language of your text. <br />

#### Example

<ComponentContainer>
  <DeepChatBrowser
    style={{borderRadius: '8px'}}
    directConnection={{
      azure: {
        key: 'placeholder name',
        summarization: {endpoint: 'https://placeholderresource.cognitiveservices.azure.com'},
      },
    }}
  ></DeepChatBrowser>
</ComponentContainer>

:::caution
Cannot input a test key as user's language service `endpoint` is required.
:::

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "azure": {
      "key": "placeholder key",
      "summarization": {"endpoint": "https://placeholderresource.cognitiveservices.azure.com"}
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "azure": {
      "key": "placeholder key",
      "summarization": {"endpoint": "https://placeholderresource.cognitiveservices.azure.com"}
    }
  }'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `Translation` {#Translation}

- Type: \{`region?: string`, `language?: string`\}
- Default: _\{language: "es"\}_

Connect to Azure's [`translation`](https://learn.microsoft.com/en-gb/azure/cognitive-services/translator/reference/v3-0-reference) API. <br />
`region` is the region of your translator resource. This is optional if your resource is global. <br />
`language` is the [BCP 47 language tag](https://en.wikipedia.org/wiki/IETF_language_tag#:~:text=An%20IETF%20BCP%2047%20language,the%20IANA%20Language%20Subtag%20Registry.) for the language you are translating to from English. <br />

#### Example

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        azure: {
          key: 'placeholder key',
          translation: {region: 'eastus', language: 'ja'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        azure: {
          translation: {region: 'eastus', language: 'ja'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "azure": {
      "key": "placeholder key",
      "translation": {"region": "eastus", "language": "ja"}
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "azure": {
      "key": "placeholder key",
      "translation": {"region": "eastus", "language": "ja"}
    }
  }'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `OpenAI` {#OpenAI}

- Type: \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; `urlDetails:` \{`endpoint: string`, `version: string`, `deploymentId: string`\}, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `chat?:` [`OpenAIChat`](/docs/directConnection/OpenAI/#Chat) & [`AzureDataSources`](#AzureDataSources), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`assistant?: OpenAIAssistant`](/docs/directConnection/OpenAI/#Assistant) <br />
  \}

Connect to the [`Azure OpenAI's`](https://platform.openai.com/docs/api-reference/chat) API: <br />
`urlDetails` is used to define the [_url parameters_](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#uri-parameters) that will be used to connect to Azure.
`endpoint` is a _url_ string for your OpenAI resource, `version` is the API version to be used and `deploymentId` is the deployment id of the model. <br />
`chat` defines whether to connect to the [Chat Completions](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/chatgpt) API.
It uses [OpenAI Chat](/docs/directConnection/OpenAI/#Chat) and [AzureDataSources](#AzureDataSources) types. <br />
`assistant` defines whether to connect to the [Assistant](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/assistant) API.
It uses the same type as the [OpenAI Assistant](/docs/directConnection/OpenAI/#Assistant) property. <br />

#### Example

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "azure": {
      "key": "placeholder key",
      "openAI": {
        "urlDetails": {
          "endpoint": "https://your-endpoint.com",
          "version": "2024-10-21",
          "deploymentId": "123123"
        },
        "chat": true
      }
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "azure": {
      "key": "placeholder key",
      "openAI": {
        "urlDetails": {
          "endpoint": "https://your-endpoint.com",
          "version": "2024-10-21",
          "deploymentId": "123123"
        },
        "chat": true
      }
    }
  }'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `AzureDataSources` {#AzureDataSources}

- Type: \{`data_sources?`: [\{`type: string`, `parameters?: object`\}]\}

The configuration entries for Azure OpenAI On Your Data, more information can be found [here](https://learn.microsoft.com/en-gb/azure/ai-services/openai/references/on-your-data?tabs=python#request-body). <br />
Currently only one object in the array is allowed. <br />
`type` is the data source type. <br />
`parameters` is the configuration required to connect to the data source. <br />

#### Example

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "azure": {
      "key": "placeholder key",
      "openAI": {
        "urlDetails": {
          "endpoint": "https://your-endpoint.com",
          "version": "2024-10-21",
          "deploymentId": "123123"
        },
        "chat": {
          "data_sources": [
            {
              "type": "azure_search",
              "parameters": {
                "endpoint": "endpoint",
                "index_name": "vector-14848022002",
                "authentication": {
                  "type": "system_assigned_managed_identity"
              }}}
          ]
        }}}}'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "azure": {
      "key": "placeholder key",
      "openAI": {
        "urlDetails": {
          "endpoint": "https://your-endpoint.com",
          "version": "2024-10-21",
          "deploymentId": "123123"
        },
        "chat": {
          "data_sources": [
            {
              "type": "azure_search",
              "parameters": {
                "endpoint": "endpoint",
                "index_name": "vector-14848022002",
                "authentication": {
                  "type": "system_assigned_managed_identity"
              }}}
          ]
        }}}}'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>



================================================
FILE: website/docs/docs/directConnection/Cohere.mdx
================================================
---
sidebar_position: 4
---

# Cohere

import cohereLogo from '/img/cohereLogo.png';

# <img src={cohereLogo} width="60" style={{float: 'left'}} /><span className="direct-service-title">Cohere</span>

Properties used to connect to [Cohere](https://docs.cohere.com/docs).

### `cohere` {#cohere}

- Type: \{[`chat?: Chat`](#Chat), [`textGeneration?: TextGeneration`](#TextGeneration), [`summarization?: Summarization`](#Summarization)\}
- Default: _\{chat: true\}_

import ContainersKeyToggle from '@site/src/components/table/containersKeyToggle';
import ComponentContainer from '@site/src/components/table/componentContainer';
import DeepChatBrowser from '@site/src/components/table/deepChatBrowser';
import LineBreak from '@site/src/components/markdown/lineBreak';
import BrowserOnly from '@docusaurus/BrowserOnly';
import TabItem from '@theme/TabItem';
import Tabs from '@theme/Tabs';

<BrowserOnly>{() => require('@site/src/components/nav/autoNavToggle').readdAutoNavShadowToggle()}</BrowserOnly>

## Service Types

### `Chat` {#Chat}

- Type: `true` | \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; `model?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `temperature?: number`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `prompt_truncation?:` `"AUTO"` | `"OFF"`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `connectors?:` `{id: string}[]`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `documents?:` `{title: string; snippet: string}[]` <br />
  \}

Connect to Cohere's [`chat`](https://docs.cohere.com/reference/chat) API. You can set this property to _true_ or configure it using an object: <br />
`model` is the name of the model used to generate text. <br />
`temperature` is the degree of the response randomness. <br />
`prompt_truncation` dictates how the prompt will be constructed. Default is _"OFF"_ which uses all resources. _"AUTO"_ drops some chat history and documents
to construct a prompt that fits within the model's context length limit. <br />
`connectors` is an array of objects that define custom connectors. <br />
`documents` is an array of objects that define relevant documents which the model can use to enrich its reply.
See [Document Mode](https://docs.cohere.com/docs/retrieval-augmented-generation-rag#document-mode) for more info. <br />

#### Example

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        cohere: {
          key: 'placeholder key',
          chat: {temperature: 1},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        cohere: {
          chat: {temperature: 1},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "cohere": {
      "key": "placeholder key",
      "chat": {"temperature": 1}
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "cohere": {
      "key": "placeholder key",
      "chat": {"temperature": 1}
    }
  }'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `TextGeneration` {#TextGeneration}

- Type: `true` | \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; `model?:` `"command"` | `"base"` | `"base-light"`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `max_tokens?: number`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `temperature?: number`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `k?: number`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `p?: number`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `frequency_penalty?: number`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `presence_penalty?: number`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `end_sequences?: string[]`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `stop_sequences?: string[]`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `logit_bias?: {[string]: number}`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `truncate?:` `"NONE"` | `"START"` | `"END"`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `preset?: string` <br />
  \}

- Default: _\{max_tokens: 1000\}_

Connect to Cohere's [`text generation`](https://docs.cohere.com/reference/generate) API. You can set this property to _true_ or configure it using an object: <br />
`model` is the name of the model used to generate text. <br />
`max_tokens` denotes the number of tokens to predict per generation. <br />
`temperature` is a non-negative float that tunes the degree of randomness in generation. Lower temperatures mean less random generations. <br />
`k` ensures only the top k most likely tokens are considered for generation at each step. The maximum value is 500. <br />
`p` is the probability (between 0.0 and 1.0) which ensures that only the most likely tokens - with total probability mass of p are considered for generation at each step. If both `k` and `p` are set, `p` acts after `k`. <br />
`frequency_penalty` (between 0.0 and 1.0) can be used to reduce repetitiveness of generated tokens. The higher the value, the stronger a penalty is applied to previously present tokens, proportional to how many times they have already appeared in the prompt or prior generation. <br />
`presence_penalty` (between 0.0 and 1.0) can be used to reduce repetitiveness of generated tokens. Similar to frequency\*penalty, except that this penalty is applied equally to all tokens that have already appeared, regardless of their exact frequencies. <br />
`end_sequences` is used to cut the generated text at the beginning of the earliest occurence of an end sequence of strings. <br />
`stop_sequences` is used to cut the generated text at the end of the earliest occurence of stop sequence strings. <br />
`logit_bias` is used to prevent the model from generating unwanted tokens or to incentivize it to include desired ibes. The format is _\{token_id: bias\}_ where bias is a float between -10 and 10. Tokens can be obtained from text using [Tokenize](https://docs.cohere.com/reference/tokenize). E.g. if the value _\{"11": -10\}_ is provided, the model will be very unlikely to include the token _11_ ("\n", the newline character) anywhere in the generated text. In contrast _\{"11": 10\}_ will result in generations that nearly only contain that token. <br />
`truncate` is used to specify how the API will handle inputs longer than the maximum token length. Passing _"START"_ will discard the start of the input. _"END"_ will discard the end of the input. _"NONE"_ will throw an error when the input exceeds the maximum input token length. <br />
`preset` is a combination of parameters, such as prompt, temperature etc. Create presets in the [Cohere Playground](https://dashboard.cohere.com/playground/generate). <br />

#### Example

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        cohere: {
          key: 'placeholder key',
          textGeneration: {model: 'command'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        cohere: {
          textGeneration: {model: 'command'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "cohere": {
      "key": "placeholder key",
      "textGeneration": {"model": "command"}
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "cohere": {
      "key": "placeholder key",
      "textGeneration": {"model": "command"}
    }
  }'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `Summarization` {#Summarization}

- Type: `true` | \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; `model?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `length?`: `"auto"` | `"short"` | `"medium"` | `"long"`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `format?:` `"auto"` | `"paragraph"` | `"bullets"`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `extractiveness?:` `"auto"` | `"low"` | `"medium"` | `"high"`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `temperature?: number`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `additional_command?: string` <br />
  \}

Connect to Cohere's [`summarize`](https://docs.cohere.com/reference/summarize-2) API. You can set this property to _true_ or configure it using an object: <br />
`model` is the name of the model used to generate a summary. <br />
`length` indicates the approximate length of the summary. _"auto"_ chooses the best option based on the input text. <br />
`format` indicates the style in which the summary will be delivered - in a free form paragraph or in bullet points. <br />
`extractiveness` controls how close to the original text the summary is. _"high"_ extractiveness summaries will lean towards reusing sentences verbatim, while _"low"_ extractiveness summaries will tend to paraphrase more. <br />
`temperature` (from 0 to 5) controls the randomness of the output. Lower values tend to generate more predictable outputs, while higher values tend to generate more creative outputs. The sweet spot is typically between _0_ and _1_. <br />
`additional_command` is a free-form instruction for modifying how the summaries get generated. Should start with _"Generate a summary \_"_. and end with Eg. _"focusing on the next steps"_ or _"written by Yoda"_. <br />

#### Example

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        cohere: {
          key: 'placeholder key',
          summarization: {model: 'summarize-xlarge'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        cohere: {
          summarization: {model: 'summarize-xlarge'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "cohere": {
      "key": "placeholder key",
      "summarization": {"model": "summarize-xlarge"}
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "cohere": {
      "key": "placeholder key",
      "summarization": {"model": "summarize-xlarge"}
    }
  }'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>



================================================
FILE: website/docs/docs/directConnection/directConnection.mdx
================================================
---
sidebar_position: 3
---

# Direct Connection

Deep Chat is preconfigured to connect to popular AI APIs right out of the box. <br /> Depending on the service you choose component assets
such as buttons and intro panel will automatically be changed to suit the chosen service. Their configuration can still be overwitten manually. <br />

<a href="https://youtu.be/RnGEUJDOTTc">
  <img src={YoutubeLogo} className={'youtube-icon'} />
  Video demo
</a>

<div style={{marginTop: '26px'}}></div>

:::caution
The [`directConnection`](#directConnection) and [`key`](#APIKey) properties are intended to be used for **prototyping purposes ONLY** and should not be
deployed to a public website as their values can be accessed in the browser. Before going live, switch to using the [`connect`](/docs/connect/#connect-1)
property to connect to your server. Read more about this in [`Connect`](../connect) and check [examples](https://deepchat.dev/examples/servers).
:::

### `directConnection` {#directConnection}

- Type: \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; `openAI?:` \{[`OpenAI`](/docs/directConnection/OpenAI#openAI), [`APIKey`](#APIKey)\}, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `huggingFace?:` \{[`HuggingFace`](/docs/directConnection/HuggingFace#huggingFace), [`APIKey`](#APIKey)\}, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `azure?:` \{[`Azure`](/docs/directConnection/Azure#azure), [`APIKey`](#APIKey)\}, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `cohere?:` \{[`Cohere`](/docs/directConnection/Cohere#cohere), [`APIKey`](#APIKey)\}, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `assemblyAI?:` \{[`AssemblyAI`](/docs/directConnection/AssemblyAI#assemblyAI), [`APIKey`](#APIKey)\}
  \}

import ContainersKeyToggle from '@site/src/components/table/containersKeyToggle';
import ComponentContainer from '@site/src/components/table/componentContainer';
import DeepChatBrowser from '@site/src/components/table/deepChatBrowser';
import LineBreak from '@site/src/components/markdown/lineBreak';
import BrowserOnly from '@docusaurus/BrowserOnly';
import YoutubeLogo from '/img/youtube.png';
import TabItem from '@theme/TabItem';
import Tabs from '@theme/Tabs';

<BrowserOnly>{() => require('@site/src/components/nav/autoNavToggle').readdAutoNavShadowToggle()}</BrowserOnly>

## Types

Shared types for the `directConnection` property.

### `APIKey` {#APIKey}

- Type: \{`key?: string`, `validateKeyProperty?: boolean`\}

These object properties are used to load up the chat view without the user having to insert the API key. <br />
`key` is the target service's API key required for authentication. <br />
`validateKeyProperty` is used to validate the value that is set for the `key` property. This will render a loading circle before the chat view
is loaded up during the validation period.

:::caution
This object is intended to be used for **prototyping purposes ONLY** and should not be deployed to an environment as it can be accessed in the browser.
Before going live, use the [`connect`](/docs/connect/#connect-1) property in combination with your own service to safely use your key there.
Read more about this in [`Connect`](../connect) and check [examples](https://deepchat.dev/examples/servers).
:::

<LineBreak></LineBreak>

#### Key Example

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          key: 'placeholder key',
          chat: {system_prompt: 'Assist me with anything you can'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          chat: {system_prompt: 'Assist me with anything you can'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "openAI": {
      "key": "placeholder key",
      "chat": {"system_prompt": "Assist me with anything you can"}
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "openAI": {
      "key": "placeholder key",
      "chat": {"system_prompt": "Assist me with anything you can"}
    }
  }'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

#### Validation Example

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          key: 'placeholder key',
          validateKeyProperty: true,
          chat: {system_prompt: 'Assist me with anything you can'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          validateKeyProperty: true,
          chat: {system_prompt: 'Assist me with anything you can'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "openAI": {
      "key": "placeholder key",
      "validateKeyProperty": true,
      "chat": {"system_prompt": "Assist me with anything you can"}
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "openAI": {
      "key": "placeholder key",
      "validateKeyProperty": true,
      "chat": {"system_prompt": "Assist me with anything you can"}
    }
  }'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>



================================================
FILE: website/docs/docs/directConnection/HuggingFace.mdx
================================================
---
sidebar_position: 2
---

# HuggingFace

import huggingFaceLogo from '/img/huggingFaceLogo.png';

# <img src={huggingFaceLogo} width="60" style={{float: 'left', marginRight: '5px'}} /><span className="direct-service-title">Hugging Face</span>

Properties used to connect to [Hugging Face API](https://huggingface.co/docs/api-inference/index).

### `huggingFace` {#huggingFace}

- Type: \{ <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`conversation?: Conversation`](#Conversation), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`textGeneration?: TextGeneration`](#TextGeneration), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`summarization?: Summarization`](#Summarization), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`translation?: Translation`](#Translation), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`fillMask?: FillMask`](#FillMask), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`questionAnswer?: QuestionAnswer`](#QuestionAnswer), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`audioSpeechRecognition?: AudioSpeechRecognition`](#AudioSpeechRecognition), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`audioClassification?: AudioClassification`](#AudioClassification), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`imageClassification?: ImageClassification`](#ImageClassification) <br />
  \}

- Default: _\{conversation: true\}_

import ContainersKeyToggle from '@site/src/components/table/containersKeyToggle';
import ComponentContainer from '@site/src/components/table/componentContainer';
import DeepChatBrowser from '@site/src/components/table/deepChatBrowser';
import LineBreak from '@site/src/components/markdown/lineBreak';
import BrowserOnly from '@docusaurus/BrowserOnly';
import TabItem from '@theme/TabItem';
import Tabs from '@theme/Tabs';

<BrowserOnly>{() => require('@site/src/components/nav/autoNavToggle').readdAutoNavShadowToggle()}</BrowserOnly>

## Service Types

### `Conversation` {#Conversation}

- Type: `true` | \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; `model?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `parameters?:` \{ <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `min_length?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `max_length?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `top_k?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `top_p?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `temperature?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `repetition_penalty?: string`\}, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `options?:` \{`use_cache?: boolean`\} <br />
  \}

- Default: _\{model: "facebook/blenderbot-400M-distill", options: \{use_cache: true\}\}_

Connect to Hugging Face [`Conversational`](https://huggingface.co/docs/api-inference/detailed_parameters#conversational-task) API. <br />
`model` is the name of the model used for the task. <br />
`min_length` is the minimum length in tokens of the output summary. <br />
`max_length` is the maximum length in tokens of the output summary. <br />
`top_k` defines the top tokens considered within the sample operation to create new text. <br />
`top_p` is a float to define the tokens that are within the sample operation of text generation. Add tokens in the sample for more probable to least probable until the sum of the probabilities is greater than top \* p. <br />
`temperature` is a float (ranging from _0.0_ to _100.0_) temperature of the sampling operation. 1 means regular sampling, _0_ means always take the highest score, _100.0_ is getting closer to uniform probability. <br />
`repetition_penalty` is a float (ranging from _0.0_ to _100.0_) that controls where a token is used more within generation the more it is penalized to not be picked in successive generation passes. <br />
`use_cache` is used to speed up requests by using the inference API cache.

#### Example

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        huggingFace: {
          key: 'placeholder key',
          conversation: {model: 'facebook/blenderbot-400M-distill', parameters: {temperature: 1}},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        huggingFace: {
          conversation: {model: 'facebook/blenderbot-400M-distill', parameters: {temperature: 1}},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "huggingFace": {
      "key": "placeholder key",
      "conversation": {"model": "facebook/blenderbot-400M-distill", "parameters": {"temperature": 1}}
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "huggingFace": {
      "key": "placeholder key",
      "conversation": {"model": "facebook/blenderbot-400M-distill", "parameters": {"temperature": 1}}
    }
  }'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `TextGeneration` {#TextGeneration}

- Type: `true` | \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; `model?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `parameters?:` \{ <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `top_k?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `top_p?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `temperature?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `repetition_penalty?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `max_new_tokens?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `do_sample?: boolean`\}, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `options?:` \{`use_cache?: boolean`\} <br />
  \}

- Default: _\{model: "gpt2", options: \{use_cache: true\}\}_

Connect to Hugging Face [`Text Generation`](https://huggingface.co/docs/api-inference/detailed_parameters#text-generation-task) API. <br />
`model` is the name of the model used for the task. <br />
`top_k` defines the top tokens considered within the sample operation to create new text. <br />
`top_p` is a float to define the tokens that are within the sample operation of text generation. Add tokens in the sample for more probable to least probable until the sum of the probabilities is greater than top \* p. <br />
`temperature` is a float (ranging from _0.0_ to _100.0_) temperature of the sampling operation. 1 means regular sampling, _0_ means always take the highest score, _100.0_ is getting closer to uniform probability. <br />
`repetition_penalty` is a float (ranging from _0.0_ to _100.0_) that controls where a token is used more within generation the more it is penalized to not be picked in successive generation passes. <br />
`max_new_tokens` is an integer (ranging from _0_ to _250_) amount of new tokens to be generated by the response. <br />
`do_sample` controls whether or not to use sampling. If `false` it uses greedy decoding sampling. <br />
`use_cache` is used to speed up requests by using the inference API cache.

#### Example

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        huggingFace: {
          key: 'placeholder key',
          textGeneration: {model: 'gpt2', parameters: {temperature: 1}},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        huggingFace: {
          textGeneration: {model: 'gpt2', parameters: {temperature: 1}},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "huggingFace": {
      "key": "placeholder key",
      "textGeneration": {"model": "gpt2", "parameters": {"temperature": 1}}
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "huggingFace": {
      "key": "placeholder key",
      "textGeneration": {"model": "gpt2", "parameters": {"temperature": 1}}
    }
  }'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `Summarization` {#Summarization}

- Type: `true` | \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; `model?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `parameters?:` \{ <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `min_length?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `max_length?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `top_k?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `top_p?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `temperature?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `repetition_penalty?: string`\}, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `options?:` \{`use_cache?: boolean`\} <br />
  \}

- Default: _\{model: "facebook/bart-large-cnn", options: \{use_cache: true\}\}_

Connect to Hugging Face [`Summarization`](https://huggingface.co/docs/api-inference/detailed_parameters#summarization-task) API. <br />
`model` is the name of the model used for the task. <br />
`min_length` is the minimum length in tokens of the output summary. <br />
`max_length` is the maximum length in tokens of the output summary. <br />
`top_k` defines the top tokens considered within the sample operation to create new text. <br />
`top_p` is a float to define the tokens that are within the sample operation of text generation. Add tokens in the sample for more probable to least probable until the sum of the probabilities is greater than top \* p. <br />
`temperature` is a float (ranging from _0.0_ to _100.0_) temperature of the sampling operation. 1 means regular sampling, _0_ means always take the highest score, _100.0_ is getting closer to uniform probability. <br />
`repetition_penalty` is a float (ranging from _0.0_ to _100.0_) that controls where a token is used more within generation the more it is penalized to not be picked in successive generation passes. <br />
`use_cache` is used to speed up requests by using the inference API cache.

#### Example

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        huggingFace: {
          key: 'placeholder key',
          summarization: {model: 'facebook/bart-large-cnn', parameters: {temperature: 1}},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        huggingFace: {
          summarization: {model: 'facebook/bart-large-cnn', parameters: {temperature: 1}},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "huggingFace": {
      "key": "placeholder key",
      "summarization": {"model": "facebook/bart-large-cnn", "parameters": {"temperature": 1}}
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "huggingFace": {
      "key": "placeholder key",
      "summarization": {"model": "facebook/bart-large-cnn", "parameters": {"temperature": 1}}
    }
  }'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `Translation` {#Translation}

- Type: `true` | \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; `model?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `options?:` \{`use_cache?: boolean`\} <br />
  \}

- Default: _\{model: "Helsinki-NLP/opus-tatoeba-en-ja", options: \{use_cache: true\}\}_

Connect to Hugging Face [`Translation`](https://huggingface.co/docs/api-inference/detailed_parameters#translation-task) API. <br />
`model` is the name of the model used for the task. <br />
`use_cache` is used to speed up requests by using the inference API cache.

#### Example

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        huggingFace: {
          key: 'placeholder key',
          translation: {model: 'Helsinki-NLP/opus-tatoeba-en-ja'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        huggingFace: {
          translation: {model: 'Helsinki-NLP/opus-tatoeba-en-ja'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "huggingFace": {
      "key": "placeholder key",
      "translation": {"model": "Helsinki-NLP/opus-tatoeba-en-ja"}
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "huggingFace": {
      "key": "placeholder key",
      "translation": {"model": "Helsinki-NLP/opus-tatoeba-en-ja"}
    }
  }'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `FillMask` {#FillMask}

- Type: `true` | \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; `model?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `options?:` \{`use_cache?: boolean`} <br />
  \}

- Default: _\{model: "bert-base-uncased", options: \{use_cache: true}\}_

Connect to Hugging Face [`Fill Mask`](https://huggingface.co/docs/api-inference/detailed_parameters#fill-mask-task) API. <br />
`model` is the name of the model used for the task. <br />
`use_cache` is used to speed up requests by using the inference API cache.

#### Example

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        huggingFace: {
          key: 'placeholder key',
          fillMask: {model: 'bert-base-uncased'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        huggingFace: {
          fillMask: {model: 'bert-base-uncased'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "huggingFace": {
      "key": "placeholder key",
      "fillMask": {"model": "bert-base-uncased"}
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "huggingFace": {
      "key": "placeholder key",
      "fillMask": {"model": "bert-base-uncased"}
    }
  }'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `QuestionAnswer` {#QuestionAnswer}

- Type: `true` | \{`context: string`, `model?: string`\}
- Default: _\{model: "bert-large-uncased-whole-word-masking-finetuned-squad"\}_

Connect to Hugging Face [`Question Answer`](https://huggingface.co/docs/api-inference/detailed_parameters#question-answering-task) API. <br />
`context` is a string containing details that AI can use to answer the given questions. <br />
`model` is the name of the model used for the task. <br />

#### Example (Ask about labrador looks)

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        huggingFace: {
          key: 'placeholder key',
          questionAnswer: {
            model: 'bert-large-uncased-whole-word-masking-finetuned-squad',
            context:
              'Labrador retrievers are easily recognized by their broad head, drop ears and large, expressive eyes. Two trademarks of the Lab are the thick but fairly short double coat, which is very water repellent, and the well known otter tail. The tail is thick and sturdy and comes off the topline almost straight.',
          },
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        huggingFace: {
          questionAnswer: {
            model: 'bert-large-uncased-whole-word-masking-finetuned-squad',
            context:
              'Labrador retrievers are easily recognized by their broad head, drop ears and large, expressive eyes. Two trademarks of the Lab are the thick but fairly short double coat, which is very water repellent, and the well known otter tail. The tail is thick and sturdy and comes off the topline almost straight.',
          },
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "huggingFace": {
      "key": "placeholder key",
      "questionAnswer": {
        "model": "bert-large-uncased-whole-word-masking-finetuned-squad",
        "context": "Labrador retrievers are easily recognized by their broad head, drop ears and large, expressive eyes. Two trademarks of the Lab are the thick but fairly short double coat, which is very water repellent, and the well known otter tail. The tail is thick and sturdy and comes off the topline almost straight."
        }
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "huggingFace": {
      "key": "placeholder key",
      "questionAnswer": {
        "model": "bert-large-uncased-whole-word-masking-finetuned-squad",
        "context": "Labrador retrievers are easily recognized by their broad head, drop ears and large, expressive eyes. Two trademarks of the Lab are the thick but fairly short double coat, which is very water repellent, and the well known otter tail. The tail is thick and sturdy and comes off the topline almost straight."
        }
    }
  }'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `AudioSpeechRecognition` {#AudioSpeechRecognition}

- Type: `true` | \{`model?: string`\}
- Default: _\{model: "facebook/wav2vec2-large-960h-lv60-self"\}_

Connect to Hugging Face [`Audio Speech Recognition`](https://huggingface.co/docs/api-inference/detailed_parameters#automatic-speech-recognition-task) API. <br />
`model` is the name of the model used for the task. <br />

#### Example

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        huggingFace: {
          key: 'placeholder key',
          audioSpeechRecognition: {model: 'facebook/wav2vec2-large-960h-lv60-self'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        huggingFace: {
          audioSpeechRecognition: {model: 'facebook/wav2vec2-large-960h-lv60-self'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "huggingFace": {
      "key": "placeholder key",
      "huggingFace": {"model": "facebook/wav2vec2-large-960h-lv60-self"}
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "huggingFace": {
      "key": "placeholder key",
      "huggingFace": {"model": "facebook/wav2vec2-large-960h-lv60-self"}
    }
  }'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `AudioClassification` {#AudioClassification}

- Type: `true` | \{`model?: string`\}
- Default: _\{model: "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"\}_

Connect to Hugging Face [`Audio Classification`](https://huggingface.co/docs/api-inference/detailed_parameters#audio-classification-task) API. <br />
`model` is the name of the model used for the task. <br />

#### Example

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        huggingFace: {
          key: 'placeholder key',
          audioClassification: {model: 'ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        huggingFace: {
          audioSpeechRecognition: {model: 'ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "huggingFace": {
      "key": "placeholder key",
      "audioSpeechRecognition": {"model": "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"}
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "huggingFace": {
      "key": "placeholder key",
      "audioSpeechRecognition": {"model": "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"}
    }
  }'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `ImageClassification` {#ImageClassification}

- Type: `true` | \{`model?: string`\}
- Default: _\{model: "google/vit-base-patch16-224"\}_

Connect to Hugging Face [`Image Classification`](https://huggingface.co/docs/api-inference/detailed_parameters#image-classification-task) API. <br />
`model` is the name of the model used for the task. <br />

#### Example

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        huggingFace: {
          key: 'placeholder key',
          imageClassification: {model: 'google/vit-base-patch16-224'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        huggingFace: {
          imageClassification: {model: 'google/vit-base-patch16-224'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "huggingFace": {
      "key": "placeholder key",
      "imageClassification": {"model": "google/vit-base-patch16-224"}
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "huggingFace": {
      "key": "placeholder key",
      "imageClassification": {"model": "google/vit-base-patch16-224"}
    }
  }'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>



================================================
FILE: website/docs/docs/directConnection/StabilityAI.mdx
================================================
---
sidebar_position: 3
---

# StabilityAI

import stabilityAILogo from '/img/stabilityAILogo.png';

# <img src={stabilityAILogo} width="48" style={{float: 'left', marginTop: '5px', marginRight: '6px', marginLeft: '2px'}} /><span className="direct-service-title">StabilityAI</span>

Properties used to connect to [Stability AI](https://platform.stability.ai/).

### `stabilityAI` {#stabilityAI}

- Type: \{ <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`textToImage?: TextToImage`](#TextToImage), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`imageToImage?: ImageToImage`](#ImageToImage), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`imageToImageMasking?: ImageToImageMasking`](#ImageToImageMasking), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`imageToImageUpscale?: ImageToImageUpscale`](#ImageToImageUpscale) <br />
  \}
- Default: _\{textToImage: true\}_

import ContainersKeyToggle from '@site/src/components/table/containersKeyToggle';
import ComponentContainer from '@site/src/components/table/componentContainer';
import DeepChatBrowser from '@site/src/components/table/deepChatBrowser';
import LineBreak from '@site/src/components/markdown/lineBreak';
import BrowserOnly from '@docusaurus/BrowserOnly';
import TabItem from '@theme/TabItem';
import Tabs from '@theme/Tabs';

<BrowserOnly>{() => require('@site/src/components/nav/autoNavToggle').readdAutoNavShadowToggle()}</BrowserOnly>

## Service Types

### `TextToImage` {#TextToImage}

- Type: `true` | \{ [`StabilityAICommon`](#StabilityAICommon), `width?: number`, `height?: number` \}
- Default: _\{engine_id: "stable-diffusion-v1-6", width: 512, height: 512\}_

Connect to Stability AI's [`text-to-image`](https://platform.stability.ai/docs/api-reference#tag/v1generation/operation/textToImage) API. <br />
`StabilityAICommon` properties can be used to set the engine Id and other image parameters. <br />
`width` and `height` is used to set the image dimensions. They must be multiples of _64_ and pass the following: <br />
For 768 engines: 589,824 ≤ _width \* height_ ≤ 1,048,576 and for other engines: 262,144 ≤ _width \* height_ ≤ 1,048,576.<br />

#### Example

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        stabilityAI: {
          key: 'placeholder key',
          textToImage: {engine_id: 'stable-diffusion-v1-6', height: 640, samples: 1},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        stabilityAI: {
          textToImage: {engine_id: 'stable-diffusion-v1-6', height: 640, samples: 1},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "stabilityAI": {
      "key": "placeholder key",
      "textToImage": {"engine_id": "stable-diffusion-v1-6", "height": 640, "samples": 1}
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "stabilityAI": {
      "key": "placeholder key",
      "textToImage": {"engine_id": "stable-diffusion-v1-6", "height": 640, "samples": 1}
    }
  }'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `ImageToImage` {#ImageToImage}

- Type: `true` | \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`StabilityAICommon`](#StabilityAICommon), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `init_image_mode?:` `"image_strength"` | `"step_schedule_*"`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `image_strength?: number`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `step_schedule_start?: number`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `step_schedule_end?: number` <br />
  \}

- Type: \{ <br />
  &nbsp;&nbsp;&nbsp;&nbsp; _engine_id: "stable-diffusion-v1-6"_, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; _init_image_mode: "image_strength"_, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; _image_strength: 0.35_, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; _step_schedule_start: 0.65_, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; _weight: 1_ <br />
  \}

Connect to Stability AI's [`image-to-image`](https://platform.stability.ai/docs/api-reference#tag/v1generation/operation/imageToImage) API. <br />
`StabilityAICommon` properties can be used to set the engine Id and other image parameters. <br />
`init_image_mode` denotes whether the `image_strength` or `step_schedule` properties control the influence of the uploaded image on the new image. <br />
`image_strength` determines how much influence the uploaded image has on the diffusion process. A value close to _1_ will yield an image
very similar to the original, whilst a value closer to _0_ will yield an image that is wildly different. (0 to 1) <br />
`step_schedule_start` and `step_schedule_end` are used to skip a proportion of the start/end of the diffusion steps,
allowing the uploaded image to influence the final generated image. Lower values will result in more influence from the original image, while higher
values will result in more influence from the diffusion steps. (0 to 1)

#### Example

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        stabilityAI: {
          key: 'placeholder key',
          imageToImage: {engine_id: 'stable-diffusion-v1-6', init_image_mode: 'image_strength', samples: 1},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        stabilityAI: {
          imageToImage: {engine_id: 'stable-diffusion-v1-6', init_image_mode: 'image_strength', samples: 1},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "stabilityAI": {
      "key": "placeholder key",
      "imageToImage": {"engine_id": "stable-diffusion-v1-6", "init_image_mode": "image_strength", "samples": 1}
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "stabilityAI": {
      "key": "placeholder key",
      "imageToImage": {"engine_id": "stable-diffusion-v1-6", "width": 1024, "height": 1024, "samples": 1}
    }
  }'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `ImageToImageMasking` {#ImageToImageMasking}

- Type: `true` | \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`StabilityAICommon`](#StabilityAICommon), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `mask_source?:` `"MASK_IMAGE_WHITE"` | `"MASK_IMAGE_BLACK"` | `"INIT_IMAGE_ALPHA"` <br />
  \}

- Default: _\{engine_id: "stable-diffusion-xl-1024-v1-0", mask_source: "MASK_IMAGE_WHITE", weight: 1\}_

Connect to Stability AI's [`image-to-image-masking`](https://platform.stability.ai/docs/api-reference#tag/v1generation/operation/masking) API. <br />
`StabilityAICommon` properties can be used to set the engine Id and other image parameters. <br />
`mask_source` is used to define where the source of the mask is from. _"MASK_IMAGE_WHITE"_ will use the white pixels of the mask image (second image) as the mask,
where white pixels are completely replaced and black pixels are unchanged. _"MASK_IMAGE_BLACK"_ will use the black pixels of the mask image (second image) as the mask,
where black pixels are completely replaced and white pixels are unchanged. _"INIT_IMAGE_ALPHA"_ will use the alpha channel of the uploaded image as the mask,
where fully transparent pixels are completely replaced and fully opaque pixels are unchanged - in this instance the mask image does not need to be uploaded.

#### Example

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        stabilityAI: {
          key: 'placeholder key',
          imageToImageMasking: {mask_source: 'MASK_IMAGE_WHITE', samples: 1},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        stabilityAI: {
          imageToImageMasking: {mask_source: 'MASK_IMAGE_WHITE', samples: 1},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "stabilityAI": {
      "key": "placeholder key",
      "imageToImageMasking": {"mask_source": "MASK_IMAGE_WHITE", "samples": 1}
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "stabilityAI": {
      "key": "placeholder key",
      "imageToImageMasking": {"mask_source": "MASK_IMAGE_WHITE", "samples": 1}
    }
  }'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `ImageToImageUpscale` {#ImageToImageUpscale}

- Type: `true` | \{`engine_id?: string`, `width?: number`, `height?: number`\}
- Default: _\{engine_id: "esrgan-v1-x2plus"\}_

Connect to Stability AI's [`image-to-image-upscale`](https://platform.stability.ai/docs/api-reference#tag/v1generation/operation/upscaleImage) API. <br />
`engine_id` is the engine that will be used to process the image. <br />
`width` and `height` are used to define the _desired_ with of the result image where only EITHER ONE of the two can be set.
Minimum dimension number is 512. <br />

#### Example

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        stabilityAI: {
          key: 'placeholder key',
          imageToImageUpscale: {width: 1000},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        stabilityAI: {
          imageToImageUpscale: {width: 1000},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "stabilityAI": {
      "key": "placeholder key",
      "imageToImageUpscale": {"width": 1000}
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "stabilityAI": {
      "key": "placeholder key",
      "imageToImageUpscale": {"width": 1000}
    }
  }'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

## Shared Types

Types used in [`stabilityAI`](#stabilityAI) properties:

### `StabilityAICommon` {#StabilityAICommon}

- Type: \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; `engine_id?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `samples?: number`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `weight?: number`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `cfg_scale?: number`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `sampler?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `seed?: number`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `steps?: number`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `style_preset?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `clip_guidance_preset?: string` <br />
  \}

- Type: \{ <br />
  &nbsp;&nbsp;&nbsp;&nbsp; _samples: 1_, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; _cfg_scale: 7_, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; _seed: 0_, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; _steps: 50_, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; _clip_guidance_preset: "NONE"_ <br />
  \}

Object that is used to define the target engine and other image processing parameters. <br />
`engine_id` is the identifier for the engine that will be used to process the images. <br />
`samples` is the number of images that will be generated (1 to 10). <br />
`weight` defines how specific to the prompt the generated image should be (0 to 1). <br />
`cfg_scale` defines how strictly the diffusion process should adhere to the prompt (0 to 35). <br />
`sampler` is the sampler that will be used for the diffusion process. If this value is not set - the most appropriate one is automatically selected. <br />
`seed` is the number for the random noise (0 to 4294967295). <br />
`steps` is the number of diffusion steps to run (10 to 150). <br />
`style_preset` guides the image model towards a particular style. <br />
`clip_guidance_preset` is the clip guidance preset. <br />

#### Example

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        stabilityAI: {
          key: 'placeholder key',
          textToImage: {engine_id: 'stable-diffusion-v1-6', weight: 1, style_preset: 'fantasy-art', samples: 2},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        stabilityAI: {
          textToImage: {engine_id: 'stable-diffusion-v1-6', weight: 1, style_preset: 'fantasy-art', samples: 2},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "stabilityAI": {
      "key": "placeholder key",
      "textToImage": {
        "engine_id": "stable-diffusion-v1-6",
        "weight": 1,
        "style_preset": "fantasy-art",
        "samples": 2
  }}}'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "stabilityAI": {
      "key": "placeholder key",
      "textToImage": {
        "engine_id": "stable-diffusion-v1-6",
        "weight": 1,
        "style_preset": "fantasy-art",
        "samples": 2
  }}}'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>



================================================
FILE: website/docs/docs/directConnection/OpenAI/OpenAI.mdx
================================================
---
sidebar_position: 1
---

# OpenAI

import openAILogo from '/img/openAILogo.png';

# <img src={openAILogo} className="adaptive-logo-filter" width="40" style={{float: 'left', marginRight: '10px', marginTop: '9px'}} /><span className="direct-service-title">OpenAI</span>

Properties used to connect to [OpenAI](https://openai.com/blog/openai-api).

### `openAI` {#openAI}

- Type: \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`chat?: Chat`](#Chat), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`assistant?: Assistant`](#Assistant), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`realtime?: OpenAIRealtime`](/docs/directConnection/OpenAI/OpenAIRealtime), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`images?: Images`](#Images), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`textToSpeech?: TextToSpeech`](#TextToSpeech), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`speechToText?: SpeechToText`](#SpeechToText) <br />
  \}
- Default: _\{chat: true\}_

import ContainersKeyToggleChatFunction from '@site/src/components/table/containersKeyToggleChatFunction';
import ContainersKeyToggle from '@site/src/components/table/containersKeyToggle';
import ComponentContainer from '@site/src/components/table/componentContainer';
import DeepChatBrowser from '@site/src/components/table/deepChatBrowser';
import LineBreak from '@site/src/components/markdown/lineBreak';
import BrowserOnly from '@docusaurus/BrowserOnly';
import TabItem from '@theme/TabItem';
import Tabs from '@theme/Tabs';

<BrowserOnly>{() => require('@site/src/components/nav/autoNavToggle').readdAutoNavShadowToggle()}</BrowserOnly>

## Service Types

### `Chat` {#Chat}

- Type: `true` | \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; `system_prompt?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `model?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `max_tokens?: number`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `temperature?: number`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `top_p?: number`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`ChatFunctions`](#chat-functions) <br />
  \}
- Default: _\{system_prompt: "You are a helpful assistant.", model: "gpt-4o"\}_

Connect to OpenAI's [`chat`](https://platform.openai.com/docs/api-reference/chat) API. You can set this property to _true_ or configure it using an object: <br />
`system_prompt` is used to set the [_"system"_](https://platform.openai.com/docs/api-reference/chat/create) message for the conversation context. <br />
`model` is the name of the model to be used by the API. Check [/v1/chat/completions](https://platform.openai.com/docs/models/model-endpoint-compatibility) for more. <br />
`max_tokens` the maximum number of tokens to generate in the chat. Check [tokenizer](https://platform.openai.com/tokenizer) for more info. <br />
`temperature` is used for sampling; between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused. <br />
`top_p` is an alternative to sampling with temperature, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens
comprising the top 10% probability mass are considered. <br />
[`ChatFunctions`](#chat-functions) encompasses properties used for [function calling](https://platform.openai.com/docs/guides/function-calling). <br />

#### Basic Example

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          key: 'placeholder key',
          chat: {max_tokens: 2000, system_prompt: 'Assist me with anything you can'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          chat: {max_tokens: 2000, system_prompt: 'Assist me with anything you can'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "openAI": {
      "key": "placeholder key",
      "chat": {"max_tokens": 2000, "system_prompt": "Assist me with anything you can"}
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "openAI": {
      "key": "placeholder key",
      "chat": {"max_tokens": 2000, "system_prompt": "Assist me with anything you can"}
    }
  }'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

#### Vision Example

If `max_tokens` is not set, the component sets it to _300_ as otherwise the API does not send a full response.

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          key: 'placeholder key',
          chat: {model: 'gpt-4-vision-preview'},
        },
      }}
      images={true}
      camera={true}
      textInput={{styles: {container: {width: '77%'}}}}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          chat: {model: 'gpt-4-vision-preview'},
        },
      }}
      images={true}
      camera={true}
      textInput={{styles: {container: {width: '77%'}}}}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "openAI": {
      "key": "placeholder key",
      "chat": {"model": "gpt-4-vision-preview"}
  }}'
  images="true"
  camera="true"
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "openAI": {
      "key": "placeholder key",
      "chat": {"model": "gpt-4-vision-preview"}
  }}'
  images="true"
  camera="true"
  style="border-radius: 8px"
  textInput='{"styles": {"container": {"width": "77%"}}}'
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `Assistant` {#Assistant}

- Type: `true` | \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; `assistant_id?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `thread_id?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `load_thread_history?: boolean`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`new_assistant?: NewAssistant`](#NewAssistant), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`files_tool_type?: FileToolTypes`](#FileToolTypes), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`function_handler?: AssistantFunctionHandler`](#assistant-functions), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `custom_base_url?: string` <br />
  \}

Connect to your OpenAI [`assistant`](https://platform.openai.com/docs/assistants/overview).
When set to `true` or the `assistant_id` is not defined, Deep Chat will automatically create a new assistant when the user sends the first message. <br />
`assistant_id` is the id of your assistant. <br />
`thread_id` allows you to communicate in the context of an already existing conversation/[thread](https://platform.openai.com/docs/api-reference/threads). <br />
`load_thread_history` toggles a preload of the previous conversation/[thread](https://platform.openai.com/docs/api-reference/threads) messages on chat initialisation. <br />
`new_assistant` defines the details for the newly created assistant. <br />
`files_tool_type` defines the type of a tool to be used to process an uploaded file. <br />
`function_handler` is the actual function used to handle the model's function response. Please navigate to [Assistant Functions](#assistant-functions) for more info. <br />
`custom_base_url` is used to proxy the calls to the service through a custom API such as your service. <br />

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          key: 'placeholder key',
          assistant: {},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          assistant: {},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "openAI": {
      "key": "placeholder key",
      "assistant": true
  }}'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "openAI": {
      "key": "placeholder key",
      "assistant": true
  }}'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

:::info
Returned [MessageContent](/docs/messages#MessageContent) contains a hidden property called `_sessionId` which
stores the thread id and allows conversation to continue on a new session.
:::

<LineBreak></LineBreak>

#### `NewAssistant` {#NewAssistant}

- Type: \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; `model?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `name?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `description?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `instructions?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `tools?`: \{ <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `type?`: `"code_interpreter"` | `"file_search"` | `"function"`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `function?`: \{`name: string`, `description?: string`, `parameters?: object`\} <br />
  &nbsp;&nbsp;&nbsp;&nbsp; \}, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `tool_resources?`: \{ <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `code_interpreter?`: \{`file_ids: string[]`\}, <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `file_search?`: \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `vector_store_ids: string[]`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `vector_stores?`: \{`file_ids: string[]`\} <br />
  &nbsp;&nbsp;&nbsp;&nbsp;\}\}\} <br />

- Default: _\{model: "gpt-4"\}_

When `assistant_id` is not used, this object is used to define the details of the new assistant that will be created by Deep Chat when
the user sends a new message. This object follows the [OpenAI Create Assistant API](https://platform.openai.com/docs/api-reference/assistants/createAssistant). <br />
`model` is the name of the model to be used by the API. Check the [model overview](https://platform.openai.com/docs/models/overview) for more. <br />
`name` and `description` are used to describe the new assistant. <br />
`instructions` direct the assistant's behaviour. <br />
`tool_resources` defines the resources that the assistant has access to. <br />
`tools` is an array of objects that describe the tools the assistant will have access to.
When using the `"function"` tool, you will need to also define the `function` object. <br />

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          key: 'placeholder key',
          assistant: {
            new_assistant: {
              name: 'test model',
              tools: [{type: 'code_interpreter'}],
            },
          },
        },
      }}
      mixedFiles={true}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          assistant: {
            new_assistant: {
              name: 'test model',
              tools: [{type: 'code_interpreter'}],
            },
          },
        },
      }}
      mixedFiles={true}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "openAI": {
      "key": "placeholder key",
      "assistant": {
        "new_assistant": {
          "name": "Demo Assistant",
          "tools": [{"type": "code_interpreter"}]
      }}
  }}'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "openAI": {
      "key": "placeholder key",
      "assistant": {
        "new_assistant": {
          "name": "Demo Assistant",
          "tools": [{"type": "code_interpreter"}]
      }}
  }}'
  mixedFiles="true"
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

:::info
You can access the created `assistant_id` via `chatElementRef._activeService.rawBody.assistant_id`.
:::

<LineBreak></LineBreak>

#### `FileToolTypes` {#FileToolTypes}

- Type: [FileToolType](#FileToolType) | (`fileNames: string[]`) => [FileToolType](#FileToolType)
- Default: _"images"_

This is used to define the type of tool that will be used to process uploaded files. You can either define it as a string or a function that will return
the tool type based on the uploaded files. <br />
When nothing is defined and the user uploads an image, Deep Chat will automatically use [`"images"`](https://platform.openai.com/docs/assistants/how-it-works/creating-image-input-content)
which will not use any tools and send the image directly to the [_vision model_](https://platform.openai.com/docs/models). <br />
It is important to note that the `"code_interpreter"` and `"file_search"` tools must be toggled ON in the assistant that you are using before
the files are uploaded. This can either be done in the [OpenAI Assistant Playground](https://platform.openai.com/playground) or in the [NewAssistant](#NewAssistant) object.

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          key: 'placeholder key',
          assistant: {
            assistant_id: 'assistant with code interpreter',
            files_tool_type: 'code_interpreter',
          },
        },
      }}
      mixedFiles={true}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          assistant: {
            assistant_id: 'assistant with code interpreter',
            files_tool_type: 'code_interpreter',
          },
        },
      }}
      mixedFiles={true}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "openAI": {
      "key": "placeholder key",
      "assistant": {
        "assistant_id": "assistant with code interpreter",
        "files_tool_type": "code_interpreter"
  }}}'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "openAI": {
      "key": "placeholder key",
      "assistant": {
        "assistant_id": "assistant with code interpreter",
        "files_tool_type": "code_interpreter"
  }}}'
  mixedFiles="true"
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

:::info
When uploading a file, the user must also submit a text message.
:::

<LineBreak></LineBreak>

#### `FileToolType` {#FileToolType}

- Type: `"code_interpreter"` | `"file_search"` | `"images"`

Type of tool used to process an uploaded file. Find out more information in [`"code_interpreter"`](https://platform.openai.com/docs/assistants/tools/code-interpreter) and
[`"file_search"`](https://platform.openai.com/docs/assistants/tools/file-search). [`"images"`](https://platform.openai.com/docs/assistants/how-it-works/managing-threads-and-messages) is
technically not a tool but a way to indicate that image files will be sent directly to a [_vision model_](https://platform.openai.com/docs/models).

<LineBreak></LineBreak>

### `Images` {#Images}

- Type: `true` | [`Dall-e-2`](#dall-e-2) | [`Dall-e-3`](#dall-e-3)
- Default: _Dall-e-2_

Connect to OpenAI's [`Images`](https://platform.openai.com/docs/api-reference/images) API.
Set this property to _true_ or use either of the [`Dall-e-2`](#dall-e-2) or [`Dall-e-3`](#dall-e-3) objects. <br />

You can automatically call any of the following three APIs by combining different inputs:

- [Create Image](https://platform.openai.com/docs/api-reference/images/create) - Send text.
- [Create Image Variation](https://platform.openai.com/docs/api-reference/images/create-variation) - Upload and send an image with no text.
- [Create Image Edit](https://platform.openai.com/docs/api-reference/images/create-edit) - Upload an image and add text. You can also upload a second image to be used as a _mask_.

#### Example

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          key: 'placeholder key',
          images: {n: 1, size: '1024x1024', response_format: 'url'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          images: {n: 1, size: '1024x1024', response_format: 'url'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "openAI": {
      "key": "placeholder key",
      "images": {"n": 1, "size": "1024x1024", "response_format": "url"}
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "openAI": {
      "key": "placeholder key",
      "images": {"n": 2, "size": "1024x1024", "response_format": "url"}
    }
  }'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

#### `Dall-e-2`

- Type: \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; `model?: "dall-e-2"`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `n?: number`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `size?:` `"256x256"` | `"512x512"` | `"1024x1024"`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `response_format?:` `"url"` | `"b64_json"`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `user?: number` <br />
  \}
- Default: _\{model: "dall-e-2", size: "1024x1024"\}_

`model` is the name of the specific model to be used by the API. <br />
`n` is the number of images to generate. Ranges between 1 and 10. <br />
`size` is the pixel dimensions of the generated images. <br />
`response_format` is the format in which the generated images are returned. <br />
`user` is a unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse. More info can be found [`here`](https://platform.openai.com/docs/guides/safety-best-practices/end-user-ids). <br />

#### `Dall-e-3`

- Type: \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; `model: "dall-e-3"`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `size?:` `"1024x1024"` | `"1792x1024"` | `"1024x1792"`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `response_format?:` `"url"` | `"b64_json"`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `user?: number` <br />
  \}
- Default: _\{size: "1024x1024"\}_

`model` is the name of the specific model to be used by the API. <br />
`size` is the pixel dimensions of the generated images. <br />
`response_format` is the format in which the generated images are returned. <br />
`user` is a unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse. More info can be found [`here`](https://platform.openai.com/docs/guides/safety-best-practices/end-user-ids). <br />

<LineBreak></LineBreak>

### `TextToSpeech` {#TextToSpeech}

- Type: `true` | \{ <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `model?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `voice?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `speed?: number` <br />
  \}
- Default: _\{model: "tts-1", voice: "alloy", speed: 1\}_

Connect to OpenAI's [`Text To Speech`](https://platform.openai.com/docs/guides/text-to-speech) API.
You can set this property to _true_ or [configure](https://platform.openai.com/docs/api-reference/audio/createSpeech) it using an object: <br />
`model` defines the target model used by the API. Check [/v1/audio/speech](https://platform.openai.com/docs/models/model-endpoint-compatibility) for more. <br />
`voice` is the name of the voice used in the generated audio. <br />
`speed` defines speed of the generated audio. It accepts a value between 0.25 and 4.0.

#### Example

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          key: 'placeholder key',
          textToSpeech: {voice: 'echo'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          textToSpeech: {voice: 'echo'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "openAI": {
      "key": "placeholder key",
      "textToSpeech": {"voice": "echo"}
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "openAI": {
      "key": "placeholder key",
      "textToSpeech": {"voice": "echo"}
    }
  }'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `SpeechToText` {#SpeechToText}

- Type: `true` | \{ <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `model?: "whisper-1"`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `temperature?: number`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `language?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `type?:` `"transcription" | "translation"` <br />
  \}
- Default: _\{model: "whisper-1", type: "transcription"\}_

Connect to OpenAI's [`Speech To Text`](https://platform.openai.com/docs/guides/speech-to-text) API.
You can set this property to _true_ or [configure](https://platform.openai.com/docs/api-reference/audio/createTranscription) it using an object: <br />
`model` is the name of the model to use. _"whisper-1"_ is currently the only one available. <br />
`temperature` is used for sampling; between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused. <br />
`language` is the language used the input audio. Supplying the input language in [_ISO-639-1_](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) format will improve accuracy and latency. (Only used for [_transcription_](https://platform.openai.com/docs/api-reference/audio/create) based API). <br />
`type` is used to toggle between the [_transcription_](https://platform.openai.com/docs/api-reference/audio/create) and the [_translation_](https://platform.openai.com/docs/api-reference/audio/create) APIs.
Note that [_translation_](https://platform.openai.com/docs/api-reference/audio/create) can only attempt to translate audio into _English_.

#### Example

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          key: 'placeholder key',
          speechToText: {model: 'whisper-1', temperature: 0.3, language: 'en', type: 'transcription'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          speechToText: {model: 'whisper-1', temperature: 0.3, language: 'en', type: 'transcription'},
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "openAI": {
      "key": "placeholder key",
      "speechToText": {"model": "whisper-1", "temperature": 0.3, "language": "en", "type": "transcription"}
    }
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "openAI": {
      "key": "placeholder key",
      "audio": {"model": "whisper-1", "temperature": 0.3, "language": "en", "type": "transcription"}
    }
  }'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

## Functions {#Functions}

Examples for OpenAI's [Function Calling](https://platform.openai.com/docs/guides/function-calling) features:

### `Chat Functions` {#chat-functions}

- Type: \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`tools: Tools`](#Tools), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `tool_choice?:` `"auto"` | `{type: "function", function: {name: string}}`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`function_handler: FunctionHandler`](#FunctionHandler) <br />
  \}

Configure the chat to call your functions via the [OpenAI Function calling API](https://platform.openai.com/docs/guides/function-calling). <br />
This is particularly useful if you want the model to analyze user's requests, check whether a function should be called, extract the relevant information
from their text and return it all in a standardized response for you to act on. <br />
`tools` defines the functions that the model can signal to call based on the user's text. <br />
`tool_choice` controls which (if any) function should be called. <br />
`function_handler` is the actual function that is called with the model's instructions.

<ContainersKeyToggleChatFunction></ContainersKeyToggleChatFunction>

<Tabs>
<TabItem value="js" label="Sample code">

```js
// using JavaScript for a simplified example

chatElementRef.directConnection = {
  openAI: {
    chat: {
      tools: [
        {
          type: 'function',
          function: {
            name: 'get_current_weather',
            description: 'Get the current weather in a given location',
            parameters: {
              type: 'object',
              properties: {
                location: {
                  type: 'string',
                  description: 'The city and state, e.g. San Francisco, CA',
                },
                unit: {type: 'string', enum: ['celsius', 'fahrenheit']},
              },
              required: ['location'],
            },
          },
        },
      ],
      function_handler: (functionsDetails) => {
        return functionsDetails.map((functionDetails) => {
          return {
            response: getCurrentWeather(functionDetails.arguments),
          };
        });
      },
    },
    key: 'placeholder-key',
  },
};
```

</TabItem>
<TabItem value="py" label="Full code">

```js
// using JavaScript for a simplified example

chatElementRef.directConnection = {
  openAI: {
    chat: {
      tools: [
        {
          type: 'function',
          function: {
            name: 'get_current_weather',
            description: 'Get the current weather in a given location',
            parameters: {
              type: 'object',
              properties: {
                location: {
                  type: 'string',
                  description: 'The city and state, e.g. San Francisco, CA',
                },
                unit: {type: 'string', enum: ['celsius', 'fahrenheit']},
              },
              required: ['location'],
            },
          },
        },
      ],
      function_handler: (functionsDetails) => {
        return functionsDetails.map((functionDetails) => {
          return {
            response: getCurrentWeather(functionDetails.arguments),
          };
        });
      },
    },
    key: 'placeholder-key',
  },
};

function getCurrentWeather(location) {
  location = location.toLowerCase();
  if (location.includes('tokyo')) {
    return JSON.stringify({location, temperature: '10', unit: 'celsius'});
  } else if (location.includes('san francisco')) {
    return JSON.stringify({location, temperature: '72', unit: 'fahrenheit'});
  } else {
    return JSON.stringify({location, temperature: '22', unit: 'celsius'});
  }
}
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

#### `Tools` {#Tools}

- Type: \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; `type: "function" | "object"`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `function:` \{`name: string`, `description?: string`, [`parameters: JSONSchema`](https://json-schema.org/learn/miscellaneous-examples)\} <br />
  \}[]

An array describing tools that the model may call. <br />
`name` is the name of a function. <br />
`description` is used by the model to understand what the function does and when it should be called. <br />
`parameters` are arguments that the function accepts defined in a [JSON Schema](https://json-schema.org/learn/miscellaneous-examples) (see example above). <br />
Checkout the following [guide](https://platform.openai.com/docs/guides/function-calling) for more about function calling.

:::tip
If your function accepts arguments - the `type` property should be set to _"function"_, otherwise use the following object `{"type": "object", "properties": {}}`.
:::

<LineBreak></LineBreak>

#### `FunctionHandler` {#FunctionHandler}

- Type: ([`functionsDetails: FunctionsDetails`](#FunctionsDetails)) => `{response: string}[]` | `{text: string}`

The actual function that the component will call if the model wants a response from [tools](#Tools) functions. <br />
[`functionsDetails`](#FunctionsDetails) contains information about what [tool](#Tools) functions should be called. <br />
This function should either return an array of JSONs containing a `response` property for each [tool](#Tools) function (in the same order as in `functionsDetails`)
which will feed it back into the model to finalise a response, or return a JSON containing `text` which will immediately display it in the chat
and not send any details to the model.

<LineBreak></LineBreak>

### `Assistant Functions` {#assistant-functions}

- Type: ([`functionsDetails: FunctionsDetails`](#FunctionsDetails)) => `string[]`

The [`function_handler`](#Assistant) property can be assigned with the actual function that the component will call if the model wants a response from your preconfigured assistant's functions
inside the [OpneAI assistants platform](https://platform.openai.com/assistants). <br />
[`functionsDetails`](#FunctionsDetails) contains information about what functions should be called. <br />
This function should return an array of strings defining the response for each function described in `functionDetails` (in the same order)
which will feed it back into the assistant to finalise a response.

<Tabs>
<TabItem value="js" label="Sample code">

```js
// using JavaScript for a simplified example

chatElementRef.directConnection = {
  openAI: {
    assistant: {
      assistant_id: 'placeholder-id',
      function_handler: (functionsDetails) => {
        return functionsDetails.map((functionDetails) => this.getCurrentWeather(functionDetails.arguments));
      },
    },
    key: 'placeholder-key',
  },
};
```

</TabItem>
<TabItem value="py" label="Full code">

```js
// using JavaScript for a simplified example

chatElementRef.directConnection = {
  openAI: {
    assistant: {
      assistant_id: 'placeholder-id',
      function_handler: (functionsDetails) => {
        return functionsDetails.map((functionDetails) => this.getCurrentWeather(functionDetails.arguments));
      },
    },
    key: 'placeholder-key',
  },
};

function getCurrentWeather(location) {
  location = location.toLowerCase();
  if (location.includes('tokyo')) {
    return 'Good';
  } else if (location.includes('san francisco')) {
    return 'Mild';
  } else {
    return 'Very Hot';
  }
}
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

## Shared Types

Types used in [`Functions`](#Functions) properties:

### `FunctionsDetails` {#FunctionsDetails}

- Type: \{`name: string`, `arguments: string`\}[]

Array of objects containing information about the functions that the model wants to call. <br />
`name` is the name of the target function. <br />
`arguments` is a stringified JSON containing properties based on the [`parameters`](#Tools) defined for the function.



================================================
FILE: website/docs/docs/directConnection/OpenAI/OpenAIRealtime.mdx
================================================
---
sidebar_position: 1
---

# OpenAI Realtime

import openAILogo from '/img/openAILogo.png';

# <img src={openAILogo} className="adaptive-logo-filter" width="40" style={{float: 'left', marginRight: '10px', marginTop: '9px'}} /><span className="direct-service-title">OpenAI Realtime</span>

Try this service with custom properties in the [Playground](/playground).

import ContainersKeyToggleRealtimeFunction from '@site/src/components/table/containersKeyToggleRealtimeFunction';
import ComponentContainerEvents from '@site/src/components/table/componentContainerEvents';
import ContainersKeyToggle from '@site/src/components/table/containersKeyToggle';
import ComponentContainer from '@site/src/components/table/componentContainer';
import DeepChatBrowser from '@site/src/components/table/deepChatBrowser';
import LineBreak from '@site/src/components/markdown/lineBreak';
import BrowserOnly from '@docusaurus/BrowserOnly';
import TabItem from '@theme/TabItem';
import Tabs from '@theme/Tabs';

<BrowserOnly>{() => require('@site/src/components/nav/autoNavToggle').readdAutoNavShadowToggle()}</BrowserOnly>

### `realtime` {#realtime}

- Type: \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; `ephemeralKey?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`fetchEphemeralKey?: FetchEphemeralKey`](#FetchEphemeralKey), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `autoFetchEphemeralKey?: boolean`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `autoStart?: boolean`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`avatar?: OpenAIRealtimeAvatar`](#OpenAIRealtimeAvatar), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`buttons?: OpenAIRealtimeButtons`](#OpenAIRealtimeButtons), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`config?: OpenAIRealtimeConfig`](#OpenAIRealtimeConfig), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`methods?: OpenAIRealtimeMethods`](#OpenAIRealtimeMethods), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`events?: SpeechToSpeechEvents`](#SpeechToSpeechEvents), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`loading?: OpenAIRealtimeLoading`](#OpenAIRealtimeLoading) <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`error?: OpenAIRealtimeError`](#OpenAIRealtimeError) <br />
  \} | `true`

Connect to [OpenAI Reatime API](https://platform.openai.com/docs/guides/realtime). You can either use `true` or an object: <br />
`ephemeralKey` is the temporary [session key](https://platform.openai.com/docs/api-reference/realtime-sessions) used to connect from the browser safely. <br />
`fetchEphemeralKey` is a function definition used to retrieve the `ephemeralKey`. <br />
`autoFetchEphemeralKey` triggers `fetchEphemeralKey` on component render. <br />
`autoStart` begins the conversation on component render. <br />
`avatar` is used to configure the avatar. <br />
`buttons` is used to configure the buttons. <br />
`config` is as object that defines the connection properties. <br />
`methods` are used to update the conversation context in real time. <br />
`events` are triggered based on user activity. <br />
`loading` defines the styling for the loading message. <br />
`error` defines the styling for the error message. <br />

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          key: 'placeholder key',
          realtime: true,
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          realtime: true,
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "openAI": {"key": "placeholder key", "realtime": true}
  }'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "openAI": {"key": "placeholder key", "realtime": true}
  }'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

:::info
If `ephemeralKey` or `fetchEphemeralKey` properties are used, the `key` property is not required. If the `key` property is used instead, the `ephemeralKey` will be fetched automatically.
:::

## Types

### `FetchEphemeralKey` {#FetchEphemeralKey}

- Type: () => `string` | `Promise<string>`

This is a function definition that will return the `ephemeralKey` value programmatically. <br />
Details on how to retrieve the key can be found [here](https://platform.openai.com/docs/api-reference/realtime-sessions).

<Tabs>
<TabItem value="js" label="Sample function">

```js
// There are many ways to define the function depending on your framework.
// The following is a simple VanillaJs example:

chatElementRef.directConnection.openAI.realtime.fetchEphemeralKey = () => 'my-key';
```

</TabItem>
<TabItem value="py" label="OpenAI function">

```js
// There are many ways to define the function depending on your framework.
// The following is a simple VanillaJs example:

// Calls the OpenAI service to fetch your ephemeral key
chatElementRef.directConnection.openAI.realtime.fetchEphemeralKey = async () => {
  try {
    const response = await fetch('https://api.openai.com/v1/realtime/sessions', {
      method: 'POST',
      headers: {
        Authorization: 'Bearer OPENAI-API-KEY',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'gpt-4o-realtime-preview-2024-12-17',
        voice: 'verse',
      }),
    });

    const data = await response.json();
    return data.client_secret.value;
  } catch (error) {
    console.error('Error fetching ephemeral key:', error);
    throw error;
  }
};
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

:::tip
See the [`OpenAIRealtimeConfig`](#OpenAIRealtimeConfig) to see available session configuration.
:::

<LineBreak></LineBreak>

### `OpenAIRealtimeAvatar` {#OpenAIRealtimeAvatar}

- Type: \{ <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `src?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `maxScale?: number`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `styles?:` \{[`image?: CustomStyle`](/docs/styles#CustomStyle), [`container?: CustomStyle`](/docs/styles#CustomStyle)} <br />
  \}
- Default: _\{maxScale: 2.5\}_

Configuration for the avatar. <br />
`src` is the path for the image. <br />
`maxScale` is the maximum size that the avatar is allowed to expand to when a response is spoken. <br />
`styles` is an object that is used to style the avatar `image` and the `container` which is the area around the avatar. <br />

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          key: 'placeholder key',
          realtime: {
            avatar: {
              src: '/img/mrFresh.png',
              maxScale: 3.5,
              styles: {
                image: {
                  padding: '5px',
                },
                container: {
                  height: '60%',
                },
              },
            },
          },
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          realtime: {
            avatar: {
              src: '/img/mrFresh.png',
              maxScale: 3.5,
              styles: {
                image: {
                  padding: '5px',
                },
                container: {
                  height: '60%',
                },
              },
            },
          },
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "openAI": {
      "realtime": {
        "avatar": {
          "src": "path-to-file.png",
          "maxScale": 3.5,
          "styles": {
            "image": {"padding": "5px"},
            "container": {"height": "60%"}
          }}}}}'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "openAI": {
      "key": "placeholder key",
      "realtime": {
        "avatar": {
          "src": "path-to-file.png",
          "maxScale": 3.5,
          "styles": {
            "image": {"padding": "5px"},
            "container": {"height": "60%"}
          }}}}}'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `OpenAIRealtimeButtons` {#OpenAIRealtimeButtons}

- Type: \{ <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`container?: CustomStyle`](/docs/styles#CustomStyle), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`microphone?: OpenAIRealtimeButton`](#OpenAIRealtimeButton), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`toggle?: OpenAIRealtimeButton`](#OpenAIRealtimeButton) <br />
  \}

Configuration for the buttons section. <br />
`container` is styling for the buttons area. <br />
`microphone` is styling for the various states of the microphone button. <br />
`toggle` is styling for the various states of the toggle button. <br />

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          key: 'placeholder key',
          realtime: {
            buttons: {
              container: {backgroundColor: '#f7f7f7'},
              microphone: {
                default: {
                  svg: {
                    content:
                      '<svg xmlns="http://www.w3.org/2000/svg" width="800px" height="800px" viewBox="0 0 24 24" fill="none">\n<path d="M3 16.5C2.59 16.5 2.25 16.16 2.25 15.75V8.25C2.25 7.84 2.59 7.5 3 7.5C3.41 7.5 3.75 7.84 3.75 8.25V15.75C3.75 16.16 3.41 16.5 3 16.5Z" fill="#292D32"/>\n<path d="M7.5 19C7.09 19 6.75 18.66 6.75 18.25V5.75C6.75 5.34 7.09 5 7.5 5C7.91 5 8.25 5.34 8.25 5.75V18.25C8.25 18.66 7.91 19 7.5 19Z" fill="#292D32"/>\n<path d="M12 21.5C11.59 21.5 11.25 21.16 11.25 20.75V3.25C11.25 2.84 11.59 2.5 12 2.5C12.41 2.5 12.75 2.84 12.75 3.25V20.75C12.75 21.16 12.41 21.5 12 21.5Z" fill="#292D32"/>\n<path d="M16.5 19C16.09 19 15.75 18.66 15.75 18.25V5.75C15.75 5.34 16.09 5 16.5 5C16.91 5 17.25 5.34 17.25 5.75V18.25C17.25 18.66 16.91 19 16.5 19Z" fill="#292D32"/>\n<path d="M21 16.5C20.59 16.5 20.25 16.16 20.25 15.75V8.25C20.25 7.84 20.59 7.5 21 7.5C21.41 7.5 21.75 7.84 21.75 8.25V15.75C21.75 16.16 21.41 16.5 21 16.5Z" fill="#292D32"/>\n</svg>',
                  },
                },
              },
              toggle: {
                default: {
                  svg: {
                    styles: {
                      default: {
                        filter:
                          'brightness(0) saturate(100%) invert(58%) sepia(77%) saturate(282%) hue-rotate(172deg) brightness(91%) contrast(93%)',
                      },
                    },
                  },
                },
              },
            },
          },
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          realtime: {
            buttons: {
              container: {backgroundColor: '#f7f7f7'},
              microphone: {
                default: {
                  svg: {
                    content:
                      '<svg xmlns="http://www.w3.org/2000/svg" width="800px" height="800px" viewBox="0 0 24 24" fill="none">\n<path d="M3 16.5C2.59 16.5 2.25 16.16 2.25 15.75V8.25C2.25 7.84 2.59 7.5 3 7.5C3.41 7.5 3.75 7.84 3.75 8.25V15.75C3.75 16.16 3.41 16.5 3 16.5Z" fill="#292D32"/>\n<path d="M7.5 19C7.09 19 6.75 18.66 6.75 18.25V5.75C6.75 5.34 7.09 5 7.5 5C7.91 5 8.25 5.34 8.25 5.75V18.25C8.25 18.66 7.91 19 7.5 19Z" fill="#292D32"/>\n<path d="M12 21.5C11.59 21.5 11.25 21.16 11.25 20.75V3.25C11.25 2.84 11.59 2.5 12 2.5C12.41 2.5 12.75 2.84 12.75 3.25V20.75C12.75 21.16 12.41 21.5 12 21.5Z" fill="#292D32"/>\n<path d="M16.5 19C16.09 19 15.75 18.66 15.75 18.25V5.75C15.75 5.34 16.09 5 16.5 5C16.91 5 17.25 5.34 17.25 5.75V18.25C17.25 18.66 16.91 19 16.5 19Z" fill="#292D32"/>\n<path d="M21 16.5C20.59 16.5 20.25 16.16 20.25 15.75V8.25C20.25 7.84 20.59 7.5 21 7.5C21.41 7.5 21.75 7.84 21.75 8.25V15.75C21.75 16.16 21.41 16.5 21 16.5Z" fill="#292D32"/>\n</svg>',
                  },
                },
              },
              toggle: {
                default: {
                  svg: {
                    styles: {
                      default: {
                        filter:
                          'brightness(0) saturate(100%) invert(58%) sepia(77%) saturate(282%) hue-rotate(172deg) brightness(91%) contrast(93%)',
                      },
                    },
                  },
                },
              },
            },
          },
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "openAI": {
      "realtime": {
        "buttons": {
          "container": {"backgroundColor": "#f7f7f7"},
          "microphone": {
            "default": {
              "svg": {"content": "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"800px\" height=\"800px\" viewBox=\"0 0 24 24\" fill=\"none\">\n<path d=\"M3 16.5C2.59 16.5 2.25 16.16 2.25 15.75V8.25C2.25 7.84 2.59 7.5 3 7.5C3.41 7.5 3.75 7.84 3.75 8.25V15.75C3.75 16.16 3.41 16.5 3 16.5Z\" fill=\"#292D32\"/>\n<path d=\"M7.5 19C7.09 19 6.75 18.66 6.75 18.25V5.75C6.75 5.34 7.09 5 7.5 5C7.91 5 8.25 5.34 8.25 5.75V18.25C8.25 18.66 7.91 19 7.5 19Z\" fill=\"#292D32\"/>\n<path d=\"M12 21.5C11.59 21.5 11.25 21.16 11.25 20.75V3.25C11.25 2.84 11.59 2.5 12 2.5C12.41 2.5 12.75 2.84 12.75 3.25V20.75C12.75 21.16 12.41 21.5 12 21.5Z\" fill=\"#292D32\"/>\n<path d=\"M16.5 19C16.09 19 15.75 18.66 15.75 18.25V5.75C15.75 5.34 16.09 5 16.5 5C16.91 5 17.25 5.34 17.25 5.75V18.25C17.25 18.66 16.91 19 16.5 19Z\" fill=\"#292D32\"/>\n<path d=\"M21 16.5C20.59 16.5 20.25 16.16 20.25 15.75V8.25C20.25 7.84 20.59 7.5 21 7.5C21.41 7.5 21.75 7.84 21.75 8.25V15.75C21.75 16.16 21.41 16.5 21 16.5Z\" fill=\"#292D32\"/>\n</svg>"}
            }},
          "toggle": {
            "default": {
              "svg": {
                "styles": {
                  "default": {"filter": "brightness(0) saturate(100%) invert(58%) sepia(77%) saturate(282%) hue-rotate(172deg) brightness(91%) contrast(93%)" }
                }}}}}}}}'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "openAI": {
      "key": "placeholder key",
      "realtime": {
        "buttons": {
          "container": {"backgroundColor": "#f7f7f7"},
          "microphone": {
            "default": {
              "svg": {"content": "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"800px\" height=\"800px\" viewBox=\"0 0 24 24\" fill=\"none\">\n<path d=\"M3 16.5C2.59 16.5 2.25 16.16 2.25 15.75V8.25C2.25 7.84 2.59 7.5 3 7.5C3.41 7.5 3.75 7.84 3.75 8.25V15.75C3.75 16.16 3.41 16.5 3 16.5Z\" fill=\"#292D32\"/>\n<path d=\"M7.5 19C7.09 19 6.75 18.66 6.75 18.25V5.75C6.75 5.34 7.09 5 7.5 5C7.91 5 8.25 5.34 8.25 5.75V18.25C8.25 18.66 7.91 19 7.5 19Z\" fill=\"#292D32\"/>\n<path d=\"M12 21.5C11.59 21.5 11.25 21.16 11.25 20.75V3.25C11.25 2.84 11.59 2.5 12 2.5C12.41 2.5 12.75 2.84 12.75 3.25V20.75C12.75 21.16 12.41 21.5 12 21.5Z\" fill=\"#292D32\"/>\n<path d=\"M16.5 19C16.09 19 15.75 18.66 15.75 18.25V5.75C15.75 5.34 16.09 5 16.5 5C16.91 5 17.25 5.34 17.25 5.75V18.25C17.25 18.66 16.91 19 16.5 19Z\" fill=\"#292D32\"/>\n<path d=\"M21 16.5C20.59 16.5 20.25 16.16 20.25 15.75V8.25C20.25 7.84 20.59 7.5 21 7.5C21.41 7.5 21.75 7.84 21.75 8.25V15.75C21.75 16.16 21.41 16.5 21 16.5Z\" fill=\"#292D32\"/>\n</svg>"}
            }},
          "toggle": {
            "default": {
              "svg": {
                "styles": {
                  "default": {"filter": "brightness(0) saturate(100%) invert(58%) sepia(77%) saturate(282%) hue-rotate(172deg) brightness(91%) contrast(93%)" }
                }}}}}}}}'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `OpenAIRealtimeButton` {#OpenAIRealtimeButton}

- Type: \{[`default?: ButtonStyles`](/docs/styles/buttons#ButtonStyles), [`active?: ButtonStyles`](/docs/styles/buttons#ButtonStyles), [`unavailable?: ButtonStyles`](/docs/styles/buttons#ButtonStyles)}

Configuration for the various sates of a button. <br />

<LineBreak></LineBreak>

### `OpenAIRealtimeConfig` {#OpenAIRealtimeConfig}

- Type: \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; `model?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `instructions?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `voice?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `temperature?: number`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `max_response_output_tokens?:` `number` | `"inf"`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `turn_detection?:` \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `type?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `threshold?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `prefix_padding_ms?: number`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `silence_duration_ms?: number`\} <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `tools?:` \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `type?:` `"function"`|`"code_interpreter"`|`"file_search"`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `name?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `description?: number`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `parameters?: object`\}[] <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `tool_choice?: string`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`function_handler?: OpenAIRealtimeFunction`](#OpenAIRealtimeFunction) <br />
  \}
- Default: _\{model: "gpt-4o-realtime-preview-2024-12-17"\}_

Session configuration. This object follows the configuration referenced [here](https://platform.openai.com/docs/api-reference/realtime-sessions/create). <br />
**IMPORTANT:** If you are providing your own `ephemeralKey` or using the [`fetchEphemeralKey`](#FetchEphemeralKey) function, this configuration will need to be used there.
However, this does not apply to the [`function_handler`](#OpenAIRealtimeFunction). <br />
`model` is the model name used for the session. <br />
`instructions` allows the model to be guided on desired responses (also known as system message). <br />
`voice` is the model response's voice. See full list [here](https://platform.openai.com/docs/api-reference/realtime-sessions/create#realtime-sessions-create-voice). <br />
`temperature` is the sampling temperature for the model. <br />
`max_response_output_tokens` is the maximum number of output tokens for a single assistant response. <br />
`turn_detection` is configuration to detect when the model should start speaking. More info can be found [here](https://platform.openai.com/docs/api-reference/realtime-sessions/create#realtime-sessions-create-turn_detection). <br />
`tools` is a list of tools available to the model. More info can be found [here](https://platform.openai.com/docs/api-reference/realtime-sessions/create#realtime-sessions-create-tools). <br />
`tool_choice` is used to define how the model chooses tools. <br />

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          key: 'placeholder key',
          realtime: {
            config: {
              instructions: 'Answer only with yes or no',
              voice: 'alloy',
            },
          },
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          realtime: {
            config: {
              instructions: 'Answer only with yes or no',
              voice: 'alloy',
            },
          },
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "openAI": {
      "realtime": {
        "config": {
          "instructions": "Answer only with yes or no",
          "voice": "alloy"
    }}}}'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "openAI": {
      "key": "placeholder key",
        "realtime": {
          "config": {
            "instructions": "Answer only with yes or no",
            "voice": "alloy"
      }}}}'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `OpenAIRealtimeFunction` {#OpenAIRealtimeFunction}

- Type: (\{`name: string`, `arguments: string`\}) => `object`

The actual function that the component will call if the model wants a response from [OpenAIRealtimeConfig](#OpenAIRealtimeConfig) `tools` functions. <br />

<ContainersKeyToggleRealtimeFunction></ContainersKeyToggleRealtimeFunction>

<Tabs>
<TabItem value="js" label="Sample code">

```js
// using JavaScript for a simplified example

chatElementRef.directConnection = {
  openAI: {
    key: 'placeholder-key',
    realtime: {
      config: {
        tools: [
          {
            type: 'function',
            name: 'get_current_weather',
            description: 'Get the current weather in a given location',
            parameters: {
              type: 'object',
              properties: {
                location: {
                  type: 'string',
                  description: 'The city and state, e.g. San Francisco, CA',
                },
                unit: {type: 'string', enum: ['celsius', 'fahrenheit']},
              },
              required: ['location'],
            },
          },
        ],
        function_handler: (functionsDetails) => {
          const {location} = JSON.parse(functionsDetails.arguments);
          return this.getCurrentWeather(location);
        },
      },
    },
  },
};
```

</TabItem>
<TabItem value="py" label="Full code">

```js
// using JavaScript for a simplified example

chatElementRef.directConnection = {
  openAI: {
    key: 'placeholder-key',
    realtime: {
      config: {
        tools: [
          {
            type: 'function',
            name: 'get_current_weather',
            description: 'Get the current weather in a given location',
            parameters: {
              type: 'object',
              properties: {
                location: {
                  type: 'string',
                  description: 'The city and state, e.g. San Francisco, CA',
                },
                unit: {type: 'string', enum: ['celsius', 'fahrenheit']},
              },
              required: ['location'],
            },
          },
        ],
        function_handler: (functionsDetails) => {
          const {location} = JSON.parse(functionsDetails.arguments);
          return this.getCurrentWeather(location);
        },
      },
    },
  },
};

function getCurrentWeather(location) {
  location = location.toLowerCase();
  if (location.includes('tokyo')) {
    return {location, temperature: '10', unit: 'celsius'};
  } else if (location.includes('san francisco')) {
    return {location, temperature: '72', unit: 'fahrenheit'};
  } else {
    return {location, temperature: '22', unit: 'celsius'};
  }
}
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `OpenAIRealtimeMethods` {#OpenAIRealtimeMethods}

- Type: \{<br />
  &nbsp;&nbsp;&nbsp;&nbsp; `updateConfig?:` ([`config?: OpenAIRealtimeConfig`](#OpenAIRealtimeConfig)) => `void`, <br />
  &nbsp;&nbsp;&nbsp;&nbsp; `sendMessage?:` (`text: string`, `role?: 'user' | 'assistant' | 'system'`) => `void` <br />
  \}

`updateConfig` updates the session configuration. [Info](https://platform.openai.com/docs/api-reference/realtime-client-events/session). <br />
`sendMessage` sends a message to the session. [Info](https://platform.openai.com/docs/api-reference/realtime-client-events/conversation/item/create). <br />

:::info
These methods are automatically assigned and do not need to be defined. <br />
To use these methods, the [`realtime`](#realtime) property must be an _object_ and not a _boolean_ (using realtime: `{}` is fine).
:::

<Tabs>
<TabItem value="js" label="Sample code">

```js
<deep-chat directConnection='{"openAI": {"key": "key","realtime": {}}}'></deep-chat>;

// retrieve element reference via your framework of choice

chatElementRef.openAI.realtime.methods.updateConfig({instructions: 'Respond with only yes or no'});

chatElementRef.openAI.realtime.methods.sendMessage('Are you a real human?', 'user');
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `SpeechToSpeechEvents` {#SpeechToSpeechEvents}

- Functions: \{ `started?:` () => `void`, `stopped?:` () => `void` \}
- Events: `sts-session-started` | `sts-session-stopped`

`started`/`sts-session-started` is triggered when the conversion has started. <br />
`stopped`/`sts-session-stopped` is triggered when the conversion has stopped. <br />

{' '}
<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          key: 'placeholder key',
          realtime: true,
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <ComponentContainerEvents eventNames={['sts-session-started', 'sts-session-stopped']}>
      <DeepChatBrowser
        style={{borderRadius: '8px'}}
        directConnection={{
          openAI: {
            realtime: true,
          },
        }}
      ></DeepChatBrowser>
    </ComponentContainerEvents>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Functions">

```js
chatElementRef.directConnection.openAI.realtime.events = {
  started: () => console.log('Session started'),
  stopped: () => console.log('Session stopped'),
};
```

</TabItem>
<TabItem value="py" label="Events">

```js
// This example is for Vanilla JS and should be tailored to your framework (see Examples)

chatElementRef.addEventListener('sts-session-started', () => {
  console.log('Session started');
});

chatElementRef.addEventListener('sts-session-stopped', () => {
  console.log('Session stopped');
});
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `OpenAIRealtimeLoading` {#OpenAIRealtimeLoading}

- Type: \{`text?: string`, `html?: string`, `display?: boolean`, [`style?: CustomStyle`](/docs/styles#CustomStyle)\}
- Default: _\{text: "Loading", "display": true\}_

Configuration for the loading message. <br />
`text` is the text that will be displayed when loading. <br />
`html` can be used to render a special loading element. <br />
`display` toggles whether the loading message is displayed. <br />
`style` is the general styling for the loading message. <br />

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          key: 'placeholder key',
          realtime: {
            loading: {
              html: '<div class="lds-ripple"><div></div><div></div></div>',
              style: {top: '20px'},
            },
          },
        },
      }}
      auxiliaryStyle={`.lds-ripple {
          color: #1c4c5b
        }
        .lds-ripple,
        .lds-ripple div {
          box-sizing: border-box;
        }
        .lds-ripple {
          display: inline-block;
          position: relative;
          width: 80px;
          height: 80px;
        }
        .lds-ripple div {
          position: absolute;
          border: 4px solid currentColor;
          opacity: 1;
          border-radius: 50%;
          animation: lds-ripple 1s cubic-bezier(0, 0.2, 0.8, 1) infinite;
        }
        .lds-ripple div:nth-child(2) {
          animation-delay: -0.5s;
        }
        @keyframes lds-ripple {
          0% {
            top: 36px;
            left: 36px;
            width: 8px;
            height: 8px;
            opacity: 0;
          }
          4.9% {
            top: 36px;
            left: 36px;
            width: 8px;
            height: 8px;
            opacity: 0;
          }
          5% {
            top: 36px;
            left: 36px;
            width: 8px;
            height: 8px;
            opacity: 1;
          }
          100% {
            top: 0;
            left: 0;
            width: 80px;
            height: 80px;
            opacity: 0;
          }
        }
        `}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          realtime: {
            loading: {
              html: '<div class="lds-ripple"><div></div><div></div></div>',
              style: {top: '20px'},
            },
          },
        },
      }}
      auxiliaryStyle={`.lds-ripple {
          color: #1c4c5b
        }
        .lds-ripple,
        .lds-ripple div {
          box-sizing: border-box;
        }
        .lds-ripple {
          display: inline-block;
          position: relative;
          width: 80px;
          height: 80px;
        }
        .lds-ripple div {
          position: absolute;
          border: 4px solid currentColor;
          opacity: 1;
          border-radius: 50%;
          animation: lds-ripple 1s cubic-bezier(0, 0.2, 0.8, 1) infinite;
        }
        .lds-ripple div:nth-child(2) {
          animation-delay: -0.5s;
        }
        @keyframes lds-ripple {
          0% {
            top: 36px;
            left: 36px;
            width: 8px;
            height: 8px;
            opacity: 0;
          }
          4.9% {
            top: 36px;
            left: 36px;
            width: 8px;
            height: 8px;
            opacity: 0;
          }
          5% {
            top: 36px;
            left: 36px;
            width: 8px;
            height: 8px;
            opacity: 1;
          }
          100% {
            top: 0;
            left: 0;
            width: 80px;
            height: 80px;
            opacity: 0;
          }
        }
        `}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "openAI": {
      "realtime": {
        "loading": {
          "html": "<div class=\"lds-ripple\"><div></div><div></div></div>",
          "style": {"top": "20px"}
      }}}}'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
    "openAI": {
      "key": "placeholder key",
      "realtime": {
        "loading": {
          "html": "<div class=\"lds-ripple\"><div></div><div></div></div>",
          "style": {"top": "20px"}
      }}}}'
  auxiliaryStyle="
    .lds-ripple {
      color: #1c4c5b
    }
    .lds-ripple,
    .lds-ripple div {
      box-sizing: border-box;
    }
    .lds-ripple {
      display: inline-block;
      position: relative;
      width: 80px;
      height: 80px;
    }
    .lds-ripple div {
      position: absolute;
      border: 4px solid currentColor;
      opacity: 1;
      border-radius: 50%;
      animation: lds-ripple 1s cubic-bezier(0, 0.2, 0.8, 1) infinite;
    }
    .lds-ripple div:nth-child(2) {
      animation-delay: -0.5s;
    }
    @keyframes lds-ripple {
      0% {
        top: 36px;
        left: 36px;
        width: 8px;
        height: 8px;
        opacity: 0;
      }
      4.9% {
        top: 36px;
        left: 36px;
        width: 8px;
        height: 8px;
        opacity: 0;
      }
      5% {
        top: 36px;
        left: 36px;
        width: 8px;
        height: 8px;
        opacity: 1;
      }
      100% {
        top: 0;
        left: 0;
        width: 80px;
        height: 80px;
        opacity: 0;
      }
    }"
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `OpenAIRealtimeError` {#OpenAIRealtimeError}

- Type: \{`text?: string`, [`style?: CustomStyle`](/docs/styles#CustomStyle)\}
- Default: _\{text: "Error"\}_

Configuration for the error message. <br />
`text` is the text that will be displayed for the error message. <br />
`style` is the general styling for the error message. <br />

<ContainersKeyToggle>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          key: 'placeholder key',
          realtime: {
            error: {
              text: 'Custom Error!',
              style: {color: 'orange'},
            },
          },
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
  <ComponentContainer>
    <DeepChatBrowser
      style={{borderRadius: '8px'}}
      directConnection={{
        openAI: {
          realtime: {
            error: {
              text: 'Custom Error!',
              style: {color: 'orange'},
            },
          },
        },
      }}
    ></DeepChatBrowser>
  </ComponentContainer>
</ContainersKeyToggle>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat
  directConnection='{
    "openAI": {
      "realtime": {
        "error": {
          "text": "Custom Error!",
          "style": {"color": "orange"}
        }}}}'
></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  directConnection='{
  "openAI": {
    "key": "placeholder key",
    "realtime": {
      "error": {
        "text": "Custom Error!",
        "style": {"color": "orange"}
      }}}}'
  style="border-radius: 8px"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>



================================================
FILE: website/docs/docs/messages/HTML.mdx
================================================
---
sidebar_position: 2
---

# HTML

You can insert and render your own code inside chat message bubbles using the `html` property. <br />
If you want to use your code for an introduction panel - check out [`Intro Panel`](/docs/introPanel) instead.

### Getting started {#Getting Started}

The `html` property can be used in server [Response](/docs/connect#Response)s and is stored inside the chat using the [MessageContent](/docs/messages#MessageContent) format.
It must describe full (not partial) elements or simple plain text. Here is an example for [`history`](/docs/messages#history):

import ComponentContainer from '@site/src/components/table/componentContainer';
import DeepChatBrowser from '@site/src/components/table/deepChatBrowser';
import LineBreak from '@site/src/components/markdown/lineBreak';
import BrowserOnly from '@docusaurus/BrowserOnly';
import TabItem from '@theme/TabItem';
import Tabs from '@theme/Tabs';

<BrowserOnly>{() => require('@site/src/components/nav/autoNavToggle').readdAutoNavShadowToggle()}</BrowserOnly>
<BrowserOnly>{() => require('@site/src/components/externalModules/externalModules').importHighlight()}</BrowserOnly>
<BrowserOnly>{() => require('@site/src/components/webComponent/exampleWebComponent').add()}</BrowserOnly>
<BrowserOnly>
  {() => {
    require('active-table-react').DeepChat;
  }}
</BrowserOnly>
<BrowserOnly>
  {() => {
    require('@google-web-components/google-chart');
  }}
</BrowserOnly>

<ComponentContainer>
  <DeepChatBrowser
    demo={true}
    history={[{html: '<button>Button</button>', role: 'user'}]}
    style={{height: '370px', borderRadius: '8px'}}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat history='[{"html": "<button>Button</button>", "role": "user"}]'></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  history='[{"html": "<button>Button</button>", "role": "user"}]'
  style="height: 370px; border-radius: 8px"
  demo="true"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### `htmlClassUtilities` {#htmlClassUtilities}

- Type: \{<br />
  &nbsp;&nbsp;[`className: string`]: \{ <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`events?: {[eventType: string]?: (event) => void}`](https://azuresdkdocs.blob.core.windows.net/$web/javascript/azure-app-configuration/1.1.0/interfaces/globaleventhandlerseventmap.html), <br />
  &nbsp;&nbsp;&nbsp;&nbsp; [`styles?: StatefulStyles`](/docs/styles/#StatefulStyles) <br />
  \}\}

Because Deep Chat is a [shadow element](https://developer.mozilla.org/en-US/docs/Web/API/Web_components/Using_shadow_DOM) and your html is rendered inside it - the resulting elements will not be able to access the CSS and JavaScript
in your app. To help with this, you can use this object to declare reusable styling and bind your app's functions to the elements via their class names. <br />
`events` is an object that accepts properties with keys from [GlobalEventHandlersEventMap](https://azuresdkdocs.blob.core.windows.net/$web/javascript/azure-app-configuration/1.1.0/interfaces/globaleventhandlerseventmap.html) (same as the string
used for _addEventListener(HERE)_, e.g. _"mousedown"_) or any custom event name and accepts a function as the value. <br />
`styles` defines the styles applied to the element for different mouse states. You can alternatively define CSS styles using the [`auxiliaryStyle`](/docs/styles#auxiliaryStyle) property. <br />

#### Example

<ComponentContainer>
  <DeepChatBrowser
    demo={true}
    htmlClassUtilities={{
      ['custom-button']: {
        events: {
          mouseenter: (event) => {
            event.target.innerText = 'Hovering';
          },
          mouseleave: (event) => {
            event.target.innerText = 'Hovered';
          },
        },
        styles: {
          default: {padding: '3px 8px', cursor: 'pointer'},
          hover: {backgroundColor: 'yellow'},
        },
      },
      ['ai-button']: {
        styles: {
          default: {color: 'green'},
        },
      },
    }}
    history={[
      {html: '<button class="custom-button">Hoverable</button>', role: 'user'},
      {html: '<button class="custom-button ai-button">Hoverable</button>', role: 'ai'},
    ]}
    style={{height: '370px', borderRadius: '8px'}}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```js
// using JavaScript for a simplified example

chatElementRef.htmlClassUtilities = {
  ['custom-button']: {
    events: {
      mouseenter: (event) => (event.target.innerText = 'Hovering'),
      mouseleave: (event) => (event.target.innerText = 'Hovered'),
    },
    styles: {
      default: {padding: '3px 8px', cursor: 'pointer'},
      hover: {backgroundColor: 'yellow'},
    },
  },
  ['ai-button']: {
    styles: {
      default: {color: 'green'},
    },
  },
};
chatElementRef.history = [
  {html: '<button class="custom-button">Hoverable</button>', role: 'user'},
  {html: '<button class="custom-button ai-button">Hoverable</button>', role: 'ai'},
];
```

</TabItem>
<TabItem value="py" label="Full code">

```js
// using JavaScript for a simplified example

chatElementRef.htmlClassUtilities = {
  ['custom-button']: {
    events: {
      mouseenter: (event) => (event.target.innerText = 'Hovering'),
      mouseleave: (event) => (event.target.innerText = 'Hovered'),
    },
    styles: {
      default: {padding: '3px 8px', cursor: 'pointer'},
      hover: {backgroundColor: 'yellow'},
    },
  },
  ['ai-button']: {
    styles: {
      default: {color: 'green'},
    },
  },
};
chatElementRef.history = [
  {html: '<button class="custom-button">Hoverable</button>', role: 'user'},
  {html: '<button class="custom-button ai-button">Hoverable</button>', role: 'ai'},
];
Object.assign(chatElementRef.style, {height: '370px', borderRadius: '8px'});
chatElementRef.demo = true;
```

</TabItem>
</Tabs>

### Deep Chat Classes {#deepChatClasses}

Deep Chat comes with a pre-defined set of classes that can be used to add styling/functionality to your elements. <br />
`deep-chat-button` - applies default button styling. <br />
`deep-chat-suggestion-button` - when clicked sends the text that is inside the button as a new user message. <br />
`deep-chat-temporary-message` - removes the message when a new one is added to the chat. This class needs to be applied
to the parent-most element in the `html` string. This message is also not tracked in state. <br />

#### Basic Example

<ComponentContainer>
  <DeepChatBrowser
    history={[
      {html: '<button class="deep-chat-button deep-chat-suggestion-button">Hello</button>', role: 'ai'},
      {
        html: '<button class="deep-chat-suggestion-button deep-chat-temporary-message">Goodbye</button>',
        role: 'user',
      },
    ]}
    style={{height: '370px', borderRadius: '8px'}}
    demo={true}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```js
// using JavaScript for a simplified example

chatElementRef.history = [
  {html: '<button class="deep-chat-button deep-chat-suggestion-button">Hello</button>', role: 'ai'},
  {html: '<button class="deep-chat-suggestion-button deep-chat-temporary-message">Goodbye</button>', role: 'user'},
];
```

</TabItem>
<TabItem value="py" label="Full code">

```js
// using JavaScript for a simplified example

chatElementRef.history = [
  {html: '<button class="deep-chat-button deep-chat-suggestion-button">Hello</button>', role: 'ai'},
  {html: '<button class="deep-chat-suggestion-button deep-chat-temporary-message">Goodbye</button>', role: 'user'},
];
Object.assign(chatElementRef.style, {height: '370px', borderRadius: '8px'});
chatElementRef.demo = true;
```

</TabItem>
</Tabs>

:::info
If you have suggestions for new classes that you think would be useful, please raise an [issue](https://github.com/OvidijusParsiunas/deep-chat/issues) on GitHub.
:::

<LineBreak></LineBreak>

### Bubble Style {#bubbleStyle}

To unset/change the message bubble styling, use the `html` property in the [messageStyles](/docs/messages/styles#messageStyles) object.

#### Example

<ComponentContainer>
  <DeepChatBrowser
    demo={true}
    history={[{html: '<button>User button</button>', role: 'user'}]}
    messageStyles={{html: {shared: {bubble: {backgroundColor: 'unset'}}}}}
    style={{height: '370px', borderRadius: '8px'}}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```html
<deep-chat messageStyles='{"html": {"shared": {"bubble": {"backgroundColor": "unset"}}}}'></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```html
<!-- This example is for Vanilla JS and should be tailored to your framework (see Examples) -->

<deep-chat
  messageStyles='{"html": {"shared": {"bubble": {"backgroundColor": "unset"}}}}'
  history='[{"html": "<button>User button</button>", "role": "user"}]'
  style="height: 370px; border-radius: 8px"
  demo="true"
></deep-chat>
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

### Custom Elements {#customElements}

If the `html` string includes your own custom tags (e.g. `<custom-element>`), they cannot be for the components in your framework
and must instead be for [custom elements](https://developer.mozilla.org/en-US/docs/Web/API/Web_components/Using_custom_elements)
or [shadow DOM elements](https://developer.mozilla.org/en-US/docs/Web/API/Web_components/Using_shadow_DOM)
([web components](https://developer.mozilla.org/en-US/docs/Web/API/Web_components)). <br />
To create new web components - use any of the following approaches:

- Most frameworks include a way to convert their components into shadow elements/web components. Please refer to their documentation for more information.
- You can also create new web components in your app using basic JavaScript - refer to [this guide](https://javascript.plainenglish.io/introduction-to-web-components-in-javascript-create-a-hello-world-web-component-e624874ec3b1).
- Web components can ultimately be created in any way you desire using any framework outside of your project and imported the same ways as you do
  `deep-chat`. To note, this approach may require you to first import or use them in your app's code in order for your bundler to register them.

#### Example

<ComponentContainer>
  <DeepChatBrowser
    demo={true}
    history={[{html: '<custom-element/>', role: 'user'}]}
    style={{height: '370px', borderRadius: '8px'}}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```txt
// This is a simple way to create web components via JavaScript, refer to all possibilities above

// JavaScript
class CustomElement extends HTMLElement {
  constructor() {
    super();
    this.textContent = 'This is a Custom Element';
  }
}

customElements.define('custom-element', CustomElement);

// HTML
<deep-chat history='[{"html": "<custom-element/>", "role": "user"}]'></deep-chat>
```

</TabItem>
<TabItem value="py" label="Full code">

```txt
// This is a simple way to create web components via JavaScript, refer to all possibilities above

// JavaScript
class CustomElement extends HTMLElement {
  constructor() {
    super();
    this.textContent = 'This is a Custom Element';
  }
}

customElements.define('custom-element', CustomElement);

// HTML
<deep-chat
  history='[{"html": "<custom-element/>", "role": "user"}]'
  style="height: 370px; border-radius: 8px"
  demo="true"
></deep-chat>
```

</TabItem>
</Tabs>

:::info
When passing values into your custom element, you need to pass them as [attributes](https://www.w3schools.com/html/html_attributes.asp) (they must be stringified). E.g.
`{"html": "<custom-element count="0" name="jeff"></custom-element>"}`
:::

:::info
If you are experiencing problems with embedding your custom elements inside the chat, you can always raise an [issue](https://github.com/OvidijusParsiunas/deep-chat/issues) on GitHub.
When you do please provide us with either a [sandbox](https://codesandbox.io/) example or sufficient information to enable us to replicate the problem.
:::

<LineBreak></LineBreak>

### `HTMLWrappers` {#htmlWrappers}

- Type: \{`default?: string`, `ai?: string`, `role-name?: string`\}

When a message is [streamed](/docs/connect#stream), its content will be populated _inside_ a custom HTML wrapper. <br />
To denote the tag in which the content is going to be populated in use the `stream-wrapper` class. <br />
You can define a string with HTML format for all roles using the `default` property, only ai responses using the `ai` role or
any other custom roles using the `role-name` property.

#### Example

<ComponentContainer>
  <DeepChatBrowser
    demo={true}
    connect={{
      stream: {
        htmlWrappers: {
          default: `
            <div>
              <b>Wrapper title</b>
              <span class="stream-wrapper"></span>
            </div>`,
        },
      },
    }}
    style={{height: '370px', borderRadius: '8px'}}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```js
// using JavaScript for a simplified example

chatElementRef.connect = {
  stream: {
    htmlWrappers: {
      default: `
        <div>
          <b>Wrapper title</b>
          <span class="stream-wrapper"></span>
        </div>`,
    },
  },
};
```

</TabItem>
<TabItem value="py" label="Full code">

```js
// using JavaScript for a simplified example

chatElementRef.connect = {
  stream: {
    htmlWrappers: {
      default: `
        <div>
          <b>Wrapper title</b>
          <span class="stream-wrapper"></span>
        </div>`,
    },
  },
};
Object.assign(chatElementRef.style, {height: '370px', borderRadius: '8px'});
chatElementRef.demo = true;
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

## Examples {#moreExamples}

<h3>Suggestion buttons</h3>

Basic suggestion buttons using [Deep Chat Classes](#deepChatClasses).

<ComponentContainer>
  <DeepChatBrowser
    demo={true}
    history={[
      {text: 'How are you doing?', role: 'user'},
      {text: 'Good, how may I help?', role: 'ai'},
      {
        html: `
          <div class="deep-chat-temporary-message">
            <button class="deep-chat-button deep-chat-suggestion-button" style="margin-top: 5px">What do shrimps eat?</button>
            <button class="deep-chat-button deep-chat-suggestion-button" style="margin-top: 6px">Can a shrimp fry rice?</button>
            <button class="deep-chat-button deep-chat-suggestion-button" style="margin-top: 6px">What is a pistol shrimp?</button>
          </div>`,
        role: 'ai',
      },
    ]}
    messageStyles={{html: {shared: {bubble: {backgroundColor: 'unset', padding: '0px'}}}}}
    style={{height: '370px', borderRadius: '8px'}}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```js
// using JavaScript for a simplified example

chatElementRef.history = [
  {
    html: `
      <div class="deep-chat-temporary-message">
        <button class="deep-chat-button deep-chat-suggestion-button" style="margin-top: 5px">What do shrimps eat?</button>
        <button class="deep-chat-button deep-chat-suggestion-button" style="margin-top: 6px">Can a shrimp fry rice?</button>
        <button class="deep-chat-button deep-chat-suggestion-button" style="margin-top: 6px">What is a pistol shrimp?</button>
      </div>`,
    role: 'ai',
  },
];

chatElementRef.messageStyles = {html: {shared: {bubble: {backgroundColor: 'unset', padding: '0px'}}}};
```

</TabItem>
<TabItem value="py" label="Full code">

```js
// using JavaScript for a simplified example

chatElementRef.history = [
  {text: 'How are you doing?', role: 'user'},
  {text: 'Good, how may I help?', role: 'ai'},
  {
    html: `
      <div class="deep-chat-temporary-message">
        <button class="deep-chat-button deep-chat-suggestion-button" style="margin-top: 5px">What do shrimps eat?</button>
        <button class="deep-chat-button deep-chat-suggestion-button" style="margin-top: 6px">Can a shrimp fry rice?</button>
        <button class="deep-chat-button deep-chat-suggestion-button" style="margin-top: 6px">What is a pistol shrimp?</button>
      </div>`,
    role: 'ai',
  },
];

chatElementRef.messageStyles = {html: {shared: {bubble: {backgroundColor: 'unset', padding: '0px'}}}};

Object.assign(chatElementRef.style, {height: '370px', borderRadius: '8px'});

chatElementRef.demo = true;
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

<h3>Controlled responses</h3>

Preset user responses which can be used to give feedback, follow a conversation path or control a service.

<ComponentContainer>
  <DeepChatBrowser
    demo={true}
    history={[
      {text: 'Can I monitor your diet?', role: 'ai'},
      {text: 'Yes', role: 'user'},
      {text: 'Have you drank water?', role: 'ai'},
      {
        html: `
          <div class="deep-chat-temporary-message">
            <button class="deep-chat-button deep-chat-suggestion-button" style="border: 1px solid green">Yes</button>
            <button class="deep-chat-button deep-chat-suggestion-button" style="border: 1px solid #d80000">No</button>
          </div>`,
        role: 'user',
      },
    ]}
    messageStyles={{
      html: {shared: {bubble: {backgroundColor: 'unset', padding: '0px', width: '100%', textAlign: 'right'}}},
    }}
    style={{height: '370px', borderRadius: '8px'}}
    textInput={{disabled: true, placeholder: {text: 'Use buttons to respond'}}}
    submitButtonStyles={{disabled: {container: {default: {opacity: 0, cursor: 'auto'}}}}}
    demo={{
      response: {
        text: 'What about now?',
        html: `
          <div class="deep-chat-temporary-message">
            <button class="deep-chat-button deep-chat-suggestion-button" style="border: 1px solid green">Yes</button>
            <button class="deep-chat-button deep-chat-suggestion-button" style="border: 1px solid #d80000">No</button>
          </div>`,
      },
    }}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```js
// using JavaScript for a simplified example

chatElementRef.history = [
  {
    html: `
      <div class="deep-chat-temporary-message">
        <button class="deep-chat-button deep-chat-suggestion-button" style="border: 1px solid green">Yes</button>
        <button class="deep-chat-button deep-chat-suggestion-button" style="border: 1px solid #d80000">No</button>
      </div>`,
    role: 'user',
  },
];

chatElementRef.messageStyles = {
  html: {shared: {bubble: {backgroundColor: 'unset', padding: '0px', width: '100%', textAlign: 'right'}}},
};
```

</TabItem>
<TabItem value="py" label="Full code">

```js
// using JavaScript for a simplified example

chatElementRef.history = [
  {text: 'Can I monitor your diet?', role: 'ai'},
  {text: 'Yes', role: 'user'},
  {text: 'Have you drank water?', role: 'ai'},
  {
    html: `
      <div class="deep-chat-temporary-message">
        <button class="deep-chat-button deep-chat-suggestion-button" style="border: 1px solid green">Yes</button>
        <button class="deep-chat-button deep-chat-suggestion-button" style="border: 1px solid #d80000">No</button>
      </div>`,
    role: 'user',
  },
];

chatElementRef.messageStyles = {
  html: {shared: {bubble: {backgroundColor: 'unset', padding: '0px', width: '100%', textAlign: 'right'}}},
};

chatElementRef.textInput = {disabled: true, placeholder: {text: 'Use buttons to respond'}};

chatElementRef.submitButtonStyles = {disabled: {container: {default: {opacity: 0, cursor: 'auto'}}}};

chatElementRef.demo = {
  response: {
    text: 'What about now?',
    html: `
      <div class="deep-chat-temporary-message">
        <button class="deep-chat-button deep-chat-suggestion-button" style="border: 1px solid green">Yes</button>
        <button class="deep-chat-button deep-chat-suggestion-button" style="border: 1px solid #d80000">No</button>
      </div>`,
  },
};

Object.assign(chatElementRef.style, {height: '370px', borderRadius: '8px'});
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

<h3>Feedback</h3>

Add feedback buttons to response messages.

<ComponentContainer>
  <DeepChatBrowser
    demo={true}
    history={[
      {text: 'What is mitochondria?', role: 'user'},
      {
        html: `<div class="feedback">
            <div class="feedback-text">The powerhouse of a cell.</div>
            <img class="feedback-icon feedback-icon-positive" src="/img/thumbsUp.svg">
            <img class="feedback-icon feedback-icon-negative" src="/img/thumbsUp.svg">
          </div>`,
        role: 'ai',
      },
      {text: 'What kind of dog should I get?', role: 'user'},
      {
        html: `<div class="feedback">
            <div class="feedback-text">A labrador.</div>
            <img class="feedback-icon feedback-icon-positive" src="/img/thumbsUp.svg">
            <img class="feedback-icon feedback-icon-negative" src="/img/thumbsUp.svg">
          </div>`,
        role: 'ai',
      },
    ]}
    messageStyles={{
      default: {
        shared: {bubble: {maxWidth: '95%', width: '100%', marginTop: '10px'}},
      },
      loading: {
        message: {
          styles: {
            bubble: {width: '1em'},
          },
        },
      },
    }}
    htmlClassUtilities={{
      feedback: {styles: {default: {display: 'flex'}}},
      'feedback-text': {styles: {default: {width: 'calc(100% - 42px)', paddingTop: '2px'}}},
      'feedback-icon': {
        styles: {
          default: {width: '20px', height: '20px', cursor: 'pointer', borderRadius: '5px'},
          hover: {backgroundColor: '#d1d1d1'},
        },
      },
      'feedback-icon-positive': {
        events: {
          click: () => {
            console.log('positive response');
          },
        },
      },
      'feedback-icon-negative': {
        events: {
          click: () => {
            console.log('negative response');
          },
        },
        styles: {default: {transform: 'rotate(180deg)', marginLeft: '3px'}},
      },
    }}
    style={{height: '370px', borderRadius: '8px'}}
    demo={{
      response: {
        html: `
          <div class="feedback">
            <div class="feedback-text">Example response.</div>
            <img class="feedback-icon feedback-icon-positive" src="/img/thumbsUp.svg">
            <img class="feedback-icon feedback-icon-negative" src="/img/thumbsUp.svg">
          </div>`,
      },
    }}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```js
// using JavaScript for a simplified example

chatElementRef.history = [
  {
    html: `<div class="feedback">
        <div class="feedback-text">The powerhouse of a cell.</div>
        <img class="feedback-icon feedback-icon-positive" src="path-to-svg.svg">
        <img class="feedback-icon feedback-icon-negative" src="path-to-svg.svg">
      </div>`,
    role: 'ai',
  },
  {
    html: `<div class="feedback">
      <div class="feedback-text">A labrador.</div>
      <img class="feedback-icon feedback-icon-positive" src="path-to-svg.svg">
      <img class="feedback-icon feedback-icon-negative" src="path-to-svg.svg">
    </div>`,
    role: 'ai',
  },
];

chatElementRef.messageStyles = {
  default: {shared: {bubble: {maxWidth: '95%', width: '100%', marginTop: '10px'}}},
};

chatElementRef.htmlClassUtilities = {
  feedback: {styles: {default: {display: 'flex'}}},
  'feedback-text': {styles: {default: {width: 'calc(100% - 42px)', paddingTop: '2px'}}},
  'feedback-icon': {
    styles: {
      default: {width: '20px', height: '20px', cursor: 'pointer', borderRadius: '5px'},
      hover: {backgroundColor: '#d1d1d1'},
    },
  },
  'feedback-icon-positive': {events: {click: () => console.log('positive response')}},
  'feedback-icon-negative': {
    events: {click: () => console.log('negative response')},
    styles: {default: {transform: 'rotate(180deg)', marginLeft: '3px'}},
  },
};
```

</TabItem>
<TabItem value="py" label="Full code">

```js
// using JavaScript for a simplified example

chatElementRef.history = [
  {text: 'What is mitochondria?', role: 'user'},
  {
    html: `<div class="feedback">
        <div class="feedback-text">The powerhouse of a cell.</div>
        <img class="feedback-icon feedback-icon-positive" src="path-to-svg.svg">
        <img class="feedback-icon feedback-icon-negative" src="path-to-svg.svg">
      </div>`,
    role: 'ai',
  },
  {text: 'What kind of dog should I get?', role: 'user'},
  {
    html: `<div class="feedback">
      <div class="feedback-text">A labrador.</div>
      <img class="feedback-icon feedback-icon-positive" src="path-to-svg.svg">
      <img class="feedback-icon feedback-icon-negative" src="path-to-svg.svg">
    </div>`,
    role: 'ai',
  },
];

chatElementRef.messageStyles = {
  default: {shared: {bubble: {maxWidth: '95%', width: '100%', marginTop: '10px'}}},
  loading: {message: {styles: {bubble: {width: '1em'}}}},
};

chatElementRef.htmlClassUtilities = {
  feedback: {styles: {default: {display: 'flex'}}},
  'feedback-text': {styles: {default: {width: 'calc(100% - 42px)', paddingTop: '2px'}}},
  'feedback-icon': {
    styles: {
      default: {width: '20px', height: '20px', cursor: 'pointer', borderRadius: '5px'},
      hover: {backgroundColor: '#d1d1d1'},
    },
  },
  'feedback-icon-positive': {events: {click: () => console.log('positive response')}},
  'feedback-icon-negative': {
    events: {click: () => console.log('negative response')},
    styles: {default: {transform: 'rotate(180deg)', marginLeft: '3px'}},
  },
};

Object.assign(chatElementRef.style, {height: '370px', borderRadius: '8px'});

chatElementRef.demo = {
  response: {
    html: `
      <div class="feedback">
        <div class="feedback-text">Example response.</div>
        <img class="feedback-icon feedback-icon-positive" src="path-to-svg.svg">
        <img class="feedback-icon feedback-icon-negative" src="path-to-svg.svg">
      </div>`,
  },
};
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

<h3>Custom Element - Chart</h3>

Add a chart component (e.g. using [Google Chart](https://developers.google.com/chart)). Live example for [React](https://codesandbox.io/s/deep-chat-react-chart-ztsgrd?file=/src/App.tsx).

<ComponentContainer>
  <DeepChatBrowser
    demo={true}
    history={[
      {text: 'Can you give me an example chart', role: 'user'},
      {
        html: `
          <div>
            <div style="margin-bottom: 10px">Here is an example chart:</div>
            <google-chart style="width: 220px; height: 200px" data='[["Planet", "Score"], ["Earth", 50], ["Moon", 100], ["Saturn", 80]]' options='{"legend": "none"}'></google-chart>
          </div>
          `,
        role: 'ai',
      },
    ]}
    style={{height: '370px', borderRadius: '8px'}}
    demo={{
      response: {
        html: `
          <google-chart style="width: 220px; height: 200px" data='[["Planet", "Score"], ["Mars", 80], ["Mercury", 100], ["Venus", 50]]' options='{"legend": "none"}'></google-chart>`,
      },
    }}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample code">

```js
// using JavaScript for a simplified example

chatElementRef.history = [
  {
    html: `
      <div>
        <div style="margin-bottom: 10px">Here is an example chart:</div>
        <google-chart
          style="width: 220px; height: 200px"
          data='[["Planet", "Score"], ["Earth", 50], ["Moon", 100], ["Saturn", 80]]'
          options='{"legend": "none"}'>
        </google-chart>
      </div>
      `,
    role: 'ai',
  },
];
```

</TabItem>
<TabItem value="py" label="Full code">

```js
// using JavaScript for a simplified example

chatElementRef.history = [
  {text: 'Can you give me an example chart', role: 'user'},
  {
    html: `
      <div>
        <div style="margin-bottom: 10px">Here is an example chart:</div>
        <google-chart
          style="width: 220px; height: 200px"
          data='[["Planet", "Score"], ["Earth", 50], ["Moon", 100], ["Saturn", 80]]'
          options='{"legend": "none"}'>
        </google-chart>
      </div>
      `,
    role: 'ai',
  },
];

Object.assign(chatElementRef.style, {height: '370px', borderRadius: '8px'});

chatElementRef.demo = {
  response: {
    html: `
      <google-chart
        style="width: 220px; height: 200px"
        data='[["Planet", "Score"], ["Mars", 80], ["Mercury", 100], ["Venus", 50]]'
        options='{"legend": "none"}'>
      </google-chart>`,
  },
};
```

</TabItem>
</Tabs>

<LineBreak></LineBreak>

<h3>Custom Element - Table</h3>

Add an interactive table component (e.g. using [Active Table](https://activetable.io/)).

<ComponentContainer>
  <DeepChatBrowser
    demo={true}
    history={[
      {text: 'Generate a table with info about planets', role: 'user'},
      {
        html: `
          <div>
            <div style="margin-bottom: 10px">Here is a simple example:</div>
            <active-table
              data='[["Planet", "Mass"], ["Earth", 5.97], ["Mars", 0.642], ["Jupiter", 1898]]'
              cellStyle='{"width": "80px"}'
              displayAddNewRow="false"
              displayAddNewColumn="false">
            </active-table>
          </div>`,
        role: 'ai',
      },
    ]}
    style={{height: '370px', borderRadius: '8px'}}
    demo={{
      response: {
        html: `
          <active-table content='[["Planet", "Mass", "Moons"], ["Saturn", 82, 1], ["Neptune", 14, 2], ["Mercury", 0.33, 0]]' cellStyle='{"width": "75px"}' displayAddNewRow="false" displayAddNewColumn="false"></active-table>`,
      },
    }}
  ></DeepChatBrowser>
</ComponentContainer>

<Tabs>
<TabItem value="js" label="Sample 