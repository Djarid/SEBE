# Data Protection Impact Assessment (DPIA)

## GPEW Policy Working Group Digital Platform

**Reference:** GPEW-DPIA-2026-001
**Version:** 1.0 (DRAFT)
**Author:** Jason Huxley
**Date:** 13 March 2026
**Status:** DRAFT for GPEx/AFCom review

---

*This DPIA follows the ICO 7-step process (UK GDPR Art.35). The ICO template
structure is used. GPEW should verify whether a designated DPO exists and
obtain their formal advice before sign-off.*

## Step 1: Need for a DPIA

Processing triggers:

- **Special category data:** political opinion (Art.9) — MANDATORY TRIGGER
- **Large-scale processing** of members (2,000 policy working group members)
- **Data concerning elected officials** (MPs, councillors)

**Conclusion: DPIA is REQUIRED.**

## Step 2: Description of Processing

### 2.1 Nature of processing

GPEW proposes to deploy two self-hosted platforms for policy working group
coordination:

**(a) Discourse** (GPL-2.0, discourse.org)
Purpose: ongoing discussion, knowledge sharing, informal collaboration
between policy working groups.

**(b) Antragsgruen / Motion.Tools** (AGPL-3.0, motion.tools)
Purpose: formal motion submission, line-by-line amendments, voting,
resolution drafting for policy conferences.

**(c) Static public website** (Hugo or similar static site generator)
Purpose: read-only publication of approved policy positions. No user
accounts, no interaction, no personal data processing.

All platforms self-hosted on UK-based infrastructure (VPS provider with UK
data centre, e.g. Hetzner UK, OVH UK, or similar). No data leaves UK
jurisdiction at any point.

**Data collected:**

- Account data: name, email address, password hash, 2FA tokens
- Content data: posts, comments, motions, amendments, votes
- Metadata: IP addresses, timestamps, session data, edit history
- Moderation data: flags, admin actions, audit logs

**How data is collected:**

- User registration (invite-only, verified against GPEW membership)
- User-generated content (posts, motions, amendments, comments, votes)
- Automated logging (IP, timestamps, session management)

**Storage:**

- Discourse: PostgreSQL database + Redis cache on UK VPS
- Antragsgruen: MySQL/MariaDB database on UK VPS
- Backups: encrypted, stored on separate UK infrastructure
- No cloud storage services used

**Access:**

- Members: own content + content shared with their groups
- Administrators (2-3 designated party officers): all content including
  private messages, moderation logs, user data
- Staff: elevated permissions as configured per role
- No third-party access. No data processors. No analytics services.

**Retention:**

- Active accounts: retained for duration of party membership
- Post content: retained indefinitely (policy record)
- IP logs: 90 days then purged
- Session data: purged on logout or after 30 days inactivity
- Deleted accounts: personal data anonymised within 30 days, content
  optionally retained with attribution removed

**Security measures:**

- 2FA mandatory for all accounts (hardware keys for admins)
- HTTPS/TLS for all connections
- Discourse: PBKDF2 (600k iterations) password hashing, CSP headers,
  CSRF protection, XSS sanitisation
- Antragsgruen: CAPTCHA after failed logins, TOTP 2FA support
- SSH key-only access to servers
- Weekly encrypted backups tested annually
- Admin audit logging enabled on both platforms

### 2.2 Scope of processing

- **Personal data types:** name, email, IP address, political opinions
  (expressed through posts, votes, motions), membership status
- **Special category data:** political opinion (Art.9(1))
- **Volume:** approximately 2,000 data subjects (policy working group members)
- **Frequency:** continuous (always-on platforms)
- **Duration:** ongoing for life of the platforms
- **Geography:** United Kingdom only

**User categories and approximate numbers:**

| User type | Approximate number | Access pattern |
|---|---|---|
| Members (policy information) | ~1,200 | Read-mostly, occasional comment |
| Members (casual engagement) | ~400 | Regular discussion participation |
| Members (expert/frequent) | ~200 | Frequent contribution, motion drafting |
| Members (needs support) | ~100 | Guided participation with training |
| MPs | ~4 | Green Party MPs |
| Councillors | ~50-100 | Green Party elected councillors |
| Staff | ~5-10 | Party employees with platform access |
| Non-members/public | 0 interactive | Static site only (no accounts) |

