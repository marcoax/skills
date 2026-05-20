---
name: mqtt-error-fixer
description: >
  Analyze MQTT pipeline errors from the CariSupport project and propose surgical fixes following project best practices.
  Use when the user provides a Symfony log error, exception trace, or error description related to MQTT message processing
  (PacketHandler, InboundFactory, GetMachineConfiguration, Header, VendingDataResponse, AckNack, etc.).
  Triggers: "analisi errore mqtt", "fix errore mqtt", "errore pipeline mqtt", "errore pacchetto", "MQTT exception",
  "InvalidArgumentException content should be", "getSupportUser on null", "aggregate not found", "BSON null".
---

# SKILL: mqtt-error-fixer

You are a senior developer on the CariSupport project. Analyze MQTT pipeline errors and propose minimal, surgical fixes following established project patterns.

## Workflow

### Step 1 — Identify the error
Read the error provided by the user. Extract:
- Exception class and message
- File and line number
- Stack trace (especially the top 3-5 frames)

Classify into one of the known error types below.

### Step 2 — Trace the pipeline
The MQTT inbound pipeline is:
```
MQTT broker
  → PacketHandler::handle()                    [www/src/MQTT/PacketHandler.php]
  → InboundMessageFactory::create($payload)    [www/src/MQTT/Message/InboundMessageFactory.php]
      → Message::create()                      [www/src/MQTT/Message/Message.php]
          → Header::create()                   [www/src/MQTT/Message/Header.php]
          → InboundFactory::create()           [www/src/MQTT/Message/Content/InboundFactory.php]
              → {CommandClass}::create()       [www/src/MQTT/Message/Content/Inbound/]
  → MessageRepository::save($message)
  → dispatch(MessageReceivedEvent)
      → AllMessagesIntoEventBus::onMessageReceived()   [www/src/MQTT/Listener/AllMessagesIntoEventBus.php]
          → Processors / Broadway events
```

Read the relevant files before proposing any fix.

### Step 3 — Propose the fix
Always:
- Show WHY the error occurs (one sentence)
- Show the specific code change (before/after)
- List all files to modify
- Reference the established pattern if one exists

---

## Known Error Types & Fix Patterns

### Pattern A — AckNack 1-byte (machine busy/NACK response)
**Symptom:** `InvalidArgumentException: content should be X bytes instead of 1`
**Cause:** Machine sent a 1-byte AckNack (BUSY=4, NACK=2) instead of a full payload. The Inbound class tries to parse it as a full response.
**Established pattern:** `GetGrinderCalibration::create()` lines 94-96.

**Fix — step 1: Inbound `create()` method:**
```php
public static function create(Payload $payload)
{
    // Detect AckNack response (machine busy/error) before full parsing
    if ($payload->getBinContent()->length() === 1) {
        return AckNack::create($payload);
    }
    // ... rest unchanged ...
}
```

**Fix — step 2: `AllMessagesIntoEventBus` guard:**
```php
// Add && $message->isOk() to skip NACK/BUSY responses
if ($message->isCommandOf(CommandTypes::GET_MACHINE_CONFIGURATION) && $message->isOk()) {
```

**AckNack values** (from `AckNack.php`): ACK=1, NACK=2, BUSY=4, LOCK=5, UNLOCK=6
**`Message::isOk()`** returns false when content is AckNack with value != ACK.

After fix, update `TECHNICAL_REFERENCE.md` table "Commands that implement this pattern".

---

### Pattern B — Null read model (getSupportUser on null)
**Symptom:** `Call to a member function getSupportUser() on null` or `getX() on null` after `findByMachineSerial()`
**Cause:** Read model repository returns `null` when machine is not yet in MongoDB (not synced). Code assumes non-null.
**Established pattern:** `CreateErrorOnErrorOccurredProcessor.php:33-36`, `CleaningEventProcessor.php:82-84`.

**Fix:**
```php
$machine = $this->machineReadModelRepository->findByMachineSerial($event->getSerial());
if ($machine === null) {
    return;
}
```

---

