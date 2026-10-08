# Damascus Certificates × Taʾrīkh al-Islām

A static reading and review interface for 25 audition certificates (*samāʿāt*, *ṭibāq al-samāʿ*). Each records a session held in Damascus between 550 and 700 AH. Every participant is linked, where possible, to a biography in al-Dhahabī's *Taʾrīkh al-Islām*.

The layout follows the [Audition Certificates Platform](https://www.audition-certificates-platform.org/) (ACP): a banner header, certificate cards, and colour-coded annotations. This project is independent and not affiliated with the ACP.

## Using it

Open `index.html`. It needs no server and works from `file://` and on GitHub Pages.

- **Read a match.** Click a highlighted name in a certificate. A superscript **TI** marks a proposed biography. The side panel shows how the name was resolved, the proposed identification with its confidence and justification, the biography's URI, and the full text of al-Dhahabī's entry.
- **Review.** Choose ✓ **Confirm** or ✗ **Reject**. You can also read the other candidates and **use** one, or link any other *Taʾrīkh al-Islām* URI by hand. The keys are `c` to confirm, `r` to reject, `n` for the next unreviewed proposal, and `Esc` to close.
- **Export.** Use *Review & export* to download CSV or JSON. There are three scopes: reviewed decisions only, all linked persons, or all mentions. Each row holds the certificate ID, the person's GUID, the name as written, the resolved name, the roles, the TI URI with the matched name, and the review status. It also carries the original proposal with its confidence and justification, plus the reviewer, a timestamp and any note.
- **Merge.** Use *Import* to load JSON exports from several reviewers. Decisions are stored only in the reviewer's browser (`localStorage`), so export regularly.

## Contents

| Path | What it is |
|---|---|
| `index.html` | The interface: a single file with no build step. |
| `data.js` | Certificates, annotations, reviewed proposals, candidates, and the 574 biographies they cite. |
| `img/` | The header image (MS Staatsbibliothek Berlin, Wetzstein II 150, fol. 1v), the same image the ACP header uses. Check its reuse terms before publishing, or replace it. |
| `data/sample_ids.json` | The 25 sampled ACP certificate IDs. |
| `data/expansions_raw.tsv` | Names given only by relation in a certificate, expanded from the certificate's own wording. Examples are «وابناه يوسف وإبراهيم» and «ولده». The phrase each expansion rests on is recorded. |
| `data/review_decisions.tsv` | The adjudication, one row per mention: TI UID, confidence, and justification. |
| `data/proposals.csv` | A flat table of all proposals. |
| `data/candidates.json` | Raw matcher output: up to six scored candidates per mention. |

## Method (short)

1. **Sample.** The pool is ACP certificates whose only tagged place is Damascus or a Damascene venue, dated 550–700 AH, with 10–45 participants. That gives 1,462 certificates. The sample is stratified by quarter-century (4/5/6/6/4), capped at 7 per venue, with no repeated work (seed 748).
2. **Parsing.** Certificate names and al-Dhahabī's entry headers are parsed into ism, nasab chain, kunya, laqab, nisba and shuhra. Defective spellings are normalised, for example إسحق becomes إسحاق.
3. **Candidates.** A candidate must share the ism, or a distinctive shuhra when the name lacks one. It must also fit the date window. Participants must have died at or after the session. Sanad links must have died within 160 years before it. Anyone whose biography gives a birth year after the session is excluded.
4. **Scoring.** The score rewards agreement in nasab position, laqab, kunya and nisba, and penalises contradictions. It adds a bonus when the biography mentions the certificate's musmiʿ, as in «سمع من ابن طبرزد».
5. **Adjudication.** Every candidate scoring 5 or more was read against the certificate. Shuhra-only sanad links were resolved by direct search, for example «السلفي», «الكندي», «أبي الوقت عبد الأول», «شهدة» and «ابن البطي».

| Outcome | Count |
|---|---|
| Person mentions | 447 |
| Proposed matches | 180 |
| of which confident | 169 |
| of which probable | 11 |
| Ambiguous, left to the reviewer | 1 |
| Candidates examined and rejected | 79 |

Many listeners, especially children and the generation that died after 700 AH, have no entry in *Taʾrīkh al-Islām*. A missing match is often correct.

## Identifiers

Biographies are cited by the record's CID in the OpenITI-derived JSON. The form is `0748Dhahabi.TarikhIslam.<UID>`, for example `0748Dhahabi.TarikhIslam.541468440943` for Muwaffaq al-Dīn Ibn Qudāma.

Note that in the ACP JSON, `endIndex` is **inclusive**. The interface converts it to an exclusive offset.

## Rebuilding

The pipeline scripts are in `scripts/` and use Python 3 with the standard library only. The commands below run from the local project root, where this site sits in `site/` next to `scripts/`, the ACP data release, and the unzipped *Taʾrīkh al-Islām* JSON. Neither data source is included in this repository.

```bash
# from the project root
python3 -I scripts/01_candidates.py msnotesannotator_audition_certificates_data-master tmp/cands.json
python3 -I scripts/02_select.py tmp/cands.json site/data/sample_ids.json
python3 -I scripts/03_index.py 0748Dhahabi.TarikhIslam_json tmp/bios.pkl          # unzipped TI JSON
python3 -I scripts/03b_expansions.py msnotesannotator_audition_certificates_data-master site/data/sample_ids.json site/data
python3 -I scripts/04_match.py msnotesannotator_audition_certificates_data-master tmp/bios.pkl \
        site/data/sample_ids.json site/data/candidates.json site/data/expansions.json
python3 -I scripts/05_build_data.py msnotesannotator_audition_certificates_data-master tmp/bios.pkl site
```

`scripts/03b_expansions.py` generates `site/data/expansions.json` from `scripts/expansions_raw.tsv`. `scripts/review_decisions.tsv` holds the manual adjudication, which `05_build_data.py` merges into the interface.

## Sources

- **Audition certificates.** Audition Certificates Platform, CSMC, Universität Hamburg. Data release `msnotesannotator_audition_certificates_data`, DOI [10.25592/uhhfdm.17611](https://doi.org/10.25592/uhhfdm.17611).
- **Biographies.** al-Dhahabī (d. 748/1348), *Taʾrīkh al-Islām*. OpenITI text `0748Dhahabi.TarikhIslam.MGR20180917-ara1`, with EIS1600-style JSON segmentation.
