---
summary: age file encryption (Filippo Valsorda) — CLI usage, recipients, SSH keys, programmatic use, E2E sync patterns
tags: [encryption, cli, security, ssh, e2e]
related: [git-workflow, github-actions]
source: synthetic-memory/age-encryption.md
---

# age Encryption for File-Level E2E

## Overview

`age` is a simple, modern file encryption tool by Filippo Valsorda. It replaces GPG for most use cases with a simpler UX and smaller attack surface.

- Repository: `github.com/FiloSottile/age`
- Spec: age-encryption.org
- No config files, no key servers, no trust models.

## Installation

```bash
brew install age                    # macOS
apt install age                     # Debian/Ubuntu
go install filippo.io/age/cmd/...@latest  # from source
```

## Key Generation

```bash
age-keygen -o key.txt
# Output:
# Public key: age1xxxxxxxxxx...
# Private key saved to key.txt
```

The key file contains one line: `AGE-SECRET-KEY-1...`. The public key is printed to stderr.

## Encryption & Decryption

```bash
# Encrypt to a recipient's public key
age -r age1recipient... -o secret.age plaintext.txt

# Encrypt to multiple recipients
age -r age1alice... -r age1bob... -o secret.age plaintext.txt

# Decrypt with private key
age -d -i key.txt -o plaintext.txt secret.age
```

## Passphrase Encryption

```bash
# Encrypt with passphrase (interactive)
age -p -o secret.age plaintext.txt

# Decrypt (prompts for passphrase)
age -d -o plaintext.txt secret.age
```

Uses scrypt for key derivation. Suitable for backups but not programmatic use.

## Recipients File

Store multiple public keys in a file:

```
# alice
age1alice...
# bob
age1bob...
```

```bash
age -R recipients.txt -o secret.age plaintext.txt
```

## SSH Key Support

age can encrypt to SSH keys:

```bash
age -r "ssh-ed25519 AAAA..." -o secret.age plaintext.txt
age -d -i ~/.ssh/id_ed25519 secret.age
```

Supports `ssh-ed25519` and `ssh-rsa` keys.

## Streaming & Pipes

age works with stdin/stdout:

```bash
tar czf - docs/ | age -r age1... > docs.tar.gz.age
age -d -i key.txt < docs.tar.gz.age | tar xzf -
```

## Programmatic Use (Go / Node.js)

### Go

```go
import "filippo.io/age"
```

### Node.js

Use `age-encryption` npm package:

```typescript
import { Encrypter, Decrypter } from 'age-encryption';

const encrypted = await new Encrypter()
  .addRecipient(publicKey)
  .encrypt(plaintext);

const decrypted = await new Decrypter()
  .addIdentity(privateKey)
  .decrypt(encrypted);
```

## Use Cases for E2E Sync

For syncing encrypted data across devices:

1. Generate a keypair per device.
2. Encrypt shared secrets to all device public keys (multi-recipient).
3. Store encrypted blobs in cloud storage (S3, Supabase Storage, git repo).
4. Each device decrypts with its own private key.
5. Key rotation: re-encrypt all files to the new recipient set.

## Security Properties

- X25519 key agreement + ChaCha20-Poly1305 AEAD.
- No forward secrecy (same keypair reused). For forward secrecy, rotate keys.
- No signatures — age provides confidentiality, not authentication. Use `minisign` or `signify` for signatures.

## Related

- [git-workflow](git-workflow.md) — encrypted secrets workflow in repos (avoid checking in plaintext credentials; `age` for committing encrypted blobs).
- [github-actions](github-actions.md) — CI secrets storage; `age` complements GitHub-managed secrets when content must be encrypted at rest in the repo itself.