### 2.3 Context of processing

- Data subjects are GPEW members who have voluntarily joined policy working
  groups. They expect their contributions to be seen by other members within
  the platform.
- Elected officials (MPs, councillors) participate as party members. Their
  posts on this platform are party communications, not parliamentary/council
  business. Parliamentary privilege does not apply.
- Processing involves political opinion, which is special category data.
  This is inherent to the purpose of a political party platform.
- No children are expected (GPEW membership requires age 14+; policy working
  groups are adult-oriented; platform is invite-only with verified membership).
- No public-facing interactive element. Non-members access a separate static
  website with no accounts, no personal data collection, and no user
  interaction.

### 2.4 Purpose of processing

- Enable GPEW members to collaboratively develop party policy
- Provide structured workflow for motions, amendments, and votes
- Maintain an accessible knowledge base of policy discussions
- Support democratic participation within the party
- Replace or supplement existing tools (email lists, WhatsApp groups,
  SharePoint) with a purpose-built, party-controlled platform

**Legitimate interest:** the party has a legitimate interest in providing its
members with tools for democratic policy development. Members expect this as
part of their party membership.

**Art.9(2)(d) exemption:** processing is carried out by a not-for-profit body
with a political aim, relating solely to members or former members, and data
is not disclosed outside the body without consent. This exemption covers all
interactive platform processing.

## Step 3: Consultation

### 3.1 Individual consultation

Members should be consulted before deployment. Recommended approach:

- Present the platform proposal at a policy working group meeting (or via
  existing communication channels)
- Publish a plain-language summary of this DPIA
- Provide a 4-week consultation period for member feedback
- Document feedback and any changes made in response

### 3.2 Stakeholder consultation

- **GPEx** (Green Party Executive): approval authority
- **AFCom** (Finance Committee): budget approval for hosting costs
- **DPO** (if appointed): formal advice required before sign-off
- **IT/digital volunteers:** technical review of hosting architecture
- **Policy Development Committee:** operational requirements

## Step 4: Necessity and Proportionality

### 4.1 Lawful basis

**Interactive platforms (Discourse, Antragsgruen):**

- Art.6(1)(f): legitimate interests of the data controller (party) in
  facilitating democratic policy development for its members. Members
  reasonably expect the party to provide such tools.
- Art.9(2)(d): processing by a not-for-profit body with a political aim,
  relating to members, with no external disclosure.

**Static public site:**

- No personal data processed. No lawful basis required.

### 4.2 Data minimisation

- Only data necessary for platform function is collected
- No analytics tracking on either platform
- No third-party integrations or data sharing
- IP logs purged after 90 days
- Registration collects only: name, email, password
- No requirement for date of birth, address, or other demographics
- Votes in Antragsgruen can be configured as anonymous

### 4.3 Alternatives considered

| Alternative | Reason rejected |
|---|---|
| WhatsApp/Signal groups | No structured policy workflow; no amendment tracking; data on US servers (WhatsApp); groups limited to 1,024 members |
| Google Workspace | US company, CLOUD Act exposure, special category data on US-controlled infrastructure |
| Microsoft Teams/SharePoint | US company, CLOUD Act exposure (GPEW currently uses this, identified as a risk) |
| CDCK-hosted Discourse | US company, CLOUD Act applies regardless of server location |
| Email-only workflow | Does not scale to 2,000 members; no voting, no amendment tracking, no searchable archive |
| No platform (status quo) | Policy development remains fragmented across WhatsApp, email, SharePoint; no party control over data sovereignty |

The proposed self-hosted architecture is the least invasive option that meets
the functional requirements while maintaining UK data sovereignty.

### 4.4 Individual rights

- **Right of access:** both platforms support user data export (CSV/JSON)
- **Right to erasure:** both platforms support account deletion and content
  anonymisation. Documented process to be created.
- **Right to rectification:** users can edit their own content at any time
- **Right to data portability:** export functionality available
- **Right to object:** users can leave the platform at any time; account
  deletion process documented
- **No automated decision-making. No profiling.**

## Step 5: Risk Identification and Assessment

Risk matrix: Likelihood (Remote / Possible / Probable) x Severity (Minimal /
Significant / Severe)

