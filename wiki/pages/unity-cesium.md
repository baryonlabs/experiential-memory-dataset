---
summary: Cesium for Unity — 3D Tiles streaming, Cesium3DTileset, CesiumGeoreference, CesiumGlobeAnchor, imagery overlays, ECEF coordinates, ion authentication
tags: [unity, cesium, 3d, geospatial, gamedev]
related: [unity-input-system]
source: synthetic-memory/unity-cesium.md
---

# Unity + Cesium for 3D Geospatial

## Overview

Cesium for Unity enables 3D geospatial visualization using real-world terrain, imagery, and 3D Tiles. It streams data from Cesium ion or custom tile servers.

## Installation

1. Open Unity Package Manager.
2. Add package by git URL: `https://github.com/CesiumGS/cesium-unity.git`
3. Or download from Cesium's website and import the `.unitypackage`.

Requires Unity 2021.3+ (LTS recommended). Supports URP and Built-in Render Pipeline (HDRP has limited support).

## Core Components

### Cesium3DTileset

The primary component for streaming 3D Tiles data:

- **Ion Asset ID**: Reference a Cesium ion asset (e.g., Cesium World Terrain = asset 1).
- **URL**: Alternatively, point to a self-hosted tileset.
- **Maximum Screen Space Error**: Controls LOD. Lower = higher quality, more tiles loaded.

### CesiumGeoreference

Attach to a root GameObject to define the coordinate reference:

- Set **Latitude/Longitude/Height** for the origin point.
- All child objects are positioned relative to this origin in Unity's coordinate system.
- Handles the WGS84 ellipsoid → Unity flat coordinate transformation.

### CesiumGlobeAnchor

Attach to any GameObject to pin it to a geographic location:

```csharp
var anchor = gameObject.AddComponent<CesiumGlobeAnchor>();
anchor.longitudeLatitudeHeight = new double3(-122.0, 37.0, 100.0);
```

### CesiumCameraController

Provides globe-aware camera controls: orbit, zoom, fly-to. Attach to the camera alongside CesiumGlobeAnchor. Bind orbit/zoom to player input via the new Input System — see [unity-input-system](unity-input-system.md#using-generated-class).

## Imagery Layers

Add `CesiumRasterOverlay` components to a tileset for satellite/map imagery:

- **CesiumIonRasterOverlay**: Bing Maps, Sentinel-2, etc. via ion.
- **CesiumWebMapServiceRasterOverlay**: WMS servers.
- **CesiumTileMapServiceRasterOverlay**: TMS/XYZ tile servers.

## Coordinate Systems

Cesium uses **Earth-Centered, Earth-Fixed (ECEF)** coordinates internally. The `CesiumGeoreference` component handles conversion:

- **ECEF ↔ LLH** (Longitude, Latitude, Height)
- **ECEF ↔ Unity world coordinates**

Use `CesiumWgs84Ellipsoid` for manual conversions:

```csharp
double3 ecef = CesiumWgs84Ellipsoid.LongitudeLatitudeHeightToEarthCenteredEarthFixed(llh);
```

## Performance Tips

- Set appropriate `maximumScreenSpaceError` (16 is default; increase for mobile).
- Use `CesiumCreditSystem` to display required attributions.
- Enable **frustum culling** and **fog culling** on tilesets.
- For large scenes, keep the georeference origin near the camera to avoid floating-point precision issues.

## Authentication

Cesium ion requires an access token:

1. Create a token at `ion.cesium.com/tokens`.
2. Set it on the `Cesium3DTileset` component or globally via `CesiumIonServer`.
3. For production, use a scoped token with only the required asset permissions.

## Related

- [unity-input-system](unity-input-system.md) — driving `CesiumCameraController` (orbit/zoom/fly-to) from action-based input bindings rather than legacy polling.
