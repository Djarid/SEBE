# Conversation Archive

> Process for importing, searching, and exporting multi-platform conversation logs.

## Objective

Archive campaign-relevant conversations from WhatsApp, Discord, and email
into a searchable database. Resolve participants across platforms. Tag
messages with metadata (claims, concessions, action items). Export in full
or anonymised (Chatham House Rule) format.

## Architecture (Option C: Dual Database)

- **Primary archive:** `~/sebe-data/conversations.db` (outside git repo)
- **Index/summaries:** Key excerpts logged to `data/memory.db` via memory system
- **Privacy:** Phone numbers stored in DB for resolution, never in exports

## Workflow

### Import

1. Export chat from WhatsApp (Settings > Export Chat > Without Media)
2. Place .txt file in `~/sebe-data/imports/whatsapp/`
3. Run import:
   ```bash
   python -m tools.conversations.importer \
     --platform whatsapp \
     --file ~/sebe-data/imports/whatsapp/chat.txt \
     --campaign "Campaign Name" \
     --subject "Thread Subject"
   ```
4. Optionally link participants to memory.db contacts:
   ```bash
   python -m tools.conversations.importer \
     --platform whatsapp \
     --file chat.txt \
     --campaign "Name" \
     --contact-map '{"Jason Huxley": 1, "+44 7977 490410": 5}'
   ```

### Search

```bash
python -m tools.conversations.db --action search --query "metering"
python -m tools.conversations.db --action search --query "metering" --campaign "Sci Tech SEBE Review"
```

### Tag

```bash
python -m tools.conversations.db --action tag-message --id 42 --tag-type claim --value "SEBE will raise £34-46B"
python -m tools.conversations.db --action tag-message --id 55 --tag-type concession --value "Existing BSC data sufficient"
```

### Export

```bash
# Full transcript
python -m tools.conversations.exporter --conversation-id 1 --format markdown

# Anonymised (Chatham House Rule)
python -m tools.conversations.exporter --conversation-id 1 --format anonymised -o export.md

# Summary with tagged highlights
python -m tools.conversations.exporter --conversation-id 1 --format summary
```

## Supported Platforms

- WhatsApp (.txt export) — implemented
- Discord (JSON export) — planned
- Email (MIME/EML) — planned
- Signal (.md export) — planned

## Privacy

- Conversations DB stored outside git repo at `~/sebe-data/`
- Phone numbers in DB for participant resolution only
- Exports use display names, never raw identifiers
- Anonymised format pseudonymises names with salted SHA256
- Phone numbers in message content redacted in anonymised exports
- Salt stored in `.env` as `CONVERSATIONS_HASH_SALT`

## Edge Cases

- Multi-line WhatsApp messages (continuation lines without timestamps)
- Preamble text before first timestamp in WhatsApp exports
- System messages (joins, leaves, deletions)
- Same person appearing as phone number and display name
- Deduplication on reimport (use `--force` to overwrite)