### Risk 1: Unauthorised access to political opinion data

- **Likelihood:** Possible
- **Severity:** Severe (Art.9 special category data)
- **Overall:** HIGH
- **Source:** External attack, compromised admin account, or insider threat
- **Impact:** Exposure of members' political positions, potential for
  discrimination, reputational damage, chilling effect on participation

### Risk 2: Admin abuse of privilege

- **Likelihood:** Remote (small, trusted admin team)
- **Severity:** Significant (admins can read PMs, edit posts, view votes)
- **Overall:** MEDIUM
- **Source:** Administrator with legitimate access exceeding their authority
- **Impact:** Breach of trust, exposure of private deliberations

### Risk 3: Data breach via unpatched vulnerability

- **Likelihood:** Possible (self-hosted requires timely patching)
- **Severity:** Severe (full database exposure)
- **Overall:** HIGH
- **Source:** Known vulnerability in Discourse/Antragsgruen/underlying OS
- **Impact:** Complete data exfiltration

### Risk 4: Loss of data (backup failure)

- **Likelihood:** Remote (with proper backup regime)
- **Severity:** Significant (loss of policy development history)
- **Overall:** LOW
- **Source:** Server failure, hosting provider insolvency, human error
- **Impact:** Loss of institutional knowledge, disruption to policy work

### Risk 5: Function creep (platform used beyond stated purpose)

- **Likelihood:** Possible
- **Severity:** Minimal to Significant
- **Overall:** MEDIUM
- **Source:** Gradual expansion of use beyond policy working groups
- **Impact:** Processing exceeds scope of this DPIA, Art.9(2)(d) exemption
  may no longer apply if data disclosed externally

### Risk 6: Sysadmin bus factor

- **Likelihood:** Possible (small volunteer team)
- **Severity:** Significant (platform becomes unmaintained)
- **Overall:** MEDIUM
- **Source:** Key volunteers become unavailable
- **Impact:** Unpatched vulnerabilities, inability to respond to SARs,
  platform degradation

### Risk 7: Disclosure of special category data to non-members

- **Likelihood:** Remote (architecture prevents this by design)
- **Severity:** Severe (Art.9(2)(d) exemption lost)
- **Overall:** LOW (due to static site architecture)
- **Source:** Misconfiguration, accidental publication of member content
- **Impact:** Loss of Art.9 exemption, regulatory exposure

## Step 6: Mitigating Measures

### Risk 1 (Unauthorised access) — HIGH to MEDIUM

- 2FA mandatory for all accounts, hardware keys for admins
- Invite-only registration verified against membership database
- Encrypted at rest (full-disk encryption on VPS)
- Encrypted in transit (TLS 1.3)
- Fail2ban or equivalent brute-force protection
- Admin audit logging
- Annual penetration test (or at minimum, automated vulnerability scan)
- **Residual risk: MEDIUM** (cannot fully eliminate external attack risk)

### Risk 2 (Admin abuse) — MEDIUM to LOW

- Limit admin accounts to 2-3 designated party officers
- Admin audit log reviewed monthly by a non-admin party officer
- Clear admin access policy documented and signed
- Admin accounts require hardware key 2FA
- **Residual risk: LOW**

### Risk 3 (Unpatched vulnerability) — HIGH to MEDIUM

- Designate 2-3 sysadmin volunteers with documented update procedures
- Subscribe to Discourse and Antragsgruen security mailing lists
- Monthly maintenance window for updates
- Automated security update notifications
- OS-level unattended security updates enabled
- **Residual risk: MEDIUM** (dependent on volunteer availability)

### Risk 4 (Data loss) — LOW to VERY LOW

- Weekly automated encrypted backups to separate UK storage
- Annual backup restore test
- Database replication if budget allows
- **Residual risk: VERY LOW**

### Risk 5 (Function creep) — MEDIUM to LOW

- This DPIA explicitly limits scope to policy working group coordination
- Any expansion of use requires DPIA review
- Terms of use for the platform state its purpose
- Annual review of processing activities
- **Residual risk: LOW**

### Risk 6 (Bus factor) — MEDIUM to LOW

- Document all server administration procedures
- Ensure 2-3 people have server access credentials (in sealed envelope or
  password manager accessible to designated officers)
