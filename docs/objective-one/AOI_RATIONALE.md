# BurnLens Deschutes — AOI Rationale

## Purpose

This document defines the area-of-interest rationale for BurnLens Deschutes.

The project will use **Deschutes County, Oregon** as the county-level study frame. A smaller demonstration AOI inside the county will be selected later during data-feasibility and source review.

## Locked AOI frame

**County-level study frame:** Deschutes County, Oregon  
**Initial AOI status:** County frame locked; final demo AOI pending Phase 2  
**Expected demo AOI type:** Bounded community-and-corridor geography inside Deschutes County

## AOI decision statement

BurnLens Deschutes will focus on a defined study area inside Deschutes County because the county provides a specific geographic anchor, wildfire-planning relevance, public GIS data availability, and enough road, parcel, facility, vegetation, hazard, and emergency-service context to support a transparent GEOINT portfolio workflow.

The final demo AOI should be small enough to process, inspect, and reproduce, but meaningful enough to show how wildfire-relevant imagery and public geospatial layers can be turned into map-ready screening outputs.

## Why Deschutes County fits

### Geographic specificity

The project name requires a bounded geography. Deschutes County prevents the project from sounding like a broad statewide wildfire platform and makes the workflow easier to scope, version, document, and explain.

### Public GIS availability

Deschutes County provides public GIS layers suitable for a GEOINT overlay workflow. Candidate layers include county and city boundaries, communities, taxlots, wildfire hazard zones, public land, vegetation, slope, emergency service locations, schools, county routes, road centerlines, state routes, USFS roads, and watershed boundaries.

### Wildfire-planning relevance

Deschutes County has active wildfire-planning context through community wildfire planning, mitigation planning, evacuation preparedness, road networks, public lands, and WUI-adjacent communities. This supports a portfolio workflow focused on screening and interpretation rather than operational response.

### Demonstration suitability

The county includes communities, corridors, public lands, wildfire hazard context, road networks, parcel/building context, and planning boundaries that can be combined into a limited study area. This makes it suitable for visible geospatial relationships without requiring county-wide coverage.

## Demo AOI selection criteria

The final demo AOI should meet these criteria:

1. **Wildfire relevance** — includes wildfire hazard context, WUI relevance, or proximity to wildfire-planning concerns.
2. **Access/corridor visibility** — includes roads, state routes, county routes, or USFS roads.
3. **Public data coverage** — has available public layers for roads, parcels or taxlots, boundaries, hazard context, and key facilities.
4. **Manageable size** — small enough to process and explain.
5. **Planning-style interpretability** — large enough to produce useful maps and summaries.
6. **Versioning suitability** — can be named, bounded, and assigned an AOI version such as `deschutes-aoi01-v0.1`.
7. **No operational dependency** — does not require live incident data, field validation, agency participation, or confidential infrastructure data.

## Candidate AOI types

- community-and-access-corridor area
- CWPP geography or subset
- WUI-adjacent neighborhood/corridor area
- road-access area connecting structures, public land, and hazard context
- small area near a city or unincorporated community with complete public layers

## Out of scope

This AOI rationale does not authorize county-wide wildfire coverage, emergency alerts, evacuation routing, incident-command use, parcel-level enforcement, official hazard classification, utility-grade infrastructure analysis, or claims of agency review.
