---
summary: Unity new Input System — Input Actions asset, generated C# class, PlayerInput component, action types, composite bindings, runtime rebinding, touch/mobile, action map best practices
tags: [unity, input, gamedev, controls, rebinding]
related: [unity-cesium]
source: synthetic-memory/unity-input-system.md
---

# Unity Input Handling Patterns

## New Input System vs Legacy

Unity has two input systems:

- **Legacy** (`Input.GetKey`, `Input.GetAxis`): Simple, polling-based. Still works but no longer recommended.
- **New Input System** (`UnityEngine.InputSystem`): Action-based, supports rebinding, multiple devices.

Install via Package Manager: "Input System". Enable in Project Settings → Player → Active Input Handling → "Input System Package (New)" or "Both".

## Input Actions Asset

Create an `.inputactions` asset for centralized input configuration:

1. Right-click → Create → Input Actions.
2. Define **Action Maps** (e.g., "Player", "UI", "Menu").
3. Define **Actions** (e.g., "Move", "Jump", "Look").
4. Add **Bindings** per action (keyboard, gamepad, touch).
5. Generate C# class: check "Generate C# Class" in the asset inspector.

## Using Generated Class

```csharp
public class PlayerController : MonoBehaviour
{
    private PlayerInputActions _input;

    void Awake()
    {
        _input = new PlayerInputActions();
    }

    void OnEnable() => _input.Player.Enable();
    void OnDisable() => _input.Player.Disable();

    void Update()
    {
        Vector2 move = _input.Player.Move.ReadValue<Vector2>();
        if (_input.Player.Jump.WasPressedThisFrame())
            Jump();
    }
}
```

This pattern drives `CesiumCameraController` orbit/zoom in geospatial scenes — see [unity-cesium](unity-cesium.md#core-components).

## PlayerInput Component

The `PlayerInput` component provides a higher-level approach:

- Assign the Input Actions asset.
- Choose behavior: **Send Messages**, **Invoke Unity Events**, **Invoke C# Events**.
- Handles device switching and player assignment automatically.

"Invoke Unity Events" is the most common choice — wire actions to methods in the Inspector.

## Action Types

- **Value**: Continuous input (movement axes, triggers). Use `ReadValue<T>()`.
- **Button**: Discrete press/release. Use `WasPressedThisFrame()`, `IsPressed()`, `WasReleasedThisFrame()`.
- **PassThrough**: Raw, unfiltered input. Useful for multiple devices.

## Composite Bindings

For WASD/arrow key movement, use a **2D Vector Composite**:

- Up: W / Up Arrow
- Down: S / Down Arrow
- Left: A / Left Arrow
- Right: D / Right Arrow

This outputs a `Vector2` on the Move action.

## Runtime Rebinding

```csharp
var rebind = _input.Player.Jump.PerformInteractiveRebinding()
    .WithControlsExcluding("Mouse")
    .OnComplete(op => { op.Dispose(); SaveBindings(); })
    .Start();
```

Save/load overrides with `SaveBindingOverridesAsJson()` / `LoadBindingOverridesFromJson()`.

## Touch & Mobile

The new Input System supports touch via `Touchscreen.current`:

- `EnhancedTouch` API for multi-touch.
- Enable with `EnhancedTouchSupport.Enable()`.
- Use `Touch.activeTouches` for current frame touches.

## Best Practices

- Use Action Maps to separate contexts (gameplay vs UI vs cutscene).
- Disable unused action maps to prevent input conflicts.
- Use `InputAction.performed` callback for event-driven input instead of polling where possible.
- Test with multiple input devices early.

## Related

- [unity-cesium](unity-cesium.md) — `CesiumCameraController` exposes orbit/zoom/fly-to that this Input System wiring drives.