### Pattern C — Invalid date format in binary payload
**Symptom:** `InvalidArgumentException: Invalid date format` from `BinaryContent::dateTime()`
**Cause:** Machine sent a malformed timestamp. `dateTime()` throws; no caller catches it.
**Decision (from project grill session):** Do NOT change `dateTime()`. Add try/catch in the caller.

**Fix in `Header::create()`:**
```php
try {
    $timestamp = $content->dateTime(14);
} catch (\InvalidArgumentException $e) {
    // log warning, skip entire message
    return null;
}
```
Then ensure `Message::create()` handles null Header (return null → PacketHandler skips).

**Fix in `VendingDataResponse::fromContentAndModelCode()`:**
```php
try {
    $timestamp = $content->dateTime(4);
} catch (\InvalidArgumentException $e) {
    return null; // skip this vending record
}
```

---

### Pattern D — NIL UUID aggregate not found
**Symptom:** `Aggregate with id '00000000-0000-0000-0000-000000000000' not found`
**Cause:** `BySerialRepository::load()` receives a NIL UUID serial (machine not yet registered in event store).
**Fix:** In `BySerialRepository::load()`, check `$pair->isNull()` after `IdSerialPairRepository::find()`. If null UUID, return null and log warning. Change return type to `?Machine`. Update all callers to add `if ($aggregate === null) { return; }`.

---

### Pattern E — SMTP broken pipe / timeout (email send failure)
**Symptom:** `Swift_TransportException: Expected response code 250` or `Broken pipe`
**Cause:** SMTP connection drops mid-send. No catch around `$this->mailer->send()`.
**Fix in `Mailer.php`:**
```php
try {
    $this->mailer->send($message);
} catch (\Swift_TransportException $e) {
    $this->logger->error('Email send failed: ' . $e->getMessage(), [
        'to' => $to,
        'subject' => $subject,
    ]);
}
```
No retry. Email loss is acceptable to preserve MQTT pipeline stability.

---

### Pattern F — BSON null bytes in snapshot keys
**Symptom:** `MongoException: BSON keys cannot contain null bytes`
**Cause:** Serialized aggregate snapshot contains PHP internal class property names with null bytes (e.g., `\0ClassName\0property`).
**Fix in `MongoDbSnapshotRepository::normalizeSnapshot()`:** Add a private `sanitizeKeys(array $data)` helper that recursively strips null bytes from array keys using `str_replace("\0", '', $key)`. Apply after serialization, before persistence.

---

## Code Quality Rules for All Fixes

- **Minimal surface**: change only what is needed. Do not refactor surrounding code.
- **No top-level catch in PacketHandler**: individual targeted fixes only.
- **Static methods have no logger**: log warnings/errors at the first non-static level that has `LoggerInterface` injected (usually `PacketHandler` or a Processor).
- **PHP 7.2**: no typed properties, no union types, no named arguments.
- **Nullable return types** (`?Type`) are fine in PHP 7.2.
- **No new unit tests required** for purely defensive null checks driven by production errors. Tests are recommended for fixes involving parsing logic changes (Pattern A, C).

## Reference Files

| Area | File |
|---|---|
| MQTT pipeline docs | `TECHNICAL_REFERENCE.md` — sections "Working with MQTT Messages", "MQTT Error Handling: AckNack 1-byte Pattern", "Appendix: MQTT Product Data Flow" |
| AckNack reference | `www/src/MQTT/Message/Content/Inbound/AckNack.php` |
| Established AckNack fix | `www/src/MQTT/Message/Content/Inbound/GetGrinderCalibration.php` |
| AllMessagesIntoEventBus | `www/src/MQTT/Listener/AllMessagesIntoEventBus.php` |
| PacketHandler | `www/src/MQTT/PacketHandler.php` |
| Header parsing | `www/src/MQTT/Message/Header.php` |
| Binary content | `www/src/MQTT/Message/BinaryContent.php` |
| Null check examples | `www/src/Machine/Communication/Processor/CreateErrorOnErrorOccurredProcessor.php` |
| Mailer | `www/src/Mailer.php` |
| Snapshot repo | `www/src/Symfony/MongoDb/MongoDbSnapshotRepository.php` |
