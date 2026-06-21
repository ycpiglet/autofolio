# Promotion Asset Owner/R3 Source Trace

This is a local source trace for TASK-160. It traces the TASK-159 readiness
index audit preview back through the local readiness index, archive rollback
manifest, handoff packet candidate, submission preflight, and review queue
records.

It is not an Owner/R3 submission, review start, approval, publication
clearance, archive write, rollback action, export, upload, SNS action, customer
contact, CRM/payment action, secret handling, KIS action, production change, or
deployment action.

## Source Root

| Item | Value |
|------|-------|
| Source artifact | `agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-REVIEW-SUBMISSION-HANDOFF-PACKET-CANDIDATE-ARCHIVE-ROLLBACK-MANIFEST-AUDIT-PREVIEW-READINESS-INDEX-AUDIT-PREVIEW.json` |
| Source SHA-256 | `1eece5535ace986ae5518241d6c8c6ceecbb662aa7125932ac1479421f92904d` |
| Source status | `local_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_readiness_index_audit_preview_not_actual_submission` |
| Source gate | pass |

## Trace Chain

| Seq | Artifact | SHA-256 |
|-----|----------|---------|
| 1 | readiness index audit preview | `1eece5535ace986ae5518241d6c8c6ceecbb662aa7125932ac1479421f92904d` |
| 2 | readiness index | `2698ec75f2410cc68c047b31fc560dd0ec43e6804dc007f86806b84db24c85fa` |
| 3 | archive rollback manifest audit preview | `05f24da517d6d3d50a8b68eb9c55123ffe4709361d2bf8f12e942191a8c1ab28` |
| 4 | archive rollback manifest | `9e50e90a22b4c409b9f8d7454a6f9af70c025e409791bba4ce3b71ba8449af50` |
| 5 | handoff packet candidate audit preview | `88e25cea68e42f058c34f14f840f0ea957f7fe9668f6c44683f36ac98d9f76e4` |
| 6 | handoff packet candidate | `d1b9aa019263f232b0c6ed9467b48a97d1df3069ca3d1fad34265181a3eb7516` |
| 7 | submission preflight audit preview | `2a4a5843d1606e19754f63bcee56f30ba0271171aa56ee797aa8562bd96a7773` |
| 8 | submission preflight contract | `982f684d485518b1090f10efa5ee51b3f3066b6e57b335bcf9f120a5d39f6385` |
| 9 | review queue audit preview | `e28528dbab73ed3f1381dbfe196081ff12c19adaefd066c7ba03c89cfa548ab6` |
| 10 | review queue contract | `8df3f8dc7dc2f8a397fcdbbce8a1c00f1a809b5ffe3e050988a3bbb45d467fe8` |

All nine upstream links between these records are local `source_inputs`
references. The trace records each upstream artifact hash and preserves the
non-action state.

## Owner/R3 Blocker Preservation

The trace preserves all nine decision partitions from the source audit preview:

| Decision | State |
|----------|-------|
| public_landing_use | Owner/R3 required before submission or public use |
| final_pdf_export | Owner/R3 required before submission or public use |
| final_pptx_export | Owner/R3 required before submission or public use |
| sns_upload | Owner/R3 required before submission or public use |
| customer_contact | Owner/R3 required before submission or public use |
| crm_payment_setup | Owner/R3 required before submission or public use |
| paid_ads | Owner/R3 required before submission or public use |
| external_account_action | Owner/R3 required before submission or public use |
| legal_tax_securities_reliance | Owner/R3 required before submission or public use |

## Blocked Actions

The local trace blocks actual Owner/R3 submission, review start, refresh
execution, archive write, rollback execution, archive deletion, approval
evidence collection, final PDF/PPTX export, public URL/upload, SNS upload,
customer contact, CRM/payment action, secret handling, platform API calls, KIS
orders, production changes, and deployment actions.

## Verification

Run:

```powershell
python scripts/promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_readiness_index_audit_preview_source_trace_gate.py --check
python -m pytest tests/unit/test_promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_readiness_index_audit_preview_source_trace_gate.py -q
```
