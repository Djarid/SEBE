# Transfer Risk Assessment (TRA)

## GPEW Policy Working Group Digital Platform

**Reference:** GPEW-TRA-2026-001
**Version:** 1.0 (DRAFT)
**Author:** Jason Huxley
**Date:** 13 March 2026
**Status:** DRAFT for GPEx/AFCom review
**Related document:** GPEW-DPIA-2026-001

---

*A TRA (referred to in the Data (Use and Access) Act 2025 as a "data
protection test") is required when making a "restricted transfer" of personal
data outside the UK. This document assesses whether any restricted transfers
arise from the proposed platform architecture, and documents the conclusion.*

## 1. Overview

The ICO's TRA framework requires organisations to assess risk when personal
data is transferred to a country outside the UK that does not have an adequacy
regulation. The assessment considers whether the legal framework in the
recipient country provides essentially equivalent protection to UK GDPR.

This TRA covers the GPEW policy working group digital platform comprising:

- **(a) Discourse** (self-hosted, discussion forum)
- **(b) Antragsgruen** (self-hosted, motion/amendment/voting management)
- **(c) Static public website** (no personal data)

## 2. Identification of Transfers

### 2.1 Primary data processing

| Component | Hosting location | Data controller | International transfer? |
|---|---|---|---|
| Discourse server | UK VPS (UK data centre) | GPEW | NO |
| Antragsgruen server | UK VPS (UK data centre) | GPEW | NO |
| Database (PostgreSQL) | Same UK VPS | GPEW | NO |
| Database (MySQL) | Same UK VPS | GPEW | NO |
| Backups | Separate UK storage | GPEW | NO |
| Static public site | UK hosting | GPEW | NO |

All personal data is stored and processed on servers physically located in the
United Kingdom, operated by a UK data controller (GPEW, registered in England
and Wales).

### 2.2 Third-party sub-processors

| Sub-processor | Service | Location | Transfer? |
|---|---|---|---|
| VPS hosting provider | Infrastructure | UK data centre | NO (1) |
| Domain registrar | DNS | Varies | NO (2) |
| Let's Encrypt | TLS certificates | US | NO (3) |

**Notes:**

1. VPS provider hosts the physical server but does not access personal data
   stored on encrypted volumes. Provider to be selected from UK-domiciled
   companies or companies with UK data centres operating under UK GDPR.
   Recommended: Hetzner (German, EU adequate), OVH (French, EU adequate),
   or UK-only provider.

2. DNS records do not contain personal data. Domain registration data
   (registrant contact) is the party's public contact information, not
   platform user data.

3. Let's Encrypt's ACME protocol involves exchanging cryptographic challenges
   for TLS certificate issuance. No personal data is transferred. Certificate
   metadata (domain name, issuance date) is published in Certificate
   Transparency logs by design; this contains no personal data.

### 2.3 Software update channels

| Software | Update source | Data sent | Transfer? |
|---|---|---|---|
| Discourse | GitHub (US) | Server IP address during download | NO (1) |
| Antragsgruen | GitHub (US) | Server IP address during download | NO (1) |
| OS packages | Debian/Ubuntu mirrors (various) | Server IP address | NO (1) |

1. Downloading software updates involves the server's IP address being logged
   by the update source. A server IP address may constitute personal data in
   some contexts, but here the IP belongs to a VPS provider (not a natural
   person), the download is initiated by a system administrator, and no user
   personal data is transmitted. This does not constitute a restricted transfer
   of personal data under UK GDPR.

### 2.4 Email delivery

| Service | Data transferred | Destination | Transfer? |
|---|---|---|---|
| Platform notifications | Recipient email, notification subject/body | Recipient's email provider | POSSIBLY (1) |

1. When Discourse or Antragsgruen sends notification emails to members (e.g.
   "new reply to your topic"), the email content is delivered via SMTP to the
   recipient's email provider. If a member uses a non-UK email provider (e.g.
   Gmail, Outlook.com), the email content (which may reveal political opinion
   through the notification subject or preview) transits to US servers.

   However:

   - This is a standard email delivery, not a deliberate transfer by the data
     controller to a third-country recipient.
   - The member has voluntarily provided their email address and chosen their
     email provider.
   - The ICO's guidance states that where data is sent to an individual at
     their own request (or to an address they have provided), this is
     generally not a restricted transfer by the controller.
   - **Mitigation:** offer members the option to disable email notifications
     entirely and use the platform's web interface only. Encourage use of
     UK/EU email providers (e.g. Proton Mail, Tuta).

   **Assessment:** no restricted transfer by the data controller. The member's
   own choice of email provider determines where notifications are delivered.
   This is analogous to posting a letter to an address the recipient has
   provided.

