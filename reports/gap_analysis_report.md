# Gap Analysis Report

## Audit Summary

The customer project already had a solid analytical core, but the GitHub presentation still looked incomplete for a top-tier portfolio. The main gaps were around ingestion flexibility, reusable business outputs, recruiter-facing visuals, and run instructions for reviewers without the full raw dataset.

## Missing vs Full Project Before Upgrade

### Missing Files

- no project-local `requirements.txt`
- no example source configuration for automated data download
- no generated PNG asset for the README
- no exported priority-tier summary for business review

### Missing Datasets In GitHub

- full `customer_shopping_behavior.csv` raw dataset

This file remains local-only by design because the repo should stay lightweight and reviewer-friendly.

### Missing Preprocessing / Analytics Steps

- no customer priority score tied to RFM-style behavior
- no retention-risk flag for action-oriented segmentation
- summary tables existed in memory but were not exported as reusable CSV assets

### Missing Automation / Operational Layer

- no configurable Google Drive or Kaggle bootstrap workflow
- no one-command chart export for dashboard screenshots

### Missing Dashboards / Reports

- dashboard brief existed, but there was no generated visual in `assets/`
- recruiter-facing README did not highlight the full business output layer strongly enough

### Missing Documentation

- dataset-handling instructions were not detailed enough for reviewers
- the README did not clearly explain the difference between local full data and sample data

## Upgrades Implemented

- added project-local `requirements.txt`
- added `data/data_sources.example.json` and multi-path bootstrap support
- added `customer_priority_score`, `customer_priority_tier`, and `retention_risk_flag`
- exported reusable processed summary tables into `data/processed/`
- generated `assets/customer_behavior_overview.png`
- rewrote the README to be recruiter-friendly and execution-ready

## Remaining Local-Only Elements

- full raw customer data remains intentionally excluded from GitHub
- if a live BI dashboard is added later, the authoring file should still stay local unless a lightweight shared version is prepared
