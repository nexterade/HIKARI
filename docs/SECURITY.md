# Genesis — Security, Privacy & Data Classification Baseline

## Purpose

Dokumen ini adalah source of truth untuk security/privacy baseline universal Genesis.
Project turunan boleh memperketat aturan ini melalui project-specific policy.

## Data classes

### Normal Data
Data project biasa yang memang dimaksudkan untuk diproses atau dipersist secara normal.

### Sensitive Data
Data yang dapat menimbulkan risiko atau kerugian bila bocor. Interface, logging,
export, backup, debugging, fixture, screenshot, dan artifact publik harus memperlakukannya
dengan kehati-hatian tambahan.

### Secret Data
Contoh: password, API key/token, PIN, recovery code, private key, seed phrase, dan
authentication secret. Secret Data tidak boleh dimasukkan plaintext ke canonical project
storage, source control, log, documentation, test fixture, atau release artifact.

## Retention / canonical boundary

Maintenance, indexing, caching, optimization, atau derived-data rebuild tidak boleh
merusak atau diam-diam menghapus canonical source. Jika project memang membutuhkan
penghapusan data, penghapusan tersebut harus merupakan operasi yang eksplisit dan
didefinisikan oleh policy project.

## Secret storage

Genesis tidak menyediakan Secret Vault universal. Jika project membutuhkan secret storage,
capability tersebut harus memiliki boundary terpisah, threat model, encryption/authentication
yang tepat, key-management lifecycle, dan recovery policy. Encoding/Base64 bukan security boundary.

## Artifact boundary

Jangan memasukkan credential nyata, token aktif, private key, recovery code, atau secret
serupa ke test drive, fixture, screenshot, documentation, ZIP release, atau contoh source.
Use synthetic placeholders instead.