## 3. Conclusion: Is a Full TRA Required?

A full TRA (data protection test) is only required when a restricted transfer
is identified, i.e. when the data controller or processor deliberately
transfers personal data to a recipient in a country outside the UK without an
adequacy regulation.

**Summary of findings:**

| Data flow | Restricted transfer? | TRA required? |
|---|---|---|
| Platform hosting | No (UK servers) | No |
| Database storage | No (UK servers) | No |
| Backups | No (UK storage) | No |
| Software updates | No (no personal data transferred) | No |
| Email notifications | No (member-initiated, member's chosen provider) | No |
| Static public site | No (no personal data) | No |

**CONCLUSION: No restricted transfers of personal data arise from the proposed
architecture. A full TRA is NOT required.**

This is a direct consequence of the self-hosted, UK-only architecture
decision. The architecture was specifically designed to eliminate international
transfers and the associated compliance burden.

## 4. Comparison With Rejected Alternatives

For completeness, this section documents why the self-hosted architecture was
chosen over alternatives that WOULD require a TRA.

### 4.1 CDCK-hosted Discourse (REJECTED)

CDCK, Inc. is a US corporation (Delaware). Under the CLOUD Act (Clarifying
Lawful Overseas Use of Data Act, 2018), US law enforcement can compel CDCK to
produce data regardless of where servers are physically located. Even CDCK's
EU-hosted Enterprise tier does not escape US jurisdiction because CDCK's
corporate domicile is the US.

A TRA for this option would need to assess:

- US surveillance laws (FISA 702, Executive Order 12333, CLOUD Act)
- Adequacy status: US does not have a UK adequacy regulation for general data
  (the UK Extension to the EU-US Data Privacy Framework covers only certified
  organisations, and CDCK's certification status would need verification)
- Supplementary measures required: encryption where CDCK cannot access
  plaintext (not possible with a hosted SaaS platform where the provider
  operates the database)

**Outcome: HIGH RISK.** Special category data (political opinion) of UK
political party members on US-controlled infrastructure subject to US
intelligence access. Supplementary measures insufficient. Transfer likely not
permissible without explicit consent from each data subject.

### 4.2 Microsoft Teams/SharePoint (CURRENTLY IN USE — FLAGGED)

GPEW currently uses Microsoft Teams/SharePoint for some policy working group
coordination. Microsoft Corporation is a US company subject to the CLOUD Act.
The same analysis as 4.1 applies.

**Recommendation:** GPEW should conduct a separate TRA for its existing use of
Microsoft Teams/SharePoint for policy working group data, or migrate this
activity to the proposed self-hosted platforms. The existing arrangement may
not be compliant for Art.9 special category data processing.

### 4.3 Google Workspace (REJECTED)

Same analysis as 4.1. Google LLC is a US company subject to the CLOUD Act.
Rejected for the same reasons.

### 4.4 Antragsgruen hosted service (motion.tools) (VIABLE ALTERNATIVE)

The hosted Antragsgruen service runs on EU servers operated by Tobias Hossl, a
German individual. Germany has a UK adequacy regulation. No CLOUD Act exposure
(not a US company).

A TRA for this option would conclude: **ADEQUATE PROTECTION.** The EU
(including Germany) has UK adequacy. No supplementary measures required.

This option is viable if GPEW lacks capacity to self-host Antragsgruen but
still wants to avoid US jurisdiction.

## 5. Recommendations

1. **PROCEED** with self-hosted UK architecture as proposed. No TRA required
   for the platform itself.

2. **FLAG** the existing Microsoft Teams/SharePoint usage for policy working
   group data. GPEW should either:
   (a) conduct a TRA for Teams/SharePoint, which will likely identify high
   risk for Art.9 data, OR
   (b) migrate policy working group activity to the proposed self-hosted
   platforms, eliminating the transfer.

3. **DOCUMENT** this assessment alongside the DPIA (GPEW-DPIA-2026-001) as
   evidence that international transfer risk was considered and eliminated by
   design.

4. **REVIEW** if the hosting provider changes, if any third-party integrations
   are added, or if the platform architecture is modified in a way that
   introduces cross-border data flows.

## 6. Sign-off

| Role | Name | Date | Signature |
|---|---|---|---|
| DPO advice | *PENDING* | | |
| Approved by (GPEx) | | | |
| Approved by (AFCom) | | | |

---
