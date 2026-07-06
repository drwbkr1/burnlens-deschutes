# BurnLens Deschutes — Source Precedence Rule

## Purpose

This document defines how BurnLens Deschutes handles conflicts between project outputs and official wildfire, emergency, evacuation, hazard, transportation, or public-safety information.

## Core rule

**Official sources govern.**

When BurnLens Deschutes outputs differ from official county, state, federal, fire-service, emergency-management, hazard, evacuation, transportation, or incident information, the official source must be treated as authoritative.

BurnLens outputs may be useful for portfolio demonstration and planning-style screening, but they must never override official information.

## Standard statement

**BurnLens Deschutes outputs are experimental screening artifacts. When BurnLens outputs differ from official wildfire, evacuation, emergency-management, hazard, transportation, or incident information, the official source governs. BurnLens Deschutes is not emergency guidance or official wildfire information.**

## Short UI version

**Official sources govern. BurnLens outputs are experimental and not emergency guidance.**

## Source hierarchy

### 1. Emergency and evacuation sources

Highest priority. These govern warnings, alerts, evacuation orders, road closures, and immediate public-safety issues.

Examples include Deschutes County emergency alerts, Deschutes County Sheriff’s Office emergency management notices, local fire-service information, Oregon evacuation guidance, and law-enforcement evacuation orders.

### 2. Incident and fire-status sources

These govern current wildfire incident status, public fire updates, suppression information, and operational fire context.

Examples include Central Oregon Fire Information, official state wildfire information, federal incident information, and local fire agency updates.

### 3. Official hazard, planning, and GIS sources

These govern public-agency hazard, land, road, parcel, facility, and planning context.

Examples include Deschutes County GIS data, county wildfire hazard zones, Oregon wildfire risk products, county road layers, and official planning datasets.

### 4. Public imagery and active-fire reference data

These may support imagery review, baseline methods, weak labeling, comparison, or visualization. They must be interpreted carefully and do not provide evacuation guidance or field-confirmed incident truth.

### 5. BurnLens-derived outputs

Lowest priority. These include baseline masks, model masks, polygons, summaries, maps, confidence layers, and reports. They are experimental and must yield to all higher-priority sources.

## Conflict-handling procedure

When a conflict appears:

1. Identify the BurnLens output.
2. Identify the official or higher-priority source.
3. Check dates, timestamps, spatial extent, and data age.
4. Mark the BurnLens output provisional, degraded, or superseded if needed.
5. Add a source-precedence note to the run report.
6. Do not present the BurnLens output as an independent conclusion.
7. If the conflict involves emergency, evacuation, road closure, or public safety, remove or heavily caveat the output from public display.

## Required run-report language

**Source-precedence note:** This BurnLens output differs from [official source name] regarding [issue]. Because BurnLens Deschutes is an experimental portfolio workflow, [official source name] governs. This output should be interpreted only as a technical artifact from run [run ID], not as official wildfire, evacuation, hazard, or emergency information.