- Annual handover/review of sysadmin documentation
- **Residual risk: LOW**

### Risk 7 (Special category disclosure) — LOW to VERY LOW

- Static public site is architecturally separate (one-way publish)
- Editorial approval required before any content reaches public site
- Published content contains party positions, not individual member opinions
- Regular audit of public site content against source material
- **Residual risk: VERY LOW**

## Step 7: Conclusion and Sign-off

### 7.1 Residual risk summary

| Risk | Initial | After mitigation | Status |
|---|---|---|---|
| Unauthorised access | HIGH | MEDIUM | Accepted (inherent to any online platform) |
| Admin abuse | MEDIUM | LOW | Accepted |
| Unpatched vulnerability | HIGH | MEDIUM | Accepted (monitor; dependent on volunteer capacity) |
| Data loss | LOW | VERY LOW | Accepted |
| Function creep | MEDIUM | LOW | Accepted |
| Bus factor | MEDIUM | LOW | Accepted |
| Special category disclosure | LOW | VERY LOW | Accepted |

### 7.2 Overall assessment

No HIGH residual risks remain after mitigation. ICO consultation is NOT
required (Art.36 only applies if high risk cannot be mitigated).

The processing can proceed subject to:

1. Confirmation of DPO status (appoint or confirm existing DPO)
2. DPO review and documented advice on this DPIA
3. GPEx approval
4. AFCom budget approval for hosting costs (~£25-40/month)
5. Member consultation (4-week period)
6. Privacy notice published before platform goes live
7. Admin access policy documented and signed by designated officers

### 7.3 Review schedule

This DPIA must be reviewed:

- Annually (as a minimum)
- When the platform architecture changes
- When the user base changes significantly (e.g. expansion beyond PWGs)
- When a data breach occurs
- When new functionality is added (e.g. new plugins, integrations)

### 7.4 Sign-off

| Role | Name | Date | Signature |
|---|---|---|---|
| DPO advice | *PENDING* | | |
| Approved by (GPEx) | | | |
| Approved by (AFCom) | | | |

## Appendix A: Data Flow Diagram

```
Member -> [Invite-only registration] -> Discourse / Antragsgruen
                                              |
                                        [UK VPS server]
                                        PostgreSQL / MySQL
                                        (encrypted at rest)
                                              |
                                        [Admin panel]
                                        (2-3 officers, audit-logged)
                                              |
                                   [Editorial approval gate]
                                              |
                                              v
                                   [Static site generator]
                                              |
                                              v
                                   [Public static website]
                                   (no personal data, no user interaction)
```

No data leaves UK jurisdiction. No third-party processors. No international
transfers.

## Appendix B: Lawful Basis Summary

| User type | Lawful basis (Art.6) | Special category (Art.9) |
|---|---|---|
| Member (all types) | Art.6(1)(f) Legitimate interest | Art.9(2)(d) Not-for-profit political body |
| MP | Art.6(1)(f) Legitimate interest | Art.9(2)(d) as party member |
| Councillor | Art.6(1)(f) Legitimate interest | Art.9(2)(d) as party member |
| Staff | Art.6(1)(f) Legitimate interest / Art.6(1)(b) Contract | Art.9(2)(d) |
| Non-member (public) | N/A (no personal data processed) | N/A |

## Appendix C: Regulatory Notes

**Online Safety Act 2023:**

- Both platforms are user-to-user services under s.3(1)
- Below all categorisation thresholds (Cat 1: 7M/34M, Cat 2B: 3M)
- Base duties apply: illegal content risk assessment (completed separately),
  children's access assessment (not likely, invite-only verified adult
  membership), reporting mechanism (built-in flagging)
- Proportionality principle applies (s.22): minimal obligations for a
  2,000-member, invite-only, no-algorithm platform
- Static public site is NOT a user-to-user service (no interaction)

**CLOUD Act / data sovereignty:**

- Self-hosted on UK infrastructure eliminates CLOUD Act exposure
- No US-headquartered company involved in data processing
- No international data transfers

**Electoral Commission:**

- Platform hosting costs (~£300-480/year) are operational party expenditure,
  not campaign spending, unless used for campaign coordination during a
  regulated period

---
